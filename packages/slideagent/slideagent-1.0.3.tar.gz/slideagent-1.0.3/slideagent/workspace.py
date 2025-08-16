"""
Workspace management for SlideAgent projects
"""

from pathlib import Path
from typing import Optional
import shutil


class WorkspaceManager:
    """Manages SlideAgent workspace and project directories"""
    
    WORKSPACE_NAME = "slideagent_workspace"
    
    @classmethod
    def ensure_workspace(cls, base_dir: Path = None) -> Path:
        """
        Ensure workspace exists and return path
        
        Args:
            base_dir: Base directory for workspace. Defaults to current directory.
            
        Returns:
            Path to workspace directory
        """
        base = base_dir or Path.cwd()
        workspace = base / cls.WORKSPACE_NAME
        
        if not workspace.exists():
            workspace.mkdir(parents=True, exist_ok=True)
            print(f"Created SlideAgent workspace at: {workspace}")
        
        return workspace
    
    @classmethod
    def find_workspace(cls, start_dir: Path = None) -> Optional[Path]:
        """
        Find existing workspace in current or parent directories
        
        Args:
            start_dir: Directory to start search from
            
        Returns:
            Path to workspace if found, None otherwise
        """
        current = start_dir or Path.cwd()
        
        # Check current directory
        workspace = current / cls.WORKSPACE_NAME
        if workspace.exists():
            return workspace
        
        # Check if we're already inside a workspace
        for parent in current.parents:
            if parent.name == cls.WORKSPACE_NAME:
                return parent
            workspace = parent / cls.WORKSPACE_NAME
            if workspace.exists():
                return workspace
        
        return None
    
    @classmethod
    def get_or_create_workspace(cls, base_dir: Path = None) -> Path:
        """
        Get existing workspace or create new one
        
        Args:
            base_dir: Base directory for workspace
            
        Returns:
            Path to workspace directory
        """
        existing = cls.find_workspace(base_dir)
        if existing:
            # Silently return existing workspace - no need to spam output
            return existing
        
        return cls.ensure_workspace(base_dir)
    
    @classmethod
    def create_project(cls, name: str, workspace: Path = None) -> Path:
        """
        Create a new project in the workspace
        
        Args:
            name: Project name
            workspace: Workspace directory (will find/create if not provided)
            
        Returns:
            Path to created project directory
        """
        if workspace is None:
            workspace = cls.get_or_create_workspace()
        
        project_dir = workspace / name
        
        if project_dir.exists():
            print(f"Project '{name}' already exists at: {project_dir}")
            return project_dir
        
        # Create project structure
        project_dir.mkdir(parents=True, exist_ok=True)
        (project_dir / "slides").mkdir(exist_ok=True)
        (project_dir / "report_pages").mkdir(exist_ok=True)
        (project_dir / "plots").mkdir(exist_ok=True)
        (project_dir / "input").mkdir(exist_ok=True)
        (project_dir / "theme").mkdir(exist_ok=True)
        
        print(f"Created project: {project_dir}")
        return project_dir