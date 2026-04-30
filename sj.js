const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();

  page.on('request', request => {
    console.log('REQUEST:', request.method(), request.url());
  });

  page.on('response', async response => {
    console.log('RESPONSE:', response.status(), response.url());
  });

  await page.goto('https://streamable.com/ri37ps');

  await page.fill("#password", "gvc277");

  await page.click('button[type="submit"]');

  await page.waitForTimeout(500000);

  await browser.close();
})();
