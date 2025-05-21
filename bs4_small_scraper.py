import requests
from bs4 import BeautifulSoup
import csv
import logging
from urllib.parse import urlparse
import time
import os
import argparse
from config import Config
import concurrent.futures
import re

# Setup logging
logger = logging.getLogger(__name__)

def get_text_from_url(url, timeout=10):
    """Extract plain text from a URL"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://www.google.com/',
        'DNT': '1',
    }
    
    try:
        logger.info(f"Requesting content from {url}")
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        
        # Parse with BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script and style tags
        for script_or_style in soup(['script', 'style', 'header', 'footer', 'nav']):
            script_or_style.decompose()
        
        # Get text and clean it up
        text = soup.get_text(separator=' ', strip=True)
        
        # Remove extra whitespace and normalize
        text = ' '.join(text.split())
        
        logger.info(f"Successfully extracted {len(text)} chars from {url}")
        return text
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching {url}: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error processing {url}: {e}")
        return None

def process_url(url_info, source_char_limit):
    """Process a single URL and return the extracted content"""
    url, description = url_info
    
    # Format the source info
    netloc = urlparse(url).netloc
    source_info = f"Source: {netloc}"
    if description:
        source_info += f" - {description}"
    
    # Skip Google domains
    if re.match(r'(www\.)?google\.[a-z]+', netloc):
        logger.info(f"Skipping Google domain: {netloc}")
        return None
    
    # Extract content
    content = get_text_from_url(url)
    if content is None:
        # Skip URLs with errors
        return None
    
    # Limit the content to source_char_limit and include source info
    excerpt = content[:source_char_limit]
    return (source_info, excerpt)

def scrape_first_urls(csv_path, output_txt_path, max_urls=None, char_limit=None):
    """Scrape content from the first URLs in the CSV file"""
    # Use configuration values if not specified
    if max_urls is None:
        max_urls = Config.MAX_URLS_TO_SCRAPE
    if char_limit is None:
        char_limit = Config.MAX_CHARACTERS_IN_SUMMARY
    
    # Calculate per-source character limit (1/4 of total, but at least 200 chars)
    source_char_limit = max(200, char_limit // 4)
    logger.info(f"Per-source character limit: {source_char_limit}")
    
    urls_to_process = []
    
    # Read URLs from CSV
    try:
        with open(csv_path, 'r', encoding='utf-8') as csv_file:
            reader = csv.reader(csv_file)
            next(reader)  # Skip header
            for i, row in enumerate(reader):
                if i >= max_urls:
                    break
                if row and row[0]:
                    urls_to_process.append((row[0], row[1] if len(row) > 1 else ""))
    except Exception as e:
        logger.error(f"Error reading CSV file {csv_path}: {e}")
        urls_to_process = []
    
    if not urls_to_process:
        logger.warning("No URLs to process!")
        return ""
    
    # Process URLs in parallel but maintain order
    all_text = []
    current_length = 0
    
    # Use ThreadPoolExecutor for concurrent processing
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        # Submit all tasks but keep track of their order
        future_to_url = {
            executor.submit(process_url, url_info, source_char_limit): i 
            for i, url_info in enumerate(urls_to_process)
        }
        
        # Process results in order of submission
        results = [None] * len(urls_to_process)
        
        # As each future completes (in any order)
        for future in concurrent.futures.as_completed(future_to_url):
            idx = future_to_url[future]
            try:
                result = future.result()
                if result:  # Skip None results (errors or Google domains)
                    results[idx] = result
            except Exception as e:
                logger.error(f"Error processing URL at index {idx}: {e}")
        
        # Compile final text in correct order
        for result in results:
            if result and current_length < char_limit:
                source_info, content = result
                
                # Add source info
                all_text.append(source_info)
                current_length += len(source_info) + 1  # +1 for newline
                
                # Add content
                content_to_add = content[:char_limit - current_length]
                if content_to_add:
                    all_text.append(content_to_add)
                    current_length += len(content_to_add) + 1  # +1 for newline
                
                if current_length >= char_limit:
                    logger.info(f"Reached character limit of {char_limit}. Stopping.")
                    break
    
    # Combine all text and ensure we're within char_limit
    combined_text = "\n".join(all_text)
    limited_text = combined_text[:char_limit]
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(output_txt_path) if os.path.dirname(output_txt_path) else ".", exist_ok=True)
    
    # Write to output file
    with open(output_txt_path, 'w', encoding='utf-8') as out_file:
        out_file.write(limited_text)
    
    # Log the results
    source_count = len([t for t in all_text if t.startswith("Source:")])
    logger.info(f"Scraped content from {source_count} valid sources and saved to {output_txt_path}")
    logger.info(f"Content length: {len(limited_text)} chars (limited to {char_limit})")
    
    return limited_text

# Module can be run independently
if __name__ == "__main__":
    # Setup basic logging for standalone use
    logging.basicConfig(level=logging.INFO, 
                       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Create argument parser
    parser = argparse.ArgumentParser(description="Scrape content from URLs in CSV")
    parser.add_argument("--csv", "-c", required=True, help="Path to CSV file with URLs")
    parser.add_argument("--output", "-o", help="Output text file path")
    parser.add_argument("--max-urls", "-m", type=int, help=f"Maximum URLs to scrape (default: {Config.MAX_URLS_TO_SCRAPE})")
    parser.add_argument("--char-limit", "-l", type=int, help=f"Character limit for output (default: {Config.MAX_CHARACTERS_IN_SUMMARY})")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Create output path if not provided
    if not args.output:
        # Make sure directory exists
        os.makedirs(Config.TXT_DIR, exist_ok=True)
        # Create output path
        args.output = f"{Config.TXT_DIR}/content_{os.path.basename(args.csv).replace('.csv', '.txt')}"
    
    # Run scraper
    logger.info(f"Scraping content from URLs in {args.csv}")
    content = scrape_first_urls(args.csv, args.output, args.max_urls, args.char_limit)
    
    logger.info(f"Scraping complete. Content saved to {args.output}")