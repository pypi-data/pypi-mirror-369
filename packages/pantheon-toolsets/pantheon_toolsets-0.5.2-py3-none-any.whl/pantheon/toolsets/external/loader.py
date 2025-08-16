"""Enhanced external toolset loader with Agent integration"""

import os
import sys
import json
import importlib
import importlib.util
import inspect
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from rich.table import Table
from ..utils.log import logger

class ExternalToolsetLoader:
    """Enhanced loader with Agent integration support"""
    
    def __init__(self, ext_dir: str = "./ext_toolsets"):
        self.ext_dir = Path(ext_dir).resolve()
        self.loaded_toolsets = {}
        self.combined_instructions = []  # Store all toolset instructions
        
        # Ensure ext_dir exists
        self.ext_dir.mkdir(exist_ok=True)
        
        # Add ext_dir to Python path for toolset imports
        if str(self.ext_dir) not in sys.path:
            sys.path.insert(0, str(self.ext_dir))
        
        # Import base class
        self._import_base_class()
    
    def _import_base_class(self):
        """Import the external toolset base class"""
        try:
            from .base import ExternalToolSet
            self.ExternalToolSet = ExternalToolSet
        except ImportError:
            # Fallback to old location for backward compatibility
            try:
                from base import ExternalToolSet
                self.ExternalToolSet = ExternalToolSet
            except ImportError:
                # Try importing from ext_dir for legacy support
                try:
                    spec = importlib.util.spec_from_file_location("base", self.ext_dir / "base.py")
                    if spec and spec.loader:
                        base_module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(base_module)
                        self.ExternalToolSet = base_module.ExternalToolSet
                    else:
                        raise ImportError("Cannot load base module")
                except Exception as e:
                    logger.info(f"[yellow]Warning: External toolset base class not found: {e}[/yellow]")
                    self.ExternalToolSet = None
    
    def discover_toolsets(self) -> List[Dict[str, Any]]:
        """Discover all available external toolsets"""
        toolsets = []
        
        if not self.ext_dir.exists():
            return toolsets
        
        for item in self.ext_dir.iterdir():
            if item.is_dir() and not item.name.startswith('_') and item.name not in ['__pycache__']:
                config_path = item / "config.json"
                toolset_path = item / "toolset.py"
                
                if toolset_path.exists():
                    toolset_info = {
                        "name": item.name,
                        "path": str(item),
                        "config": {}
                    }
                    
                    if config_path.exists():
                        try:
                            with open(config_path, 'r') as f:
                                toolset_info["config"] = json.load(f)
                        except Exception as e:
                            logger.info(f"[yellow]Warning: Failed to load config for {item.name}: {e}[/yellow]")
                    
                    toolsets.append(toolset_info)
        
        return toolsets
    
    def load_toolset(self, name: str, **kwargs) -> Optional[Any]:
        """Load a specific external toolset"""
        if name in self.loaded_toolsets:
            return self.loaded_toolsets[name]
        
        toolset_dir = self.ext_dir / name
        
        if not toolset_dir.exists():
            logger.info(f"[red]Toolset '{name}' not found[/red]")
            return None
        
        toolset_file = toolset_dir / "toolset.py"
        if not toolset_file.exists():
            logger.info(f"[red]toolset.py not found in {name}[/red]")
            return None
        
        try:
            # Import the toolset module
            spec = importlib.util.spec_from_file_location(
                f"{name}.toolset",
                toolset_file
            )
            
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                sys.modules[f"{name}.toolset"] = module
                spec.loader.exec_module(module)
                
                # Find the toolset class
                toolset_class = None
                for item_name in dir(module):
                    item = getattr(module, item_name)
                    if (inspect.isclass(item) and 
                        self.ExternalToolSet and
                        item != self.ExternalToolSet and
                        issubclass(item, self.ExternalToolSet)):
                        toolset_class = item
                        break
                
                if toolset_class:
                    instance = toolset_class(name=name, **kwargs)
                    self.loaded_toolsets[name] = instance
                    
                    # Load prompt file if exists
                    prompt_file = toolset_dir / "prompt.py"
                    if prompt_file.exists():
                        try:
                            # Import the prompt module
                            prompt_spec = importlib.util.spec_from_file_location(
                                f"{name}.prompt",
                                prompt_file
                            )
                            if prompt_spec and prompt_spec.loader:
                                prompt_module = importlib.util.module_from_spec(prompt_spec)
                                sys.modules[f"{name}.prompt"] = prompt_module
                                prompt_spec.loader.exec_module(prompt_module)
                                
                                # Store prompt function in the toolset instance
                                function_name = f"generate_{name}_analysis_message"
                                if hasattr(prompt_module, function_name):
                                    instance._prompt_function = getattr(prompt_module, function_name)
                                    logger.info(f"[cyan]  ✓ Loaded prompt guidance for {name}[/cyan]")
                        except Exception as e:
                            logger.info(f"[yellow]  Warning: Failed to load prompt for {name}: {e}[/yellow]")
                    
                    # Add instructions to combined list
                    if hasattr(instance, 'get_prompt_addon'):
                        self.combined_instructions.append(instance.get_prompt_addon())
                    
                    logger.info(f"[green]✓ Loaded external toolset: {name}[/green]")
                    return instance
                else:
                    logger.info(f"[red]No valid toolset class found in {name}[/red]")
            
        except Exception as e:
            logger.info(f"[red]Failed to load toolset '{name}': {e}[/red]")
            import traceback
            traceback.print_exc()
        
        return None
    
    def load_all_toolsets(self, **kwargs) -> Dict[str, Any]:
        """Load all discovered toolsets"""
        toolsets = self.discover_toolsets()
        loaded = {}
        
        with self.console.status("[cyan]Loading external toolsets...") as status:
            for toolset_info in toolsets:
                name = toolset_info["name"]
                status.update(f"Loading {name}...")
                instance = self.load_toolset(name, **kwargs)
                if instance:
                    loaded[name] = instance
        
        # Display summary
        if loaded:
            logger.info(f"\n[green]Loaded {len(loaded)} external toolsets[/green]")
        else:
            logger.info(f"[yellow]No external toolsets found in {self.ext_dir}[/yellow]")
        
        return loaded
    
    def get_combined_instructions(self) -> str:
        """Get combined instructions for all loaded toolsets"""
        if not self.combined_instructions:
            return ""
        
        header = """
================================================================================
EXTERNAL TOOLSETS
================================================================================

The following external toolsets are available:
"""
        return header + "\n".join(self.combined_instructions)
    
    def register_with_agent(self, agent, toolsets: Optional[List[str]] = None):
        """Register external toolsets with an agent
        
        Args:
            agent: The Pantheon Agent instance
            toolsets: Optional list of specific toolsets to load (None = load all)
        """
        if toolsets:
            # Load specific toolsets
            for name in toolsets:
                toolset = self.load_toolset(name)
                if toolset:
                    agent.toolset(toolset)
        else:
            # Load all toolsets
            loaded = self.load_all_toolsets()
            for toolset in loaded.values():
                agent.toolset(toolset)
        
        # Return combined instructions for agent prompt enhancement
        return self.get_combined_instructions()
    
    def list_toolsets(self) -> None:
        """List all available external toolsets"""
        toolsets = self.discover_toolsets()
        
        if not toolsets:
            logger.info(f"[yellow]No external toolsets found in {self.ext_dir}[/yellow]")
            logger.info(f"[dim]Create toolsets in: {self.ext_dir}[/dim]")
            return
        
        table = Table(title="External Toolsets")
        table.add_column("Name", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Description", style="dim")
        table.add_column("Version", style="dim")
        
        for toolset_info in toolsets:
            name = toolset_info["name"]
            status = "✅ Loaded" if name in self.loaded_toolsets else "⚪ Available"
            description = toolset_info["config"].get("description", "No description")
            version = toolset_info["config"].get("version", "N/A")
            
            table.add_row(name, status, description, version)
        
        logger.info("", rich=table)
    
    def execute_tool(self, toolset_name: str, tool_name: str, *args, **kwargs) -> Dict[str, Any]:
        """Execute a tool from a specific toolset
        
        Args:
            toolset_name: Name of the toolset
            tool_name: Name of the tool method
            *args, **kwargs: Arguments to pass to the tool
        
        Returns:
            Tool execution result
        """
        # Load toolset if not loaded
        if toolset_name not in self.loaded_toolsets:
            self.load_toolset(toolset_name)
        
        if toolset_name not in self.loaded_toolsets:
            return {
                "status": "error",
                "message": f"Failed to load toolset '{toolset_name}'"
            }
        
        toolset = self.loaded_toolsets[toolset_name]
        
        # Check if tool exists
        if tool_name not in toolset.tools:
            return {
                "status": "error",
                "message": f"Tool '{tool_name}' not found in toolset '{toolset_name}'",
                "available_tools": list(toolset.tools.keys())
            }
        
        # Execute tool
        tool_method = toolset.tools[tool_name]["method"]
        return tool_method(*args, **kwargs)
    
    def get_toolset_prompt(self, toolset_name: str, target_path: Optional[str] = None) -> Optional[str]:
        """Get prompt message for a specific toolset with dynamic tool capabilities
        
        Args:
            toolset_name: Name of the toolset
            target_path: Optional target path for analysis
        
        Returns:
            Prompt message string with real tool capabilities or None if not available
        """
        if toolset_name not in self.loaded_toolsets:
            self.load_toolset(toolset_name)
        
        if toolset_name not in self.loaded_toolsets:
            return None
        
        toolset = self.loaded_toolsets[toolset_name]
        
        # Check if prompt function is available
        if hasattr(toolset, '_prompt_function'):
            try:
                # Get the base prompt message
                base_prompt = toolset._prompt_function(target_path)
                
                # Generate dynamic tool capabilities
                real_tools = self._get_real_tool_capabilities(toolset, toolset_name)
                
                # Replace generic tool descriptions with real ones
                if real_tools and base_prompt:
                    # Replace the generic tool section with real tool capabilities
                    updated_prompt = base_prompt.replace(
                        f"     - {toolset_name}.process_data() - Main data processing function\n"
                        f"     - {toolset_name}.analyze_content() - Analyze and process content  \n"
                        f"     - {toolset_name}.validate_input() - Validate input data and parameters\n"
                        f"     - {toolset_name}.generate_output() - Generate results and output files\n"
                        f"     - {toolset_name}.create_report() - Create summary reports\n"
                        f"     - {toolset_name}.export_results() - Export processed results\n"
                        f"     - {toolset_name}.cleanup_resources() - Clean up temporary resources",
                        real_tools
                    )
                    return updated_prompt
                
                return base_prompt
            except Exception as e:
                logger.info(f"[yellow]Warning: Failed to generate prompt for {toolset_name}: {e}[/yellow]")
                return None
        
        return None
    
    def _get_real_tool_capabilities(self, toolset, toolset_name: str) -> str:
        """Get real tool capabilities from the loaded toolset instance"""
        try:
            # Get all tool methods from the toolset
            tool_methods = []
            for attr_name in dir(toolset):
                attr = getattr(toolset, attr_name)
                if hasattr(attr, '_is_tool'):
                    # Get method docstring for description
                    doc = attr.__doc__ or "No description available"
                    # Take first line of docstring as description
                    description = doc.split('\n')[0].strip()
                    tool_methods.append(f"     - {toolset_name}.{attr_name}() - {description}")
            
            if tool_methods:
                return "\n".join(tool_methods)
            else:
                # Fallback to generic descriptions if no tools found
                return f"""     - {toolset_name}.get_status() - Check toolset status
     - {toolset_name}.list_tools() - Show all available tools
     - {toolset_name}.scan_folder() - Analyze folder contents"""
                
        except Exception as e:
            logger.info(f"[yellow]Warning: Failed to get real tool capabilities: {e}[/yellow]")
            return f"     - {toolset_name}.get_status() - Check toolset status"


# Global loader instance
ext_loader = ExternalToolsetLoader()