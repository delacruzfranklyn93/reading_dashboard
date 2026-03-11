import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import os

def sync_to_google_sheets():
    # Define scope
    scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    
    # --- NEW SMART PATH LOGIC ---
    # Get the folder where this script is correctly located
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # combine that folder with the filename
    creds_file = os.path.join(script_dir, 'credentials.json')

    if not os.path.exists(creds_file):
        print(f"Error: '{creds_file}' not found. Please place your Google Service Account credentials in this directory.")
        return

    try:
        # Now load using the full path
        creds = ServiceAccountCredentials.from_json_keyfile_name(creds_file, scope)
        client = gspread.authorize(creds)
        
        # Open the sheet
        sheet_name = 'Reading Competition 2026'
        try:
            sheet = client.open(sheet_name)
        except gspread.SpreadsheetNotFound:
            print(f"Error: Google Sheet '{sheet_name}' not found. Please ensure it exists and the service account has access.")
            return

        worksheet = sheet.get_worksheet(0) # Sheet1
        
        # Read the CSV
        csv_file = 'final_scoreboard.csv'
        if not os.path.exists(csv_file):
             print(f"Error: '{csv_file}' not found.")
             return
             
        df = pd.read_csv(csv_file)
        
        # Convert DataFrame to list of lists for gspread (including header)
        data = [df.columns.values.tolist()] + df.values.tolist()
        
        # Clear existing content
        worksheet.clear()
        
        # Update with new data
        worksheet.update(data)
        
        print("[SUCCESS] Data uploaded to Google Sheets.")
        
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    sync_to_google_sheets()
