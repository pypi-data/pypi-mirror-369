"""
Pure Vision Analysis Tool for SWE Agent

This tool ONLY analyzes website screenshots and extracts information.
It does NOT build websites - that's SWE Agent's job.

The tool provides structured analysis data that SWE Agent can use
to make informed decisions about how to build similar websites.
"""

import base64
import os
import json
from typing import Dict, Any, List, Optional
from pathlib import Path
from anthropic import Anthropic


class PureVisionAnalyzer:
    """
    Vision analyzer that ONLY extracts information from website screenshots.
    Does not generate code or build websites - only provides analysis data.
    """
    
    def __init__(self):
        # The newest Anthropic model is "claude-sonnet-4-20250514"
        api_key = os.environ.get('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is required")
        self.client = Anthropic(api_key=api_key)
        self.model = "claude-sonnet-4-20250514"
    
    def analyze_screenshot(self, image_path: str, context: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze a website screenshot and extract structured information.
        
        Args:
            image_path: Path to the screenshot image
            context: Optional context about the website
            
        Returns:
            Dictionary containing ONLY analysis data - no build instructions
        """
        
        if not os.path.exists(image_path):
            return {
                "success": False,
                "error": f"Screenshot not found: {image_path}"
            }
        
        try:
            # Encode image
            base64_image = self._encode_image(image_path)
            image_type = Path(image_path).suffix.lower().replace('.', '')
            if image_type not in ['jpg', 'jpeg', 'png', 'webp']:
                image_type = 'png'
            
            # Create analysis prompt that focuses ONLY on extraction
            prompt = self._build_extraction_prompt(context)
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=3000,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": f"image/{image_type}",
                                    "data": base64_image
                                }
                            }
                        ]
                    }
                ]
            )
            
            # Extract analysis text
            analysis_text = ""
            for content_block in response.content:
                if hasattr(content_block, 'text'):
                    analysis_text = content_block.text
                    break
            
            return self._parse_analysis_data(analysis_text)
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Vision analysis failed: {str(e)}"
            }
    
    def _encode_image(self, image_path: str) -> str:
        """Encode image to base64."""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def _build_extraction_prompt(self, context: Optional[str] = None) -> str:
        """Build prompt that focuses on DATA EXTRACTION ONLY."""
        
        prompt = """
You are analyzing a website screenshot to extract FACTUAL INFORMATION ONLY.
Do NOT provide build instructions, code suggestions, or implementation advice.
ONLY describe what you observe in the image.

Provide your analysis in this JSON structure:

{
  "layout": {
    "overall_structure": "Describe the layout (header, main, sidebar, footer positions)",
    "content_organization": "How content is arranged (grid, columns, sections)",
    "spacing_patterns": "Observed spacing and alignment"
  },
  "visual_elements": {
    "color_palette": ["List of colors you can identify"],
    "typography": {
      "heading_styles": "Observed heading font characteristics",
      "body_text": "Body text appearance",
      "special_text": "Any unique text styling"
    },
    "design_style": "Overall design aesthetic (modern, minimal, corporate, etc.)"
  },
  "components_observed": [
    {
      "type": "Type of component (header, navigation, search, card, form, etc.)",
      "description": "What this component contains/displays",
      "location": "Where it appears on the page",
      "visual_characteristics": "Colors, size, styling details",
      "content_type": "Type of content (text, images, data, etc.)"
    }
  ],
  "interactive_elements": [
    {
      "element_type": "button, link, input, dropdown, etc.",
      "appearance": "Visual characteristics",
      "location": "Where it appears",
      "likely_purpose": "What it probably does based on appearance"
    }
  ],
  "data_displays": [
    {
      "type": "chart, metric, list, table, etc.",
      "content": "What kind of data is shown",
      "format": "How the data is presented"
    }
  ],
  "technical_observations": {
    "responsive_indicators": "Signs of responsive design",
    "ui_framework_hints": "Any UI framework patterns you recognize",
    "complexity_assessment": "Simple, moderate, or complex interface"
  }
}

IMPORTANT: Only describe what you can actually see in the image. Do not make assumptions or provide implementation suggestions.
"""
        
        if context:
            prompt += f"\n\nContext provided: {context}"
        
        return prompt
    
    def _parse_analysis_data(self, response_text: str) -> Dict[str, Any]:
        """Parse response into structured data."""
        
        try:
            # Extract JSON from response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                analysis_data = json.loads(json_str)
                
                return {
                    "success": True,
                    "analysis": analysis_data,
                    "raw_response": response_text
                }
            else:
                # No JSON found, return as text analysis
                return {
                    "success": True,
                    "analysis": {
                        "text_analysis": response_text,
                        "parsed": False
                    },
                    "raw_response": response_text
                }
                
        except json.JSONDecodeError:
            return {
                "success": True,
                "analysis": {
                    "text_analysis": response_text,
                    "parsed": False,
                    "note": "Response could not be parsed as JSON"
                },
                "raw_response": response_text
            }


def extract_website_info(image_path: str, context: Optional[str] = None) -> Dict[str, Any]:
    """
    Convenience function to extract website information from screenshot.
    
    Args:
        image_path: Path to screenshot
        context: Optional context
        
    Returns:
        Structured analysis data for SWE Agent to use
    """
    analyzer = PureVisionAnalyzer()
    return analyzer.analyze_screenshot(image_path, context)


def get_component_list(image_path: str) -> List[Dict[str, Any]]:
    """
    Extract just the list of components from a screenshot.
    
    Args:
        image_path: Path to screenshot
        
    Returns:
        List of components with their details
    """
    analysis = extract_website_info(image_path)
    
    if analysis.get("success") and analysis.get("analysis", {}).get("parsed", True):
        return analysis["analysis"].get("components_observed", [])
    
    return []


def get_color_palette(image_path: str) -> List[str]:
    """
    Extract color palette from screenshot.
    
    Args:
        image_path: Path to screenshot
        
    Returns:
        List of color codes/names
    """
    analysis = extract_website_info(image_path)
    
    if analysis.get("success") and analysis.get("analysis", {}).get("parsed", True):
        visual_elements = analysis["analysis"].get("visual_elements", {})
        return visual_elements.get("color_palette", [])
    
    return []


def get_layout_info(image_path: str) -> Dict[str, str]:
    """
    Extract layout information from screenshot.
    
    Args:
        image_path: Path to screenshot
        
    Returns:
        Layout structure details
    """
    analysis = extract_website_info(image_path)
    
    if analysis.get("success") and analysis.get("analysis", {}).get("parsed", True):
        return analysis["analysis"].get("layout", {})
    
    return {}