#!/usr/bin/env python3
"""
Example: Website Screenshot Analysis with SWE Agent Vision Tool

This example demonstrates how to use the SWE Agent Vision Tool to analyze
website screenshots and generate detailed build instructions.

Usage:
    python examples/vision_website_analysis.py path/to/screenshot.png

Requirements:
    - ANTHROPIC_API_KEY environment variable set
    - Image file (PNG, JPG, JPEG, WebP)
"""

import sys
import os
from pathlib import Path

# Add swe_agent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from swe_agent.tools.vision_analyzer import analyze_website_image, get_build_summary
from swe_agent.tools.website_vision_tool import analyze_website_screenshot


def main():
    if len(sys.argv) < 2:
        print("Usage: python vision_website_analysis.py <image_path> [context]")
        print("Example: python vision_website_analysis.py screenshot.png 'e-commerce website'")
        sys.exit(1)
    
    image_path = sys.argv[1]
    context = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not os.path.exists(image_path):
        print(f"Error: Image file not found: {image_path}")
        sys.exit(1)
    
    print(f"🔍 Analyzing website screenshot: {image_path}")
    if context:
        print(f"📝 Context: {context}")
    print("-" * 60)
    
    try:
        # Example 1: Quick Summary Analysis
        print("📋 QUICK BUILD SUMMARY:")
        print("=" * 40)
        summary = get_build_summary(image_path, context)
        print(summary)
        print("\n")
        
        # Example 2: Detailed Analysis
        print("🔬 DETAILED ANALYSIS:")
        print("=" * 40)
        detailed_analysis = analyze_website_screenshot(
            image_path=image_path,
            context=context,
            output_format="detailed"
        )
        
        if detailed_analysis["success"]:
            print(f"✅ Analysis completed successfully")
            print(f"🎯 Estimated Complexity: {detailed_analysis['estimated_complexity']}")
            
            # Show build plan
            print("\n📋 BUILD PLAN:")
            for i, step in enumerate(detailed_analysis["build_plan"], 1):
                print(f"  {i}. {step}")
            
            # Show key components
            print(f"\n🧩 COMPONENTS IDENTIFIED ({len(detailed_analysis['components'])}):")
            for comp in detailed_analysis["components"][:5]:  # Show first 5
                comp_type = comp.get("type", "unknown")
                description = comp.get("description", "No description")[:80]
                priority = comp.get("build_priority", 3)
                print(f"  • {comp_type.upper()} (Priority {priority}): {description}")
            
            # Show styling guide
            styling = detailed_analysis["styling"]
            print(f"\n🎨 STYLING GUIDE:")
            colors = styling.get("color_palette", [])
            if colors:
                print(f"  Colors: {', '.join(colors)}")
            print(f"  Style: {styling.get('style_approach', 'Not specified')}")
            print(f"  CSS Approach: {styling.get('css_methodology', 'Not specified')}")
            
            # Show agent instructions
            print(f"\n🤖 AGENT INSTRUCTIONS:")
            for instruction in detailed_analysis["agent_instructions"]:
                print(f"  • {instruction}")
                
        else:
            print(f"❌ Analysis failed: {detailed_analysis['error']}")
    
    except Exception as e:
        print(f"❌ Error during analysis: {str(e)}")
        return 1
    
    print("\n" + "=" * 60)
    print("✨ Analysis complete! Use this information to build your website.")
    return 0


if __name__ == "__main__":
    sys.exit(main())