import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re
import zipfile
import threading
import http.server
import socketserver
import time

def get_filename_from_url(url, default="file"):
    path = urlparse(url).path
    filename = os.path.basename(path)
    if not filename or "." not in filename:
        filename = default
    filename = filename.split("?")[0]
    filename = re.sub(r'[^\w\-_\.]', '_', filename)
    if not filename or filename == "_":
        filename = default
    return filename


def download_resource(url, save_folder, session):
    try:
        response = session.get(url, timeout=12)
        if response.status_code != 200:
            return None

        content_type = response.headers.get("Content-Type", "").lower()
        if "text/css" in content_type:
            default_name = "style.css"
        elif "javascript" in content_type:
            default_name = "script.js"
        elif "image" in content_type:
            default_name = "image.jpg"
        else:
            default_name = "file"

        filename = get_filename_from_url(url, default_name)
        filepath = os.path.join(save_folder, filename)
        counter = 1
        name, ext = os.path.splitext(filename)
        while os.path.exists(filepath):
            filepath = os.path.join(save_folder, f"{name}_{counter}{ext}")
            counter += 1
            filename = f"{name}_{counter}{ext}"

        with open(filepath, "wb") as f:
            f.write(response.content)
        print(f"  ✓ {filename}")
        return filename
    except:
        return None


def create_zip(folder_name):
    zip_name = f"{folder_name}.zip"
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(folder_name):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, os.path.dirname(folder_name))
                zipf.write(file_path, arcname)
    return zip_name


def start_server(folder, port=8000):
    os.chdir(folder)
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"\nLocal server started!")
        print(f"Open this link in your browser:")
        print(f"→ http://localhost:{port}")
        print(f"→ http://127.0.0.1:{port}")
        print("\nPress Ctrl + C to stop the server when you're done.")
        httpd.serve_forever()


def clone_website(start_url):
    print("\n" + "="*55)
    print("WEBSITE CLONER STARTED")
    print("="*55)

    domain = urlparse(start_url).netloc.replace("www.", "").replace(".", "_")
    main_folder = f"cloned_{domain}"
    assets_folder = os.path.join(main_folder, "assets")
    os.makedirs(assets_folder, exist_ok=True)

    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    })

    try:
        print("Downloading main page...")
        response = session.get(start_url, timeout=15)
        response.raise_for_status()
    except Exception as e:
        print(f"Failed to load page: {e}")
        return

    soup = BeautifulSoup(response.text, "html.parser")

    print("\nDownloading CSS...")
    for tag in soup.find_all("link"):
        rel = str(tag.get("rel", "")).lower()
        if "stylesheet" in rel:
            href = tag.get("href")
            if href:
                full_url = urljoin(start_url, href)
                local = download_resource(full_url, assets_folder, session)
                if local:
                    tag["href"] = f"assets/{local}"

    print("\nDownloading JavaScript...")
    for tag in soup.find_all("script", src=True):
        src = tag.get("src")
        if src:
            full_url = urljoin(start_url, src)
            local = download_resource(full_url, assets_folder, session)
            if local:
                tag["src"] = f"assets/{local}"

    print("\nDownloading images...")
    for tag in soup.find_all("img", src=True):
        src = tag.get("src")
        if src and not src.startswith("data:"):
            full_url = urljoin(start_url, src)
            local = download_resource(full_url, assets_folder, session)
            if local:
                tag["src"] = f"assets/{local}"

    print("\nChecking favicon...")
    for tag in soup.find_all("link"):
        if "icon" in str(tag.get("rel", "")).lower():
            href = tag.get("href")
            if href:
                full_url = urljoin(start_url, href)
                local = download_resource(full_url, assets_folder, session)
                if local:
                    tag["href"] = f"assets/{local}"

    # Save HTML
    html_path = os.path.join(main_folder, "index.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(str(soup.prettify()))

    print("\n" + "="*55)
    print("CLONING COMPLETED!")
    print("="*55)

    # Create ZIP
    print("\nCreating ZIP file...")
    zip_file = create_zip(main_folder)
    print(f"ZIP created: {zip_file}")

    print(f"\nFolder: {main_folder}")
    print(f"ZIP file: {zip_file}")
    print(f"Main file: {html_path}")

    # Ask if user wants local server
    choice = input("\nDo you want to open it with a local link now? (y/n): ").strip().lower()
    if choice == "y":
        print("\nStarting local server...")
        time.sleep(1)
        start_server(main_folder)
    else:
        print("\nDone! You can open the index.html or the ZIP file anytime.")


if __name__ == "__main__":
    print("=== Advanced Website Cloner ===")
    url = input("Enter the full website URL to clone:\n→ ").strip()

    if not url.startswith(("http://", "https://")):
        print("URL must start with http:// or https://")
    else:
        clone_website(url)
