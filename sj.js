const { chromium } = require('playwright');
const chromiumPath = "/usr/bin/chromium-browser";
const fs = require('fs');

(async () => {

const browser = await chromium.launch({
    executablePath: chromiumPath,
    headless: true
   });
    

    let clicked = false;
  const logFile = fs.createWriteStream('network_log.txt', { flags: 'a' });
  
  const page = await browser.newPage();

    page.on('request', req => {
  if (clicked && req.method() === 'POST') {
      logFile.write(`POST ${req.url()}\nBODY: ${req.postData()}\n\n`);
  }
});


  page.on('response', async response => {
      if (clicked) {
    logFile.write(`<<< RESPONSE: ${response.status()} ${response.url()}\n`);
      }
  });

  await page.goto('https://streamable.com/ri37ps');

  await page.fill("#password", "gvc277");

    console.log("password got filled")

  await page.click('button[type="submit"]');

    clicked = true
    console.log(clicked, "buttong clicked")
    const exists = await page.locator('p.invisible').count() > 0;

console.log(exists, "error exists");
    


  logFile.end();
  
  await page.waitForTimeout(500000);

  await browser.close();
})();
