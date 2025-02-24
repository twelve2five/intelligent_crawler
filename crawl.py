import requests
from bs4 import BeautifulSoup
import csv
import openai
import urllib.parse
from urllib.parse import urlparse, urljoin
import time
import argparse
import os
from openai import OpenAI
import random
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

# Load API key from environment variable
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("Please set the OPENAI_API_KEY environment variable")

def fetch_page(url):
    """Fetches the HTML content for a given URL with enhanced headers and retry mechanism."""
    # List of common user agents to rotate through
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59'
    ]
    
    headers = {
        'User-Agent': random.choice(user_agents),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'max-age=0',
        'DNT': '1',  # Do Not Track
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
    }
    
    # Configure retry strategy
    retry_strategy = Retry(
        total=3,  # number of retries
        backoff_factor=1,  # wait 1, 2, 4 seconds between retries
        status_forcelist=[429, 500, 502, 503, 504],  # status codes to retry on
    )
    
    session = requests.Session()
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    try:
        # Add a random delay between requests (1-3 seconds)
        time.sleep(random.uniform(1, 3))
        
        response = session.get(
            url,
            headers=headers,
            timeout=30,
            verify=True,
            allow_redirects=True
        )
        response.raise_for_status()
        return response.text
    except requests.exceptions.SSLError:
        print(f"SSL Error for {url}, trying without verification...")
        try:
            response = session.get(
                url,
                headers=headers,
                timeout=30,
                verify=False,
                allow_redirects=True
            )
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None
    finally:
        session.close()

def extract_links(html, base_url):
    """
    Extracts and returns all internal links from the HTML content.
    Only returns URLs that share the same domain as the base_url.
    """
    soup = BeautifulSoup(html, 'html.parser')
    links = set()
    for a in soup.find_all('a', href=True):
        href = a['href']
        # Convert relative URL to absolute URL
        absolute_link = urljoin(base_url, href)
        # Only consider links within the same domain
        if urlparse(absolute_link).netloc == urlparse(base_url).netloc:
            links.add(absolute_link)
    return links

def extract_details(html, url):
    """
    Extracts details from the HTML, such as the title and main text content.
    Strips out script and style tags.
    """
    soup = BeautifulSoup(html, 'html.parser')
    title = soup.title.string.strip() if soup.title else ""
    # Remove scripts and styles for a cleaner text extraction
    for script in soup(["script", "style"]):
        script.decompose()
    content = soup.get_text(separator=' ', strip=True)
    return {"url": url, "title": title, "content": content}

def get_intelligent_context(text):
    """
    Uses OpenAI's API to generate a summary and extract key themes from the text.
    Limits the text to the first 1000 characters to respect token limits.
    """
    client = OpenAI()  # This will use the api key from environment variable

    truncated_text = text[:1000]  # Adjust as needed based on your token constraints
    prompt = f"Summarize the following webpage content and extract key themes and keywords:\n\n{truncated_text}"
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=150
        )
        summary = response.choices[0].message.content.strip()
        return summary
    except Exception as e:
        print(f"Error fetching intelligent context: {e}")
        return ""

def crawl_website(start_url, max_pages=100):
    """
    Crawls a website starting from start_url with improved error handling.
    """
    visited = set()
    to_visit = [start_url]
    results = []
    
    error_count = 0
    max_errors = 5
    retry_delay = 5  # seconds to wait after an error

    while to_visit and len(visited) < max_pages and error_count < max_errors:
        url = to_visit.pop(0)
        if url in visited:
            continue
            
        print(f"Crawling: {url}")
        html = fetch_page(url)
        
        if html is None:
            error_count += 1
            print(f"Error {error_count}/{max_errors}. Waiting {retry_delay} seconds before next attempt...")
            time.sleep(retry_delay)
            continue
        else:
            error_count = 0
            
        details = extract_details(html, url)
        details["intelligent_context"] = get_intelligent_context(details["content"])
        results.append(details)
        visited.add(url)
        
        links = extract_links(html, start_url)
        for link in links:
            if link not in visited and link not in to_visit:
                to_visit.append(link)
        
        # Random delay between successful requests
        time.sleep(random.uniform(2, 4))
        
    if error_count >= max_errors:
        print(f"Stopping crawl due to {max_errors} consecutive errors")
        
    return results

def write_to_csv(data, filename="output.csv"):
    """
    Writes the crawled data to a CSV file.
    Each row includes the URL, page title, content, and intelligent context.
    """
    if not data:
        print("No data to write.")
        return
    fieldnames = list(data[0].keys())
    with open(filename, 'w', newline='', encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            writer.writerow(row)
    print(f"Data written to {filename}")

if __name__ == "__main__":
    print("Welcome to the Web Crawler!")
    url = input("Please enter the URL to crawl (e.g., https://example.com): ")
    max_pages = input("Enter maximum number of pages to crawl (default is 100): ")
    
    try:
        max_pages = int(max_pages) if max_pages.strip() else 100
    except ValueError:
        print("Invalid number, using default of 100 pages")
        max_pages = 100

    print(f"\nStarting crawl of {url}")
    print(f"Will crawl up to {max_pages} pages")
    
    crawled_data = crawl_website(url, max_pages=max_pages)
    write_to_csv(crawled_data)
