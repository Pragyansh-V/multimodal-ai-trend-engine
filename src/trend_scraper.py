import asyncio
import os
import json
import random
from playwright.async_api import async_playwright

async def scrape_trends():
    os.makedirs("./data/raw_trends", exist_ok=True)
    os.makedirs("./data/logs", exist_ok=True)
    
    targets = ["mar_antaya", "systemsbyakshay"] 
    
    async with async_playwright() as p:
        print("🚀 LAUNCHING STEALTH SCRAPER (Broad-Net Mode)...")
        # Using a persistent context to maintain the 'pra_g14' session
        context = await p.chromium.launch_persistent_context(
            user_data_dir="./data/session_data",
            headless=True,
            args=["--no-sandbox", "--disable-blink-features=AutomationControlled"],
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
        
        page = await context.new_page()
        all_reels = set()

        for target in targets:
            url = f"https://www.instagram.com/{target}/reels/"
            print(f"🌐 SCANNING: @{target}...")
            
            try:
                await page.goto(url, wait_until="domcontentloaded")
                # Random jitter to simulate human 'read time'
                await asyncio.sleep(random.uniform(6, 10)) 

                # --- INTERACTION: Breaking the 'Empty DOM' ---
                print("   🖱️ Simulating human behavior...")
                for i in range(3):
                    await page.mouse.wheel(0, random.randint(800, 1500))
                    await asyncio.sleep(random.uniform(2, 4))
                
                # --- THE BROAD-NET EXTRACTION ---
                # We grab EVERY anchor tag on the page
                all_anchors = await page.locator('a').all()
                found_on_page = 0
                
                print(f"   🔎 Analyzing {len(all_anchors)} total links...")
                
                for link in all_anchors:
                    href = await link.get_attribute("href")
                    if href:
                        # Logic: If it's a post (/p/) or a reel (/reels/) and not a navigation tab
                        is_content = any(pattern in href for pattern in ["/reels/", "/p/"])
                        is_not_tab = href != f"/{target}/reels/" and href != f"/{target}/"
                        
                        if is_content and is_not_tab:
                            full_url = f"https://www.instagram.com{href}"
                            if full_url not in all_reels:
                                all_reels.add(full_url)
                                found_on_page += 1

                print(f"   ✅ Successfully extracted {found_on_page} links from @{target}.")
                await page.screenshot(path=f"./data/logs/harvest_{target}.png")

            except Exception as e:
                print(f"   ❌ Error during @{target} scan: {e}")
            
            # Cooldown between profiles to stay under the radar
            await asyncio.sleep(random.uniform(5, 8))

        # Save the structured manifest
        with open("./data/raw_trends/manifest.json", "w") as f:
            json.dump(list(all_reels), f, indent=4)
            
        print(f"\n🏁 TOTAL TRENDS HARVESTED: {len(all_reels)}")
        print("📂 File updated: ./data/raw_trends/manifest.json")
        await context.close()

if __name__ == "__main__":
    asyncio.run(scrape_trends())