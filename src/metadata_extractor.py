import asyncio
import os
import json
import random
from playwright.async_api import async_playwright

async def extract_metadata():
    os.makedirs("./data/raw_trends/metadata", exist_ok=True)
    os.makedirs("./data/logs", exist_ok=True)
    
    with open("./data/raw_trends/manifest.json", "r") as f:
        urls = json.load(f)

    async with async_playwright() as p:
        print("🚀 LAUNCHING THE STEALTH HARVESTER...")
        context = await p.chromium.launch_persistent_context(
            user_data_dir="./data/session_data",
            headless=True,
            # We add extra arguments to hide the 'automation' signature
            args=[
                "--no-sandbox", 
                "--disable-blink-features=AutomationControlled",
                "--disable-infobars"
            ],
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
        
        page = await context.new_page()

        for url in urls:
            reel_id = url.split("/")[-2] if "/reel/" in url else "unknown"
            print(f"📡 SCANNING REEL: {reel_id}...")
            
            try:
                # 1. Navigate and wait for the 'Network' to calm down
                await page.goto(url, wait_until="domcontentloaded")
                try:
                    # Give it 10 seconds to finish loading images/scripts
                    await page.wait_for_load_state("networkidle", timeout=10000)
                except: pass

                # --- MODAL BUSTER (Based on your screenshots) ---
                # We try clicking 'X', 'Escape', and clicking off-screen
                try:
                    await page.keyboard.press("Escape")
                    # Target the 'X' inside the specific dialog role
                    close_x = page.locator('div[role="dialog"] svg[aria-label="Close"], svg[aria-label="Dismiss"]').first
                    if await close_x.is_visible():
                        await close_x.click(force=True)
                        print("   💥 Modal dismissed.")
                    await asyncio.sleep(2)
                except: pass

                # --- BROAD-SPECTRUM HARVEST ---
                # We grab EVERY visible text block on the page
                # This works even if the 'article' tag is missing or renamed
                all_text_elements = page.locator('span, h1, div[dir="auto"]')
                texts = await all_text_elements.all_inner_texts()
                
                # Heuristic: Captions are usually > 40 chars and contain real sentences
                # We filter out UI junk like "Log In", "Follow", "1.2k likes"
                possible_captions = [t.strip() for t in texts if len(t.strip()) > 40]
                
                if possible_captions:
                    # The longest one is statistically almost always the caption
                    final_caption = max(possible_captions, key=len)
                    
                    metadata = {
                        "url": url,
                        "reel_id": reel_id,
                        "caption": final_caption
                    }
                    
                    with open(f"./data/raw_trends/metadata/{reel_id}.json", "w") as f:
                        json.dump(metadata, f, indent=4)
                    print(f"   ✅ SUCCESS: Captured metadata for {reel_id}")
                else:
                    print(f"   ⚠️ EMPTY: No caption-like text found for {reel_id}.")
                    await page.screenshot(path=f"./data/logs/empty_{reel_id}.png")

            except Exception as e:
                print(f"   ❌ CRITICAL ERROR on {reel_id}: {str(e)[:50]}")
            
            # Randomized 'Read Time' to prevent the next block
            await asyncio.sleep(random.uniform(5, 10))

        await context.close()

if __name__ == "__main__":
    asyncio.run(extract_metadata())