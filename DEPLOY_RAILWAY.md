# Deploy to Railway (RECOMMENDED)

Railway is modern, easy to use, and has a generous free tier.

## Prerequisites
- A GitHub account
- A Railway account (sign up at https://railway.app with GitHub)

## Step 1: Upload to GitHub

1. Go to https://github.com and create a new repository
   - Name it something like `lego-pdf-downloader`
   - Make it **Public** or **Private** (your choice)
   - Don't initialize with README

2. Upload these files to the repository:
   ```
   lego_pdf_ui.py
   requirements.txt
   Procfile
   runtime.txt
   templates/
     └── index.html
   static/
     └── images/
         ├── pirates.jpg
         ├── space.jpg
         └── forestmen.png
   ```

3. **Important**: Create a `.gitignore` file with:
   ```
   downloads/
   __pycache__/
   *.pyc
   _tmp_*.png
   ```

## Step 2: Deploy on Railway

1. Go to https://railway.app and sign in with GitHub

2. Click **"New Project"**

3. Select **"Deploy from GitHub repo"**

4. Choose your `lego-pdf-downloader` repository

5. Railway will automatically:
   - Detect it's a Python app
   - Install dependencies from `requirements.txt`
   - Start the app using the `Procfile`

6. After deployment (takes ~2 minutes):
   - Click on your project
   - Go to **"Settings"** tab
   - Click **"Generate Domain"** to get a public URL
   - Your app will be live at something like: `https://lego-pdf-downloader.up.railway.app`

## Step 3: Fix the Downloads Folder Issue

**IMPORTANT**: Railway's filesystem is temporary. Downloaded PDFs won't persist between restarts.

You have two options:

### Option A: User downloads PDFs immediately (simpler)
- Files are saved temporarily
- Users must download within the session
- No changes needed to code

### Option B: Add persistent storage (advanced)
- Use Railway's volume storage
- PDFs persist forever
- Requires modifying the code to use `/app/data` volume

**For now, Option A works fine** - users just need to click "Open PDF" and save it to their computer right away.

## Railway Free Tier Limits
- 500 hours/month (plenty for personal use)
- $5 free credit each month
- Sleeps after 30 minutes of inactivity (wakes up instantly when visited)

## Troubleshooting

**App won't start?**
- Check the deployment logs in Railway dashboard
- Make sure all files are uploaded correctly
- Verify `Procfile` has no extra spaces

**Can't access the site?**
- Make sure you generated a domain in Settings
- Railway apps take ~30 seconds to wake up from sleep

**Downloads not working?**
- This is expected with Railway's temporary filesystem
- Users should download PDFs immediately after creation

---

## Your live URL will look like:
`https://your-app-name.up.railway.app`

Share this with anyone - they can access it from anywhere! 🎉
