import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re
import zipfile
import time

def clean_filename(url, default="file"):
    path = urlparse(url).path
    name = os.path.basename(path).split("?")[0]
    name = re.sub(r'[^\w\-_\.]', '_', name)
    if not name or name == "_" or "." not in name:
        name = default
    return name

def download_file(url, folder, session):
    try:
        r = session.get(url, timeout=12)
        if r.status_code != 200:
            return None

        content_type = r.headers.get("Content-Type", "").lower()
        if "css" in content_type:
            default = "style.css"
        elif "javascript" in content_type:
            default = "script.js"
        elif "image" in content_type:
            default = "image.png"
        else:
            default = "file"

        filename = clean_filename(url, default)
        path = os.path.join(folder, filename)

        base, ext = os.path.splitext(filename)
        counter = 1
        while os.path.exists(path):
            filename = f"{base}_{counter}{ext}"
            path = os.path.join(folder, filename)
            counter += 1

        with open(path, "wb") as f:
            f.write(r.content)
        print(f"  ✓ {filename}")
        return filename
    except:
        return None

def make_zip(folder):
    zip_name = folder + ".zip"
    with zipfile.ZipFile(zip_name, "w", zipfile.ZIP_DEFLATED) as z:
        for root, _, files in os.walk(folder):
            for file in files:
                full = os.path.join(root, file)
                arc = os.path.relpath(full, os.path.dirname(folder))
                z.write(full, arc)
    return zip_name

def upload_zip(zip_path):
    """Upload ZIP to a temporary host and return download link"""
    print("\nUploading ZIP to get a download link...")
    try:
        with open(zip_path, "rb") as f:
            response = requests.post(
                "https://file.io",
                files={"file": f},
                timeout=60
            )
        data = response.json()
        if data.get("success"):
            return data.get("link")
        else:
            return None
    except Exception as e:
        print("Upload failed:", e)
        return None

def clone(url):
    print("\n" + "="*55)
    print("WEBSITE CLONER")
    print("="*55)

    domain = urlparse(url).netloc.replace("www.", "").replace(".", "_")
    folder = f"cloned_{domain}"
    assets = os.path.join(folder, "assets")
    os.makedirs(assets, exist_ok=True)

    session = requests.Session()
    session.headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

    try:
        print("Downloading main page...")
        res = session.get(url, timeout=15)
        res.raise_for_status()
    except Exception as e:
        print("Failed to load page:", e)
        return

    soup = BeautifulSoup(res.text, "html.parser")

    print("\nDownloading CSS...")
    for tag in soup.find_all("link"):
        if "stylesheet" in str(tag.get("rel", "")).lower():
            href = tag.get("href")
            if href:
                full = urljoin(url, href)
                name = download_file(full, assets, session)
                if name:
                    tag["href"] = f"assets/{name}"

    print("\nDownloading JavaScript...")
    for tag in soup.find_all("script", src=True):
        src = tag["src"]
        full = urljoin(url, src)
        name = download_file(full, assets, session)
        if name:
            tag["src"] = f"assets/{name}"

    print("\nDownloading images...")
    for tag in soup.find_all("img", src=True):
        src = tag["src"]
        if not src.startswith("data:"):
            full = urljoin(url, src)
            name = download_file(full, assets, session)
            if name:
                tag["src"] = f"assets/{name}"

    print("\nChecking favicon...")
    for tag in soup.find_all("link"):
        if "icon" in str(tag.get("rel", "")).lower():
            href = tag.get("href")
            if href:
                full = urljoin(url, href)
                name = download_file(full, assets, session)
                if name:
                    tag["href"] = f"assets/{name}"

    # Save HTML
    with open(os.path.join(folder, "index.html"), "w", encoding="utf-8") as f:
        f.write(str(soup.prettify()))

    print("\n" + "="*55)
    print("CLONING FINISHED")
    print("="*55)

    # Create ZIP
    zip_file = make_zip(folder)
    print(f"\nLocal ZIP created: {zip_file}")

    # Upload and get link
    link = upload_zip(zip_file)
    if link:
        print("\n" + "="*55)
        print("DOWNLOAD LINK (valid for a limited time):")
        print(link)
        print("="*55)
        print("Anyone can use this link to download the full cloned site (with images).")
    else:
        print("\nCould not create public link. You can still use the local ZIP file.")

if __name__ == "__main__":
    print("=== Website Cloner ===")
    print("Clones HTML + CSS + JS + Images and gives a download link\n")
    url = input("Enter the website URL:\n→ ").strip()

    if not url.startswith(("http://", "https://")):
        print("Please enter a valid URL starting with https://")
    else:
        clone(url)
