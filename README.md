# 🎯 Job Scraper - Automated Job Collection & Google Sheets Integration

An intelligent job scraper that automatically collects relevant job postings from multiple job sites and organizes them in Google Sheets for easy review and application tracking.

## 🌟 Features

- **Multi-Site Scraping**: 6+ job sources including TimesJobs, LinkedIn, Glassdoor, Company Career Pages
- **Advanced Browser Automation**: Playwright-powered scraping for JavaScript-heavy sites
- **Smart Filtering**: AI-powered keyword matching and relevance detection
- **Google Sheets Integration**: Automatic job storage with intelligent duplicate detection
- **Stealth Techniques**: Anti-detection measures for respectful scraping
- **Company Career Pages**: Direct scraping from Infosys, TCS, Wipro, Tech Mahindra, Capgemini
- **Automated Scheduling**: Daily runs via GitHub Actions
- **Configurable**: Easy customization for different job criteria and locations
- **Rate Limiting**: Respectful scraping with delays and retries

## 📊 Target Job Sources

| Site | Status | Features |
|------|--------|----------|
| **TimesJobs.com** | ✅ Active | Primary reliable scraper |
| **LinkedIn Jobs** | ✅ Limited | Stealth scraping (10 jobs/session) |
| **Glassdoor** | ✅ Limited | Company insights + salary data |
| **Company Career Pages** | ✅ Active | Infosys, TCS, Wipro, Tech Mahindra, Capgemini |
| **Naukri.com** | ⚠️ Limited | Anti-bot protection (Playwright ready) |
| **Indeed.com** | ⚠️ Limited | Rate limiting (needs rotation) |

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.11+
- Google Cloud account (free)
- GitHub account (for automation)

### 2. Setup Google Sheets API

1. **Create Google Cloud Project**:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one
   - Enable Google Sheets API and Google Drive API

2. **Create Service Account**:
   - Go to IAM & Admin → Service Accounts
   - Create new service account
   - Download JSON credentials file
   - Rename it to `credentials.json` and place in project root

3. **Create Google Sheet**:
   - Create a new Google Sheet
   - Share it with your service account email (from credentials.json)
   - Copy the sheet ID from URL: `https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit`

### 3. Configuration

1. **Update config.json**:
```json
{
  "keywords": ["SAP", "Customer Success", "Data Analyst", "Consultant"],
  "location": "Pune",
  "sheet_id": "YOUR_ACTUAL_SHEET_ID_HERE",
  "max_jobs_per_site": 50
}
```

2. **Install Dependencies**:
```bash
pip install -r requirements.txt
playwright install chromium
```

### 4. Test Run

```bash
# Test with limited jobs
python jobs_runner.py --test

# Run specific scraper
python jobs_runner.py --scrapers naukri

# Run all scrapers
python jobs_runner.py
```

## 🔧 Configuration Options

### config.json Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `keywords` | Job search keywords | `["SAP", "Data Analyst"]` |
| `location` | Target job location | `"Pune"` |
| `exclude_keywords` | Keywords to avoid | `["Intern", "Unpaid"]` |
| `sheet_id` | Google Sheet ID | `"1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"` |
| `max_jobs_per_site` | Jobs per scraper run | `50` |
| `delay_between_requests` | Delay between requests (seconds) | `2` |

### Google Sheets Structure

The scraper creates a sheet with these columns:

| Column | Description |
|--------|-------------|
| Job Title | Position title |
| Company | Company name |
| Location | Job location |
| Application Link | Direct apply URL |
| Source | Job board name |
| Posted Date | When job was posted |
| Scraped Date | When we found it |
| Salary | Salary information (if available) |
| Application Status | Your application status |

## 🤖 Automation Setup

### GitHub Actions (Recommended)

1. **Fork/Clone this repository**

2. **Add Repository Secrets**:
   - Go to Settings → Secrets and variables → Actions
   - Add secret: `GOOGLE_CREDENTIALS`
   - Paste entire contents of your `credentials.json` file

3. **Enable Actions**:
   - Go to Actions tab
   - Enable workflows
   - The scraper will run daily at 7 AM IST

### Manual Scheduling

For local automation, use cron (Linux/Mac) or Task Scheduler (Windows):

```bash
# Add to crontab for daily 7 AM runs
30 1 * * * cd /path/to/job-scraper && python jobs_runner.py
```

## 📈 Usage Examples

### Command Line Options

```bash
# Basic run
python jobs_runner.py

# Test mode (5 jobs per site)
python jobs_runner.py --test

# Specific scrapers only
python jobs_runner.py --scrapers timesjobs linkedin

# Run multiple sources
python jobs_runner.py --scrapers timesjobs companies glassdoor

# LinkedIn only (limited but high quality)
python jobs_runner.py --scrapers linkedin --test

# Custom config file
python jobs_runner.py --config my_config.json
```

### Programmatic Usage

```python
from jobs_runner import JobScraperRunner

# Initialize runner
runner = JobScraperRunner('config.json')

# Run all scrapers
results = runner.run()

# Run specific scrapers
results = runner.run(['naukri', 'indeed'])

print(f"Added {results['new_jobs']} new jobs!")
```

## 🛠️ Development

### Project Structure

```
job-scraper/
├── scrapers/           # Individual site scrapers
│   ├── naukri.py      # Naukri.com scraper
│   ├── indeed.py      # Indeed.com scraper
│   └── utils.py       # Common utilities
├── sheets/            # Google Sheets integration
│   └── google_sheets.py
├── .github/workflows/ # GitHub Actions
│   └── scraper.yml
├── jobs_runner.py     # Main orchestrator
├── config.json        # Configuration
└── requirements.txt   # Dependencies
```

### Adding New Scrapers

1. Create new scraper in `scrapers/` directory
2. Implement required methods: `scrape_jobs()`, `extract_job_details()`
3. Add to `JobScraperRunner.setup_scrapers()`
4. Update documentation

### Testing Individual Scrapers

```bash
# Test Naukri scraper
cd scrapers && python naukri.py

# Test Indeed scraper  
cd scrapers && python indeed.py

# Test Google Sheets
cd sheets && python google_sheets.py
```

## 🔍 Troubleshooting

### Common Issues

1. **Authentication Errors**:
   - Verify `credentials.json` is valid
   - Check if service account has sheet access
   - Ensure APIs are enabled in Google Cloud

2. **No Jobs Found**:
   - Check if keywords match job titles
   - Verify location spelling
   - Website structure may have changed

3. **Rate Limiting**:
   - Increase `delay_between_requests` in config
   - Reduce `max_jobs_per_site`
   - Check if IP is temporarily blocked

4. **GitHub Actions Failing**:
   - Verify `GOOGLE_CREDENTIALS` secret is set correctly
   - Check workflow logs for specific errors
   - Ensure repository has Actions enabled

### Debug Mode

Enable detailed logging:

```bash
export PYTHONPATH=.
python -c "
import logging
logging.basicConfig(level=logging.DEBUG)
from jobs_runner import JobScraperRunner
runner = JobScraperRunner()
runner.run()
"
```

## 📊 Monitoring & Analytics

### View Results

- **Google Sheets**: Direct access to organized job data
- **Summary Reports**: Generated after each run (`scraping_summary_*.txt`)
- **GitHub Actions**: Workflow logs and artifacts

### Key Metrics

- Jobs found per source
- Duplicate detection rate
- Application status tracking
- Daily/weekly job trends

## 🔒 Privacy & Ethics

### Responsible Scraping

- ✅ Respects robots.txt files
- ✅ Implements reasonable delays
- ✅ Uses public job postings only
- ✅ Includes proper user-agent identification
- ✅ Follows rate limiting best practices

### Data Handling

- Job data stored only in your Google Sheets
- No personal information collected
- Credentials stored securely in GitHub Secrets
- Local credentials file excluded from git

## 🚀 Future Enhancements

### Planned Features

- **LinkedIn Jobs Integration** (careful rate limiting)
- **Glassdoor Scraper** (company insights)
- **AI-Powered Job Matching** (resume compatibility)
- **Email Notifications** (daily job digest)
- **Advanced Filtering** (salary range, experience level)
- **Application Tracking** (status updates, follow-ups)

### Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -am 'Add feature'`
4. Push branch: `git push origin feature-name`
5. Submit pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/job-scraper/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/job-scraper/discussions)
- **Email**: your.email@example.com

---

**Happy Job Hunting! 🎯**

*Built with ❤️ for job seekers who want to automate the tedious parts of job searching while maintaining control over their applications.*
