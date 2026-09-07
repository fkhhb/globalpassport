#!/usr/bin/env node
/*
 * Generate responsive width variants of the hero photograph.
 *
 * OPTIONAL DEV TOOL. build.py never needs this and stays standard-library
 * Python; it emits a srcset only for variant files that exist, so a checkout
 * without them still builds. Run this when the hero photograph changes.
 *
 * Why it exists: the hero is the LCP element and, at 3720x2028 / ~1 MB, about a
 * third of every image byte on the page. A 390px phone at 3x needs ~1200px of
 * width, not 3720. With a srcset the browser picks the smallest variant that
 * covers its box; measured, the 1600px variant is ~250 KB.
 *
 * Why Chromium and not PIL/ImageMagick: neither is available in the build
 * environment this repo is maintained from, Playwright's Chromium is. Canvas
 * drawImage with imageSmoothingQuality:'high' is a conventional resample - it
 * invents nothing, so it is fine for a cityscape (and would be fine for the
 * portraits too, unlike the generative upscalers docs/BRIEF.md §2.4 forbids).
 *
 * Requires: node + playwright (npm i playwright) + a Chromium binary.
 *
 *   node tools/make_hero_variants.js
 *   node tools/make_hero_variants.js assets/img/some-other-hero.jpg
 */
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');

const ROOT   = path.resolve(__dirname, '..');
const SRC    = process.argv[2] || path.join(ROOT, 'assets/img/01-marienplatz-and-the-frauenkirche-at-dusk-mun.jpg');
const WIDTHS = [1000, 1600, 2400];      // the source itself is the largest candidate
const QUALITY = 0.82;
const CHROME = process.env.CHROMIUM_PATH || '/opt/pw-browsers/chromium-1194/chrome-linux/chrome';

(async () => {
  const b = await chromium.launch({ executablePath: fs.existsSync(CHROME) ? CHROME : undefined });
  const p = await (await b.newContext()).newPage();
  const src = 'data:image/jpeg;base64,' + fs.readFileSync(SRC).toString('base64');
  for (const w of WIDTHS) {
    const r = await p.evaluate(async ({ src, w, q }) => {
      const img = new Image(); img.src = src; await img.decode();
      if (w >= img.naturalWidth) return null;              // never upscale
      const h = Math.round(img.naturalHeight * w / img.naturalWidth);
      const c = document.createElement('canvas'); c.width = w; c.height = h;
      const x = c.getContext('2d'); x.imageSmoothingEnabled = true; x.imageSmoothingQuality = 'high';
      x.drawImage(img, 0, 0, w, h);
      return { h, data: c.toDataURL('image/jpeg', q).split(',')[1] };
    }, { src, w, q: QUALITY });
    if (!r) { console.log(`  skip ${w}w (source is not wider than that)`); continue; }
    const out = path.join(ROOT, 'assets/img', `01-hero-w${w}.jpg`);
    const buf = Buffer.from(r.data, 'base64');
    fs.writeFileSync(out, buf);
    console.log(`  ${path.basename(out)}  ${w}x${r.h}  ${(buf.length / 1024).toFixed(0)} KB`);
  }
  await b.close();
})();
