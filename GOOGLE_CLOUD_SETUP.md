# 🔧 Google Cloud Setup Guide for Job Scraper

This guide will help you set up Google Cloud services to enable your job scraper to automatically save jobs to Google Sheets.

## 📋 Prerequisites

- Google account (Gmail)
- Web browser
- 10-15 minutes of time

---

## 🚀 Step-by-Step Setup

### Step 1: Create Google Cloud Project

1. **Go to Google Cloud Console**
   - Visit: https://console.cloud.google.com/
   - Sign in with your Google account

2. **Create New Project**
   - Click the project dropdown at the top
   - Click "New Project"
   - Enter project name: `job-scraper-project` (or your preferred name)
   - Click "Create"
   - Wait for project creation (30-60 seconds)

### Step 2: Enable Required APIs

1. **Navigate to APIs & Services**
   - In the left sidebar, click "APIs & Services" → "Library"
   
2. **Enable Google Sheets API**
   - Search for "Google Sheets API"
   - Click on "Google Sheets API"
   - Click "Enable"
   - Wait for activation

3. **Enable Google Drive API**
   - Search for "Google Drive API"
   - Click on "Google Drive API" 
   - Click "Enable"
   - Wait for activation

### Step 3: Create Service Account

1. **Go to Credentials**
   - Click "APIs & Services" → "Credentials"

2. **Create Service Account**
   - Click "Create Credentials" → "Service Account"
   - Fill in details:
     - **Service account name**: `job-scraper-service`
     - **Service account ID**: (auto-generated)
     - **Description**: `Service account for job scraper automation`
   - Click "Create and Continue"

3. **Grant Permissions**
   - **Role**: Select "Editor" (gives read/write access)
   - Click "Continue"
   - Click "Done"

### Step 4: Generate Credentials JSON

1. **Access Service Account**
   - In Credentials page, find your service account
   - Click on the service account email

2. **Create Key**
   - Go to "Keys" tab
   - Click "Add Key" → "Create new key"
   - Select "JSON" format
   - Click "Create"

3. **Download & Save**
   - File will download automatically as `job-scraper-project-xxxxx.json`
   - **IMPORTANT**: Rename this file to `credentials.json`
   - Move it to your job-scraper project folder
   - **Keep this file secure and never share it!**

### Step 5: Create Google Sheet

1. **Create New Sheet**
   - Go to: https://sheets.google.com/
   - Click "Blank" to create new sheet
   - Name it: `Job Applications Tracker`

2. **Get Sheet ID**
   - Copy the URL of your sheet
   - Extract the ID from: `https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit`
   - Save this ID - you'll need it for configuration

3. **Share with Service Account**
   - Click "Share" button in your sheet
   - In the email field, enter the service account email from your `credentials.json`
   - Set permission to "Editor"
   - **Uncheck** "Notify people" 
   - Click "Share"

---

## ⚙️ Configuration

### Update config.json

Open your `config.json` file and update the `sheet_id`:

```json
{
  "keywords": ["SAP", "Customer Success", "Data Analyst", "Consultant"],
  "location": "Pune",
  "sheet_id": "YOUR_ACTUAL_SHEET_ID_HERE",
  "sheet_name": "Jobs",
  "max_jobs_per_site": 50
}
```

Replace `YOUR_ACTUAL_SHEET_ID_HERE` with the ID you copied from your Google Sheet URL.

---

## 🧪 Test Your Setup

### Test Google Sheets Connection

1. **Run Test Command**:
```bash
cd sheets
python google_sheets.py
```

2. **Expected Output**:
```
✅ Successfully authenticated with Google Sheets API
✅ Connected to existing sheet: Jobs
📊 Sheet stats: {'total_jobs': 0}
✅ Google Sheets connection test successful!
```

### Test Full Scraper

1. **Run Test Scraper**:
```bash
python jobs_runner.py --test
```

2. **Check Your Google Sheet**:
   - Should see headers automatically created
   - Should see a few test jobs added

---

## 🔒 Security Best Practices

### Protect Your Credentials

1. **Never Commit credentials.json**
   - File is already in `.gitignore`
   - Double-check it's not in your git repository

2. **For GitHub Actions**
   - Don't put credentials in your code
   - Use GitHub Secrets (we'll set this up next)

3. **Local Development**
   - Keep `credentials.json` in project root
   - Don't share or email this file

---

## 🚨 Troubleshooting

### Common Issues & Solutions

#### "Authentication failed"
- ✅ Check `credentials.json` is in project root
- ✅ Verify file is valid JSON (not corrupted)
- ✅ Ensure APIs are enabled in Google Cloud

#### "Permission denied"
- ✅ Share sheet with service account email
- ✅ Grant "Editor" permission (not just "Viewer")
- ✅ Check service account has correct roles

#### "Sheet not found"
- ✅ Verify sheet ID is correct
- ✅ Check sheet name matches config
- ✅ Ensure sheet is accessible

#### "Quota exceeded"
- ✅ Google Sheets API has daily limits
- ✅ Reduce `max_jobs_per_site` in config
- ✅ Add delays between requests

### Getting Help

If you encounter issues:

1. **Check Error Messages**: Look for specific error details
2. **Verify Each Step**: Go through setup steps again
3. **Test Components**: Test Google Sheets connection separately
4. **Check Permissions**: Ensure service account has access

---

## 📊 What's Next?

After successful setup:

1. ✅ **Test Local Scraping**: `python jobs_runner.py --test`
2. ✅ **Configure Keywords**: Update your job search criteria
3. ✅ **Set Up GitHub Actions**: For automated daily runs
4. ✅ **Monitor Results**: Check your Google Sheet regularly

---

## 🎯 Quick Checklist

- [ ] Google Cloud project created
- [ ] Google Sheets API enabled
- [ ] Google Drive API enabled  
- [ ] Service account created with Editor role
- [ ] `credentials.json` downloaded and renamed
- [ ] Google Sheet created and shared with service account
- [ ] Sheet ID added to `config.json`
- [ ] Connection test successful
- [ ] First scraper test completed

---

**🎉 Once all items are checked, your Google Cloud setup is complete!**

Your job scraper can now automatically save jobs to your Google Sheet. The next step is setting up GitHub Actions for daily automation.
