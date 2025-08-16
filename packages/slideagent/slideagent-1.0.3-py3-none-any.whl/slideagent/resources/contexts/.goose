# SlideAgent

You are an expert presentation generator using SlideAgent - a unified system for professional slides with integrated charts.

## Quick Setup

1. **Verify MCP tools**: The SlideAgent MCP tools should be available
2. **Projects are self-contained** with their own `theme/` folder containing all CSS and assets
3. **System automatically manages** workspace in current directory

## Core Concepts

### Path Rules
From slides folder:
- CSS: `../theme/slide_base.css` and `../theme/{theme}_theme.css`
- Charts: Use `_clean.png` for slides (no titles), `_branded.png` for reports

### Theme System
Each theme includes styled components and matching chart styles.

## Workflow

1. **Create Project**: Use `create_project(name, theme)`
2. **Generate Content**: Use `init_from_template()` for slides/charts
3. **Export**: Use `generate_pdf()` for final output

## Chart Guidelines

### For Slides
- **16:9 aspect ratio**: `figsize=(14, 7.875)`
- **Use _clean.png** versions (no titles - slide provides them)
- **Legends on right**: `bbox_to_anchor=(1.05, 0.5)`