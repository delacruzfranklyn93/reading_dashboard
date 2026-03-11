import scrape_leaderboard
import sync_to_cloud
import time

def main():
    print("=== READING DASHBOARD AUTOMATION ===")
    
    # Step 1: Scrape Data
    print("\n--- STEP 1: SCRAPING DATA ---")
    try:
        scrape_leaderboard.main()
    except Exception as e:
        print(f"CRITICAL ERROR in Scraping: {e}")
        return

    # Optional: Short pause to ensure file write buffer clears (though usually not strictly necessary with Python's close())
    time.sleep(1)

    # Step 2: Sync to Cloud
    print("\n--- STEP 2: SYNCING TO CLOUD ---")
    try:
        sync_to_cloud.sync_to_google_sheets()
    except Exception as e:
        print(f"CRITICAL ERROR in Sync: {e}")
        return

    print("\n=== AUTOMATION COMPLETE ===")

if __name__ == "__main__":
    main()
