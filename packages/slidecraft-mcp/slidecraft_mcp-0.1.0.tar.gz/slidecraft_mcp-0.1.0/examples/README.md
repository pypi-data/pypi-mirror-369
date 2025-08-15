# PowerPoint MCP Server Examples

This directory contains examples of how to use the PowerPoint MCP Server tools.

## Basic Usage Example

Here's a step-by-step example of creating a presentation:

### 1. Create a New Presentation

```json
{
  "tool": "create_presentation",
  "arguments": {
    "title": "My Business Report",
    "template": "business",
    "slide_size": "widescreen"
  }
}
```

Response:
```
Created presentation 'My Business Report' with ID: abc123-def456-ghi789
```

### 2. Add a Title Slide

```json
{
  "tool": "add_slide",
  "arguments": {
    "presentation_id": "abc123-def456-ghi789",
    "layout": "title",
    "title": "Q4 Business Review"
  }
}
```

### 3. Add Content Slides

```json
{
  "tool": "add_slide",
  "arguments": {
    "presentation_id": "abc123-def456-ghi789",
    "layout": "title_content",
    "title": "Sales Performance"
  }
}
```

### 4. Add Text Content

```json
{
  "tool": "add_text",
  "arguments": {
    "presentation_id": "abc123-def456-ghi789",
    "slide_number": 1,
    "text": "Sales increased by 25% in Q4",
    "position": {
      "x": 1,
      "y": 2,
      "width": 8,
      "height": 1
    },
    "font_size": 24,
    "bold": true
  }
}
```

### 5. Create a Chart

```json
{
  "tool": "create_chart",
  "arguments": {
    "presentation_id": "abc123-def456-ghi789",
    "slide_number": 1,
    "chart_type": "bar",
    "data": {
      "labels": ["Q1", "Q2", "Q3", "Q4"],
      "values": [100, 120, 110, 150]
    },
    "title": "Quarterly Sales (in thousands)",
    "position": {
      "x": 1,
      "y": 3,
      "width": 8,
      "height": 4
    }
  }
}
```

### 6. Add an Image

```json
{
  "tool": "add_image",
  "arguments": {
    "presentation_id": "abc123-def456-ghi789",
    "slide_number": 2,
    "image_source": "https://example.com/company-logo.png",
    "position": {
      "x": 8,
      "y": 1,
      "width": 2,
      "height": 1.5
    },
    "alt_text": "Company Logo"
  }
}
```

### 7. Add a QR Code

```json
{
  "tool": "generate_qr_code",
  "arguments": {
    "presentation_id": "abc123-def456-ghi789",
    "slide_number": 2,
    "data": "https://company.com/q4-report",
    "position": {
      "x": 8.5,
      "y": 6,
      "size": 1.5
    }
  }
}
```

### 8. Save the Presentation

```json
{
  "tool": "save_presentation",
  "arguments": {
    "presentation_id": "abc123-def456-ghi789",
    "filename": "Q4_Business_Review",
    "format": "pptx"
  }
}
```

## Advanced Examples

### Creating an Infographic-Style Slide

```json
{
  "tool": "add_slide",
  "arguments": {
    "presentation_id": "abc123-def456-ghi789",
    "layout": "blank"
  }
}
```

```json
{
  "tool": "add_text",
  "arguments": {
    "presentation_id": "abc123-def456-ghi789",
    "slide_number": 3,
    "text": "Key Metrics",
    "position": {"x": 1, "y": 0.5, "width": 12, "height": 1},
    "font_size": 36,
    "bold": true
  }
}
```

```json
{
  "tool": "create_chart",
  "arguments": {
    "presentation_id": "abc123-def456-ghi789",
    "slide_number": 3,
    "chart_type": "pie",
    "data": {
      "labels": ["Desktop", "Mobile", "Tablet"],
      "values": [60, 35, 5]
    },
    "title": "Traffic Sources",
    "position": {"x": 0.5, "y": 2, "width": 4, "height": 4}
  }
}
```

```json
{
  "tool": "create_chart",
  "arguments": {
    "presentation_id": "abc123-def456-ghi789",
    "slide_number": 3,
    "chart_type": "line",
    "data": {
      "labels": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
      "values": [1000, 1200, 1100, 1400, 1300, 1600]
    },
    "title": "Monthly Growth",
    "position": {"x": 5, "y": 2, "width": 4, "height": 4}
  }
}
```

### Educational Presentation Example

```json
{
  "tool": "create_presentation",
  "arguments": {
    "title": "Introduction to Machine Learning",
    "template": "modern",
    "slide_size": "widescreen"
  }
}
```

```json
{
  "tool": "add_slide",
  "arguments": {
    "presentation_id": "presentation_id_here",
    "layout": "title_content",
    "title": "What is Machine Learning?"
  }
}
```

```json
{
  "tool": "add_text",
  "arguments": {
    "presentation_id": "presentation_id_here",
    "slide_number": 0,
    "text": "Machine Learning is a subset of artificial intelligence that enables computers to learn and make decisions from data without being explicitly programmed.",
    "position": {"x": 1, "y": 2, "width": 10, "height": 3},
    "font_size": 20
  }
}
```

## Error Handling

The MCP server includes comprehensive error handling. Common errors include:

- **Presentation not found**: Make sure to use the correct presentation ID
- **Slide number out of range**: Verify the slide exists before adding content
- **Invalid image source**: Ensure URLs are accessible or file paths exist
- **Chart data mismatch**: Labels and values arrays must have the same length

## Tips and Best Practices

1. **Positioning**: Use the coordinate system where (0,0) is top-left, measurements in inches
2. **Image Sources**: Support URLs, file paths, and base64 encoded data
3. **Chart Types**: Choose appropriate chart types for your data (bar, line, pie, scatter, area)
4. **Layout Planning**: Plan slide layouts before adding content for better results
5. **File Management**: The server automatically manages temporary files for images and charts

## Template and Layout Options

### Available Templates
- `blank`: Empty presentation
- `business`: Professional business template
- `modern`: Modern design template
- `classic`: Traditional presentation template

### Available Layouts
- `title`: Title slide with centered title and subtitle
- `title_content`: Title with content area below
- `content`: Content-focused layout
- `blank`: Empty slide for custom layouts
- `two_content`: Two content areas side by side

## Integration with Claude

When using with Claude Desktop, you can ask natural language questions like:

- "Create a presentation about quarterly sales with charts"
- "Add a slide with our company logo and contact QR code"
- "Generate a pie chart showing market share data"
- "Save the presentation as a PDF file"

The MCP server will translate these requests into the appropriate tool calls automatically.
