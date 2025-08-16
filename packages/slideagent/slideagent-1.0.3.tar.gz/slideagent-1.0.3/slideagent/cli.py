#!/usr/bin/env python3
"""
Enhanced CLI commands for SlideAgent
"""

import sys
import json
import subprocess
from pathlib import Path
from typing import Optional

from .workspace import WorkspaceManager
from .context import AgentContextManager
from . import __version__


def cmd_init(args=None):
    """Initialize workspace in current directory"""
    workspace = WorkspaceManager.ensure_workspace()
    AgentContextManager.deploy_all_contexts(workspace)
    print(f"✓ SlideAgent workspace initialized at: {workspace}")
    print(f"  Created AI context files for Claude, Cursor, Gemini, etc.")
    print(f"\nNext steps:")
    print(f"  1. Run 'slideagent serve' to start MCP server")
    print(f"  2. Or use 'slideagent new <name>' to create a project")
    return 0


def cmd_serve(args=None):
    """Start the MCP server"""
    from .mcp.server import main as server_main
    
    # Auto-init if needed
    workspace = WorkspaceManager.get_or_create_workspace()
    if not (workspace / "CLAUDE.md").exists():
        AgentContextManager.deploy_all_contexts(workspace)
    
    return server_main()


def cmd_new(args):
    """Create a new project"""
    if not args or len(args) < 1:
        print("Error: Project name required")
        print("Usage: slideagent new <project-name> [--theme <theme>]")
        return 1
    
    project_name = args[0]
    theme = "acme_corp"
    
    # Parse theme if provided
    if "--theme" in args:
        idx = args.index("--theme")
        if idx + 1 < len(args):
            theme = args[idx + 1]
    
    workspace = WorkspaceManager.get_or_create_workspace()
    project = WorkspaceManager.create_project(project_name, workspace)
    
    # Import server to use its functions
    from .mcp import server
    result = server.create_project(project_name, theme=theme)
    print(result)
    
    print(f"\nProject created at: {project}")
    print(f"Theme: {theme}")
    print(f"\nNext steps:")
    print(f"  1. cd {project}")
    print(f"  2. Add slides with 'slideagent serve' and MCP tools")
    print(f"  3. Generate PDF with 'slideagent pdf {project_name}'")
    return 0


def cmd_list(args=None):
    """List all projects in workspace"""
    workspace = WorkspaceManager.find_workspace()
    if not workspace:
        print("No workspace found. Run 'slideagent init' first.")
        return 1
    
    projects = []
    if workspace.exists():
        for item in workspace.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                # Check if it's a project (has slides or theme folder)
                if (item / "slides").exists() or (item / "theme").exists():
                    projects.append(item.name)
    
    if projects:
        print(f"Projects in {workspace}:\n")
        for project in sorted(projects):
            project_dir = workspace / project
            slide_count = len(list((project_dir / "slides").glob("*.html"))) if (project_dir / "slides").exists() else 0
            has_pdf = (project_dir / f"{project}.pdf").exists()
            pdf_marker = " [PDF]" if has_pdf else ""
            print(f"  • {project} ({slide_count} slides){pdf_marker}")
    else:
        print("No projects found. Create one with 'slideagent new <name>'")
    
    return 0


def cmd_config(args=None):
    """Show MCP configuration for Claude Desktop"""
    config = {
        "mcpServers": {
            "slideagent": {
                "command": "uv",
                "args": ["run", "python", "-m", "slideagent", "serve"],
                "env": {}
            }
        }
    }
    
    print("Add this to your Claude Desktop configuration:\n")
    print(json.dumps(config, indent=2))
    print("\nLocation: Claude Desktop → Settings → Developer → Edit Config")
    return 0


def cmd_version(args=None):
    """Show version information"""
    print(f"SlideAgent v{__version__}")
    print(f"Python: {sys.version.split()[0]}")
    
    # Check Node.js
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True)
        node_version = result.stdout.strip()
        print(f"Node.js: {node_version}")
    except:
        print("Node.js: Not installed (required for PDF generation)")
    
    # Check uv
    try:
        result = subprocess.run(["uv", "--version"], capture_output=True, text=True)
        uv_version = result.stdout.strip()
        print(f"uv: {uv_version}")
    except:
        print("uv: Not installed (recommended for faster installs)")
    
    return 0


def cmd_help(args=None):
    """Show help information"""
    print("SlideAgent - Professional presentation generator")
    print(f"Version {__version__}")
    print()
    print("Usage: slideagent <command> [options]")
    print()
    print("Commands:")
    print("  init         Initialize workspace in current directory")
    print("  serve        Start MCP server for AI agents")
    print("  new <name>   Create a new presentation project")
    print("  list         List all projects in workspace")
    print("  config       Show MCP configuration for Claude Desktop")
    print("  version      Show version information")
    print("  help         Show this help message")
    print()
    print("Examples:")
    print("  slideagent init                    # Initialize workspace")
    print("  slideagent new q4-results           # Create new project")
    print("  slideagent new demo --theme barney  # Create with specific theme")
    print("  slideagent serve                    # Start MCP server")
    print()
    print("For more information, see SETUP_INSTRUCTIONS.md")
    return 0


def main():
    """Enhanced CLI entry point"""
    args = sys.argv[1:] if len(sys.argv) > 1 else []
    
    if not args:
        # Default to serve
        return cmd_serve()
    
    command = args[0].lower()
    command_args = args[1:] if len(args) > 1 else []
    
    commands = {
        'init': cmd_init,
        'serve': cmd_serve,
        'new': cmd_new,
        'list': cmd_list,
        'config': cmd_config,
        'version': cmd_version,
        'help': cmd_help,
        '--help': cmd_help,
        '-h': cmd_help,
    }
    
    if command in commands:
        return commands[command](command_args)
    else:
        print(f"Unknown command: {command}")
        print("Run 'slideagent help' for usage information")
        return 1


if __name__ == "__main__":
    sys.exit(main())