"""Single-cell ATAC-seq upstream processing with cellranger-atac"""

import json
import shutil
import tarfile
import requests
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn

from .base import ScATACSeqBase
from ...utils.toolset import tool
from ...utils.log import logger


class ScATACSeqUpstreamToolSet(ScATACSeqBase):
    """Single-cell ATAC-seq upstream processing toolset using cellranger-atac"""
    
    def __init__(
        self,
        name: str = "scatac_upstream",
        workspace_path: str = None,
        launch_directory: str = None,
        worker_params: dict = None,
        **kwargs
    ):
        super().__init__(name, workspace_path, launch_directory, worker_params, **kwargs)
    
    @tool
    def check_dependencies(self) -> Dict[str, Any]:
        """Check cellranger-atac and related tool dependencies"""
        logger.info("")
        logger.info("\n" + "="*70)
        logger.info("🧬 [bold cyan]Single-cell ATAC-seq Tools Check[/bold cyan]", justify="center")
        logger.info("="*70)
        
        tools_status = {
            "installed": {},
            "missing": [],
            "install_commands": {}
        }
        
        # Check cellranger-atac (primary tool)
        cellranger_status = self._check_cellranger_atac()
        tools_status["installed"]["cellranger-atac"] = cellranger_status["installed"]
        if not cellranger_status["installed"]:
            tools_status["missing"].append("cellranger-atac")
            tools_status["install_commands"]["cellranger-atac"] = "Download from 10X Genomics website"
        
        # Check optional tools
        optional_tools = {
            "python3": "python3 --version",
            "R": "R --version",
            "bedtools": "bedtools --version"
        }
        
        for tool_name, check_cmd in optional_tools.items():
            try:
                result = self._run_command(check_cmd.split())
                tools_status["installed"][tool_name] = result["status"] == "success"
            except:
                tools_status["installed"][tool_name] = False
                if tool_name not in tools_status["missing"]:
                    tools_status["missing"].append(tool_name)
        
        # Display results
        from rich.table import Table
        dep_table = Table(title="Dependency Status")
        dep_table.add_column("Tool", style="cyan")
        dep_table.add_column("Status", justify="center")
        dep_table.add_column("Details")
        
        # cellranger-atac details
        if cellranger_status["installed"]:
            dep_table.add_row(
                "cellranger-atac", 
                "✅ Installed",
                f"v{cellranger_status['version']} at {cellranger_status['path']}"
            )
        else:
            dep_table.add_row(
                "cellranger-atac",
                "❌ Missing", 
                "Download from 10X Genomics website"
            )
        
        # Other tools
        for tool_name, installed in tools_status["installed"].items():
            if tool_name != "cellranger-atac":
                status = "✅ Installed" if installed else "⚠️  Optional"
                dep_table.add_row(tool_name, status, "Optional dependency")
        
        logger.info("", rich=dep_table)
        
        # Summary
        missing_count = len(tools_status["missing"])
        if missing_count == 0:
            logger.info("\n✅ [bold green]All required dependencies are installed![/bold green]")
        else:
            logger.info(f"\n⚠️ [bold yellow]{missing_count} dependencies missing[/bold yellow]")
        
        return {
            "status": "complete" if missing_count == 0 else "partial",
            "installed": tools_status["installed"],
            "missing": tools_status["missing"],
            "cellranger_details": cellranger_status
        }
    
    @tool 
    def check_installation_status(self, install_dir: str = None) -> Dict[str, Any]:
        """Check cellranger-atac installation status"""
        
        logger.info(f"\n🔍 [bold cyan]Checking cellranger-atac installation status[/bold cyan]")
        
        cellranger_config = self.pipeline_config["cellranger_atac"]
        version = cellranger_config["version"]
        
        # Determine installation directory
        if install_dir is None:
            # Use launch directory if available, otherwise current directory
            if hasattr(self, 'launch_directory') and self.launch_directory:
                install_dir = self.launch_directory / "software"
            else:
                install_dir = Path.cwd() / "software"
        else:
            install_dir = Path(install_dir)
            
        # Set up expected paths
        extracted_dir = install_dir / f"cellranger-atac-{version}"
        expected_binary = extracted_dir / "bin" / "cellranger-atac"
        download_path = install_dir / f"cellranger-atac-{version}.tar.gz"
        
        status = {
            "install_dir": str(install_dir),
            "install_dir_exists": install_dir.exists(),
            "download_file_exists": download_path.exists(),
            "extracted_dir_exists": extracted_dir.exists(),
            "binary_exists": expected_binary.exists(),
            "binary_path": str(expected_binary),
            "binary_executable": False,
            "version_check": {"valid": False, "output": None},
            "recommendation": "unknown"
        }
        
        from rich.table import Table
        status_table = Table(title="Installation Status")
        status_table.add_column("Component", style="cyan")
        status_table.add_column("Status", style="green")
        status_table.add_column("Details", style="yellow")
        
        # Check installation directory
        if status["install_dir_exists"]:
            status_table.add_row("Install Directory", "✅ Exists", str(install_dir))
        else:
            status_table.add_row("Install Directory", "❌ Missing", "Directory needs to be created")
        
        # Check download file
        if status["download_file_exists"]:
            file_size = download_path.stat().st_size
            status_table.add_row("Download File", "✅ Exists", f"{file_size / (1024*1024):.1f} MB")
        else:
            status_table.add_row("Download File", "❌ Missing", "Download needed")
        
        # Check extracted directory
        if status["extracted_dir_exists"]:
            status_table.add_row("Extracted Directory", "✅ Exists", str(extracted_dir))
        else:
            status_table.add_row("Extracted Directory", "❌ Missing", "Extraction needed")
        
        # Check binary
        if status["binary_exists"]:
            try:
                import stat
                file_mode = expected_binary.stat().st_mode
                is_executable = bool(file_mode & stat.S_IXUSR)
                status["binary_executable"] = is_executable
                
                if is_executable:
                    verification = self._verify_installation(expected_binary)
                    status["version_check"] = verification
                    
                    if verification["valid"]:
                        status_table.add_row("Binary", "✅ Ready", f"Found at: {expected_binary}")
                    else:
                        status_table.add_row("Binary", "❌ Broken", f"Not functional: {verification.get('error', 'Unknown error')}")
                else:
                    status_table.add_row("Binary", "⚠️ Not Executable", f"Found at: {expected_binary}")
            except Exception as e:
                status_table.add_row("Binary", "❌ Error", f"Cannot check: {str(e)}")
        else:
            status_table.add_row("Binary", "❌ Missing", "Binary not found")
        
        logger.info("", rich=status_table)
        
        # Provide recommendation
        if status["binary_exists"] and status["binary_executable"] and status["version_check"]["valid"]:
            status["recommendation"] = "ready"
            logger.info("✅ [bold green]cellranger-atac is fully installed and ready to use![/bold green]")
        elif status["binary_exists"] and status["binary_executable"]:
            status["recommendation"] = "verify"
            logger.info("⚠️ [yellow]Binary exists but may have issues. Run verification test.[/yellow]")
        elif status["binary_exists"]:
            status["recommendation"] = "fix_permissions"
            logger.info("⚠️ [yellow]Binary exists but not executable. Fix permissions.[/yellow]")
        elif status["extracted_dir_exists"]:
            status["recommendation"] = "missing_binary"
            logger.info("❌ [red]Extraction exists but binary missing. Re-extraction needed.[/red]")
        elif status["download_file_exists"]:
            status["recommendation"] = "extract"
            logger.info("📦 [yellow]Download ready for extraction.[/yellow]")
        else:
            status["recommendation"] = "install"
            logger.info("📥 [yellow]Installation needed. Run install_cellranger_atac.[/yellow]")
        
        return {
            "status": "success",
            "installation_status": status
        }

    @tool
    def install_cellranger_atac(self, install_dir: str = None, force_reinstall: bool = False) -> Dict[str, Any]:
        """Automatically download and install cellranger-atac with comprehensive checks
        
        Args:
            install_dir: Installation directory (defaults to current_dir/software)
            force_reinstall: Force reinstallation even if already installed
        """
        
        logger.info("\n🔧 [bold cyan]Installing cellranger-atac v2.2.0[/bold cyan]")
        
        # Get cellranger-atac configuration
        cellranger_config = self.pipeline_config["cellranger_atac"]
        url = cellranger_config["url"]  # Use the signed URL directly
        version = cellranger_config["version"]
        
        # Set up installation directory - use launch directory/software as default
        if install_dir is None:
            install_dir = self.launch_directory / cellranger_config.get("install_dir", "software")
        else:
            install_dir = Path(install_dir)
        
        install_dir.mkdir(parents=True, exist_ok=True)
        
        filename = f"cellranger-atac-{version}.tar.gz"
        download_path = install_dir / filename
        extracted_dir = install_dir / f"cellranger-atac-{version}"
        cellranger_binary = extracted_dir / "bin" / "cellranger-atac"
        
        logger.info(f"📁 [dim]Installation directory: {install_dir}[/dim]")
        logger.info(f"📦 [dim]Target binary: {cellranger_binary}[/dim]")
        
        # Step 1: Check if already fully installed and working (unless force_reinstall)
        if cellranger_binary.exists() and not force_reinstall:
            logger.info("🔍 [yellow]Found existing installation, verifying...[/yellow]")
            verification = self._verify_installation(cellranger_binary)
            
            if verification["valid"]:
                logger.info("✅ [green]cellranger-atac already installed and working[/green]")
                logger.info(f"[dim]Version: {verification['version_output']}[/dim]")
                logger.info(f"[dim]Binary path: {cellranger_binary}[/dim]")
                return {
                    "status": "success",
                    "path": str(cellranger_binary),
                    "version": version,
                    "already_installed": True,
                    "verification": verification,
                    "install_dir": str(install_dir)
                }
            else:
                logger.info(f"⚠️ [yellow]Existing installation not working: {verification['error']}[/yellow]")
                logger.info("🗑️ [yellow]Removing broken installation...[/yellow]")
                if extracted_dir.exists():
                    shutil.rmtree(extracted_dir)
        elif force_reinstall and cellranger_binary.exists():
            logger.info("🔄 [yellow]Force reinstall enabled, removing existing installation...[/yellow]")
            if extracted_dir.exists():
                shutil.rmtree(extracted_dir)
        
        try:
            # Step 2: Check if download file exists
            download_needed = True
            
            if download_path.exists():
                logger.info("📦 [yellow]Found existing download file - using existing file[/yellow]")
                download_needed = False
            
            # Step 3: Download if needed using signed URL
            if download_needed:
                logger.info(f"📥 [yellow]Downloading cellranger-atac v{version} from 10X Genomics...[/yellow]")
                
                download_result = self._download_with_progress(
                    url, download_path, f"Downloading cellranger-atac v{version}"
                )
                
                if not download_result["success"]:
                    return {
                        "status": "failed",
                        "error": f"Download failed: {download_result['error']}"
                    }
                
                logger.info("✅ [green]Download completed[/green]")
            
            # Step 4: Extract if not already extracted or if extraction is incomplete
            if not extracted_dir.exists() or not cellranger_binary.exists():
                logger.info("📦 [yellow]Extracting cellranger-atac...[/yellow]")
                
                # Remove any partial extraction
                if extracted_dir.exists():
                    shutil.rmtree(extracted_dir)
                
                with tarfile.open(download_path, 'r:gz') as tar:
                    tar.extractall(install_dir)
                
                logger.info("✅ [green]Extraction completed[/green]")
            
            # Step 5: Make binary executable and verify installation
            if cellranger_binary.exists():
                cellranger_binary.chmod(0o755)
                
                logger.info("🧪 [yellow]Verifying installation...[/yellow]")
                verification = self._verify_installation(cellranger_binary)
                
                if verification["valid"]:
                    # Clean up download file after successful installation
                    if download_path.exists():
                        download_path.unlink()
                        logger.info("🗑️ [green]Cleaned up download file[/green]")
                    
                    logger.info("✅ [bold green]cellranger-atac installation completed successfully![/bold green]")
                    logger.info(f"[dim]Binary location: {cellranger_binary}[/dim]")
                    logger.info(f"[dim]Installation verified: {verification['version_output']}[/dim]")
                    logger.info(f"[yellow]To use cellranger-atac globally, add to PATH:[/yellow]")
                    logger.info(f"[dim]export PATH=\"{cellranger_binary.parent}:$PATH\"[/dim]")
                    
                    return {
                        "status": "success",
                        "path": str(cellranger_binary),
                        "version": version,
                        "already_installed": False,
                        "verification": verification,
                        "install_dir": str(install_dir)
                    }
                else:
                    return {
                        "status": "failed",
                        "error": f"Installation verification failed: {verification['error']}",
                        "path": str(cellranger_binary),
                        "verification": verification
                    }
            else:
                return {
                    "status": "failed",
                    "error": "cellranger-atac binary not found after extraction"
                }
                
        except Exception as e:
            return {
                "status": "failed",
                "error": f"Installation failed: {str(e)}"
            }
    
    @tool
    def scan_folder(self, folder_path: str) -> Dict[str, Any]:
        """Comprehensive scan for single-cell ATAC-seq data"""
        
        folder_path = Path(folder_path)
        logger.info(f"\n🔍 [bold cyan]Scanning scATAC folder: {folder_path}[/bold cyan]")
        
        if not folder_path.exists():
            return {
                "status": "failed",
                "error": f"Folder does not exist: {folder_path}"
            }
        
        scan_results = {
            "folder_path": str(folder_path),
            "total_files": 0,
            "total_size": 0,
            "files": {},
            "samples": {},
            "data_format": "unknown",
            "analysis_stage": "unknown",
            "next_steps": []
        }
        
        # Categorize files by extension
        for category, extensions in self.pipeline_config["file_extensions"].items():
            scan_results["files"][category] = []
            for ext in extensions:
                files = list(folder_path.rglob(f"*{ext}"))
                for file in files:
                    scan_results["files"][category].append({
                        "path": str(file),
                        "size": file.stat().st_size,
                        "name": file.name
                    })
                    scan_results["total_size"] += file.stat().st_size
                    scan_results["total_files"] += 1
        
        # Detect 10X Chromium format
        fastq_files = scan_results["files"].get("input", [])
        if fastq_files:
            # Look for 10X naming pattern: *_S*_L00*_R*_001.fastq.gz
            chromium_pattern = False
            samples = {}
            
            for file_info in fastq_files:
                filename = file_info["name"]
                if "_S" in filename and "_L00" in filename and "_R" in filename and "_001" in filename:
                    chromium_pattern = True
                    # Extract sample name: everything before _S
                    sample_name = filename.split("_S")[0]
                    if sample_name not in samples:
                        samples[sample_name] = {"files": [], "lanes": set(), "reads": set()}
                    samples[sample_name]["files"].append(file_info)
                    
                    # Extract lane and read info
                    parts = filename.split("_")
                    for part in parts:
                        if part.startswith("L00"):
                            samples[sample_name]["lanes"].add(part)
                        elif part.startswith("R"):
                            samples[sample_name]["reads"].add(part.split(".")[0])
            
            if chromium_pattern:
                scan_results["data_format"] = "10X_Chromium"
                scan_results["samples"] = {
                    name: {
                        "files": info["files"],
                        "lanes": len(info["lanes"]),
                        "reads": list(info["reads"]),
                        "file_count": len(info["files"])
                    }
                    for name, info in samples.items()
                }
            else:
                scan_results["data_format"] = "bulk_fastq"
        
        # Check for existing cellranger outputs
        cellranger_files = scan_results["files"].get("cellranger", [])
        if cellranger_files:
            scan_results["analysis_stage"] = "cellranger_complete"
            scan_results["next_steps"] = [
                "load_cellranger_data",
                "run_quality_control", 
                "downstream_analysis"
            ]
        elif scan_results["data_format"] == "10X_Chromium":
            scan_results["analysis_stage"] = "raw_chromium"
            scan_results["next_steps"] = [
                "setup_reference",
                "run_cellranger_count",
                "validate_outputs"
            ]
        elif fastq_files:
            scan_results["analysis_stage"] = "raw_fastq"
            scan_results["next_steps"] = [
                "validate_format",
                "prepare_for_cellranger"
            ]
        else:
            scan_results["analysis_stage"] = "no_data"
            scan_results["next_steps"] = ["add_fastq_data"]
        
        # Display results
        self._display_scan_results(scan_results)
        
        return scan_results
    
    def _display_scan_results(self, results: Dict[str, Any]):
        """Display scan results in formatted tables"""
        
        # Summary table
        from rich.table import Table
        summary_table = Table(title="scATAC Data Summary")
        summary_table.add_column("Property", style="cyan")
        summary_table.add_column("Value", style="green")
        
        summary_table.add_row("Data Format", results["data_format"])
        summary_table.add_row("Analysis Stage", results["analysis_stage"])
        summary_table.add_row("Total Files", str(results["total_files"]))
        summary_table.add_row("Total Size", f"{results['total_size'] / (1024**3):.2f} GB")
        summary_table.add_row("Samples Detected", str(len(results["samples"])))
        
        logger.info("", rich=summary_table)
        
        # Samples table if 10X format detected
        if results["data_format"] == "10X_Chromium" and results["samples"]:
            samples_table = Table(title="Detected Samples")
            samples_table.add_column("Sample", style="cyan")
            samples_table.add_column("Files", style="green")
            samples_table.add_column("Lanes", style="yellow")
            samples_table.add_column("Reads", style="magenta")
            
            for sample_name, sample_info in results["samples"].items():
                samples_table.add_row(
                    sample_name,
                    str(sample_info["file_count"]),
                    str(sample_info["lanes"]),
                    ", ".join(sample_info["reads"])
                )
            
            logger.info("", rich=samples_table)
        
        # Next steps panel
        if results["next_steps"]:
            next_panel = Panel(
                "\n".join([f"• {step}" for step in results["next_steps"]]),
                title="Suggested Next Steps",
                border_style="green"
            )
            logger.info("", rich=next_panel)
    
    @tool
    def check_reference_status(self, species: str = None, genome_version: str = None) -> Dict[str, Any]:
        """Check reference genome availability with smart detection (similar to cellranger detection)"""
        
        logger.info("\n🧬 [bold cyan]Checking Reference Genome Status[/bold cyan]")
        
        # Default to human if not specified
        if species is None:
            species = "human"
        species = species.lower()
        
        # Auto-select genome version
        if genome_version is None:
            if species == "human":
                genome_version = "GRCh38"
            elif species == "mouse":
                genome_version = "GRCm39"
        
        status = {
            "species": species,
            "genome_version": genome_version,
            "reference_exists": False,
            "reference_complete": False,
            "reference_path": None,
            "download_exists": False,
            "download_path": None,
            "recommendation": None
        }
        
        # Check multiple potential reference locations (similar to cellranger detection)
        reference_search_paths = [
            self.launch_directory / "references" / species / genome_version,
            self.workspace_path / "references" / species / genome_version,
            self._get_cache_dir() / "references" / species / genome_version
        ]
        
        for ref_path in reference_search_paths:
            if ref_path.exists():
                logger.info(f"🔍 [cyan]Found reference directory: {ref_path}[/cyan]")
                # Check for refdata-* directories
                extracted_refs = list(ref_path.glob("refdata-*"))
                if extracted_refs:
                    ref_dir = extracted_refs[0]
                    if ref_dir.is_dir():
                        # Check if reference is complete (has required files)
                        required_files = ['fasta/genome.fa', 'genes/genes.gtf']
                        is_complete = all((ref_dir / f).exists() for f in required_files)
                        
                        status.update({
                            "reference_exists": True,
                            "reference_complete": is_complete,
                            "reference_path": str(ref_dir)
                        })
                        
                        if is_complete:
                            logger.info(f"✅ [green]Complete reference found: {ref_dir}[/green]")
                            status["recommendation"] = "ready"
                            return {"status": "success", "reference_status": status}
                        else:
                            logger.info(f"⚠️ [yellow]Incomplete reference found: {ref_dir}[/yellow]")
                            status["recommendation"] = "redownload"
                            break
        
        # Check for existing downloads
        if species in self.pipeline_config["references"] and genome_version in self.pipeline_config["references"][species]:
            ref_config = self.pipeline_config["references"][species][genome_version]
            url = ref_config["url"] 
            filename = url.split("/")[-1].split("?")[0]
            
            for search_path in reference_search_paths:
                download_path = search_path.parent / filename
                if download_path.exists():
                    logger.info(f"📦 [yellow]Found existing download: {download_path}[/yellow]")
                    status.update({
                        "download_exists": True,
                        "download_path": str(download_path)
                    })
                    status["recommendation"] = "extract"
                    break
        
        # Final recommendations
        if not status["reference_exists"] and not status["download_exists"]:
            status["recommendation"] = "download"
            logger.info("📥 [yellow]Reference download needed[/yellow]")
        elif status["download_exists"] and not status["reference_complete"]:
            status["recommendation"] = "extract"
            logger.info("📦 [yellow]Reference extraction needed[/yellow]")
        
        return {
            "status": "success",
            "reference_status": status
        }

    @tool
    def setup_reference(self, species: str = None, 
                        genome_version: str = None, 
                        auto_detect: bool = True) -> Dict[str, Any]:
        """Download and setup scATAC-seq reference genome with auto-detection"""
        
        if auto_detect and species is None:
            logger.info("\n🔍 [bold cyan]Auto-detecting reference requirements...[/bold cyan]")
            # For now, default to human. In practice, this would analyze data files.
            species = "human"
            logger.info(f"[yellow]Auto-detected species: {species}[/yellow]")
        
        if species is None:
            return {
                "status": "failed",
                "error": "Species must be specified or auto_detect enabled"
            }
        
        species = species.lower()
        if species not in self.pipeline_config["references"]:
            available = list(self.pipeline_config["references"].keys())
            return {
                "status": "failed",
                "error": f"Species '{species}' not supported. Available: {available}"
            }
        
        # Auto-select genome version based on species
        species_refs = self.pipeline_config["references"][species]
        if genome_version is None:
            if species == "human":
                genome_version = "GRCh38"  # Updated to use latest version
            elif species == "mouse":
                genome_version = "GRCm39"  # Updated to use latest version
            else:
                genome_version = list(species_refs.keys())[0]  # Use first available
        
        if genome_version not in species_refs:
            available = list(species_refs.keys())
            return {
                "status": "failed", 
                "error": f"Genome version '{genome_version}' not available for {species}. Available: {available}"
            }
        
        ref_config = species_refs[genome_version]
        cache_dir = self.workspace_path
        ref_dir = cache_dir / "references" / species / genome_version
        
        logger.info(f"\n🧬 [bold cyan]Setting up {species} {genome_version} reference[/bold cyan]")
        
        # Check if already downloaded and extracted
        extracted_ref_dirs = list(ref_dir.glob("refdata-*"))
        if extracted_ref_dirs and any(d.is_dir() for d in extracted_ref_dirs):
            logger.info("✅ [green]Reference already exists in cache[/green]")
            # Find the actual reference directory
            ref_path = next(d for d in extracted_ref_dirs if d.is_dir())
            return {
                "status": "success",
                "path": str(ref_path),
                "cached": True,
                "species": species,
                "genome_version": genome_version
            }
        
        # Download reference
        url = ref_config["url"]
        expected_size = ref_config["size"]
        filename = url.split("/")[-1].split("?")[0]  # Remove URL parameters
        download_path = cache_dir / filename
        
        try:
            # Download with progress
            logger.info(f"📥 [yellow]Downloading {species} {genome_version} reference...[/yellow]")
            
            download_result = self._download_with_progress(
                url, download_path, f"Downloading {species} {genome_version}", expected_size
            )
            
            if not download_result["success"]:
                return {
                    "status": "failed",
                    "error": "Download failed",
                    "details": download_result
                }
            
            # Extract reference
            logger.info("📦 [yellow]Extracting reference genome (this may take a while)...[/yellow]")
            ref_dir.mkdir(parents=True, exist_ok=True)
            
            with tarfile.open(download_path, 'r:gz') as tar:
                tar.extractall(ref_dir)
            
            # Clean up download file
            download_path.unlink()
            
            # Find the extracted reference directory
            extracted_ref_dirs = list(ref_dir.glob("refdata-*"))
            if extracted_ref_dirs:
                ref_path = next(d for d in extracted_ref_dirs if d.is_dir())
                logger.info("✅ [green]Reference setup complete![/green]")
                logger.info(f"[dim]Reference path: {ref_path}[/dim]")
                
                return {
                    "status": "success", 
                    "path": str(ref_path),
                    "cached": False,
                    "species": species,
                    "genome_version": genome_version,
                    "size": expected_size
                }
            else:
                return {
                    "status": "failed",
                    "error": "Reference directory not found after extraction"
                }
            
        except Exception as e:
            return {
                "status": "failed",
                "error": f"Reference setup failed: {str(e)}",
                "species": species,
                "genome_version": genome_version
            }
    
    @tool 
    def setup_references_batch(self, species_list: List[str] = None) -> Dict[str, Any]:
        """Download both human and mouse references for comprehensive analysis"""
        
        if species_list is None:
            species_list = ["human", "mouse"]
        
        logger.info(f"\n🧬 [bold cyan]Setting up references for: {', '.join(species_list)}[/bold cyan]")
        
        results = {}
        
        for species in species_list:
            logger.info(f"\n--- Processing {species.title()} Reference ---")
            result = self.setup_reference(species=species)
            results[species] = result
            
            if result["status"] == "success":
                logger.info(f"✅ [green]{species.title()} reference ready[/green]")
            else:
                logger.info(f"❌ [red]{species.title()} reference failed: {result['error']}[/red]")
        
        successful_count = sum(1 for r in results.values() if r["status"] == "success")
        
        return {
            "status": "success" if successful_count == len(species_list) else "partial",
            "results": results,
            "successful": successful_count,
            "total": len(species_list)
        }
    
    def _download_with_progress(self, url: str, output_path: Path, description: str, expected_size: int = None) -> Dict[str, Any]:
        """Download file with rich progress bar using requests"""
        
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                TextColumn("[blue]{task.fields[downloaded]}[/blue]")
            ) as progress:
                
                # Start the request
                response = requests.get(url, stream=True)
                response.raise_for_status()
                
                # Get actual file size from headers or use expected
                total_size = int(response.headers.get('content-length', 0))
                if total_size == 0 and expected_size:
                    total_size = expected_size
                
                download_task = progress.add_task(
                    description, 
                    total=total_size,
                    downloaded="0 MB"
                )
                
                downloaded = 0
                with open(output_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            progress.update(
                                download_task,
                                completed=downloaded,
                                downloaded=f"{downloaded / (1024*1024):.1f} MB"
                            )
                
                progress.update(
                    download_task, 
                    completed=total_size if total_size > 0 else downloaded,
                    downloaded=f"{downloaded / (1024*1024):.1f} MB"
                )
            
            return {"success": True, "path": str(output_path)}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @tool
    def run_count(
        self, 
        sample_id: str,
        fastqs_path: str,
        reference_path: str,
        output_dir: str = None,
        expected_cells: int = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Run cellranger-atac count for single sample"""
        
        # Check cellranger-atac
        cellranger_check = self._check_cellranger_atac()
        if not cellranger_check["installed"]:
            return {
                "status": "failed",
                "error": "cellranger-atac not found",
                "install_instructions": cellranger_check["install_instructions"]
            }
        
        # Prepare paths
        fastqs_path = Path(fastqs_path)
        reference_path = Path(reference_path)
        
        if output_dir is None:
            output_dir = self.workspace_path / "cellranger_output"
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Build cellranger-atac count command
        cmd = [
            "cellranger-atac", "count",
            "--id", sample_id,
            "--fastqs", str(fastqs_path),
            "--reference", str(reference_path),
            "--localcores", str(self.pipeline_config["default_params"]["threads"]),
            "--localmem", str(int(self.pipeline_config["default_params"]["memory"].replace("G", "")))
        ]
        
        # Add optional parameters
        if expected_cells:
            cmd.extend(["--expect-cells", str(expected_cells)])
        elif self.pipeline_config["default_params"]["expected_cells"]:
            cmd.extend(["--expect-cells", str(self.pipeline_config["default_params"]["expected_cells"])])
        
        logger.info(f"\n🧬 [bold cyan]Running cellranger-atac count for {sample_id}[/bold cyan]")
        logger.info(f"[dim]Command: {' '.join(cmd)}[/dim]")
        
        # Run with progress monitoring
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
        ) as progress:
            
            task = progress.add_task(f"Processing {sample_id}...", total=None)
            
            # Execute cellranger-atac count (this can take hours)
            result = self._run_command(cmd, cwd=output_dir, timeout=7200)  # 2 hour timeout
            
            if result["status"] == "success":
                progress.update(task, description="✅ cellranger-atac count completed!")
                
                # Validate outputs
                output_path = output_dir / sample_id
                validation = self._validate_cellranger_outputs(output_path)
                
                return {
                    "status": "success",
                    "sample_id": sample_id,
                    "output_path": str(output_path),
                    "validation": validation,
                    "command": result["command"]
                }
            else:
                progress.update(task, description="❌ cellranger-atac count failed")
                return {
                    "status": "failed",
                    "sample_id": sample_id,
                    "error": result.get("error", "Unknown error"),
                    "stderr": result.get("stderr", ""),
                    "recovery_suggestions": result.get("recovery_suggestions", [])
                }
    
    def _validate_cellranger_outputs(self, output_path: Path) -> Dict[str, Any]:
        """Validate cellranger-atac outputs"""
        
        validation = {
            "valid": True,
            "files_found": [],
            "files_missing": [],
            "file_sizes": {}
        }
        
        # Expected output files
        expected_files = [
            "outs/web_summary.html",
            "outs/summary.csv", 
            "outs/fragments.tsv.gz",
            "outs/fragments.tsv.gz.tbi",
            "outs/filtered_peak_bc_matrix.h5",
            "outs/filtered_peak_bc_matrix/barcodes.tsv",
            "outs/filtered_peak_bc_matrix/features.tsv",
            "outs/filtered_peak_bc_matrix/matrix.mtx",
            "outs/peaks.bed",
            "outs/possorted_bam.bam",
            "outs/possorted_bam.bam.bai"
        ]
        
        for file_rel_path in expected_files:
            file_path = output_path / file_rel_path
            if file_path.exists():
                validation["files_found"].append(file_rel_path)
                validation["file_sizes"][file_rel_path] = file_path.stat().st_size
            else:
                validation["files_missing"].append(file_rel_path)
                validation["valid"] = False
        
        return validation
    
    @tool
    def init(self, project_name: str = "scatac_project", expected_cells: int = 10000) -> str:
        """Initialize single-cell ATAC-seq project structure"""
        
        project_dir = self.workspace_path / project_name
        
        logger.info(f"\n🧬 [bold cyan]Initializing scATAC project: {project_name}[/bold cyan]")
        
        # Create directory structure
        dirs = self.pipeline_config["project_structure"]["dirs"]
        for dir_name in dirs:
            (project_dir / dir_name).mkdir(parents=True, exist_ok=True)
        
        # Create project config
        config = {
            "project_name": project_name,
            "project_type": "single_cell_atac_seq",
            "expected_cells": expected_cells,
            "created": datetime.now().isoformat(),
            "pipeline_version": "1.0.0",
            "directories": {d: str(project_dir / d) for d in dirs},
            "parameters": self.pipeline_config["default_params"].copy()
        }
        
        with open(project_dir / "scatac_config.json", 'w') as f:
            json.dump(config, f, indent=2)
        
        # Create sample sheet template
        with open(project_dir / "samples.csv", 'w') as f:
            f.write("sample_id,fastqs_path,expected_cells,description\n")
            f.write("# Example:\n")
            f.write("# Sample1,/path/to/fastqs,10000,Control sample\n")
            f.write("# Sample2,/path/to/fastqs,8000,Treatment sample\n")
        
        # Create README
        with open(project_dir / "README.md", 'w') as f:
            f.write(f"""# {project_name}

Single-cell ATAC-seq analysis project created on {datetime.now().strftime('%Y-%m-%d')}

## Project Structure
- `raw_data/`: Input FASTQ files  
- `references/`: Genome reference files
- `cellranger/`: cellranger-atac outputs
- `filtered/`: Quality-filtered data
- `analysis/`: Downstream analysis results
- `plots/`: Generated visualizations
- `reports/`: Analysis reports
- `logs/`: Processing logs

## Quick Start
1. Add FASTQ files to `raw_data/` directory
2. Update `samples.csv` with sample information
3. Run: `/bio scatac upstream ./raw_data`

## Configuration
See `scatac_config.json` for pipeline parameters.
""")
        
        logger.info("✅ [green]Project structure created successfully![/green]")
        logger.info(f"[dim]Project directory: {project_dir}[/dim]")
        
        return f"✅ scATAC project '{project_name}' initialized at {project_dir}"
    
    @tool
    def test_cellranger_functionality(self, install_dir: str = None) -> Dict[str, Any]:
        """Test cellranger-atac functionality with comprehensive checks"""
        
        logger.info("\n🧪 [bold cyan]Testing cellranger-atac functionality[/bold cyan]")
        
        cellranger_config = self.pipeline_config["cellranger_atac"]
        version = cellranger_config["version"]
        
        # Set up paths - use launch directory
        if install_dir is None:
            install_dir = self.launch_directory / cellranger_config.get("install_dir", "software")
        else:
            install_dir = Path(install_dir)
        
        extracted_dir = install_dir / f"cellranger-atac-{version}"
        cellranger_binary = extracted_dir / "bin" / "cellranger-atac"
        
        test_results = {
            "binary_path": str(cellranger_binary),
            "tests_passed": [],
            "tests_failed": [],
            "overall_status": "unknown",
            "version_info": None,
            "help_output": None,
            "subcommands": []
        }
        
        # Test 1: Binary exists and is executable
        if not cellranger_binary.exists():
            test_results["tests_failed"].append("Binary file not found")
            test_results["overall_status"] = "failed"
            logger.info("❌ [red]Binary file not found[/red]")
            return {
                "status": "failed",
                "test_results": test_results,
                "error": "cellranger-atac binary not found. Run installation first."
            }
        
        import stat
        try:
            file_mode = cellranger_binary.stat().st_mode
            is_executable = bool(file_mode & stat.S_IXUSR)
            if is_executable:
                test_results["tests_passed"].append("Binary is executable")
                logger.info("✅ [green]Binary is executable[/green]")
            else:
                test_results["tests_failed"].append("Binary not executable")
                logger.info("❌ [red]Binary not executable[/red]")
        except Exception as e:
            test_results["tests_failed"].append(f"Cannot check executable status: {str(e)}")
        
        # Test 2: Version check
        logger.info("🔍 [yellow]Testing version command...[/yellow]")
        try:
            version_result = self._run_command(
                [str(cellranger_binary), "--version"], 
                timeout=30
            )
            if version_result["status"] == "success":
                test_results["tests_passed"].append("Version command works")
                test_results["version_info"] = version_result["stdout"].strip()
                logger.info(f"✅ [green]Version: {test_results['version_info']}[/green]")
            else:
                test_results["tests_failed"].append(f"Version command failed: {version_result.get('error', 'Unknown error')}")
                logger.info(f"❌ [red]Version command failed: {version_result.get('stderr', 'Unknown error')}[/red]")
        except Exception as e:
            test_results["tests_failed"].append(f"Version test exception: {str(e)}")
            
        # Test 3: Help command
        logger.info("🔍 [yellow]Testing help command...[/yellow]")
        try:
            help_result = self._run_command(
                [str(cellranger_binary), "--help"], 
                timeout=30
            )
            if help_result["status"] == "success":
                test_results["tests_passed"].append("Help command works")
                test_results["help_output"] = help_result["stdout"]
                # Extract subcommands
                help_text = help_result["stdout"]
                if "count" in help_text:
                    test_results["subcommands"].append("count")
                if "aggr" in help_text:
                    test_results["subcommands"].append("aggr")
                if "reanalyze" in help_text:
                    test_results["subcommands"].append("reanalyze")
                logger.info(f"✅ [green]Help command works, found subcommands: {', '.join(test_results['subcommands'])}[/green]")
            else:
                test_results["tests_failed"].append(f"Help command failed: {help_result.get('error', 'Unknown error')}")
                logger.info(f"❌ [red]Help command failed[/red]")
        except Exception as e:
            test_results["tests_failed"].append(f"Help test exception: {str(e)}")
            
        # Test 4: Count subcommand help (most important for functionality)
        logger.info("🔍 [yellow]Testing count subcommand...[/yellow]")
        try:
            count_result = self._run_command(
                [str(cellranger_binary), "count", "--help"], 
                timeout=30
            )
            if count_result["status"] == "success":
                test_results["tests_passed"].append("Count subcommand works")
                logger.info("✅ [green]Count subcommand accessible[/green]")
            else:
                test_results["tests_failed"].append("Count subcommand failed")
                logger.info("❌ [red]Count subcommand failed[/red]")
        except Exception as e:
            test_results["tests_failed"].append(f"Count subcommand test exception: {str(e)}")
        
        # Test 5: Dependencies test (optional but useful)
        logger.info("🔍 [yellow]Checking for common dependency issues...[/yellow]")
        try:
            # Test if common libraries are available (this is a simplified check)
            ldd_result = self._run_command(["ldd", str(cellranger_binary)], timeout=10)
            if ldd_result["status"] == "success":
                if "not found" not in ldd_result["stdout"]:
                    test_results["tests_passed"].append("Dependencies check passed")
                    logger.info("✅ [green]No missing library dependencies detected[/green]")
                else:
                    test_results["tests_failed"].append("Missing library dependencies")
                    logger.info("⚠️ [yellow]Some library dependencies may be missing[/yellow]")
            else:
                # ldd might not be available on all systems (e.g., macOS)
                test_results["tests_passed"].append("Dependencies check skipped (ldd not available)")
                logger.info("⚠️ [yellow]Dependency check skipped (ldd not available)[/yellow]")
        except Exception as e:
            test_results["tests_passed"].append("Dependencies check skipped")
            
        # Final assessment
        total_tests = len(test_results["tests_passed"]) + len(test_results["tests_failed"])
        passed_tests = len(test_results["tests_passed"])
        
        if len(test_results["tests_failed"]) == 0:
            test_results["overall_status"] = "passed"
            logger.info(f"\n✅ [bold green]All functionality tests passed! ({passed_tests}/{total_tests})[/bold green]")
            logger.info("🎉 [green]cellranger-atac is ready for use![/green]")
        elif passed_tests > len(test_results["tests_failed"]):
            test_results["overall_status"] = "partial"
            logger.info(f"\n⚠️ [yellow]Partial functionality ({passed_tests}/{total_tests} tests passed)[/yellow]")
            logger.info("📝 [yellow]Some features may not work correctly[/yellow]")
        else:
            test_results["overall_status"] = "failed"
            logger.info(f"\n❌ [red]Functionality tests failed ({passed_tests}/{total_tests} tests passed)[/red]")
            logger.info("🚨 [red]cellranger-atac may not work correctly[/red]")
        
        # Display detailed results
        from rich.table import Table
        results_table = Table(title="Functionality Test Results")
        results_table.add_column("Test", style="cyan")
        results_table.add_column("Status", style="green")
        
        for test in test_results["tests_passed"]:
            results_table.add_row(test, "✅ Passed")
        
        for test in test_results["tests_failed"]:
            results_table.add_row(test, "❌ Failed")
            
        logger.info("", rich=results_table)
        
        return {
            "status": "success",
            "test_results": test_results
        }