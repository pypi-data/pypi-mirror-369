"""
Multi-agent context file management
"""

from pathlib import Path
from typing import Dict, List
import importlib.resources


class AgentContextManager:
    """Manages context files for different AI agents"""
    
    # Agent-specific context file names
    AGENT_FILES = {
        'claude': 'CLAUDE.md',
        'cursor': '.cursorrules',
        'gemini': 'GEMINI.md',
        'qwen': 'QWEN.md',
        'goose': '.goose',
        'windsurf': '.windsurfrules',
        'aider': '.aider',
        'default': 'AGENT.md'
    }
    
    @classmethod
    def get_base_content(cls, workspace_path: Path) -> str:
        """
        Generate base content for agent context files
        
        Args:
            workspace_path: Path to workspace directory
            
        Returns:
            Context file content
        """
        return f"""# SlideAgent Workspace

This folder contains all SlideAgent presentation projects.

## Current Location
Working directory: {workspace_path}

## Workspace Structure
```
slideagent_workspace/
├── [agent context files]
├── project-1/
│   ├── slides/         # HTML slides
│   ├── report_pages/   # Report pages
│   ├── plots/          # Generated charts
│   ├── theme/          # Project theme (copied)
│   └── input/          # Source materials
└── project-2/
    └── ...
```

## Available MCP Tools

### Project Management
- `create_project(name, theme)` - Create new presentation project
- `get_projects()` - List all projects

### Content Discovery
- `get_templates(type)` - List templates (slides/reports/charts/outlines)
- `get_themes()` - List available themes

### Content Generation
- `init_from_template(project, resource_type, name, template)` - Generate content
- `generate_pdf(project, format)` - Export to PDF
- `start_live_viewer(project, port)` - Preview presentation

### Theme Management
- `swap_theme(project, theme)` - Change project theme

## Quick Start

1. Create a project:
   ```
   create_project("my-presentation", theme="acme_corp")
   ```

2. Add slides:
   ```
   init_from_template(
       project="my-presentation",
       resource_type="slide",
       name="1",
       template="00_title_slide.html"
   )
   ```

3. Generate PDF:
   ```
   generate_pdf("my-presentation")
   ```

## Notes
- Projects are self-contained with copied themes
- All paths are relative within projects
- Node.js required for PDF generation and live preview
"""
    
    @classmethod
    def deploy_all_contexts(cls, workspace: Path) -> List[str]:
        """
        Deploy context files for all known agents
        
        Args:
            workspace: Workspace directory path
            
        Returns:
            List of created files
        """
        created_files = []
        
        # Try to load from package resources first
        try:
            # Get the base content from bundled resource
            with importlib.resources.open_text('slideagent.resources.contexts', 'AGENT.md') as f:
                base_content = f.read()
        except (FileNotFoundError, ModuleNotFoundError):
            # Fallback to generated content
            base_content = cls.get_base_content(workspace)
        
        for agent, filename in cls.AGENT_FILES.items():
            file_path = workspace / filename
            
            # Skip if already exists
            if file_path.exists():
                continue
            
            # Try to load agent-specific content
            try:
                with importlib.resources.open_text('slideagent.resources.contexts', filename) as f:
                    content = f.read()
            except (FileNotFoundError, ModuleNotFoundError):
                # Use base content as fallback
                content = base_content
            
            # Write context file
            file_path.write_text(content)
            created_files.append(filename)
            print(f"✓ Created {filename} for {agent}")
        
        return created_files
    
    @classmethod
    def ensure_context(cls, directory: Path = None) -> bool:
        """
        Ensure context files exist in directory
        
        Args:
            directory: Target directory (defaults to current)
            
        Returns:
            True if files were created, False if already existed
        """
        target_dir = directory or Path.cwd()
        created = cls.deploy_all_contexts(target_dir)
        return len(created) > 0