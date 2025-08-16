"""Todo toolset main entry point"""

from .core import TodoToolSet

if __name__ == "__main__":
    import asyncio
    from pathlib import Path
    from ..utils.remote import serve_toolset_in_process
    
    async def main():
        toolset = TodoToolSet("todo", workspace_path=Path.cwd())
        await serve_toolset_in_process(toolset)
    
    asyncio.run(main())