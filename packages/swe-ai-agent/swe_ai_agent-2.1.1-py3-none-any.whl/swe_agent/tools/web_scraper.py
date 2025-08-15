# SPDX-License-Identifier: Apache-2.0

import os
import re
import time
from typing import Any, Optional
import requests
from bs4 import BeautifulSoup
import trafilatura
from urllib.parse import urljoin, urlparse


class DocumentationScraper:
    """Advanced web scraper optimized for documentation and technical content."""
    
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://www.google.com/",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }
    
    def scrape_url(self, url: str, extract_links: bool = False) -> dict:
        """
        Scrape content from a URL with enhanced extraction for documentation.
        
        Args:
            url: The URL to scrape
            extract_links: Whether to extract related documentation links
            
        Returns:
            Dictionary with content, metadata, and optionally related links
        """
        try:
            # First try with trafilatura for better content extraction
            downloaded = trafilatura.fetch_url(url)
            if downloaded:
                # Extract main content
                content = trafilatura.extract(downloaded, include_links=True, include_tables=True)
                metadata = trafilatura.extract_metadata(downloaded)
                
                if content:
                    result = {
                        "url": url,
                        "title": metadata.title if metadata else "Unknown",
                        "content": content,
                        "extraction_method": "trafilatura",
                        "success": True
                    }
                    
                    # Extract related links if requested
                    if extract_links:
                        result["related_links"] = self._extract_documentation_links(url, downloaded)
                    
                    return result
            
            # Fallback to BeautifulSoup if trafilatura fails
            return self._fallback_scrape(url, extract_links)
            
        except Exception as e:
            return {
                "url": url,
                "content": f"Error scraping URL: {str(e)}",
                "success": False,
                "error": str(e)
            }
    
    def _fallback_scrape(self, url: str, extract_links: bool = False) -> dict:
        """Fallback scraping method using BeautifulSoup."""
        try:
            response = requests.get(url, timeout=15, headers=self.headers)
            response.encoding = response.apparent_encoding
            
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "aside"]):
                script.decompose()
            
            # Extract title
            title = soup.find("title")
            title_text = title.text.strip() if title else "Unknown"
            
            # Try to find main content areas
            content_selectors = [
                "main", "article", ".content", "#content", 
                ".documentation", ".docs", ".markdown-body"
            ]
            
            content_element = None
            for selector in content_selectors:
                content_element = soup.select_one(selector)
                if content_element:
                    break
            
            if not content_element:
                content_element = soup.find("body")
            
            # Extract text with better formatting
            text = content_element.get_text(" ", strip=True) if content_element else soup.get_text(" ", strip=True)
            
            # Clean up text
            text = re.sub(r"[ \t]+", " ", text)
            text = re.sub(r"\s*\n\s*", "\n", text)
            text = re.sub(r"\n{3,}", "\n\n", text)
            
            result = {
                "url": url,
                "title": title_text,
                "content": text,
                "extraction_method": "beautifulsoup",
                "success": True
            }
            
            if extract_links:
                result["related_links"] = self._extract_documentation_links(url, response.text)
            
            return result
            
        except Exception as e:
            return {
                "url": url,
                "content": f"Error in fallback scraping: {str(e)}",
                "success": False,
                "error": str(e)
            }
    
    def _extract_documentation_links(self, base_url: str, html_content: str) -> list:
        """Extract relevant documentation links from the page."""
        try:
            soup = BeautifulSoup(html_content, "html.parser")
            links = []
            
            # Look for links that likely point to documentation
            doc_patterns = [
                r"doc", r"guide", r"tutorial", r"api", r"reference", 
                r"getting.?started", r"install", r"setup", r"config"
            ]
            
            for link in soup.find_all("a", href=True):
                href = link.get("href")
                text = link.get_text().strip().lower()
                
                # Skip empty links
                if not href or not text:
                    continue
                
                # Convert relative URLs to absolute
                full_url = urljoin(base_url, href)
                
                # Check if link text or URL suggests documentation
                is_doc_link = any(re.search(pattern, text + " " + href.lower()) for pattern in doc_patterns)
                
                if is_doc_link and len(text) > 2:
                    links.append({
                        "url": full_url,
                        "text": text,
                        "type": "documentation"
                    })
            
            # Remove duplicates and limit results
            seen = set()
            unique_links = []
            for link in links:
                if link["url"] not in seen:
                    seen.add(link["url"])
                    unique_links.append(link)
                    if len(unique_links) >= 20:  # Limit to top 20 links
                        break
            
            return unique_links
            
        except Exception:
            return []
    
    def scrape_multiple_urls(self, urls: list, delay: float = 1.0) -> list:
        """
        Scrape multiple URLs with rate limiting.
        
        Args:
            urls: List of URLs to scrape
            delay: Delay between requests in seconds
            
        Returns:
            List of scraping results
        """
        results = []
        
        for i, url in enumerate(urls):
            if i > 0:  # Skip delay for first URL
                time.sleep(delay)
            
            result = self.scrape_url(url)
            results.append(result)
        
        return results


def scrape_website_content(url: str, extract_links: bool = False) -> str:
    """
    Scrape content from a website URL. Optimized for documentation.
    
    Args:
        url: The website URL to scrape
        extract_links: Whether to include related documentation links
        
    Returns:
        Formatted text content from the website
    """
    scraper = DocumentationScraper()
    result = scraper.scrape_url(url, extract_links)
    
    if not result["success"]:
        return f"Failed to scrape {url}: {result.get('error', 'Unknown error')}"
    
    # Format the output
    output = f"# {result['title']}\n"
    output += f"Source: {result['url']}\n"
    output += f"Extraction method: {result['extraction_method']}\n\n"
    output += result["content"]
    
    # Add related links if extracted
    if extract_links and "related_links" in result and result["related_links"]:
        output += "\n\n## Related Documentation Links:\n"
        for link in result["related_links"][:10]:  # Show top 10 links
            output += f"- [{link['text']}]({link['url']})\n"
    
    return output


def scrape_documentation_site(base_url: str, max_pages: int = 5) -> str:
    """
    Scrape a documentation site by following internal links.
    
    Args:
        base_url: The base URL of the documentation site
        max_pages: Maximum number of pages to scrape
        
    Returns:
        Combined content from multiple pages
    """
    scraper = DocumentationScraper()
    
    # Start with the base URL
    first_result = scraper.scrape_url(base_url, extract_links=True)
    
    if not first_result["success"]:
        return f"Failed to scrape base URL {base_url}: {first_result.get('error', 'Unknown error')}"
    
    # Collect URLs to scrape
    urls_to_scrape = [base_url]
    
    # Add related documentation links
    if "related_links" in first_result:
        base_domain = urlparse(base_url).netloc
        for link in first_result["related_links"]:
            link_domain = urlparse(link["url"]).netloc
            if link_domain == base_domain:  # Only follow same-domain links
                urls_to_scrape.append(link["url"])
                if len(urls_to_scrape) >= max_pages:
                    break
    
    # Scrape all URLs
    results = scraper.scrape_multiple_urls(urls_to_scrape[:max_pages], delay=1.0)
    
    # Combine content
    combined_content = f"# Documentation from {base_url}\n\n"
    
    for i, result in enumerate(results):
        if result["success"]:
            combined_content += f"## Page {i+1}: {result['title']}\n"
            combined_content += f"URL: {result['url']}\n\n"
            combined_content += result["content"]
            combined_content += "\n\n" + "="*50 + "\n\n"
        else:
            combined_content += f"## Failed to scrape: {result['url']}\n"
            combined_content += f"Error: {result.get('error', 'Unknown error')}\n\n"
    
    return combined_content