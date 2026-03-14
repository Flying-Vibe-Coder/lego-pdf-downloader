# 🧱 LEGO Instructions PDF Downloader

A web-based tool to download LEGO building instructions as PDF files. Simply enter a set number and get the instructions!

![LEGO Downloader](https://img.shields.io/badge/LEGO-Instructions-red?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge)
![Flask](https://img.shields.io/badge/Flask-3.0-green?style=for-the-badge)

## ✨ Features

- 🔍 Searches multiple sources:
  - Official Lego.com (when available)
  - Internet Archive
  - BrickInstructions.com
- 📥 Downloads PDFs directly to your Downloads folder
- 🎨 Beautiful retro-themed interface with random backgrounds
- 📊 Real-time download progress tracking
- 🖥️ Works on desktop and mobile

## 🚀 Quick Start (Run Locally)

1. **Install Python 3.10+** (if not already installed)

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the app:**
   ```bash
   python lego_pdf_ui.py
   ```

4. **Open in browser:**
   ```
   http://localhost:5000
   ```

## 🌐 Deploy Online (Share with Others)

Choose one:

### Option A: Railway (Recommended)
- Modern platform
- Generous free tier (500 hours/month)
- Auto-sleeps when inactive
- See: **[DEPLOY_RAILWAY.md](DEPLOY_RAILWAY.md)**

### Option B: PythonAnywhere
- Forever free tier
- Always-on (doesn't sleep)
- Python-specific hosting
- See: **[DEPLOY_PYTHONANYWHERE.md](DEPLOY_PYTHONANYWHERE.md)**

## 📁 File Structure

```
lego-pdf-downloader/
├── lego_pdf_ui.py          # Main Flask application
├── requirements.txt         # Python dependencies
├── Procfile                # For Railway/Heroku deployment
├── runtime.txt             # Python version specification
├── templates/
│   └── index.html          # Web interface
├── static/
│   └── images/             # Background images
│       ├── pirates.jpg
│       ├── space.jpg
│       └── forestmen.png
└── downloads/              # Where PDFs are saved (created automatically)
```

## 🎯 How It Works

1. User enters a LEGO set number (e.g., `10305`, `6080`, `75192`)
2. Script searches in priority order:
   - Lego.com (official source, sometimes blocked)
   - Archive.org (community archives)
   - BrickInstructions.com (scrapes and creates PDF)
3. Downloads or creates the PDF
4. Saves to Downloads folder
5. User can open/view the PDF

## 🛠️ Technologies Used

- **Backend:** Flask (Python)
- **Web Scraping:** BeautifulSoup4, Requests
- **PDF Generation:** ReportLab, Pillow
- **Frontend:** Vanilla HTML/CSS/JavaScript

## ⚠️ Known Limitations

- **Lego.com blocking:** Lego.com often blocks automated requests (403 Forbidden). This is normal - the script automatically falls back to Archive.org and BrickInstructions.com.
- **Temporary storage (Railway):** On Railway, downloaded PDFs don't persist between restarts. Users should download immediately.
- **PythonAnywhere performance:** Free tier has CPU limits, so downloads may be slower.

## 📝 License

Free to use for personal projects. Not affiliated with LEGO Group.

## 🤝 Contributing

Feel free to fork, improve, and submit pull requests!

## 💡 Tips

- Most LEGO sets from 1980s onwards are available
- Set numbers are usually 4-5 digits (e.g., 6080, 10305)
- Multiple booklets are combined into one PDF when available
- If one source fails, it automatically tries the next

---

**Made with ❤️ for LEGO fans**
