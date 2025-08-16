# SlideAgent

MCP server for AI-powered presentation generation. Create professional slides, charts, and PDFs with Claude Desktop and other AI assistants.

## Features

- 🎨 **Professional Themes** - Multiple built-in themes (acme_corp, barney, pokemon)
- 📊 **Integrated Charts** - Create charts with matplotlib, auto-styled to match themes
- 📄 **PDF Export** - Generate PDFs in slide (16:9) or report (8.5x11) format
- 🤖 **AI Integration** - Works with Claude Desktop via MCP (Model Context Protocol)
- 🔄 **Auto-workspace** - Automatically manages projects in current directory

## Quick Start

### 1. Install

```bash
pip install slideagent
```

### 2. Configure Claude Desktop

Get the configuration:
```bash
python -m slideagent config
```

Add to Claude Desktop settings (Developer → Edit Config):
```json
{
  "mcpServers": {
    "slideagent": {
      "command": "python",
      "args": ["-m", "slideagent"],
      "env": {}
    }
  }
}
```

### 3. Use in Claude

```
Create a presentation called "Q4-results" with:
- Title slide "Q4 Financial Results"
- Bullet points with key metrics
- A revenue chart
- Conclusion slide
```

## How It Works

SlideAgent is an MCP server that:
1. Runs in the background when Claude Desktop connects
2. Creates a `slideagent_workspace/` in your current directory
3. Manages projects with self-contained themes and assets
4. Generates HTML slides that can be exported to PDF

## MCP Tools Available

- `create_project(name, theme)` - Create new presentation
- `get_templates(type)` - List templates (slides/reports/charts/outlines)
- `init_from_template(...)` - Create content from templates
- `generate_pdf(project)` - Export to PDF
- `start_live_viewer(project)` - Preview slides in browser

## Requirements

- Python 3.8+
- Node.js (for PDF generation)
- Claude Desktop or other MCP-compatible AI assistant

## Project Structure

```
your_folder/
└── slideagent_workspace/      # Auto-created
    ├── CLAUDE.md              # AI context files
    ├── project_name/          # Your presentations
    │   ├── slides/           # HTML slides
    │   ├── theme/            # CSS and assets
    │   ├── plots/            # Charts
    │   └── project.pdf       # Generated PDF
```

## Documentation

For detailed documentation, examples, and troubleshooting, visit:
[https://github.com/flong28/slideagent](https://github.com/flong28/slideagent)

## License

MIT License - See LICENSE file for details.