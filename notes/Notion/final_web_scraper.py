
import os
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re
from markdownify import MarkdownConverter

# Headers to mimic a browser
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

class CustomConverter(MarkdownConverter):
    """
    Custom Markdownify Converter for MS Learn specifics.
    """
    def __init__(self, base_url, **kwargs):
        super().__init__(**kwargs)
        self.base_url = base_url

    def convert_a(self, el, text, convert_as_inline=False, **kwargs):
        href = el.get('href')
        if href and not href.startswith('http'):
            href = urljoin(self.base_url, href)
        if not text: text = href
        return f"[{text}]({href})" if href else text

    def convert_img(self, el, text, convert_as_inline=False, **kwargs):
        src = el.get('src') or el.get('data-src') or el.get('data-original')
        alt = el.get('alt', '')
        if src and not src.startswith('http'):
            src = urljoin(self.base_url, src)
        return f"![{alt}]({src})" if src else ""

    def convert_pre(self, el, text, convert_as_inline=False, **kwargs):
        code = el.find('code')
        language = ""
        if code:
            # Extract language from class (e.g. lang-csharp)
            classes = code.get('class', [])
            for c in classes:
                if c.startswith('lang-'):
                    language = c.replace('lang-', '')
            # Heuristic SQL
            if not language and self._is_sql(code.get_text()):
                language = 'sql'
            
            raw_text = code.get_text()
        else:
            raw_text = el.get_text()
            
        return f"\n\n```{language}\n{raw_text.strip()}\n```\n\n"

    def convert_code(self, el, text, convert_as_inline=False, **kwargs):
        return f" `{text}` " if text else ""

    def convert_strong(self, el, text, convert_as_inline=False, **kwargs):
        return f"**{text}**" if text else ""

    def convert_b(self, el, text, convert_as_inline=False, **kwargs):
        return f"**{text}**" if text else ""

    def convert_em(self, el, text, convert_as_inline=False, **kwargs):
        return f"*{text}*" if text else ""

    def convert_i(self, el, text, convert_as_inline=False, **kwargs):
        return f"*{text}*" if text else ""

    def convert_div(self, el, text, convert_as_inline=False, **kwargs):
        # Handle Alerts
        classes = [c.upper() for c in el.get('class', [])]
        alert_type = None
        if 'NOTE' in classes or 'ALERT-INFO' in classes: alert_type = 'NOTE'
        elif 'TIP' in classes or 'ALERT-SUCCESS' in classes: alert_type = 'TIP'
        elif 'IMPORTANT' in classes: alert_type = 'IMPORTANT'
        elif 'WARNING' in classes or 'ALERT-WARNING' in classes: alert_type = 'WARNING'
        elif 'CAUTION' in classes: alert_type = 'CAUTION'

        if alert_type:
            # Strip "Note" prefix if present in text
            # Note: 'text' passed here is already converted markdown of children.
            # We need raw text to check prefix? 
            # Actually, `text` is the inner content.
            # MS Learn alerts usually have the type as the first word.
            clean_text = text.strip()
            # Simple check: if it starts with the alert type (case insensitive)
            if clean_text.upper().startswith(alert_type):
                clean_text = clean_text[len(alert_type):].strip()
            
            # Format as blockquote with alert syntax
            lines = clean_text.splitlines()
            quoted_lines = [f"> {line}" for line in lines]
            return f"\n> [!{alert_type}]\n" + "\n".join(quoted_lines) + "\n\n"
        
        # Default recursive usage for other divs (unwrap)
        return text

    def _is_sql(self, text):
        keywords = ["SELECT", "INSERT", "UPDATE", "DELETE", "FROM", "WHERE", "JOIN"]
        count = sum(1 for k in keywords if k in text.upper())
        return count >= 2


class BaseScraper:
    def __init__(self, base_url):
        self.base_url = base_url

    def fetch_html(self, url):
        try:
            print(f"    Fetching: {url}")
            response = requests.get(url, headers=HEADERS, timeout=15)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"    Error fetching {url}: {e}")
            return None

    def extract_main_content(self, soup):
        # Specific MS Learn attribute (User Suggested)
        content_div = soup.find(attrs={"data-main-column": True})
        
        if not content_div:
            content_div = soup.find('div', class_='entry-content')
        
        if not content_div:
            content_div = (soup.find('main') or 
                           soup.find('article') or 
                           soup.find('div', attrs={'id': 'content'}))
        return content_div or soup.body

    def html_to_markdown(self, soup):
        # Use markdownify with custom converter
        # heading_style='ATX' -> # Header
        converter = CustomConverter(base_url=self.base_url, heading_style='ATX')
        return converter.convert_soup(soup)


class MicrosoftLearnScraper(BaseScraper):
    def preprocess_html(self, soup, url):
        # 1. Global Moniker Filter
        if 'view=' in url:
            try:
                target_version = url.split('view=')[1].split('&')[0]
                # Safe Iteration
                for tag in list(soup.find_all(attrs={"data-moniker": True})):
                     if tag.attrs is None or not tag.has_attr('data-moniker'): continue
                     monikers = tag['data-moniker'].split()
                     if target_version not in monikers:
                         tag.decompose()
            except IndexError:
                pass

        # 2. Cleanup
        selectors = [
             '.page-metadata-container', '.doc-outline', '#action-panel', 
             '.feedback-section', '.page-actions', 'bread-crumbs', 
             '#article-header', '.display-none-print', 'script', 'style', 'footer', 'nav',
             # New aggressive filters
             '.toc', '.toc-container', 'button.toc-button', 
             '.edit-mode-alert', '.authorization-alert', '.azure-study-group-notification'
        ]
        for sel in selectors:
            for tag in soup.select(sel):
                tag.decompose()

        # 2a. Text-Based Removal (Stubborn artifacts)
        # Remove elements that are just "Table of contents" or "Exit editor mode"
        # We iterate over all divs and navs to check their direct text match
        text_targets = ["Table of contents", "Exit editor mode", "Summarize this article for me"]
        for tag in soup.find_all(['div', 'nav', 'button', 'span']):
            if tag.get_text(strip=True) in text_targets:
                tag.decompose()
        
        # Remove specific warning block (text processing)
        # "Access to this page requires authorization" is usually in a div with a link
        for div in soup.find_all('div'):
             txt = div.get_text(strip=True)
             if "Access to this page requires authorization" in txt and len(txt) < 300:
                 div.decompose()

        # 3. Tab Groups -> Unwrap
        for tg in soup.find_all('div', class_='tabGroup'):
            tg.unwrap()

    def postprocess_markdown(self, text):
        # Footer Truncation
        markers = ["In the next article,", "## Additional resources", "## See also"]
        for marker in markers:
            if marker in text:
                text = text.split(marker)[0].strip()
        
        # Intro Cleanup
        lines = text.splitlines()
        while lines and not lines[0].strip(): lines.pop(0)
        
        cleaned_lines = []
        for line in lines:
             if line.strip() in ["Back to top", "On this page"]: continue
             cleaned_lines.append(line)
        
        return "\n".join(cleaned_lines)

    def scrape(self, url):
        html = self.fetch_html(url)
        if not html: return f"# Error\nFailed to fetch {url}"
        
        soup = BeautifulSoup(html, 'html.parser')
        main_soup = self.extract_main_content(soup)
        self.preprocess_html(main_soup, url)
        md = self.html_to_markdown(main_soup)
        md = self.postprocess_markdown(md)
        return md

# --- Orchestration ---

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_TOC_FILE = os.path.join(SCRIPT_DIR, "toc.html")
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "Scraped_Docs")
BASE_URL = "https://learn.microsoft.com/en-us/aspnet/core/"

def clean_filename(text):
    text = re.sub(r'[\\/*?:"<>|]', "", text)
    # Robust whitespace normalization
    text = " ".join(text.split())
    return text.strip() or "Untitled"

def process_toc_recursive(element, current_path, index=None):
    if element.name == 'ul':
        for i, li in enumerate(element.find_all('li', recursive=False), 1):
            process_toc_recursive(li, current_path, index=i)
    
    elif element.name == 'li':
        link = element.find('a', recursive=False)
        nested_ul = element.find('ul', recursive=False)
        item_name = "Untitled"
        target_url = None
        
        if link:
            item_name = clean_filename(link.get_text(strip=True))
            if link.get('href'):
                target_url = urljoin(BASE_URL, link['href'])
        
        if item_name == "Untitled":
             for s in element.stripped_strings:
                 item_name = clean_filename(s)
                 break
        
        if index is not None:
            item_name = f"{index}. {item_name}"

        # Folder or File?
        if nested_ul:
            new_dir = os.path.join(current_path, item_name)
            os.makedirs(new_dir, exist_ok=True)
            if target_url:
                scraper = MicrosoftLearnScraper(BASE_URL)
                md = scraper.scrape(target_url)
                with open(os.path.join(current_path, f"{item_name}.md"), "w", encoding="utf-8") as f:
                    f.write(md)
            process_toc_recursive(nested_ul, new_dir)
        elif target_url:
            scraper = MicrosoftLearnScraper(BASE_URL)
            md = scraper.scrape(target_url)
            with open(os.path.join(current_path, f"{item_name}.md"), "w", encoding="utf-8") as f:
                f.write(md)
            time.sleep(0.5)

def main():
    if not os.path.exists(INPUT_TOC_FILE):
        print(f"Error: {INPUT_TOC_FILE} not found.")
        return

    print("Starting Modular Web Scraper (Markdownify)...")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(INPUT_TOC_FILE, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
    
    root = soup.find('ul')
    if root:
        process_toc_recursive(root, OUTPUT_DIR)
        print("Done.")
    else:
        print("No root UL found.")

if __name__ == "__main__":
    main()
