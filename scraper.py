import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re
import zipfile

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
            return None, None

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
        return filename, r.text if "text" in content_type or "javascript" in content_type or "css" in content_type else None
    except:
        return None, None

def make_zip(folder):
    zip_name = folder + ".zip"
    with zipfile.ZipFile(zip_name, "w", zipfile.ZIP_DEFLATED) as z:
        for root, _, files in os.walk(folder):
            for file in files:
                full = os.path.join(root, file)
                arc = os.path.relpath(full, os.path.dirname(folder))
                z.write(full, arc)
    return zip_name

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
    html_code = str(soup.prettify())

    css_codes = []
    js_codes = []

    print("\nDownloading CSS...")
    for tag in soup.find_all("link"):
        if "stylesheet" in str(tag.get("rel", "")).lower():
            href = tag.get("href")
            if href:
                full = urljoin(url, href)
                name, content = download_file(full, assets, session)
                if name:
                    tag["href"] = f"assets/{name}"
                    if content:
                        css_codes.append((name, content))

    print("\nDownloading JavaScript...")
    for tag in soup.find_all("script", src=True):
        src = tag["src"]
        full = urljoin(url, src)
        name, content = download_file(full, assets, session)
        if name:
            tag["src"] = f"assets/{name}"
            if content:
                js_codes.append((name, content))

    print("\nDownloading images...")
    for tag in soup.find_all("img", src=True):
        src = tag["src"]
        if not src.startswith("data:"):
            full = urljoin(url, src)
            name, _ = download_file(full, assets, session)
            if name:
                tag["src"] = f"assets/{name}"

    print("\nChecking favicon...")
    for tag in soup.find_all("link"):
        if "icon" in str(tag.get("rel", "")).lower():
            href = tag.get("href")
            if href:
                full = urljoin(url, href)
                name, _ = download_file(full, assets, session)
                if name:
                    tag["href"] = f"assets/{name}"

    # Save final HTML
    final_html = str(soup.prettify())
    with open(os.path.join(folder, "index.html"), "w", encoding="utf-8") as f:
        f.write(final_html)

    print("\n" + "="*55)
    print("CLONING FINISHED")
    print("="*55)

    zip_file = make_zip(folder)
    print(f"\nZIP created: {zip_file}")

    # ========== PRINT THE CODES ==========
    print("\n\n" + "="*60)
    print("========== HTML CODE ==========")
    print("="*60)
    print(final_html[:3000])          # first 3000 characters
    if len(final_html) > 3000:
        print("\n... (HTML truncated, full version is in index.html)")

    if css_codes:
        print("\n\n" + "="*60)
        print("========== CSS CODES ==========")
        print("="*60)
        for name, code in css_codes:
            print(f"\n----- {name} -----")
            print(code[:2000])
            if len(code) > 2000:
                print("... (truncated)")

    if js_codes:
        print("\n\n" + "="*60)
        print("========== JAVASCRIPT CODES ==========")
        print("="*60)
        for name, code in js_codes:
            print(f"\n----- {name} -----")
            print(code[:2000])
            if len(code) > 2000:
                print("... (truncated)")

    print("\n" + "="*60)
    print("Full codes are saved inside the ZIP and folder.")
    print("="*60)

if __name__ == "__main__":
    print("=== Website Cloner ===")
    url = input("Enter the website URL:\n→ ").strip()

    if not url.startswith(("http://", "https://")):
        print("URL must start with http:// or https://")
    else:
        clone(url)
