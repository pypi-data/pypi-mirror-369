"""
Node.js helper utilities for SlideAgent
"""

import subprocess
import shutil
from pathlib import Path
import importlib.resources


class NodeHelper:
    """Helper class for Node.js operations"""
    
    @staticmethod
    def ensure_node() -> bool:
        """
        Check if Node.js is installed
        
        Returns:
            True if Node.js is available
            
        Raises:
            RuntimeError: If Node.js is not installed
        """
        if not shutil.which('node'):
            raise RuntimeError(
                "Node.js is required for SlideAgent.\n"
                "Please install from: https://nodejs.org/"
            )
        
        # Check npm too
        if not shutil.which('npm'):
            raise RuntimeError(
                "npm is required for SlideAgent.\n"
                "It should come with Node.js installation."
            )
        
        return True
    
    @staticmethod
    def get_js_dir() -> Path:
        """Get the JS resources directory"""
        # Try to get from package resources
        try:
            if hasattr(importlib.resources, 'files'):
                js_dir = importlib.resources.files('slideagent.resources.js')
            else:
                # Fallback for older Python
                from .. import PACKAGE_DIR
                js_dir = PACKAGE_DIR / 'resources' / 'js'
            
            # Convert to Path if needed
            if not isinstance(js_dir, Path):
                js_dir = Path(str(js_dir))
            
            return js_dir
        except Exception:
            # Ultimate fallback
            from .. import PACKAGE_DIR
            return PACKAGE_DIR / 'resources' / 'js'
    
    @staticmethod
    def ensure_dependencies() -> bool:
        """
        Install npm packages if not already installed
        
        Returns:
            True if dependencies are ready
        """
        NodeHelper.ensure_node()
        
        js_dir = NodeHelper.get_js_dir()
        node_modules = js_dir / 'node_modules'
        
        if not node_modules.exists():
            print("First run: Installing Node.js dependencies...")
            print(f"Installing in: {js_dir}")
            
            try:
                result = subprocess.run(
                    ['npm', 'install'],
                    cwd=str(js_dir),
                    capture_output=True,
                    text=True,
                    check=True
                )
                print("✓ Dependencies installed successfully!")
                return True
            except subprocess.CalledProcessError as e:
                print(f"Error installing dependencies: {e}")
                print(f"stderr: {e.stderr}")
                raise RuntimeError(f"Failed to install npm dependencies: {e.stderr}")
        
        return True
    
    @staticmethod
    def run_js_file(js_file: Path, args: list = None) -> subprocess.CompletedProcess:
        """
        Run a JavaScript file with Node.js
        
        Args:
            js_file: Path to JavaScript file
            args: Additional arguments to pass
            
        Returns:
            Completed process result
        """
        NodeHelper.ensure_dependencies()
        
        cmd = ['node', str(js_file)]
        if args:
            cmd.extend(args)
        
        return subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )