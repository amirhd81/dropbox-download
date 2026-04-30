from playwright.sync_api import sync_playwright

URL = "https://streamable.com/ri37ps"
PASSWORD = "gvc277"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()

    print("Opening page...")
    page.goto(URL)

    print("Filling password...")
    page.fill('input[name="password"]', PASSWORD)

    print("Submitting...")
    page.click('button[type="submit"]')

    # Wait until Streamable loads the unlocked video source
    print("Waiting for unlocked video source...")
    page.wait_for_selector("video source[src]", timeout=15000)

    # Extract the URL
    video_src = page.get_attribute("video source", "src")
    print("Video source:", video_src)

    print("Downloading video...")
    response = context.request.get(video_src)

    if not response.ok:
        print("Download failed:", response.status, response.status_text())
        browser.close()
        exit()

    output_name = "ri37ps.mp4"
    with open(output_name, "wb") as f:
        f.write(response.body())

    print(f"Saved video as {output_name}")

    browser.close()
