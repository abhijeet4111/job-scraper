"""
Improved Naukri.com job scraper using Playwright for dynamic content
"""
from playwright.sync_api import sync_playwright
from typing import List, Dict, Optional
import time
import random
from urllib.parse import urljoin, quote_plus
try:
    from .utils import (
        clean_text, extract_salary, is_relevant_job, 
        parse_date, validate_job_data
    )
except ImportError:
    from utils import (
        clean_text, extract_salary, is_relevant_job, 
        parse_date, validate_job_data
    )


class NaukriPlaywrightScraper:
    def __init__(self, config: Dict):
        self.config = config
        self.base_url = "https://www.naukri.com"
        
    def build_search_url(self, keywords: List[str], location: str, page: int = 1) -> str:
        """Build search URL for Naukri with given parameters"""
        # Try simpler URL formats that are less likely to be blocked
        simple_keywords = ["sap", "analyst", "consultant"]  # Use simpler, common terms
        
        # Use the basic job search format
        search_url = f"{self.base_url}/sap-jobs-in-pune"
        
        return search_url
    
    def extract_job_details(self, job_element, page) -> Optional[Dict]:
        """Extract job details from a job listing element using Playwright"""
        try:
            job_data = {}
            
            # Job Title and Link - try multiple selectors
            title_selectors = [
                'a[title]',
                '.title a',
                'h2 a',
                'h3 a',
                '.jobTitle a',
                'a[data-job-title]'
            ]
            
            title_element = None
            for selector in title_selectors:
                try:
                    title_element = job_element.query_selector(selector)
                    if title_element:
                        break
                except:
                    continue
            
            if title_element:
                job_data['title'] = clean_text(title_element.get_attribute('title') or title_element.inner_text())
                href = title_element.get_attribute('href')
                if href:
                    if href.startswith('/'):
                        job_data['link'] = urljoin(self.base_url, href)
                    else:
                        job_data['link'] = href
                else:
                    job_data['link'] = ""
            else:
                # Try to get title from text content
                title_text = job_element.inner_text()
                if title_text and len(title_text.split('\n')) > 0:
                    job_data['title'] = clean_text(title_text.split('\n')[0])
                    job_data['link'] = ""
                else:
                    return None
            
            # Company Name - try multiple selectors
            company_selectors = [
                '.companyName',
                '.company',
                '.subTitle',
                'a[title*="company"]',
                '.org',
                '.companyInfo'
            ]
            
            company_element = None
            for selector in company_selectors:
                try:
                    company_element = job_element.query_selector(selector)
                    if company_element:
                        break
                except:
                    continue
            
            if company_element:
                job_data['company'] = clean_text(company_element.inner_text())
            else:
                job_data['company'] = "Not specified"
            
            # Location - try multiple selectors
            location_selectors = [
                '.location',
                '.locationsContainer',
                '.jobLocation',
                '[class*="location"]'
            ]
            
            location_element = None
            for selector in location_selectors:
                try:
                    location_element = job_element.query_selector(selector)
                    if location_element:
                        break
                except:
                    continue
            
            if location_element:
                job_data['location'] = clean_text(location_element.inner_text())
            else:
                job_data['location'] = self.config.get('location', 'Not specified')
            
            # Experience
            exp_selectors = [
                '.experience',
                '.expwdth',
                '[class*="exp"]'
            ]
            
            for selector in exp_selectors:
                try:
                    exp_element = job_element.query_selector(selector)
                    if exp_element:
                        job_data['experience'] = clean_text(exp_element.inner_text())
                        break
                except:
                    continue
            
            # Salary
            salary_selectors = [
                '.salary',
                '.ctc',
                '[class*="salary"]'
            ]
            
            for selector in salary_selectors:
                try:
                    salary_element = job_element.query_selector(selector)
                    if salary_element:
                        job_data['salary'] = clean_text(salary_element.inner_text())
                        break
                except:
                    continue
            
            # Job Description (for relevance checking)
            desc_selectors = [
                '.job-description',
                '.jobDescription',
                '.summary',
                '.snippet'
            ]
            
            job_description = ""
            for selector in desc_selectors:
                try:
                    desc_element = job_element.query_selector(selector)
                    if desc_element:
                        job_description = clean_text(desc_element.inner_text())
                        break
                except:
                    continue
            
            # If no description found, use all text content
            if not job_description:
                job_description = clean_text(job_element.inner_text())
            
            # Check relevance
            if not is_relevant_job(
                job_data.get('title', ''), 
                job_description, 
                self.config['keywords'], 
                self.config['exclude_keywords']
            ):
                return None
            
            # Set source
            job_data['source'] = 'Naukri'
            
            # Set posted date (default to today if not found)
            if 'posted_date' not in job_data:
                from datetime import datetime
                job_data['posted_date'] = datetime.now().strftime('%Y-%m-%d')
            
            # Validate required fields
            if validate_job_data(job_data):
                return job_data
            else:
                return None
                
        except Exception as e:
            print(f"❌ Error extracting job details: {e}")
            return None
    
    def scrape_jobs(self, max_jobs: int = 50) -> List[Dict]:
        """Scrape jobs from Naukri.com using Playwright"""
        print(f"🔍 Starting Naukri Playwright scraping for {max_jobs} jobs...")
        
        jobs = []
        
        with sync_playwright() as p:
            # Launch browser with stealth settings
            browser = p.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-blink-features=AutomationControlled',
                    '--disable-web-security',
                    '--disable-features=VizDisplayCompositor'
                ]
            )
            
            # Create context with realistic settings
            context = browser.new_context(
                user_agent=random.choice(self.config['user_agents']),
                viewport={'width': 1920, 'height': 1080},
                extra_http_headers={
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                }
            )
            
            page = context.new_page()
            
            try:
                page_num = 1
                max_pages = 3  # Limit pages to avoid excessive requests
                
                while len(jobs) < max_jobs and page_num <= max_pages:
                    print(f"📄 Scraping Naukri page {page_num}...")
                    
                    # Build search URL
                    search_url = self.build_search_url(
                        self.config['keywords'], 
                        self.config['location'], 
                        page_num
                    )
                    
                    print(f"🌐 URL: {search_url}")
                    
                    # Navigate to page
                    try:
                        page.goto(search_url, wait_until='networkidle', timeout=30000)
                        
                        # Wait a bit for dynamic content
                        page.wait_for_timeout(3000)
                        
                        # Try multiple job listing selectors
                        job_selectors = [
                            'article[data-job-id]',
                            '.jobTuple',
                            '.srp-jobtuple-wrapper',
                            '.job-listing',
                            'article.jobTuple',
                            '[class*="job"][class*="card"]',
                            '[class*="job"][class*="item"]',
                            'div[data-job-id]'
                        ]
                        
                        job_elements = []
                        for selector in job_selectors:
                            try:
                                elements = page.query_selector_all(selector)
                                if elements:
                                    job_elements = elements
                                    print(f"✅ Found {len(job_elements)} job elements using selector: {selector}")
                                    break
                            except:
                                continue
                        
                        # If no specific job selectors work, try generic approach
                        if not job_elements:
                            print("🔄 Trying generic selectors...")
                            generic_selectors = [
                                'div[class*="job"]',
                                'article',
                                'div[data-*]',
                                '.card',
                                '.item'
                            ]
                            
                            for selector in generic_selectors:
                                try:
                                    elements = page.query_selector_all(selector)
                                    if elements and len(elements) > 5:  # Likely job listings
                                        job_elements = elements[:20]  # Limit to reasonable number
                                        print(f"✅ Found {len(job_elements)} elements using generic selector: {selector}")
                                        break
                                except:
                                    continue
                        
                        if not job_elements:
                            print(f"❌ No job elements found on page {page_num}")
                            
                            # Debug: save page content
                            page_content = page.content()
                            if 'job' in page_content.lower():
                                print("📝 Page contains 'job' text, but no structured elements found")
                                # Try to extract any text that looks like job titles
                                all_text = page.inner_text('body')
                                lines = [line.strip() for line in all_text.split('\n') if line.strip()]
                                print(f"📄 Page has {len(lines)} text lines")
                                
                                # Look for lines that might be job titles
                                potential_jobs = []
                                for line in lines[:50]:  # Check first 50 lines
                                    if any(keyword.lower() in line.lower() for keyword in self.config['keywords']):
                                        potential_jobs.append(line)
                                
                                if potential_jobs:
                                    print(f"🔍 Found {len(potential_jobs)} potential job matches in text:")
                                    for job in potential_jobs[:5]:
                                        print(f"  - {job[:100]}...")
                            
                            break
                        
                        # Extract job details
                        page_jobs = 0
                        for job_element in job_elements:
                            if len(jobs) >= max_jobs:
                                break
                            
                            job_data = self.extract_job_details(job_element, page)
                            if job_data:
                                jobs.append(job_data)
                                page_jobs += 1
                                print(f"✅ Extracted: {job_data['title']} at {job_data['company']}")
                        
                        print(f"📊 Page {page_num}: Found {page_jobs} relevant jobs")
                        
                        # If no jobs found on this page, stop
                        if page_jobs == 0:
                            print("🛑 No more relevant jobs found, stopping...")
                            break
                        
                        page_num += 1
                        
                        # Add delay between pages
                        if page_num <= max_pages:
                            delay = self.config.get('delay_between_requests', 2) + random.uniform(1, 3)
                            print(f"⏳ Waiting {delay:.1f} seconds before next page...")
                            time.sleep(delay)
                        
                    except Exception as e:
                        print(f"❌ Error on page {page_num}: {e}")
                        break
                
            finally:
                browser.close()
        
        print(f"🎉 Naukri Playwright scraping completed! Found {len(jobs)} relevant jobs")
        return jobs


def test_naukri_playwright():
    """Test the Naukri Playwright scraper"""
    import json
    
    # Load config
    with open('../config.json', 'r') as f:
        config = json.load(f)
    
    scraper = NaukriPlaywrightScraper(config)
    jobs = scraper.scrape_jobs(max_jobs=5)
    
    print(f"\n📊 Test Results:")
    print(f"Total jobs found: {len(jobs)}")
    
    for i, job in enumerate(jobs, 1):
        print(f"\n{i}. {job['title']}")
        print(f"   Company: {job['company']}")
        print(f"   Location: {job['location']}")
        print(f"   Link: {job['link']}")
        if 'salary' in job:
            print(f"   Salary: {job['salary']}")


if __name__ == "__main__":
    test_naukri_playwright()
