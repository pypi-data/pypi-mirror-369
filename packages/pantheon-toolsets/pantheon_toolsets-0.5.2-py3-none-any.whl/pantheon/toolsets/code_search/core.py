"""Code Search Toolset - Claude Code style file and content search capabilities"""

import os
import re
import subprocess
from pathlib import Path
from typing import Optional, List, Dict, Any
import glob
from ..utils.toolset import ToolSet, tool
from ..utils.log import logger


class CodeSearchToolSet(ToolSet):
    """
    Code Search Toolset with Claude Code-like search capabilities.
    
    This toolset provides file and content search functions similar to Claude Code:
    - Glob: File pattern matching and search
    - Grep: Content search within files (ripgrep-style)
    - LS: Enhanced directory listing
    """
    
    def __init__(
        self,
        name: str,
        workspace_path: str | Path | None = None,
        worker_params: dict | None = None,
        **kwargs,
    ):
        """
        Initialize the Code Search Toolset.
        
        Args:
            name: Name of the toolset
            workspace_path: Base directory for search operations (default: current directory)
            worker_params: Parameters for the worker
            **kwargs: Additional keyword arguments
        """
        super().__init__(name, worker_params, **kwargs)
        self.workspace_path = Path(workspace_path) if workspace_path else Path.cwd()
                
    def _resolve_path(self, path: str) -> Path:
        """Resolve path relative to workspace."""
        path_obj = Path(path)
        if path_obj.is_absolute():
            return path_obj
        return self.workspace_path / path_obj
    
    def _validate_path(self, path: str) -> tuple[bool, str, Path | None]:
        """
        Validate path for security and existence.
        
        Returns:
            tuple: (is_valid, error_message, resolved_path)
        """
        if '..' in path:
            return False, "Path cannot contain '..' for security reasons", None
            
        resolved_path = self._resolve_path(path)
        
        # Check if path is within workspace (allow some flexibility for searches)
        try:
            resolved_path.relative_to(self.workspace_path.parent)
        except ValueError:
            return False, f"Path must be within accessible area: {self.workspace_path.parent}", None
            
        return True, "", resolved_path

    @tool
    async def glob(
        self,
        pattern: str,
        path: str = ".",
        include_hidden: bool = False,
        max_results: int = 100
    ) -> dict:
        """
        Search for files using glob patterns (similar to Claude Code Glob tool).
        
        Args:
            pattern: Glob pattern (e.g., "*.py", "**/*.js", "src/**/*.tsx")
            path: Directory to search in (default: current directory)
            include_hidden: Whether to include hidden files/directories
            max_results: Maximum number of results to return
            
        Returns:
            dict with matching file paths
        """
        is_valid, error_msg, resolved_path = self._validate_path(path)
        if not is_valid:
            return {"success": False, "error": error_msg}
            
        if not resolved_path.exists():
            return {"success": False, "error": f"Directory not found: {path}"}
            
        if not resolved_path.is_dir():
            return {"success": False, "error": f"Path is not a directory: {path}"}
            
        try:
            logger.info(f"[cyan]Searching for pattern: {pattern} in {path}[/cyan]")
            
            # Use pathlib glob for pattern matching
            if '**' in pattern:
                # Recursive glob
                matches = list(resolved_path.rglob(pattern))
            else:
                # Non-recursive glob
                matches = list(resolved_path.glob(pattern))
            
            # Filter out hidden files if not requested
            if not include_hidden:
                matches = [m for m in matches if not any(part.startswith('.') for part in m.parts)]
            
            # Sort by modification time (newest first)
            matches.sort(key=lambda x: x.stat().st_mtime if x.exists() else 0, reverse=True)
            
            # Limit results
            matches = matches[:max_results]
            
            if matches:
                # Print results immediately to console
                logger.info("")
                logger.info(f"╭─ [bold green]Found {len(matches)} files matching '{pattern}'[/bold green] " + "─" * (50 - len(pattern)) + "╮")
                
                for match in matches:
                    try:
                        rel_path = match.relative_to(self.workspace_path)
                        file_type = "📁" if match.is_dir() else "📄"
                        logger.info(f"│ {file_type} [cyan]{rel_path}[/cyan]" + " " * (70 - len(str(rel_path))) + "│")
                    except ValueError:
                        # File outside workspace
                        logger.info(f"│ 📄 [cyan]{match}[/cyan]" + " " * (70 - len(str(match))) + "│")
                
                logger.info("╰" + "─" * 74 + "╯")
                logger.info(f"[green]✅ Found {len(matches)} matching files[/green]")
            else:
                logger.info("")
                logger.info(f"╭─ [bold yellow]No files found matching '{pattern}'[/bold yellow] " + "─" * (45 - len(pattern)) + "╮")
                logger.info("│ No matching files found in the specified directory" + " " * 23 + "│")
                logger.info("╰" + "─" * 74 + "╯")
                logger.info("[yellow]No matching files found[/yellow]")
            
            # Convert to string paths for return
            file_paths = []
            for match in matches:
                try:
                    rel_path = match.relative_to(self.workspace_path)
                    file_paths.append(str(rel_path))
                except ValueError:
                    file_paths.append(str(match))
            
            return {
                "success": True,
                "pattern": pattern,
                "search_path": str(resolved_path),
                "files": file_paths,
                "count": len(file_paths),
                "max_results": max_results
            }
            
        except Exception as e:
            return {"success": False, "error": f"Error during glob search: {str(e)}"}

    @tool
    async def grep(
        self,
        pattern: str,
        path: str = ".",
        file_pattern: str = "*",
        recursive: bool = True,
        case_sensitive: bool = True,
        regex: bool = False,
        context_lines: int = 2,
        max_results: int = 50
    ) -> dict:
        """
        Search for text within files (similar to Claude Code Grep tool).
        
        Args:
            pattern: Text pattern to search for
            path: Directory to search in OR specific file path (default: current directory)  
            file_pattern: File pattern to limit search (e.g., "*.py") or specific filename
            recursive: Whether to search recursively
            case_sensitive: Whether search is case-sensitive
            regex: Whether pattern is a regular expression
            context_lines: Number of context lines around matches
            max_results: Maximum number of matches to return
            
        Returns:
            dict with search results
        """
        is_valid, error_msg, resolved_path = self._validate_path(path)
        if not is_valid:
            return {"success": False, "error": error_msg}
            
        if not resolved_path.exists():
            return {"success": False, "error": f"Path not found: {path}"}
        
        # Check if path is a specific file
        is_single_file = resolved_path.is_file()
        if is_single_file:
            # For single file search, set file_pattern to match this file
            file_pattern = resolved_path.name
            resolved_path = resolved_path.parent
            recursive = False
            
        try:
            # Show search status
            logger.info(f"[cyan]Searching for '{pattern}' in files matching '{file_pattern}'[/cyan]")
            
            # Debug info
            logger.info(f"[dim]Search path: {resolved_path}, recursive: {recursive}[/dim]")
            
            # Find files to search
            if recursive:
                if file_pattern == "*":
                    files = list(resolved_path.rglob("*"))
                else:
                    files = list(resolved_path.rglob(file_pattern))
            else:
                if file_pattern == "*":
                    files = list(resolved_path.glob("*"))
                else:
                    files = list(resolved_path.glob(file_pattern))
            
            # Filter to only text files
            logger.info(f"[dim]Scanning {len(files)} files...[/dim]")
            
            text_files = []
            for f in files:
                if f.is_file():
                    try:
                        # Try to read a small portion to check if it's text
                        with open(f, 'r', encoding='utf-8', errors='ignore') as test_file:
                            test_file.read(100)
                        text_files.append(f)
                    except:
                        continue
            
            logger.info(f"[dim]Found {len(text_files)} text files to search[/dim]")
            
            matches = []
            total_matches = 0
            
            # Compile regex if needed
            if regex:
                flags = 0 if case_sensitive else re.IGNORECASE
                try:
                    compiled_pattern = re.compile(pattern, flags)
                except re.error as e:
                    return {"success": False, "error": f"Invalid regex pattern: {str(e)}"}
            else:
                search_pattern = pattern if case_sensitive else pattern.lower()
            
            # Search through files
            for file_path in text_files:
                if total_matches >= max_results:
                    break
                    
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()
                    
                    file_matches = []
                    for line_no, line in enumerate(lines, 1):
                        if total_matches >= max_results:
                            break
                            
                        line_to_search = line if case_sensitive else line.lower()
                        
                        # Check for match
                        match_found = False
                        if regex:
                            match_found = bool(compiled_pattern.search(line))
                        else:
                            match_found = search_pattern in line_to_search
                        
                        if match_found:
                            # Get context lines
                            start = max(0, line_no - context_lines - 1)
                            end = min(len(lines), line_no + context_lines)
                            
                            context = []
                            for i in range(start, end):
                                prefix = ">>>" if i == line_no - 1 else "   "
                                context.append({
                                    "line_no": i + 1,
                                    "content": lines[i].rstrip(),
                                    "is_match": i == line_no - 1
                                })
                            
                            file_matches.append({
                                "line_number": line_no,
                                "line": line.rstrip(),
                                "context": context
                            })
                            total_matches += 1
                    
                    if file_matches:
                        try:
                            rel_path = file_path.relative_to(self.workspace_path)
                        except ValueError:
                            rel_path = file_path
                            
                        matches.append({
                            "file": str(rel_path),
                            "matches": file_matches
                        })
                        
                except Exception:
                    continue  # Skip files that can't be read
            
            # Print results
            if matches:
                logger.info("")
                logger.info(f"╭─ [bold green]Found {total_matches} matches for '{pattern}'[/bold green] " + "─" * (40 - len(pattern)) + "╮")
                
                for file_match in matches:
                    logger.info(f"│ 📄 [bold cyan]{file_match['file']}[/bold cyan]" + " " * (70 - len(file_match['file'])) + "│")
                    
                    for match in file_match['matches'][:3]:  # Show max 3 matches per file in display
                        highlighted_line = match['line'][:60] + ('...' if len(match['line']) > 60 else '')
                        logger.info(f"│   [dim]Line {match['line_number']}:[/dim] {highlighted_line}" + " " * (70 - min(60, len(match['line'])) - len(str(match['line_number'])) - 8) + "│")
                    
                    if len(file_match['matches']) > 3:
                        logger.info(f"│   [dim]... and {len(file_match['matches']) - 3} more matches[/dim]" + " " * 40 + "│")
                
                logger.info("╰" + "─" * 74 + "╯")
                logger.info(f"[green]✅ Found {total_matches} matches in {len(matches)} files[/green]")
            else:
                logger.info(f"╭─ [bold yellow]No matches found for '{pattern}'[/bold yellow] " + "─" * (45 - len(pattern)) + "╮")
                logger.info("│ No matching content found in the specified files" + " " * 25 + "│")
                logger.info("╰" + "─" * 74 + "╯")
                logger.info("[yellow]No matches found[/yellow]")
            
            return {
                "success": True,
                "pattern": pattern,
                "search_path": str(resolved_path),
                "file_pattern": file_pattern,
                "matches": matches,
                "total_matches": total_matches,
                "files_searched": len(text_files)
            }
            
        except Exception as e:
            return {"success": False, "error": f"Error during grep search: {str(e)}"}

    @tool
    async def ls(
        self,
        path: str = ".",
        show_hidden: bool = False,
        show_details: bool = False,
        recursive: bool = False
    ) -> dict:
        """
        Enhanced directory listing (similar to Claude Code LS tool).
        
        Args:
            path: Directory path to list (default: current directory)
            show_hidden: Whether to show hidden files/directories
            show_details: Whether to show file sizes and modification times
            recursive: Whether to list recursively
            
        Returns:
            dict with directory contents
        """
        is_valid, error_msg, resolved_path = self._validate_path(path)
        if not is_valid:
            return {"success": False, "error": error_msg}
            
        if not resolved_path.exists():
            return {"success": False, "error": f"Directory not found: {path}"}
            
        if not resolved_path.is_dir():
            return {"success": False, "error": f"Path is not a directory: {path}"}
            
        try:
            
            # Get directory contents
            if recursive:
                items = list(resolved_path.rglob("*"))
            else:
                items = list(resolved_path.glob("*"))
            
            # Filter hidden files
            if not show_hidden:
                items = [item for item in items if not any(part.startswith('.') for part in item.parts[len(resolved_path.parts):])]
            
            # Sort: directories first, then files
            items.sort(key=lambda x: (not x.is_dir(), x.name.lower()))
            
            # Print results
            display_path = resolved_path.name if resolved_path.name else str(resolved_path)
            logger.info("")
            logger.info(f"╭─ [bold cyan]Directory: {display_path}[/bold cyan] " + "─" * (60 - len(display_path)) + "╮")
            
            if not items:
                logger.info("│ [yellow]Empty directory[/yellow]" + " " * 45 + "│")
            else:
                for item in items:
                    try:
                        rel_path = item.relative_to(resolved_path)
                        
                        if item.is_dir():
                            icon = "📁"
                            color = "[bold cyan]"
                            size_info = ""
                        else:
                            icon = "📄"
                            color = "[white]"
                            if show_details:
                                size = item.stat().st_size
                                if size < 1024:
                                    size_info = f" [dim]({size}B)[/dim]"
                                elif size < 1024 * 1024:
                                    size_info = f" [dim]({size//1024}KB)[/dim]"
                                else:
                                    size_info = f" [dim]({size//(1024*1024)}MB)[/dim]"
                            else:
                                size_info = ""
                        
                        display_name = str(rel_path)
                        if recursive and len(str(rel_path)) > 50:
                            display_name = "..." + str(rel_path)[-47:]
                        
                        padding = max(0, 65 - len(display_name) - len(size_info.replace('[dim]', '').replace('[/dim]', '').replace('(', '').replace(')', '').replace('B', '').replace('K', '').replace('M', '')))
                        logger.info(f"    {icon} {color}{display_name}[/{color.split('[')[1].split(']')[0]}]{size_info}")
                        
                    except ValueError:
                        continue
            
            logger.info("╰" + "─" * 75 + "╯")
            logger.info(f"[green]📂 Listed {len(items)} items[/green]")
            
            # Prepare return data
            file_list = []
            for item in items:
                try:
                    rel_path = item.relative_to(resolved_path)
                    file_info = {
                        "path": str(rel_path),
                        "type": "directory" if item.is_dir() else "file",
                        "size": item.stat().st_size if item.is_file() else None
                    }
                    file_list.append(file_info)
                except:
                    continue
            
            return {
                "success": True,
                "directory": str(resolved_path),
                "files": file_list,
                "count": len(file_list),
                "show_hidden": show_hidden,
                "recursive": recursive
            }
            
        except Exception as e:
            return {"success": False, "error": f"Error listing directory: {str(e)}"}