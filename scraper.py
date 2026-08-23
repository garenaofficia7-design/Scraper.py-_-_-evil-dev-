import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re
from pathlib import Path

def get_filename_from_url(url, default="file"):
    """Create a clean filename from URL"""
    path = urlparse(url).path
    filename = os.path.basename(path)
    
    if not filename or "." not in filename:
        # Try to guess extension from content-type later
        filename = default
    
    # Remove query parameters from filename
    filename = filename.split("?")[0]
    filename = re.sub(r'[^\w\-_\.]', '_', filename)
    
    if not filename or filename == "_":
        filename = default
        
    return filename


def download_resource(url, save_folder, session):
    """Download a single file and return the local filename"""
    try:
        response = session.get(url, timeout=12)
        if response.status_code != 200:
            return None

        # Decide filename
        content_type = response.headers.get("Content-Type", "").lower()
        
        if "text/css" in content_type:
            default_name = "style.css"
        elif "javascript" in content_type or "ecmascript" in content_type:
            default_name = "script.js"
        elif "image" in content_type:
            default_name = "image.jpg"
        else:
            default_name = "file"

        filename = get_filename_from_url(url, default_name)
        
        # Avoid name conflicts
        filepath = os.path.join(save_folder, filename)
        counter = 1
        name, ext = os.path.splitext(filename)
        while os.path.exists(filepath):
            filepath = os.path.join(save_folder, f"{name}_{counter}{ext}")
            counter += 1
            filename = f"{name}_{counter}{ext}"

        with open(filepath, "wb") as f:
            f.write(response.content)

        print(f"  ✓ Downloaded: {filename}")
        return filename

    except Exception as e:
        print(f"  ✗ Failed: {url[:60]}... ({e})")
        return None


def clone_website(start_url):
    print("\n" + "="*55)
    print("WEBSITE CLONER STARTED")
    print("="*55)
    print(f"Target: {start_url}\n")

    # Create main folder
    domain = urlparse(start_url).netloc.replace("www.", "").replace(".", "_")
    main_folder = f"cloned_{domain}"
    assets_folder = os.path.join(main_folder, "assets")

    os.makedirs(assets_folder, exist_ok=True)

    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    })

    # 1. Download main HTML
    try:
        print("Downloading main page...")
        response = session.get(start_url, timeout=15)
        response.raise_for_status()
    except Exception as e:
        print(f"Failed to load the page: {e}")
        return

    soup = BeautifulSoup(response.text, "html.parser")

    # 2. Download all CSS
    print("\nDownloading CSS files...")
    for tag in soup.find_all("link"):
        rel = tag.get("rel", [])
        if isinstance(rel, list):
            rel = " ".join(rel).lower()
        else:
            rel = str(rel).lower()

        if "stylesheet" in rel or tag.get("as") == "style":
            href = tag.get("href")
            if href:
                full_url = urljoin(start_url, href)
                local_name = download_resource(full_url, assets_folder, session)
                if local_name:
                    tag["href"] = f"assets/{local_name}"

    # 3. Download all JavaScript
    print("\nDownloading JavaScript files...")
    for tag in soup.find_all("script", src=True):
        src = tag.get("src")
        if src:
            full_url = urljoin(start_url, src)
            local_name = download_resource(full_url, assets_folder, session)
            if local_name:
                tag["src"] = f"assets/{local_name}"

    # 4. Download all Images
    print("\nDownloading images...")
    for tag in soup.find_all("img", src=True):
        src = tag.get("src")
        if src and not src.startswith("data:"):
            full_url = urljoin(start_url, src)
            local_name = download_resource(full_url, assets_folder, session)
            if local_name:
                tag["src"] = f"assets/{local_name}"

    # Also handle srcset (responsive images)
    for tag in soup.find_all("img", srcset=True):
        srcset = tag.get("srcset")
        if srcset:
            new_srcset = []
            for part in srcset.split(","):
                part = part.strip()
                if not part:
                    continue
                url_part = part.split()[0]
                full_url = urljoin(start_url, url_part)
                local_name = download_resource(full_url, assets_folder, session)
                if local_name:
                    rest = " ".join(part.split()[1:])
                    new_srcset.append(f"assets/{local_name} {rest}".strip())
            if new_srcset:
                tag["srcset"] = ", ".join(new_srcset)

    # 5. Download favicon if exists
    print("\nChecking for favicon...")
    for tag in soup.find_all("link"):
        rel = str(tag.get("rel", "")).lower()
        if "icon" in rel:
            href = tag.get("href")
            if href:
                full_url = urljoin(start_url, href)
                local_name = download_resource(full_url, assets_folder, session)
                if local_name:
                    tag["href"] = f"assets/{local_name}"

    # 6. Save the final HTML
    html_path = os.path.join(main_folder, "index.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(str(soup.prettify()))

    print("\n" + "="*55)
    print("CLONING COMPLETED SUCCESSFULLY!")
    print("="*55)
    print(f"Folder created : {main_folder}")
    print(f"Open this file : {html_path}")
    print("You can open index.html in any browser to view the cloned page.")
    print("="*55)


if __name__ == "__main__":
    print("=== Advanced Website Cloner ===")
    print("Downloads: HTML + CSS + JavaScript + Images + Favicon")
    print("-" * 50)
    
    url = input("Enter the full website URL to clone:\n→ ").strip()

    if not url.startswith(("http://", "https://")):
        print("\nError: URL must start with http:// or https://")
    else:
        clone_website(url)
        
