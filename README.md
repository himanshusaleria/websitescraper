# Website Content Downloader

A Python script to download the entire content of a website from a root URL. We'll use the `requests` library to fetch web pages and `BeautifulSoup` for parsing HTML.

## Features

This script provides a comprehensive website downloader with several key features:

- **Domain-specific downloading**
- **Recursive link extraction**
- **Unique filename generation**
- **Error handling**
- **Configurable page limit**

## Installation

Before running, install the required libraries:

```bash
pip install requests beautifulsoup4
```

Run the script by: 

```bash
python website_extractor.py https://example.com
```

Additional options:
```bash
# Limit to 20 pages
python website_extractor.py https://example.com -m 20

# Specify custom output directory
python website_extractor.py https://example.com -o my_extracted_text

# Exclude specific paths
python website_extractor.py https://example.com -x "blog" "category"

```


Note: 
- Replace `'https://example.com'` with your target website.
- Respect robots.txt and the website's terms of service.
- Some websites may block or rate-limit scraping attempts.

**Important**: Be aware of potential legal and ethical implications of mass downloading.

