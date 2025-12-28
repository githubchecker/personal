import os
import sys
import time
import json
import requests
import traceback
import re
from typing import List, Dict
from notion_client import Client, APIResponseError
from markdown_it import MarkdownIt

# --- Helper ---
def get_input(prompt_text):
    return input(prompt_text).strip()

# ==========================================
# 1. OFFICIAL UPLOADER (Rich Text, Tables, Alerts)
# ==========================================
def run_official_uploader():
    print("\n--- Notion Official Markdown Uploader (Advanced) ---")
    NOTION_TOKEN = get_input("Enter your Notion Integration Token (starts with 'ntn_'): ")
    PARENT_PAGE_ID = get_input("Enter the Parent Page ID: ")
    LOCAL_DIR = get_input("Enter the Local Directory Path to upload: ")

    if not os.path.exists(LOCAL_DIR):
        print("Directory not found.")
        return

    # Initialize Client
    try:
        notion = Client(auth=NOTION_TOKEN)
        md = MarkdownIt("gfm-like", {'linkify': False})
    except Exception as e:
        print(f"Error initializing client: {e}")
        return

    # --- Internal Helper Functions (Scoped) ---
    def build_rich_text(inline_tokens):
        rich_text = []
        current_annotations = {"bold": False, "italic": False, "strikethrough": False, "underline": False, "code": False, "color": "default"}
        current_link = None
        
        for token in inline_tokens:
            if token.type == "text":
                rich_text.append({"type": "text", "text": {"content": token.content, "link": {"url": current_link} if current_link else None}, "annotations": current_annotations.copy()})
            elif token.type == "code_inline":
                rich_text.append({"type": "text", "text": {"content": token.content}, "annotations": {"bold": False, "italic": False, "strikethrough": False, "underline": False, "code": True, "color": "red"}})
            elif token.type == "strong_open": current_annotations["bold"] = True
            elif token.type == "strong_close": current_annotations["bold"] = False
            elif token.type == "em_open": current_annotations["italic"] = True
            elif token.type == "em_close": current_annotations["italic"] = False
            elif token.type == "s_open": current_annotations["strikethrough"] = True
            elif token.type == "s_close": current_annotations["strikethrough"] = False
            elif token.type == "link_open": current_link = token.attrGet("href")
            elif token.type == "link_close": current_link = None
        return rich_text

    def parse_md_to_notion_blocks(content):
        try:
            tokens = md.parse(content)
            blocks = []
            i = 0
            while i < len(tokens):
                token = tokens[i]
                
                if token.type == "heading_open":
                    level = min(int(token.tag[1]), 3)
                    if i + 1 < len(tokens) and tokens[i+1].type == "inline":
                        rich_text = build_rich_text(tokens[i+1].children)
                        blocks.append({"object": "block", "type": f"heading_{level}", f"heading_{level}": {"rich_text": rich_text}})
                    i += 3
                
                elif token.type == "paragraph_open":
                    if i + 1 < len(tokens) and tokens[i+1].type == "inline":
                        inline = tokens[i+1]
                        if inline.content and inline.content.strip():
                            rich_text = build_rich_text(inline.children)
                            blocks.append({"object": "block", "type": "paragraph", "paragraph": {"rich_text": rich_text}})
                    i += 3

                elif token.type == "bullet_list_open": i+=1; continue
                elif token.type == "list_item_open":
                    found_text = False
                    skip = 1
                    for j in range(i+1, len(tokens)):
                        if tokens[j].type == "list_item_close": skip = j-i+1; break
                        if not found_text and tokens[j].type == "inline":
                             rich_text = build_rich_text(tokens[j].children)
                             blocks.append({"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": rich_text}})
                             found_text=True
                    i+=skip
                
                elif token.type == "blockquote_open":
                    found_text = False; skip = 1
                    for j in range(i+1, len(tokens)):
                        if tokens[j].type == "blockquote_close": skip=j-i+1; break
                        if not found_text and tokens[j].type == "inline":
                            raw = tokens[j].content
                            # Alert Logic
                            callout_type = None; emoji="💡"; color="gray_background"
                            if "[!NOTE]" in raw: callout_type="NOTE"; emoji="ℹ️"; color="blue_background"
                            elif "[!TIP]" in raw: callout_type="TIP"; emoji="💡"; color="green_background"
                            elif "[!IMPORTANT]" in raw: callout_type="IMPORTANT"; emoji="🔥"; color="purple_background"
                            elif "[!WARNING]" in raw: callout_type="WARNING"; emoji="⚠️"; color="orange_background"
                            elif "[!CAUTION]" in raw: callout_type="CAUTION"; emoji="🛑"; color="red_background"
                            
                            if callout_type:
                                tag = f"[!{callout_type}]"
                                # Strip tag from children for Rich Text
                                for child in tokens[j].children:
                                    if child.type == 'text' and tag in child.content:
                                        child.content = child.content.replace(tag, "").strip()
                                
                                rich_text = build_rich_text(tokens[j].children)
                                blocks.append({"object": "block", "type": "callout", "callout": {"rich_text": rich_text, "icon": {"emoji": emoji}, "color": color}})
                            else:
                                rich_text = build_rich_text(tokens[j].children)
                                blocks.append({"object": "block", "type": "quote", "quote": {"rich_text": rich_text}})
                            found_text = True
                    i+=skip

                elif token.type == "table_open":
                    rows = []
                    end_idx = i
                    for k in range(i+1, len(tokens)):
                         if tokens[k].type == "table_close": end_idx=k; break
                    for k in range(i+1, end_idx):
                        t = tokens[k]
                        if t.type == "tr_open": current_row = []
                        elif t.type == "tr_close": rows.append(current_row)
                        elif t.type in ["th_open", "td_open"]:
                             if k+1 < len(tokens) and tokens[k+1].type == "inline":
                                 current_row.append(build_rich_text(tokens[k+1].children))
                    if rows:
                         blocks.append({"object": "block", "type": "table", "table": {"table_width": max(len(r) for r in rows), "has_column_header": True, "has_row_header": False, "children": [{"type": "table_row", "table_row": {"cells": r}} for r in rows]}})
                    i = end_idx + 1

                elif token.type == "fence" or token.type == "code_block":
                    lang = "plain text"
                    if token.type == "fence" and token.info:
                        lang = token.info.split()[0].lower()
                    
                    code = token.content
                    
                    # Language Map
                    valid_langs = {"abap", "agda", "arduino", "assembly", "bash", "basic", "bnf", "c", "c#", "c++", "clojure", "coffeescript", "coq", "css", "dart", "dhall", "diff", "docker", "ebnf", "elixir", "elm", "erlang", "f#", "flow", "fortran", "gherkin", "glsl", "go", "graphql", "groovy", "haskell", "hcl", "html", "idris", "java", "javascript", "json", "julia", "kotlin", "latex", "less", "lisp", "livescript", "llvm ir", "lua", "makefile", "markdown", "markup", "matlab", "mathematica", "mermaid", "nix", "notion formula", "objective-c", "ocaml", "pascal", "perl", "php", "plain text", "powershell", "prolog", "protobuf", "purescript", "python", "r", "racket", "reason", "ruby", "rust", "sass", "scala", "scheme", "scss", "shell", "smalltalk", "solidity", "sql", "swift", "toml", "typescript", "vb.net", "verilog", "vhdl", "visual basic", "webassembly", "xml", "yaml", "java/c/c++/c#"}
                    alias_map = {
                        "dotnetcli": "shell", "console": "shell", "log": "shell", "output": "shell", 
                        "t4": "c#", "tsql": "sql", "mssql": "sql", "plsql": "sql", 
                        "powershell": "powershell", "cs": "c#", "csharp": "c#",
                        "js": "javascript", "ts": "typescript", "py": "python",
                        "xml": "xml", "json": "json", "html": "html", "css": "css",
                        "bash": "bash", "sh": "bash", "zsh": "bash"
                    }
                    
                    clean_lang = alias_map.get(lang, lang)
                    if clean_lang not in valid_langs: clean_lang = "plain text"

                    blocks.append({"object": "block", "type": "code", "code": {"rich_text": [{"type": "text", "text": {"content": code[:2000]}}], "language": clean_lang}})
                    i+=1
                
                elif token.type == "inline":
                     for child in token.children:
                         if child.type == "image":
                             url = child.attrGet("src")
                             if url: blocks.append({"object": "block", "type": "image", "image": {"type": "external", "external": {"url": url}}})
                     i+=1
                else:
                    i+=1
            return blocks[:100]
        except Exception:
            return []

    def create_page(title, parent_id, content=""):
        payload = {"parent": {"page_id": parent_id}, "properties": {"title": {"title": [{"text": {"content": title}}]}}}
        if content:
             blocks = parse_md_to_notion_blocks(content)
             if blocks: payload["children"] = blocks
        try:
            return notion.pages.create(**payload)["id"]
        except Exception as e:
            print(f"Error creating '{title}': {e}")
            return None

    def upload_recursive(path, parent_id, level=0):
        indent = "  " * level
        
        def natural_sort_key(s):
            return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]

        for item in sorted(os.listdir(path), key=natural_sort_key):
            full_path = os.path.join(path, item)
            if os.path.isdir(full_path):
                print(f"{indent}[Folder] {item}")
                pid = create_page(item, parent_id)
                if pid: upload_recursive(full_path, pid, level+1)
            elif item.endswith(".md"):
                print(f"{indent}[File]   {item}")
                with open(full_path, "r", encoding="utf-8") as f: content = f.read()
                create_page(item[:-3], parent_id, content)

    print(f"Starting Upload to {PARENT_PAGE_ID}...")
    upload_recursive(LOCAL_DIR, PARENT_PAGE_ID)
    print("Done.")

# ==========================================
# 2. TEAMSPACE CLEANUP TOOL
# ==========================================
def run_cleanup():
    print("\n--- Teamspace Cleanup Tool ---")
    SECRET = get_input("Enter Notion Secret: ")
    HEADERS = {"Authorization": f"Bearer {SECRET}", "Content-Type": "application/json", "Notion-Version": "2022-06-28"}

    def fetch_all():
        url = "https://api.notion.com/v1/search"
        results = []
        has_more = True
        cursor = None
        while has_more:
             pl = {"page_size": 100}
             if cursor: pl["start_cursor"] = cursor
             r = requests.post(url, json=pl, headers=HEADERS)
             if r.status_code != 200: print("Error fetching"); return []
             d = r.json()
             results.extend(d.get("results", []))
             has_more = d.get("has_more")
             cursor = d.get("next_cursor")
        return results

    print("Fetching items...")
    items = fetch_all()
    print(f"Found {len(items)} total items.")
    
    for i, item in enumerate(items):
        t = "Untitled"
        if item["object"] == "page": 
             p = item.get("properties", {}).get("title", {}).get("title", [])
             if p: t = p[0].get("plain_text", "Untitled")
        print(f"{i+1}. {item['object']} - {t} ({item['id']})")
    
    sel = get_input("Enter indices to DELETE (comma separated) or 'ALL': ")
    to_delete = []
    if sel.upper() == "ALL":
         to_delete = items
    else:
         try:
             idxs = [int(x)-1 for x in sel.split(",")]
             to_delete = [items[i] for i in idxs if 0 <= i < len(items)]
         except:
             print("Invalid input")
             return

    if not to_delete: return
    
    conf = get_input(f"Deleting {len(to_delete)} items. Type DELETE to confirm: ")
    if conf == "DELETE":
         for it in to_delete:
             print(f"Archiving {it['id']}...")
             requests.patch(f"https://api.notion.com/v1/{it['object']}s/{it['id']}", json={"archived": True}, headers=HEADERS)
         print("Done.")
    else:
         print("Cancelled.")

# ==========================================
# 3. SCAN TAGS
# ==========================================
def run_tag_extraction():
    print("\n--- Markdown Tag Extraction ---")
    root_dir = get_input("Enter directory to scan: ")
    if not os.path.exists(root_dir):
        print("Invalid directory.")
        return

    tags = set()
    print(f"Scanning {root_dir}...")
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith(".md"):
                try:
                    with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                        for line in f:
                            match = re.search(r"^\s*```([a-zA-Z0-9#\+\-]+)", line)
                            if match:
                                tags.add(match.group(1).lower())
                except Exception:
                    pass
    
    print("\nUnique Language Tags Found:")
    print("-" * 30)
    for t in sorted(tags):
        print(t)
    print("-" * 30)

# ==========================================
# MAIN MENU
# ==========================================
def main():
    while True:
        print("\n=== UNIFIED NOTION MANAGER ===")
        print("1. Official Uploader (Rich Text, Tables, Alerts)")
        print("2. Teamspace Cleanup Tool")
        print("3. Scan Markdown Tags")
        print("4. Exit")
        
        choice = get_input("Select an option (1-4): ")
        
        if choice == "1":
            try: run_official_uploader()
            except Exception as e: print(f"Crash: {e}")
        elif choice == "2":
            try: run_cleanup()
            except Exception as e: print(f"Crash: {e}")
        elif choice == "3":
            try: run_tag_extraction()
            except Exception as e: print(f"Crash: {e}")
        elif choice == "4":
            print("Exiting.")
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()
