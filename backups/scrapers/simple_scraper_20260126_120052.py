#!/usr/bin/env python3
"""
Simple scraper usando requests + BeautifulSoup (ferramentas prontas)
Sem complexidade desnecessária - apenas scraping e indexação
"""

import requests
from bs4 import BeautifulSoup
import json
import time
from pathlib import Path
from datetime import datetime, timezone
from urllib.parse import urljoin, urlparse
from collections import deque


class SimpleSeniorScraper:
    """Simple web scraper for Senior documentation."""
    
    def __init__(self, base_url, max_pages=50):
        self.base_url = base_url
        self.max_pages = max_pages
        self.output_dir = Path("documentacao")
        self.output_dir.mkdir(exist_ok=True)
        
        self.visited = set()
        self.queue = deque([base_url])
        self.pages_saved = 0
        
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
    
    def run(self):
        """Run the scraper."""
        print(f"\n{'='*70}")
        print(f"SCRAPING: {self.base_url}")
        print(f"{'='*70}\n")
        
        while self.queue and self.pages_saved < self.max_pages:
            url = self.queue.popleft()
            
            if url in self.visited:
                continue
            
            self.visited.add(url)
            
            # Only same domain
            if not self._same_domain(url):
                continue
            
            try:
                print(f"[{self.pages_saved + 1}] Scraping: {url}")
                
                response = self.session.get(url, timeout=10)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract and save
                if self._save_page(url, soup):
                    self.pages_saved += 1
                
                # Find more links
                if self.pages_saved < self.max_pages:
                    for link in soup.find_all('a', href=True):
                        href = link['href']
                        next_url = urljoin(url, href)
                        next_url = next_url.split('#')[0]  # Remove fragments
                        
                        if next_url not in self.visited and self._same_domain(next_url):
                            self.queue.append(next_url)
                
                time.sleep(0.5)  # Be respectful
            
            except Exception as e:
                print(f"   [!] Error: {e}")
                continue
        
        print(f"\n{'='*70}")
        print(f"DONE! Saved {self.pages_saved} pages")
        print(f"{'='*70}\n")
    
    def _save_page(self, url, soup):
        """Save a page."""
        try:
            # Title
            title = soup.find('h1')
            if title:
                title = title.get_text(strip=True)
            else:
                title = soup.title
                if title:
                    title = title.get_text(strip=True)
                else:
                    title = url.split('/')[-1] or "index"
            
            # Content
            content = ""
            for tag in soup.find_all(['main', 'article', 'div']):
                if tag.get('class'):
                    if any(x in str(tag.get('class')).lower() for x in ['content', 'post', 'doc']):
                        text = tag.get_text(separator=' ', strip=True)
                        if len(text) > len(content):
                            content = text
            
            if not content:
                # Fallback
                body = soup.find('body')
                if body:
                    content = body.get_text(separator=' ', strip=True)
            
            if len(content) < 100:
                return False
            
            # Clean content
            content = ' '.join(content.split())[:50000]
            
            # Generate ID from URL
            page_id = urlparse(url).path
            page_id = page_id.strip('/').replace('/', '_')
            if not page_id or page_id == '':
                page_id = 'index'
            
            # Save
            page_dir = self.output_dir / page_id
            page_dir.mkdir(exist_ok=True)
            
            # Metadata
            metadata = {
                "title": title,
                "url": url,
                "section": urlparse(url).path.split('/')[1] if '/' in urlparse(url).path else "root",
                "language": "pt",
                "source": "scraped",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            
            with open(page_dir / "metadata.json", "w", encoding="utf-8") as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            
            with open(page_dir / "content.txt", "w", encoding="utf-8") as f:
                f.write(content)
            
            return True
        
        except Exception as e:
            print(f"   Error saving: {e}")
            return False
    
    def _same_domain(self, url):
        """Check if same domain."""
        base_parsed = urlparse(self.base_url)
        url_parsed = urlparse(url)
        return url_parsed.netloc == base_parsed.netloc


def main():
    """Main."""
    import sys
    
    url = sys.argv[1] if len(sys.argv) > 1 else "https://documentacao.senior.com.br"
    max_pages = int(sys.argv[2]) if len(sys.argv) > 2 else 20
    
    scraper = SimpleSeniorScraper(url, max_pages)
    scraper.run()


if __name__ == "__main__":
    main()
