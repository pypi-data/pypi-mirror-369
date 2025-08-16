#!/usr/bin/env python3
"""
SlideAgent - MCP server for presentation generation
"""

import sys
import json


def main():
    """Main entry point - starts MCP server directly"""
    
    # Only handle --help and config for user assistance
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        
        if arg in ['--help', '-h', 'help']:
            print("SlideAgent MCP Server")
            print("\nUsage:")
            print("  slideagent          Start MCP server")
            print("  slideagent --help   Show this help")
            print("  slideagent config   Show Claude Desktop configuration")
            print("\nThis is an MCP server for AI assistants like Claude Desktop.")
            print("All features are accessed through MCP tools, not CLI commands.")
            return 0
        
        elif arg == 'config':
            config = {
                "mcpServers": {
                    "slideagent": {
                        "command": "python",
                        "args": ["-m", "slideagent"],
                        "env": {}
                    }
                }
            }
            print("Add to Claude Desktop config:")
            print(json.dumps(config, indent=2))
            print("\nLocation: Claude Desktop → Settings → Developer → Edit Config")
            return 0
        
        # Ignore 'serve' for backwards compatibility but just start server
        elif arg != 'serve':
            print(f"Unknown option: {arg}")
            print("Run 'slideagent --help' for usage")
            return 1
    
    # Always just start the MCP server
    from .workspace import WorkspaceManager
    from .context import AgentContextManager
    
    # Auto-initialize workspace silently
    workspace = WorkspaceManager.get_or_create_workspace()
    if not (workspace / "CLAUDE.md").exists():
        AgentContextManager.deploy_all_contexts(workspace)
    
    # Start MCP server
    from .mcp.server import main as server_main
    return server_main()


if __name__ == "__main__":
    sys.exit(main())