import requests
from bs4 import BeautifulSoup
import csv
import json
from datetime import datetime
from urllib.parse import urljoin, urlparse

def scrape_any_page(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        print(f"\nConnecting to: {url}")
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch page: {e}")
        return

    soup = BeautifulSoup(response.text, "html.parser")

    title = soup.title.get_text(strip=True) if soup.title else "No title found"

    headings = []
    for tag in ["h1", "h2", "h3", "h4"]:
        for h in soup.find_all(tag):
            text = h.get_text(strip=True)
            if text:
                headings.append({"level": tag, "text": text})

    links = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        full_url = urljoin(url, href)
        text = a.get_text(strip=True) or "(no text)"
        links.append({"text": text, "url": full_url})

    paragraphs = [p.get_text(strip=True) for p in soup.find_all("p") if p.get_text(strip=True)]

    code_blocks = []
    for code in soup.find_all(["code", "pre"]):
        text = code.get_text(strip=True)
        if text and len(text) > 10:
            code_blocks.append(text)

    print("\n" + "="*60)
    print(f"Title       : {title}")
    print(f"Headings    : {len(headings)}")
    print(f"Links       : {len(links)}")
    print(f"Paragraphs  : {len(paragraphs)}")
    print(f"Code blocks : {len(code_blocks)}")
    print("="*60)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    domain = urlparse(url).netloc.replace(".", "_") or "page"

    # Save CSV
    csv_file = f"scrape_{domain}_{timestamp}.csv"
    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Type", "Content"])
        writer.writerow(["Title", title])
        writer.writerow([])
        writer.writerow(["=== HEADINGS ===", ""])
        for h in headings:
            writer.writerow([h["level"], h["text"]])
        writer.writerow([])
        writer.writerow(["=== LINKS ===", ""])
        for link in links:
            writer.writerow([link["text"], link["url"]])
        writer.writerow([])
        writer.writerow(["=== CODE BLOCKS ===", ""])
        for i, code in enumerate(code_blocks, 1):
            writer.writerow([f"Code {i}", code[:500] + ("..." if len(code) > 500 else "")])

    # Save JSON
    json_file = f"scrape_{domain}_{timestamp}.json"
    data = {
        "url": url,
        "scraped_at": datetime.now().isoformat(),
        "title": title,
        "headings": headings,
        "links": links,
        "paragraphs": paragraphs[:50],
        "code_blocks": code_blocks
    }
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\nResults saved:")
    print(f"  → {csv_file}")
    print(f"  → {json_file}")


if __name__ == "__main__":
    print("=== Simple Web Scraper ===")
    print("Enter the full URL you want to scrape (including https://)")
    target_url = input("URL: ").strip()

    if not target_url.startswith("http"):
        print("Please enter a full URL starting with http:// or https://")
    else:
        scrape_any_page(target_url)
