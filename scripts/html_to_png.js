/* Render HTML file to PNG using Puppeteer */
const puppeteer = require('puppeteer');
const path = require('path');

(async () => {
  const [, , inputPath, outputPath] = process.argv;
  if (!inputPath || !outputPath) {
    console.error('Usage: node html_to_png.js <input_html> <output_png>');
    process.exit(1);
  }
  const absHtml = path.resolve(inputPath);
  const browser = await puppeteer.launch({
    headless: 'new',
    defaultViewport: { width: 1400, height: 900 }
  });
  const page = await browser.newPage();
  await page.goto(`file://${absHtml}`, { waitUntil: 'networkidle0' });
  // Ensure body is fully loaded
  await page.evaluate(() => new Promise(resolve => setTimeout(resolve, 500)));
  await page.screenshot({ path: outputPath, fullPage: true, type: 'png' });
  await browser.close();
})();
