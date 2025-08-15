#!/usr/bin/env python3
"""
List all available tools in SlideCraft MCP Server
"""

import asyncio
from slidecraft_mcp.server import handle_list_tools

async def list_tools():
    """List all available tools."""
    print("🛠️  SlideCraft MCP Server - Available Tools\n")
    
    tools = await handle_list_tools()
    
    for i, tool in enumerate(tools, 1):
        print(f"{i:2}. 🔧 {tool.name}")
        print(f"    📋 {tool.description}")
        
        # Show required parameters
        required = tool.inputSchema.get('required', [])
        if required:
            print(f"    📝 Required: {', '.join(required)}")
        
        # Show properties
        properties = tool.inputSchema.get('properties', {})
        if properties:
            print(f"    ⚙️  Parameters: {', '.join(properties.keys())}")
        print()
    
    print(f"📊 Total tools available: {len(tools)}")
    print("\n🚀 SlideCraft MCP Features:")
    print("   ✅ LLM-powered content generation")
    print("   ✅ ASCII-based charts and infographics") 
    print("   ✅ Multiple export formats (JSON, Markdown, HTML)")
    print("   ✅ Zero heavyweight dependencies")
    print("   ✅ Lightning-fast startup and execution")

if __name__ == "__main__":
    asyncio.run(list_tools())
