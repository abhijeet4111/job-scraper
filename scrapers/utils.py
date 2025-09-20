"""
Utility functions for job scrapers
"""
import time
import random
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import requests
from bs4 import BeautifulSoup


def get_random_user_agent(user_agents: List[str]) -> str:
    """Get a random user agent from the list"""
    return random.choice(user_agents)


def clean_text(text: str) -> str:
    """Clean and normalize text content"""
    if not text:
        return ""
    
    # Remove extra whitespace and newlines
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Remove special characters that might cause issues
    text = re.sub(r'[^\w\s\-.,()&]', '', text)
    
    return text


def extract_salary(text: str) -> Optional[str]:
    """Extract salary information from job description"""
    if not text:
        return None
    
    # Common salary patterns
    salary_patterns = [
        r'₹\s*[\d,]+\s*-\s*₹\s*[\d,]+',
        r'Rs\.?\s*[\d,]+\s*-\s*Rs\.?\s*[\d,]+',
        r'[\d,]+\s*-\s*[\d,]+\s*LPA',
        r'[\d,]+\s*LPA',
        r'\$\s*[\d,]+\s*-\s*\$\s*[\d,]+',
    ]
    
    for pattern in salary_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group().strip()
    
    return None


def is_relevant_job(job_title: str, job_description: str, keywords: List[str], 
                   exclude_keywords: List[str]) -> bool:
    """Check if job is relevant based on keywords"""
    title_lower = job_title.lower()
    desc_lower = job_description.lower() if job_description else ""
    
    # Check exclude keywords first
    for exclude_word in exclude_keywords:
        if exclude_word.lower() in title_lower or exclude_word.lower() in desc_lower:
            return False
    
    # Check if any keyword matches
    for keyword in keywords:
        if keyword.lower() in title_lower or keyword.lower() in desc_lower:
            return True
    
    return False


def parse_date(date_str: str) -> Optional[str]:
    """Parse various date formats to standard YYYY-MM-DD format"""
    if not date_str:
        return None
    
    date_str = date_str.strip().lower()
    today = datetime.now()
    
    # Handle relative dates
    if 'today' in date_str or 'just now' in date_str:
        return today.strftime('%Y-%m-%d')
    elif 'yesterday' in date_str:
        return (today - timedelta(days=1)).strftime('%Y-%m-%d')
    elif 'days ago' in date_str:
        days_match = re.search(r'(\d+)\s*days?\s*ago', date_str)
        if days_match:
            days = int(days_match.group(1))
            return (today - timedelta(days=days)).strftime('%Y-%m-%d')
    elif 'week ago' in date_str or 'weeks ago' in date_str:
        weeks_match = re.search(r'(\d+)\s*weeks?\s*ago', date_str)
        if weeks_match:
            weeks = int(weeks_match.group(1))
            return (today - timedelta(weeks=weeks)).strftime('%Y-%m-%d')
        else:
            return (today - timedelta(weeks=1)).strftime('%Y-%m-%d')
    
    # Try to parse standard date formats
    date_formats = [
        '%Y-%m-%d',
        '%d-%m-%Y',
        '%d/%m/%Y',
        '%m/%d/%Y',
        '%d %b %Y',
        '%d %B %Y',
        '%b %d, %Y',
        '%B %d, %Y'
    ]
    
    for fmt in date_formats:
        try:
            parsed_date = datetime.strptime(date_str, fmt)
            return parsed_date.strftime('%Y-%m-%d')
        except ValueError:
            continue
    
    return None


def safe_request(url: str, headers: Dict[str, str], delay: float = 2, 
                max_retries: int = 3) -> Optional[requests.Response]:
    """Make a safe HTTP request with retries and delays"""
    for attempt in range(max_retries):
        try:
            time.sleep(delay + random.uniform(0, 1))  # Add random delay
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            print(f"Request failed (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt == max_retries - 1:
                return None
            time.sleep(delay * (attempt + 1))  # Exponential backoff
    
    return None


def extract_company_from_url(url: str) -> Optional[str]:
    """Extract company name from job URL if possible"""
    if not url:
        return None
    
    # Common patterns for company names in URLs
    patterns = [
        r'/company/([^/]+)',
        r'/companies/([^/]+)',
        r'company=([^&]+)',
        r'/jobs/([^/]+)/company'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url, re.IGNORECASE)
        if match:
            company = match.group(1).replace('-', ' ').replace('_', ' ')
            return company.title()
    
    return None


def deduplicate_jobs(jobs: List[Dict], existing_urls: set) -> List[Dict]:
    """Remove duplicate jobs based on URL and title+company similarity"""
    unique_jobs = []
    seen_urls = set(existing_urls)
    seen_combinations = set()
    
    for job in jobs:
        job_url = job.get('link', '')
        job_title = job.get('title', '').lower().strip()
        job_company = job.get('company', '').lower().strip()
        
        # Skip if URL already exists
        if job_url and job_url in seen_urls:
            continue
        
        # Create a combination key for title+company similarity
        combination_key = f"{job_title}|{job_company}"
        
        # Skip if very similar job already exists
        if combination_key in seen_combinations:
            continue
        
        # Add to unique jobs
        unique_jobs.append(job)
        if job_url:
            seen_urls.add(job_url)
        seen_combinations.add(combination_key)
    
    return unique_jobs


def validate_job_data(job: Dict) -> bool:
    """Validate that job data has required fields"""
    required_fields = ['title', 'company', 'location', 'link', 'source']
    
    for field in required_fields:
        if not job.get(field) or job.get(field).strip() == '':
            return False
    
    return True


def format_job_for_sheet(job: Dict) -> List[str]:
    """Format job data for Google Sheets row"""
    return [
        job.get('title', ''),
        job.get('company', ''),
        job.get('location', ''),
        job.get('link', ''),
        job.get('source', ''),
        job.get('posted_date', ''),
        datetime.now().strftime('%Y-%m-%d'),  # scraped_date
        job.get('salary', ''),
        'Not Applied'  # status
    ]
