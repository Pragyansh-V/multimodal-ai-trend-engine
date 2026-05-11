import asyncio
import os
from playwright.async_api import async_playwright

async def run_auth():
    os.makedirs("./data/session_data", exist_ok=True)
    os.makedirs("./data/logs", exist_ok=True)
    
    username = input("Enter Instagram Username: ")
    password = input("Enter Instagram Password: ")

    async with async_playwright() as p:
        print("\n🚀 LAUNCHING BROWSER...")
        context = await p.chromium.launch_persistent_context(
            user_data_dir="./data/session_data",
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox"]
        )
        
        page = await context.new_page()
        
        try:
            print("🌐 NAVIGATING...")
            await page.goto("https://www.instagram.com/accounts/login/", wait_until="networkidle")
            
            # Type credentials
            await page.get_by_label("Phone number, username, or email").fill(username)
            await page.get_by_label("Password").fill(password)
            await page.get_by_role("button", name="Log in").first.click()
            
            print("⏳ PROCESSING LOGIN...")
            await asyncio.sleep(5) 

            # --- THE STATE CHECKER ---
            current_url = page.url
            print(f"📍 CURRENT LOCATION: {current_url}")

            if "two_factor" in current_url or "challenge" in current_url:
                print("\n🔐 SECURITY CHECK DETECTED!")
                # Take a screenshot so you can see the code request
                await page.screenshot(path="./data/logs/checkpoint.png")
                two_fa_code = input("Enter the 2FA / Security Code sent to your phone/email: ")
                
                # Blind type the 2FA code
                await page.keyboard.type(two_fa_code)
                await page.keyboard.press("Enter")
                await asyncio.sleep(5)

            # Check for "Save Info" or "Notifications" popups that block the home feed
            if "onetap" in page.url or "accounts/onetap" in page.url:
                print("👋 Bypassing 'Save Login Info'...")
                await page.get_by_role("button", name="Not Now").first.click()
                await asyncio.sleep(2)

            print("🏁 FINALIZING SESSION...")
            # We wait for ANY part of the main feed to appear
            await page.wait_for_selector('svg[aria-label="Home"]', timeout=30000)
            print("✅ LOGIN SUCCESSFUL! Session is now hard-coded to your cloud machine.")

        except Exception as e:
            await page.screenshot(path="./data/logs/final_error.png")
            print(f"\n❌ FAILED: {e}")
            print("Look at './data/logs/final_error.png' - what do you see?")
        
        finally:
            await asyncio.sleep(2)
            await context.close()

if __name__ == "__main__":
    asyncio.run(run_auth())