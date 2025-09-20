"""
TimesJobs.com scraper - Alternative to Naukri
"""
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import time
import random
from urllib.parse import urljoin, quote_plus
try:
    from .utils import (
        get_random_user_agent, clean_text, extract_salary, 
        is_relevant_job, parse_date, safe_request, validate_job_data
    )
except ImportError:
    from utils import (
        get_random_user_agent, clean_text, extract_salary, 
        is_relevant_job, parse_date, safe_request, validate_job_data
    )


class TimesJobsScraper:
    def __init__(self, config: Dict):
        self.config = config
        self.base_url = "https://www.timesjobs.com"
        
    def build_search_url(self, keywords: List[str], location: str, page: int = 1) -> str:
        """Build search URL for TimesJobs"""
        # TimesJobs uses a different URL structure
        # Example: https://www.timesjobs.com/candidate/job-search.html?searchType=personalizedSearch&from=submit&txtKeywords=sap&txtLocation=pune
        
        keyword_string = " ".join(keywords[:3])  # Use first 3 keywords to avoid long URLs
        
        search_url = f"{self.base_url}/candidate/job-search.html"
        params = {
            'searchType': 'personalizedSearch',
            'from': 'submit',
            'txtKeywords': keyword_string,
            'txtLocation': location,
            'cboWorkExp1': '0',  # Min experience
            'cboWorkExp2': '10'  # Max experience
        }
        
        # Build URL with parameters
        param_string = "&".join([f"{k}={quote_plus(str(v))}" for k, v in params.items()])
        full_url = f"{search_url}?{param_string}"
        
        if page > 1:
            full_url += f"&sequence={page}"
            
        return full_url
    
    def extract_job_details(self, job_element) -> Optional[Dict]:
        """Extract job details from a TimesJobs listing"""
        try:
            job_data = {}
            
            # Job Title and Link
            title_elem = job_element.find('h2') or job_element.find('h3')
            if title_elem:
                link_elem = title_elem.find('a')
                if link_elem:
                    job_data['title'] = clean_text(link_elem.get_text())
                    href = link_elem.get('href', '')
                    if href.startswith('http'):
                        job_data['link'] = href
                    elif href.startswith('/'):
                        job_data['link'] = urljoin(self.base_url, href)
                    else:
                        job_data['link'] = f"{self.base_url}/{href}"
                else:
                    job_data['title'] = clean_text(title_elem.get_text())
                    job_data['link'] = ""
            else:
                return None
            
            # Company Name
            company_elem = job_element.find('h3', class_='joblist-comp-name') or \
                          job_element.find('span', class_='comp-name') or \
                          job_element.find('div', class_='comp-name')
            
            if company_elem:
                # Remove any nested links and get clean text
                company_text = company_elem.get_text()
                job_data['company'] = clean_text(company_text)
            else:
                job_data['company'] = "Not specified"
            
            # Location
            location_elem = job_element.find('span', class_='loc') or \
                           job_element.find('div', class_='location') or \
                           job_element.find('span', string=lambda text: text and 'pune' in text.lower())
            
            if location_elem:
                job_data['location'] = clean_text(location_elem.get_text())
            else:
                job_data['location'] = self.config.get('location', 'Not specified')
            
            # Experience
            exp_elem = job_element.find('span', class_='exp') or \
                      job_element.find('div', class_='experience')
            
            if exp_elem:
                job_data['experience'] = clean_text(exp_elem.get_text())
            
            # Salary
            salary_elem = job_element.find('span', class_='sal') or \
                         job_element.find('div', class_='salary')
            
            if salary_elem:
                job_data['salary'] = clean_text(salary_elem.get_text())
            
            # Job Description
            desc_elem = job_element.find('div', class_='job-description') or \
                       job_element.find('span', class_='list-job-dtl') or \
                       job_element.find('ul', class_='list-job-dtl')
            
            job_description = ""
            if desc_elem:
                job_description = clean_text(desc_elem.get_text())
            
            # Posted Date
            date_elem = job_element.find('span', class_='sim-posted') or \
                       job_element.find('div', class_='posted-date')
            
            if date_elem:
                date_text = clean_text(date_elem.get_text())
                parsed_date = parse_date(date_text)
                if parsed_date:
                    job_data['posted_date'] = parsed_date
            
            # Check relevance
            if not is_relevant_job(
                job_data.get('title', ''), 
                job_description, 
                self.config['keywords'], 
                self.config['exclude_keywords']
            ):
                return None
            
            # Set source
            job_data['source'] = 'TimesJobs'
            
            # Validate required fields
            if validate_job_data(job_data):
                return job_data
            else:
                return None
                
        except Exception as e:
            print(f"❌ Error extracting job details: {e}")
            return None
    
    def scrape_jobs(self, max_jobs: int = 50) -> List[Dict]:
        """Scrape jobs from TimesJobs.com"""
        print(f"🔍 Starting TimesJobs scraping for {max_jobs} jobs...")
        
        jobs = []
        page = 1
        max_pages = 3
        
        while len(jobs) < max_jobs and page <= max_pages:
            print(f"📄 Scraping TimesJobs page {page}...")
            
            # Build search URL
            search_url = self.build_search_url(
                self.config['keywords'], 
                self.config['location'], 
                page
            )
            
            print(f"🌐 URL: {search_url}")
            
            # Make request
            headers = {
                'User-Agent': get_random_user_agent(self.config['user_agents']),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Referer': 'https://www.timesjobs.com/',
            }
            
            response = safe_request(
                search_url, 
                headers, 
                self.config.get('delay_between_requests', 2),
                self.config.get('max_retries', 3)
            )
            
            if not response:
                print(f"❌ Failed to fetch page {page}")
                break
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find job listings
            job_selectors = [
                'li[class*="clearfix job-bx"]',
                'div[class*="job-bx"]',
                'li.clearfix',
                'div.job-listing',
                'li[id*="job"]'
            ]
            
            job_elements = []
            for selector in job_selectors:
                job_elements = soup.select(selector)
                if job_elements:
                    print(f"✅ Found {len(job_elements)} job elements using selector: {selector}")
                    break
            
            if not job_elements:
                print(f"❌ No job elements found on page {page}")
                # Debug: check page content
                if 'job' in response.text.lower():
                    print("📝 Page contains 'job' text but no structured elements")
                break
            
            # Extract job details
            page_jobs = 0
            for job_element in job_elements:
                if len(jobs) >= max_jobs:
                    break
                
                job_data = self.extract_job_details(job_element)
                if job_data:
                    jobs.append(job_data)
                    page_jobs += 1
                    print(f"✅ Extracted: {job_data['title']} at {job_data['company']}")
            
            print(f"📊 Page {page}: Found {page_jobs} relevant jobs")
            
            if page_jobs == 0:
                print("🛑 No more relevant jobs found, stopping...")
                break
            
            page += 1
            
            # Add delay between pages
            time.sleep(self.config.get('delay_between_requests', 2) + random.uniform(1, 3))
        
        print(f"🎉 TimesJobs scraping completed! Found {len(jobs)} relevant jobs")
        return jobs


def test_timesjobs_scraper():
    """Test the TimesJobs scraper"""
    import json
    
    # Load config
    with open('../config.json', 'r') as f:
        config = json.load(f)
    
    scraper = TimesJobsScraper(config)
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
    test_timesjobs_scraper()
