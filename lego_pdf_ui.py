#!/usr/bin/env python3
"""
Web UI for Lego Instructions -> PDF downloader
A Flask-based interface for downloading Lego instruction manuals.

Usage:
  python lego_pdf_ui.py

Then open http://localhost:5000 in your browser

Requirements:
  pip install flask requests beautifulsoup4 pillow reportlab
"""

from flask import Flask, render_template, request, jsonify, send_file
import os
import re
import requests
import urllib.parse
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
import threading
import time
import pathlib

app = Flask(__name__, static_folder='static', static_url_path='/static')

# Store download progress
download_status = {}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# Configure output directory
# For local: saves to user's Downloads folder
# For deployment: saves to a 'downloads' folder in the app directory
if os.path.exists(str(pathlib.Path.home() / "Downloads")):
    # Local environment (Windows/Mac/Linux with Downloads folder)
    OUTPUT_DIR = str(pathlib.Path.home() / "Downloads")
else:
    # Deployment environment (Railway, PythonAnywhere, etc.)
    OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "downloads")
    os.makedirs(OUTPUT_DIR, exist_ok=True)

print(f"Saving PDFs to: {OUTPUT_DIR}")


def make_filename(set_number, set_name):
    """Generate filename like Lego_6080 - King's Castle.pdf"""
    if set_name:
        safe_name = re.sub(r'[\\/:*?"<>|]', "", set_name).strip()
        # FIX #3: Remove duplicate set number from name if present
        # Handle cases like "10497 - Galaxy Explorer" -> just "Galaxy Explorer"
        safe_name = re.sub(rf'^{set_number}\s*-?\s*', '', safe_name, flags=re.IGNORECASE).strip()
        return f"Lego_{set_number} - {safe_name}.pdf"
    return f"Lego_{set_number}.pdf"


def try_lego_official(set_number):
    """Try to find PDF instructions on official Lego.com website."""
    try:
        print(f"   Checking official Lego.com for set {set_number}...")
        
        page_url = f"https://www.lego.com/en-us/service/building-instructions/{set_number}"
        resp = requests.get(page_url, headers=HEADERS, timeout=15, allow_redirects=True)
        
        # Handle different status codes with informative messages
        if resp.status_code == 403:
            print(f"   ⚠ Lego.com blocked this request (403 Forbidden)")
            print(f"   → This is normal - Lego.com often blocks automated tools")
            print(f"   → Trying alternative sources (Archive.org, brickinstructions.com)...")
            return None, ""
        elif resp.status_code == 404:
            print(f"   Set {set_number} not found on Lego.com (404)")
            return None, ""
        elif resp.status_code != 200:
            print(f"   Lego.com returned status {resp.status_code}")
            print(f"   → Trying alternative sources...")
            return None, ""
        
        html_text = resp.text
        
        # Multiple methods to find PDFs
        pdf_links = []
        
        # Method 1: Direct CDN pattern with product.bi.core.pdf
        pattern1 = r'https://www\.lego\.com/cdn/product-assets/product\.bi\.core\.pdf/\d+\.pdf'
        found1 = re.findall(pattern1, html_text)
        pdf_links.extend(found1)
        
        # Method 2: Any lego.com CDN PDF
        pattern2 = r'https://[^"\s<>]*?lego\.com/cdn/[^"\s<>]*?\.pdf'
        found2 = re.findall(pattern2, html_text)
        pdf_links.extend(found2)
        
        # Method 3: Look in href attributes specifically
        soup = BeautifulSoup(html_text, "html.parser")
        for link in soup.find_all('a', href=True):
            href = link['href']
            if '.pdf' in href.lower() and 'lego.com' in href:
                if href.startswith('http'):
                    pdf_links.append(href)
                elif href.startswith('//'):
                    pdf_links.append('https:' + href)
                elif href.startswith('/'):
                    pdf_links.append('https://www.lego.com' + href)
        
        # Remove duplicates while preserving order
        unique_pdfs = list(dict.fromkeys(pdf_links))
        
        # Get set name
        set_name = ""
        h1 = soup.find('h1')
        if h1:
            set_name = h1.get_text().strip()
            set_name = re.sub(r'Building Instructions?\s*-?\s*', '', set_name, flags=re.IGNORECASE)
            set_name = re.sub(r'Download\s*', '', set_name, flags=re.IGNORECASE)
            set_name = set_name.strip()
        
        if unique_pdfs:
            print(f"   ✓ Found {len(unique_pdfs)} PDF(s) on Lego.com!")
            print(f"   Using: {unique_pdfs[0]}")
            return unique_pdfs[0], set_name
        
        print(f"   No PDFs found on page (may require JavaScript)")
        print(f"   → Trying alternative sources...")
        return None, ""
        
    except requests.exceptions.RequestException as e:
        print(f"   Connection error: {e}")
        print(f"   → Trying alternative sources...")
        return None, ""
    except Exception as e:
        print(f"   Lego.com error: {e}")
        print(f"   → Trying alternative sources...")
        return None, ""


def try_archive(set_number):
    """Try Internet Archive using full search."""
    try:
        # Try multiple search strategies
        search_queries = [
            f"https://archive.org/advancedsearch.php?q=identifier:lego-{set_number}-*&fl[]=identifier&fl[]=title&rows=10&output=json",
            f"https://archive.org/advancedsearch.php?q=lego%20{set_number}%20instructions&fl[]=identifier&fl[]=title&rows=10&output=json",
            f"https://archive.org/advancedsearch.php?q=lego%20{set_number}&fl[]=identifier&fl[]=title&rows=10&output=json"
        ]
        
        for search_url in search_queries:
            print(f"   Searching Archive.org for set {set_number}...")
            resp = requests.get(search_url, headers=HEADERS, timeout=15)
            resp.raise_for_status()
            docs = resp.json().get("response", {}).get("docs", [])
            print(f"   Found {len(docs)} potential matches")
            
            for doc in docs:
                identifier = doc.get("identifier", "")
                title = doc.get("title", "")
                title_lower = title.lower()
                identifier_lower = identifier.lower()
                
                # Skip obviously unrelated results
                if "voa" in title_lower or "voice of america" in title_lower:
                    continue
                    
                print(f"   Checking: {title} ({identifier})")
                
                # Check if this looks like a LEGO instructions document
                if (set_number in identifier or set_number in str(title)) and \
                   ("lego" in title_lower or "lego" in identifier_lower):
                    print(f"   Match found! Fetching metadata...")
                    meta = requests.get(f"https://archive.org/metadata/{identifier}", headers=HEADERS, timeout=15)
                    files = meta.json().get("files", [])
                    for f in files:
                        name = f.get("name", "")
                        if name.lower().endswith(".pdf") and "text.pdf" not in name.lower():
                            encoded = urllib.parse.quote(name)
                            set_name = re.sub(rf"(?i)lego\s*(instructions?\s*)?({set_number}[-\s]?\d*)?\s*", "", title).strip()
                            print(f"   Found PDF: {name}")
                            return f"https://archive.org/download/{identifier}/{encoded}", set_name
    except Exception as e:
        print(f"   Archive.org error: {e}")
    print(f"   No PDF found on Archive.org for set {set_number}")
    return None, ""


def get_brickinstructions_images(set_number):
    """Scrape full-size image URLs and set name from lego.brickinstructions.com."""
    url = f"https://lego.brickinstructions.com/lego_instructions/set/{set_number}/"
    resp = requests.get(url, headers=HEADERS, timeout=15)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")

    set_name = ""
    h1 = soup.find("h1")
    if h1:
        text = h1.get_text()
        for prefix in [f"LEGO Instructions for set {set_number}-1 ", f"LEGO Instructions for set {set_number} "]:
            if prefix in text:
                set_name = text.replace(prefix, "").strip()
                set_name = re.split(r"\s+which\s+", set_name)[0].strip()
                break

    images = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "/instructions/" in href and href.lower().endswith(".jpg") and "main.jpg" not in href:
            full_url = urllib.parse.urljoin("https://lego.brickinstructions.com", href)
            if full_url not in images:
                images.append(full_url)

    return images, set_name


def download_pdf(pdf_url, output_path, set_number):
    """Download a pre-made PDF directly."""
    resp = requests.get(pdf_url, headers=HEADERS, timeout=120, stream=True)
    resp.raise_for_status()
    total = int(resp.headers.get("content-length", 0))
    downloaded = 0
    with open(output_path, "wb") as f:
        for chunk in resp.iter_content(chunk_size=65536):
            f.write(chunk)
            downloaded += len(chunk)
            if total:
                progress = int(downloaded / total * 100)
                download_status[set_number] = {
                    "status": "downloading",
                    "message": f"Downloading PDF: {progress}%",
                    "progress": progress
                }


def download_images(image_urls, set_number):
    images = []
    total = len(image_urls)
    for i, url in enumerate(image_urls, 1):
        download_status[set_number] = {
            "status": "downloading",
            "message": f"Downloading page {i} of {total}",
            "progress": int((i / total) * 50)  # First 50% for downloading
        }
        try:
            resp = requests.get(url, headers=HEADERS, timeout=15)
            resp.raise_for_status()
            img = Image.open(BytesIO(resp.content)).convert("RGB")
            images.append((img, url))
        except Exception as e:
            pass
    return images


def images_to_pdf(images, output_path, set_number):
    c = canvas.Canvas(output_path)
    total = len(images)

    for i, (img, url) in enumerate(images, 1):
        download_status[set_number] = {
            "status": "processing",
            "message": f"Creating PDF page {i} of {total}",
            "progress": 50 + int((i / total) * 50)  # Second 50% for PDF creation
        }

        img_w, img_h = img.size
        page_w, page_h = landscape(A4) if img_w > img_h else A4
        c.setPageSize((page_w, page_h))

        margin = 20
        scale = min((page_w - 2*margin) / img_w, (page_h - 2*margin) / img_h)
        draw_w, draw_h = img_w * scale, img_h * scale
        x = (page_w - draw_w) / 2
        y = (page_h - draw_h) / 2

        tmp = f"_tmp_{set_number}_{i}.png"
        img.save(tmp, format="PNG")
        c.drawImage(tmp, x, y, width=draw_w, height=draw_h, preserveAspectRatio=True)
        os.remove(tmp)

        c.setFont("Helvetica", 8)
        c.setFillColorRGB(0.6, 0.6, 0.6)
        c.drawCentredString(page_w/2, 8, f"Set {set_number}  •  Page {i} of {total}")
        c.showPage()

    c.save()


def process_download(set_number):
    """Background thread to handle the download process."""
    try:
        download_status[set_number] = {
            "status": "searching",
            "message": "Searching for set...",
            "progress": 0
        }

        # Priority 1: Try official Lego.com first
        pdf_url, set_name = try_lego_official(set_number)
        if pdf_url:
            filename = make_filename(set_number, set_name)
            output_path = os.path.join(OUTPUT_DIR, filename)
            download_status[set_number] = {
                "status": "downloading",
                "message": "Found on Lego.com, downloading...",
                "progress": 10
            }
            download_pdf(pdf_url, output_path, set_number)
            download_status[set_number] = {
                "status": "complete",
                "message": "Download complete!",
                "progress": 100,
                "filename": filename,
                "set_name": set_name,
                "source": "Lego.com"
            }
            return

        # Priority 2: Try Archive.org
        pdf_url, set_name = try_archive(set_number)
        if pdf_url:
            filename = make_filename(set_number, set_name)
            output_path = os.path.join(OUTPUT_DIR, filename)
            download_status[set_number] = {
                "status": "downloading",
                "message": "Found on Archive.org, downloading...",
                "progress": 10
            }
            download_pdf(pdf_url, output_path, set_number)
            download_status[set_number] = {
                "status": "complete",
                "message": "Download complete!",
                "progress": 100,
                "filename": filename,
                "set_name": set_name,
                "source": "Archive.org"
            }
            return

        # Priority 3: Fallback to brickinstructions.com
        download_status[set_number] = {
            "status": "searching",
            "message": "Searching brickinstructions.com...",
            "progress": 5
        }

        image_urls, set_name = get_brickinstructions_images(set_number)
        if not image_urls:
            download_status[set_number] = {
                "status": "error",
                "message": f"Could not find set {set_number}",
                "progress": 0
            }
            return

        filename = make_filename(set_number, set_name)
        output_path = os.path.join(OUTPUT_DIR, filename)

        download_status[set_number] = {
            "status": "downloading",
            "message": f"Found {len(image_urls)} pages",
            "progress": 10
        }

        images = download_images(image_urls, set_number)
        images_to_pdf(images, output_path, set_number)

        download_status[set_number] = {
            "status": "complete",
            "message": "PDF created successfully!",
            "progress": 100,
            "filename": filename,
            "set_name": set_name,
            "source": "brickinstructions.com"
        }

    except Exception as e:
        download_status[set_number] = {
            "status": "error",
            "message": str(e),
            "progress": 0
        }


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/download', methods=['POST'])
def start_download():
    set_number = request.json.get('set_number', '').strip()
    if not set_number:
        return jsonify({"error": "Please enter a set number"}), 400

    # Start download in background thread
    thread = threading.Thread(target=process_download, args=(set_number,))
    thread.daemon = True
    thread.start()

    return jsonify({"message": "Download started", "set_number": set_number})


@app.route('/status/<set_number>')
def get_status(set_number):
    status = download_status.get(set_number, {"status": "unknown"})
    return jsonify(status)


@app.route('/file/<filename>')
def download_file(filename):
    filepath = os.path.join(OUTPUT_DIR, filename)
    if os.path.exists(filepath):
        # Open in browser instead of forcing download
        return send_file(filepath, mimetype='application/pdf')
    return "File not found", 404


if __name__ == '__main__':
    print("\n" + "="*60)
    print("🧱 LEGO Instructions PDF Downloader")
    print("="*60)
    print(f"\n💾 Saving PDFs to: {OUTPUT_DIR}")
    print("\n📱 Open in your browser: http://localhost:5000")
    print("\n💡 Press Ctrl+C to stop the server\n")
    app.run(debug=True, host='0.0.0.0', port=5000)
