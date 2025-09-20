"""
Glassdoor Jobs scraper
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


class GlassdoorScraper:
    def __init__(self, config: Dict):
        self.config = config
        self.base_url = "https://www.glassdoor.co.in"
        
    def build_search_url(self, keywords: List[str], location: str, page: int = 1) -> str:
        """Build Glassdoor search URL"""
        keyword_string = " ".join(keywords[:3])
        
        # Glassdoor India job search URL
        search_url = f"{self.base_url}/Job/jobs.htm"
        
        params = {
            'sc.keyword': keyword_string,
            'locT': 'C',
            'locId': '1146732',  # Pune location ID
            'jobType': '',
            'fromAge': 1,  # Jobs from last day
            'minSalary': 0,
            'includeNoSalaryJobs': 'true',
            'radius': 25,
            'cityId': -1,
            'minRating': 0.0,
            'industryId': -1,
            'sgocId': -1,
            'seniorityType': '',
            'companyId': -1,
            'employerSizes': '',
            'applicationType': '',
            'remoteWorkType': 0
        }
        
        if page > 1:
            params['p'] = page
        
        # Build URL
        param_string = "&".join([f"{k}={quote_plus(str(v))}" for k, v in params.items()])
        return f"{search_url}?{param_string}"
    
    def extract_job_details(self, job_element, page) -> Optional[Dict]:
        """Extract job details from Glassdoor listing"""
        try:
            job_data = {}
            
            # Job Title and Link
            title_selectors = [
                'a[data-test="job-title"]',
                '.jobTitle a',
                'h2 a',
                'a[data-test="job-link"]'
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
                job_data['title'] = clean_text(title_element.inner_text())
                href = title_element.get_attribute('href')
                if href:
                    if href.startswith('/'):
                        job_data['link'] = urljoin(self.base_url, href)
                    else:
                        job_data['link'] = href
                else:
                    job_data['link'] = ""
            else:
                return None
            
            # Company Name
            company_selectors = [
                'span[data-test="employer-name"]',
                '.employerName',
                'a[data-test="employer-short-name"]'
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
            
            # Location
            location_selectors = [
                'div[data-test="job-location"]',
                '.jobLocation',
                'span[data-test="job-location"]'
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
            
            # Salary
            salary_selectors = [
                'span[data-test="detailSalary"]',
                '.salaryText',
                'div[data-test="salary-estimate"]'
            ]
            
            for selector in salary_selectors:
                try:
                    salary_element = job_element.query_selector(selector)
                    if salary_element:
                        job_data['salary'] = clean_text(salary_element.inner_text())
                        break
                except:
                    continue
            
            # Job Description/Summary
            desc_selectors = [
                'div[data-test="job-description"]',
                '.jobDescription',
                '.jobSummary'
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
            
            # Posted Date
            date_selectors = [
                'div[data-test="job-age"]',
                '.jobAge',
                'span[data-test="job-posted-date"]'
            ]
            
            for selector in date_selectors:
                try:
                    date_element = job_element.query_selector(selector)
                    if date_element:
                        date_text = clean_text(date_element.inner_text())
                        parsed_date = parse_date(date_text)
                        if parsed_date:
                            job_data['posted_date'] = parsed_date
                            break
                except:
                    continue
            
            # Check relevance
            if not is_relevant_job(
                job_data.get('title', ''), 
                job_description, 
                self.config['keywords'], 
                self.config['exclude_keywords']
            ):
                return None
            
            # Set source
            job_data['source'] = 'Glassdoor'
            
            # Set default posted date if not found
            if 'posted_date' not in job_data:
                from datetime import datetime
                job_data['posted_date'] = datetime.now().strftime('%Y-%m-%d')
            
            # Validate required fields
            if validate_job_data(job_data):
                return job_data
            else:
                return None
                
        except Exception as e:
            print(f"❌ Error extracting Glassdoor job details: {e}")
            return None
    
    def scrape_jobs(self, max_jobs: int = 50) -> List[Dict]:
        """Scrape jobs from Glassdoor"""
        print(f"🔍 Starting Glassdoor scraping for {max_jobs} jobs...")
        
        jobs = []
        
        with sync_playwright() as p:
            # Launch browser
            browser = p.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-blink-features=AutomationControlled'
                ]
            )
            
            context = browser.new_context(
                user_agent=random.choice(self.config['user_agents']),
                viewport={'width': 1920, 'height': 1080}
            )
            
            page = context.new_page()
            
            try:
                page_num = 1
                max_pages = 2  # Limit pages
                
                while len(jobs) < max_jobs and page_num <= max_pages:
                    print(f"📄 Scraping Glassdoor page {page_num}...")
                    
                    search_url = self.build_search_url(
                        self.config['keywords'], 
                        self.config['location'], 
                        page_num
                    )
                    
                    print(f"🌐 URL: {search_url}")
                    
                    page.goto(search_url, wait_until='networkidle', timeout=30000)
                    time.sleep(random.uniform(3, 5))
                    
                    # Handle potential popups or overlays
                    try:
                        # Close any modal dialogs
                        close_buttons = page.query_selector_all('button[aria-label="Close"], .modal-close, .close-button')
                        for button in close_buttons:
                            try:
                                button.click()
                                time.sleep(1)
                            except:
                                pass
                    except:
                        pass
                    
                    # Find job listings
                    job_selectors = [
                        'li[data-test="jobListing"]',
                        '.react-job-listing',
                        '.jobContainer',
                        'article[data-test="jobListing"]',
                        '.job-search-card'
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
                    
                    if not job_elements:
                        print(f"❌ No job elements found on page {page_num}")
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
                    
                    if page_jobs == 0:
                        break
                    
                    page_num += 1
                    time.sleep(random.uniform(2, 4))
                
            except Exception as e:
                print(f"❌ Glassdoor scraping error: {e}")
                
            finally:
                browser.close()
        
        print(f"🎉 Glassdoor scraping completed! Found {len(jobs)} relevant jobs")
        return jobs


def test_glassdoor_scraper():
    """Test Glassdoor scraper"""
    import json
    
    # Load config
    with open('../config.json', 'r') as f:
        config = json.load(f)
    
    scraper = GlassdoorScraper(config)
    jobs = scraper.scrape_jobs(max_jobs=3)
    
    print(f"\n📊 Glassdoor Test Results:")
    print(f"Total jobs found: {len(jobs)}")
    
    for i, job in enumerate(jobs, 1):
        print(f"\n{i}. {job['title']}")
        print(f"   Company: {job['company']}")
        print(f"   Location: {job['location']}")
        print(f"   Link: {job['link']}")
        if 'salary' in job:
            print(f"   Salary: {job['salary']}")


if __name__ == "__main__":
    test_glassdoor_scraper()
