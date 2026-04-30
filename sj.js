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

  await page.goto('https://streamable.com/dnd1');

    // console.log("filling password")

//   await page.fill('form[name="video-password"] input[name="password"]', 'gvc277');


//     console.log("password got filled")

//   await page.click('button[type="submit"]');

//     clicked = true
//     console.log(clicked, "buttong clicked")
//     const exists = await page.locator('p.invisible').count() > 0;

// console.log(exists, "error exists");
    


  logFile.end();

    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(5000);

    const html = await page.content();

  // save to file
  fs.writeFileSync('page3.html', html);

  console.log('HTML saved');
  
  await page.waitForTimeout(500000);

  await browser.close();
})();
