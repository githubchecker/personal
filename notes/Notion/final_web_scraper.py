import os
import requests
from bs4 import BeautifulSoup
import re
import time
import urllib.parse
from urllib.parse import urljoin

# --- Configuration ---
INPUT_TOC_FILE = "toc.html"
OUTPUT_DIR = "Scraped_Docs"
# Optional: Set this if links in TOC are relative
BASE_URL = "https://learn.microsoft.com" 

# Headers to mimic a browser
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

def clean_filename(name):
    """Sanitizes strings to be safe for filenames."""
    cleaned = re.sub(r'[\\/*?:"<>|]', "", name)
    cleaned = "".join(ch for ch in cleaned if ord(ch) >= 32)
    cleaned = re.sub(r'\s+', ' ', cleaned)
    return cleaned.strip() or "Untitled"

def is_sql(content):
    """Heuristic to check if content is SQL."""
    keywords = [
        r'\bCREATE\s+DATABASE\b', r'\bCREATE\s+TABLE\b', r'\bINSERT\s+INTO\b',
        r'\bSELECT\s+.*?\s+FROM\b', r'\bUPDATE\s+.*?\s+SET\b', r'\bDELETE\s+FROM\b',
        r'\bUSE\s+\[?\w+\]?', r'\bGO\s*$', r'\bNVARCHAR\b', r'\bPRIMARY\s+KEY\b'
    ]
    content_upper = content.upper()
    if "namespace " in content and "class " in content: return False # C# false positive check
    
    match_count = 0
    for pattern in keywords:
        if re.search(pattern, content_upper, re.MULTILINE):
            match_count += 1
            if match_count >= 2: return True
    return False

def clean_intro_text(content):
    """
    Cleans up tutorial introductions:
    - Removes 'Back to' links.
    - Removes redundant agenda lists (1. ... 2. ...) before the first real header.
    - Removes dangling phrases like 'discuss the following points:'.
    """
    lines = content.splitlines()
    new_lines = []
    header_found = False
    
    hanging_phrases = [
        "discuss the following pointers", "discuss the following points",
        "discuss the following topics", "discuss the following concepts"
    ]

    for line in lines:
        stripped = line.strip()
        
        # 1. Remove "Back to:" link
        if not header_found and stripped.startswith("Back to") and "asp-net-core-tutorials" in stripped.lower():
            continue
            
        # Stop intro processing if we hit a Header (H1 or H2)
        if stripped.startswith("#"):
            header_found = True
            
        # 2. Remove Numbered List (Agenda) before first header
        # Regex: Start of line, number, dot, space.
        if not header_found and re.match(r'^\d+\.\s.*', stripped):
            continue
        
        # 3. Remove Hanging Phrases in Intro
        if not header_found:
            for phrase in hanging_phrases:
                if phrase in line:
                    # Replace specific connective variations
                    line = line.replace(" and " + phrase, ".")
                    line = line.replace(", " + phrase, ".")
                    line = line.replace(" " + phrase, ".")
                    line = line.replace(phrase, "")
                    # Clean up trailing punctuation/colons if left
                    line = re.sub(r'[:\.]+\s*$', '.', line)

        new_lines.append(line)
        
    return "\n".join(new_lines)

def html_to_markdown_custom(html_content, base_url, default_lang=''):
    """
    Custom HTML to Markdown converter from doc_manager.py
    optimized for MS Learn and Technical Docs.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 1. Handle Images (Lazy Loading support)
    for img in soup.find_all('img'):
        if not img.parent: continue
        src = img.get('data-src') or img.get('data-original') or img.get('src')
        alt = img.get('alt', 'Image')
        if src:
            if not src.startswith('http'):
                src = urljoin(base_url, src)
            img.replace_with(f"![{alt}]({src})")

    # 2. MS Learn Tab Groups (Convert to Header Sections)
    for tab_group in soup.find_all('div', class_='tabGroup'):
        if not tab_group.parent: continue
        tab_group.unwrap()

    # 3. Links
    for a in soup.find_all('a'):
        if not a.parent: continue
        href = a.get('href', '')
        text = a.get_text(strip=True)
        if href:
            if not href.startswith('http'):
                href = urljoin(base_url, href)
            a.replace_with(f"[{text}]({href})")

    # 4. Code Blocks (Preserve Language + SQL Detection)
    for pre in soup.find_all('pre'):
        if not pre.parent: continue
        code = pre.find('code')
        lang = default_lang
        if code and code.has_attr('class'):
            for c in code['class']:
                if c.startswith('lang-'):
                    lang = c.replace('lang-', '')
        
        text = code.get_text() if code else pre.get_text()
        
        # Heuristic SQL Detection
        if (not lang or lang == 'plain') and is_sql(text):
            lang = 'sql'

        new_text = f"\n\n```{lang}\n{text.strip()}\n```\n\n"
        pre.replace_with(new_text)

    # 5. Headers (H1-H6)
    for i in range(1, 7):
        for h in soup.find_all(f'h{i}'):
            if not h.parent: continue
            prefix = '#' * i
            h.replace_with(f"\n\n{prefix} {h.get_text(strip=True)}\n\n")

    # 6. Alerts (Note, Tip, Warning) -> GitHub Alert Syntax
    for div in soup.find_all('div'):
        if not div.parent: continue
        classes = [c.upper() for c in div.get('class', [])]
        alert_type = None
        if 'NOTE' in classes: alert_type = 'NOTE'
        elif 'TIP' in classes: alert_type = 'TIP'
        elif 'IMPORTANT' in classes: alert_type = 'IMPORTANT'
        elif 'WARNING' in classes: alert_type = 'WARNING'
        elif 'CAUTION' in classes: alert_type = 'CAUTION'
        
        if alert_type:
            content = div.get_text(separator=' ', strip=True)
            div.replace_with(f"\n> [!{alert_type}]\n> {content}\n")

    # 7. Tables (Basic Markdown Table generation)
    for table in soup.find_all('table'):
        if not table.parent: continue
        rows = []
        headers = []
        
        # Extract headers
        thead = table.find('thead')
        if thead:
            headers = [th.get_text(strip=True) for th in thead.find_all('th')]
        
        # Extract rows
        tbody = table.find('tbody') or table
        for tr in tbody.find_all('tr'):
            cells = [td.get_text(strip=True) for td in tr.find_all(['td', 'th'])]
            if cells:
                rows.append(cells)
        
        # If no headers found but rows exist, use empty headers
        if not headers and rows:
             headers = [""] * len(rows[0])

        if headers:
            md_table = "\n\n| " + " | ".join(headers) + " |\n"
            md_table += "| " + " | ".join(["---"] * len(headers)) + " |\n"
            for row in rows:
                while len(row) < len(headers): row.append("")
                md_table += "| " + " | ".join(row) + " |\n"
            table.replace_with(md_table)

    # 8. Lists (Bold Keys Logic)
    for li in soup.find_all('li'):
         if not li.parent: continue
         content = li.get_text(strip=True)
         
         # Bold "Key: Value" pattern
         if ':' in content and not content.startswith('**'):
             parts = content.split(':', 1)
             key = parts[0].strip()
             val = parts[1].strip()
             # Heuristic: keys usually aren't super long sentences
             if len(key) < 50: 
                 content = f"**{key}:** {val}"
         
         li.replace_with(f"* {content}\n")

    final_text = soup.get_text().strip()
    
    # 9. Clean Intro (Back to, Agenda lists, Dangling phrases)
    final_text = clean_intro_text(final_text)

    # 10. Footer Truncation
    marker = "In the next article,"
    if marker in final_text:
        final_text = final_text.split(marker)[0].strip()

    return final_text

def fetch_and_convert(url):
    """Fetches URL and converts main content to Markdown."""
    try:
        print(f"    Fetching: {url}")
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Smart Content Detection (Merged from doc_manager.py)
        content_div = None
        
        # 1. Try WordPress/DotNetTutorials style
        content_div = soup.find('div', class_='entry-content')
        
        # 2. Try MS Learn aggregated content
        if not content_div:
            content_nodes = soup.find_all('div', class_='content')
            if content_nodes:
                 content_div = soup.new_tag("div")
                 for node in content_nodes: content_div.append(node)
        
        # 3. Fallback generic
        if not content_div:
            content_div = (soup.find('main') or 
                           soup.find('article') or 
                           soup.find('div', attrs={'id': 'content'}))

        if not content_div:
            print("    Warning: No main content found. Using body.")
            content_div = soup.body

        # Cleanup Junk
        selectors_to_remove = [
            '.page-metadata-container', '.doc-outline', '#action-panel', 
            '.feedback-section', '.page-actions', 'bread-crumbs', 
            '#article-header', '.display-none-print', 'script', 'style', 'footer', 'nav'
        ]
        for selector in selectors_to_remove:
            for tag in content_div.select(selector):
                tag.decompose()

        # Convert
        return html_to_markdown_custom(str(content_div), url)

    except Exception as e:
        print(f"    Error scraping {url}: {e}")
        return f"# Error\nFailed to fetch {url}\n{e}"

def process_toc_recursive(element, current_path):
    """Recursively processes UL/LI structure."""
    if element.name == 'ul':
        for li in element.find_all('li', recursive=False):
            process_toc_recursive(li, current_path)
    
    elif element.name == 'li':
        link = element.find('a', recursive=False)
        nested_ul = element.find('ul', recursive=False)
        
        item_name = "Untitled"
        target_url = None
        
        if link:
            item_name = clean_filename(link.get_text())
            href = link.get('href')
            if href:
                target_url = urljoin(BASE_URL, href)
        else:
             text = element.find(string=True, recursive=False)
             if text: item_name = clean_filename(text)

        # Folder Logic
        if nested_ul:
            new_dir = os.path.join(current_path, item_name)
            os.makedirs(new_dir, exist_ok=True)
            
            # If folder has content, save as {Folder}.md inside
            if target_url:
                md_content = fetch_and_convert(target_url)
                with open(os.path.join(current_path, f"{item_name}.md"), "w", encoding="utf-8") as f:
                    f.write(md_content)
            
            process_toc_recursive(nested_ul, new_dir)
        
        # File Logic
        elif target_url:
            md_content = fetch_and_convert(target_url)
            with open(os.path.join(current_path, f"{item_name}.md"), "w", encoding="utf-8") as f:
                f.write(md_content)
            time.sleep(0.5)

def main():
    if not os.path.exists(INPUT_TOC_FILE):
        print(f"Error: {INPUT_TOC_FILE} not found. Please create it with your <ul> structure.")
        return

    print(f"Reading {INPUT_TOC_FILE}...")
    with open(INPUT_TOC_FILE, "r", encoding="utf-8") as f:
        html = f.read()

    soup = BeautifulSoup(html, 'html.parser')
    root_ul = soup.find('ul')
    
    if not root_ul:
        print("Error: No root <ul> found.")
        return

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    print("Starting Final Web Scraper...")
    process_toc_recursive(root_ul, OUTPUT_DIR)
    print("\nDone! Content saved in:", OUTPUT_DIR)

if __name__ == "__main__":
    main()
