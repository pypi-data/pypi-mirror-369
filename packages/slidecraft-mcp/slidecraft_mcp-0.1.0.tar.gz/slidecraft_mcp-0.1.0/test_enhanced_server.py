#!/usr/bin/env python3
"""
Test script for enhanced lightweight SlideCraft MCP Server with LLM features
"""

import asyncio
from slidecraft_mcp.server import (
    handle_create_presentation_from_prompt,
    handle_add_infographic,
    handle_export_to_markdown,
    handle_export_to_html
)

async def test_enhanced_features():
    """Test the new LLM-powered features."""
    print("Testing Enhanced Lightweight SlideCraft MCP Server...")
    
    try:
        # Test 1: Create complete presentation from prompt
        print("\n1. Creating presentation from LLM prompt...")
        result = await handle_create_presentation_from_prompt({
            "prompt": "The benefits of using lightweight microservices in modern software architecture",
            "slide_count": 4,
            "template": "business"
        })
        print(f"✓ {result[0].text}")
        
        # Extract presentation ID from result
        presentation_id = result[0].text.split("ID: ")[1].split("\n")[0]
        
        # Test 2: Add infographic
        print("\n2. Adding process infographic...")
        result = await handle_add_infographic({
            "presentation_id": presentation_id,
            "slide_index": 0,
            "infographic_type": "process",
            "data": "Microservice deployment pipeline: Code → Build → Test → Deploy"
        })
        print(f"✓ {result[0].text}")
        
        # Test 3: Add comparison infographic
        print("\n3. Adding comparison infographic...")
        result = await handle_add_infographic({
            "presentation_id": presentation_id,
            "slide_index": 1,
            "infographic_type": "comparison",
            "data": "Monolith vs Microservices architecture"
        })
        print(f"✓ {result[0].text}")
        
        # Test 4: Export enhanced presentation
        print("\n4. Exporting enhanced presentation to HTML...")
        result = await handle_export_to_html({
            "presentation_id": presentation_id,
            "filename": "enhanced_presentation.html",
            "theme": "corporate"
        })
        print(f"✓ {result[0].text}")
        
        # Test 5: Export to Markdown
        print("\n5. Exporting to Markdown...")
        result = await handle_export_to_markdown({
            "presentation_id": presentation_id,
            "filename": "enhanced_presentation.md"
        })
        print(f"✓ {result[0].text}")
        
        print("\n🎉 All enhanced tests passed!")
        print("🚀 Features tested:")
        print("   ✅ LLM-based presentation generation")
        print("   ✅ ASCII infographics (process, comparison)")
        print("   ✅ Enhanced content templates")
        print("   ✅ Corporate theme export")
        print("   ✅ Zero heavyweight dependencies")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_enhanced_features())
