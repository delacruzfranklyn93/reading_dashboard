import requests
from bs4 import BeautifulSoup
import pandas as pd
import datetime
import re
import time
import os
import json

# --- CONFIG SECTION ---
# To add more users, just add {"name": "Name", "id": "12345"} to this list.
USERS = [
    {'name': 'Franklyn', 'id': '191137522'},
    {'name': 'Savannah', 'id': '56357420'}
]
HANDICAP_MULTIPLIER = 1.0
# ----------------------

def get_read_books(user_id, user_name):
    books = []
    # Use RSS feed which is more reliable and public
    base_url = f"https://www.goodreads.com/review/list_rss/{user_id}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    print(f"Scraping books for {user_name} via RSS...")
    
    params = {
        'shelf': 'read',
    }
        
    try:
        response = requests.get(base_url, params=params, headers=headers)
        if response.status_code != 200:
            print(f"  Error: Failed to fetch RSS for {user_name}. Status: {response.status_code}")
            return []
        
        # Parse XML
        soup = BeautifulSoup(response.content, 'xml')
        items = soup.find_all('item')
        
        if not items:
            print(f"  No items found in RSS feed for {user_name}.")
            return []
            
        print(f"  Found {len(items)} items in RSS feed.")
        
        for item in items:
            # Extract Title
            title = item.title.text.strip() if item.title else "Unknown Title"
            
            # Extract Date Read
            # Format in RSS: "Mon, 5 Jan 2026 00:00:00 +0000"
            date_read_text = item.user_read_at.text.strip() if item.find('user_read_at') else ""
            
            if not date_read_text:
                continue
            
            try:
                # Parse date
                date_read = datetime.datetime.strptime(date_read_text, '%a, %d %b %Y %H:%M:%S %z')
            except ValueError:
                # Try fallback format or just skip
                continue

            # Filter for 2026
            if date_read.year == 2026:
                # Extract Pages
                pages_text = item.num_pages.text.strip() if item.find('num_pages') else "0"
                try:
                        pages = int(re.sub(r'[^\d]', '', pages_text))
                except ValueError:
                    pages = 0

                books.append({
                    'Reader': user_name,
                    'Book Title': title,
                    'Pages': pages,
                    'Date Read': date_read.strftime('%Y-%m-%d')
                })
        
    except Exception as e:
        print(f"  Exception occurred: {e}")

    if not books:
         print(f"  No books found for {user_name} in 2026.")
    else:
        print(f"  Found {len(books)} books for {user_name} in 2026.")
        
    return books

def get_custom_reads():
    books = []
    custom_reads_file = 'custom_reads.json'
    
    if not os.path.exists(custom_reads_file):
        return books
        
    try:
        with open(custom_reads_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        for item in data:
            try:
                # Parse date to check if it's 2026
                date_read = datetime.datetime.strptime(item.get('date_read', ''), '%Y-%m-%d')
                if date_read.year == 2026:
                    books.append({
                        'Reader': item.get('Reader', 'Unknown'),
                        'Book Title': item.get('book_title', 'Unknown Title'),
                        'Pages': item.get('estimated_pages', 0),
                        'Date Read': date_read.strftime('%Y-%m-%d')
                    })
            except (ValueError, TypeError):
                print(f"  Skipping custom read due to invalid date format (needs YYYY-MM-DD): {item}")
                continue
                
        if books:
            print(f"Loaded {len(books)} custom reads from {custom_reads_file}.")
    except Exception as e:
        print(f"  Error loading custom reads: {e}")
        
    return books

def main():
    all_books = []
    
    for user in USERS:
        user_books = get_read_books(user['id'], user['name'])
        all_books.extend(user_books)
        
    # Append Custom Reads
    print("\nLoading Custom Reads...")
    custom_books = get_custom_reads()
    all_books.extend(custom_books)
        
    if all_books:
        df = pd.DataFrame(all_books)
        
        # --- APPLY LOGIC MERGED FROM process_data.py ---
        # Initialize Adjusted Pages with normal Pages
        df['Adjusted Pages'] = df['Pages']
        
        # Apply Handicap to Franklyn (assuming Franklyn is 'Me' from the old script)
        # You can change the name below if you want to apply it to someone else
        df.loc[df['Reader'] == 'Franklyn', 'Adjusted Pages'] = df['Pages'] * HANDICAP_MULTIPLIER
        
        # Reorder columns match the preferred final format
        # Date Read, Reader, Book Title, Pages, Adjusted Pages
        output_columns = ['Date Read', 'Reader', 'Book Title', 'Pages', 'Adjusted Pages']
        # Ensure all columns exist
        for col in output_columns:
            if col not in df.columns:
                df[col] = None # Should not happen based on above logic
                
        df = df[output_columns]
        # -----------------------------------------------
        
        # Save to CSV
        output_file = 'final_scoreboard.csv'
        df.to_csv(output_file, index=False)
        print(f"\nSaved {len(df)} records to {output_file}")
        
        # Print Summary
        print("\n--- Summary Table ---")
        summary = df.groupby('Reader')[['Pages', 'Adjusted Pages']].sum().reset_index().sort_values('Adjusted Pages', ascending=False)
        print(summary)
    else:
        print("\nNo books found for any user in 2026.")
        # Create empty file with correct columns
        pd.DataFrame(columns=['Date Read', 'Reader', 'Book Title', 'Pages', 'Adjusted Pages']).to_csv('final_scoreboard.csv', index=False)

if __name__ == "__main__":
    main()
