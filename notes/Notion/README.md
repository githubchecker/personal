# Scraping & Uploading Scripts

This folder contains the complete toolchain for scraping documentation sites (like Microsoft Learn) and uploading them to Notion.

## 1. The Manager (`unified_notion_manager.py`)
**"The One Script"** for all Notion operations.
Run this to access:
1.  **Official Uploader**: Upload with rich text, tables, alerts.
2.  **Teamspace Cleanup**: Bulk archive/delete pages.
3.  **Tag Scanner**: Extract code block languages for config.

**Usage:**
```bash
python unified_notion_manager.py
```
*(Follow the interactive menu)*

---

## 2. The Scraper (`final_web_scraper.py`)
This is the **Master Script** for scraping. It merges all previous logic.

**Features:**
- Recursive crawling based on an input HTML list.
- **Microsof Learn Optimized**: Handles Tabs, Notes/Tips/Warnings, and Tables perfectly.
- **GitHub Alerts**: Converts `div.note` to `> [!NOTE]`.
- **Images**: Fixes lazy-loaded images.
- **Tables**: Converts HTML tables to Markdown tables.

**Usage:**
1.  Create a file named **`toc.html`** in this directory.
    -   Paste the `<ul>` list from the sidebar of the documentation site you want to scrape.
2.  Run the script:
    ```bash
    python final_web_scraper.py
    ```
3.  Output will be saved to `Scraped_Docs/`.

---

## 2. The Uploader (`notion_official_uploader.py`)
Uploads the `Scraped_Docs` (or any Markdown folder) to Notion.

**Usage:**
```bash
python notion_official_uploader.py
```
- Enter your **Parent Page ID** when prompted.
- Enter the path to `Scraped_Docs`.

---

### Other Scripts
- `scan_tags.py`: Helper to find code block languages.
- `notion_teamspace_cleanup.py`: Helper to empty Notion pages.
