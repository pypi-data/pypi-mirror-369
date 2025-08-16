"""Run File Editor Toolset as a standalone service"""

import asyncio
import sys
from pathlib import Path

from ..utils.remote import run_toolset
from .core import FileEditorToolSet


async def main():
    """Run the file editor toolset service"""
    # Get workspace path from command line or use current directory
    workspace_path = sys.argv[1] if len(sys.argv) > 1 else "."
    workspace_path = Path(workspace_path).resolve()
    
    print(f"Starting File Editor Toolset...")
    print(f"Workspace: {workspace_path}")
    
    # Create the toolset
    toolset = FileEditorToolSet("file_editor", workspace_path=workspace_path)
    
    # Run the service
    await run_toolset(toolset)


if __name__ == "__main__":
    asyncio.run(main())