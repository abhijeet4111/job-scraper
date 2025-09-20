"""
Naukri.com job scraper
"""
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import time
import random
from urllib.parse import urljoin, quote
from .utils import (
    get_random_user_agent, clean_text, extract_salary, 
    is_relevant_job, parse_date, safe_request, validate_job_data
)


class NaukriScraper:
    def __init__(self, config: Dict):
        self.config = config
        self.base_url = "https://www.naukri.com"
        self.session = requests.Session()
        
    def build_search_url(self, keywords: List[str], location: str, page: int = 1) -> str:
        """Build search URL for Naukri with given parameters"""
        # Join keywords with OR operator
        keyword_string = " OR ".join(keywords)
        
        # URL encode the search terms
        encoded_keywords = quote(keyword_string)
        encoded_location = quote(location)
        
        # Build the search URL
        search_url = f"{self.base_url}/jobs-in-{encoded_location}?k={encoded_keywords}&l={encoded_location}"
        
        if page > 1:
            search_url += f"&p={page}"
            
        return search_url
    
    def extract_job_details(self, job_element) -> Optional[Dict]:
        """Extract job details from a job listing element"""
        try:
            job_data = {}
            
            # Job Title
            title_elem = job_element.find('a', class_='title')
            if not title_elem:
                title_elem = job_element.find('h2') or job_element.find('h3')
            
            if title_elem:
                job_data['title'] = clean_text(title_elem.get_text())
                job_data['link'] = urljoin(self.base_url, title_elem.get('href', ''))
            else:
                return None
            
            # Company Name
            company_elem = job_element.find('a', class_='subTitle') or \
                          job_element.find('div', class_='companyInfo') or \
                          job_element.find('span', class_='companyName')
            
            if company_elem:
                job_data['company'] = clean_text(company_elem.get_text())
            else:
                job_data['company'] = "Not specified"
            
            # Location
            location_elem = job_element.find('span', class_='locationsContainer') or \
                           job_element.find('div', class_='location') or \
                           job_element.find('span', class_='location')
            
            if location_elem:
                job_data['location'] = clean_text(location_elem.get_text())
            else:
                job_data['location'] = self.config.get('location', 'Not specified')
            
            # Experience
            exp_elem = job_element.find('span', class_='expwdth') or \
                      job_element.find('div', class_='experience')
            
            if exp_elem:
                job_data['experience'] = clean_text(exp_elem.get_text())
            
            # Salary
            salary_elem = job_element.find('span', class_='salary') or \
                         job_element.find('div', class_='salary')
            
            if salary_elem:
                job_data['salary'] = clean_text(salary_elem.get_text())
            else:
                # Try to extract salary from job description
                desc_elem = job_element.find('div', class_='job-description') or \
                           job_element.find('span', class_='job-description')
                if desc_elem:
                    salary = extract_salary(desc_elem.get_text())
                    if salary:
                        job_data['salary'] = salary
            
            # Posted Date
            date_elem = job_element.find('span', class_='date') or \
                       job_element.find('div', class_='jobTupleFooter')
            
            if date_elem:
                date_text = clean_text(date_elem.get_text())
                parsed_date = parse_date(date_text)
                if parsed_date:
                    job_data['posted_date'] = parsed_date
            
            # Job Description (for relevance checking)
            desc_elem = job_element.find('div', class_='job-description') or \
                       job_element.find('span', class_='job-description') or \
                       job_element.find('div', class_='jobDescription')
            
            job_description = ""
            if desc_elem:
                job_description = clean_text(desc_elem.get_text())
            
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
            
            # Validate required fields
            if validate_job_data(job_data):
                return job_data
            else:
                return None
                
        except Exception as e:
            print(f"❌ Error extracting job details: {e}")
            return None
    
    def scrape_jobs(self, max_jobs: int = 50) -> List[Dict]:
        """Scrape jobs from Naukri.com"""
        print(f"🔍 Starting Naukri scraping for {max_jobs} jobs...")
        
        jobs = []
        page = 1
        max_pages = 5  # Limit to prevent excessive requests
        
        while len(jobs) < max_jobs and page <= max_pages:
            print(f"📄 Scraping Naukri page {page}...")
            
            # Build search URL
            search_url = self.build_search_url(
                self.config['keywords'], 
                self.config['location'], 
                page
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
            
            # Find job listings - try multiple selectors
            job_selectors = [
                'article[data-job-id]',
                'div.jobTuple',
                'div.srp-jobtuple-wrapper',
                'div.job-listing',
                'article.jobTuple'
            ]
            
            job_elements = []
            for selector in job_selectors:
                job_elements = soup.select(selector)
                if job_elements:
                    print(f"✅ Found {len(job_elements)} job elements using selector: {selector}")
                    break
            
            if not job_elements:
                print(f"❌ No job elements found on page {page}")
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
            
            # If no jobs found on this page, stop
            if page_jobs == 0:
                print("🛑 No more relevant jobs found, stopping...")
                break
            
            page += 1
            
            # Add delay between pages
            time.sleep(self.config.get('delay_between_requests', 2) + random.uniform(1, 3))
        
        print(f"🎉 Naukri scraping completed! Found {len(jobs)} relevant jobs")
        return jobs
    
    def get_job_details(self, job_url: str) -> Optional[Dict]:
        """Get detailed information for a specific job"""
        headers = {
            'User-Agent': get_random_user_agent(self.config['user_agents'])
        }
        
        response = safe_request(job_url, headers)
        if not response:
            return None
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        details = {}
        
        # Job Description
        desc_elem = soup.find('div', class_='job-description') or \
                   soup.find('section', class_='job-description')
        if desc_elem:
            details['full_description'] = clean_text(desc_elem.get_text())
        
        # Skills Required
        skills_elem = soup.find('div', class_='skills') or \
                     soup.find('section', class_='key-skill')
        if skills_elem:
            skills = [clean_text(skill.get_text()) for skill in skills_elem.find_all('a')]
            details['skills'] = ', '.join(skills)
        
        # Company Details
        company_elem = soup.find('div', class_='company-details')
        if company_elem:
            details['company_details'] = clean_text(company_elem.get_text())
        
        return details


def test_naukri_scraper():
    """Test the Naukri scraper"""
    import json
    
    # Load config
    with open('../config.json', 'r') as f:
        config = json.load(f)
    
    scraper = NaukriScraper(config)
    jobs = scraper.scrape_jobs(max_jobs=5)
    
    print(f"\n📊 Test Results:")
    print(f"Total jobs found: {len(jobs)}")
    
    for i, job in enumerate(jobs, 1):
        print(f"\n{i}. {job['title']}")
        print(f"   Company: {job['company']}")
        print(f"   Location: {job['location']}")
        print(f"   Link: {job['link']}")


if __name__ == "__main__":
    test_naukri_scraper()
