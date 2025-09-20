"""
Company career page scrapers for major IT companies in Pune
"""
import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
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


class CompanyCareersScraper:
    def __init__(self, config: Dict):
        self.config = config
        self.companies = {
            'infosys': {
                'name': 'Infosys',
                'url': 'https://www.infosys.com/careers/job-search.html',
                'location_filter': 'pune',
                'method': 'playwright'  # Some need browser automation
            },
            'tcs': {
                'name': 'TCS',
                'url': 'https://www.tcs.com/careers/tcs-careers-search',
                'location_filter': 'pune',
                'method': 'requests'
            },
            'wipro': {
                'name': 'Wipro',
                'url': 'https://careers.wipro.com/careers-home/jobs',
                'location_filter': 'pune',
                'method': 'playwright'
            },
            'techm': {
                'name': 'Tech Mahindra',
                'url': 'https://careers.techmahindra.com/job-search/',
                'location_filter': 'pune',
                'method': 'requests'
            },
            'capgemini': {
                'name': 'Capgemini',
                'url': 'https://www.capgemini.com/careers/job-search/',
                'location_filter': 'pune',
                'method': 'playwright'
            }
        }
    
    def scrape_infosys_jobs(self, max_jobs: int = 10) -> List[Dict]:
        """Scrape jobs from Infosys careers page"""
        print("🔍 Scraping Infosys careers...")
        jobs = []
        
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(
                    user_agent=random.choice(self.config['user_agents'])
                )
                page = context.new_page()
                
                # Navigate to Infosys careers
                page.goto(self.companies['infosys']['url'], timeout=30000)
                time.sleep(3)
                
                # Look for job listings
                job_selectors = [
                    '.job-card',
                    '.career-opportunity',
                    '.job-listing',
                    'div[class*="job"]'
                ]
                
                for selector in job_selectors:
                    try:
                        elements = page.query_selector_all(selector)
                        if elements:
                            print(f"✅ Found {len(elements)} Infosys job elements")
                            
                            for element in elements[:max_jobs]:
                                try:
                                    # Extract basic job info
                                    title_elem = element.query_selector('h3, h4, .title, .job-title')
                                    if title_elem:
                                        title = clean_text(title_elem.inner_text())
                                        
                                        # Check if relevant
                                        if is_relevant_job(title, "", self.config['keywords'], self.config['exclude_keywords']):
                                            job_data = {
                                                'title': title,
                                                'company': 'Infosys',
                                                'location': 'Pune, Maharashtra',
                                                'link': self.companies['infosys']['url'],
                                                'source': 'Infosys Careers',
                                                'posted_date': time.strftime('%Y-%m-%d')
                                            }
                                            
                                            if validate_job_data(job_data):
                                                jobs.append(job_data)
                                                print(f"✅ Found Infosys job: {title}")
                                except:
                                    continue
                            break
                    except:
                        continue
                
                browser.close()
                
        except Exception as e:
            print(f"❌ Error scraping Infosys: {e}")
        
        return jobs
    
    def scrape_tcs_jobs(self, max_jobs: int = 10) -> List[Dict]:
        """Scrape jobs from TCS careers page"""
        print("🔍 Scraping TCS careers...")
        jobs = []
        
        try:
            headers = {
                'User-Agent': get_random_user_agent(self.config['user_agents']),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            }
            
            # TCS often has API endpoints for job search
            api_urls = [
                'https://www.tcs.com/careers/tcs-careers-search',
                'https://careers.tcs.com/job-search'
            ]
            
            for url in api_urls:
                try:
                    response = safe_request(url, headers)
                    if response:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        # Look for job listings
                        job_elements = soup.find_all(['div', 'article'], class_=lambda x: x and 'job' in x.lower())
                        
                        if job_elements:
                            print(f"✅ Found {len(job_elements)} TCS job elements")
                            
                            for element in job_elements[:max_jobs]:
                                try:
                                    title_elem = element.find(['h2', 'h3', 'h4'])
                                    if title_elem:
                                        title = clean_text(title_elem.get_text())
                                        
                                        if is_relevant_job(title, "", self.config['keywords'], self.config['exclude_keywords']):
                                            job_data = {
                                                'title': title,
                                                'company': 'TCS',
                                                'location': 'Pune, Maharashtra',
                                                'link': url,
                                                'source': 'TCS Careers',
                                                'posted_date': time.strftime('%Y-%m-%d')
                                            }
                                            
                                            if validate_job_data(job_data):
                                                jobs.append(job_data)
                                                print(f"✅ Found TCS job: {title}")
                                except:
                                    continue
                            break
                except:
                    continue
                    
        except Exception as e:
            print(f"❌ Error scraping TCS: {e}")
        
        return jobs
    
    def scrape_generic_company(self, company_key: str, max_jobs: int = 5) -> List[Dict]:
        """Generic company scraper for other companies"""
        company_info = self.companies.get(company_key)
        if not company_info:
            return []
        
        print(f"🔍 Scraping {company_info['name']} careers...")
        jobs = []
        
        try:
            if company_info['method'] == 'playwright':
                with sync_playwright() as p:
                    browser = p.chromium.launch(headless=True)
                    context = browser.new_context(
                        user_agent=random.choice(self.config['user_agents'])
                    )
                    page = context.new_page()
                    
                    page.goto(company_info['url'], timeout=30000)
                    time.sleep(3)
                    
                    # Generic job selectors
                    job_selectors = [
                        'div[class*="job"]',
                        'article[class*="job"]',
                        '.career-opportunity',
                        '.job-listing',
                        '.position'
                    ]
                    
                    for selector in job_selectors:
                        try:
                            elements = page.query_selector_all(selector)
                            if elements:
                                print(f"✅ Found {len(elements)} {company_info['name']} job elements")
                                
                                for element in elements[:max_jobs]:
                                    try:
                                        title_elem = element.query_selector('h1, h2, h3, h4, .title, .job-title')
                                        if title_elem:
                                            title = clean_text(title_elem.inner_text())
                                            
                                            if is_relevant_job(title, "", self.config['keywords'], self.config['exclude_keywords']):
                                                job_data = {
                                                    'title': title,
                                                    'company': company_info['name'],
                                                    'location': 'Pune, Maharashtra',
                                                    'link': company_info['url'],
                                                    'source': f"{company_info['name']} Careers",
                                                    'posted_date': time.strftime('%Y-%m-%d')
                                                }
                                                
                                                if validate_job_data(job_data):
                                                    jobs.append(job_data)
                                                    print(f"✅ Found {company_info['name']} job: {title}")
                                    except:
                                        continue
                                break
                        except:
                            continue
                    
                    browser.close()
            
            else:  # requests method
                headers = {
                    'User-Agent': get_random_user_agent(self.config['user_agents'])
                }
                
                response = safe_request(company_info['url'], headers)
                if response:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    job_elements = soup.find_all(['div', 'article'], class_=lambda x: x and 'job' in x.lower())
                    
                    if job_elements:
                        print(f"✅ Found {len(job_elements)} {company_info['name']} job elements")
                        
                        for element in job_elements[:max_jobs]:
                            try:
                                title_elem = element.find(['h1', 'h2', 'h3', 'h4'])
                                if title_elem:
                                    title = clean_text(title_elem.get_text())
                                    
                                    if is_relevant_job(title, "", self.config['keywords'], self.config['exclude_keywords']):
                                        job_data = {
                                            'title': title,
                                            'company': company_info['name'],
                                            'location': 'Pune, Maharashtra',
                                            'link': company_info['url'],
                                            'source': f"{company_info['name']} Careers",
                                            'posted_date': time.strftime('%Y-%m-%d')
                                        }
                                        
                                        if validate_job_data(job_data):
                                            jobs.append(job_data)
                                            print(f"✅ Found {company_info['name']} job: {title}")
                            except:
                                continue
                                
        except Exception as e:
            print(f"❌ Error scraping {company_info['name']}: {e}")
        
        return jobs
    
    def scrape_jobs(self, max_jobs: int = 25) -> List[Dict]:
        """Scrape jobs from all company career pages"""
        print(f"🔍 Starting company careers scraping for {max_jobs} jobs...")
        
        all_jobs = []
        jobs_per_company = max(2, max_jobs // len(self.companies))
        
        # Scrape major companies
        try:
            # Infosys (custom scraper)
            infosys_jobs = self.scrape_infosys_jobs(jobs_per_company)
            all_jobs.extend(infosys_jobs)
            
            # TCS (custom scraper)
            tcs_jobs = self.scrape_tcs_jobs(jobs_per_company)
            all_jobs.extend(tcs_jobs)
            
            # Other companies (generic scraper)
            for company_key in ['wipro', 'techm', 'capgemini']:
                if len(all_jobs) < max_jobs:
                    company_jobs = self.scrape_generic_company(company_key, jobs_per_company)
                    all_jobs.extend(company_jobs)
                    
                    # Add delay between companies
                    time.sleep(random.uniform(2, 4))
            
        except Exception as e:
            print(f"❌ Error in company careers scraping: {e}")
        
        print(f"🎉 Company careers scraping completed! Found {len(all_jobs)} relevant jobs")
        return all_jobs[:max_jobs]  # Limit to requested number


def test_company_scraper():
    """Test company careers scraper"""
    import json
    
    # Load config
    with open('../config.json', 'r') as f:
        config = json.load(f)
    
    scraper = CompanyCareersScraper(config)
    jobs = scraper.scrape_jobs(max_jobs=5)
    
    print(f"\n📊 Company Careers Test Results:")
    print(f"Total jobs found: {len(jobs)}")
    
    for i, job in enumerate(jobs, 1):
        print(f"\n{i}. {job['title']}")
        print(f"   Company: {job['company']}")
        print(f"   Location: {job['location']}")
        print(f"   Source: {job['source']}")


if __name__ == "__main__":
    test_company_scraper()
