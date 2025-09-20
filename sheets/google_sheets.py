"""
Google Sheets integration for job scraper
"""
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from typing import List, Dict, Optional
import json
import os
from datetime import datetime


class GoogleSheetsManager:
    def __init__(self, credentials_file: str = "credentials.json"):
        """Initialize Google Sheets manager with service account credentials"""
        self.credentials_file = credentials_file
        self.client = None
        self.sheet = None
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Google Sheets API"""
        try:
            scope = [
                "https://spreadsheets.google.com/feeds",
                "https://www.googleapis.com/auth/drive"
            ]
            
            if not os.path.exists(self.credentials_file):
                print(f"❌ Credentials file {self.credentials_file} not found!")
                print("Please follow the setup instructions in README.md")
                return
            
            creds = ServiceAccountCredentials.from_json_keyfile_name(
                self.credentials_file, scope
            )
            self.client = gspread.authorize(creds)
            print("✅ Successfully authenticated with Google Sheets API")
            
        except Exception as e:
            print(f"❌ Failed to authenticate with Google Sheets: {e}")
            self.client = None
    
    def connect_to_sheet(self, sheet_id: str, sheet_name: str = "Jobs") -> bool:
        """Connect to a specific Google Sheet"""
        if not self.client:
            print("❌ Not authenticated with Google Sheets")
            return False
        
        try:
            spreadsheet = self.client.open_by_key(sheet_id)
            
            # Try to get existing worksheet or create new one
            try:
                self.sheet = spreadsheet.worksheet(sheet_name)
                print(f"✅ Connected to existing sheet: {sheet_name}")
            except gspread.WorksheetNotFound:
                # Create new worksheet with headers
                self.sheet = spreadsheet.add_worksheet(
                    title=sheet_name, 
                    rows=1000, 
                    cols=10
                )
                self._setup_headers()
                print(f"✅ Created new sheet: {sheet_name}")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to connect to sheet: {e}")
            return False
    
    def _setup_headers(self):
        """Set up column headers for the jobs sheet"""
        headers = [
            "Job Title",
            "Company",
            "Location", 
            "Application Link",
            "Source",
            "Posted Date",
            "Scraped Date",
            "Salary",
            "Application Status"
        ]
        
        try:
            self.sheet.insert_row(headers, 1)
            
            # Format header row
            self.sheet.format('A1:I1', {
                'backgroundColor': {'red': 0.2, 'green': 0.6, 'blue': 0.9},
                'textFormat': {'bold': True, 'foregroundColor': {'red': 1, 'green': 1, 'blue': 1}},
                'horizontalAlignment': 'CENTER'
            })
            
            print("✅ Set up sheet headers")
            
        except Exception as e:
            print(f"❌ Failed to setup headers: {e}")
    
    def get_existing_job_urls(self) -> set:
        """Get all existing job URLs to avoid duplicates"""
        if not self.sheet:
            return set()
        
        try:
            # Get all values from the Application Link column (column D)
            urls = self.sheet.col_values(4)  # 4th column is Application Link
            
            # Remove header and empty values
            existing_urls = {url for url in urls[1:] if url.strip()}
            
            print(f"📊 Found {len(existing_urls)} existing job URLs")
            return existing_urls
            
        except Exception as e:
            print(f"❌ Failed to get existing URLs: {e}")
            return set()
    
    def append_jobs(self, jobs: List[Dict]) -> int:
        """Append new jobs to the sheet"""
        if not self.sheet or not jobs:
            return 0
        
        try:
            # Get existing URLs to avoid duplicates
            existing_urls = self.get_existing_job_urls()
            
            # Filter out duplicates
            new_jobs = []
            for job in jobs:
                job_url = job.get('link', '')
                if job_url and job_url not in existing_urls:
                    new_jobs.append(job)
            
            if not new_jobs:
                print("📝 No new jobs to add (all were duplicates)")
                return 0
            
            # Prepare rows for batch insert
            rows_to_insert = []
            for job in new_jobs:
                row = [
                    job.get('title', ''),
                    job.get('company', ''),
                    job.get('location', ''),
                    job.get('link', ''),
                    job.get('source', ''),
                    job.get('posted_date', ''),
                    datetime.now().strftime('%Y-%m-%d'),
                    job.get('salary', ''),
                    'Not Applied'
                ]
                rows_to_insert.append(row)
            
            # Batch insert all rows
            self.sheet.append_rows(rows_to_insert)
            
            print(f"✅ Added {len(new_jobs)} new jobs to Google Sheet")
            return len(new_jobs)
            
        except Exception as e:
            print(f"❌ Failed to append jobs: {e}")
            return 0
    
    def update_job_status(self, job_url: str, new_status: str) -> bool:
        """Update the application status for a specific job"""
        if not self.sheet:
            return False
        
        try:
            # Find the row with the matching URL
            urls = self.sheet.col_values(4)  # Application Link column
            
            for i, url in enumerate(urls):
                if url == job_url:
                    row_num = i + 1
                    self.sheet.update_cell(row_num, 9, new_status)  # Status column
                    print(f"✅ Updated job status to: {new_status}")
                    return True
            
            print(f"❌ Job URL not found: {job_url}")
            return False
            
        except Exception as e:
            print(f"❌ Failed to update job status: {e}")
            return False
    
    def get_job_stats(self) -> Dict:
        """Get statistics about jobs in the sheet"""
        if not self.sheet:
            return {}
        
        try:
            # Get all data
            all_data = self.sheet.get_all_records()
            
            if not all_data:
                return {"total_jobs": 0}
            
            # Calculate stats
            total_jobs = len(all_data)
            sources = {}
            statuses = {}
            
            for job in all_data:
                source = job.get('Source', 'Unknown')
                status = job.get('Application Status', 'Unknown')
                
                sources[source] = sources.get(source, 0) + 1
                statuses[status] = statuses.get(status, 0) + 1
            
            return {
                "total_jobs": total_jobs,
                "by_source": sources,
                "by_status": statuses,
                "last_updated": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            print(f"❌ Failed to get job stats: {e}")
            return {}
    
    def cleanup_duplicates(self) -> int:
        """Remove duplicate jobs based on URL"""
        if not self.sheet:
            return 0
        
        try:
            all_data = self.sheet.get_all_records()
            seen_urls = set()
            rows_to_delete = []
            
            for i, job in enumerate(all_data):
                job_url = job.get('Application Link', '')
                if job_url in seen_urls:
                    rows_to_delete.append(i + 2)  # +2 because of header and 0-indexing
                else:
                    seen_urls.add(job_url)
            
            # Delete duplicate rows (in reverse order to maintain indices)
            for row_num in reversed(rows_to_delete):
                self.sheet.delete_rows(row_num)
            
            print(f"✅ Removed {len(rows_to_delete)} duplicate jobs")
            return len(rows_to_delete)
            
        except Exception as e:
            print(f"❌ Failed to cleanup duplicates: {e}")
            return 0


def test_connection(sheet_id: str, sheet_name: str = "Jobs") -> bool:
    """Test Google Sheets connection"""
    print("🧪 Testing Google Sheets connection...")
    
    manager = GoogleSheetsManager()
    
    if not manager.client:
        print("❌ Authentication failed")
        return False
    
    if not manager.connect_to_sheet(sheet_id, sheet_name):
        print("❌ Failed to connect to sheet")
        return False
    
    # Test basic operations
    stats = manager.get_job_stats()
    print(f"📊 Sheet stats: {stats}")
    
    print("✅ Google Sheets connection test successful!")
    return True


if __name__ == "__main__":
    # Test the Google Sheets integration
    with open("../config.json", "r") as f:
        config = json.load(f)
    
    sheet_id = config.get("sheet_id")
    if sheet_id and sheet_id != "YOUR_GOOGLE_SHEET_ID_HERE":
        test_connection(sheet_id)
    else:
        print("❌ Please update sheet_id in config.json first")
