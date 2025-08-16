"""Base class for external toolsets with full Agent compatibility"""

import json
import inspect
from pathlib import Path
from typing import Dict, Any, Optional, Callable, List
from functools import wraps
from rich.table import Table
from rich.panel import Panel
from ..utils.log import logger

# Mock worker for Agent compatibility
class MockWorker:
    """Mock worker to simulate MagiqueWorker interface"""
    def __init__(self):
        self.functions = {}

def tool(func: Callable = None, **kwargs):
    """Tool decorator compatible with Pantheon Agent"""
    if func is None:
        from functools import partial
        return partial(tool, **kwargs)
    
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            # Log execution
            logger.info(f"[dim]→ Executing: {self.name}.{func.__name__}[/dim]")
            
            # Execute function
            result = func(self, *args, **kwargs)
            
            # Ensure consistent return format
            if not isinstance(result, dict):
                result = {"status": "success", "data": result}
            
            # Add metadata
            if "status" not in result:
                result["status"] = "success"
            
            return result
            
        except Exception as e:
            import traceback
            return {
                "status": "error",
                "message": str(e),
                "recommendation": f"Check parameters and try again. Error: {type(e).__name__}",
                "traceback": traceback.format_exc() if hasattr(self, 'debug') and self.debug else None
            }
    
    # Mark as tool
    wrapper._is_tool = True
    wrapper._tool_params = kwargs
    wrapper._tool_metadata = {
        "name": func.__name__,
        "doc": func.__doc__,
        "params": kwargs
    }
    return wrapper


class ExternalToolSet:
    """Base class for external toolsets with full Pantheon compatibility"""
    
    def __init__(self, 
                 name: str = None,
                 workspace_path: str = None,
                 debug: bool = False,
                 **kwargs):
        """Initialize external toolset
        
        Args:
            name: Toolset name
            workspace_path: Working directory
            debug: Enable debug mode
            **kwargs: Additional parameters
        """
        self.name = name or self.__class__.__name__.replace('ToolSet', '').lower()
        self.workspace_path = Path(workspace_path) if workspace_path else Path.cwd()
        self.debug = debug
        
        # Load configuration
        self.config = self._load_config()
        
        # Create mock worker for Agent compatibility
        self.worker = MockWorker()
        
        # Initialize tool registry
        self.tools = {}
        
        # Auto-discover tools
        self._discover_tools()
        
        # Generate instructions
        self.instructions = self._generate_instructions()
        
        # Show initialization message
        if self.debug:
            logger.info("", rich=Panel(
                f"[green]✓[/green] Initialized {self.name} toolset\n"
                f"[dim]Workspace: {self.workspace_path}[/dim]\n"
                f"[dim]Tools: {len(self.tools)}[/dim]",
                title=f"[bold cyan]{self.name.upper()}[/bold cyan]",
                border_style="cyan"
            ))
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from config.json"""
        # Try to find config in the same directory as the toolset
        toolset_file = inspect.getfile(self.__class__)
        config_path = Path(toolset_file).parent / "config.json"
        
        if config_path.exists():
            with open(config_path, 'r') as f:
                return json.load(f)
        return {
            "name": self.name,
            "version": "1.0.0",
            "description": f"{self.name} external toolset"
        }
    
    def _discover_tools(self):
        """Discover and register tool methods"""
        for name, method in inspect.getmembers(self, inspect.ismethod):
            if hasattr(method, '_is_tool'):
                # Get method documentation
                doc = method.__doc__ or "No description available"
                # Clean up doc string
                doc = doc.strip().split('\n')[0] if doc else "No description"
                
                # Register in both formats for compatibility
                self.tools[name] = {
                    "method": method,
                    "metadata": getattr(method, '_tool_metadata', {}),
                    "description": doc
                }
                
                # Register in worker.functions format
                self.worker.functions[name] = (method, doc)
    
    def _generate_instructions(self) -> str:
        """Generate agent instructions for this toolset"""
        # Parse tools and create instruction sections
        tool_summaries = []
        tool_details = []
        workflow_examples = []
        
        for name, info in self.tools.items():
            method = info["method"]
            desc = info["description"]
            
            # Get method signature
            sig = inspect.signature(method)
            params = []
            param_docs = []
            
            for param_name, param in sig.parameters.items():
                if param_name != 'self':
                    # Get type annotation
                    if param.annotation != inspect.Parameter.empty:
                        param_type = param.annotation.__name__ if hasattr(param.annotation, '__name__') else str(param.annotation)
                    else:
                        param_type = "Any"
                    
                    # Get default value
                    if param.default != inspect.Parameter.empty:
                        default = f" = {repr(param.default)}"
                    else:
                        default = ""
                    
                    params.append(f"{param_name}: {param_type}{default}")
                    param_docs.append(f"  - {param_name} ({param_type}): Parameter description")
            
            # Create tool summary
            tool_summaries.append(f"- {self.name}.{name}: {desc}")
            
            # Create detailed documentation
            if method.__doc__:
                tool_details.append(f"""
{name.upper()} ({self.name}.{name}):
Usage: {self.name}.{name}({', '.join(params) if params else ''})
Description: {method.__doc__.strip()}
""")
        
        # Create workflow examples based on tool categories
        if any('load' in name or 'read' in name for name in self.tools):
            workflow_examples.append(f"1. Load data: {self.name}.load_*(...)")
        if any('process' in name or 'transform' in name for name in self.tools):
            workflow_examples.append(f"2. Process data: {self.name}.process_*(...)")
        if any('analyze' in name or 'predict' in name for name in self.tools):
            workflow_examples.append(f"3. Analyze: {self.name}.analyze_*(...)")
        if any('save' in name or 'export' in name for name in self.tools):
            workflow_examples.append(f"4. Save results: {self.name}.save_*(...)")
        
        # Generate complete instructions
        instructions = f"""
================================================================================
{self.name.upper()} TOOLSET - {self.config.get('description', 'External toolset')}
================================================================================

AVAILABLE TOOLS ({len(self.tools)} total):
{chr(10).join(tool_summaries)}

TOOL DETAILS:
{chr(10).join(tool_details) if tool_details else 'See individual tool documentation'}

TYPICAL WORKFLOW:
{chr(10).join(workflow_examples) if workflow_examples else f'1. Use {self.name}.list_tools() to see available operations'}

ERROR HANDLING:
- All tools return {{"status": "success/error", "data": ..., "message": ...}}
- Check status before using data
- Use recommendations for error recovery

INTEGRATION:
- Tools are available as: {self.name}.<tool_name>(...)
- Get help: {self.name}.list_tools() or {self.name}.get_status()
"""
        return instructions
    
    def get_prompt_addon(self) -> str:
        """Get prompt addon for agent instructions"""
        return self.instructions
    
    @tool
    def list_tools(self) -> Dict[str, Any]:
        """List all available tools with details"""
        table = Table(title=f"{self.name.upper()} Tools")
        table.add_column("Tool", style="cyan")
        table.add_column("Description", style="green")
        table.add_column("Parameters", style="dim")
        
        tools_data = []
        for name, info in self.tools.items():
            method = info["method"]
            desc = info["description"]
            
            # Get parameters
            sig = inspect.signature(method)
            params = [
                param_name for param_name in sig.parameters.keys()
                if param_name != 'self'
            ]
            param_str = ", ".join(params) if params else "none"
            
            table.add_row(name, desc, param_str)
            tools_data.append({
                "name": name,
                "description": desc,
                "parameters": params
            })
        
        # Display table
        logger.info("", rich=table)
        
        return {
            "status": "success",
            "data": {
                "toolset": self.name,
                "version": self.config.get("version", "1.0.0"),
                "tools": tools_data,
                "total": len(tools_data)
            }
        }
    
    @tool
    def get_status(self) -> Dict[str, Any]:
        """Get toolset status and configuration"""
        status_info = {
            "name": self.name,
            "version": self.config.get("version", "1.0.0"),
            "description": self.config.get("description", "No description"),
            "workspace": str(self.workspace_path),
            "tools_count": len(self.tools),
            "tools": list(self.tools.keys()),
            "config": self.config
        }
        
        # Display status panel
        logger.info("", rich=Panel(
            f"[bold]{self.name.upper()} Status[/bold]\n\n"
            f"Version: {status_info['version']}\n"
            f"Tools: {status_info['tools_count']}\n"
            f"Workspace: {status_info['workspace']}\n"
            f"Description: {status_info['description']}",
            border_style="green"
        ))
        
        return {
            "status": "success",
            "data": status_info
        }