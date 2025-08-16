"""
Code Validator ToolSet - Comprehensive code verification system

This toolset provides multiple methods to verify generated code:
1. Help-based parameter validation
2. Import and syntax checking  
3. Function signature verification
4. Module existence validation
5. Documentation verification
"""

import ast
import importlib
import inspect
import subprocess
import sys
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from tempfile import NamedTemporaryFile
import json
import difflib
from io import StringIO
from ..utils.log import logger

from ..utils.toolset import ToolSet, tool


class CodeValidatorToolSet(ToolSet):
    """ToolSet for comprehensive code validation and verification"""

    def __init__(self, name: str = "code_validator", **kwargs):
        super().__init__(name, **kwargs)


    @tool
    def validate_python_code(
        self,
        code: str,
        check_syntax: bool = True,
        check_imports: bool = True,  
        check_functions: bool = True,
        safe_mode: bool = True
    ) -> Dict[str, Any]:
        """
        Comprehensive Python code validation
        
        Args:
            code: Python code to validate
            check_syntax: Check syntax correctness
            check_imports: Verify import statements
            check_functions: Validate function calls and signatures
            safe_mode: Only use safe validation methods (no execution)
            
        Returns:
            Validation results with detailed findings
        """
        results = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "details": {
                "syntax": None,
                "imports": [],
                "functions": [],
                "modules": []
            }
        }
        
        try:
            pass  # Silent validation
            
            # 1. Syntax validation
            if check_syntax:
                pass  # Silent syntax check
                syntax_result = self._check_syntax(code)
                results["details"]["syntax"] = syntax_result
                if not syntax_result["valid"]:
                    results["valid"] = False
                    results["errors"].extend(syntax_result["errors"])
                    logger.info("[red]❌ Syntax errors found[/red]")
                else:
                    pass  # Silent on success
            
            # 2. Import validation
            if check_imports:
                pass  # Silent import check
                import_result = self._check_imports(code, safe_mode)
                results["details"]["imports"] = import_result
                
                missing_imports = 0
                for imp in import_result:
                    if not imp["available"]:
                        missing_imports += 1
                        results["warnings"].append(f"Import '{imp['name']}' may not be available")
                
                if missing_imports == 0:
                    pass  # Silent on success
                else:
                    logger.info(f"[yellow]⚠️ {missing_imports} imports may not be available[/yellow]")
            
            # 3. Function validation
            if check_functions:
                pass  # Silent function check
                func_result = self._check_functions(code, safe_mode)
                results["details"]["functions"] = func_result
                
                func_issues = 0
                for func in func_result:
                    if func["issues"]:
                        func_issues += len(func["issues"])
                        results["warnings"].extend(func["issues"])
                
                if func_issues == 0:
                    pass  # Silent on success
                else:
                    logger.info(f"[yellow]⚠️ {func_issues} function issues found[/yellow]")
            
            # Final validation status
            if results["valid"]:
                pass  # Silent when successful
            else:
                logger.info(f"[red]❌ Validation failed with {len(results['errors'])} errors[/red]")
                        
        except Exception as e:
            results["valid"] = False
            results["errors"].append(f"Validation error: {str(e)}")
            logger.info(f"[red]💥 Validation error: {str(e)}[/red]")
            
        return results

    @tool
    def validate_command(
        self,
        command: str,
        check_help: bool = True,
        check_man: bool = True,
        check_which: bool = True
    ) -> Dict[str, Any]:
        """
        Validate shell commands and their parameters
        
        Args:
            command: Shell command to validate
            check_help: Check command help output
            check_man: Check manual pages
            check_which: Check if command exists in PATH
            
        Returns:
            Command validation results
        """
        results = {
            "valid": True,
            "command_exists": False,
            "help_info": None,
            "parameters": [],
            "suggestions": [],
            "errors": []
        }
        
        try:
            logger.info(f"[cyan]🔍 Validating command: {command}[/cyan]")
            
            # Parse command
            cmd_parts = command.strip().split()
            if not cmd_parts:
                results["valid"] = False
                results["errors"].append("Empty command")
                logger.info("[red]❌ Empty command provided[/red]")
                return results
                
            cmd_name = cmd_parts[0]
            cmd_args = cmd_parts[1:] if len(cmd_parts) > 1 else []
            
            # Check if command exists
            if check_which:
                logger.info("[dim]Checking if command exists...[/dim]")
                exists_result = self._check_command_exists(cmd_name)
                results["command_exists"] = exists_result["exists"]
                if not exists_result["exists"]:
                    results["valid"] = False
                    results["errors"].append(f"Command '{cmd_name}' not found in PATH")
                    results["suggestions"].extend(exists_result["suggestions"])
                    logger.info(f"[red]❌ Command '{cmd_name}' not found in PATH[/red]")
                    if exists_result["suggestions"]:
                        logger.info(f"[yellow]💡 Similar commands: {', '.join(exists_result['suggestions'])}[/yellow]")
                    return results
                else:
                    logger.info(f"[green]✅ Command '{cmd_name}' found[/green]")
            
            # Get help information
            if check_help:
                logger.info("[dim]Validating parameters against help...[/dim]")
                help_info = self._get_command_help(cmd_name)
                results["help_info"] = help_info
                
                # Validate parameters against help
                param_validation = self._validate_command_parameters(cmd_name, cmd_args, help_info)
                results["parameters"] = param_validation
                
                # Check for invalid parameters
                invalid_params = 0
                for param in param_validation:
                    if not param["valid"]:
                        invalid_params += 1
                        results["warnings"] = results.get("warnings", [])
                        results["warnings"].append(param["message"])
                
                if invalid_params == 0 and cmd_args:
                    logger.info("[green]✅ Parameters validated[/green]")
                elif invalid_params > 0:
                    logger.info(f"[yellow]⚠️ {invalid_params} parameter warnings[/yellow]")
                else:
                    logger.info("[dim]No parameters to validate[/dim]")
            
            # Check manual pages
            if check_man:
                logger.info("[dim]Checking manual page availability...[/dim]")
                man_info = self._get_man_page_info(cmd_name)
                if man_info:
                    results["man_available"] = True
                    logger.info("[green]✅ Manual page available[/green]")
                else:
                    results["man_available"] = False
                    logger.info("[yellow]⚠️ No manual page found[/yellow]")
            
            # Final status
            if results["valid"]:
                logger.info("[green]🎉 Command validation completed successfully[/green]")
            else:
                logger.info("[red]❌ Command validation failed[/red]")
                    
        except Exception as e:
            results["valid"] = False
            results["errors"].append(f"Command validation error: {str(e)}")
            logger.info(f"[red]💥 Command validation error: {str(e)}[/red]")
            
        return results

    @tool
    def detect_common_errors(
        self,
        code: str,
        check_method_calls: bool = True,
        check_parameter_passing: bool = True
    ) -> Dict[str, Any]:
        """
        Detect common coding errors and anti-patterns
        
        Args:
            code: Code to analyze for common errors
            check_method_calls: Check for method call errors
            check_parameter_passing: Check for parameter passing errors
            
        Returns:
            Common error detection results
        """
        results = {
            "errors_found": [],
            "warnings": [],
            "suggestions": [],
            "patterns_detected": []
        }
        
        # Silent detection, only output if errors found
        
        lines = code.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            # Pattern 1: Object passed to its own method (e.g., obj.method(obj=obj))
            pattern1 = re.findall(r'(\w+)\.(\w+)\([^)]*\b\1\s*=\s*\1\b[^)]*\)', line)
            if pattern1:
                for obj_name, method_name in pattern1:
                    results["errors_found"].append({
                        "line": line_num,
                        "type": "redundant_parameter",
                        "message": f"Line {line_num}: '{obj_name}' object passed to its own method '{method_name}()' - this is usually redundant",
                        "suggestion": f"Try: {obj_name}.{method_name}() without the {obj_name}= parameter"
                    })
            
            # Pattern 2: Self parameter explicitly passed
            if re.search(r'\.\w+\([^)]*\bself\s*=', line):
                results["errors_found"].append({
                    "line": line_num,
                    "type": "explicit_self",
                    "message": f"Line {line_num}: 'self' parameter passed explicitly - this is incorrect in method calls",
                    "suggestion": "Remove the self= parameter from the method call"
                })
            
            # Pattern 3: Common AnnData method errors
            if 'var_names_make_unique' in line and '=' in line:
                results["errors_found"].append({
                    "line": line_num,
                    "type": "anndata_method_error", 
                    "message": f"Line {line_num}: var_names_make_unique() doesn't take parameters - it modifies the object in place",
                    "suggestion": "Use: adata.var_names_make_unique() without parameters"
                })
            
            # Pattern 4: Duplicate variable names in arguments
            duplicate_pattern = re.findall(r'(\w+)\s*=\s*\1\b', line)
            if duplicate_pattern:
                for var_name in duplicate_pattern:
                    results["warnings"].append({
                        "line": line_num,
                        "type": "duplicate_variable",
                        "message": f"Line {line_num}: Suspicious pattern '{var_name}={var_name}' - verify this is intentional"
                    })
            
            # Pattern 5: Method calls that should be property access
            property_methods = ['shape', 'size', 'dtype', 'ndim']
            for prop in property_methods:
                if f'.{prop}()' in line:
                    results["warnings"].append({
                        "line": line_num,
                        "type": "property_as_method",
                        "message": f"Line {line_num}: '{prop}' is typically a property, not a method",
                        "suggestion": f"Use .{prop} instead of .{prop}()"
                    })
        
        # Report results
        total_issues = len(results["errors_found"]) + len(results["warnings"])
        if total_issues == 0:
            pass  # Silent when no errors
        else:
            error_count = len(results["errors_found"])
            warning_count = len(results["warnings"])
            logger.info(f"[yellow]⚠️ Found {error_count} errors and {warning_count} warnings[/yellow]")
        
        return results

    @tool
    def suggest_function_alternatives(
        self,
        function_path: str,
        module_name: Optional[str] = None,
        max_suggestions: int = 5
    ) -> Dict[str, Any]:
        """
        Suggest alternative functions when a function doesn't exist
        
        Args:
            function_path: Full function path (e.g., "scanpy.datasets.pbmc")
            module_name: Optional base module name  
            max_suggestions: Maximum number of suggestions to return
            
        Returns:
            Function suggestions with similarity scores
        """
        results = {
            "function_exists": False,
            "suggestions": [],
            "available_functions": [],
            "module_info": {},
            "help_output": None
        }
        
        try:
            pass  # Silent function search
            
            # Parse the function path
            parts = function_path.split('.')
            if len(parts) < 2:
                results["suggestions"].append({
                    "message": "Function path too short - need at least module.function format",
                    "score": 0
                })
                logger.info("[red]❌ Invalid function path format[/red]")
                return results
            
            base_module = parts[0] if not module_name else module_name
            target_function = parts[-1]  # Last part is the function name
            
            # Skip validation for likely variable method calls
            # Common variable prefixes that indicate object instances, not modules
            variable_like_prefixes = ['df', 'data', 'arr', 'series', 'matrix', 'model', 'result', 'output']
            if any(base_module.lower().startswith(prefix) for prefix in variable_like_prefixes):
                logger.info(f"[yellow]⚠️ Skipping validation for '{base_module}' - appears to be a variable, not a module[/yellow]")
                results["suggestions"].append({
                    "message": f"'{base_module}' appears to be a variable/object, not a module. Method validation skipped.",
                    "score": 0,
                    "reason": "Variable method calls are validated at runtime"
                })
                return results
            
            # Get module path (everything except the last part)  
            if len(parts) > 2:
                module_path = '.'.join(parts[:-1])
            else:
                module_path = base_module
            
            # Try to import and inspect the module
            pass  # Silent module inspection
            module_info = self._inspect_module_for_functions(module_path)
            results["module_info"] = module_info
            
            if module_info["importable"]:
                available_functions = module_info["functions"]
                results["available_functions"] = available_functions
                pass  # Silent module import success
                
                # Get help output
                help_output = self._get_module_help(module_path)
                results["help_output"] = help_output
                
                # Find similar function names
                suggestions = self._find_similar_functions(
                    target_function, 
                    available_functions, 
                    max_suggestions
                )
                results["suggestions"] = suggestions
                
                if suggestions:
                    pass  # Silent suggestion finding
                    for suggestion in suggestions[:3]:
                        logger.info(f"  [cyan]{suggestion['function']}[/cyan] (score: {suggestion['score']:.2f})")
                else:
                    logger.info("[yellow]⚠️ No similar functions found[/yellow]")
                
                # Check if the exact function exists (shouldn't if we're here)
                if target_function in available_functions:
                    results["function_exists"] = True
                    pass  # Silent function found
            else:
                pass  # Silent import failure
                results["suggestions"].append({
                    "message": f"Module '{module_path}' could not be imported: {module_info.get('error', 'Unknown error')}",
                    "score": 0
                })
                
        except Exception as e:
            results["suggestions"].append({
                "message": f"Error analyzing function: {str(e)}",
                "score": 0
            })
        
        return results

    @tool
    def validate_function_call(
        self,
        function_call: str,
        module_name: Optional[str] = None,
        check_signature: bool = True
    ) -> Dict[str, Any]:
        """
        Validate function calls and their signatures
        
        Args:
            function_call: Function call to validate (e.g., "numpy.array([1,2,3])")
            module_name: Optional module name if not included in function_call
            check_signature: Check function signature compatibility
            
        Returns:
            Function call validation results
        """
        results = {
            "valid": True,
            "function_exists": False,
            "signature_valid": False,
            "function_info": None,
            "errors": [],
            "warnings": []
        }
        
        try:
            # Parse the function call
            parsed = self._parse_function_call(function_call)
            if not parsed:
                results["valid"] = False
                results["errors"].append("Could not parse function call")
                return results
                
            func_name = parsed["function"]
            args = parsed["args"]
            kwargs = parsed["kwargs"]
            
            # Add module prefix if provided
            if module_name and "." not in func_name:
                full_func_name = f"{module_name}.{func_name}"
            else:
                full_func_name = func_name
            
            # Check if function exists
            func_info = self._get_function_info(full_func_name)
            results["function_info"] = func_info
            
            if func_info and func_info["exists"]:
                results["function_exists"] = True
                
                # Validate signature if requested
                if check_signature and func_info["signature"]:
                    sig_validation = self._validate_function_signature(
                        func_info["signature"], args, kwargs
                    )
                    results["signature_valid"] = sig_validation["valid"]
                    if not sig_validation["valid"]:
                        results["errors"].extend(sig_validation["errors"])
                    results["warnings"].extend(sig_validation["warnings"])
            else:
                results["valid"] = False
                results["errors"].append(f"Function '{full_func_name}' not found")
                
                # Automatically get suggestions for non-existent functions
                try:
                    suggestions_result = self.suggest_function_alternatives(
                        function_path=full_func_name,
                        module_name=module_name,
                        max_suggestions=3
                    )
                    
                    if suggestions_result["suggestions"]:
                        results["function_suggestions"] = suggestions_result["suggestions"]
                        suggestion_text = ", ".join([
                            f"{s['function']} ({s['score']:.2f})" 
                            for s in suggestions_result["suggestions"][:3]
                        ])
                        results["errors"].append(f"Did you mean one of: {suggestion_text}?")
                        
                except Exception:
                    pass  # Don't fail the main validation if suggestions fail
                
        except Exception as e:
            results["valid"] = False
            results["errors"].append(f"Function validation error: {str(e)}")
            
        return results

    @tool
    def validate_imports(
        self,
        imports: List[str],
        suggest_alternatives: bool = True
    ) -> Dict[str, Any]:
        """
        Validate import statements and suggest alternatives
        
        Args:
            imports: List of import statements to validate
            suggest_alternatives: Suggest alternative packages if imports fail
            
        Returns:
            Import validation results
        """
        results = {
            "valid": True,
            "imports": [],
            "missing": [],
            "suggestions": []
        }
        
        for import_stmt in imports:
            try:
                import_info = self._validate_single_import(import_stmt)
                results["imports"].append(import_info)
                
                if not import_info["available"]:
                    results["missing"].append(import_stmt)
                    
                    if suggest_alternatives:
                        alternatives = self._suggest_import_alternatives(import_stmt)
                        if alternatives:
                            results["suggestions"].extend(alternatives)
                            
            except Exception as e:
                results["imports"].append({
                    "statement": import_stmt,
                    "available": False,
                    "error": str(e)
                })
                results["missing"].append(import_stmt)
        
        if results["missing"]:
            results["valid"] = False
            
        return results

    @tool
    def check_code_style(
        self,
        code: str,
        style_guide: str = "pep8",
        fix_suggestions: bool = True
    ) -> Dict[str, Any]:
        """
        Check code style and provide improvement suggestions
        
        Args:
            code: Code to check
            style_guide: Style guide to use (pep8, google, etc.)
            fix_suggestions: Provide fix suggestions
            
        Returns:
            Style checking results
        """
        results = {
            "compliant": True,
            "issues": [],
            "suggestions": [],
            "metrics": {}
        }
        
        try:
            # Basic style checks
            style_issues = self._check_basic_style(code)
            results["issues"].extend(style_issues)
            
            if style_issues:
                results["compliant"] = False
            
            # Code metrics
            metrics = self._calculate_code_metrics(code)
            results["metrics"] = metrics
            
            # Generate suggestions
            if fix_suggestions:
                suggestions = self._generate_style_suggestions(code, style_issues)
                results["suggestions"] = suggestions
                
        except Exception as e:
            results["issues"].append(f"Style check error: {str(e)}")
            results["compliant"] = False
            
        return results

    # Private helper methods
    
    def _check_syntax(self, code: str) -> Dict[str, Any]:
        """Check Python syntax"""
        try:
            ast.parse(code)
            return {"valid": True, "errors": []}
        except SyntaxError as e:
            return {
                "valid": False,
                "errors": [f"Syntax error at line {e.lineno}: {e.msg}"]
            }
    
    def _check_imports(self, code: str, safe_mode: bool) -> List[Dict[str, Any]]:
        """Check import statements"""
        imports = []
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for name in node.names:
                        import_info = self._validate_single_import(f"import {name.name}")
                        imports.append(import_info)
                elif isinstance(node, ast.ImportFrom):
                    if node.names:
                        for name in node.names:
                            import_stmt = f"from {node.module or ''} import {name.name}"
                            import_info = self._validate_single_import(import_stmt)
                            imports.append(import_info)
        except Exception as e:
            imports.append({
                "name": "parse_error",
                "available": False,
                "error": str(e)
            })
        
        return imports
    
    def _validate_single_import(self, import_stmt: str) -> Dict[str, Any]:
        """Validate a single import statement"""
        try:
            # Handle different formats: import statements vs simple module names
            if import_stmt.startswith("import "):
                module_name = import_stmt[7:].split()[0].split('.')[0]
            elif import_stmt.startswith("from "):
                module_name = import_stmt.split()[1].split('.')[0]
            else:
                # Assume it's just a module name
                module_name = import_stmt.split('.')[0]
            
            # Try to find module
            try:
                importlib.util.find_spec(module_name)
                return {
                    "statement": import_stmt,
                    "name": module_name,
                    "available": True
                }
            except (ImportError, AttributeError, ValueError, ModuleNotFoundError):
                return {
                    "statement": import_stmt, 
                    "name": module_name,
                    "available": False
                }
        except Exception as e:
            return {
                "statement": import_stmt,
                "available": False,
                "error": str(e)
            }
    
    def _check_functions(self, code: str, safe_mode: bool) -> List[Dict[str, Any]]:
        """Check function calls in code"""
        functions = []
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    func_name = None
                    
                    if isinstance(node.func, ast.Name):
                        func_name = node.func.id
                    elif isinstance(node.func, ast.Attribute):
                        # Handle attribute access like obj.method()
                        if isinstance(node.func.value, ast.Name):
                            func_name = f"{node.func.value.id}.{node.func.attr}"
                        else:
                            # For more complex expressions, just use the attribute name
                            func_name = f"<complex>.{node.func.attr}"
                    
                    if func_name:
                        func_info = {
                            "name": func_name,
                            "line": node.lineno if hasattr(node, 'lineno') else None,
                            "issues": []
                        }
                        
                        # Basic validation - check if it's a reasonable function name
                        if not func_name.startswith('<complex>'):
                            # Simple check for valid Python identifiers
                            parts = func_name.split('.')
                            for part in parts:
                                if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', part):
                                    func_info["issues"].append(f"Invalid identifier in function name: {part}")
                                    break
                        
                        functions.append(func_info)
                    
        except Exception as e:
            functions.append({
                "name": "parse_error",
                "issues": [f"Could not parse functions: {str(e)}"]
            })
        
        return functions
    
    def _check_command_exists(self, command: str) -> Dict[str, Any]:
        """Check if command exists in PATH"""
        try:
            result = subprocess.run(['which', command], 
                                  capture_output=True, text=True, timeout=5)
            exists = result.returncode == 0
            
            suggestions = []
            if not exists:
                # Try to suggest similar commands
                similar_commands = self._find_similar_commands(command)
                suggestions = similar_commands
            
            return {
                "exists": exists,
                "path": result.stdout.strip() if exists else None,
                "suggestions": suggestions
            }
        except Exception as e:
            return {"exists": False, "error": str(e), "suggestions": []}
    
    def _get_command_help(self, command: str) -> Dict[str, Any]:
        """Get command help information"""
        help_info = {}
        
        for help_flag in ['--help', '-h', 'help']:
            try:
                result = subprocess.run([command, help_flag], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0 and result.stdout.strip():
                    help_info[help_flag] = result.stdout
                    break
                elif result.stderr.strip():
                    help_info[help_flag] = result.stderr
            except Exception:
                continue
        
        return help_info
    
    def _validate_command_parameters(self, command: str, args: List[str], help_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Validate command parameters against help information"""
        param_results = []
        
        if not help_info:
            return param_results
        
        help_text = next(iter(help_info.values()), "")
        
        for arg in args:
            param_info = {
                "parameter": arg,
                "valid": True,
                "message": "Parameter validated"
            }
            
            # Basic validation - check if parameter looks like a valid flag
            if arg.startswith('-'):
                # Check if flag is mentioned in help
                if arg not in help_text and arg.replace('=', ' ') not in help_text:
                    param_info["valid"] = False
                    param_info["message"] = f"Parameter '{arg}' not found in help documentation"
            
            param_results.append(param_info)
        
        return param_results
    
    def _get_man_page_info(self, command: str) -> Optional[str]:
        """Get manual page information for command"""
        try:
            result = subprocess.run(['man', command], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                return result.stdout
        except Exception:
            pass
        return None
    
    def _parse_function_call(self, func_call: str) -> Optional[Dict[str, Any]]:
        """Parse function call string"""
        try:
            # Fixed regex pattern - removed extra backslashes
            match = re.match(r'([a-zA-Z_][a-zA-Z0-9_.]*)\s*\((.*?)\)', func_call.strip())
            if match:
                func_name = match.group(1)
                args_str = match.group(2)
                
                # Parse arguments and keyword arguments
                args = []
                kwargs = {}
                
                if args_str.strip():
                    # Split by comma, but be careful with nested structures
                    arg_parts = []
                    current_arg = ""
                    paren_count = 0
                    
                    for char in args_str:
                        if char == '(':
                            paren_count += 1
                        elif char == ')':
                            paren_count -= 1
                        elif char == ',' and paren_count == 0:
                            arg_parts.append(current_arg.strip())
                            current_arg = ""
                            continue
                        current_arg += char
                    
                    if current_arg.strip():
                        arg_parts.append(current_arg.strip())
                    
                    # Classify as args or kwargs
                    for arg_part in arg_parts:
                        if '=' in arg_part and not any(op in arg_part for op in ['==', '!=', '<=', '>=', '+=', '-=', '*=', '/=']):
                            # This looks like a keyword argument
                            key, value = arg_part.split('=', 1)
                            kwargs[key.strip()] = value.strip()
                        else:
                            # This is a positional argument
                            args.append(arg_part)
                
                return {
                    "function": func_name,
                    "args": args,
                    "kwargs": kwargs
                }
        except Exception:
            pass
        return None
    
    def _get_function_info(self, func_name: str) -> Dict[str, Any]:
        """Get information about a function"""
        try:
            if '.' in func_name:
                module_name, function_name = func_name.rsplit('.', 1)
                module = importlib.import_module(module_name)
                if hasattr(module, function_name):
                    func = getattr(module, function_name)
                    return {
                        "exists": True,
                        "signature": inspect.signature(func) if callable(func) else None,
                        "doc": inspect.getdoc(func),
                        "module": module_name
                    }
            else:
                # Check built-ins
                if hasattr(__builtins__, func_name):
                    func = getattr(__builtins__, func_name)
                    return {
                        "exists": True,
                        "signature": inspect.signature(func) if callable(func) else None,
                        "doc": inspect.getdoc(func),
                        "module": "builtins"
                    }
        except Exception:
            pass
        
        return {"exists": False}
    
    def _validate_function_signature(self, signature, args: List[str], kwargs: Dict[str, str]) -> Dict[str, Any]:
        """Validate function call against signature"""
        errors = []
        warnings = []
        valid = True
        
        try:
            if signature:
                # Get signature parameters
                sig_params = list(signature.parameters.keys())
                
                # Check for common mistakes
                # 1. Check if self/cls parameter is being passed explicitly
                if sig_params and sig_params[0] in ['self', 'cls']:
                    for arg in args:
                        if arg.strip() in ['self', 'cls'] or 'self.' in arg or 'cls.' in arg:
                            errors.append(f"Passing '{arg}' as argument - 'self' is implicit in method calls")
                            valid = False
                    
                    # Check if first parameter name is used as keyword argument
                    first_param = sig_params[0]
                    for kwarg_name in kwargs:
                        if kwarg_name == first_param:
                            errors.append(f"'{first_param}' parameter is implicit in method calls, should not be passed as keyword argument")
                            valid = False
                
                # 2. Check for duplicate object passing (like adata=adata)
                for kwarg_name, kwarg_value in kwargs.items():
                    if kwarg_name.lower() == kwarg_value.lower():
                        warnings.append(f"Suspicious keyword argument '{kwarg_name}={kwarg_value}' - check if this parameter is needed")
                    
                    # Check if parameter exists in signature
                    if kwarg_name not in sig_params:
                        errors.append(f"Parameter '{kwarg_name}' not found in function signature")
                        valid = False
                
                # 3. Check argument count (basic check)
                required_params = [p for p, param in signature.parameters.items() 
                                 if param.default == param.empty and p not in ['self', 'cls']]
                
                if len(args) < len(required_params):
                    missing = required_params[len(args):]
                    warnings.append(f"Possibly missing required parameters: {missing}")
                
        except Exception as e:
            warnings.append(f"Signature validation error: {str(e)}")
        
        return {
            "valid": valid,
            "errors": errors,
            "warnings": warnings
        }
    
    def _suggest_import_alternatives(self, import_stmt: str) -> List[str]:
        """Suggest alternative imports"""
        suggestions = []
        
        # Common alternative mappings
        alternatives = {
            'cv2': ['opencv-python', 'opencv-contrib-python'],
            'sklearn': ['scikit-learn'],
            'PIL': ['Pillow'],
            'yaml': ['PyYAML'],
            'bs4': ['beautifulsoup4'],
            'requests': ['urllib3'],
        }
        
        # Extract module name from import
        if 'import ' in import_stmt:
            module = import_stmt.split('import ')[1].split()[0].split('.')[0]
            if module in alternatives:
                suggestions.extend([f"Try installing: pip install {alt}" for alt in alternatives[module]])
        
        return suggestions
    
    def _find_similar_commands(self, command: str) -> List[str]:
        """Find similar commands in PATH"""
        try:
            # Get all commands in PATH
            result = subprocess.run(['ls', '/usr/bin', '/usr/local/bin'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                all_commands = result.stdout.split()
                # Find commands with similar names (simple similarity)
                similar = [cmd for cmd in all_commands 
                          if abs(len(cmd) - len(command)) <= 2 and 
                          any(c in command for c in cmd[:3])][:5]
                return similar
        except Exception:
            pass
        return []
    
    def _check_basic_style(self, code: str) -> List[str]:
        """Basic style checking"""
        issues = []
        lines = code.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Check line length
            if len(line) > 88:  # PEP 8 recommends 79, but 88 is more practical
                issues.append(f"Line {i} exceeds 88 characters")
            
            # Check for trailing whitespace
            if line.rstrip() != line:
                issues.append(f"Line {i} has trailing whitespace")
            
            # Check for tabs
            if '\t' in line:
                issues.append(f"Line {i} contains tabs (use spaces)")
        
        return issues
    
    def _calculate_code_metrics(self, code: str) -> Dict[str, Any]:
        """Calculate basic code metrics"""
        lines = code.split('\n')
        return {
            "lines_total": len(lines),
            "lines_non_empty": len([line for line in lines if line.strip()]),
            "lines_comments": len([line for line in lines if line.strip().startswith('#')]),
            "max_line_length": max(len(line) for line in lines) if lines else 0,
            "avg_line_length": sum(len(line) for line in lines) / len(lines) if lines else 0
        }
    
    def _generate_style_suggestions(self, code: str, issues: List[str]) -> List[str]:
        """Generate style improvement suggestions"""
        suggestions = []
        
        if any("exceeds" in issue for issue in issues):
            suggestions.append("Consider breaking long lines using parentheses or backslashes")
        
        if any("trailing whitespace" in issue for issue in issues):
            suggestions.append("Remove trailing whitespace from lines")
        
        if any("tabs" in issue for issue in issues):
            suggestions.append("Replace tabs with 4 spaces for indentation")
        
        return suggestions
    
    def _inspect_module_for_functions(self, module_path: str) -> Dict[str, Any]:
        """Inspect a module to get available functions and attributes using Python environment"""
        result = {
            "importable": False,
            "functions": [],
            "attributes": [],
            "submodules": [],
            "error": None
        }
        
        try:
            # Use subprocess to run Python code in the actual environment
            # This handles cases like pd (pandas alias) correctly
            inspection_code = f"""
import sys
import importlib

# Common aliases mapping
alias_mapping = {{
    'pd': 'pandas',
    'np': 'numpy',
    'plt': 'matplotlib.pyplot',
    'sc': 'scanpy',
    'sns': 'seaborn',
    'tf': 'tensorflow',
    'cv2': 'cv2',
    'sk': 'sklearn',
    'sp': 'scipy'
}}

module_path = '{module_path}'

try:
    # First, try to handle common aliases
    if module_path in alias_mapping:
        actual_module_path = alias_mapping[module_path]
        try:
            module = importlib.import_module(actual_module_path)
            print(f"ALIAS_RESOLVED: {{module_path}} -> {{actual_module_path}}")
        except ImportError:
            raise Exception(f"Alias '{{module_path}}' maps to '{{actual_module_path}}' but module not available")
    else:
        # Try direct import
        module = importlib.import_module(module_path)
    
    # Get all attributes
    attrs = dir(module)
    functions = []
    attributes = []
    submodules = []
    
    for attr_name in attrs:
        if attr_name.startswith('_'):
            continue
        
        try:
            attr = getattr(module, attr_name)
            if callable(attr):
                functions.append(attr_name)
            elif hasattr(attr, '__module__') and hasattr(attr, '__name__'):
                submodules.append(attr_name)
            else:
                attributes.append(attr_name)
        except Exception:
            continue
    
    print("SUCCESS")
    print("FUNCTIONS:", "|".join(functions))
    print("ATTRIBUTES:", "|".join(attributes))
    print("SUBMODULES:", "|".join(submodules))
    
except Exception as e:
    print("ERROR:", str(e))
"""
            
            # Run the inspection code
            process = subprocess.run(
                [sys.executable, '-c', inspection_code],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if process.returncode == 0:
                lines = process.stdout.strip().split('\n')
                success_found = False
                
                for i, line in enumerate(lines):
                    if line.startswith("ALIAS_RESOLVED:"):
                        # Record that we resolved an alias
                        result["alias_resolved"] = line[15:].strip()
                    elif line == "SUCCESS":
                        success_found = True
                        result["importable"] = True
                        # Process the remaining lines
                        for remaining_line in lines[i+1:]:
                            if remaining_line.startswith("FUNCTIONS:"):
                                funcs = remaining_line[10:].strip()
                                if funcs:
                                    result["functions"] = funcs.split('|')
                            elif remaining_line.startswith("ATTRIBUTES:"):
                                attrs = remaining_line[11:].strip()
                                if attrs:
                                    result["attributes"] = attrs.split('|')
                            elif remaining_line.startswith("SUBMODULES:"):
                                subs = remaining_line[11:].strip()
                                if subs:
                                    result["submodules"] = subs.split('|')
                        break
                
                if not success_found:
                    result["error"] = f"Inspection failed for module '{module_path}'"
            else:
                error_lines = process.stderr.strip().split('\n')
                if error_lines and error_lines[-1].startswith("ERROR:"):
                    result["error"] = error_lines[-1][6:].strip()
                else:
                    result["error"] = f"Could not inspect module '{module_path}': {process.stderr}"
            
        except Exception as e:
            result["error"] = f"Inspection error: {str(e)}"
        
        return result
    
    def _get_module_help(self, module_path: str) -> Optional[str]:
        """Get help documentation for a module"""
        try:
            module = importlib.import_module(module_path)
            
            # Capture help output
            old_stdout = sys.stdout
            sys.stdout = help_buffer = StringIO()
            
            try:
                help(module)
                help_text = help_buffer.getvalue()
            finally:
                sys.stdout = old_stdout
            
            return help_text if help_text.strip() else None
            
        except Exception:
            return None
    
    def _find_similar_functions(self, target: str, available: List[str], max_suggestions: int) -> List[Dict[str, Any]]:
        """Find functions similar to the target using string similarity"""
        suggestions = []
        
        # Use difflib to find similar strings
        matches = difflib.get_close_matches(
            target.lower(), 
            [func.lower() for func in available], 
            n=max_suggestions * 2,  # Get more matches to filter
            cutoff=0.3  # Lower cutoff to catch more possibilities
        )
        
        # Create suggestion objects with scores
        for match in matches:
            # Find the original case version
            original_match = None
            for func in available:
                if func.lower() == match:
                    original_match = func
                    break
            
            if original_match:
                # Calculate similarity score
                score = difflib.SequenceMatcher(None, target.lower(), match).ratio()
                
                suggestions.append({
                    "function": original_match,
                    "score": score,
                    "reason": f"Similar to '{target}' (similarity: {score:.2f})"
                })
        
        # Also look for functions containing the target as substring
        substring_matches = []
        for func in available:
            if target.lower() in func.lower() or func.lower() in target.lower():
                if func.lower() not in [s["function"].lower() for s in suggestions]:
                    score = 0.8 if target.lower() in func.lower() else 0.6
                    substring_matches.append({
                        "function": func,
                        "score": score,
                        "reason": f"Contains '{target}' or vice versa"
                    })
        
        # Combine and sort by score
        all_suggestions = suggestions + substring_matches
        all_suggestions.sort(key=lambda x: x["score"], reverse=True)
        
        # Return top suggestions
        return all_suggestions[:max_suggestions]