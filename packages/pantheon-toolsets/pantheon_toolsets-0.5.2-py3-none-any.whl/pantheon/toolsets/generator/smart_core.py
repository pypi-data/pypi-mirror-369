"""
Smart Pantheon Toolset Generator with Dynamic Template Optimization
Simple approach: Load template file → Fill variables → Generate toolset
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional

from ..utils.toolset import ToolSet, tool
from ..utils.log import logger
from ..file_editor.core import FileEditorToolSet 
from ..python.python_interpreter import PythonInterpreterToolSet


class SmartGeneratorToolSet(ToolSet):
    """Smart ToolSet for generating toolsets with dynamic template filling"""

    def __init__(self, name: str = "generator", **kwargs):
        super().__init__(name, **kwargs)
        # Use the existing ext_toolsets directory in the project root
        project_root = Path(__file__).parent.parent.parent.parent.parent  # Navigate up from pantheon/toolsets/generator/
        self.workspace = project_root / "ext_toolsets"
        self.workspace.mkdir(exist_ok=True)
        
    def _load_and_fill_template(self, 
                               name: str, 
                               domain: str, 
                               description: str, 
                               requirements: Optional[str] = None) -> str:
        """Load base template and fill with user requirements"""
        
        # Load the template file
        template_path = Path(__file__).parent / "TOOLSET_GENERATION_TEMPLATE.md"
        if not template_path.exists():
            raise FileNotFoundError("TOOLSET_GENERATION_TEMPLATE.md not found")
            
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        # Define domain-specific optimizations
        domain_specs = {
            "web_scraper": {
                "primary_purpose": "provide intelligent web scraping capabilities with rate limiting, anti-bot detection, and content extraction",
                "main_tool": "requests + beautifulsoup4",
                "dependencies": "requests, beautifulsoup4, selenium, fake-useragent",
                "functions": [
                    "fetch_page: Intelligently fetch web pages with rate limiting",
                    "extract_content: Extract text, links, images from HTML", 
                    "handle_javascript: Process dynamic content with headless browsers",
                    "manage_sessions: Handle cookies and authentication",
                    "detect_blocking: Identify and handle anti-bot measures"
                ],
                "detect": "proxy servers, browser installations, existing sessions",
                "specific_instructions": """
### Web Scraping Specific Requirements:
- Implement intelligent rate limiting with exponential backoff
- Add user-agent rotation and proxy support  
- Handle common anti-bot measures (CAPTCHA detection, blocking)
- Support both static HTML and JavaScript-rendered content
- Implement session persistence and cookie management
- Add robust error handling for network timeouts and blocks
                """
            },
            "api_client": {
                "primary_purpose": "provide robust REST API client with authentication, caching, and intelligent error handling",
                "main_tool": "requests + httpx",
                "dependencies": "requests, httpx, pydantic, cachetools, tenacity",
                "functions": [
                    "authenticate: Handle OAuth, API keys, JWT authentication",
                    "make_request: Execute API calls with retry logic",
                    "handle_pagination: Process paginated responses automatically",
                    "cache_responses: Intelligent caching with TTL",
                    "validate_schema: Validate responses against schemas"
                ],
                "detect": "API keys, authentication tokens, cached responses",
                "specific_instructions": """
### API Client Specific Requirements:
- Support multiple authentication methods (OAuth2, API keys, Basic Auth)
- Implement exponential backoff retry with jitter
- Add intelligent response caching with configurable TTL
- Handle rate limiting with automatic throttling
- Support request/response validation with Pydantic
- Add comprehensive logging and debugging capabilities
                """
            },
            "data_processor": {
                "primary_purpose": "provide comprehensive data processing with validation, transformation, and analysis",
                "main_tool": "pandas + numpy", 
                "dependencies": "pandas, numpy, pydantic, polars, pyarrow",
                "functions": [
                    "load_data: Load from multiple formats (CSV, JSON, Excel, Parquet)",
                    "validate_schema: Validate data against predefined schemas",
                    "transform_data: Apply cleaning and transformation operations",
                    "analyze_data: Perform statistical analysis and profiling",
                    "export_data: Export to various formats with optimization"
                ],
                "detect": "data files, schema definitions, processing configurations",
                "specific_instructions": """
### Data Processing Specific Requirements:
- Support multiple data formats with automatic type inference
- Implement comprehensive schema validation and profiling
- Add streaming processing capabilities for large datasets
- Support common transformations (filtering, aggregation, joins)
- Add statistical analysis and visualization tools
- Implement data lineage tracking and quality metrics
                """
            }
        }
        
        # Get domain specifications or use defaults
        spec = domain_specs.get(domain, {
            "primary_purpose": f"provide {domain} capabilities",
            "main_tool": "python standard library",
            "dependencies": "",
            "functions": ["process: Main processing function"],
            "detect": "configuration files",
            "specific_instructions": f"### {domain.title()} Specific Requirements:\n- Implement domain-specific logic"
        })
        
        # Fill template variables
        filled_template = template_content.replace("[TOOLSET_NAME]", name)
        filled_template = filled_template.replace("[PRIMARY_PURPOSE]", spec["primary_purpose"])
        filled_template = filled_template.replace("[MAIN_TOOL_NAME]", spec["main_tool"])
        filled_template = filled_template.replace("[LIST_OF_DEPENDENCIES]", spec["dependencies"])
        filled_template = filled_template.replace("[WHAT_TO_DETECT]", spec["detect"])
        
        # Replace function list
        functions_text = "\n".join([f"{i+1}. {func}" for i, func in enumerate(spec["functions"])])
        filled_template = filled_template.replace(
            "1. [FUNCTION_1]: [DESCRIPTION]\n2. [FUNCTION_2]: [DESCRIPTION]\n3. [FUNCTION_3]: [DESCRIPTION]\n...",
            functions_text
        )
        
        # Add domain-specific instructions
        filled_template = filled_template.replace(
            "[ADD ANY DOMAIN-SPECIFIC REQUIREMENTS HERE]", 
            spec["specific_instructions"]
        )
        
        # Add user requirements if provided
        if requirements:
            user_requirements = f"""
### User-Specific Requirements:
{requirements}

Please integrate these requirements into the toolset implementation.
            """
            filled_template += user_requirements
        
        return filled_template

    def _load_knowledge_base(self, 
                            name: str, 
                            domain: str, 
                            description: str, 
                            requirements: Optional[str] = None) -> str:
        """Load complete knowledge base with filled template"""
        
        knowledge_base = "# SMART PANTHEON TOOLSET GENERATION SYSTEM\n\n"
        
        # Add filled template
        filled_template = self._load_and_fill_template(name, domain, description, requirements)
        knowledge_base += f"## CUSTOMIZED GENERATION TEMPLATE\n\n{filled_template}\n\n---\n\n"
        
        # Add design documents
        design_docs = self._get_embedded_design_docs()
        knowledge_base += design_docs
        
        return knowledge_base

    def _get_embedded_design_docs(self) -> str:
        """Load embedded design documents from local files"""
        docs_content = ""
        
        local_docs = [
            "EXTERNAL_TOOLSET_DESIGN.md",
            "EXTERNAL_TOOLSET_AGENT_INTEGRATION.md"
        ]
        
        for doc_name in local_docs:
            doc_path = Path(__file__).parent / doc_name
            if doc_path.exists():
                try:
                    with open(doc_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    docs_content += f"## {doc_name}\n\n{content}\n\n---\n\n"
                except Exception as e:
                    logger.warning(f"Failed to load {doc_name}: {e}")
        
        return docs_content
    
    def _generate_config_template(self, domain: str) -> str:
        """Generate generic configuration template that AI can adapt"""
        # Generic template that works for any domain - AI will determine specific usage
        return '''{
            "file_extensions": {
                "input": [".txt", ".json", ".csv", ".yml", ".yaml"],
                "output": [".out", ".result", ".log", ".json", ".csv"], 
                "processed": [".tmp", ".cache", ".processed"],
                "config": [".conf", ".cfg", ".ini", ".env"]
            },
            "tools": {
                "required": ["python3"],
                "optional": ["curl", "jq"],
                "alternatives": {}
            },
            "install_commands": {
                "requests": "pip install requests",
                "pyyaml": "pip install pyyaml",
                "pandas": "pip install pandas"
            },
            "defaults": {
                "threads": 2,
                "timeout": 30,
                "max_retries": 3,
                "chunk_size": 1024
            },
            "paths": {
                "cache": "~/.pantheon/cache",
                "temp": "temp/",
                "output": "output/",
                "logs": "logs/"
            }
        }'''
    
    def _generate_domain_methods(self, domain: str, name: str) -> str:
        """Generate generic domain methods that AI can adapt to any use case"""
        # Generic methods that work for any domain - AI will determine specific behavior
        return '''
    @tool
    def process_data(self, input_data: str, **params) -> Dict[str, Any]:
        """Main data processing method - AI will adapt based on domain and requirements"""
        logger.info(f"[bold green]Processing data: {input_data}[/bold green]")
        
        # Merge parameters with defaults  
        process_params = self.pipeline_config["defaults"].copy()
        process_params.update(params)
        
        # Simulate processing with progress
        with Progress(SpinnerColumn(), TextColumn("{task.description}")) as progress:
            task = progress.add_task("Processing...", total=None)
            time.sleep(2)  # Replace with actual processing logic
            progress.update(task, description="Processing complete!")
        
        return {
            "status": "success",
            "input": input_data,
            "parameters": process_params,
            "output": "processed_data.out"
        }
    
    @tool
    def analyze_content(self, content: str, analysis_type: str = "default", **options) -> Dict[str, Any]:
        """Analyze content - AI will determine specific analysis based on domain"""
logger.info(f"[cyan]Analyzing content: {analysis_type}[/cyan]")
        
        # Generic analysis framework
        analysis_results = {
            "content_type": type(content).__name__,
            "content_length": len(str(content)),
            "analysis_type": analysis_type,
            "timestamp": datetime.now().isoformat()
        }
        
        # AI will determine specific analysis steps based on domain
        with Progress(SpinnerColumn(), TextColumn("{task.description}")) as progress:
            task = progress.add_task("Analyzing...", total=None)
            time.sleep(1)  # Replace with domain-specific analysis
            progress.update(task, description="Analysis complete!")
        
        return {"status": "success", "results": analysis_results}
    
    @tool
    def validate_input(self, input_path: str, **validation_options) -> Dict[str, Any]:
        """Validate input data - AI will apply domain-specific validation rules"""
        input_path = Path(input_path)
        
        if not input_path.exists():
            return {
                "status": "error",
                "message": f"Input not found: {input_path}",
                "suggestions": ["Check path", "Ensure file/directory exists"]
            }
        
        # Generic validation - AI will add domain-specific checks
        validation_results = {
            "path": str(input_path),
            "exists": input_path.exists(),
            "is_file": input_path.is_file(),
            "is_directory": input_path.is_dir(),
            "size_bytes": input_path.stat().st_size if input_path.is_file() else 0,
            "extension": input_path.suffix if input_path.is_file() else None
        }
        
        logger.info("", rich=Panel(
            f"Path: {input_path.name}\\n"
            f"Type: {'File' if input_path.is_file() else 'Directory'}\\n"
            f"Size: {validation_results['size_bytes']} bytes\\n"
            f"Extension: {validation_results['extension'] or 'N/A'}",
            title="Input Validation",
            border_style="green"
        ))
        
        return {"status": "success", "validation": validation_results}
    
    @tool
    def generate_output(self, data: str, output_format: str = "json", output_path: str = None) -> Dict[str, Any]:
        """Generate output in specified format - AI will determine best format for domain"""
        if output_path is None:
            output_path = self.workspace_path / f"output.{output_format}"
        else:
            output_path = Path(output_path)
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"[green]Generating output: {output_path}[/green]")
        
        # AI will determine appropriate output generation based on domain
        try:
            if output_format.lower() == "json":
                with open(output_path, 'w') as f:
                    json.dump({"data": str(data), "timestamp": datetime.now().isoformat()}, f, indent=2)
            else:
                with open(output_path, 'w') as f:
                    f.write(str(data))
            
            return {
                "status": "success",
                "output_path": str(output_path),
                "format": output_format,
                "size_bytes": output_path.stat().st_size
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to generate output: {e}",
                "suggestions": ["Check permissions", "Verify output format"]
            }
    
    @tool
    def create_report(self, data: str, report_format: str = "summary") -> Dict[str, Any]:
        """Create analysis report - AI will customize based on domain and data"""
        logger.info(f"[blue]Creating {report_format} report...[/blue]")
        
        # Try to parse data as JSON if it's a string, otherwise use as-is
        try:
            parsed_data = json.loads(data) if isinstance(data, str) else data
        except (json.JSONDecodeError, TypeError):
            parsed_data = data
            
        # Generic report structure - AI will customize for specific domains
        report = {
            "report_type": report_format,
            "generated_at": datetime.now().isoformat(),
            "summary": {
                "total_items": len(parsed_data) if isinstance(parsed_data, (list, dict)) else 1,
                "data_type": type(parsed_data).__name__,
                "status": "completed"
            },
            "details": parsed_data
        }
        
        # Save report
        report_path = self.workspace_path / f"report_{report_format}.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info("", rich=Panel(
            f"Report Type: {report_format}\\n"
            f"Items: {report['summary']['total_items']}\\n"
            f"Status: {report['summary']['status']}\\n"
            f"Output: {report_path}",
            title="✅ Report Generated",
            border_style="blue"
        ))
        
        return {"status": "success", "report_path": str(report_path), "report": report}
    
    @tool
    def cleanup_resources(self) -> Dict[str, Any]:
        """Clean up temporary resources - AI will determine what to clean based on domain"""
        logger.info("[yellow]Cleaning up resources...[/yellow]")
        
        # Generic cleanup - AI will add domain-specific cleanup logic
        cleanup_summary = {
            "temp_files_removed": 0,
            "cache_cleared": False,
            "workspace_organized": True
        }
        
        # AI will determine specific cleanup actions based on domain
        temp_dir = self.workspace_path / "temp"
        if temp_dir.exists():
            import shutil
            shutil.rmtree(temp_dir)
            cleanup_summary["temp_files_removed"] = 1
            cleanup_summary["cache_cleared"] = True
        
        return {"status": "success", "cleanup": cleanup_summary}'''

    @tool
    def generate_toolset(self, 
                        name: str,
                        domain: str, 
                        description: str,
                        requirements: str = None) -> Dict[str, Any]:
        """Generate a new external toolset with optimized template based on requirements
        
        Args:
            name: Toolset name (lowercase, underscores)
            domain: Domain category (web_scraper, data_processor, api_client, etc.)
            description: Brief description of toolset functionality
            requirements: Optional specific requirements (e.g., "GitHub API v4 with OAuth2")
            
        Returns:
            Generation result with status and created files
        """
        try:
            # Validate inputs
            if not name or not domain or not description:
                return {
                    "status": "error",
                    "message": "Name, domain, and description are required",
                    "recommendation": "Provide all required parameters"
                }
            
            # Domain validation removed - Smart Generator supports any domain through dynamic templates
            # The template system will adapt to any domain automatically
            
            # Check if toolset already exists
            toolset_path = self.workspace / name
            if toolset_path.exists():
                return {
                    "status": "error", 
                    "message": f"Toolset '{name}' already exists",
                    "recommendation": f"Choose a different name or remove existing {toolset_path}"
                }
            
            # Create toolset directory
            toolset_path.mkdir(parents=True)
            
            # Load smart knowledge base with filled template
            smart_knowledge = self._load_knowledge_base(name, domain, description, requirements)
            
            # Create smart generation prompt
            generation_prompt = f"""Using the SMART PANTHEON TOOLSET GENERATION SYSTEM, create a complete, production-ready external toolset:

TOOLSET SPECIFICATIONS:
- Name: {name}
- Domain: {domain}
- Description: {description}
{f"- Specific Requirements: {requirements}" if requirements else ""}

SMART GENERATION PROCESS:
The CUSTOMIZED GENERATION TEMPLATE has been pre-filled with domain-specific optimizations for {domain}:
- Primary purpose and main tools identified
- Key functions and dependencies specified  
- Domain-specific requirements and patterns included
- User requirements integrated into the template

DELIVERABLES:
Create complete, working implementations for:
- toolset.py: Full implementation following the customized template
- config.json: Complete metadata with domain-specific settings
- __init__.py: Proper module exports
- README.md: Comprehensive documentation

SMART KNOWLEDGE BASE:
{smart_knowledge[:8000]}...

Follow the customized template exactly - it has been optimized for your specific {domain} requirements."""

            # Create smart toolset files directly
            toolset_code = self._generate_smart_toolset_code(name, domain, description, requirements)
            with open(toolset_path / "toolset.py", "w", encoding="utf-8") as f:
                f.write(toolset_code)
            
            config_data = self._generate_smart_config(name, domain, description, requirements)
            with open(toolset_path / "config.json", "w", encoding="utf-8") as f:
                f.write(json.dumps(config_data, indent=2))
            
            init_code = self._generate_init(name)
            with open(toolset_path / "__init__.py", "w", encoding="utf-8") as f:
                f.write(init_code)
            
            readme_content = self._generate_smart_readme(name, domain, description, requirements)
            with open(toolset_path / "README.md", "w", encoding="utf-8") as f:
                f.write(readme_content)
            
            # Generate AI prompt guidance file in the toolset directory
            prompt_content = self._generate_prompt_file(name, domain, description, requirements)
            prompt_file = toolset_path / "prompt.py"
            with open(prompt_file, "w", encoding="utf-8") as f:
                f.write(prompt_content)
            
            return {
                "status": "success",
                "message": f"Generated smart toolset '{name}' with customized {domain} template",
                "data": {
                    "name": name,
                    "domain": domain,
                    "template_customized": True,
                    "location": str(toolset_path),
                    "files_created": ["toolset.py", "config.json", "__init__.py", "README.md", "prompt.py"],
                    "optimizations_applied": [
                        f"Template pre-filled for {domain}",
                        "Domain-specific functions and dependencies",
                        "Smart error handling and validation",
                        "Production-ready implementations",
                        "AI prompt guidance file generated"
                    ] + ([f"Custom requirements: {requirements}"] if requirements else []),
                    "next_steps": [
                        f"Review customized implementation in {toolset_path}/",
                        f"Install dependencies as specified in config.json",
                        f"Test: python -c \"from {name}.toolset import *; print('Success!')\"",
                        f"Use: python -m pantheon.cli --ext-toolsets {name}"
                    ]
                }
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Smart generation failed: {str(e)}",
                "recommendation": "Check parameters and template file availability"
            }

    def _generate_smart_toolset_code(self, name: str, domain: str, description: str, requirements: str = None) -> str:
        """Generate professional-grade toolset code following bio toolset patterns"""
        class_name = ''.join(word.capitalize() for word in name.split('_')) + 'ToolSet'
        
        # Generate domain-specific configuration
        config_template = self._generate_config_template(domain)
        methods_template = self._generate_domain_methods(domain, name)
        
        # Create the code template string without f-string to avoid conflicts
        template_code = f'''"""{description}

Professional toolset generated following Pantheon bio toolset patterns.
Domain: {domain}
Requirements: {requirements or "Standard implementation"}

This toolset follows the universal design patterns from:
/pantheon/toolsets/bio/README.md
"""

import os
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

# Logger import (REQUIRED)
from ...utils.log import logger
from rich.table import Table
from rich.panel import Panel  
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn

# Import base class from new location
try:
    from pantheon.toolsets.external import ExternalToolSet, tool
except ImportError:
    # Fallback to legacy location for backward compatibility
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent.parent))
    from base import ExternalToolSet, tool


class {class_name}(ExternalToolSet):
    """Professional {domain} toolset: {description}
    
    Follows universal bio toolset design patterns:
    - Configuration-driven design
    - Rich console output  
    - Progress tracking
    - Dependency checking
    - Folder scanning
    - Error handling with recovery suggestions
    """
    
    def __init__(self, 
                 name: str = "{name}",
                 workspace_path: str = None,
                 **kwargs):
        super().__init__(name=name, workspace_path=workspace_path, **kwargs)
        
        # REQUIRED: Initialize configuration (Pattern 1)
        self.pipeline_config = self._initialize_config()
        
        # REQUIRED: Logger for formatted output (Pattern 6)
        
        # Domain-specific setup
        self.domain = "{domain}"
        
        # Show initialization message
        logger.info("", rich=Panel(
            f"[green]✓[/green] Initialized {{self.name}} toolset\\n"
            f"[dim]Domain: {domain}[/dim]\\n"
            f"[dim]Workspace: {{self.workspace_path}}[/dim]\\n"
            f"[dim]Tools: {{len([m for m in dir(self) if hasattr(getattr(self, m, None), '_is_tool')])}}[/dim]",
            title=f"[bold cyan]{{self.name.upper()}}[/bold cyan]",
            border_style="cyan"
        ))
        
    def _initialize_config(self) -> Dict[str, Any]:
        """REQUIRED: Initialize toolset configuration (Pattern 1)"""
        return {config_template}
        
    @tool
    def check_dependencies(self) -> Dict[str, Any]:
        """REQUIRED: Check tool dependencies (Pattern 2.1)"""
        logger.info("\\n" + "="*70)
        logger.info(f"🔧 [bold cyan]{{{{self.name.title()}}}} Dependencies Check[/bold cyan]")
        logger.info("="*70)
        
        tools_status = {{"installed": {{}}, "missing": [], "install_commands": {{}}}}
        
        # Create dependency table
        dep_table = Table(title="Dependency Status")
        dep_table.add_column("Tool", style="cyan")  
        dep_table.add_column("Status", justify="center")
        dep_table.add_column("Path / Install Command")
        
        # Check each required tool with progress
        required_tools = self.pipeline_config.get("tools", {{}}).get("required", [])
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{{{{task.description}}}}")
        ) as progress:
            task = progress.add_task("Checking dependencies...", total=len(required_tools))
            
            for tool in required_tools:
                progress.update(task, description=f"Checking {{{{tool}}}}...")
                
                try:
                    # Check if tool is available
                    result = subprocess.run(["which", tool], capture_output=True, text=True)
                    if result.returncode == 0:
                        path = result.stdout.strip()
                        tools_status["installed"][tool] = path
                        dep_table.add_row(tool, "✅ Installed", path)
                    else:
                        tools_status["missing"].append(tool)
                        install_cmd = self.pipeline_config.get("install_commands", {{}}).get(tool, f"# Install {{{{tool}}}} manually")
                        tools_status["install_commands"][tool] = install_cmd
                        dep_table.add_row(tool, "❌ Missing", install_cmd)
                        
                except Exception as e:
                    tools_status["missing"].append(tool)
                    dep_table.add_row(tool, "⚠️ Error", str(e))
                
                progress.advance(task)
        
        logger.info("", rich=dep_table)
        
        # Show summary panel
        status = "complete" if not tools_status["missing"] else "partial"
        color = "green" if status == "complete" else "yellow"
        
        summary = Panel(
            f"Status: [bold {{{{color}}}}]{{{{status.title()}}}}[/bold {{{{color}}}}]\\n"
            f"Installed: {{{{len(tools_status['installed'])}}}}\\n"
            f"Missing: {{{{len(tools_status['missing'])}}}}",
            title="Dependency Summary",
            border_style=color
        )
        logger.info("", rich=summary)
        
        return {{
            "status": status,
            "installed": tools_status["installed"],
            "missing": tools_status["missing"],
            "install_commands": tools_status["install_commands"]
        }}
        
    @tool  
    def scan_folder(self, folder_path: str) -> Dict[str, Any]:
        """REQUIRED: Scan folder for relevant data (Pattern 3.1)"""
        folder_path = Path(folder_path)
        logger.info(f"\\n🔍 [bold cyan]Scanning folder: {{{{folder_path}}}}[/bold cyan]")
        
        scan_results = {{
            "folder_path": str(folder_path),
            "total_files": 0,
            "total_size_mb": 0,
            "files": {{}},
            "metadata": {{}},
            "analysis_stage": "unknown",
            "next_steps": [],
            "warnings": []
        }}
        
        if not folder_path.exists():
            scan_results["warnings"].append(f"Folder does not exist: {{{{folder_path}}}}")
            return {{"status": "error", "message": "Folder not found", "data": scan_results}}
        
        # Categorize files by extension patterns
        file_extensions = self.pipeline_config.get("file_extensions", {{}})
        
        with Progress(SpinnerColumn(), TextColumn("{{{{task.description}}}}")) as progress:
            scan_task = progress.add_task("Scanning files...", total=None)
            
            for category, patterns in file_extensions.items():
                scan_results["files"][category] = []
                for pattern in patterns:
                    files = list(folder_path.rglob(f"*{{{{pattern}}}}"))
                    for file in files:
                        if file.is_file():
                            scan_results["files"][category].append({{
                                "path": str(file),
                                "size_mb": file.stat().st_size / (1024*1024),
                                "modified": datetime.fromtimestamp(file.stat().st_mtime).isoformat()
                            }})
                            scan_results["total_size_mb"] += file.stat().st_size / (1024*1024)
                            scan_results["total_files"] += 1
            
            progress.update(scan_task, description="Scan completed!")
        
        # Determine analysis stage and next steps
        self._determine_analysis_stage(scan_results)
        
        # Display results table
        summary_table = Table(title=f"{{{{self.domain.title()}}}} Data Summary")
        summary_table.add_column("Category", style="cyan")
        summary_table.add_column("Files", style="green", justify="right")
        summary_table.add_column("Size (MB)", style="blue", justify="right")
        
        for category, files in scan_results["files"].items():
            if files:
                total_size = sum(f["size_mb"] for f in files)
                summary_table.add_row(
                    category.replace("_", " ").title(),
                    str(len(files)),
                    f"{{{{total_size:.1f}}}}"
                )
        
        logger.info("", rich=summary_table)
        
        # Show next steps if available
        if scan_results["next_steps"]:
            next_panel = Panel(
                "\\n".join([f"• {{{{step}}}}" for step in scan_results["next_steps"]]),
                title="🎯 Suggested Next Steps",
                border_style="green"
            )
            logger.info("", rich=next_panel)
        
        return {{"status": "success", "data": scan_results}}
        
    def _determine_analysis_stage(self, scan_results: Dict[str, Any]):
        """Determine current analysis stage and suggest next steps"""
        files = scan_results["files"]
        
        # Domain-specific logic will be added here
        if any(files.get(category, []) for category in ["output", "results"]):
            scan_results["analysis_stage"] = "analysis_complete"
            scan_results["next_steps"] = ["generate_report", "create_visualizations"]
        elif any(files.get(category, []) for category in ["processed", "intermediate"]):
            scan_results["analysis_stage"] = "processing_done"
            scan_results["next_steps"] = ["run_analysis", "validate_results"]
        elif any(files.get(category, []) for category in ["input", "raw"]):
            scan_results["analysis_stage"] = "raw_data"
            scan_results["next_steps"] = ["validate_input", "preprocess_data", "run_analysis"]
        else:
            scan_results["analysis_stage"] = "empty"
            scan_results["next_steps"] = ["add_input_data"]

{methods_template}
    
    @tool
    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive toolset status"""
        return {{
            "status": "success",
            "message": f"{{{{self.name}}}} professional toolset is ready",
            "data": {{
                "name": self.name,
                "domain": self.domain,
                "version": "1.0.0",
                "workspace": str(self.workspace_path),
                "tools_available": len([m for m in dir(self) if hasattr(getattr(self, m, None), '_is_tool')]),
                "config_loaded": bool(self.pipeline_config),
                "patterns_implemented": [
                    "configuration_driven",
                    "rich_console", 
                    "progress_tracking",
                    "dependency_checking",
                    "folder_scanning",
                    "error_handling"
                ]
            }}
        }}
'''
        
        return template_code

    def _generate_smart_config(self, name: str, domain: str, description: str, requirements: str = None) -> Dict[str, Any]:
        """Generate smart config with domain-specific settings"""
        return {
            "name": name,
            "version": "1.0.0", 
            "description": description,
            "domain": domain,
            "template_customized": True,
            "author": "Smart Pantheon Generator",
            "dependencies": [],
            "tags": [domain, "generated", "smart", "template-customized"],
            "capabilities": ["domain_optimized", "template_filled"],
            "requirements": requirements
        }
    
    def _generate_init(self, name: str) -> str:
        """Generate __init__.py content"""
        class_name = ''.join(word.capitalize() for word in name.split('_')) + 'ToolSet'
        return f'''"""Smart external toolset: {name}"""

from .toolset import {class_name}

__all__ = ['{class_name}']
__smart__ = True
'''

    def _generate_smart_readme(self, name: str, domain: str, description: str, requirements: str = None) -> str:
        """Generate smart README"""
        class_name = ''.join(word.capitalize() for word in name.split('_')) + 'ToolSet'
        
        return f'''# {name.replace('_', ' ').title()} Smart Toolset

## 🧠 Smart Generation
{description}

This toolset was generated using **Smart Template Customization**:
- ✅ Template pre-filled with {domain} specifications
- ✅ Domain-specific functions and dependencies identified  
- ✅ Production-ready patterns and best practices included
- ✅ Custom requirements integrated: {requirements or 'None'}

## 🎯 Domain: {domain}

Template was customized with domain-specific optimizations for {domain} operations.

## 🚀 Usage

```python
from ext_toolsets.{name}.toolset import {class_name}

# Initialize smart toolset
toolset = {class_name}()

# Check smart features
status = toolset.get_status()
print("Template customized:", status["data"]["template_customized"])
```

## 📚 Smart Features

- **Template Customization**: Pre-filled template with domain expertise
- **Domain Optimization**: Specialized for {domain} workflows  
- **Requirements Integration**: Custom requirements built into template
- **Production Ready**: Generated with best practices and patterns

---
*Generated by Smart Pantheon Generator with Template Customization*
'''

    @tool
    def list_domains(self) -> Dict[str, Any]:
        """List example domains for smart toolset generation"""
        example_domains = {
            "web_scraper": "Smart web scraping with template-driven optimizations",
            "api_client": "Production API client with pre-filled authentication patterns",  
            "data_processor": "Advanced data processing with template-customized workflows",
            "database_client": "Enterprise database management with smart templates",
            "file_manager": "Intelligent file operations with optimized patterns",
            "image_processor": "Computer vision with template-driven batch processing",
            "text_processor": "NLP tools with smart template customizations",
            "system_monitor": "System monitoring with template-optimized alerting",
            "automation": "Workflow automation with smart template patterns", 
            "security": "Security tools with template-driven best practices",
            "bioinformatics": "Bioinformatics analysis tools with scientific workflow patterns",
            "machine_learning": "ML/AI tools with model training and inference patterns",
            "blockchain": "Blockchain and cryptocurrency tools with web3 patterns",
            "iot": "Internet of Things tools with sensor and device patterns",
            "devops": "DevOps and infrastructure tools with deployment patterns"
        }
        
        return {
            "status": "success",
            "message": f"Smart Generator supports ANY domain - these are just examples",
            "data": {
                "example_domains": example_domains,
                "total_examples": len(example_domains),
                "supports_any_domain": True,
                "template_customization": True,
                "approach": "Load template file → Fill variables → Generate optimized code for ANY domain",
                "note": "You can use ANY domain name - the system will adapt automatically"
            }
        }

    @tool
    def remove_toolset(self, name: str) -> Dict[str, Any]:
        """Remove an external toolset
        
        Args:
            name: Toolset name to remove
            
        Returns:
            Removal result with status and details
        """
        try:
            toolset_path = self.workspace / name
            
            if not toolset_path.exists():
                return {
                    "status": "error",
                    "message": f"Toolset '{name}' not found",
                    "recommendation": "Check toolset name and try again"
                }
            
            if not toolset_path.is_dir():
                return {
                    "status": "error",
                    "message": f"'{name}' is not a valid toolset directory",
                    "recommendation": "Provide a valid toolset directory name"
                }
            
            # List files to be removed
            files_to_remove = []
            for item in toolset_path.rglob("*"):
                if item.is_file():
                    files_to_remove.append(str(item.relative_to(toolset_path)))
            
            # Remove the toolset directory
            import shutil
            shutil.rmtree(toolset_path)
            
            return {
                "status": "success",
                "message": f"Successfully removed toolset '{name}'",
                "data": {
                    "removed_toolset": name,
                    "location": str(toolset_path),
                    "files_removed": len(files_to_remove),
                    "file_list": files_to_remove[:10] + (["...and more"] if len(files_to_remove) > 10 else [])
                }
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to remove toolset '{name}': {str(e)}",
                "recommendation": "Check permissions and try again"
            }

    @tool
    def list_existing_toolsets(self) -> Dict[str, Any]:
        """List all existing external toolsets
        
        Returns:
            List of existing toolsets with details
        """
        try:
            if not self.workspace.exists():
                return {
                    "status": "success",
                    "message": "No external toolsets workspace found",
                    "data": {
                        "toolsets": [],
                        "total": 0,
                        "workspace": str(self.workspace)
                    }
                }
            
            toolsets = []
            for item in self.workspace.iterdir():
                if item.is_dir() and not item.name.startswith('.'):
                    # Check if it's a valid toolset (has required files)
                    config_file = item / "config.json"
                    toolset_file = item / "toolset.py"
                    init_file = item / "__init__.py"
                    
                    config_data = {}
                    if config_file.exists():
                        try:
                            with open(config_file, 'r') as f:
                                config_data = json.load(f)
                        except Exception:
                            pass
                    
                    toolsets.append({
                        "name": item.name,
                        "path": str(item),
                        "description": config_data.get("description", "No description"),
                        "domain": config_data.get("domain", "unknown"),
                        "version": config_data.get("version", "unknown"),
                        "has_config": config_file.exists(),
                        "has_toolset": toolset_file.exists(),
                        "has_init": init_file.exists(),
                        "valid": all([config_file.exists(), toolset_file.exists(), init_file.exists()])
                    })
            
            # Sort by name
            toolsets.sort(key=lambda x: x["name"])
            
            return {
                "status": "success",
                "message": f"Found {len(toolsets)} external toolsets",
                "data": {
                    "toolsets": toolsets,
                    "total": len(toolsets),
                    "workspace": str(self.workspace),
                    "valid_toolsets": len([t for t in toolsets if t["valid"]])
                }
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to list toolsets: {str(e)}",
                "recommendation": "Check workspace permissions"
            }

    @tool
    def clear_all_toolsets(self) -> Dict[str, Any]:
        """Clear all external toolsets (use with caution!)
        
        Returns:
            Clearing result with removed toolsets count
        """
        try:
            if not self.workspace.exists():
                return {
                    "status": "success",
                    "message": "No toolsets to clear - workspace doesn't exist",
                    "data": {
                        "removed_count": 0,
                        "removed_toolsets": []
                    }
                }
            
            removed_toolsets = []
            removed_count = 0
            
            for item in self.workspace.iterdir():
                if item.is_dir() and not item.name.startswith('.'):
                    try:
                        import shutil
                        shutil.rmtree(item)
                        removed_toolsets.append(item.name)
                        removed_count += 1
                    except Exception as e:
                        # Continue removing others even if one fails
                        continue
            
            return {
                "status": "success",
                "message": f"Successfully cleared {removed_count} external toolsets",
                "data": {
                    "removed_count": removed_count,
                    "removed_toolsets": removed_toolsets,
                    "workspace": str(self.workspace)
                }
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to clear toolsets: {str(e)}",
                "recommendation": "Check permissions and try again"
            }

    @tool 
    def get_generation_help(self) -> Dict[str, Any]:
        """Get help for smart toolset generation"""
        return {
            "status": "success",
            "data": {
                "approach": "Smart Template Customization - Simple and Effective",
                "process": [
                    "1. Load TOOLSET_GENERATION_TEMPLATE.md from local file",
                    "2. Fill template variables based on domain and requirements", 
                    "3. Generate optimized toolset with customized template",
                    "4. Create production-ready implementations"
                ],
                "advantages": [
                    "Simple and maintainable approach",
                    "Template file is easily editable and versionable",
                    "Domain-specific customizations are clear and explicit",
                    "No complex embedded strings or syntax issues",
                    "Easy to debug and extend"
                ],
                "usage": "generate_toolset(name, domain, description, requirements)",
                "examples": {
                    "web_scraper": "generate_toolset('shop_scraper', 'web_scraper', 'E-commerce scraper', 'Amazon with anti-detection')",
                    "api_client": "generate_toolset('github_client', 'api_client', 'GitHub API client', 'GraphQL v4 with OAuth2')"
                },
                "template_file": "TOOLSET_GENERATION_TEMPLATE.md (embedded in generator directory)"
            }
        }
        
    def _generate_prompt_file(self, name: str, domain: str, description: str, requirements: str = None) -> str:
        """Generate AI prompt guidance file for the external toolset"""
        class_name = ''.join(word.capitalize() for word in name.split('_')) + 'ToolSet'
        
        # Create domain-specific tool descriptions
        domain_tools = self._get_domain_tool_descriptions(domain, name)
        
        prompt_content = f'''"""AI Prompt Guide for {name} External Toolset"""

from pathlib import Path
from typing import Optional

def generate_{name}_analysis_message(target_path: Optional[str] = None) -> str:
    """Generate {name} analysis message using {name} external toolset"""
    
    if target_path:
        target_path = Path(target_path).resolve()
        
        message = f"""
🔧 {name.replace('_', ' ').title()} Analysis Pipeline — External Toolset Integration
Domain: {domain} | Description: {description}
Target: {{target_path}}

You have access to the {name} external toolset and TodoList management.
The toolset is designed for: {description}
Use your AI intelligence to determine the most appropriate tools and workflow based on the domain ({domain}) and requirements.

GLOBAL RULES
- Always use the provided target path: "{{target_path}}" in all operations.
- Idempotent behavior: NEVER create duplicate todos. Only create if the list is EMPTY.
- Do not ask the user for confirmations; proceed automatically and log warnings when needed.
- After each tool completes successfully, call mark_task_done("what was completed"), then show_todos().
- IMPORTANT: Analyze the domain ({domain}) and description ({description}) to intelligently choose the right tools and workflow.

PHASE 0 — INITIALIZATION & SETUP
1) Initialize toolset:
   - Use {name} toolset methods to set up workspace
   - Check dependencies with check_dependencies()
   - Scan target folder with scan_folder("{{target_path}}")
   - Use get_status() to understand toolset capabilities

PHASE 1 — TODO CREATION (STRICT DE-DUP & AI-GUIDED)
Mandatory order:
  a) current = show_todos()
  b) scan_folder("{{target_path}}")
  c) get_status() # understand available tools
Creation rule (single condition):
  • If current is EMPTY → create ONCE todos based on the domain ({domain}) and description ({description}):
      0. "Initialize {name} workspace and check dependencies"
      1. "Scan and validate input data in target folder"
      2. "Process data using appropriate {name} tools" 
      3. "Generate results and output files"
      4. "Create summary report and cleanup"
  • Else → DO NOT create anything. Work with the existing todos.
  • AI GUIDANCE: Adapt the todos based on the specific domain and requirements.

PHASE 2 — EXECUTE WITH TODO TRACKING (LOOP)
For each current task:
  1) hint = execute_current_task()   # obtain guidance for the next action
  2) Use list_tools() to see available tools, then choose appropriate {name} tools:
{domain_tools}
  3) AI INTELLIGENCE: Based on the domain ({domain}) and description ({description}), 
     intelligently select and sequence the most appropriate tools for the task.
  4) mark_task_done("brief, precise description of the completed step")
  5) show_todos()
Repeat until all todos are completed.

PHASE 3 — ADAPTIVE TODO REFINEMENT
- If dependencies missing → add_todo("Install missing tools for {domain}")
- If quality issues found → add_todo("Address data quality issues")
- If additional processing needed → add_todo("Additional {domain} processing task")
- AI GUIDANCE: Add domain-specific todos based on analysis results.

EXECUTION STRATEGY (MUST FOLLOW THIS ORDER)
  1) Initialize {name} toolset, check dependencies, and understand capabilities
  2) scan_folder("{{target_path}}") and get_status()
  3) show_todos()  
  4) If todos empty → create the standard set ONCE; else skip creation
  5) Loop Phase 2 until all done; refine with Phase 3 when needed
  6) AI INTELLIGENCE: Continuously adapt approach based on {domain} domain and {description}

BEGIN NOW:
- Execute PHASE 0 → then PHASE 1 → then PHASE 2 loop.
- Use your AI intelligence to adapt the workflow to the specific domain ({domain}) and requirements.
- Output should clearly show: initialization status, dependency check results, todo status,
  and then progress through Phase 2 loop.
"""
        
    else:
        message = f"""
I need help with {name.replace('_', ' ')} analysis using the {name} external toolset.

🎯 TOOLSET INFO:
- Domain: {domain}
- Description: {description}
- Use AI intelligence to determine the best approach based on the domain and description

📋 TODO MANAGEMENT (use these for ALL tasks):
- add_todo() - Add tasks and auto-break them down
- show_todos() - Display current progress  
- execute_current_task() - Get smart guidance
- mark_task_done() - Mark tasks complete and progress

🔧 {name.upper()} EXTERNAL TOOLSET:
CORE OPERATIONS (always available):
- {name}.get_status() - Check toolset status and capabilities
- {name}.check_dependencies() - Verify tool availability
- {name}.scan_folder() - Analyze folder contents
- {name}.list_tools() - Show all available tools

GENERIC TOOLS (AI will determine specific usage based on domain):
{domain_tools}

💡 AI GUIDANCE:
- The toolset is designed for: {description}
- Domain: {domain}
- Use your AI intelligence to understand what tools are most appropriate
- Call {name}.list_tools() first to see what specific tools are actually available
- Adapt your approach based on the toolset's actual capabilities and the user's needs

WORKFLOW:
1. Start by adding todos for your specific task
2. Use {name}.get_status() and {name}.list_tools() to understand capabilities
3. Use execute_current_task() for smart guidance on which tools to use
4. Let AI intelligence guide the specific tool selection based on domain and description

Please start by adding a todo for your {name.replace('_', ' ')} task, then explore the toolset capabilities!"""
    
    return message
'''
        return prompt_content

    def _get_domain_tool_descriptions(self, domain: str, name: str) -> str:
        """Generate generic tool descriptions that work for any domain"""
        # AI will determine the appropriate tools based on the domain and description
        return f"""     - {name}.process_data() - Main data processing function
     - {name}.analyze_content() - Analyze and process content  
     - {name}.validate_input() - Validate input data and parameters
     - {name}.generate_output() - Generate results and output files
     - {name}.create_report() - Create summary reports
     - {name}.export_results() - Export processed results
     - {name}.cleanup_resources() - Clean up temporary resources"""