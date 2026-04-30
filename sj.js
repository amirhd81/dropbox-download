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

    await page.waitForTimeout(1000);

// Wait a moment for iframe to load
await page.waitForTimeout(3000);

// Find the streamable iframe
const frames = page.frames();
const frame = frames.find(f => f.url().includes("streamable.com"));

if (!frame) {
    console.log("No streamable iframe found!");
    process.exit();
}

// Wait for source inside iframe
await frame.waitForSelector("source");

// Extract URL
const src = await frame.getAttribute("source", "src");

console.log("Final video src:", src);

    const html = await page.content();

//     const src = await page.locator('source').getAttribute('src');
// console.log(src); 

  // save to file
  fs.writeFileSync('page3.html', html);

  console.log('HTML saved');
  
  // await page.waitForTimeout(500000);

  await browser.close();
})();
