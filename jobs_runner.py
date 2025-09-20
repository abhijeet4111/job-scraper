"""
Main job scraper runner - orchestrates all scrapers and Google Sheets integration
"""
import json
import os
import sys
from datetime import datetime
from typing import List, Dict

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scrapers.naukri import NaukriScraper
from scrapers.indeed import IndeedScraper
from scrapers.timesjobs import TimesJobsScraper
from scrapers.linkedin import LinkedInJobsScraper
from scrapers.glassdoor import GlassdoorScraper
from scrapers.company_careers import CompanyCareersScraper
from scrapers.utils import deduplicate_jobs
from sheets.google_sheets import GoogleSheetsManager


class JobScraperRunner:
    def __init__(self, config_file: str = "config.json"):
        """Initialize the job scraper runner"""
        self.config = self.load_config(config_file)
        self.sheets_manager = GoogleSheetsManager()
        self.scrapers = {}
        self.setup_scrapers()
        
    def load_config(self, config_file: str) -> Dict:
        """Load configuration from JSON file"""
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            print("✅ Configuration loaded successfully")
            return config
        except FileNotFoundError:
            print(f"❌ Config file {config_file} not found!")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON in config file: {e}")
            sys.exit(1)
    
    def setup_scrapers(self):
        """Initialize all available scrapers"""
        try:
            self.scrapers['naukri'] = NaukriScraper(self.config)
            self.scrapers['indeed'] = IndeedScraper(self.config)
            self.scrapers['timesjobs'] = TimesJobsScraper(self.config)
            self.scrapers['linkedin'] = LinkedInJobsScraper(self.config)
            self.scrapers['glassdoor'] = GlassdoorScraper(self.config)
            self.scrapers['companies'] = CompanyCareersScraper(self.config)
            print("✅ Scrapers initialized successfully")
        except Exception as e:
            print(f"❌ Error initializing scrapers: {e}")
    
    def setup_google_sheets(self) -> bool:
        """Setup Google Sheets connection"""
        sheet_id = self.config.get('sheet_id')
        sheet_name = self.config.get('sheet_name', 'Jobs')
        
        if not sheet_id or sheet_id == "YOUR_GOOGLE_SHEET_ID_HERE":
            print("❌ Please update sheet_id in config.json")
            return False
        
        if not self.sheets_manager.client:
            print("❌ Google Sheets authentication failed")
            return False
        
        if not self.sheets_manager.connect_to_sheet(sheet_id, sheet_name):
            print("❌ Failed to connect to Google Sheet")
            return False
        
        return True
    
    def run_scraper(self, scraper_name: str, max_jobs: int) -> List[Dict]:
        """Run a specific scraper"""
        if scraper_name not in self.scrapers:
            print(f"❌ Scraper '{scraper_name}' not available")
            return []
        
        try:
            print(f"\n🚀 Running {scraper_name} scraper...")
            scraper = self.scrapers[scraper_name]
            jobs = scraper.scrape_jobs(max_jobs)
            print(f"✅ {scraper_name} completed: {len(jobs)} jobs found")
            return jobs
        except Exception as e:
            print(f"❌ Error running {scraper_name} scraper: {e}")
            return []
    
    def run_all_scrapers(self) -> List[Dict]:
        """Run all available scrapers"""
        print("🎯 Starting job scraping from all sources...")
        
        all_jobs = []
        max_jobs_per_site = self.config.get('max_jobs_per_site', 50)
        
        # Run each scraper
        for scraper_name in self.scrapers.keys():
            jobs = self.run_scraper(scraper_name, max_jobs_per_site)
            all_jobs.extend(jobs)
        
        print(f"\n📊 Total jobs collected: {len(all_jobs)}")
        return all_jobs
    
    def process_and_save_jobs(self, jobs: List[Dict]) -> Dict:
        """Process jobs and save to Google Sheets"""
        if not jobs:
            print("📝 No jobs to process")
            return {"total_jobs": 0, "new_jobs": 0, "duplicates": 0}
        
        print(f"\n🔄 Processing {len(jobs)} jobs...")
        
        # Get existing job URLs from sheet
        existing_urls = set()
        if self.sheets_manager.sheet:
            existing_urls = self.sheets_manager.get_existing_job_urls()
        
        # Remove duplicates
        unique_jobs = deduplicate_jobs(jobs, existing_urls)
        duplicates_removed = len(jobs) - len(unique_jobs)
        
        print(f"🔍 Removed {duplicates_removed} duplicates")
        print(f"📝 {len(unique_jobs)} new jobs to add")
        
        # Save to Google Sheets
        new_jobs_added = 0
        if unique_jobs and self.sheets_manager.sheet:
            new_jobs_added = self.sheets_manager.append_jobs(unique_jobs)
        
        return {
            "total_jobs": len(jobs),
            "new_jobs": new_jobs_added,
            "duplicates": duplicates_removed,
            "existing_jobs": len(existing_urls) if existing_urls else 0
        }
    
    def generate_summary_report(self, results: Dict) -> str:
        """Generate a summary report of the scraping session"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        report = f"""
📊 Job Scraping Summary Report
Generated: {timestamp}

🎯 Results:
• Total jobs found: {results['total_jobs']}
• New jobs added: {results['new_jobs']}
• Duplicates removed: {results['duplicates']}
• Existing jobs in sheet: {results['existing_jobs']}

🔍 Search Criteria:
• Keywords: {', '.join(self.config['keywords'])}
• Location: {self.config['location']}
• Max jobs per site: {self.config.get('max_jobs_per_site', 50)}

🌐 Sources Scraped:
• TimesJobs.com ✅
• LinkedIn Jobs ⚠️ (limited)
• Glassdoor ⚠️ (limited)
• Company Career Pages ✅
• Naukri.com (when available)
• Indeed.com (when available)

📈 Sheet Statistics:
"""
        
        # Add sheet stats if available
        if self.sheets_manager.sheet:
            stats = self.sheets_manager.get_job_stats()
            if stats:
                report += f"• Total jobs in sheet: {stats.get('total_jobs', 0)}\n"
                
                if 'by_source' in stats:
                    report += "• Jobs by source:\n"
                    for source, count in stats['by_source'].items():
                        report += f"  - {source}: {count}\n"
                
                if 'by_status' in stats:
                    report += "• Jobs by status:\n"
                    for status, count in stats['by_status'].items():
                        report += f"  - {status}: {count}\n"
        
        return report
    
    def run(self, scrapers_to_run: List[str] = None) -> Dict:
        """Main execution method"""
        print("🎯 Job Scraper Runner Starting...")
        print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Setup Google Sheets
        if not self.setup_google_sheets():
            print("❌ Cannot proceed without Google Sheets connection")
            return {"error": "Google Sheets setup failed"}
        
        # Run scrapers
        if scrapers_to_run:
            # Run specific scrapers
            all_jobs = []
            max_jobs_per_site = self.config.get('max_jobs_per_site', 50)
            for scraper_name in scrapers_to_run:
                jobs = self.run_scraper(scraper_name, max_jobs_per_site)
                all_jobs.extend(jobs)
        else:
            # Run all scrapers
            all_jobs = self.run_all_scrapers()
        
        # Process and save jobs
        if all_jobs:
            results = self.process_and_save_jobs(all_jobs)
        else:
            results = {
                "total_jobs": 0,
                "new_jobs": 0,
                "duplicates": 0,
                "existing_jobs": 0
            }
        
        # Generate and display summary
        summary = self.generate_summary_report(results)
        print(summary)
        
        # Save summary to file
        summary_file = f"scraping_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(summary)
        print(f"📄 Summary saved to: {summary_file}")
        
        print("🎉 Job scraping completed successfully!")
        return results


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Job Scraper Runner')
    parser.add_argument('--scrapers', nargs='+', 
                       choices=['naukri', 'indeed', 'timesjobs', 'linkedin', 'glassdoor', 'companies'], 
                       help='Specific scrapers to run (default: all)')
    parser.add_argument('--config', default='config.json',
                       help='Configuration file path')
    parser.add_argument('--test', action='store_true',
                       help='Run in test mode (limited jobs)')
    
    args = parser.parse_args()
    
    # Initialize runner
    runner = JobScraperRunner(args.config)
    
    # Adjust config for test mode
    if args.test:
        runner.config['max_jobs_per_site'] = 5
        print("🧪 Running in test mode (5 jobs per site)")
    
    # Run the scraper
    try:
        results = runner.run(args.scrapers)
        
        if 'error' in results:
            sys.exit(1)
        else:
            print(f"\n✅ Success! Added {results['new_jobs']} new jobs to your sheet")
            
    except KeyboardInterrupt:
        print("\n⏹️ Scraping interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
