import asyncio
import json
import os
from playwright.async_api import async_playwright

async def inject_cookies():
    os.makedirs("./data/session_data", exist_ok=True)
    os.makedirs("./data/logs", exist_ok=True)
    
    password = input("Enter Instagram password (Final Check): ")

    with open("./data/cookies.json", "r") as f:
        raw_cookies = json.load(f)

    # Normalization
    clean_cookies = [{**c, 'sameSite': 'Lax'} for c in raw_cookies]

    async with async_playwright() as p:
        print("🚀 LAUNCHING STEALTH BROWSER...")
        # We add a common User-Agent and hide the 'WebDriver' flag
        context = await p.chromium.launch_persistent_context(
            user_data_dir="./data/session_data",
            headless=True,
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            args=["--no-sandbox", "--disable-blink-features=AutomationControlled"]
        )
        
        await context.add_cookies(clean_cookies)
        page = await context.new_page()
        
        # TRICK: Navigate to a deep-link to bypass the 'Continue' screen
        print("🌐 ATTEMPTING DIRECT BYPASS (Navigating to /explore/)...")
        await page.goto("https://www.instagram.com/explore/", wait_until="domcontentloaded")
        await asyncio.sleep(8)

        # --- THE MULTI-MODAL HANDLER ---
        for attempt in range(4):
            current_url = page.url
            print(f"📍 Round {attempt+1} | URL: {current_url}")
            await page.screenshot(path=f"./data/logs/debug_round_{attempt+1}.png")

            # 1. If we are on Explore or Home, we WIN
            if "/explore/" in current_url or "instagram.com/?next" in current_url or await page.locator('svg[aria-label="Home"]').is_visible():
                print("🏁 RESULT: FULL SUCCESS! Bypassed the loop.")
                break

            # 2. If stuck on 'Continue', try Keyboard 'Enter' (more human-like)
            continue_btn = page.locator('button:has-text("Continue"), [role="button"]:has-text("Continue")').first
            if await continue_btn.is_visible():
                print("⌨️ Interaction Gate found. Using Keyboard 'Enter' to bypass...")
                await continue_btn.focus()
                await page.keyboard.press("Enter")
                await asyncio.sleep(6)
                continue

            # 3. Handle 'Not Now' Popups
            not_now = page.locator('button:has-text("Not Now")').first
            if await not_now.is_visible():
                await not_now.click(force=True)
                print("✅ Dismissed 'Not Now' popup.")
                await asyncio.sleep(3)
                continue

        # Final Verification
        await page.screenshot(path="./data/logs/bridge_final_check.png")
        await context.close()

if __name__ == "__main__":
    asyncio.run(inject_cookies())