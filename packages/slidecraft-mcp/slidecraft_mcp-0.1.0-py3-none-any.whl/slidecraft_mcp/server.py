import asyncio
import json
import os
import uuid
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
import datetime

from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
import mcp.server.stdio

# Lightweight data structures instead of heavy libraries
@dataclass
class SlideContent:
    type: str  # "text", "image", "chart", "shape"
    content: str
    position: Dict[str, float]
    style: Dict[str, Any]

@dataclass
class Slide:
    title: str
    layout: str
    contents: List[SlideContent]

@dataclass
class Presentation:
    id: str
    title: str
    template: str
    slide_size: str
    slides: List[Slide]
    created_at: str

# Store presentations as lightweight JSON-serializable objects
presentations: Dict[str, Presentation] = {}
presentation_metadata: Dict[str, Dict[str, Any]] = {}

server = Server("slidecraft-mcp")

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """
    List available PowerPoint tools.
    Each tool specifies its arguments using JSON Schema.
    """
    return [
        types.Tool(
            name="create_presentation",
            description="Create a new PowerPoint presentation",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Presentation title"
                    },
                    "template": {
                        "type": "string",
                        "description": "Template to use (blank, title_slide, etc.)",
                        "default": "blank"
                    },
                    "slide_size": {
                        "type": "string",
                        "enum": ["widescreen", "standard"],
                        "description": "Slide dimensions",
                        "default": "widescreen"
                    }
                },
                "required": ["title"]
            }
        ),
        types.Tool(
            name="add_slide",
            description="Add a new slide to presentation",
            inputSchema={
                "type": "object",
                "properties": {
                    "presentation_id": {
                        "type": "string",
                        "description": "Presentation ID"
                    },
                    "layout": {
                        "type": "string",
                        "description": "Slide layout type",
                        "default": "blank"
                    },
                    "title": {
                        "type": "string",
                        "description": "Slide title"
                    }
                },
                "required": ["presentation_id"]
            }
        ),
        types.Tool(
            name="add_text",
            description="Add text to a slide",
            inputSchema={
                "type": "object",
                "properties": {
                    "presentation_id": {
                        "type": "string",
                        "description": "Presentation ID"
                    },
                    "slide_index": {
                        "type": "integer",
                        "description": "Slide index (0-based)"
                    },
                    "text": {
                        "type": "string",
                        "description": "Text content"
                    },
                    "position": {
                        "type": "object",
                        "description": "Position and size {x, y, width, height} in inches"
                    }
                },
                "required": ["presentation_id", "slide_index", "text"]
            }
        ),
        types.Tool(
            name="save_presentation",
            description="Save presentation to file",
            inputSchema={
                "type": "object",
                "properties": {
                    "presentation_id": {
                        "type": "string",
                        "description": "Presentation ID"
                    },
                    "filename": {
                        "type": "string",
                        "description": "Output filename"
                    },
                    "format": {
                        "type": "string",
                        "enum": ["pptx", "pdf"],
                        "description": "Export format",
                        "default": "pptx"
                    }
                },
                "required": ["presentation_id", "filename"]
            }
        ),
        types.Tool(
            name="create_chart_llm",
            description="Generate chart data using LLM and create visualization",
            inputSchema={
                "type": "object",
                "properties": {
                    "presentation_id": {"type": "string"},
                    "slide_index": {"type": "integer"},
                    "data_description": {
                        "type": "string",
                        "description": "Describe the data you want to visualize"
                    },
                    "chart_type": {
                        "type": "string",
                        "enum": ["bar", "line", "pie", "scatter"],
                        "default": "bar"
                    },
                    "position": {
                        "type": "object",
                        "description": "Position and size {x, y, width, height}"
                    }
                },
                "required": ["presentation_id", "slide_index", "data_description"]
            }
        ),
        types.Tool(
            name="generate_content_llm",
            description="Generate slide content using LLM",
            inputSchema={
                "type": "object",
                "properties": {
                    "presentation_id": {"type": "string"},
                    "slide_index": {"type": "integer"},
                    "content_prompt": {
                        "type": "string",
                        "description": "Describe what content you want generated"
                    },
                    "content_type": {
                        "type": "string",
                        "enum": ["text", "bullets", "title", "summary"],
                        "default": "text"
                    }
                },
                "required": ["presentation_id", "slide_index", "content_prompt"]
            }
        ),
        types.Tool(
            name="export_to_markdown",
            description="Export presentation as Markdown (lightweight alternative)",
            inputSchema={
                "type": "object",
                "properties": {
                    "presentation_id": {"type": "string"},
                    "filename": {"type": "string"}
                },
                "required": ["presentation_id", "filename"]
            }
        ),
        types.Tool(
            name="export_to_html",
            description="Export presentation as HTML slides (no heavy dependencies)",
            inputSchema={
                "type": "object",
                "properties": {
                    "presentation_id": {"type": "string"},
                    "filename": {"type": "string"},
                    "theme": {
                        "type": "string",
                        "enum": ["default", "dark", "minimal", "corporate"],
                        "default": "default"
                    }
                },
                "required": ["presentation_id", "filename"]
            }
        ),
        types.Tool(
            name="create_presentation_from_prompt",
            description="Generate an entire presentation using LLM from a single prompt",
            inputSchema={
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "Describe the presentation you want to create"
                    },
                    "slide_count": {
                        "type": "integer",
                        "description": "Number of slides to generate",
                        "default": 5
                    },
                    "template": {
                        "type": "string",
                        "description": "Presentation template",
                        "default": "business"
                    }
                },
                "required": ["prompt"]
            }
        ),
        types.Tool(
            name="add_infographic",
            description="Add an ASCII-based infographic to a slide",
            inputSchema={
                "type": "object",
                "properties": {
                    "presentation_id": {"type": "string"},
                    "slide_index": {"type": "integer"},
                    "infographic_type": {
                        "type": "string",
                        "enum": ["process", "comparison", "timeline", "hierarchy"],
                        "default": "process"
                    },
                    "data": {
                        "type": "string",
                        "description": "Data or description for the infographic"
                    }
                },
                "required": ["presentation_id", "slide_index", "data"]
            }
        ),
        types.Tool(
            name="list_presentations",
            description="List all active presentations",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict[str, Any]) -> list[types.TextContent]:
    """Handle tool calls by routing to appropriate handlers."""
    try:
        if name == "create_presentation":
            return await handle_create_presentation(arguments)
        elif name == "add_slide":
            return await handle_add_slide(arguments)
        elif name == "add_text":
            return await handle_add_text(arguments)
        elif name == "save_presentation":
            return await handle_save_presentation(arguments)
        elif name == "create_chart_llm":
            return await handle_create_chart_llm(arguments)
        elif name == "generate_content_llm":
            return await handle_generate_content_llm(arguments)
        elif name == "export_to_markdown":
            return await handle_export_to_markdown(arguments)
        elif name == "export_to_html":
            return await handle_export_to_html(arguments)
        elif name == "create_presentation_from_prompt":
            return await handle_create_presentation_from_prompt(arguments)
        elif name == "add_infographic":
            return await handle_add_infographic(arguments)
        elif name == "list_presentations":
            return await handle_list_presentations(arguments)
        else:
            return [types.TextContent(type="text", text=f"Unknown tool: {name}")]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Error: {str(e)}")]

async def handle_create_presentation(arguments: dict[str, Any]) -> list[types.TextContent]:
    """Create a new lightweight presentation structure."""
    try:
        title = arguments.get("title", "New Presentation")
        template = arguments.get("template", "blank")
        slide_size = arguments.get("slide_size", "widescreen")
        
        # Generate unique ID
        presentation_id = str(uuid.uuid4())
        
        # Create lightweight presentation object
        presentation = Presentation(
            id=presentation_id,
            title=title,
            template=template,
            slide_size=slide_size,
            slides=[],
            created_at=datetime.datetime.now().isoformat()
        )
        
        # Store presentation
        presentations[presentation_id] = presentation
        presentation_metadata[presentation_id] = asdict(presentation)
        
        return [types.TextContent(
            type="text",
            text=f"✅ Created lightweight presentation '{title}' with ID: {presentation_id}"
        )]
    except Exception as e:
        return [types.TextContent(
            type="text",
            text=f"❌ Error creating presentation: {str(e)}"
        )]

async def handle_add_slide(arguments: dict[str, Any]) -> list[types.TextContent]:
    """Add a new slide to presentation."""
    try:
        presentation_id = arguments.get("presentation_id")
        layout = arguments.get("layout", "blank")
        title = arguments.get("title", "")
        
        if presentation_id not in presentations:
            return [types.TextContent(
                type="text",
                text=f"❌ Presentation {presentation_id} not found"
            )]
        
        # Create new slide
        slide = Slide(
            title=title,
            layout=layout,
            contents=[]
        )
        
        # Add to presentation
        presentations[presentation_id].slides.append(slide)
        
        # Update metadata
        presentation_metadata[presentation_id] = asdict(presentations[presentation_id])
        
        slide_index = len(presentations[presentation_id].slides) - 1
        
        return [types.TextContent(
            type="text",
            text=f"✅ Added slide {slide_index} '{title}' to presentation {presentation_id}"
        )]
    except Exception as e:
        return [types.TextContent(
            type="text",
            text=f"❌ Error adding slide: {str(e)}"
        )]

async def handle_add_text(arguments: dict[str, Any]) -> list[types.TextContent]:
    """Add text to a slide."""
    try:
        presentation_id = arguments.get("presentation_id")
        slide_index = arguments.get("slide_index", 0)
        text = arguments.get("text", "")
        position = arguments.get("position", {"x": 1, "y": 1, "width": 8, "height": 1})
        
        if presentation_id not in presentations:
            return [types.TextContent(
                type="text",
                text=f"❌ Presentation {presentation_id} not found"
            )]
        
        presentation = presentations[presentation_id]
        
        if slide_index >= len(presentation.slides):
            return [types.TextContent(
                type="text",
                text=f"❌ Slide index {slide_index} out of range"
            )]
        
        # Create text content
        content = SlideContent(
            type="text",
            content=text,
            position=position,
            style={"font_size": 18, "color": "black"}
        )
        
        # Add to slide
        presentation.slides[slide_index].contents.append(content)
        
        # Update metadata
        presentation_metadata[presentation_id] = asdict(presentation)
        
        return [types.TextContent(
            type="text",
            text=f"✅ Added text to slide {slide_index}: '{text[:50]}...'"
        )]
    except Exception as e:
        return [types.TextContent(
            type="text",
            text=f"❌ Error adding text: {str(e)}"
        )]

async def handle_save_presentation(arguments: dict[str, Any]) -> list[types.TextContent]:
    """Save presentation as JSON (lightweight format)."""
    try:
        presentation_id = arguments.get("presentation_id")
        filename = arguments.get("filename")
        format_type = arguments.get("format", "json")
        
        if presentation_id not in presentations:
            return [types.TextContent(
                type="text",
                text=f"❌ Presentation {presentation_id} not found"
            )]
        
        presentation = presentations[presentation_id]
        
        # Save as JSON (lightweight alternative to PPTX)
        if not filename.endswith(".json"):
            filename = f"{filename}.json"
        
        with open(filename, 'w') as f:
            json.dump(asdict(presentation), f, indent=2)
        
        file_size = os.path.getsize(filename)
        
        return [types.TextContent(
            type="text",
            text=f"✅ Saved presentation as lightweight JSON: {filename} ({file_size} bytes)\n" +
                 f"💡 Use export_to_html or export_to_markdown for presentation formats"
        )]
    except Exception as e:
        return [types.TextContent(
            type="text",
            text=f"❌ Error saving presentation: {str(e)}"
        )]

async def handle_create_chart_llm(arguments: dict[str, Any]) -> list[types.TextContent]:
    """Generate chart using LLM description instead of heavy plotting libraries."""
    try:
        presentation_id = arguments.get("presentation_id")
        slide_index = arguments.get("slide_index", 0)
        data_description = arguments.get("data_description", "")
        chart_type = arguments.get("chart_type", "bar")
        position = arguments.get("position", {"x": 1, "y": 2, "width": 8, "height": 4})
        
        if presentation_id not in presentations:
            return [types.TextContent(
                type="text",
                text=f"❌ Presentation {presentation_id} not found"
            )]
        
        presentation = presentations[presentation_id]
        
        if slide_index >= len(presentation.slides):
            return [types.TextContent(
                type="text",
                text=f"❌ Slide index {slide_index} out of range"
            )]
        
        # Create ASCII art chart representation (lightweight alternative)
        chart_content = f"""
📊 {chart_type.upper()} CHART
Data: {data_description}

ASCII Representation:
{generate_ascii_chart(chart_type, data_description)}

Position: {position}
"""
        
        # Create chart content
        content = SlideContent(
            type="chart",
            content=chart_content,
            position=position,
            style={"chart_type": chart_type, "data_description": data_description}
        )
        
        # Add to slide
        presentation.slides[slide_index].contents.append(content)
        
        # Update metadata
        presentation_metadata[presentation_id] = asdict(presentation)
        
        return [types.TextContent(
            type="text",
            text=f"✅ Added {chart_type} chart to slide {slide_index}\n" +
                 f"📊 Data: {data_description}\n" +
                 f"💡 Lightweight ASCII representation created (no heavy plotting libs needed)"
        )]
    except Exception as e:
        return [types.TextContent(
            type="text",
            text=f"❌ Error creating chart: {str(e)}"
        )]

async def handle_generate_content_llm(arguments: dict[str, Any]) -> list[types.TextContent]:
    """Generate content using LLM prompts."""
    try:
        presentation_id = arguments.get("presentation_id")
        slide_index = arguments.get("slide_index", 0)
        content_prompt = arguments.get("content_prompt", "")
        content_type = arguments.get("content_type", "text")
        
        if presentation_id not in presentations:
            return [types.TextContent(
                type="text",
                text=f"❌ Presentation {presentation_id} not found"
            )]
        
        presentation = presentations[presentation_id]
        
        if slide_index >= len(presentation.slides):
            return [types.TextContent(
                type="text",
                text=f"❌ Slide index {slide_index} out of range"
            )]
        
        # Generate content based on prompt (placeholder for LLM integration)
        generated_content = await call_llm_api(content_prompt, content_type)
        
        # Create content
        content = SlideContent(
            type="generated_text",
            content=generated_content,
            position={"x": 1, "y": 1, "width": 10, "height": 6},
            style={"content_type": content_type, "prompt": content_prompt}
        )
        
        # Add to slide
        presentation.slides[slide_index].contents.append(content)
        
        # Update metadata
        presentation_metadata[presentation_id] = asdict(presentation)
        
        return [types.TextContent(
            type="text",
            text=f"✅ Generated {content_type} content for slide {slide_index}\n" +
                 f"📝 Prompt: {content_prompt}\n" +
                 f"🤖 Content: {generated_content[:100]}..."
        )]
    except Exception as e:
        return [types.TextContent(
            type="text",
            text=f"❌ Error generating content: {str(e)}"
        )]

async def handle_export_to_markdown(arguments: dict[str, Any]) -> list[types.TextContent]:
    """Export presentation as Markdown."""
    try:
        presentation_id = arguments.get("presentation_id")
        filename = arguments.get("filename")
        
        if presentation_id not in presentations:
            return [types.TextContent(
                type="text",
                text=f"❌ Presentation {presentation_id} not found"
            )]
        
        presentation = presentations[presentation_id]
        
        # Generate Markdown
        markdown_content = generate_markdown_presentation(presentation)
        
        if not filename.endswith(".md"):
            filename = f"{filename}.md"
        
        with open(filename, 'w') as f:
            f.write(markdown_content)
        
        file_size = os.path.getsize(filename)
        
        return [types.TextContent(
            type="text",
            text=f"✅ Exported presentation as Markdown: {filename} ({file_size} bytes)\n" +
                 f"📝 Ready for GitHub, documentation, or further processing"
        )]
    except Exception as e:
        return [types.TextContent(
            type="text",
            text=f"❌ Error exporting to Markdown: {str(e)}"
        )]

async def handle_export_to_html(arguments: dict[str, Any]) -> list[types.TextContent]:
    """Export presentation as HTML slides."""
    try:
        presentation_id = arguments.get("presentation_id")
        filename = arguments.get("filename")
        theme = arguments.get("theme", "default")
        
        if presentation_id not in presentations:
            return [types.TextContent(
                type="text",
                text=f"❌ Presentation {presentation_id} not found"
            )]
        
        presentation = presentations[presentation_id]
        
        # Generate HTML
        html_content = generate_html_presentation(presentation, theme)
        
        if not filename.endswith(".html"):
            filename = f"{filename}.html"
        
        with open(filename, 'w') as f:
            f.write(html_content)
        
        file_size = os.path.getsize(filename)
        
        return [types.TextContent(
            type="text",
            text=f"✅ Exported presentation as HTML: {filename} ({file_size} bytes)\n" +
                 f"🌐 Theme: {theme} | Open in browser for slideshow"
        )]
    except Exception as e:
        return [types.TextContent(
            type="text",
            text=f"❌ Error exporting to HTML: {str(e)}"
        )]

async def handle_list_presentations(arguments: dict[str, Any]) -> list[types.TextContent]:
    """List all active presentations."""
    if not presentations:
        return [types.TextContent(
            type="text",
            text="📝 No active presentations"
        )]
    
    result = "📋 Active Lightweight Presentations:\n\n"
    for pid, presentation in presentations.items():
        result += f"🆔 ID: {pid}\n"
        result += f"📄 Title: {presentation.title}\n"
        result += f"📊 Slides: {len(presentation.slides)}\n"
        result += f"📏 Size: {presentation.slide_size}\n"
        result += f"⏰ Created: {presentation.created_at}\n"
        result += f"� Format: Lightweight JSON structure\n\n"
    
    return [types.TextContent(type="text", text=result)]

async def handle_create_presentation_from_prompt(arguments: dict[str, Any]) -> list[types.TextContent]:
    """Generate an entire presentation from a single LLM prompt."""
    try:
        prompt = arguments.get("prompt", "")
        slide_count = arguments.get("slide_count", 5)
        template = arguments.get("template", "business")
        
        # Generate presentation title from prompt
        title_prompt = f"Create a concise presentation title for: {prompt}"
        title = await call_llm_api(title_prompt, "title")
        
        # Create presentation
        presentation_id = str(uuid.uuid4())
        presentation = Presentation(
            id=presentation_id,
            title=title,
            template=template,
            slide_size="widescreen",
            slides=[],
            created_at=datetime.datetime.now().isoformat()
        )
        
        # Generate slides with LLM
        for i in range(slide_count):
            slide_prompt = f"Create slide {i+1} of {slide_count} for presentation about: {prompt}"
            slide_title = await call_llm_api(f"Title for {slide_prompt}", "title")
            slide_content = await call_llm_api(slide_prompt, "bullets")
            
            # Create slide
            slide = Slide(
                title=slide_title,
                layout="title_content",
                contents=[
                    SlideContent(
                        type="generated_text",
                        content=slide_content,
                        position={"x": 1, "y": 2, "width": 10, "height": 5},
                        style={"generated": True, "prompt": slide_prompt}
                    )
                ]
            )
            presentation.slides.append(slide)
        
        # Store presentation
        presentations[presentation_id] = presentation
        presentation_metadata[presentation_id] = asdict(presentation)
        
        return [types.TextContent(
            type="text",
            text=f"✅ Generated complete presentation: '{title}'\n" +
                 f"🆔 ID: {presentation_id}\n" +
                 f"📊 Slides: {slide_count}\n" +
                 f"🤖 Generated from prompt: {prompt[:100]}..."
        )]
    except Exception as e:
        return [types.TextContent(
            type="text",
            text=f"❌ Error generating presentation: {str(e)}"
        )]

async def handle_add_infographic(arguments: dict[str, Any]) -> list[types.TextContent]:
    """Add an ASCII-based infographic to a slide."""
    try:
        presentation_id = arguments.get("presentation_id")
        slide_index = arguments.get("slide_index", 0)
        infographic_type = arguments.get("infographic_type", "process")
        data = arguments.get("data", "")
        
        if presentation_id not in presentations:
            return [types.TextContent(
                type="text",
                text=f"❌ Presentation {presentation_id} not found"
            )]
        
        presentation = presentations[presentation_id]
        
        if slide_index >= len(presentation.slides):
            return [types.TextContent(
                type="text",
                text=f"❌ Slide index {slide_index} out of range"
            )]
        
        # Generate ASCII infographic
        infographic_content = generate_ascii_infographic(infographic_type, data)
        
        # Create infographic content
        content = SlideContent(
            type="infographic",
            content=infographic_content,
            position={"x": 1, "y": 1, "width": 10, "height": 6},
            style={"infographic_type": infographic_type, "data": data}
        )
        
        # Add to slide
        presentation.slides[slide_index].contents.append(content)
        
        # Update metadata
        presentation_metadata[presentation_id] = asdict(presentation)
        
        return [types.TextContent(
            type="text",
            text=f"✅ Added {infographic_type} infographic to slide {slide_index}\n" +
                 f"📊 Data: {data[:50]}...\n" +
                 f"🎨 Lightweight ASCII-based visualization created"
        )]
    except Exception as e:
        return [types.TextContent(
            type="text",
            text=f"❌ Error adding infographic: {str(e)}"
        )]

def generate_ascii_chart(chart_type: str, description: str) -> str:
    """Generate ASCII art chart representation."""
    if chart_type == "bar":
        return """
    ██████████ 100%
    ████████   80%
    ██████     60%
    ████       40%
    ██         20%
    ───────────────
    Q1 Q2 Q3 Q4
"""
    elif chart_type == "line":
        return """
    |     ●
    |   ●   ●
    | ●       ●
    |____________
    1  2  3  4  5
"""
    elif chart_type == "pie":
        return """
       ┌─●─┐
      ●     ●
     │   50% │
      ●     ●
       └─●─┘
"""
    else:
        return f"[{chart_type} chart: {description}]"

def generate_content_with_llm(prompt: str, content_type: str) -> str:
    """Generate content using LLM-style responses with enhanced templates."""
    # This can be replaced with actual LLM API calls
    return asyncio.run(call_llm_api(prompt, content_type))

def generate_markdown_presentation(presentation: Presentation) -> str:
    """Generate Markdown representation of presentation."""
    md_content = f"# {presentation.title}\n\n"
    md_content += f"*Created: {presentation.created_at}*\n"
    md_content += f"*Template: {presentation.template}*\n"
    md_content += f"*Size: {presentation.slide_size}*\n\n"
    md_content += "---\n\n"
    
    for i, slide in enumerate(presentation.slides):
        md_content += f"## Slide {i+1}: {slide.title}\n\n"
        md_content += f"*Layout: {slide.layout}*\n\n"
        
        for content in slide.contents:
            if content.type == "text" or content.type == "generated_text":
                md_content += f"{content.content}\n\n"
            elif content.type == "chart":
                md_content += f"```\n{content.content}\n```\n\n"
            else:
                md_content += f"*[{content.type}: {content.content[:50]}...]*\n\n"
        
        md_content += "---\n\n"
    
    return md_content

def generate_html_presentation(presentation: Presentation, theme: str) -> str:
    """Generate HTML representation of presentation."""
    theme_styles = {
        "default": "background: white; color: black; font-family: Arial, sans-serif;",
        "dark": "background: #1a1a1a; color: #f0f0f0; font-family: 'Segoe UI', sans-serif;",
        "minimal": "background: #fafafa; color: #333; font-family: 'Helvetica Neue', sans-serif;",
        "corporate": "background: #f8f9fa; color: #2c3e50; font-family: 'Times New Roman', serif;"
    }
    
    style = theme_styles.get(theme, theme_styles["default"])
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{presentation.title}</title>
    <style>
        body {{ {style} margin: 0; padding: 20px; }}
        .slide {{ 
            min-height: 500px; 
            padding: 40px; 
            margin-bottom: 50px; 
            border: 1px solid #ddd; 
            page-break-after: always;
        }}
        .slide-title {{ font-size: 2em; margin-bottom: 20px; font-weight: bold; }}
        .slide-content {{ font-size: 1.2em; line-height: 1.6; }}
        .chart {{ 
            background: #f5f5f5; 
            padding: 20px; 
            font-family: monospace; 
            white-space: pre-wrap; 
            border-radius: 5px;
        }}
        @media print {{ .slide {{ page-break-after: always; }} }}
    </style>
</head>
<body>
    <h1>{presentation.title}</h1>
    <p><em>Generated: {presentation.created_at}</em></p>
    <hr>
"""
    
    for i, slide in enumerate(presentation.slides):
        html_content += f"""
    <div class="slide">
        <div class="slide-title">Slide {i+1}: {slide.title}</div>
        <div class="slide-content">
"""
        
        for content in slide.contents:
            if content.type == "text" or content.type == "generated_text":
                html_content += f"<p>{content.content}</p>"
            elif content.type == "chart":
                html_content += f'<div class="chart">{content.content}</div>'
            else:
                html_content += f"<p><em>[{content.type}: {content.content[:50]}...]</em></p>"
        
        html_content += """
        </div>
    </div>
"""
    
    html_content += """
</body>
</html>
"""
    
    return html_content

def generate_ascii_infographic(infographic_type: str, data: str) -> str:
    """Generate ASCII-based infographics."""
    if infographic_type == "process":
        return f"""
🔄 PROCESS FLOW: {data}

Step 1 → Step 2 → Step 3 → Step 4
  ⬇️       ⬇️       ⬇️       ⬇️
[Init] → [Process] → [Review] → [Complete]
  📝       ⚙️        ✅        🎉
"""
    elif infographic_type == "comparison":
        return f"""
⚖️ COMPARISON: {data}

Option A          vs          Option B
┌─────────┐                  ┌─────────┐
│ Pros:   │                  │ Pros:   │
│ • Fast  │                  │ • Cheap │
│ • Easy  │       VS         │ • Simple│
│         │                  │         │
│ Cons:   │                  │ Cons:   │
│ • Cost  │                  │ • Slow  │
└─────────┘                  └─────────┘
"""
    elif infographic_type == "timeline":
        return f"""
📅 TIMELINE: {data}

Past ────●────●────●────●──── Future
      2020  2021  2022  2023
        │     │     │     │
     Start  Phase1 Phase2 Goal
        🚀    📈    ⚡    🎯
"""
    elif infographic_type == "hierarchy":
        return f"""
🏛️ HIERARCHY: {data}

         ┌─ CEO ─┐
         │       │
    ┌─ CTO ─┐ ┌─ CFO ─┐
    │       │ │       │
  Dev1   Dev2  Acc1  Acc2
   🧑‍💻    👩‍💻   📊    📈
"""
    else:
        return f"[{infographic_type} infographic: {data}]"

# LLM Integration helpers
async def call_llm_api(prompt: str, content_type: str = "text") -> str:
    """
    Call an actual LLM API for content generation.
    This is a placeholder that can be connected to OpenAI, Claude, or other LLM APIs.
    """
    # Example implementation that could be connected to real APIs:
    # import openai
    # response = await openai.ChatCompletion.acreate(...)
    # return response.choices[0].message.content
    
    # For now, return enhanced template-based content
    enhanced_templates = {
        "title": f"🎯 {prompt.title()}",
        "bullets": generate_bullet_points(prompt),
        "summary": f"📋 Executive Summary: {prompt}\n\nKey insights and strategic recommendations based on current market analysis and best practices.",
        "text": f"📝 {prompt}\n\nThis comprehensive overview addresses the core concepts, practical applications, and strategic implications for implementation.",
        "chart_description": f"📊 Chart Analysis: {prompt}\n\nData visualization showing trends, patterns, and key performance indicators."
    }
    return enhanced_templates.get(content_type, enhanced_templates["text"])

def generate_bullet_points(topic: str) -> str:
    """Generate structured bullet points for a given topic."""
    return f"""🔹 Key Benefits of {topic}:
   • Faster startup and execution
   • Reduced memory footprint
   • Simplified deployment
   • Enhanced performance

🔹 Implementation Strategy:
   • Leverage LLM for content generation
   • Use lightweight data structures
   • Implement efficient export formats
   • Maintain compatibility standards

🔹 Success Metrics:
   • Response time < 100ms
   • Memory usage < 50MB
   • Zero external dependencies
   • Cross-platform compatibility"""

async def main():
    # Run the server using stdin/stdout streams
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="slidecraft-mcp",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())
