"""
LinkedIn Jobs scraper with advanced stealth techniques
WARNING: Use responsibly and respect LinkedIn's terms of service
"""
from playwright.sync_api import sync_playwright
from typing import List, Dict, Optional
import time
import random
from urllib.parse import urljoin, quote_plus
import json
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


class LinkedInJobsScraper:
    def __init__(self, config: Dict):
        self.config = config
        self.base_url = "https://www.linkedin.com"
        self.max_jobs_per_session = 10  # Conservative limit to avoid detection
        
    def build_search_url(self, keywords: List[str], location: str, page: int = 0) -> str:
        """Build LinkedIn Jobs search URL"""
        # LinkedIn uses different URL structure
        keyword_string = " ".join(keywords[:3])  # Limit keywords
        
        # Use LinkedIn's job search endpoint
        search_url = f"{self.base_url}/jobs/search"
        
        # Build parameters
        params = {
            'keywords': keyword_string,
            'location': location,
            'f_TPR': 'r86400',  # Past 24 hours
            'f_JT': 'F',  # Full-time
            'start': page * 25  # LinkedIn shows 25 jobs per page
        }
        
        # Build URL with parameters
        param_string = "&".join([f"{k}={quote_plus(str(v))}" for k, v in params.items()])
        return f"{search_url}?{param_string}"
    
    def setup_stealth_browser(self, playwright):
        """Set up browser with advanced stealth techniques"""
        # Launch browser with stealth settings
        browser = playwright.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--disable-blink-features=AutomationControlled',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor',
                '--disable-background-timer-throttling',
                '--disable-backgrounding-occluded-windows',
                '--disable-renderer-backgrounding',
                '--disable-field-trial-config',
                '--disable-back-forward-cache',
                '--disable-ipc-flooding-protection',
                '--no-first-run',
                '--no-default-browser-check',
                '--no-pings',
                '--password-store=basic',
                '--use-mock-keychain'
            ]
        )
        
        # Create context with realistic settings
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080},
            locale='en-US',
            timezone_id='America/New_York',
            extra_http_headers={
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Cache-Control': 'max-age=0'
            }
        )
        
        return browser, context
    
    def add_stealth_scripts(self, page):
        """Add JavaScript to make browser less detectable"""
        stealth_js = """
        // Remove webdriver property
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined,
        });
        
        // Mock plugins
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3, 4, 5],
        });
        
        // Mock languages
        Object.defineProperty(navigator, 'languages', {
            get: () => ['en-US', 'en'],
        });
        
        // Mock permissions
        const originalQuery = window.navigator.permissions.query;
        window.navigator.permissions.query = (parameters) => (
            parameters.name === 'notifications' ?
                Promise.resolve({ state: Notification.permission }) :
                originalQuery(parameters)
        );
        
        // Mock chrome object
        window.chrome = {
            runtime: {},
        };
        """
        
        page.add_init_script(stealth_js)
    
    def extract_job_details(self, job_element, page) -> Optional[Dict]:
        """Extract job details from LinkedIn job listing"""
        try:
            job_data = {}
            
            # Job Title and Link
            title_selectors = [
                'h3.base-search-card__title a',
                '.job-search-card__title a',
                'a[data-control-name="job_search_job_result_title"]',
                '.base-card__full-link',
                'h4 a'
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
                'h4.base-search-card__subtitle a',
                '.job-search-card__subtitle-link',
                'a[data-control-name="job_search_job_result_company_name"]',
                '.base-search-card__subtitle',
                'h4 span'
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
                '.job-search-card__location',
                '.base-search-card__metadata span',
                'span[data-test="job-search-card-location"]'
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
            
            # Job Description (limited on search page)
            desc_selectors = [
                '.job-search-card__snippet',
                '.base-search-card__snippet'
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
                'time',
                '.job-search-card__listdate',
                '.base-search-card__metadata time'
            ]
            
            for selector in date_selectors:
                try:
                    date_element = job_element.query_selector(selector)
                    if date_element:
                        date_text = date_element.get_attribute('datetime') or date_element.inner_text()
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
            job_data['source'] = 'LinkedIn'
            
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
            print(f"❌ Error extracting LinkedIn job details: {e}")
            return None
    
    def scrape_jobs(self, max_jobs: int = 10) -> List[Dict]:
        """Scrape jobs from LinkedIn with careful rate limiting"""
        # Limit max jobs to avoid detection
        max_jobs = min(max_jobs, self.max_jobs_per_session)
        
        print(f"🔍 Starting LinkedIn scraping for {max_jobs} jobs...")
        print("⚠️  Using conservative limits to respect LinkedIn's terms")
        
        jobs = []
        
        with sync_playwright() as p:
            browser, context = self.setup_stealth_browser(p)
            page = context.new_page()
            
            # Add stealth scripts
            self.add_stealth_scripts(page)
            
            try:
                # Start with LinkedIn homepage to establish session
                print("🌐 Establishing LinkedIn session...")
                page.goto(self.base_url, wait_until='networkidle', timeout=30000)
                
                # Random delay to mimic human behavior
                time.sleep(random.uniform(2, 4))
                
                # Navigate to jobs search
                search_url = self.build_search_url(
                    self.config['keywords'], 
                    self.config['location']
                )
                
                print(f"🔍 Searching LinkedIn jobs...")
                print(f"🌐 URL: {search_url}")
                
                page.goto(search_url, wait_until='networkidle', timeout=30000)
                
                # Wait for content to load
                time.sleep(random.uniform(3, 5))
                
                # Check if we're blocked or need to login
                page_content = page.content().lower()
                if 'sign in' in page_content and 'linkedin' in page_content:
                    print("⚠️  LinkedIn requires sign-in - using public job listings only")
                    
                    # Try public jobs endpoint
                    public_url = f"{self.base_url}/jobs/search?keywords={quote_plus(' '.join(self.config['keywords'][:2]))}&location={quote_plus(self.config['location'])}"
                    page.goto(public_url, wait_until='networkidle', timeout=30000)
                    time.sleep(random.uniform(2, 4))
                
                # Find job listings
                job_selectors = [
                    '.base-card.relative.w-full.hover\\:no-underline.focus\\:no-underline.base-card--link.base-search-card.base-search-card--link.job-search-card',
                    '.base-search-card',
                    '.job-search-card',
                    '.jobs-search__results-list li',
                    '[data-entity-urn*="job"]'
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
                    print("❌ No job elements found - LinkedIn may be blocking access")
                    print("💡 Try running with a VPN or different IP address")
                    return jobs
                
                # Extract job details with careful pacing
                processed = 0
                for i, job_element in enumerate(job_elements):
                    if processed >= max_jobs:
                        break
                    
                    # Add random delays between extractions
                    if i > 0:
                        time.sleep(random.uniform(1, 2))
                    
                    job_data = self.extract_job_details(job_element, page)
                    if job_data:
                        jobs.append(job_data)
                        processed += 1
                        print(f"✅ Extracted: {job_data['title']} at {job_data['company']}")
                
                print(f"📊 LinkedIn scraping completed: Found {len(jobs)} relevant jobs")
                
            except Exception as e:
                print(f"❌ LinkedIn scraping error: {e}")
                print("💡 LinkedIn has strong anti-bot protection - consider using their API")
                
            finally:
                # Clean up
                browser.close()
        
        return jobs


def test_linkedin_scraper():
    """Test LinkedIn scraper with minimal requests"""
    import json
    
    # Load config
    with open('../config.json', 'r') as f:
        config = json.load(f)
    
    # Override max jobs for testing
    config['max_jobs_per_site'] = 3
    
    scraper = LinkedInJobsScraper(config)
    jobs = scraper.scrape_jobs(max_jobs=3)
    
    print(f"\n📊 LinkedIn Test Results:")
    print(f"Total jobs found: {len(jobs)}")
    
    for i, job in enumerate(jobs, 1):
        print(f"\n{i}. {job['title']}")
        print(f"   Company: {job['company']}")
        print(f"   Location: {job['location']}")
        print(f"   Link: {job['link']}")


if __name__ == "__main__":
    test_linkedin_scraper()
