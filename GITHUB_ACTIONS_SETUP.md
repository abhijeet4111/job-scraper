# 🤖 GitHub Actions Setup Guide - Automated Daily Job Scraping

This guide will help you set up GitHub Actions to run your job scraper automatically every day at 7 AM IST, updating your Google Sheet with fresh job opportunities.

## 📋 Prerequisites

✅ **Completed Requirements:**
- [x] Job scraper working locally
- [x] Google Cloud project set up
- [x] Google Sheets integration working
- [x] `credentials.json` file available

## 🚀 Step-by-Step Setup

### Step 1: Create GitHub Repository

1. **Go to GitHub.com**
   - Sign in to your GitHub account
   - Click "New repository" (green button)

2. **Repository Settings**
   - **Repository name**: `job-scraper` (or your preferred name)
   - **Description**: `Automated job scraper with Google Sheets integration`
   - **Visibility**: Private (recommended for personal use)
   - **Initialize**: Don't check any boxes (we'll push existing code)
   - Click **"Create repository"**

### Step 2: Push Your Code to GitHub

1. **Initialize Git in Your Project** (if not already done):
```bash
cd "C:\Users\miniOrange\Desktop\miniorange projects\job-scrapper"
git init
git add .
git commit -m "Initial commit: Multi-source job scraper"
```

2. **Connect to GitHub Repository**:
```bash
git remote add origin https://github.com/YOUR_USERNAME/job-scraper.git
git branch -M main
git push -u origin main
```

*Replace `YOUR_USERNAME` with your actual GitHub username*

### Step 3: Set Up GitHub Secrets

This is the **most important step** - it securely stores your Google credentials.

1. **Go to Your Repository on GitHub**
   - Navigate to your repository: `https://github.com/YOUR_USERNAME/job-scraper`

2. **Access Repository Settings**
   - Click **"Settings"** tab (top right of repository)
   - In left sidebar, click **"Secrets and variables"** → **"Actions"**

3. **Add Google Credentials Secret**
   - Click **"New repository secret"**
   - **Name**: `GOOGLE_CREDENTIALS`
   - **Secret**: 
     - Open your local `credentials.json` file
     - Copy **ALL** the content (the entire JSON)
     - Paste it into the Secret value field
   - Click **"Add secret"**

**⚠️ Important**: Make sure you copy the ENTIRE contents of `credentials.json`, including all the curly braces and quotes.

### Step 4: Configure the Workflow

The workflow is already set up in `.github/workflows/scraper.yml`. Here's what it does:

**🕐 Schedule**: Runs daily at 7:00 AM IST (1:30 AM UTC)
**🔧 Scrapers**: Uses TimesJobs + Company Careers (most reliable)
**📊 Output**: Updates your Google Sheet automatically
**📄 Reports**: Saves summary reports as artifacts

**Current Configuration:**
```yaml
- cron: "30 1 * * *"  # 7:00 AM IST daily
python jobs_runner.py --scrapers timesjobs companies
```

### Step 5: Test the Automation

1. **Manual Test Run**
   - Go to your repository on GitHub
   - Click **"Actions"** tab
   - Click **"Daily Job Scraper"** workflow
   - Click **"Run workflow"** button (right side)
   - Click **"Run workflow"** in the dropdown
   - Wait for the workflow to complete (3-5 minutes)

2. **Check Results**
   - The workflow should show green checkmarks ✅
   - Check your Google Sheet for new jobs
   - Download the summary report from "Artifacts" section

### Step 6: Monitor Daily Runs

**🔍 How to Check if It's Working:**

1. **GitHub Actions Page**
   - Go to repository → Actions tab
   - See daily run history and status

2. **Your Google Sheet**
   - Check for new jobs added daily
   - Look for "TimesJobs" and company career jobs

3. **Email Notifications** (Optional)
   - GitHub can email you if workflows fail
   - Go to Settings → Notifications to configure

## ⚙️ Customization Options

### Change Schedule

Edit `.github/workflows/scraper.yml`:

```yaml
# Every 12 hours
- cron: "0 */12 * * *"

# Weekdays only at 8 AM IST
- cron: "30 2 * * 1-5"

# Twice daily (8 AM and 6 PM IST)
- cron: "30 2,14 * * *"
```

### Change Scrapers

Edit the run command in the workflow:

```yaml
# Maximum coverage (may be slower)
python jobs_runner.py --scrapers timesjobs companies linkedin glassdoor

# Fast and reliable only
python jobs_runner.py --scrapers timesjobs

# Premium sources only
python jobs_runner.py --scrapers linkedin glassdoor --test
```

### Adjust Job Limits

Edit `config.json` in your repository:

```json
{
  "max_jobs_per_site": 25,  // Reduce for faster runs
  "delay_between_requests": 3  // Increase for more respectful scraping
}
```

## 🛠️ Troubleshooting

### Common Issues

**❌ "credentials.json not found"**
- Check that `GOOGLE_CREDENTIALS` secret is set correctly
- Verify the secret contains the full JSON content

**❌ "Permission denied" for Google Sheets**
- Ensure your service account has "Editor" access to the sheet
- Check that the sheet ID in config.json is correct

**❌ "No jobs found"**
- Websites may have changed structure
- Check individual scraper logs in Actions output

**❌ Workflow doesn't run**
- Ensure repository is not archived
- Check that the workflow file is in `.github/workflows/`
- Verify cron syntax is correct

### Getting Help

1. **Check Workflow Logs**
   - Go to Actions → Failed workflow → Click on job → Expand steps

2. **Test Locally First**
   - Always test changes locally before pushing to GitHub

3. **Monitor Rate Limits**
   - GitHub Actions has usage limits (2000 minutes/month for free accounts)
   - Each run takes about 3-5 minutes

## 📊 What Happens Daily

**Every Day at 7 AM IST:**

1. ✅ **GitHub Actions starts** the workflow
2. ✅ **Environment setup** (Python, dependencies, Playwright)
3. ✅ **Credentials loaded** securely from secrets
4. ✅ **Job scrapers run** (TimesJobs + Company Careers)
5. ✅ **Jobs filtered** by your keywords and location
6. ✅ **Duplicates removed** automatically
7. ✅ **Google Sheet updated** with new jobs
8. ✅ **Summary report generated** and saved
9. ✅ **Cleanup completed** (credentials removed)

**Expected Results:**
- 10-30 new relevant jobs added to your sheet daily
- Automatic duplicate prevention
- Professional summary reports
- Zero manual intervention required

## 🎯 Success Metrics

**After 1 Week:**
- 50-150 new job opportunities in your sheet
- Organized by source, date, and relevance
- Ready for your review and applications

**After 1 Month:**
- 200-500+ job opportunities collected
- Comprehensive view of Pune job market
- Significant time saved on job searching

## 🔒 Security & Privacy

✅ **Secure**: Credentials stored as encrypted GitHub secrets
✅ **Private**: Your data stays in your Google Sheet
✅ **Controlled**: Only you have access to the repository
✅ **Clean**: Credentials automatically cleaned after each run

---

## 🎉 You're All Set!

Once configured, your job scraper will:
- 🤖 **Run automatically** every day
- 📊 **Update your Google Sheet** with fresh jobs
- 🔍 **Find relevant opportunities** while you sleep
- 📈 **Save hours** of manual job searching
- 💼 **Keep you ahead** of the competition

**Your automated job search system is now live!** 🚀

---

*Last Updated: September 20, 2025*
*Status: Ready for Production* ✅
