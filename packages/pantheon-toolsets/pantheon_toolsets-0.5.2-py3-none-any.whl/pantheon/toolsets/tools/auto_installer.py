"""Universal software detection and installation system"""

import os
import platform
import subprocess
import shutil
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from ..utils.log import logger
from rich.prompt import Confirm
from rich.table import Table


class PackageManager:
    """Base class for package managers"""
    
    def __init__(self, name: str, check_cmd: str):
        self.name = name
        self.check_cmd = check_cmd
    
    def is_available(self) -> bool:
        """Check if this package manager is available"""
        return shutil.which(self.check_cmd.split()[0]) is not None
    
    def search_package(self, tool_name: str) -> List[str]:
        """Search for packages matching the tool name"""
        raise NotImplementedError
    
    def install_package(self, package_name: str) -> bool:
        """Install a package"""
        raise NotImplementedError

class CondaManager(PackageManager):
    def __init__(self):
        # Prefer mamba over conda if available
        cmd = 'mamba' if shutil.which('mamba') else 'conda'
        super().__init__('conda/mamba', cmd)
    
    def search_package(self, tool_name: str) -> List[str]:
        """Search conda packages"""
        try:
            result = subprocess.run(
                [self.check_cmd, 'search', '-c', 'bioconda', '-c', 'conda-forge', tool_name],
                capture_output=True, text=True, timeout=30
            )
            if result.returncode == 0:
                # Parse output to find exact matches
                packages = []
                for line in result.stdout.split('\n'):
                    if line.strip() and not line.startswith('#') and tool_name.lower() in line.lower():
                        packages.append(f"conda: {line.split()[0]}")
                return packages[:3]  # Return top 3 matches
        except Exception:
            pass
        return []
    
    def install_package(self, package_name: str) -> bool:
        """Install conda package"""
        try:
            cmd = [self.check_cmd, 'install', '-c', 'bioconda', '-c', 'conda-forge', package_name, '-y']
            result = subprocess.run(cmd, timeout=300)
            return result.returncode == 0
        except Exception:
            return False

class BrewManager(PackageManager):
    def __init__(self):
        super().__init__('homebrew', 'brew')
    
    def search_package(self, tool_name: str) -> List[str]:
        """Search homebrew packages"""
        try:
            result = subprocess.run(
                ['brew', 'search', tool_name], capture_output=True, text=True, timeout=30
            )
            if result.returncode == 0:
                packages = []
                for line in result.stdout.split('\n'):
                    if line.strip() and tool_name.lower() in line.lower():
                        packages.append(f"brew: {line.strip()}")
                return packages[:3]
        except Exception:
            pass
        return []
    
    def install_package(self, package_name: str) -> bool:
        """Install brew package"""
        try:
            result = subprocess.run(['brew', 'install', package_name], timeout=300)
            return result.returncode == 0
        except Exception:
            return False

class AptManager(PackageManager):
    def __init__(self):
        super().__init__('apt', 'apt')
    
    def search_package(self, tool_name: str) -> List[str]:
        """Search apt packages"""
        try:
            result = subprocess.run(
                ['apt', 'search', tool_name], capture_output=True, text=True, timeout=30
            )
            if result.returncode == 0:
                packages = []
                for line in result.stdout.split('\n'):
                    if '/' in line and tool_name.lower() in line.lower():
                        pkg_name = line.split('/')[0]
                        packages.append(f"apt: {pkg_name}")
                return packages[:3]
        except Exception:
            pass
        return []
    
    def install_package(self, package_name: str) -> bool:
        """Install apt package"""
        try:
            result = subprocess.run(['sudo', 'apt', 'install', '-y', package_name], timeout=300)
            return result.returncode == 0
        except Exception:
            return False

class PipManager(PackageManager):
    def __init__(self):
        super().__init__('pip', 'pip')
    
    def search_package(self, tool_name: str) -> List[str]:
        """Search pip packages using PyPI search API alternative"""
        try:
            import requests
            response = requests.get(f"https://pypi.org/search/?q={tool_name}", timeout=10)
            if response.status_code == 200:
                # Simple regex to find package names (this is a basic implementation)
                packages = re.findall(r'class="package-snippet__name">([^<]+)</span>', response.text)
                return [f"pip: {pkg}" for pkg in packages[:3] if tool_name.lower() in pkg.lower()]
        except Exception:
            pass
        return []
    
    def install_package(self, package_name: str) -> bool:
        """Install pip package"""
        try:
            result = subprocess.run(['pip', 'install', package_name], timeout=300)
            return result.returncode == 0
        except Exception:
            return False

class UniversalInstaller:
    """Universal software detection and installation system"""
    
    def __init__(self):
        self.package_managers = [
            CondaManager(),
            BrewManager() if platform.system() == 'Darwin' else None,
            AptManager() if platform.system() == 'Linux' else None,
            PipManager()
        ]
        # Filter out None values
        self.package_managers = [pm for pm in self.package_managers if pm is not None]
    
    def is_tool_installed(self, tool_name: str) -> bool:
        """Check if a tool is installed and available in PATH"""
        return shutil.which(tool_name) is not None
    
    def extract_tools_from_command(self, command: str) -> Set[str]:
        """Extract potential tool names from a command string"""
        # Split command by common separators and get the first word of each part
        tools = set()
        
        # Bash keywords and constructs that should NOT be treated as tools
        bash_keywords = {
            'if', 'then', 'else', 'elif', 'fi', 'for', 'do', 'done', 'while', 'until', 
            'case', 'esac', 'in', 'break', 'continue', 'function', 'return', 'local',
            'declare', 'readonly', 'export', 'unset', 'shift', 'exit', 'trap', 'test',
            '[', '[[', '{', '}', '(', ')', 'true', 'false'
        }
        
        # Check for heredoc pattern and remove heredoc content
        # Pattern: command << DELIMITER ... DELIMITER
        heredoc_pattern = r'<<\s*[\'"]?(\w+)[\'"]?\s*\n(.*?)\n\1'
        # Remove heredoc content from the command before analysis
        command_without_heredoc = re.sub(heredoc_pattern, '', command, flags=re.DOTALL)
        
        # Also handle simpler heredoc without quotes: << DELIMITER
        heredoc_pattern2 = r'<<\s*(\w+)\s*\n(.*?)\n\1'
        command_without_heredoc = re.sub(heredoc_pattern2, '', command_without_heredoc, flags=re.DOTALL)
        
        # Split by common separators and get the first word of each part
        # Split by && || ; | and newlines, but preserve structure for for/while loops
        parts = re.split(r'[;&|]+|\n', command_without_heredoc)
        
        for part in parts:
            part = part.strip()
            if part and not part.startswith('#'):  # Skip comments
                # Get the first word (likely the command)
                words = part.split()
                if words:
                    first_word = words[0]
                    # Remove common prefixes
                    first_word = first_word.replace('sudo', '').replace('time', '').strip()
                    
                    # Skip bash keywords, options, and special characters
                    if (first_word and 
                        not first_word.startswith('-') and 
                        not first_word.startswith('$') and
                        first_word not in bash_keywords and
                        not first_word.isdigit()):
                        tools.add(first_word)
        
        return tools
    
    def detect_missing_tools(self, command: str) -> List[str]:
        """Detect missing tools from a command string"""
        potential_tools = self.extract_tools_from_command(command)
        missing_tools = []
        
        # Common shell built-ins and utilities that shouldn't trigger installation
        common_commands = {
            'cd', 'ls', 'mkdir', 'cp', 'mv', 'rm', 'echo', 'export', 'source', '.', 'bash',
            'sh', 'zsh', 'fish', 'pwd', 'cat', 'head', 'tail', 'grep', 'sed', 'awk', 'cut',
            'sort', 'uniq', 'wc', 'find', 'xargs', 'chmod', 'chown', 'ln', 'touch', 'which',
            'whoami', 'id', 'ps', 'kill', 'jobs', 'bg', 'fg', 'nohup', 'sleep', 'date',
            'uname', 'hostname', 'df', 'du', 'free', 'top', 'history', 'alias', 'type',
            'python', 'python3', 'python2', 'pip', 'pip3', 'conda', 'mamba'  # Add Python interpreters
        }
        
        for tool in potential_tools:
            # Skip common shell commands and built-ins
            if tool not in common_commands:
                if not self.is_tool_installed(tool):
                    missing_tools.append(tool)
        
        return missing_tools
    
    def get_available_managers(self) -> List[PackageManager]:
        """Get list of available package managers"""
        return [pm for pm in self.package_managers if pm.is_available()]
    
    def search_tool_in_repos(self, tool_name: str) -> Dict[str, List[str]]:
        """Search for a tool across all available package managers"""
        results = {}
        available_managers = self.get_available_managers()
        
        for manager in available_managers:
            try:
                packages = manager.search_package(tool_name)
                if packages:
                    results[manager.name] = packages
            except Exception as e:
                logger.info(f"[dim]Error searching in {manager.name}: {e}[/dim]")
        
        return results
    
    def display_installation_options(self, tool_name: str, search_results: Dict[str, List[str]]):
        """Display installation options in a nice table"""
        if not search_results:
            logger.info(f"[red]No packages found for '{tool_name}'[/red]")
            logger.info(f"[dim]You may need to install it manually from the official website[/dim]")
            return
        
        table = Table(title=f"Installation options for '{tool_name}'")
        table.add_column("Package Manager", style="cyan")
        table.add_column("Package Names", style="green")
        
        for manager, packages in search_results.items():
            package_list = "\n".join(packages)
            table.add_row(manager, package_list)
        
        logger.info("", rich=table)
    
    def suggest_installation(self, command: str, interactive: bool = True) -> bool:
        """Analyze command and suggest installing missing tools"""
        missing_tools = self.detect_missing_tools(command)
        
        if not missing_tools:
            return True  # No missing tools
        
        logger.info(f"\n[yellow]⚠ Command requires {len(missing_tools)} missing tool(s):[/yellow]")
        
        all_found = True
        for tool in missing_tools:
            logger.info(f"\n[bold red]Missing: {tool}[/bold red]")
            
            if interactive:
                search_results = self.search_tool_in_repos(tool)
                self.display_installation_options(tool, search_results)
                
                if search_results:
                    # Auto-select best option (prefer conda, then brew, then others)
                    best_option = None
                    for manager_name in ['conda/mamba', 'homebrew', 'apt', 'pip']:
                        if manager_name in search_results:
                            best_option = (manager_name, search_results[manager_name][0])
                            break
                    
                    if best_option and Confirm.ask(f"Install using {best_option[1]}?"):
                        manager_name, package_info = best_option
                        package_name = package_info.split(': ', 1)[1] if ': ' in package_info else tool
                        
                        # Find the corresponding manager
                        manager = next((pm for pm in self.get_available_managers() if pm.name == manager_name), None)
                        if manager:
                            logger.info(f"[green]Installing {tool} via {manager_name}...[/green]")
                            success = manager.install_package(package_name)
                            if success:
                                logger.info(f"[green]✓ {tool} installed successfully![/green]")
                            else:
                                logger.info(f"[red]✗ Failed to install {tool}[/red]")
                                all_found = False
                        else:
                            all_found = False
                    else:
                        all_found = False
                else:
                    all_found = False
            else:
                logger.info(f"[dim]Use: python -m pantheon.cli --help for installation guidance[/dim]")
                all_found = False
        
        return all_found


# Global instance
universal_installer = UniversalInstaller()