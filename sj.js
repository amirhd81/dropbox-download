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
  
      logFile.write(` ${req.url()}\nBODY: ${req.postData()}\n\n`);
  
});


  page.on('response', async response => {
      
    logFile.write(`<<< RESPONSE: ${response.status()} ${response.url()}\n`);
      
  });

  await page.goto('https://streamable.com/ri37ps');

  await page.fill('form[name="video-password"] input[name="password"]', 'gvc277');

  await page.click('button[type="submit"]');

    clicked = true
    console.log(clicked, "buttong clicked")
    


  logFile.end();

    await page.waitForTimeout(10000);

await page.waitForTimeout(3000);

    const div = await page.locator("div.svp-desktop-player")

    const html = await div.innerHTML();
console.log(html);
  
  // await page.waitForTimeout(500000);

  await browser.close();
})();
