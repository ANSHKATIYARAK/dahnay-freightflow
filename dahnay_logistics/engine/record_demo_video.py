"""
FreightFlow: Automated High-Resolution Screen Recording Generator
Uses Playwright to capture a crisp, high-definition video of the 60-second FreightFlow demo.
Saves the video directly to dahnay_logistics/datasets/freightflow_demo.webm
"""

import os
import sys
import time
from playwright.sync_api import sync_playwright

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
output_dir = os.path.join(parent_dir, "datasets")
os.makedirs(output_dir, exist_ok=True)

video_dir = os.path.join(output_dir, "video_recordings")
os.makedirs(video_dir, exist_ok=True)


def record_demo():
    print("[1/4] Launching headless Chromium with high-definition video recording...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1600, "height": 950},
            record_video_dir=video_dir,
            record_video_size={"width": 1600, "height": 950}
        )

        page = context.new_page()

        print("[2/4] Navigating to http://localhost:8000/dahnay...")
        page.goto("http://localhost:8000/dahnay", wait_until="networkidle")
        page.wait_for_timeout(2000)

        print("[3/4] Executing choreographed 60-second demo...")
        # Click the Run 60s Demo button
        demo_btn = page.locator("button:has-text('Run 60s Demo')")
        if demo_btn.count() > 0:
            demo_btn.first.click()
        else:
            page.evaluate("runGuidedDemo()")

        # Wait for the demo steps to play out on screen
        # Step 1: Raw SI view & discrepancies (approx 3-4s)
        page.wait_for_timeout(3500)

        # Step 2: Auto-Fix transition
        page.wait_for_timeout(2500)

        # Step 3: Terminal CargoWise XML export
        page.wait_for_timeout(4000)

        # Hold on final clean state
        page.wait_for_timeout(3000)

        print("[4/4] Finalizing and encoding video file...")
        # Close page to ensure video flush
        page.close()
        context.close()
        browser.close()

    # Find the generated video file
    video_files = [os.path.join(video_dir, f) for f in os.listdir(video_dir) if f.endswith(".webm")]
    if video_files:
        latest_video = max(video_files, key=os.path.getctime)
        target_path = os.path.join(output_dir, "freightflow_demo.webm")
        if os.path.exists(target_path):
            os.remove(target_path)
        os.rename(latest_video, target_path)
        size_kb = os.path.getsize(target_path) / 1024
        print(f"[OK] Video successfully saved to:")
        print(f"     Path: {target_path}")
        print(f"     Size: {size_kb:.1f} KB")
        return target_path
    else:
        print("[!] No video recorded.")
        return None


if __name__ == "__main__":
    record_demo()
