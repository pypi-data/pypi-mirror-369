#!/usr/bin/env python3
"""
Simple test script for SlideCraft MCP Server
"""

import asyncio
import json
from slidecraft_mcp.server import (
    handle_create_presentation,
    handle_add_slide,
    handle_add_text,
    handle_create_chart_llm,
    handle_generate_content_llm,
    handle_export_to_markdown,
    handle_export_to_html,
    handle_save_presentation,
    handle_list_presentations
)

async def test_basic_functionality():
    """Test basic PowerPoint generation functionality."""
    print("Testing SlideCraft MCP Server...")
    
    try:
        # Test 1: Create presentation
        print("\n1. Creating presentation...")
        result = await handle_create_presentation({
            "title": "Test Presentation",
            "template": "business",
            "slide_size": "widescreen"
        })
        print(f"✓ {result[0].text}")
        
        # Extract presentation ID from result
        presentation_id = result[0].text.split("ID: ")[1]
        
        # Test 2: Add slide
        print("\n2. Adding slide...")
        result = await handle_add_slide({
            "presentation_id": presentation_id,
            "layout": "title_content",
            "title": "Test Slide"
        })
        print(f"✓ {result[0].text}")
        
        # Test 3: Add text
        print("\n3. Adding text...")
        result = await handle_add_text({
            "presentation_id": presentation_id,
            "slide_index": 0,
            "text": "This is a test slide created by the lightweight PowerPoint MCP Server!",
            "position": {"x": 1, "y": 1, "width": 8, "height": 2}
        })
        print(f"✓ {result[0].text}")
        
        # Test 4: Generate content with LLM
        print("\n4. Generating content with LLM...")
        result = await handle_generate_content_llm({
            "presentation_id": presentation_id,
            "slide_index": 0,
            "content_prompt": "Benefits of lightweight MCP servers",
            "content_type": "bullets"
        })
        print(f"✓ {result[0].text}")
        
        # Test 5: Create chart with LLM
        print("\n5. Creating chart with LLM...")
        result = await handle_create_chart_llm({
            "presentation_id": presentation_id,
            "slide_index": 0,
            "data_description": "Quarterly performance showing Q1: 100, Q2: 120, Q3: 110, Q4: 150",
            "chart_type": "bar",
            "position": {"x": 1, "y": 3, "width": 8, "height": 4}
        })
        print(f"✓ {result[0].text}")
        
        # Test 6: Export to Markdown
        print("\n6. Exporting to Markdown...")
        result = await handle_export_to_markdown({
            "presentation_id": presentation_id,
            "filename": "test_presentation.md"
        })
        print(f"✓ {result[0].text}")
        
        # Test 7: Export to HTML
        print("\n7. Exporting to HTML...")
        result = await handle_export_to_html({
            "presentation_id": presentation_id,
            "filename": "test_presentation.html",
            "theme": "dark"
        })
        print(f"✓ {result[0].text}")
        
        # Test 8: Save presentation as JSON
        print("\n8. Saving presentation as JSON...")
        result = await handle_save_presentation({
            "presentation_id": presentation_id,
            "filename": "test_presentation.json",
            "format": "json"
        })
        print(f"✓ {result[0].text}")
        
        # Test 9: List presentations
        print("\n9. Listing presentations...")
        result = await handle_list_presentations({})
        print(f"✓ {result[0].text}")
        
        print("\n🎉 All tests passed! Lightweight SlideCraft MCP Server is working correctly.")
        print("📁 Generated files:")
        print("   - test_presentation.json (lightweight data structure)")
        print("   - test_presentation.md (Markdown export)")
        print("   - test_presentation.html (HTML slideshow)")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_basic_functionality())
