# Deploy to PythonAnywhere (ALTERNATIVE)

PythonAnywhere is specifically designed for Python web apps and has a forever-free tier.

## Step 1: Create Account

1. Go to https://www.pythonanywhere.com
2. Click **"Start running Python online in less than a minute!"**
3. Create a **free Beginner account** (no credit card needed)

## Step 2: Upload Files

1. After logging in, go to the **"Files"** tab

2. Create a new folder: `lego_downloader`

3. Upload these files to that folder:
   - `lego_pdf_ui.py`
   - `requirements.txt`
   - Create a `templates` folder and upload `index.html` inside it
   - Create a `static/images` folder and upload the background images

## Step 3: Install Dependencies

1. Go to the **"Consoles"** tab
2. Click **"Bash"** to open a console
3. Run these commands:
   ```bash
   cd lego_downloader
   pip3.10 install --user -r requirements.txt
   ```
   (This takes ~2 minutes)

## Step 4: Configure Web App

1. Go to the **"Web"** tab
2. Click **"Add a new web app"**
3. Choose **"Manual configuration"** (NOT Flask)
4. Select **Python 3.10**

5. In the **"Code"** section:
   - **Source code:** `/home/yourusername/lego_downloader`
   - **Working directory:** `/home/yourusername/lego_downloader`

6. Edit the **WSGI configuration file** (click the link):
   - Delete everything in the file
   - Paste this:
   ```python
   import sys
   import os
   
   # Add your project directory to the sys.path
   project_home = '/home/yourusername/lego_downloader'
   if project_home not in sys.path:
       sys.path = [project_home] + sys.path
   
   # Import the Flask app
   from lego_pdf_ui import app as application
   ```
   - **Replace `yourusername`** with your actual PythonAnywhere username
   - Click **Save**

7. Scroll back up and click the big green **"Reload"** button

## Step 5: Access Your App

Your app is now live at:
```
https://yourusername.pythonanywhere.com
```

Share this URL with anyone!

## PythonAnywhere Free Tier Limits
- Always on (doesn't sleep)
- One web app
- Limited CPU/bandwidth (fine for personal use)
- Must log in every 3 months to keep it active

## Important Notes

**Downloads Folder:**
- PythonAnywhere has persistent storage
- PDFs will be saved and available until manually deleted
- Consider adding a cleanup script for old files

**Static Files:**
- If background images don't show up:
  1. Go to Web tab
  2. In "Static files" section, add:
     - URL: `/static`
     - Directory: `/home/yourusername/lego_downloader/static`
  3. Click Reload

## Troubleshooting

**500 Internal Server Error?**
- Check the error log (link in the Web tab)
- Make sure WSGI file has correct username
- Verify all dependencies installed

**Images not loading?**
- Configure static files mapping (see above)
- Make sure images are in `static/images/` folder

**App is slow?**
- Free tier has CPU limits
- Normal for free hosting
- Upgrade to paid tier for better performance

---

Your live URL: `https://yourusername.pythonanywhere.com` 🎉
