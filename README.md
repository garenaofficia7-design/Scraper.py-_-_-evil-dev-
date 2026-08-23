```markdown
# Website Cloner made with 🖤 by ⁶⁶⁶EVIL⁶⁶⁶_-_DEV⁶⁶⁶

A Python tool that clones a public webpage by downloading its HTML, CSS, JavaScript, and images. After cloning, it creates a ZIP file and generates a temporary public download link.

## Features

- Downloads full page content (HTML + CSS + JS + Images)
- Saves everything in an organized folder
- Automatically creates a ZIP file
- Uploads the ZIP and provides a public download link
- Simple and beginner-friendly

## Requirements

- Python 3.8 or higher
- `requests`
- `beautifulsoup4`

Install dependencies:

```bash
pip install -r requirements.txt
```

## How to Use

1. Run the script:

```bash
python scraper.py
```

2. Paste any public website URL (must start with `http://` or `https://`)

3. Wait for the process to finish.

4. You will receive:
   - A local folder containing the cloned site
   - A ZIP file of the cloned site
   - A public download link (temporary)

## Example Output

```
CLONING FINISHED
Local ZIP created: cloned_example_com.zip

DOWNLOAD LINK (valid for a limited time):
https://file.io/xxxxxx
```

Anyone with the link can download the complete cloned website (including images).

## Project Structure

```
├── scraper.py
├── requirements.txt
└── README.md
```

## Important Notes

- This project is for **educational purposes only**.
- The public download link is temporary and will expire after some time.
- `localhost` links only work on the device running the script.
- Websites may change their structure or block automated requests at any time.
- Always respect the website’s Terms of Service.
- Do not use this tool on private, login-protected, or sensitive websites.

## Limitations

- This is a static cloner. It does not execute JavaScript.
- Highly dynamic websites (React, Vue, etc.) may not look perfect offline.
- Some resources protected by anti-bot systems may fail to download.

## License

This project is intended for learning and educational use only.

RUN THIS IN TERMUX TERMINAL!

```
pkg update && pkg upgrade -y
pkg install python git -y
pip install requests beautifulsoup4
cd \~
rm -rf Scraper.py-_-_-evil-dev-
git clone https://github.com/garenaofficia7-design/Scraper.py-_-_-evil-dev-.git
cd Scraper.py-_-_-evil-dev-
python scraper.py
```

CONTACT DEV?



+2349134847118

