# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2025 Harish SG

"""
Tavily Web Search Tool for SWE Agent
Provides intelligent web search capabilities using Tavily's search API
"""

import os
import json
from typing import Dict, Any, Optional
from tavily import TavilyClient


def search_web(query: str, max_results: int = 5) -> Dict[str, Any]:
    """
    Search the web using Tavily's intelligent search API.
    
    Args:
        query: The search query string
        max_results: Maximum number of search results to return (default: 5)
        
    Returns:
        Dictionary containing search results with URLs, titles, content, and metadata
        
    Example:
        result = search_web("Who is Leo Messi?")
        print(result["summary"])  # AI-generated summary
        for item in result["results"]:
            print(f"{item['title']}: {item['url']}")
    """
    try:
        # Get API key from environment variable
        api_key = os.getenv("TAVILY_API_KEY")
        if not api_key:
            return {
                "error": "Tavily API key not found. Please set TAVILY_API_KEY environment variable.",
                "setup_instructions": "Get your API key from https://tavily.com and set it as TAVILY_API_KEY",
                "results": [],
                "summary": "API key required for web search functionality"
            }
        
        # Initialize Tavily client
        tavily_client = TavilyClient(api_key=api_key)
        
        # Perform search with error handling
        response = tavily_client.search(
            query=query,
            max_results=max_results,
            include_answer=True,
            include_raw_content=False
        )
        
        # Format response for better usability
        formatted_response = {
            "query": query,
            "summary": response.get("answer", "No summary available"),
            "results": [],
            "total_results": len(response.get("results", [])),
            "search_metadata": {
                "query_time": response.get("query_time", "unknown"),
                "search_depth": response.get("search_depth", "unknown")
            }
        }
        
        # Process search results
        for result in response.get("results", []):
            formatted_result = {
                "title": result.get("title", "No title"),
                "url": result.get("url", ""),
                "content": result.get("content", "No content available"),
                "score": result.get("score", 0),
                "published_date": result.get("published_date", "Unknown date")
            }
            formatted_response["results"].append(formatted_result)
        
        return formatted_response
        
    except Exception as e:
        return {
            "error": f"Tavily search failed: {str(e)}",
            "query": query,
            "results": [],
            "summary": f"Search error: {str(e)}",
            "troubleshooting": "Check API key validity and internet connection"
        }


def search_web_news(query: str, max_results: int = 5) -> Dict[str, Any]:
    """
    Search for recent news using Tavily's news search capabilities.
    
    Args:
        query: The news search query
        max_results: Maximum number of news results to return
        
    Returns:
        Dictionary containing news search results with recent articles
    """
    try:
        api_key = os.getenv("TAVILY_API_KEY")
        if not api_key:
            return {
                "error": "Tavily API key not found for news search",
                "results": [],
                "summary": "API key required for news search functionality"
            }
        
        tavily_client = TavilyClient(api_key=api_key)
        
        # Search for news with recency focus
        response = tavily_client.search(
            query=f"{query} news recent",
            max_results=max_results,
            include_answer=True,
            search_depth="advanced"
        )
        
        return {
            "query": query,
            "news_summary": response.get("answer", "No news summary available"),
            "articles": response.get("results", []),
            "total_articles": len(response.get("results", [])),
            "search_type": "news"
        }
        
    except Exception as e:
        return {
            "error": f"News search failed: {str(e)}",
            "query": query,
            "articles": [],
            "news_summary": f"News search error: {str(e)}"
        }


# Test function for development
if __name__ == "__main__":
    # Test basic search
    test_result = search_web("Who is Leo Messi?")
    print("Search Results:")
    print(json.dumps(test_result, indent=2))
    
    # Test news search
    news_result = search_web_news("AI latest developments")
    print("\nNews Results:")
    print(json.dumps(news_result, indent=2))