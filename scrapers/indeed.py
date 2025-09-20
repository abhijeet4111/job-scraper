"""
Indeed.com job scraper
"""
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import time
import random
from urllib.parse import urljoin, quote_plus
from .utils import (
    get_random_user_agent, clean_text, extract_salary, 
    is_relevant_job, parse_date, safe_request, validate_job_data
)


class IndeedScraper:
    def __init__(self, config: Dict):
        self.config = config
        self.base_url = "https://in.indeed.com"
        self.session = requests.Session()
        
    def build_search_url(self, keywords: List[str], location: str, start: int = 0) -> str:
        """Build search URL for Indeed with given parameters"""
        # Join keywords with space (Indeed handles OR automatically)
        keyword_string = " ".join(keywords)
        
        # URL encode the search terms
        encoded_keywords = quote_plus(keyword_string)
        encoded_location = quote_plus(location)
        
        # Build the search URL
        search_url = f"{self.base_url}/jobs?q={encoded_keywords}&l={encoded_location}"
        
        if start > 0:
            search_url += f"&start={start}"
            
        # Add filters for recent jobs
        search_url += "&fromage=7"  # Jobs from last 7 days
        search_url += "&sort=date"  # Sort by date
            
        return search_url
    
    def extract_job_details(self, job_element) -> Optional[Dict]:
        """Extract job details from a job listing element"""
        try:
            job_data = {}
            
            # Job Title and Link
            title_elem = job_element.find('h2', class_='jobTitle') or \
                        job_element.find('a', {'data-jk': True}) or \
                        job_element.find('span', {'title': True})
            
            if title_elem:
                # Get the actual link element
                link_elem = title_elem.find('a') if title_elem.name != 'a' else title_elem
                
                if link_elem:
                    job_data['title'] = clean_text(link_elem.get('title') or link_elem.get_text())
                    href = link_elem.get('href', '')
                    if href.startswith('/'):
                        job_data['link'] = urljoin(self.base_url, href)
                    else:
                        job_data['link'] = href
                else:
                    job_data['title'] = clean_text(title_elem.get_text())
                    job_data['link'] = ""
            else:
                return None
            
            # Company Name
            company_elem = job_element.find('span', class_='companyName') or \
                          job_element.find('a', {'data-testid': 'company-name'}) or \
                          job_element.find('div', class_='companyName')
            
            if company_elem:
                # Remove any nested elements like ratings
                company_text = company_elem.get_text()
                job_data['company'] = clean_text(company_text)
            else:
                job_data['company'] = "Not specified"
            
            # Location
            location_elem = job_element.find('div', class_='companyLocation') or \
                           job_element.find('span', class_='locationsContainer') or \
                           job_element.find('div', {'data-testid': 'job-location'})
            
            if location_elem:
                job_data['location'] = clean_text(location_elem.get_text())
            else:
                job_data['location'] = self.config.get('location', 'Not specified')
            
            # Salary
            salary_elem = job_element.find('span', class_='salary-snippet') or \
                         job_element.find('div', class_='salary-snippet-container') or \
                         job_element.find('span', {'data-testid': 'job-salary'})
            
            if salary_elem:
                job_data['salary'] = clean_text(salary_elem.get_text())
            
            # Job Summary/Description
            summary_elem = job_element.find('div', class_='job-snippet') or \
                          job_element.find('span', class_='summary') or \
                          job_element.find('div', {'data-testid': 'job-snippet'})
            
            job_description = ""
            if summary_elem:
                job_description = clean_text(summary_elem.get_text())
            
            # Posted Date
            date_elem = job_element.find('span', class_='date') or \
                       job_element.find('time') or \
                       job_element.find('span', {'data-testid': 'job-age'})
            
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
            job_data['source'] = 'Indeed'
            
            # Validate required fields
            if validate_job_data(job_data):
                return job_data
            else:
                return None
                
        except Exception as e:
            print(f"❌ Error extracting job details: {e}")
            return None
    
    def scrape_jobs(self, max_jobs: int = 50) -> List[Dict]:
        """Scrape jobs from Indeed.com"""
        print(f"🔍 Starting Indeed scraping for {max_jobs} jobs...")
        
        jobs = []
        start = 0
        jobs_per_page = 10  # Indeed typically shows 10 jobs per page
        max_pages = 5  # Limit to prevent excessive requests
        
        while len(jobs) < max_jobs and start < (max_pages * jobs_per_page):
            print(f"📄 Scraping Indeed page {(start // jobs_per_page) + 1}...")
            
            # Build search URL
            search_url = self.build_search_url(
                self.config['keywords'], 
                self.config['location'], 
                start
            )
            
            print(f"🌐 URL: {search_url}")
            
            # Make request with random user agent
            headers = {
                'User-Agent': get_random_user_agent(self.config['user_agents']),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Referer': 'https://in.indeed.com/',
            }
            
            response = safe_request(
                search_url, 
                headers, 
                self.config.get('delay_between_requests', 2),
                self.config.get('max_retries', 3)
            )
            
            if not response:
                print(f"❌ Failed to fetch page at start={start}")
                break
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find job listings - try multiple selectors
            job_selectors = [
                'div[data-jk]',  # Main job container
                'div.job_seen_beacon',  # Alternative selector
                'div.slider_container div.slider_item',  # Slider items
                'td.resultContent',  # Table-based layout
                'div.jobsearch-SerpJobCard'  # Older layout
            ]
            
            job_elements = []
            for selector in job_selectors:
                job_elements = soup.select(selector)
                if job_elements:
                    print(f"✅ Found {len(job_elements)} job elements using selector: {selector}")
                    break
            
            if not job_elements:
                print(f"❌ No job elements found at start={start}")
                # Try to find any div with job-related classes
                fallback_elements = soup.find_all('div', class_=lambda x: x and 'job' in x.lower())
                if fallback_elements:
                    print(f"🔄 Found {len(fallback_elements)} fallback elements")
                    job_elements = fallback_elements[:10]  # Limit to reasonable number
                else:
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
            
            print(f"📊 Page {(start // jobs_per_page) + 1}: Found {page_jobs} relevant jobs")
            
            # If no jobs found on this page, stop
            if page_jobs == 0:
                print("🛑 No more relevant jobs found, stopping...")
                break
            
            start += jobs_per_page
            
            # Add delay between pages
            time.sleep(self.config.get('delay_between_requests', 2) + random.uniform(1, 3))
        
        print(f"🎉 Indeed scraping completed! Found {len(jobs)} relevant jobs")
        return jobs
    
    def get_job_details(self, job_url: str) -> Optional[Dict]:
        """Get detailed information for a specific job"""
        headers = {
            'User-Agent': get_random_user_agent(self.config['user_agents']),
            'Referer': 'https://in.indeed.com/'
        }
        
        response = safe_request(job_url, headers)
        if not response:
            return None
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        details = {}
        
        # Job Description
        desc_elem = soup.find('div', class_='jobsearch-jobDescriptionText') or \
                   soup.find('div', id='jobDescriptionText') or \
                   soup.find('div', class_='job-description')
        
        if desc_elem:
            details['full_description'] = clean_text(desc_elem.get_text())
        
        # Company Information
        company_elem = soup.find('div', class_='jobsearch-CompanyInfoContainer')
        if company_elem:
            details['company_info'] = clean_text(company_elem.get_text())
        
        # Job Type (Full-time, Part-time, etc.)
        job_type_elem = soup.find('span', class_='jobsearch-JobMetadataHeader-item')
        if job_type_elem:
            details['job_type'] = clean_text(job_type_elem.get_text())
        
        return details


def test_indeed_scraper():
    """Test the Indeed scraper"""
    import json
    
    # Load config
    with open('../config.json', 'r') as f:
        config = json.load(f)
    
    scraper = IndeedScraper(config)
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
    test_indeed_scraper()
