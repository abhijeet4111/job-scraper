# 🎯 Job Scraper Project - Development Tracker

## 📋 Project Overview

**Goal**: Build an automated job scraper that collects job postings from multiple job sites and saves them to Google Sheets for easy review and application tracking.

**Target User**: Job seekers looking for positions in Pune, specifically in SAP, Customer Success, Data Analyst, and Consultant roles.

---

## 🎯 Key Objectives

- [x] ✅ **Project Planning & Documentation**
- [ ] 🔄 **MVP Development** (Week 1)
- [ ] ⏳ **Feature Expansion** (Week 2-3)
- [ ] 🚀 **Automation & Deployment** (Week 3-4)
- [ ] 🤖 **AI Enhancement** (Future)

---

## 🏗️ Architecture Overview

```
job-scraper/
├── scrapers/           # Individual site scrapers
├── sheets/            # Google Sheets integration
├── .github/workflows/ # GitHub Actions automation
├── jobs_runner.py     # Main orchestrator
├── config.json        # Configuration settings
└── requirements.txt   # Dependencies
```

---

## 📊 Target Job Sources

| Site | Priority | Status | Notes |
|------|----------|--------|-------|
| **Naukri.com** | High | 🔄 Planned | Primary Indian job board |
| **Indeed** | High | 🔄 Planned | Global reach, good API |
| **LinkedIn Jobs** | Medium | 🔄 Planned | Limited scraping, use carefully |
| **Glassdoor** | Medium | 🔄 Planned | Good for company insights |
| **Company Career Pages** | Low | 🔄 Future | SAP, TCS, Infosys, etc. |

---

## 🛠️ Tech Stack

### Backend & Scraping
- **Python 3.11+** - Main language
- **BeautifulSoup4** - HTML parsing for static sites
- **Requests** - HTTP client
- **Playwright** - Browser automation for dynamic sites

### Data Storage
- **Google Sheets API** - Free, collaborative storage
- **gspread** - Python Google Sheets client
- **oauth2client** - Authentication

### Automation
- **GitHub Actions** - Free CI/CD for daily runs
- **Cron scheduling** - Daily job collection

---

## 📋 Development Phases

### Phase 1: MVP (Week 1) 🎯
**Goal**: Basic scraper working with Google Sheets

- [ ] **Project Setup**
  - [ ] Initialize repository structure
  - [ ] Create requirements.txt
  - [ ] Set up config.json
  
- [ ] **Google Sheets Integration**
  - [ ] Set up Google Cloud project
  - [ ] Create service account & credentials
  - [ ] Implement sheets/google_sheets.py
  - [ ] Test sheet writing functionality

- [ ] **Basic Scraper**
  - [ ] Implement Naukri scraper
  - [ ] Test job extraction
  - [ ] Integrate with Google Sheets

- [ ] **Main Runner**
  - [ ] Create jobs_runner.py
  - [ ] Test end-to-end flow

**Success Criteria**: Can scrape Naukri jobs and save to Google Sheets

### Phase 2: Expansion (Week 2) 🚀
**Goal**: Multiple job sources + better filtering

- [ ] **Additional Scrapers**
  - [ ] Indeed scraper
  - [ ] LinkedIn Jobs scraper (careful limits)
  - [ ] Glassdoor scraper

- [ ] **Enhanced Filtering**
  - [ ] Keyword matching
  - [ ] Location filtering (Pune focus)
  - [ ] Date filtering (recent jobs only)

- [ ] **Deduplication**
  - [ ] URL-based duplicate detection
  - [ ] Title + Company similarity check
  - [ ] Maintain job history

**Success Criteria**: Scraping 3+ job sites with smart filtering

### Phase 3: Automation (Week 3) ⚙️
**Goal**: Fully automated daily runs

- [ ] **GitHub Actions Setup**
  - [ ] Create workflow file
  - [ ] Configure secrets management
  - [ ] Test automated runs

- [ ] **Error Handling**
  - [ ] Robust scraper error handling
  - [ ] Notification on failures
  - [ ] Retry mechanisms

- [ ] **Monitoring**
  - [ ] Job count tracking
  - [ ] Success/failure logging
  - [ ] Daily summary reports

**Success Criteria**: Scraper runs daily without manual intervention

### Phase 4: AI Enhancement (Future) 🤖
**Goal**: Smart job matching and insights

- [ ] **AI-Powered Features**
  - [ ] Resume-job matching scores
  - [ ] Skill gap analysis
  - [ ] Auto-generated cover letters
  - [ ] Salary prediction

---

## 🔧 Configuration Settings

### Target Criteria
```json
{
  "keywords": ["SAP", "Customer Success", "Data Analyst", "Consultant"],
  "location": "Pune",
  "experience_levels": ["Entry Level", "Mid Level", "Senior Level"],
  "max_jobs_per_site": 50,
  "exclude_keywords": ["Intern", "Unpaid"]
}
```

### Google Sheets Structure
| Column | Description | Example |
|--------|-------------|---------|
| Title | Job Title | "SAP Consultant" |
| Company | Company Name | "Infosys" |
| Location | Job Location | "Pune, Maharashtra" |
| Link | Application URL | "https://..." |
| Source | Job Board | "Naukri" |
| Posted Date | When job was posted | "2025-09-20" |
| Scraped Date | When we found it | "2025-09-20" |
| Status | Application status | "Not Applied" |

---

## 🚨 Risk Management

### Technical Risks
| Risk | Impact | Mitigation |
|------|--------|------------|
| **Rate Limiting** | High | Implement delays, rotate user agents |
| **Site Structure Changes** | Medium | Modular scrapers, easy updates |
| **API Limits** | Medium | Use multiple sources, cache results |
| **Google Sheets Limits** | Low | Monitor usage, implement pagination |

### Legal/Ethical Considerations
- ✅ Respect robots.txt files
- ✅ Implement reasonable delays between requests
- ✅ Don't overload job sites with requests
- ✅ Use public job postings only
- ✅ Add user-agent identification

---

## 📈 Success Metrics

### Quantitative Goals
- **Jobs per Day**: 20-50 new relevant jobs
- **Accuracy**: 90%+ relevant job matches
- **Uptime**: 95%+ successful daily runs
- **Duplicates**: <5% duplicate jobs

### Qualitative Goals
- Easy to review jobs in Google Sheets
- Minimal manual intervention required
- Clear application tracking workflow
- Expandable to new job sources

---

## 🔄 Daily Workflow (Post-Implementation)

1. **7:00 AM IST** - GitHub Actions triggers scraper
2. **7:05 AM** - Scrapers collect jobs from all sources
3. **7:10 AM** - Deduplication and filtering applied
4. **7:15 AM** - New jobs added to Google Sheets
5. **Morning** - Review new jobs, mark interesting ones
6. **Throughout day** - Apply to selected jobs
7. **Evening** - Update application status in sheet

---

## 📝 Development Log

### 2025-09-20
- [x] Created project tracker document
- [x] Defined project scope and architecture
- [x] Planned development phases
- [x] Set up complete project structure
- [x] Implemented core scrapers (Naukri, Indeed)
- [x] Created Google Sheets integration
- [x] Built main runner with CLI interface
- [x] Set up GitHub Actions workflow
- [x] Added comprehensive documentation
- [x] **MVP COMPLETED** ✅

**Status**: Phase 1 MVP completed successfully! Ready for testing and deployment.

### Next Steps
- [ ] Set up Google Cloud project and credentials
- [ ] Test scrapers with real job searches
- [ ] Deploy to GitHub Actions for automation
- [ ] Add LinkedIn and Glassdoor scrapers (Phase 2)

---

## 🔗 Useful Resources

### Documentation
- [Google Sheets API Docs](https://developers.google.com/sheets/api)
- [BeautifulSoup Documentation](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [Playwright Python Docs](https://playwright.dev/python/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)

### Job Site Analysis
- **Naukri.com**: Static HTML, easy to scrape
- **Indeed**: Some dynamic content, rate limited
- **LinkedIn**: Heavy rate limiting, use sparingly
- **Glassdoor**: Dynamic content, requires browser automation

---

## 🎯 Next Steps

1. **Immediate** (Today):
   - Set up project folder structure
   - Create requirements.txt
   - Initialize Git repository

2. **This Week**:
   - Set up Google Cloud project
   - Implement basic Naukri scraper
   - Test Google Sheets integration

3. **Next Week**:
   - Add more job sources
   - Implement deduplication
   - Set up GitHub Actions

---

## 📞 Contact & Support

- **Developer**: Your Name
- **Project Start**: September 20, 2025
- **Expected Completion**: October 15, 2025
- **Repository**: [GitHub Link - TBD]

---

*Last Updated: September 20, 2025*
*Status: 🚀 Project Initiated*
