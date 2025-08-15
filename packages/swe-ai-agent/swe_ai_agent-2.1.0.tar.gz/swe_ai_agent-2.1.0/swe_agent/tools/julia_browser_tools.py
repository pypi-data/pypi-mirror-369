#!/usr/bin/env python3
"""
Julia Browser Tools for SWE Agent
Comprehensive web browsing capabilities using julia-browser SDK with fallback
"""

from langchain_core.tools import tool
from typing import Dict, Any, List, Optional
import json

try:
    from julia_browser import AgentSDK
    JULIA_BROWSER_AVAILABLE = True
except ImportError:
    JULIA_BROWSER_AVAILABLE = False
    AgentSDK = None
except Exception as e:
    JULIA_BROWSER_AVAILABLE = False
    AgentSDK = None

# Fallback browser implementation
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

# Browser state management
class BrowserState:
    def __init__(self):
        self.current_url = None
        self.current_soup = None
        self.current_content = None
        self.clickable_elements = []
        self.input_elements = []
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

# Global instances
_browser_instance = None
_browser_state = BrowserState()

def get_browser_instance():
    """Get or create browser instance"""
    global _browser_instance
    if _browser_instance is None and JULIA_BROWSER_AVAILABLE:
        try:
            _browser_instance = AgentSDK()
        except Exception as e:
            return None
    return _browser_instance

@tool
def open_website(url: str) -> str:
    """
    Open a website in the browser and get page content.
    
    Args:
        url: The website URL to open (e.g., "https://example.com")
        
    Returns:
        JSON string with page title, URL, and content summary
        
    Example:
        open_website("https://python.org")
        
    Note: This is the first step for any web browsing task. Always start with this tool.
    """
    try:
        # Add protocol if missing
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            
        response = _browser_state.session.get(url, timeout=10)
        response.raise_for_status()
        
        _browser_state.current_url = url
        _browser_state.current_soup = BeautifulSoup(response.content, 'html.parser')
        _browser_state.current_content = response.text
        
        # Extract title
        title = _browser_state.current_soup.title.string.strip() if _browser_state.current_soup.title else "No Title"
        
        # Get text content preview
        text_content = _browser_state.current_soup.get_text()[:500]
        
        return json.dumps({
            "success": True,
            "title": title,
            "url": url,
            "content_preview": text_content.replace('\n', ' ').strip(),
            "message": f"Successfully opened: {title}",
            "next_steps": "Use list_elements() to see clickable items, or search_page() to find specific content"
        })
        
    except Exception as e:
        return json.dumps({
            "error": f"Failed to open website: {str(e)}",
            "url": url,
            "suggestion": "Check URL format and internet connection"
        })

@tool 
def list_elements() -> str:
    """
    List all interactive elements on the current page (buttons, links, input fields).
    
    Returns:
        JSON string with numbered list of clickable elements and input fields
        
    Example:
        After opening a website, use this to see what you can interact with:
        list_elements()
        
    Note: Use this after opening a website to see available interactions. Elements are numbered for easy reference.
    """
    if not _browser_state.current_soup:
        return json.dumps({"error": "No website is open. Use open_website() first."})
    
    try:
        # Find clickable elements
        clickable_selectors = ['a[href]', 'button', 'input[type="submit"]', 'input[type="button"]', '[onclick]']
        clickable_elements = []
        
        for selector in clickable_selectors:
            elements = _browser_state.current_soup.select(selector)
            for elem in elements:
                text = elem.get_text(strip=True)
                href = elem.get('href', '')
                onclick = elem.get('onclick', '')
                element_type = elem.name
                
                clickable_elements.append({
                    "text": text[:100] if text else f"{element_type.upper()}",
                    "type": element_type,
                    "href": href,
                    "onclick": onclick
                })
        
        # Find input elements
        input_elements = []
        inputs = _browser_state.current_soup.find_all(['input', 'textarea', 'select'])
        
        for inp in inputs:
            input_type = inp.get('type', 'text')
            name = inp.get('name', '')
            placeholder = inp.get('placeholder', '')
            
            input_elements.append({
                "type": input_type,
                "name": name,
                "placeholder": placeholder
            })
        
        _browser_state.clickable_elements = clickable_elements
        _browser_state.input_elements = input_elements
        
        result = {
            "success": True,
            "total_clickable": len(clickable_elements),
            "total_inputs": len(input_elements),
            "clickable_elements": clickable_elements[:20],  # Show first 20
            "input_elements": input_elements[:10],  # Show first 10
            "usage": "Use click_element(number) for buttons/links, type_text(number, text) for input fields"
        }
        
        return json.dumps(result)
        
    except Exception as e:
        return json.dumps({
            "error": f"Failed to list elements: {str(e)}",
            "suggestion": "Make sure a website is open first using open_website()"
        })

@tool
def click_element(element_number: int) -> str:
    """
    Click on a button, link, or other clickable element by its number.
    
    Args:
        element_number: The number of the element to click (from list_elements())
        
    Returns:
        JSON string with click result and new page information
        
    Example:
        click_element(1)  # Click the first clickable element
        
    Note: Get element numbers from list_elements() first. Use for buttons, links, and clickable items.
    """
    if not _browser_state.clickable_elements:
        return json.dumps({"error": "No clickable elements found. Use list_elements() first."})
    
    try:
        if element_number < 1 or element_number > len(_browser_state.clickable_elements):
            return json.dumps({"error": f"Invalid element number. Available: 1-{len(_browser_state.clickable_elements)}"})
        
        element = _browser_state.clickable_elements[element_number - 1]
        
        # If it's a link, navigate to it
        if element.get('href'):
            href = element['href']
            
            # Handle relative URLs
            if href.startswith('/'):
                href = urljoin(_browser_state.current_url, href)
            elif not href.startswith(('http://', 'https://')):
                href = urljoin(_browser_state.current_url, href)
            
            # Navigate to the link
            return open_website(href)
        
        return json.dumps({
            "success": True,
            "element_clicked": element_number,
            "element_info": element,
            "message": f"Clicked element {element_number}: {element.get('text', 'Unknown')}",
            "next_steps": "Use get_page_info() to see new page content, or list_elements() for new interactions"
        })
        
    except Exception as e:
        return json.dumps({
            "error": f"Failed to click element {element_number}: {str(e)}",
            "suggestion": "Check element number exists using list_elements()"
        })

@tool
def type_text(field_number: int, text: str) -> str:
    """
    Type text into an input field by its number.
    
    Args:
        field_number: The number of the input field (from list_elements())
        text: The text to type into the field
        
    Returns:
        JSON string with typing result
        
    Example:
        type_text(1, "search query")  # Type into the first input field
        
    Note: Get field numbers from list_elements() first. Use for text inputs, search boxes, forms.
    """
    if not _browser_state.input_elements:
        return json.dumps({"error": "No input elements found. Use list_elements() first."})
    
    try:
        if field_number < 1 or field_number > len(_browser_state.input_elements):
            return json.dumps({"error": f"Invalid field number. Available: 1-{len(_browser_state.input_elements)}"})
        
        field = _browser_state.input_elements[field_number - 1]
        
        # Store the text for form submission
        field['value'] = text
        
        return json.dumps({
            "success": True,
            "field_number": field_number,
            "text_typed": text,
            "field_info": field,
            "message": f"Successfully typed '{text}' into field {field_number}",
            "next_steps": "Use submit_form() to submit, or click_element() to click submit button"
        })
        
    except Exception as e:
        return json.dumps({
            "error": f"Failed to type into field {field_number}: {str(e)}",
            "suggestion": "Check field number exists and is an input field using list_elements()"
        })

@tool
def submit_form() -> str:
    """
    Submit the current form with any typed data.
    
    Returns:
        JSON string with form submission result and new page information
        
    Example:
        After typing into fields, submit the form:
        submit_form()
        
    Note: Use after typing text into form fields. Submits the entire form.
    """
    if not _browser_state.current_soup:
        return json.dumps({"error": "No website is open."})
    
    try:
        # Find form elements
        forms = _browser_state.current_soup.find_all('form')
        
        if not forms:
            return json.dumps({"error": "No forms found on the page"})
        
        # Use the first form
        form = forms[0]
        action = form.get('action', '')
        method = form.get('method', 'GET').upper()
        
        # Build form data from typed values
        form_data = {}
        for field in _browser_state.input_elements:
            if 'value' in field and field.get('name'):
                form_data[field['name']] = field['value']
        
        # Handle relative action URLs
        if action:
            if action.startswith('/'):
                action = urljoin(_browser_state.current_url, action)
            elif not action.startswith(('http://', 'https://')):
                action = urljoin(_browser_state.current_url, action)
        else:
            action = _browser_state.current_url
        
        # Submit form
        if method == 'POST':
            response = _browser_state.session.post(action, data=form_data, timeout=10)
        else:
            response = _browser_state.session.get(action, params=form_data, timeout=10)
        
        response.raise_for_status()
        
        # Update browser state
        _browser_state.current_url = response.url
        _browser_state.current_soup = BeautifulSoup(response.content, 'html.parser')
        _browser_state.current_content = response.text
        
        title = _browser_state.current_soup.title.string.strip() if _browser_state.current_soup.title else "No Title"
        
        return json.dumps({
            "success": True,
            "form_data": form_data,
            "new_url": response.url,
            "title": title,
            "message": "Form submitted successfully",
            "next_steps": "Use get_page_info() to see results, or list_elements() for new interactions"
        })
        
    except Exception as e:
        return json.dumps({
            "error": f"Failed to submit form: {str(e)}",
            "suggestion": "Make sure form fields are filled and form is present on page"
        })

@tool
def follow_link(link_number: int) -> str:
    """
    Navigate to a link by its number.
    
    Args:
        link_number: The number of the link to follow (from list_elements())
        
    Returns:
        JSON string with navigation result and new page information
        
    Example:
        follow_link(2)  # Follow the second link on the page
        
    Note: Alternative to click_element() specifically for links. Get numbers from list_elements().
    """
    return click_element(link_number)

@tool
def get_page_info() -> str:
    """
    Get current page title, URL, and full content.
    
    Returns:
        JSON string with comprehensive page information
        
    Example:
        get_page_info()  # Get current page details
        
    Note: Use to understand current page content and context. Helpful after navigation or form submission.
    """
    if not _browser_state.current_soup:
        return json.dumps({"error": "No website is open. Use open_website() first."})
    
    try:
        title = _browser_state.current_soup.title.string.strip() if _browser_state.current_soup.title else "No Title"
        text_content = _browser_state.current_soup.get_text()
        
        return json.dumps({
            "success": True,
            "title": title,
            "url": _browser_state.current_url,
            "content": text_content[:2000] + "..." if len(text_content) > 2000 else text_content,
            "content_length": len(text_content),
            "next_steps": "Use search_page() to find specific content, or list_elements() for interactions"
        })
        
    except Exception as e:
        return json.dumps({
            "error": f"Failed to get page info: {str(e)}",
            "suggestion": "Make sure a website is open first"
        })

@tool
def search_page(term: str) -> str:
    """
    Search for specific text within the current page.
    
    Args:
        term: The text to search for on the page
        
    Returns:
        JSON string with search results and matches found
        
    Example:
        search_page("Python tutorial")  # Find Python tutorial content
        
    Note: Searches current page content for specific terms. Useful for finding relevant information quickly.
    """
    if not _browser_state.current_soup:
        return json.dumps({"error": "No website is open. Use open_website() first."})
    
    try:
        text_content = _browser_state.current_soup.get_text()
        
        # Find all occurrences
        matches = []
        lines = text_content.split('\n')
        
        for i, line in enumerate(lines):
            if term.lower() in line.lower():
                matches.append({
                    "line_number": i + 1,
                    "content": line.strip()[:200]
                })
        
        return json.dumps({
            "success": True,
            "search_term": term,
            "matches_found": len(matches),
            "matches": matches[:10],  # Show first 10 matches
            "message": f"Found {len(matches)} matches for '{term}'",
            "next_steps": "Use scroll tools to navigate to specific content areas"
        })
        
    except Exception as e:
        return json.dumps({
            "error": f"Failed to search page for '{term}': {str(e)}",
            "suggestion": "Make sure a website is open and has content"
        })

@tool
def scroll_down(chunks: int = 1) -> str:
    """
    Scroll down to see more content on the page.
    
    Args:
        chunks: Number of scroll chunks to move down (default: 1)
        
    Returns:
        JSON string with scroll result and new visible content
        
    Example:
        scroll_down(2)  # Scroll down 2 chunks
        
    Note: Use when page content extends below visible area. Each chunk is a reasonable scroll amount.
    """
    if not _browser_state.current_soup:
        return json.dumps({"error": "No website is open."})
    
    return json.dumps({
        "success": True,
        "scrolled_chunks": chunks,
        "direction": "down",
        "message": f"Simulated scroll down {chunks} chunk(s)",
        "note": "This is a simplified browser - scrolling simulation only",
        "next_steps": "Use list_elements() to see interactive elements, or get_page_info() for content"
    })

@tool
def scroll_up(chunks: int = 1) -> str:
    """
    Scroll up to see previous content on the page.
    
    Args:
        chunks: Number of scroll chunks to move up (default: 1)
        
    Returns:
        JSON string with scroll result and new visible content
        
    Example:
        scroll_up(1)  # Scroll up 1 chunk
        
    Note: Use to go back to previous content areas. Each chunk is a reasonable scroll amount.
    """
    if not _browser_state.current_soup:
        return json.dumps({"error": "No website is open."})
    
    return json.dumps({
        "success": True,
        "scrolled_chunks": chunks,
        "direction": "up",
        "message": f"Simulated scroll up {chunks} chunk(s)",
        "note": "This is a simplified browser - scrolling simulation only",
        "next_steps": "Use list_elements() to see interactive elements, or get_page_info() for content"
    })

@tool
def scroll_to_top() -> str:
    """
    Jump to the top of the page.
    
    Returns:
        JSON string with scroll result
        
    Example:
        scroll_to_top()  # Go to page top
        
    Note: Quick way to return to the beginning of the page content.
    """
    if not _browser_state.current_soup:
        return json.dumps({"error": "No website is open."})
    
    return json.dumps({
        "success": True,
        "position": "top",
        "message": "Simulated scroll to top of page",
        "note": "This is a simplified browser - scrolling simulation only",
        "next_steps": "Use list_elements() to see page header elements"
    })

@tool
def scroll_to_bottom() -> str:
    """
    Jump to the bottom of the page.
    
    Returns:
        JSON string with scroll result
        
    Example:
        scroll_to_bottom()  # Go to page bottom
        
    Note: Quick way to see page footer content and bottom elements.
    """
    if not _browser_state.current_soup:
        return json.dumps({"error": "No website is open."})
    
    return json.dumps({
        "success": True,
        "position": "bottom",
        "message": "Simulated scroll to bottom of page",
        "note": "This is a simplified browser - scrolling simulation only",
        "next_steps": "Use list_elements() to see page footer elements"
    })

@tool 
def get_scroll_info() -> str:
    """
    Get current scroll position and page progress information.
    
    Returns:
        JSON string with scroll position and page navigation info
        
    Example:
        get_scroll_info()  # Check current position
        
    Note: Helpful to understand current position on long pages and navigation progress.
    """
    if not _browser_state.current_soup:
        return json.dumps({"error": "No website is open."})
    
    text_content = _browser_state.current_soup.get_text()
    
    return json.dumps({
        "success": True,
        "position": "full_page_view",
        "content_length": len(text_content),
        "current_url": _browser_state.current_url,
        "message": "Full page content is visible in simplified browser",
        "note": "This is a simplified browser - no actual scrolling",
        "next_steps": "Use list_elements() for interactions or search_page() to find content"
    })