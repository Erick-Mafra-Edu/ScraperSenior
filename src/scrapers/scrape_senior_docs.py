#!/usr/bin/env python3
"""
Web scraper for documentacao.senior.com.br
Extracts all articles and content for indexing in Meilisearch.
Uses Playwright for JavaScript-rendered content.
"""

import asyncio
import json
import os
import re
import hashlib
from pathlib import Path
from datetime import datetime
from urllib.parse import urljoin, urlparse
from typing import Dict, List, Set, Any
import time

from playwright.async_api import async_playwright, Page, Browser, BrowserContext


class SeniorDocsScraper:
    """Scraper for Senior documentation portal."""
    
    def __init__(self, base_url: str = "https://documentacao.senior.com.br"):
        """Initialize scraper."""
        self.base_url = base_url
        self.docs_folder = Path("documentacao")
        self.docs_folder.mkdir(exist_ok=True)
        
        self.visited_urls: Set[str] = set()
        self.failed_urls: List[str] = []
        self.articles: List[Dict[str, Any]] = []
        self.start_time = datetime.now()
    
    async def scrape_page(self, page: Page, url: str) -> Dict[str, Any]:
        """Scrape a single page and extract article content."""
        print(f"  Scraping: {url}")
        
        try:
            await page.goto(url, wait_until="networkidle", timeout=30000)
            await page.wait_for_timeout(1000)  # Wait for JS to render
            
            # Extract page content
            page_html = await page.content()
            
            # Get title
            title = ""
            try:
                title_elem = await page.query_selector("h1")
                if title_elem:
                    title = await title_elem.text_content()
                    title = title.strip() if title else ""
            except:
                pass
            
            # Get article content
            content = ""
            content_selectors = [
                "article",
                ".article-content",
                ".content",
                "main",
                ".main-content",
                ".documentation-content"
            ]
            
            for selector in content_selectors:
                try:
                    elem = await page.query_selector(selector)
                    if elem:
                        content = await elem.inner_text()
                        if content.strip():
                            break
                except:
                    pass
            
            # If no content found, try to get body
            if not content.strip():
                try:
                    body_elem = await page.query_selector("body")
                    if body_elem:
                        content = await body_elem.inner_text()
                except:
                    pass
            
            # Clean content
            content = re.sub(r'\s+', ' ', content).strip()
            
            # Extract section from breadcrumb or URL
            section = self._extract_section(url)
            
            # Extract all links for crawling
            links = []
            try:
                link_elements = await page.query_selector_all("a[href]")
                for link_elem in link_elements:
                    href = await link_elem.get_attribute("href")
                    if href:
                        links.append(href)
            except:
                pass
            
            return {
                "url": url,
                "title": title or "Untitled",
                "content": content,
                "section": section,
                "links": links,
                "success": True
            }
        
        except Exception as e:
            print(f"    Error: {e}")
            self.failed_urls.append(url)
            return {
                "url": url,
                "success": False,
                "error": str(e)
            }
    
    def _extract_section(self, url: str) -> str:
        """Extract section from URL path."""
        path = urlparse(url).path
        parts = path.strip("/").split("/")
        if len(parts) > 1:
            return parts[0]
        return "General"
    
    def _is_valid_url(self, url: str) -> bool:
        """Check if URL is valid and in scope."""
        if not url or url.startswith("#"):
            return False
        
        # Normalize URL
        url = urljoin(self.base_url, url)
        
        # Check if in domain
        if not url.startswith(self.base_url):
            return False
        
        # Skip downloads and static files
        skip_patterns = [".pdf", ".zip", ".exe", ".jpg", ".png", ".css", ".js", ".woff"]
        if any(url.endswith(pattern) for pattern in skip_patterns):
            return False
        
        return True
    
    def _save_article(self, article: Dict[str, Any]) -> bool:
        """Save article as metadata.json + content.txt."""
        if not article["content"] or len(article["content"]) < 50:
            print(f"    Skipped (too short)")
            return False
        
        # Generate unique ID from URL
        url_hash = hashlib.md5(article["url"].encode()).hexdigest()[:8]
        article_id = f"senior_{url_hash}"
        
        # Create article folder
        article_folder = self.docs_folder / article_id
        article_folder.mkdir(exist_ok=True)
        
        # Save metadata
        metadata = {
            "id": article_id,
            "title": article["title"],
            "url": article["url"],
            "section": article["section"],
            "language": "pt",
            "source": "documentacao.senior.com.br",
            "scraped_at": datetime.now().isoformat(),
            "content_length": len(article["content"])
        }
        
        metadata_file = article_folder / "metadata.json"
        with open(metadata_file, "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        # Save content
        content_file = article_folder / "content.txt"
        with open(content_file, "w", encoding="utf-8") as f:
            f.write(article["content"])
        
        print(f"    Saved: {article_id}")
        return True
    
    async def scrape_recursive(self, page: Page, start_url: str, max_pages: int = 100):
        """Recursively scrape site starting from URL."""
        print(f"\n🕷️  Starting recursive scrape from: {start_url}")
        print(f"Max pages: {max_pages}")
        print("=" * 70)
        
        to_visit = [start_url]
        pages_scraped = 0
        
        while to_visit and pages_scraped < max_pages:
            url = to_visit.pop(0)
            
            if url in self.visited_urls:
                continue
            
            self.visited_urls.add(url)
            
            # Scrape page
            result = await self.scrape_page(page, url)
            
            if result["success"]:
                article = result
                article["scraped_at"] = datetime.now().isoformat()
                self.articles.append(article)
                
                # Save article
                if self._save_article(article):
                    pages_scraped += 1
                
                # Find new links
                for link in result.get("links", []):
                    full_url = urljoin(url, link)
                    if self._is_valid_url(full_url) and full_url not in self.visited_urls:
                        to_visit.append(full_url)
                        print(f"    Found link: {full_url}")
            
            # Rate limiting
            await page.wait_for_timeout(500)
            
            # Progress
            progress = len(self.visited_urls)
            print(f"\n[{progress}/{max_pages}] Pages processed: {progress}, Articles saved: {pages_scraped}")
            print(f"Queue size: {len(to_visit)}")
        
        print("\n" + "=" * 70)
        print(f"✓ Scraping complete!")
        print(f"  Pages visited: {len(self.visited_urls)}")
        print(f"  Articles saved: {pages_scraped}")
        print(f"  Failed URLs: {len(self.failed_urls)}")
        
        if self.failed_urls:
            print("\nFailed URLs:")
            for url in self.failed_urls[:5]:
                print(f"  - {url}")
            if len(self.failed_urls) > 5:
                print(f"  ... and {len(self.failed_urls) - 5} more")
    
    async def scrape_menu_based(self, page: Page, max_pages: int = 100):
        """Scrape by clicking menu items and extracting content."""
        print(f"\n🕷️  Starting menu-based scrape")
        print(f"Max pages: {max_pages}")
        print("=" * 70)
        
        await page.goto(self.base_url, wait_until="networkidle")
        await page.wait_for_timeout(1000)
        
        # Find all navigation links
        print("Looking for navigation links...")
        
        nav_selectors = [
            "nav a",
            ".navigation a",
            ".sidebar a",
            ".menu a",
            ".nav-item a"
        ]
        
        all_links = set()
        for selector in nav_selectors:
            try:
                elements = await page.query_selector_all(selector)
                for elem in elements:
                    href = await elem.get_attribute("href")
                    text = await elem.text_content()
                    if href and self._is_valid_url(href):
                        full_url = urljoin(self.base_url, href)
                        all_links.add(full_url)
                        print(f"  Found: {text.strip() if text else 'Link'} -> {full_url}")
            except:
                pass
        
        print(f"\nTotal links found: {len(all_links)}")
        print("Scraping pages...")
        
        pages_scraped = 0
        for url in list(all_links)[:max_pages]:
            if url in self.visited_urls:
                continue
            
            self.visited_urls.add(url)
            
            # Create new page to avoid state issues
            new_page = await page.context.new_page()
            
            result = await self.scrape_page(new_page, url)
            await new_page.close()
            
            if result["success"]:
                article = result
                article["scraped_at"] = datetime.now().isoformat()
                self.articles.append(article)
                
                if self._save_article(article):
                    pages_scraped += 1
            
            await page.wait_for_timeout(500)
            
            progress = len(self.visited_urls)
            print(f"[{progress}/{len(all_links)}] Articles: {pages_scraped}")
        
        print("\n" + "=" * 70)
        print(f"✓ Scraping complete!")
        print(f"  Pages visited: {len(self.visited_urls)}")
        print(f"  Articles saved: {pages_scraped}")


async def main():
    """Main entry point."""
    # Configuration
    BASE_URL = "https://documentacao.senior.com.br"
    MAX_PAGES = 50  # Limit for safety, increase as needed
    
    print("\n" + "=" * 70)
    print("📚 SENIOR DOCUMENTATION SCRAPER")
    print("=" * 70)
    print(f"Target: {BASE_URL}")
    print(f"Max pages: {MAX_PAGES}")
    print("=" * 70)
    
    scraper = SeniorDocsScraper(BASE_URL)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 720}
        )
        page = await context.new_page()
        
        try:
            # Try menu-based scraping first (more reliable)
            print("\n[1/2] Attempting menu-based scrape...")
            await scraper.scrape_menu_based(page, max_pages=MAX_PAGES)
            
            # If few pages found, try recursive scrape
            if len(scraper.articles) < 5:
                print("\n[2/2] Attempting recursive scrape...")
                await scraper.scrape_recursive(page, BASE_URL, max_pages=MAX_PAGES)
        
        finally:
            await context.close()
            await browser.close()
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 SCRAPING SUMMARY")
    print("=" * 70)
    print(f"Total articles scraped: {len(scraper.articles)}")
    print(f"Saved to folder: {scraper.docs_folder.absolute()}")
    print(f"Time taken: {(datetime.now() - scraper.start_time).total_seconds():.1f}s")
    print("=" * 70)
    
    if scraper.articles:
        print("\n✓ Sample articles:")
        for article in scraper.articles[:3]:
            print(f"  - {article['title']} ({len(article['content'])} chars)")
    
    # Ask to index
    if scraper.articles:
        print("\n" + "=" * 70)
        print("📌 NEXT STEP: Index documents in Meilisearch")
        print("=" * 70)
        print("Run:")
        print("  curl -X POST http://localhost:5000/index")
        print("\nOr from Python:")
        print("  python -c \"from search_engine.meilisearch_client import MeilisearchClient;")
        print("             c = MeilisearchClient(); c.load_from_files('documentacao')\"")
        print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
