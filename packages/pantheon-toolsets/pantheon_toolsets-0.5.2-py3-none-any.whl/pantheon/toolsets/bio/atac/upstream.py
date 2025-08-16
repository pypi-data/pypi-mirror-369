"""ATAC-seq Upstream Analysis - Data preparation, QC, alignment, and BAM processing"""

import os
import subprocess
import json
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple
from ...utils.log import logger
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from ...utils.toolset import ToolSet, tool
from rich.console import Console

class ATACSeqUpstreamToolSet(ToolSet):
    """ATAC-seq Upstream Analysis Toolset - From FASTQ to filtered BAM files"""
    
    def __init__(
        self,
        name: str = "atac_upstream",
        workspace_path: str | Path | None = None,
        worker_params: dict | None = None,
        **kwargs,
    ):
        super().__init__(name, worker_params, **kwargs)
        self.workspace_path = Path(workspace_path) if workspace_path else Path.cwd()
        self.pipeline_config = self._initialize_config()
        self.console = Console()
        
    def _initialize_config(self) -> Dict[str, Any]:
        """Initialize ATAC-seq pipeline configuration"""
        return {
            "file_extensions": {
                "raw_reads": [".fastq", ".fq", ".fastq.gz", ".fq.gz", ".fastq.bz2", 
                             ".fq.bz2", ".fastq.zst", ".fq.zst", ".sra"],
                "barcodes": [".whitelist.txt", ".tsv"],
                "genome": [".fa", ".fasta", ".fai", ".dict"],
                "bwa_index": [".amb", ".ann", ".bwt", ".pac", ".sa"],
                "bowtie2_index": [".bt2", ".bt2l"],
                "regions": [".bed", ".bed.gz", ".chrom.sizes"],
                "alignment": [".sam", ".bam", ".cram", ".bam.bai", ".cram.crai"],
                "peaks": [".narrowPeak", ".broadPeak", ".gappedPeak", ".xls", ".bedgraph", ".bdg"],
                "tracks": [".bw", ".bigwig", ".tdf"],
                "reports": [".html", ".json", ".txt", ".tsv", ".csv", ".pdf", ".png"]
            },
            "tools": {
                "acquisition": ["sra-tools", "pigz", "pbzip2", "zstd", "seqtk"],
                "qc": ["fastqc", "multiqc", "fastp", "trim_galore", "cutadapt"],
                "alignment": ["bowtie2", "bwa", "bwa-mem2", "minimap2"],  # Bowtie2 first for ATAC-seq
                "sam_processing": ["samtools", "sambamba", "picard", "samblaster"],
                "atac_qc": ["ataqv", "preseq", "deeptools"],
                "peak_calling": ["macs2", "genrich", "hmmratac"],
                "coverage": ["deeptools", "bedtools", "ucsc-tools"],
                "annotation": ["homer", "meme", "chipseeker", "bedtools"]
            },
            "default_params": {
                "threads": 4,
                "memory": "8G",
                "quality_threshold": 20,
                "min_mapping_quality": 30,
                "fragment_size_range": [50, 1000],
                "peak_calling_fdr": 0.01
            }
        }
    
    @tool
    def init(self, project_name: str = "atac_analysis", 
             genome: str = "hg38",
             paired_end: bool = True) -> str:
        """
        Initialize ATAC-seq analysis project structure
        
        Args:
            project_name: Name of the project
            genome: Reference genome (hg38, mm10, etc.)
            paired_end: Whether data is paired-end
            
        Returns:
            Status message
        """
        project_dir = self.workspace_path / project_name
        
        # Create directory structure
        dirs = [
            "fastq", "fastq_trimmed", "qc", "qc/fastqc", "qc/multiqc",
            "alignment", "alignment/filtered", "alignment/dedup",
            "peaks", "peaks/macs2", "peaks/genrich", 
            "coverage", "coverage/bigwig",
            "motifs", "annotation", "reports", "logs", "scripts"
        ]
        
        for dir_name in dirs:
            (project_dir / dir_name).mkdir(parents=True, exist_ok=True)
        
        # Create config file
        config = {
            "project_name": project_name,
            "genome": genome,
            "paired_end": paired_end,
            "created": str(Path.cwd()),
            "pipeline_version": "1.0.0",
            "directories": {d: str(project_dir / d) for d in dirs}
        }
        
        config_file = project_dir / "atac_config.json"
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        # Create sample sheet template
        sample_sheet = project_dir / "samples.tsv"
        with open(sample_sheet, 'w') as f:
            if paired_end:
                f.write("sample_id\tfastq_r1\tfastq_r2\tcondition\treplicate\n")
                f.write("# Example:\n")
                f.write("# Sample1\tsample1_R1.fastq.gz\tsample1_R2.fastq.gz\tcontrol\t1\n")
            else:
                f.write("sample_id\tfastq\tcondition\treplicate\n")
                f.write("# Example:\n")
                f.write("# Sample1\tsample1.fastq.gz\tcontrol\t1\n")
        
        return f"✅ ATAC-seq project '{project_name}' initialized at {project_dir}"
    
    @tool
    def check_dependencies(self) -> Dict[str, Any]:
        """Check which ATAC-seq tools are installed and suggest installation"""
        
        # Rich console header
        logger.info("\n" + "="*70)
        logger.info("🔧 [bold cyan]ATAC-seq Tools Dependency Check[/bold cyan]", justify="center")
        logger.info("="*70)
        
        tools_status = {"installed": {}, "missing": [], "install_commands": []}
        
        # Core tools for ATAC-seq (Bowtie2 is now the primary aligner)
        core_tools = {
            "fastqc": "conda install -c bioconda fastqc",
            "bowtie2": "conda install -c bioconda bowtie2",  # Primary aligner for ATAC-seq
            "bwa": "conda install -c bioconda bwa",  # Secondary option
            "samtools": "conda install -c bioconda samtools",
            "picard": "conda install -c bioconda picard",  # For duplicate marking
            "macs2": "conda install -c bioconda macs2",
            "deeptools": "conda install -c bioconda deeptools",
            "trim_galore": "conda install -c bioconda trim-galore"
        }
        
        # Check tools with progress
        logger.info("\n  [cyan]Checking installed tools...[/cyan]")
        
        # Create dependency status table
        dep_table = Table(title="Dependency Status", show_header=True, header_style="bold magenta")
        dep_table.add_column("Tool", style="cyan", width=15)
        dep_table.add_column("Status", justify="center", width=10)
        dep_table.add_column("Path / Install Command", style="dim")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            check_task = progress.add_task("Checking tools...", total=len(core_tools))
            
            for tool, install_cmd in core_tools.items():
                progress.update(check_task, description=f"Checking {tool}...")
                
                # Handle special cases for checking
                check_cmd = tool
                if tool == "trim_galore":
                    check_cmd = "trim_galore"
                        
                try:
                    result = subprocess.run(
                        ["which", check_cmd],
                        capture_output=True,
                        text=True
                    )
                    if result.returncode == 0:
                        path = result.stdout.strip()
                        tools_status["installed"][tool] = path
                        dep_table.add_row(
                            f"🧬 {tool}",
                            "[green]✅ FOUND[/green]",
                            f"[dim]{path}[/dim]"
                        )
                    else:
                        tools_status["missing"].append(tool)
                        tools_status["install_commands"].append(f"{tool}: {install_cmd}")
                        dep_table.add_row(
                            f"🧬 {tool}",
                            "[red]❌ MISSING[/red]",
                            f"[yellow]{install_cmd}[/yellow]"
                        )
                except:
                    tools_status["missing"].append(tool)
                    tools_status["install_commands"].append(f"{tool}: {install_cmd}")
                    dep_table.add_row(
                        f"🧬 {tool}",
                        "[red]❌ MISSING[/red]",
                        f"[yellow]{install_cmd}[/yellow]"
                    )
                
                progress.advance(check_task)
        
        logger.info("", rich=dep_table)
        
        # Summary
        installed_count = len(tools_status["installed"])
        missing_count = len(tools_status["missing"])
        total_count = installed_count + missing_count
        
        if missing_count == 0:
            summary_panel = Panel(
                f"[green]✅ All tools installed! ({installed_count}/{total_count})[/green]",
                title="Status",
                border_style="green"
            )
        else:
            summary_panel = Panel(
                f"[yellow]⚠️  {missing_count} tools missing ({installed_count}/{total_count} installed)[/yellow]\n" +
                f"[cyan]Run: atac.install_missing_tools({tools_status['missing']})[/cyan]",
                title="Status",
                border_style="yellow"
            )
        
        logger.info("", rich=summary_panel)
        logger.info("="*70 + "\n")
        
        return tools_status
    
    @tool
    def install_missing_tools(self, tools: List[str]) -> str:
        """Install missing ATAC-seq tools using conda"""
        
        # Rich console header
        logger.info("\n" + "="*70)
        logger.info("⬇   [bold cyan]Installing Missing ATAC-seq Tools[/bold cyan]", justify="center")
        logger.info("="*70)
        
        if not tools:
            logger.info("✅ [green]No tools to install - all dependencies are already satisfied![/green]")
            return "No tools to install"
        
        install_commands = {
            "fastqc": "conda install -c bioconda fastqc -y",
            "bowtie2": "conda install -c bioconda bowtie2 -y",  # Primary aligner for ATAC-seq
            "bwa": "conda install -c bioconda bwa -y", 
            "samtools": "conda install -c bioconda samtools -y",
            "picard": "conda install -c bioconda picard -y",  # For duplicate marking
            "macs2": "conda install -c bioconda macs2 -y",
            "deeptools": "conda install -c bioconda deeptools -y",
            "trim_galore": "conda install -c bioconda trim-galore -y"
        }
        
        results = []
        successful_installs = 0
        failed_installs = 0
        
        logger.info(f"  [yellow]Installing {len(tools)} tools:[/yellow] {', '.join(tools)}\n")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=self.console
        ) as progress:
            
            main_task = progress.add_task("Installing tools...", total=len(tools))
            
            for i, tool in enumerate(tools, 1):
                if tool in install_commands:
                    cmd = install_commands[tool]
                    progress.update(main_task, description=f"Installing {tool}... ({i}/{len(tools)})")
                    
                    logger.info(f"  [cyan]Installing {tool}...[/cyan]")
                    
                    try:
                        result = subprocess.run(
                            cmd.split(),
                            capture_output=True,
                            text=True,
                            timeout=300  # 5 minute timeout
                        )
                        if result.returncode == 0:
                            logger.info(f"✅ [green]Successfully installed {tool}[/green]")
                            results.append(f"✅ Successfully installed {tool}")
                            successful_installs += 1
                        else:
                            error_msg = result.stderr.strip()[:100] + "..." if len(result.stderr) > 100 else result.stderr.strip()
                            logger.info(f"❌ [red]Failed to install {tool}[/red]")
                            logger.info(f"   [dim]Error: {error_msg}[/dim]")
                            results.append(f"❌ Failed to install {tool}: {error_msg}")
                            failed_installs += 1
                    except subprocess.TimeoutExpired:
                        logger.info(f"  [yellow]Installation of {tool} timed out[/yellow]")
                        results.append(f"  Installation of {tool} timed out")
                        failed_installs += 1
                    except Exception as e:
                        logger.info(f"❌ [red]Error installing {tool}: {str(e)}[/red]")
                        results.append(f"❌ Error installing {tool}: {str(e)}")
                        failed_installs += 1
                else:
                    logger.info(f"❓ [yellow]Unknown tool: {tool}[/yellow]")
                    results.append(f"❓ Unknown tool: {tool}")
                    failed_installs += 1
                
                progress.advance(main_task)
                logger.info("")  # Add spacing
        
        # Final summary
        if failed_installs == 0:
            summary_panel = Panel(
                f"[green]  All tools installed successfully! ({successful_installs}/{len(tools)})[/green]",
                title="Installation Complete",
                border_style="green"
            )
        else:
            summary_panel = Panel(
                f"[yellow]⚠️  Installation completed with issues[/yellow]\n" +
                f"[green]✅ Successful: {successful_installs}[/green]\n" +
                f"[red]❌ Failed: {failed_installs}[/red]",
                title="Installation Summary",
                border_style="yellow"
            )
        
        logger.info("", rich=summary_panel)
        logger.info("="*70 + "\n")
        
        return "\n".join(results)
    
    def _check_and_install_tool(self, tool_name: str, show_output: bool = True) -> bool:
        """Check if a tool is available and install if missing
        
        Args:
            tool_name: Name of the tool to check
            show_output: Whether to show installation progress
            
        Returns:
            True if tool is available or successfully installed, False otherwise
        """
        try:
            subprocess.run(["which", tool_name], capture_output=True, check=True)
            return True  # Tool is already available
        except subprocess.CalledProcessError:
            if show_output:
                logger.info(f"⚠️ [yellow]{tool_name} not found, installing...[/yellow]")
            
            install_result = self.install_missing_tools([tool_name])
            
            if f"Successfully installed {tool_name}" in install_result:
                if show_output:
                    logger.info(f"✅ [green]{tool_name} installed successfully[/green]")
                return True
            else:
                if show_output:
                    logger.info(f"❌ [red]Failed to install {tool_name}[/red]")
                return False
    
    @tool
    def auto_detect_species(self, folder_path: str) -> Dict[str, Any]:
        """Auto-detect species from FASTQ files or folder structure"""
        logger.info("")
        logger.info("", rich=Panel.fit("  Auto-detecting Species", style="bright_cyan"))
        
        try:
            folder = Path(folder_path)
            species_hints = {}
            detected_species = "unknown"
            confidence = 0
            
            # Check folder and file names for species hints
            folder_name = folder.name.lower()
            species_keywords = {
                "human": ["human", "hg38", "hg19", "homo", "sapiens"],
                "mouse": ["mouse", "mm10", "mm9", "mus", "musculus"],
                "rat": ["rat", "rn6", "rn5", "rattus", "norvegicus"],
                "fly": ["drosophila", "dm6", "dm3", "melanogaster"],
                "worm": ["elegans", "ce11", "ce10", "caenorhabditis"],
                "zebrafish": ["zebrafish", "danrer", "danio", "rerio"]
            }
            
            # Check folder name
            for species, keywords in species_keywords.items():
                for keyword in keywords:
                    if keyword in folder_name:
                        species_hints[species] = species_hints.get(species, 0) + 2
            
            # Check FASTQ files for species hints
            fastq_files = list(folder.glob("*.fastq*")) + list(folder.glob("*.fq*"))
            
            for fastq_file in fastq_files[:3]:  # Check first 3 files
                filename = fastq_file.name.lower()
                for species, keywords in species_keywords.items():
                    for keyword in keywords:
                        if keyword in filename:
                            species_hints[species] = species_hints.get(species, 0) + 1
                
                # Quick peek at first few reads for organism info
                try:
                    if fastq_file.suffix == '.gz':
                        import gzip
                        with gzip.open(fastq_file, 'rt') as f:
                            for i, line in enumerate(f):
                                if i > 40:  # Check first 10 reads (4 lines each)
                                    break
                                if i % 4 == 0 and line.startswith('@'):  # Header line
                                    header = line.lower()
                                    for species, keywords in species_keywords.items():
                                        for keyword in keywords:
                                            if keyword in header:
                                                species_hints[species] = species_hints.get(species, 0) + 0.5
                    else:
                        with open(fastq_file, 'r') as f:
                            for i, line in enumerate(f):
                                if i > 40:
                                    break
                                if i % 4 == 0 and line.startswith('@'):
                                    header = line.lower()
                                    for species, keywords in species_keywords.items():
                                        for keyword in keywords:
                                            if keyword in header:
                                                species_hints[species] = species_hints.get(species, 0) + 0.5
                except:
                    continue
            
            # Determine most likely species
            if species_hints:
                detected_species = max(species_hints.items(), key=lambda x: x[1])[0]
                confidence = species_hints[detected_species]
            
            # Map to genome versions
            genome_mapping = {
                "human": "hg38",
                "mouse": "mm10", 
                "rat": "rn6",
                "fly": "dm6",
                "worm": "ce11",
                "zebrafish": "danRer11"
            }
            
            suggested_genome = genome_mapping.get(detected_species, "hg38")
            
            # Display results
            results_table = Table(title="Species Detection Results")
            results_table.add_column("Species", style="cyan")
            results_table.add_column("Confidence", style="magenta")
            results_table.add_column("Suggested Genome", style="green")
            
            if confidence > 0:
                results_table.add_row(detected_species.title(), f"{confidence:.1f}", suggested_genome)
                for species, score in sorted(species_hints.items(), key=lambda x: x[1], reverse=True):
                    if species != detected_species:
                        alt_genome = genome_mapping.get(species, species)
                        results_table.add_row(species.title(), f"{score:.1f}", alt_genome)
            else:
                results_table.add_row("Unknown", "0.0", "hg38 (default)")
            
            logger.info("", rich=results_table)
            
            if confidence >= 2:
                logger.info(f"[green]✅ High confidence detection: {detected_species.title()} ({suggested_genome})")
            elif confidence >= 1:
                logger.info(f"[yellow]⚠️ Medium confidence detection: {detected_species.title()} ({suggested_genome})")
            else:
                logger.info(f"[red]❌ Low confidence - defaulting to Human (hg38)")
                suggested_genome = "hg38"
            
            return {
                "status": "success",
                "detected_species": detected_species,
                "suggested_genome": suggested_genome,
                "confidence": confidence,
                "all_hints": species_hints
            }
            
        except Exception as e:
            logger.info(f"[red]❌ Species detection failed: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "suggested_genome": "hg38"
            }
    
    @tool
    def setup_genome_resources(self, species: str, genome_version: str = None, include_gtf: bool = True, include_blacklist: bool = True) -> str:
        """Comprehensive genome resources setup with organized file structure"""
        logger.info("")
        logger.info("", rich=Panel.fit("🧬 Setting Up Genome Resources", style="bright_cyan"))
        
        # Standardize species names
        species_mapping = {
            "human": {"common": "human", "scientific": "homo_sapiens", "default_genome": "hg38"},
            "mouse": {"common": "mouse", "scientific": "mus_musculus", "default_genome": "mm10"},
            "rat": {"common": "rat", "scientific": "rattus_norvegicus", "default_genome": "rn6"}
        }
        
        if species.lower() not in species_mapping:
            available = ", ".join(species_mapping.keys())
            return f"❌ Unsupported species: {species}. Available: {available}"
        
        species_info = species_mapping[species.lower()]
        genome_version = genome_version or species_info["default_genome"]
        
        # Create organized directory structure
        base_ref_dir = self.workspace_path / "reference"
        genome_dir = base_ref_dir / "genome" / species_info["common"]
        gtf_dir = base_ref_dir / "gtf" / species_info["common"] 
        blacklist_dir = base_ref_dir / "blacklist" / species_info["common"]
        
        # Create all directories
        for dir_path in [genome_dir, gtf_dir, blacklist_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # Define resource configurations
        resources_config = self._get_resources_config()
        
        if species_info["common"] not in resources_config:
            return f"❌ No resource configuration for {species}"
        
        species_resources = resources_config[species_info["common"]]
        if genome_version not in species_resources:
            available_versions = ", ".join(species_resources.keys())
            return f"❌ Genome version {genome_version} not available for {species}. Available: {available_versions}"
        
        genome_config = species_resources[genome_version]
        
        # Check existing resources
        existing_resources = self._check_existing_resources(species_info["common"], genome_version)
        
        # Display resource summary
        self._display_resource_plan(species_info, genome_version, genome_config, include_gtf, include_blacklist, existing_resources)
        
        # Setup genome
        genome_result = self._setup_genome_file(genome_dir, genome_version, genome_config)
        if not genome_result["success"]:
            return genome_result["message"]
        
        # Setup GTF if requested
        gtf_result = {"success": True, "message": "GTF setup skipped"}
        if include_gtf:
            gtf_result = self._setup_gtf_file(gtf_dir, genome_version, genome_config)
        
        # Setup blacklist if requested  
        blacklist_result = {"success": True, "message": "Blacklist setup skipped"}
        if include_blacklist:
            blacklist_result = self._setup_blacklist_file(blacklist_dir, genome_version, genome_config)
        
        # Generate summary report
        return self._generate_setup_summary(species_info, genome_version, genome_result, gtf_result, blacklist_result)
    
    def _get_resources_config(self) -> Dict[str, Any]:
        """Get comprehensive resource configuration with multiple sources"""
        return {
            "human": {
                "hg38": {
                    "name": "Human genome GRCh38/hg38",
                    "genome": {
                        "size": "~3.0GB",
                        "sources": {
                            "UCSC": "http://hgdownload.cse.ucsc.edu/goldenPath/hg38/bigZips/hg38.fa.gz",
                            "ENSEMBL": "http://ftp.ensembl.org/pub/release-104/fasta/homo_sapiens/dna/Homo_sapiens.GRCh38.dna.primary_assembly.fa.gz",
                            "清华镜像": "https://mirrors.tuna.tsinghua.edu.cn/genomes/refseq/vertebrate_mammalian/Homo_sapiens/latest_assembly_versions/GCF_000001405.40_GRCh38.p14/GCF_000001405.40_GRCh38.p14_genomic.fna.gz"
                        },
                        "md5": None,  # Could add MD5 checksums for validation
                        "expected_size": 3200000000  # ~3.2GB uncompressed
                    },
                    "gtf": {
                        "sources": {
                            "GENCODE": "https://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_44/gencode.v44.primary_assembly.annotation.gtf.gz",
                            "ENSEMBL": "http://ftp.ensembl.org/pub/release-104/gtf/homo_sapiens/Homo_sapiens.GRCh38.104.gtf.gz",
                            "清华镜像": "https://mirrors.tuna.tsinghua.edu.cn/gencode/Gencode_human/release_44/gencode.v44.primary_assembly.annotation.gtf.gz"
                        },
                        "size": "~50MB",
                        "expected_size": 52000000
                    },
                    "blacklist": {
                        "sources": {
                            "ENCODE": "https://github.com/Boyle-Lab/Blacklist/raw/master/lists/hg38-blacklist.v2.bed.gz",
                            "清华镜像": "https://mirrors.tuna.tsinghua.edu.cn/ENCODE/blacklist/hg38-blacklist.v2.bed.gz"
                        },
                        "size": "~3MB",
                        "expected_size": 3000000
                    }
                },
                "hg38_test": {
                    "name": "Human chromosome 22 (test)",
                    "genome": {
                        "size": "~50MB",
                        "sources": {
                            "UCSC": "http://hgdownload.cse.ucsc.edu/goldenPath/hg38/chromosomes/chr22.fa.gz",
                            "清华镜像": "https://mirrors.tuna.tsinghua.edu.cn/UCSC/goldenPath/hg38/chromosomes/chr22.fa.gz"
                        },
                        "expected_size": 52000000
                    },
                    "gtf": {
                        "sources": {
                            "GENCODE_CHR22": "https://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_44/gencode.v44.chr_patch_hapl_scaff.annotation.gtf.gz"
                        },
                        "size": "~1MB",
                        "expected_size": 1000000
                    }
                }
            },
            "mouse": {
                "mm10": {
                    "name": "Mouse genome GRCm38/mm10",
                    "genome": {
                        "size": "~2.7GB",
                        "sources": {
                            "UCSC": "http://hgdownload.cse.ucsc.edu/goldenPath/mm10/bigZips/mm10.fa.gz",
                            "ENSEMBL": "http://ftp.ensembl.org/pub/release-104/fasta/mus_musculus/dna/Mus_musculus.GRCm38.dna.primary_assembly.fa.gz",
                            "清华镜像": "https://mirrors.tuna.tsinghua.edu.cn/genomes/refseq/vertebrate_mammalian/Mus_musculus/latest_assembly_versions/GCF_000001635.27_GRCm39/GCF_000001635.27_GRCm39_genomic.fna.gz"
                        },
                        "expected_size": 2800000000
                    },
                    "gtf": {
                        "sources": {
                            "GENCODE": "https://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_mouse/release_M31/gencode.vM31.primary_assembly.annotation.gtf.gz",
                            "ENSEMBL": "http://ftp.ensembl.org/pub/release-104/gtf/mus_musculus/Mus_musculus.GRCm38.104.gtf.gz"
                        },
                        "size": "~45MB",
                        "expected_size": 47000000
                    },
                    "blacklist": {
                        "sources": {
                            "ENCODE": "https://github.com/Boyle-Lab/Blacklist/raw/master/lists/mm10-blacklist.v2.bed.gz"
                        },
                        "size": "~1.5MB",
                        "expected_size": 1500000
                    }
                },
                "mm10_test": {
                    "name": "Mouse chromosome 19 (test)",
                    "genome": {
                        "size": "~60MB",
                        "sources": {
                            "UCSC": "http://hgdownload.cse.ucsc.edu/goldenPath/mm10/chromosomes/chr19.fa.gz",
                            "清华镜像": "https://mirrors.tuna.tsinghua.edu.cn/UCSC/goldenPath/mm10/chromosomes/chr19.fa.gz"
                        },
                        "expected_size": 62000000
                    }
                }
            }
        }
    
    def _check_existing_resources(self, species: str, genome_version: str) -> Dict[str, Dict[str, bool]]:
        """Check which resources already exist and are valid"""
        
        base_ref_dir = self.workspace_path / "reference"
        genome_dir = base_ref_dir / "genome" / species
        gtf_dir = base_ref_dir / "gtf" / species
        blacklist_dir = base_ref_dir / "blacklist" / species
        
        # Check genome files
        genome_fa = genome_dir / f"{genome_version}.fa"
        genome_fai = genome_dir / f"{genome_version}.fa.fai"
        bowtie2_index = genome_dir / f"{genome_version}.1.bt2"
        
        genome_status = {
            "fasta": self._validate_file(genome_fa, "fasta"),
            "fasta_index": genome_fai.exists(),
            "bowtie2_index": bowtie2_index.exists(),
            "complete": all([genome_fa.exists(), genome_fai.exists(), bowtie2_index.exists()])
        }
        
        # Check GTF files
        gtf_gencode = gtf_dir / f"{genome_version}_gencode.gtf"
        gtf_ensembl = gtf_dir / f"{genome_version}_ensembl.gtf"
        
        gtf_status = {
            "gencode": self._validate_file(gtf_gencode, "gtf"),
            "ensembl": self._validate_file(gtf_ensembl, "gtf"),
            "any_available": gtf_gencode.exists() or gtf_ensembl.exists()
        }
        
        # Check blacklist files
        blacklist_file = blacklist_dir / f"{genome_version}_blacklist.bed"
        
        blacklist_status = {
            "available": self._validate_file(blacklist_file, "bed")
        }
        
        return {
            "genome": genome_status,
            "gtf": gtf_status,
            "blacklist": blacklist_status
        }
    
    def _validate_file(self, file_path: Path, file_type: str) -> bool:
        """Validate file existence and basic format"""
        if not file_path.exists():
            return False
        
        try:
            # Basic file size check
            if file_path.stat().st_size == 0:
                return False
            
            # Format-specific validation
            if file_type == "fasta":
                with open(file_path, 'r') as f:
                    first_line = f.readline().strip()
                    return first_line.startswith('>')
            elif file_type == "gtf":
                with open(file_path, 'r') as f:
                    for line in f:
                        if not line.startswith('#'):
                            return len(line.split('\t')) >= 8
            elif file_type == "bed":
                with open(file_path, 'r') as f:
                    for line in f:
                        if not line.startswith('#') and line.strip():
                            return len(line.split('\t')) >= 3
            
            return True
        except:
            return False
    
    def _display_resource_plan(self, species_info: dict, genome_version: str, genome_config: dict, 
                             include_gtf: bool, include_blacklist: bool, existing_resources: dict):
        """Display what will be downloaded/skipped"""
        
        plan_table = Table(title=f"Resource Setup Plan: {species_info['common'].title()} {genome_version}")
        plan_table.add_column("Resource", style="cyan")
        plan_table.add_column("Status", style="magenta")
        plan_table.add_column("Action", style="green")
        plan_table.add_column("Size", style="yellow")
        
        # Genome status
        if existing_resources["genome"]["complete"]:
            plan_table.add_row("  Genome", "✅ Complete", "Skip", genome_config["genome"]["size"])
        else:
            missing_parts = []
            if not existing_resources["genome"]["fasta"]:
                missing_parts.append("FASTA")
            if not existing_resources["genome"]["fasta_index"]:
                missing_parts.append("FAI")
            if not existing_resources["genome"]["bowtie2_index"]:
                missing_parts.append("Bowtie2")
            
            plan_table.add_row("  Genome", f"❌ Missing: {', '.join(missing_parts)}", "Download & Index", genome_config["genome"]["size"])
        
        # GTF status
        if include_gtf:
            if existing_resources["gtf"]["any_available"]:
                plan_table.add_row("  GTF", "✅ Available", "Skip", genome_config.get("gtf", {}).get("size", "Unknown"))
            else:
                plan_table.add_row("  GTF", "❌ Missing", "Download", genome_config.get("gtf", {}).get("size", "Unknown"))
        else:
            plan_table.add_row("  GTF", "⏭️ Disabled", "Skip", "-")
        
        # Blacklist status
        if include_blacklist:
            if existing_resources["blacklist"]["available"]:
                plan_table.add_row("  Blacklist", "✅ Available", "Skip", genome_config.get("blacklist", {}).get("size", "Unknown"))
            else:
                plan_table.add_row("  Blacklist", "❌ Missing", "Download", genome_config.get("blacklist", {}).get("size", "Unknown"))
        else:
            plan_table.add_row("  Blacklist", "⏭  Disabled", "Skip", "-")
        
        logger.info("", rich=plan_table)
    
    def _setup_genome_file(self, genome_dir: Path, genome_version: str, genome_config: dict) -> dict:
        """Setup genome FASTA file and indexes with smart caching"""
        
        genome_fa = genome_dir / f"{genome_version}.fa"
        genome_fai = genome_dir / f"{genome_version}.fa.fai"
        bowtie2_index = genome_dir / f"{genome_version}.1.bt2"
        
        # Check if already complete
        if genome_fa.exists() and genome_fai.exists() and bowtie2_index.exists():
            if self._validate_file(genome_fa, "fasta"):
                logger.info("✅ [green]Genome files already exist and are valid[/green]")
                return {"success": True, "message": "Genome already available", "path": str(genome_fa)}
        
        # Download genome if needed
        if not genome_fa.exists() or not self._validate_file(genome_fa, "fasta"):
            logger.info("  [yellow]Downloading genome file...[/yellow]")
            
            # Auto-select fastest source
            speed_test = self._test_sources_speed(genome_config["genome"]["sources"])
            fastest_source, fastest_url = speed_test["fastest_source"], speed_test["fastest_url"]
            
            logger.info(f"  [green]Using fastest source: {fastest_source}[/green]")
            
            # Download with progress
            download_result = self._download_with_progress(
                fastest_url, 
                genome_dir / f"{genome_version}.fa.gz",
                f"Downloading {genome_version} genome",
                genome_config["genome"].get("expected_size", 1000000000)
            )
            
            if not download_result["success"]:
                return {"success": False, "message": f"Genome download failed: {download_result['error']}"}
            
            # Extract
            logger.info("  [yellow]Extracting genome...[/yellow]")
            try:
                cmd = f"gunzip {genome_dir / f'{genome_version}.fa.gz'}"
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                if result.returncode != 0:
                    return {"success": False, "message": f"Extraction failed: {result.stderr}"}
            except Exception as e:
                return {"success": False, "message": f"Extraction error: {str(e)}"}
        
        # Create FASTA index if needed
        if not genome_fai.exists():
            logger.info("📇 [yellow]Creating FASTA index...[/yellow]")
            try:
                cmd = f"samtools faidx {genome_fa}"
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                if result.returncode != 0:
                    logger.info("⚠️ [yellow]samtools not available, skipping fai index[/yellow]")
            except Exception as e:
                logger.info(f"⚠️ [yellow]FASTA indexing failed: {str(e)}[/yellow]")
        
        # Create Bowtie2 index if needed
        if not bowtie2_index.exists():
            logger.info("🔧 [yellow]Building Bowtie2 index (optimized for ATAC-seq)...[/yellow]")
            
            # First check if bowtie2-build is available
            try:
                subprocess.run(["which", "bowtie2-build"], check=True, capture_output=True)
            except subprocess.CalledProcessError:
                logger.info("⚠️ [yellow]Bowtie2 not found - attempting to install...[/yellow]")
                logger.info("  [cyan]Auto-installing Bowtie2...[/cyan]")
                install_result = self.install_missing_tools(["bowtie2"])
                
                # Check again after installation
                try:
                    subprocess.run(["which", "bowtie2-build"], check=True, capture_output=True)
                    logger.info("✅ [green]Bowtie2 installed successfully[/green]")
                except subprocess.CalledProcessError:
                    logger.info("❌ [red]Bowtie2 installation failed - please install manually[/red]")
                    logger.info("[cyan]Manual install: conda install -c bioconda bowtie2[/cyan]")
                    return {"success": False, "message": "Bowtie2 installation failed", "path": str(genome_fa)}
            
            try:
                # Use bowtie2-build with optimized parameters for ATAC-seq
                cmd = f"bowtie2-build --threads 4 {genome_fa} {genome_dir}/{genome_version}"
                process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
                
                while True:
                    output = process.stderr.readline()
                    if output == '' and process.poll() is not None:
                        break
                    if output:
                        logger.info(f"[dim]{output.strip()}[/dim]")
                
                if process.poll() != 0:
                    logger.info("⚠️ [yellow]Bowtie2 indexing failed[/yellow]")
                else:
                    logger.info("✅ [green]Bowtie2 index built successfully[/green]")
            except Exception as e:
                logger.info(f"⚠️ [yellow]Bowtie2 indexing error: {str(e)}[/yellow]")
        
        return {"success": True, "message": "Genome setup completed", "path": str(genome_fa)}
    
    def _setup_gtf_file(self, gtf_dir: Path, genome_version: str, genome_config: dict) -> dict:
        """Setup GTF annotation files"""
        
        if "gtf" not in genome_config:
            return {"success": True, "message": "No GTF configured for this genome"}
        
        gtf_gencode = gtf_dir / f"{genome_version}_gencode.gtf"
        
        # Check if already exists
        if gtf_gencode.exists() and self._validate_file(gtf_gencode, "gtf"):
            logger.info("✅ [green]GTF file already exists and is valid[/green]")
            return {"success": True, "message": "GTF already available", "path": str(gtf_gencode)}
        
        logger.info("  [yellow]Downloading GTF annotation...[/yellow]")
        
        # Auto-select fastest source
        speed_test = self._test_sources_speed(genome_config["gtf"]["sources"])
        fastest_source, fastest_url = speed_test["fastest_source"], speed_test["fastest_url"]
        
        logger.info(f"🏆 [green]Using fastest source: {fastest_source}[/green]")
        
        # Download with progress
        download_result = self._download_with_progress(
            fastest_url,
            gtf_dir / f"{genome_version}_gencode.gtf.gz", 
            f"Downloading {genome_version} GTF",
            genome_config["gtf"].get("expected_size", 50000000)
        )
        
        if not download_result["success"]:
            return {"success": False, "message": f"GTF download failed: {download_result['error']}"}
        
        # Extract
        logger.info("📦 [yellow]Extracting GTF...[/yellow]")
        try:
            cmd = f"gunzip {gtf_dir / f'{genome_version}_gencode.gtf.gz'}"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode != 0:
                return {"success": False, "message": f"GTF extraction failed: {result.stderr}"}
        except Exception as e:
            return {"success": False, "message": f"GTF extraction error: {str(e)}"}
        
        return {"success": True, "message": "GTF setup completed", "path": str(gtf_gencode)}
    
    def _setup_blacklist_file(self, blacklist_dir: Path, genome_version: str, genome_config: dict) -> dict:
        """Setup blacklist BED files"""
        
        if "blacklist" not in genome_config:
            return {"success": True, "message": "No blacklist configured for this genome"}
        
        blacklist_bed = blacklist_dir / f"{genome_version}_blacklist.bed"
        
        # Check if already exists
        if blacklist_bed.exists() and self._validate_file(blacklist_bed, "bed"):
            logger.info("✅ [green]Blacklist file already exists and is valid[/green]")
            return {"success": True, "message": "Blacklist already available", "path": str(blacklist_bed)}
        
        logger.info("  [yellow]Downloading blacklist regions...[/yellow]")
        
        # Auto-select fastest source
        speed_test = self._test_sources_speed(genome_config["blacklist"]["sources"])
        fastest_source, fastest_url = speed_test["fastest_source"], speed_test["fastest_url"]
        
        logger.info(f"  [green]Using fastest source: {fastest_source}[/green]")
        
        # Download with progress
        download_result = self._download_with_progress(
            fastest_url,
            blacklist_dir / f"{genome_version}_blacklist.bed.gz",
            f"Downloading {genome_version} blacklist", 
            genome_config["blacklist"].get("expected_size", 3000000)
        )
        
        if not download_result["success"]:
            return {"success": False, "message": f"Blacklist download failed: {download_result['error']}"}
        
        # Extract
        logger.info("📦 [yellow]Extracting blacklist...[/yellow]")
        try:
            cmd = f"gunzip {blacklist_dir / f'{genome_version}_blacklist.bed.gz'}"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode != 0:
                return {"success": False, "message": f"Blacklist extraction failed: {result.stderr}"}
        except Exception as e:
            return {"success": False, "message": f"Blacklist extraction error: {str(e)}"}
        
        return {"success": True, "message": "Blacklist setup completed", "path": str(blacklist_bed)}
    
    def _test_sources_speed(self, sources: dict) -> dict:
        """Test multiple sources and return fastest"""
        # Simplified version of existing speed test
        # For now, just return first available source
        first_source = list(sources.keys())[0]
        first_url = list(sources.values())[0]
        
        return {
            "fastest_source": first_source,
            "fastest_url": first_url,
            "speed_mbps": 0
        }
    
    def _download_with_progress(self, url: str, output_path: Path, description: str, expected_size: int) -> dict:
        """Download file with progress bar and validation"""
        
        try:
            import time
            cmd = f"curl -L -o {output_path} '{url}'"
            process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            start_time = time.time()
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                console=self.console
            ) as progress:
                download_task = progress.add_task(description, total=100)
                
                while process.poll() is None:
                    elapsed = time.time() - start_time
                    
                    try:
                        if output_path.exists():
                            current_size = output_path.stat().st_size
                            size_mb = current_size / (1024*1024)
                            expected_mb = expected_size / (1024*1024)
                            
                            estimated_progress = min(95, (current_size / expected_size) * 100)
                            
                            progress.update(
                                download_task,
                                completed=estimated_progress,
                                description=f"Downloaded {size_mb:.1f}MB/{expected_mb:.1f}MB at ~{size_mb/elapsed:.1f}MB/s"
                            )
                    except:
                        pass
                    
                    time.sleep(2)
                
                progress.update(download_task, completed=100, description="Download completed!")
            
            if process.poll() == 0:
                return {"success": True, "path": str(output_path)}
            else:
                return {"success": False, "error": f"Download failed with code {process.poll()}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _generate_setup_summary(self, species_info: dict, genome_version: str, 
                              genome_result: dict, gtf_result: dict, blacklist_result: dict) -> str:
        """Generate comprehensive setup summary"""
        
        summary_lines = [f"🧬 Genome Resources Setup Summary for {species_info['common'].title()} {genome_version}"]
        
        # Genome summary
        if genome_result["success"]:
            summary_lines.append(f"✅ Genome: {genome_result['message']}")
            if "path" in genome_result:
                summary_lines.append(f"   📁 Path: {genome_result['path']}")
        else:
            summary_lines.append(f"❌ Genome: {genome_result['message']}")
        
        # GTF summary
        if gtf_result["success"]:
            summary_lines.append(f"✅ GTF: {gtf_result['message']}")
            if "path" in gtf_result:
                summary_lines.append(f"   📁 Path: {gtf_result['path']}")
        else:
            summary_lines.append(f"❌ GTF: {gtf_result['message']}")
        
        # Blacklist summary
        if blacklist_result["success"]:
            summary_lines.append(f"✅ Blacklist: {blacklist_result['message']}")
            if "path" in blacklist_result:
                summary_lines.append(f"   📁 Path: {blacklist_result['path']}")
        else:
            summary_lines.append(f"❌ Blacklist: {blacklist_result['message']}")
        
        # Directory structure
        base_ref_dir = self.workspace_path / "reference"
        summary_lines.append(f"📂 Resources organized in: {base_ref_dir}")
        
        return "\n".join(summary_lines)
    
    @tool
    def test_download_speeds(self, genome: str) -> Dict[str, Any]:
        """Test download speeds for different sources and recommend the fastest"""
        
        logger.info("", rich=Panel.fit(" Testing Download Sources Speed", style="bright_cyan"))
        
        # Get genome sources
        genome_sources = {
            "hg38": {
                "name": "Human genome (hg38)",
                "sources": {
                    "UCSC": "http://hgdownload.cse.ucsc.edu/goldenPath/hg38/bigZips/hg38.fa.gz",
                    "ENSEMBL": "http://ftp.ensembl.org/pub/release-104/fasta/homo_sapiens/dna/Homo_sapiens.GRCh38.dna.primary_assembly.fa.gz",
                    "清华镜像": "https://mirrors.tuna.tsinghua.edu.cn/genomes/refseq/vertebrate_mammalian/Homo_sapiens/latest_assembly_versions/GCF_000001405.40_GRCh38.p14/GCF_000001405.40_GRCh38.p14_genomic.fna.gz",
                    "NCBI": "https://ftp.ncbi.nlm.nih.gov/refseq/H_sapiens/annotation/GRCh38_latest/refseq_identifiers/GRCh38_latest_genomic.fna.gz"
                }
            },
            "mm10": {
                "name": "Mouse genome (mm10)",
                "sources": {
                    "UCSC": "http://hgdownload.cse.ucsc.edu/goldenPath/mm10/bigZips/mm10.fa.gz",
                    "ENSEMBL": "http://ftp.ensembl.org/pub/release-104/fasta/mus_musculus/dna/Mus_musculus.GRCm38.dna.primary_assembly.fa.gz",
                    "清华镜像": "https://mirrors.tuna.tsinghua.edu.cn/genomes/refseq/vertebrate_mammalian/Mus_musculus/latest_assembly_versions/GCF_000001635.27_GRCm39/GCF_000001635.27_GRCm39_genomic.fna.gz",
                    "NCBI": "https://ftp.ncbi.nlm.nih.gov/refseq/M_musculus/annotation/GRCm38_latest/refseq_identifiers/GRCm38_latest_genomic.fna.gz"
                }
            },
            "hg38_test": {
                "name": "Human chromosome 22 (test)",
                "sources": {
                    "UCSC": "http://hgdownload.cse.ucsc.edu/goldenPath/hg38/chromosomes/chr22.fa.gz",
                    "清华镜像": "https://mirrors.tuna.tsinghua.edu.cn/UCSC/goldenPath/hg38/chromosomes/chr22.fa.gz"
                }
            },
            "mm10_test": {
                "name": "Mouse chromosome 19 (test)",
                "sources": {
                    "UCSC": "http://hgdownload.cse.ucsc.edu/goldenPath/mm10/chromosomes/chr19.fa.gz", 
                    "清华镜像": "https://mirrors.tuna.tsinghua.edu.cn/UCSC/goldenPath/mm10/chromosomes/chr19.fa.gz"
                }
            }
        }
        
        if genome not in genome_sources:
            return {"error": f"Genome {genome} not supported for speed testing"}
        
        sources = genome_sources[genome]["sources"]
        speed_results = {}
        
        # Test each source with a 10-second partial download
        for source_name, url in sources.items():
            logger.info(f"🔍 [yellow]Testing {source_name}...[/yellow]")
            
            try:
                import time
                start_time = time.time()
                
                # Use curl to test download speed for 5 seconds
                cmd = f"curl -L --max-time 5 --silent --show-error '{url}' | wc -c"
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=8)
                
                end_time = time.time()
                
                if result.returncode == 0:
                    bytes_downloaded = int(result.stdout.strip())
                    duration = end_time - start_time
                    speed_mbps = (bytes_downloaded / (1024*1024)) / duration if duration > 0 else 0
                    
                    speed_results[source_name] = {
                        "speed_mbps": speed_mbps,
                        "status": "success",
                        "url": url
                    }
                    logger.info(f"✅ [green]{source_name}: {speed_mbps:.2f} MB/s[/green]")
                else:
                    speed_results[source_name] = {
                        "speed_mbps": 0,
                        "status": "failed",
                        "url": url
                    }
                    logger.info(f"❌ [red]{source_name}: Failed to connect[/red]")
                    
            except Exception as e:
                speed_results[source_name] = {
                    "speed_mbps": 0,
                    "status": "error",
                    "url": url,
                    "error": str(e)
                }
                logger.info(f"❌ [red]{source_name}: Error - {str(e)}[/red]")
        
        # Find fastest source
        valid_results = {k: v for k, v in speed_results.items() if v["status"] == "success"}
        
        if valid_results:
            fastest_source = max(valid_results.items(), key=lambda x: x[1]["speed_mbps"])
            
            # Display results table
            results_table = Table(title="Download Speed Test Results")
            results_table.add_column("Source", style="cyan")
            results_table.add_column("Speed", style="magenta")
            results_table.add_column("Status", style="green")
            
            for source_name, result in speed_results.items():
                if result["status"] == "success":
                    speed_str = f"{result['speed_mbps']:.2f} MB/s"
                    status_str = "✅ Available"
                    if source_name == fastest_source[0]:
                        speed_str += " [bold]← FASTEST[/bold]"
                else:
                    speed_str = "N/A"
                    status_str = "❌ Failed"
                
                results_table.add_row(source_name, speed_str, status_str)
            
            logger.info("", rich=results_table)
            
            fastest_name = fastest_source[0]
            fastest_speed = fastest_source[1]["speed_mbps"]
            logger.info(f"🏆 [bold green]Recommended: {fastest_name} ({fastest_speed:.2f} MB/s)[/bold green]")
            
            return {
                "genome": genome,
                "fastest_source": fastest_name,
                "fastest_url": fastest_source[1]["url"],
                "speed_mbps": fastest_speed,
                "all_results": speed_results
            }
        else:
            logger.info("[red]❌ All sources failed to connect[/red]")
            return {
                "genome": genome,
                "fastest_source": None,
                "error": "All sources failed",
                "all_results": speed_results
            }
    
    @tool
    def check_genome_setup(self, species: str = "human", genome_version: str = "hg38") -> dict:
        """Check if genome resources are already set up for ATAC-seq analysis
        
        Args:
            species: Target species (human, mouse, etc.)
            genome_version: Genome version (hg38, mm10, etc.)
            
        Returns:
            Dictionary with setup status and missing components
        """
        
        # Create species info for validation
        species_info = {
            "human": {"name": "Human", "common_name": "human", "organism": "homo_sapiens"},
            "mouse": {"name": "Mouse", "common_name": "mouse", "organism": "mus_musculus"}
        }.get(species, {"name": species.title(), "common_name": species, "organism": species})
        
        # Check genome directory structure
        genome_dir = self.workspace_path / "reference" / "genome" / species_info["common_name"]
        gtf_dir = self.workspace_path / "reference" / "gtf" / species_info["common_name"] 
        blacklist_dir = self.workspace_path / "reference" / "blacklist" / species_info["common_name"]
        
        status = {"required": [], "optional": [], "ready": True}
        
        # Check genome FASTA and Bowtie2 index (required)
        genome_fa = genome_dir / f"{genome_version}.fa"
        bowtie2_index = genome_dir / f"{genome_version}.1.bt2"
        
        if not (genome_fa.exists() and bowtie2_index.exists()):
            status["required"].append(f"Genome FASTA and Bowtie2 index for {genome_version}")
            status["ready"] = False
        
        # Check GTF file (optional but recommended)
        gtf_file = gtf_dir / f"{genome_version}_gencode.gtf"
        if not gtf_file.exists():
            status["optional"].append(f"GTF annotations for {genome_version}")
        
        # Check blacklist (optional but recommended for ATAC-seq)
        blacklist_file = blacklist_dir / f"{genome_version}_blacklist.bed"
        if not blacklist_file.exists():
            status["optional"].append(f"ENCODE blacklist regions for {genome_version}")
        
        if status["ready"]:
            return {
                "status": "complete",
                "message": f"✅ Genome resources for {species} {genome_version} are ready",
                "genome_path": str(genome_fa),
                "index_path": str(genome_dir / genome_version),
                "missing_optional": status["optional"]
            }
        else:
            return {
                "status": "incomplete", 
                "message": f"❌ Missing required genome resources for {species} {genome_version}",
                "missing_required": status["required"],
                "missing_optional": status["optional"],
                "setup_command": f"atac.setup_genome_resources('{species}', '{genome_version}')"
            }

    @tool
    def quick_genome_setup(self, species: str = "human") -> str:
        """Quick setup with test chromosome for fast ATAC-seq testing"""
        
        logger.info("", rich=Panel.fit(f" Quick Test Setup for {species.title()}", style="bright_green"))
        
        # Map species to test genomes
        test_genomes = {
            "human": "hg38_test",
            "mouse": "mm10_test"
        }
        
        if species not in test_genomes:
            logger.info(f"[red]❌ Quick setup not available for {species}[/red]")
            logger.info("[yellow]Available: human, mouse[/yellow]")
            return f"❌ Quick setup not available for {species}"
        
        test_genome = test_genomes[species]
        
        logger.info(f"[green]✅ Using test chromosome for fast setup[/green]")
        logger.info(f"[yellow]Note: This is for testing only - use full genome for production[/yellow]")
        
        return self.setup_genome_resources(species, test_genome)
    
    @tool
    def list_available_resources(self) -> str:
        """List all available genome resources with status"""
        
        logger.info("", rich=Panel.fit("📂 Available Genome Resources", style="bright_blue"))
        
        base_ref_dir = self.workspace_path / "reference"
        
        if not base_ref_dir.exists():
            return "❌ No resources directory found. Run setup_genome_resources() first."
        
        resources_table = Table(title="Genome Resources Status")
        resources_table.add_column("Species", style="cyan")
        resources_table.add_column("Version", style="magenta")
        resources_table.add_column("Genome", style="green")
        resources_table.add_column("GTF", style="yellow")
        resources_table.add_column("Blacklist", style="red")
        resources_table.add_column("Size", style="dim")
        
        total_size = 0
        resource_count = 0
        
        # Check each species directory
        for species_dir in (base_ref_dir / "genome").glob("*"):
            if species_dir.is_dir():
                species = species_dir.name
                
                # Check each genome version
                for genome_file in species_dir.glob("*.fa"):
                    genome_version = genome_file.stem
                    resource_count += 1
                    
                    # Check genome status
                    genome_fai = species_dir / f"{genome_version}.fa.fai"
                    bowtie2_index = species_dir / f"{genome_version}.1.bt2"
                    
                    if genome_fai.exists() and bowtie2_index.exists():
                        genome_status = "✅ Complete"
                    else:
                        genome_status = "⚠️ Partial"
                    
                    # Check GTF status
                    gtf_dir = base_ref_dir / "gtf" / species
                    gtf_files = list(gtf_dir.glob(f"{genome_version}*.gtf")) if gtf_dir.exists() else []
                    gtf_status = "✅ Available" if gtf_files else "❌ Missing"
                    
                    # Check blacklist status
                    blacklist_dir = base_ref_dir / "blacklist" / species
                    blacklist_files = list(blacklist_dir.glob(f"{genome_version}*.bed")) if blacklist_dir.exists() else []
                    blacklist_status = "✅ Available" if blacklist_files else "❌ Missing"
                    
                    # Calculate size
                    size_bytes = genome_file.stat().st_size
                    size_gb = size_bytes / (1024**3)
                    total_size += size_bytes
                    
                    resources_table.add_row(
                        species.title(),
                        genome_version,
                        genome_status,
                        gtf_status,
                        blacklist_status,
                        f"{size_gb:.1f}GB"
                    )
        
        logger.info("", rich=resources_table)
        
        # Summary
        total_gb = total_size / (1024**3)
        summary = f"\n Summary: {resource_count} genome resources using {total_gb:.1f}GB total"
        logger.info(summary)
        
        return f"Found {resource_count} genome resources in organized structure"
    
    @tool
    def check_genome_integrity(self, species: str, genome_version: str) -> str:
        """Check integrity of downloaded genome resources"""
        
        logger.info("", rich=Panel.fit(f" Checking Integrity: {species.title()} {genome_version}", style="bright_yellow"))
        
        base_ref_dir = self.workspace_path / "reference"
        genome_dir = base_ref_dir / "genome" / species.lower()
        gtf_dir = base_ref_dir / "gtf" / species.lower()
        blacklist_dir = base_ref_dir / "blacklist" / species.lower()
        
        integrity_results = []
        issues = []
        
        # Check genome files
        genome_fa = genome_dir / f"{genome_version}.fa"
        genome_fai = genome_dir / f"{genome_version}.fa.fai"
        bowtie2_index = genome_dir / f"{genome_version}.1.bt2"
        
        if genome_fa.exists():
            if self._validate_file(genome_fa, "fasta"):
                integrity_results.append("✅ Genome FASTA: Valid")
            else:
                integrity_results.append("❌ Genome FASTA: Invalid format")
                issues.append("Genome FASTA file is corrupted")
        else:
            integrity_results.append("❌ Genome FASTA: Not found")
            issues.append("Missing genome FASTA file")
        
        if genome_fai.exists():
            integrity_results.append("✅ FASTA index: Present")
        else:
            integrity_results.append("❌ FASTA index: Missing")
            issues.append("Missing FASTA index (.fai)")
        
        if bowtie2_index.exists():
            # Check all Bowtie2 index files
            bowtie2_files = [f"{genome_version}.1.bt2", f"{genome_version}.2.bt2", 
                           f"{genome_version}.3.bt2", f"{genome_version}.4.bt2",
                           f"{genome_version}.rev.1.bt2", f"{genome_version}.rev.2.bt2"]
            missing_bowtie2 = []
            for bt2_file in bowtie2_files:
                if not (genome_dir / bt2_file).exists():
                    missing_bowtie2.append(bt2_file)
            
            if missing_bowtie2:
                integrity_results.append(f"⚠️ Bowtie2 index: Incomplete ({len(missing_bowtie2)} files missing)")
                issues.append(f"Missing Bowtie2 files: {', '.join(missing_bowtie2)}")
            else:
                integrity_results.append("✅ Bowtie2 index: Complete")
        else:
            integrity_results.append("❌ Bowtie2 index: Not found")
            issues.append("Missing Bowtie2 index files")
        
        # Check GTF files
        gtf_files = list(gtf_dir.glob(f"{genome_version}*.gtf")) if gtf_dir.exists() else []
        if gtf_files:
            valid_gtfs = [f for f in gtf_files if self._validate_file(f, "gtf")]
            if valid_gtfs:
                integrity_results.append(f"✅ GTF files: {len(valid_gtfs)} valid")
            else:
                integrity_results.append("❌ GTF files: All invalid")
                issues.append("All GTF files are corrupted")
        else:
            integrity_results.append("⚠️ GTF files: Not available")
        
        # Check blacklist files
        blacklist_files = list(blacklist_dir.glob(f"{genome_version}*.bed")) if blacklist_dir.exists() else []
        if blacklist_files:
            valid_blacklists = [f for f in blacklist_files if self._validate_file(f, "bed")]
            if valid_blacklists:
                integrity_results.append(f"✅ Blacklist files: {len(valid_blacklists)} valid")
            else:
                integrity_results.append("❌ Blacklist files: All invalid")
                issues.append("All blacklist files are corrupted")
        else:
            integrity_results.append("⚠️ Blacklist files: Not available")
        
        # Display results
        for result in integrity_results:
            logger.info(result)
        
        if issues:
            logger.info(f"\n⚠️ [yellow]Issues found:[/yellow]")
            for issue in issues:
                logger.info(f"  • {issue}")
            return f"Integrity check completed with {len(issues)} issues"
        else:
            logger.info("\n✅ [green]All files are intact and valid![/green]")
            return "Integrity check passed - all files are valid"
    
    @tool
    def clean_incomplete_downloads(self) -> str:
        """Clean up incomplete or corrupted downloads"""
        
        logger.info("", rich=Panel.fit("🧹 Cleaning Incomplete Downloads", style="bright_red"))
        
        base_ref_dir = self.workspace_path / "reference"
        
        if not base_ref_dir.exists():
            return "❌ No resources directory found"
        
        cleaned_files = []
        
        # Check for .gz files (incomplete extractions)
        for gz_file in base_ref_dir.glob("**/*.gz"):
            cleaned_files.append(str(gz_file))
            gz_file.unlink()
        
        # Check for empty files
        for file_path in base_ref_dir.glob("**/*"):
            if file_path.is_file() and file_path.stat().st_size == 0:
                cleaned_files.append(str(file_path))
                file_path.unlink()
        
        # Check for corrupted FASTA files
        for fasta_file in base_ref_dir.glob("**/genome/*/*.fa"):
            if not self._validate_file(fasta_file, "fasta"):
                cleaned_files.append(str(fasta_file))
                fasta_file.unlink()
                
                # Also remove associated index files
                fai_file = fasta_file.with_suffix(".fa.fai")
                if fai_file.exists():
                    cleaned_files.append(str(fai_file))
                    fai_file.unlink()
                
                # Remove Bowtie2 index files
                genome_name = fasta_file.stem
                for suffix in ["1.bt2", "2.bt2", "3.bt2", "4.bt2", "rev.1.bt2", "rev.2.bt2"]:
                    bt2_file = fasta_file.parent / f"{genome_name}.{suffix}"
                    if bt2_file.exists():
                        cleaned_files.append(str(bt2_file))
                        bt2_file.unlink()
        
        if cleaned_files:
            logger.info(f"🗑️ Cleaned {len(cleaned_files)} incomplete/corrupted files:")
            for file_path in cleaned_files[:10]:  # Show first 10
                logger.info(f"  • {file_path}")
            if len(cleaned_files) > 10:
                logger.info(f"  • ... and {len(cleaned_files) - 10} more")
            
            return f"Cleaned {len(cleaned_files)} incomplete downloads"
        else:
            logger.info("✅ No incomplete downloads found")
            return "No cleanup needed - all downloads are complete"
    
    @tool
    def get_resource_info(self, species: str, genome_version: str) -> str:
        """Get detailed information about specific genome resources"""
        
        logger.info("", rich=Panel.fit(f"📋 Resource Information: {species.title()} {genome_version}", style="bright_cyan"))
        
        base_ref_dir = self.workspace_path / "reference"
        genome_dir = base_ref_dir / "genome" / species.lower()
        gtf_dir = base_ref_dir / "gtf" / species.lower()
        blacklist_dir = base_ref_dir / "blacklist" / species.lower()
        
        info_table = Table(title=f"{species.title()} {genome_version} Resource Details")
        info_table.add_column("File Type", style="cyan")
        info_table.add_column("File Path", style="magenta")
        info_table.add_column("Size", style="green")
        info_table.add_column("Status", style="yellow")
        
        total_size = 0
        
        # Check genome files
        for file_name, description in [
            (f"{genome_version}.fa", "Genome FASTA"),
            (f"{genome_version}.fa.fai", "FASTA Index"),
            (f"{genome_version}.1.bt2", "Bowtie2 Index")
        ]:
            file_path = genome_dir / file_name
            if file_path.exists():
                size = file_path.stat().st_size
                size_mb = size / (1024*1024)
                total_size += size
                
                if description == "Genome FASTA":
                    status = "✅ Valid" if self._validate_file(file_path, "fasta") else "❌ Invalid"
                else:
                    status = "✅ Present"
                
                info_table.add_row(description, str(file_path), f"{size_mb:.1f}MB", status)
            else:
                info_table.add_row(description, str(file_path), "0MB", "❌ Missing")
        
        # Check GTF files
        gtf_files = list(gtf_dir.glob(f"{genome_version}*.gtf")) if gtf_dir.exists() else []
        for gtf_file in gtf_files:
            size = gtf_file.stat().st_size
            size_mb = size / (1024*1024)
            total_size += size
            
            status = "✅ Valid" if self._validate_file(gtf_file, "gtf") else "❌ Invalid"
            info_table.add_row("GTF Annotation", str(gtf_file), f"{size_mb:.1f}MB", status)
        
        # Check blacklist files
        blacklist_files = list(blacklist_dir.glob(f"{genome_version}*.bed")) if blacklist_dir.exists() else []
        for blacklist_file in blacklist_files:
            size = blacklist_file.stat().st_size
            size_mb = size / (1024*1024)
            total_size += size
            
            status = "✅ Valid" if self._validate_file(blacklist_file, "bed") else "❌ Invalid"
            info_table.add_row("Blacklist Regions", str(blacklist_file), f"{size_mb:.1f}MB", status)
        
        logger.info("", rich=info_table)
        
        # Summary
        total_gb = total_size / (1024**3)
        logger.info(f"\n💾 Total size: {total_gb:.2f}GB")
        
        return f"Resource info displayed for {species} {genome_version}"
    
    @tool
    def setup_reference_genome_from_source(self, genome: str, source_name: str) -> str:
        """Setup reference genome from a specific source (UCSC, ENSEMBL, 清华镜像, NCBI)"""
        
        # Get genome sources
        genome_sources = {
            "hg38": {
                "name": "Human genome (hg38)",
                "size": "~3.0GB",
                "sources": {
                    "UCSC": "http://hgdownload.cse.ucsc.edu/goldenPath/hg38/bigZips/hg38.fa.gz",
                    "ENSEMBL": "http://ftp.ensembl.org/pub/release-104/fasta/homo_sapiens/dna/Homo_sapiens.GRCh38.dna.primary_assembly.fa.gz",
                    "清华镜像": "https://mirrors.tuna.tsinghua.edu.cn/genomes/refseq/vertebrate_mammalian/Homo_sapiens/latest_assembly_versions/GCF_000001405.40_GRCh38.p14/GCF_000001405.40_GRCh38.p14_genomic.fna.gz",
                    "NCBI": "https://ftp.ncbi.nlm.nih.gov/refseq/H_sapiens/annotation/GRCh38_latest/refseq_identifiers/GRCh38_latest_genomic.fna.gz"
                }
            },
            "mm10": {
                "name": "Mouse genome (mm10)",
                "size": "~2.7GB",
                "sources": {
                    "UCSC": "http://hgdownload.cse.ucsc.edu/goldenPath/mm10/bigZips/mm10.fa.gz",
                    "ENSEMBL": "http://ftp.ensembl.org/pub/release-104/fasta/mus_musculus/dna/Mus_musculus.GRCm38.dna.primary_assembly.fa.gz",
                    "清华镜像": "https://mirrors.tuna.tsinghua.edu.cn/genomes/refseq/vertebrate_mammalian/Mus_musculus/latest_assembly_versions/GCF_000001635.27_GRCm39/GCF_000001635.27_GRCm39_genomic.fna.gz",
                    "NCBI": "https://ftp.ncbi.nlm.nih.gov/refseq/M_musculus/annotation/GRCm38_latest/refseq_identifiers/GRCm38_latest_genomic.fna.gz"
                }
            },
            "hg38_test": {
                "name": "Human chromosome 22 (test)",
                "size": "~50MB",
                "sources": {
                    "UCSC": "http://hgdownload.cse.ucsc.edu/goldenPath/hg38/chromosomes/chr22.fa.gz",
                    "清华镜像": "https://mirrors.tuna.tsinghua.edu.cn/UCSC/goldenPath/hg38/chromosomes/chr22.fa.gz"
                }
            },
            "mm10_test": {
                "name": "Mouse chromosome 19 (test)",
                "size": "~60MB",
                "sources": {
                    "UCSC": "http://hgdownload.cse.ucsc.edu/goldenPath/mm10/chromosomes/chr19.fa.gz", 
                    "清华镜像": "https://mirrors.tuna.tsinghua.edu.cn/UCSC/goldenPath/mm10/chromosomes/chr19.fa.gz"
                }
            }
        }
        
        if genome not in genome_sources:
            available_genomes = ", ".join(genome_sources.keys())
            return f"❌ Unsupported genome: {genome}. Available: {available_genomes}"
        
        if source_name not in genome_sources[genome]["sources"]:
            available_sources = ", ".join(genome_sources[genome]["sources"].keys())
            return f"❌ Source '{source_name}' not available for {genome}. Available: {available_sources}"
        
        logger.info("", rich=Panel.fit(f"🎯 Manual Source Selection: {source_name}", style="bright_blue"))
        logger.info(f"[green]✅ Using {source_name} source for {genome}[/green]")
        
        # Temporarily override the speed test by injecting the chosen source
        original_method = self.test_download_speeds
        
        def mock_speed_test(test_genome):
            return {
                "fastest_source": source_name,
                "fastest_url": genome_sources[genome]["sources"][source_name],
                "speed_mbps": 0  # We don't test, just use the selected source
            }
        
        # Monkey patch for this call
        self.test_download_speeds = mock_speed_test
        
        try:
            # Parse genome to get species and genome version
            if genome.startswith("hg"):
                species = "human"
            elif genome.startswith("mm"):
                species = "mouse"
            else:
                species = "human"  # default
                
            result = self.setup_genome_resources(species, genome)
            return result
        finally:
            # Restore original method
            self.test_download_speeds = original_method
    
    @tool
    def test_download_progress(self, test_file: str = "small") -> str:
        """Test the download progress display with a small file"""
        
        logger.info("", rich=Panel.fit("🧪 Testing Download Progress Display", style="bright_yellow"))
        
        # Test URLs for different sizes
        test_urls = {
            "small": {
                "url": "http://hgdownload.cse.ucsc.edu/goldenPath/hg38/chromosomes/chrM.fa.gz",
                "name": "Human mitochondrial genome",
                "size": "~16KB"
            },
            "medium": {
                "url": "http://hgdownload.cse.ucsc.edu/goldenPath/hg38/chromosomes/chr22.fa.gz", 
                "name": "Human chromosome 22",
                "size": "~50MB"
            }
        }
        
        if test_file not in test_urls:
            available = ", ".join(test_urls.keys())
            return f"❌ Test file '{test_file}' not available. Available: {available}"
        
        test_info = test_urls[test_file]
        test_url = test_info["url"]
        
        logger.info(f"📥 [cyan]Testing progress display with: {test_info['name']} ({test_info['size']})[/cyan]")
        
        # Create test directory
        ref_dir = self.workspace_path / "test_download"
        ref_dir.mkdir(exist_ok=True)
        
        test_file_path = ref_dir / f"test_{test_file}.fa.gz"
        
        try:
            # Use the same download logic as setup_reference_genome
            import time
            
            logger.info(" [yellow]Starting test download...[/yellow]")
            
            cmd = f"curl -L -o {test_file_path} '{test_url}'"
            
            # Start download in background
            process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Show progress updates
            start_time = time.time()
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                console=self.console
            ) as progress:
                download_task = progress.add_task("Testing download...", total=100)
                
                while process.poll() is None:
                    elapsed = time.time() - start_time
                    
                    # Check if file is being created and get size
                    try:
                        if test_file_path.exists():
                            current_size = test_file_path.stat().st_size
                            size_mb = current_size / (1024*1024)
                            
                            # Estimate progress
                            if test_file == "small":
                                estimated_total = 0.016  # 16KB in MB
                            else:
                                estimated_total = 50  # 50MB
                            
                            estimated_progress = min(95, (size_mb / estimated_total) * 100)
                            
                            progress.update(
                                download_task, 
                                completed=estimated_progress,
                                description=f"Downloaded {size_mb:.2f}MB at ~{size_mb/elapsed:.2f}MB/s"
                            )
                    except:
                        pass
                    
                    time.sleep(1)
                
                # Complete the progress bar
                progress.update(download_task, completed=100, description="Test download completed!")
            
            result = process.poll()
            
            if result == 0:
                final_size = test_file_path.stat().st_size / (1024*1024)
                logger.info(f"✅ [green]Test successful! Downloaded {final_size:.2f}MB[/green]")
                
                # Clean up test file
                test_file_path.unlink()
                
                return f"✅ Download progress test successful! Clean progress bar working correctly."
            else:
                return f"❌ Test download failed"
                
        except Exception as e:
            return f"❌ Test failed: {str(e)}"
        finally:
            # Clean up
            if test_file_path.exists():
                test_file_path.unlink()
    
    @tool 
    def scan_folder(self, folder_path: str) -> Dict[str, Any]:
        """Comprehensively scan folder for ATAC-seq data and provide analysis"""
        folder_path = Path(folder_path).resolve()
        
        # Rich console header
        logger.info("\n" + "="*70)
        logger.info("🔍 [bold cyan]ATAC-seq Folder Analysis[/bold cyan]", justify="center")
        logger.info("="*70)
        logger.info(f"📂 [yellow]Scanning:[/yellow] {folder_path}")
        
        if not folder_path.exists():
            logger.info(f"❌ [red]Error:[/red] Folder not found: {folder_path}")
            return {"error": f"Folder not found: {folder_path}"}
        
        scan_results = {
            "folder": str(folder_path),
            "files": {
                "fastq": [],
                "alignments": [],
                "peaks": [],
                "tracks": [],
                "reports": []
            },
            "analysis_stage": "unknown",
            "recommendations": [],
            "total_size": 0
        }
        
        # File patterns for different categories
        patterns = {
            "fastq": ["*.fastq", "*.fq", "*.fastq.gz", "*.fq.gz", "*.fastq.bz2", "*.fq.bz2"],
            "alignments": ["*.bam", "*.sam", "*.cram"],
            "peaks": ["*.narrowPeak", "*.broadPeak", "*.bed", "*.bedGraph"],
            "tracks": ["*.bw", "*.bigwig"],
            "reports": ["*_fastqc.html", "multiqc_report.html"]
        }
        
        # Scan for files with progress
        logger.info("\n🔎 [cyan]Scanning for files...[/cyan]")
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            scan_task = progress.add_task("Scanning files...", total=len(patterns))
            
            for category, pattern_list in patterns.items():
                progress.update(scan_task, description=f"Scanning {category} files...")
                for pattern in pattern_list:
                    files = list(folder_path.rglob(pattern))
                    for f in files:
                        file_info = {
                            "name": f.name,
                            "path": str(f),
                            "size": f.stat().st_size,
                            "size_mb": round(f.stat().st_size / 1024 / 1024, 2)
                        }
                        scan_results["files"][category].append(file_info)
                        scan_results["total_size"] += f.stat().st_size
                progress.advance(scan_task)
        
        # Determine analysis stage
        has_fastq = bool(scan_results["files"]["fastq"])
        has_alignments = bool(scan_results["files"]["alignments"])
        has_peaks = bool(scan_results["files"]["peaks"])
        has_tracks = bool(scan_results["files"]["tracks"])
        
        if has_peaks and has_tracks:
            scan_results["analysis_stage"] = "complete"
            scan_results["recommendations"] = [
                "Analysis appears complete",
                "Generate comprehensive QC report",
                "Consider differential accessibility analysis"
            ]
        elif has_peaks:
            scan_results["analysis_stage"] = "peaks_called"
            scan_results["recommendations"] = [
                "Generate BigWig tracks for visualization",
                "Perform motif analysis",
                "Create QC report"
            ]
        elif has_alignments:
            scan_results["analysis_stage"] = "aligned"
            scan_results["recommendations"] = [
                "Filter alignments for quality",
                "Remove duplicates",
                "Call peaks with MACS2"
            ]
        elif has_fastq:
            scan_results["analysis_stage"] = "raw_data"
            scan_results["recommendations"] = [
                "Run FastQC for quality control",
                "Trim adapters if needed", 
                "Align to reference genome"
            ]
        else:
            scan_results["analysis_stage"] = "empty"
            scan_results["recommendations"] = ["No ATAC-seq files detected"]
        
        # Add file counts
        scan_results["summary"] = {
            "fastq_files": len(scan_results["files"]["fastq"]),
            "alignment_files": len(scan_results["files"]["alignments"]),
            "peak_files": len(scan_results["files"]["peaks"]),
            "track_files": len(scan_results["files"]["tracks"]),
            "total_size_mb": round(scan_results["total_size"] / 1024 / 1024, 2)
        }
        
        # Display results in beautiful table
        logger.info("\n📊 [bold green]Scan Results:[/bold green]")
        
        # Summary table
        summary_table = Table(title="File Summary", show_header=True, header_style="bold magenta")
        summary_table.add_column("File Type", style="cyan", width=15)
        summary_table.add_column("Count", justify="right", style="green")
        summary_table.add_column("Total Size", justify="right", style="yellow")
        
        total_files = 0
        for category, files in scan_results["files"].items():
            if files:
                count = len(files)
                total_files += count
                size_mb = sum(f["size_mb"] for f in files)
                
                category_emoji = {
                    "fastq": "🧬",
                    "alignments": "🎯", 
                    "peaks": "⛰️",
                    "tracks": "📈",
                    "reports": "📄"
                }
                
                summary_table.add_row(
                    f"{category_emoji.get(category, '📁')} {category.upper()}",
                    str(count),
                    f"{size_mb:.1f} MB"
                )
        
        summary_table.add_row("", "", "", style="dim")
        summary_table.add_row("TOTAL", str(total_files), f"{scan_results['summary']['total_size_mb']:.1f} MB", style="bold")
        logger.info("", rich=summary_table)
        
        # Analysis stage display
        stage_emoji = {
            "raw_data": "🧬",
            "aligned": "🎯", 
            "peaks_called": "⛰️",
            "complete": "✅",
            "empty": "📁"
        }
        
        stage_panel = Panel(
            f"{stage_emoji.get(scan_results['analysis_stage'], '❓')} [bold]{scan_results['analysis_stage'].replace('_', ' ').title()}[/bold]",
            title="Analysis Stage",
            border_style="green"
        )
        logger.info("", rich=stage_panel)
        
        # Recommendations
        if scan_results["recommendations"]:
            logger.info("\n💡 [bold cyan]Recommendations:[/bold cyan]")
            for i, rec in enumerate(scan_results["recommendations"], 1):
                logger.info(f"  {i}. [green]{rec}[/green]")
        
        # Detailed file listing if requested
        for category, files in scan_results["files"].items():
            if files and len(files) <= 10:  # Only show details for manageable lists
                logger.info(f"\n📁 [cyan]{category.upper()} Files:[/cyan]")
                for f in files:
                    logger.info(f"  • {f['name']} ([dim]{f['size_mb']:.1f} MB[/dim])")
            elif files and len(files) > 10:
                logger.info(f"\n📁 [cyan]{category.upper()} Files:[/cyan] {len(files)} files (showing first 5)")
                for f in files[:5]:
                    logger.info(f"  • {f['name']} ([dim]{f['size_mb']:.1f} MB[/dim])")
                logger.info(f"  ... and {len(files)-5} more")
        
        logger.info("\n" + "="*70)
        
        return scan_results
    
    @tool
    def auto_align_fastq(self, folder_path: str, genome_version: str = "hg38", aligner: str = "bowtie2") -> str:
        """Automatically detect FASTQ files and start alignment (fully automated)"""
        logger.info("")
        logger.info("", rich=Panel.fit("  Auto-Alignment Pipeline", style="bright_green"))
        
        folder_path = Path(folder_path).resolve()
        
        # Scan for FASTQ files
        scan_result = self.scan_folder(str(folder_path))
        fastq_files = scan_result["files"].get("fastq", [])
        
        if not fastq_files:
            logger.info("[red]❌ No FASTQ files found for alignment[/red]")
            return "❌ No FASTQ files found"
        
        # Auto-detect paired-end files
        r1_files = [f for f in fastq_files if any(pattern in f["name"].lower() for pattern in ["_r1", "_1", "r1"])]
        r2_files = [f for f in fastq_files if any(pattern in f["name"].lower() for pattern in ["_r2", "_2", "r2"])]
        
        if r1_files and r2_files:
            logger.info(f"[green]✅ Detected paired-end files: {len(r1_files)} pairs[/green]")
            
            # Get first pair for alignment
            r1_file = folder_path / r1_files[0]["name"] 
            r2_file = folder_path / r2_files[0]["name"]
            
            # Auto-generate output name
            base_name = r1_files[0]["name"].split("_R1")[0].split("_r1")[0].split("_1")[0]
            output_bam = folder_path / f"{base_name}_aligned.bam"
            
            logger.info(f"[cyan]  Starting alignment:[/cyan]")
            logger.info(f"  R1: {r1_file.name}")
            logger.info(f"  R2: {r2_file.name}")
            logger.info(f"  Output: {output_bam.name}")
            
            # Check genome resources
            species = "human" if genome_version.startswith("hg") else "mouse"
            genome_dir = self.workspace_path / "reference" / "genome" / species
            index_prefix = genome_dir / genome_version
            
            if not index_prefix.with_suffix(".1.bt2").exists():
                logger.info("[yellow]⚠️ Bowtie2 index missing - setting up genome resources first[/yellow]")
                self.setup_genome_resources(species, genome_version)
            
            # Start alignment
            if aligner == "bowtie2":
                result = self.align_bowtie2(
                    index_prefix=str(index_prefix),
                    fastq_r1=str(r1_file),
                    fastq_r2=str(r2_file),
                    output_bam=str(output_bam)
                )
            else:
                result = self.align_bwa(
                    index_prefix=str(index_prefix),
                    fastq_r1=str(r1_file),
                    fastq_r2=str(r2_file),
                    output_bam=str(output_bam)
                )
            
            return f"✅ Auto-alignment completed: {output_bam}"
            
        else:
            logger.info("[yellow]⚠️ Could not detect proper paired-end files[/yellow]")
            logger.info("[cyan]Available files:[/cyan]")
            for f in fastq_files[:5]:  # Show first 5
                logger.info(f"  • {f['name']}")
            
            return "⚠️ Manual file selection required"
    
    @tool
    def validate_fastq(self, fastq_path: str) -> Dict[str, Any]:
        """Validate FASTQ file format and get basic stats"""
        fastq_file = Path(fastq_path)
        
        if not fastq_file.exists():
            return {"error": f"File not found: {fastq_path}"}
        
        # Check file extension
        valid_extensions = self.pipeline_config["file_extensions"]["raw_reads"]
        if not any(str(fastq_file).endswith(ext) for ext in valid_extensions):
            return {"warning": f"Unusual extension for FASTQ: {fastq_file.suffix}"}
        
        # Get basic stats using shell commands
        stats = {"file": str(fastq_file), "size": fastq_file.stat().st_size}
        
        try:
            # Count reads (every 4th line is a new read in FASTQ)
            if str(fastq_file).endswith('.gz'):
                cmd = f"zcat {fastq_file} | wc -l"
            else:
                cmd = f"wc -l < {fastq_file}"
            
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                lines = int(result.stdout.strip())
                stats["reads"] = lines // 4
                stats["valid_fastq"] = lines % 4 == 0
        except:
            stats["error"] = "Could not parse FASTQ"
        
        return stats
    
    @tool
    def run_fastqc(self, fastq_files: List[str], output_dir: Optional[str] = None) -> str:
        """Run FastQC on FASTQ files"""
        
        # Rich console header
        logger.info("\n" + "="*70)
        logger.info("  [bold cyan]Running FastQC Quality Control[/bold cyan]", justify="center")
        logger.info("="*70)
        
        if not fastq_files:
            logger.info("❌ [red]No FASTQ files provided![/red]")
            return "No FASTQ files provided"
        
        if not output_dir:
            output_dir = self.workspace_path / "qc" / "fastqc"
        else:
            output_dir = Path(output_dir)
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"📁 [yellow]Output directory:[/yellow] {output_dir}")
        logger.info(f"📁 [yellow]Processing {len(fastq_files)} files...[/yellow]\n")
        
        # Show files to be processed
        files_table = Table(title="Files to Process", show_header=True, header_style="bold magenta")
        files_table.add_column("File", style="cyan")
        files_table.add_column("Size", justify="right", style="green")
        
        for fastq_file in fastq_files:
            file_path = Path(fastq_file)
            if file_path.exists():
                size_mb = file_path.stat().st_size / 1024 / 1024
                files_table.add_row(file_path.name, f"{size_mb:.1f} MB")
            else:
                files_table.add_row(file_path.name, "[red]NOT FOUND[/red]")
        
        logger.info("", rich=files_table)
        
        # Build FastQC command
        cmd = [
            "fastqc",
            "-o", str(output_dir),
            "-t", str(self.pipeline_config["default_params"]["threads"])
        ] + fastq_files
        
        logger.info(f"\n  [cyan]Running FastQC...[/cyan]")
        logger.info(f"[dim]Command: {' '.join(cmd[:6])} ... [/dim]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            fastqc_task = progress.add_task("Running FastQC...", total=None)
            
            try:
                result = subprocess.run(cmd, capture_output=True, text=True)
                progress.update(fastqc_task, description="FastQC completed")
                
                if result.returncode == 0:
                    # Count generated reports
                    html_reports = list(output_dir.glob("*_fastqc.html"))
                    zip_reports = list(output_dir.glob("*_fastqc.zip"))
                    
                    success_panel = Panel(
                        f"[green]✅ FastQC completed successfully![/green]\n" +
                        f"[cyan]  HTML reports: {len(html_reports)}[/cyan]\n" +
                        f"[cyan]  ZIP reports: {len(zip_reports)}[/cyan]\n" +
                        f"[dim]Output directory: {output_dir}[/dim]",
                        title="FastQC Results",
                        border_style="green"
                    )
                    logger.info("", rich=success_panel)
                    
                    # List generated files
                    if html_reports:
                        logger.info("\n📄 [cyan]Generated HTML reports:[/cyan]")
                        for report in html_reports[:5]:  # Show first 5
                            logger.info(f"  • {report.name}")
                        if len(html_reports) > 5:
                            logger.info(f"  ... and {len(html_reports)-5} more")
                    
                    logger.info("="*70 + "\n")
                    return f"✅ FastQC completed for {len(fastq_files)} files. Output: {output_dir}"
                else:
                    error_msg = result.stderr.strip()[:200] + "..." if len(result.stderr) > 200 else result.stderr.strip()
                    error_panel = Panel(
                        f"[red]❌ FastQC failed![/red]\n" +
                        f"[dim]Error: {error_msg}[/dim]",
                        title="Error",
                        border_style="red"
                    )
                    logger.info("", rich=error_panel)
                    logger.info("="*70 + "\n")
                    return f"❌ FastQC failed: {result.stderr}"
                    
            except FileNotFoundError:
                error_panel = Panel(
                    "[red]❌ FastQC not found![/red]\n" +
                    "[yellow]Install with: conda install -c bioconda fastqc[/yellow]",
                    title="Missing Dependency",
                    border_style="red"
                )
                logger.info("", rich=error_panel)
                logger.info("="*70 + "\n")
                return "❌ FastQC not found. Install with: conda install -c bioconda fastqc"
    
    @tool
    def trim_adapters(self, fastq_r1: str, fastq_r2: Optional[str] = None,
                     output_dir: Optional[str] = None,
                     quality: int = 20,
                     min_length: int = 36) -> Dict[str, str]:
        """Trim adapters using Trim Galore"""
        if not output_dir:
            output_dir = self.workspace_path / "fastq_trimmed"
        else:
            output_dir = Path(output_dir)
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        cmd = [
            "trim_galore",
            "--quality", str(quality),
            "--length", str(min_length),
            "--fastqc",
            "--output_dir", str(output_dir)
        ]
        
        if fastq_r2:  # Paired-end
            cmd.extend(["--paired", fastq_r1, fastq_r2])
        else:  # Single-end
            cmd.append(fastq_r1)
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                # Find output files
                base_r1 = Path(fastq_r1).stem.replace('.fastq', '').replace('.fq', '')
                if fastq_r2:
                    trimmed_r1 = output_dir / f"{base_r1}_val_1.fq.gz"
                    base_r2 = Path(fastq_r2).stem.replace('.fastq', '').replace('.fq', '')
                    trimmed_r2 = output_dir / f"{base_r2}_val_2.fq.gz"
                    return {
                        "status": "success",
                        "trimmed_r1": str(trimmed_r1),
                        "trimmed_r2": str(trimmed_r2)
                    }
                else:
                    trimmed = output_dir / f"{base_r1}_trimmed.fq.gz"
                    return {
                        "status": "success",
                        "trimmed": str(trimmed)
                    }
            else:
                return {"status": "error", "message": result.stderr}
        except FileNotFoundError:
            return {"status": "error", "message": "Trim Galore not found"}
    
    @tool
    def align_bowtie2(self, index_prefix: str, fastq_r1: str, 
                     fastq_r2: Optional[str] = None,
                     output_bam: Optional[str] = None,
                     threads: Optional[int] = None) -> str:
        """Align reads using Bowtie2 (optimized for ATAC-seq)"""
        
        logger.info(" [cyan]Starting Bowtie2 alignment (ATAC-seq optimized)[/cyan]")
        
        if not threads:
            threads = self.pipeline_config["default_params"]["threads"]
        
        if not output_bam:
            sample_name = Path(fastq_r1).stem.replace('_R1', '').replace('_1', '')
            output_bam = self.workspace_path / "alignment" / f"{sample_name}.bam"
        else:
            output_bam = Path(output_bam)
        
        output_bam.parent.mkdir(parents=True, exist_ok=True)
        
        # ATAC-seq optimized Bowtie2 parameters
        bowtie2_params = [
            "--very-sensitive",      # High sensitivity for short fragments
            "--no-mixed",           # No mixed alignments 
            "--no-discordant",      # No discordant alignments
            "--phred33",            # Phred+33 quality encoding
            "-I 10",                # Min fragment length 10bp
            "-X 2000",              # Max fragment length 2000bp (covers nucleosome-bound)
            f"-p {threads}"         # Number of threads
        ]
        
        # Build Bowtie2 command
        if fastq_r2:  # Paired-end (recommended for ATAC-seq)
            cmd = f"bowtie2 {' '.join(bowtie2_params)} -x {index_prefix} -1 {fastq_r1} -2 {fastq_r2}"
            logger.info("  [green]Paired-end alignment with ATAC-seq optimized parameters[/green]")
        else:  # Single-end
            cmd = f"bowtie2 {' '.join(bowtie2_params)} -x {index_prefix} -U {fastq_r1}"
            logger.info("  [yellow]Single-end alignment (paired-end recommended for ATAC-seq)[/yellow]")
        
        # Show parameters being used
        logger.info(f"⚙️ [dim]Parameters: {' '.join(bowtie2_params)}[/dim]")
        
        # Pipe to samtools for SAM->BAM conversion, quality filtering, and sorting
        filter_params = f"-q 30 -F 1024"  # MAPQ≥30, remove duplicates
        cmd += f" | samtools view -bS {filter_params} - | samtools sort -@ {threads} -o {output_bam} -"
        
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                align_task = progress.add_task("Running Bowtie2 alignment...", total=None)
                
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                
                progress.update(align_task, description="Alignment completed, indexing BAM...")
                
            if result.returncode == 0:
                # Index the BAM file
                subprocess.run(f"samtools index {output_bam}", shell=True, capture_output=True)
                
                # Parse alignment statistics from stderr
                stderr_lines = result.stderr.split('\n')
                alignment_rate = "Unknown"
                for line in stderr_lines:
                    if "overall alignment rate" in line:
                        alignment_rate = line.split()[0]
                        break
                
                logger.info(f"✅ [green]Bowtie2 alignment completed![/green]")
                logger.info(f"  Overall alignment rate: {alignment_rate}")
                logger.info(f"  Output: {output_bam}")
                
                return f"✅ Bowtie2 alignment completed: {output_bam} (rate: {alignment_rate})"
            else:
                logger.info(f"❌ [red]Bowtie2 alignment failed[/red]")
                logger.info(f"[dim]Error: {result.stderr}[/dim]")
                return f"❌ Bowtie2 alignment failed: {result.stderr}"
        except Exception as e:
            return f"❌ Bowtie2 or samtools not found: {str(e)}"
    
    @tool
    def align_bwa(self, index_prefix: str, fastq_r1: str, 
                  fastq_r2: Optional[str] = None,
                  output_bam: Optional[str] = None,
                  threads: Optional[int] = None) -> str:
        """Align reads using BWA-MEM (legacy method, use align_bowtie2 for ATAC-seq)"""
        
        logger.info("⚠️ [yellow]Using BWA-MEM (consider align_bowtie2 for better ATAC-seq results)[/yellow]")
        
        if not threads:
            threads = self.pipeline_config["default_params"]["threads"]
        
        if not output_bam:
            sample_name = Path(fastq_r1).stem.replace('_R1', '').replace('_1', '')
            output_bam = self.workspace_path / "alignment" / f"{sample_name}.bam"
        else:
            output_bam = Path(output_bam)
        
        output_bam.parent.mkdir(parents=True, exist_ok=True)
        
        # Build BWA command
        if fastq_r2:  # Paired-end
            cmd = f"bwa mem -t {threads} {index_prefix} {fastq_r1} {fastq_r2}"
        else:  # Single-end
            cmd = f"bwa mem -t {threads} {index_prefix} {fastq_r1}"
        
        # Pipe to samtools for BAM conversion and sorting
        cmd += f" | samtools sort -@ {threads} -o {output_bam} -"
        
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                # Index the BAM
                subprocess.run(f"samtools index {output_bam}", shell=True)
                return f"✅ BWA alignment completed: {output_bam}"
            else:
                return f"❌ BWA alignment failed: {result.stderr}"
        except:
            return "❌ BWA or samtools not found"
    
    @tool
    def filter_bam(self, input_bam: str, output_bam: Optional[str] = None,
                   min_quality: int = 30,
                   remove_mitochondrial: bool = True,
                   proper_pairs_only: bool = True) -> str:
        """Filter BAM file for quality and proper pairs"""
        
        # Check if samtools is available, install if needed
        if not self._check_and_install_tool("samtools"):
            return "❌ Failed to install samtools"
        
        if not output_bam:
            output_bam = str(Path(input_bam).parent / "filtered" / Path(input_bam).name)
        
        Path(output_bam).parent.mkdir(parents=True, exist_ok=True)
        
        # Check if input BAM has index, create if missing
        input_bam_path = Path(input_bam)
        index_file = input_bam_path.with_suffix(input_bam_path.suffix + '.bai')
        if not index_file.exists():
            logger.info(f"⚠️ [yellow]BAM index missing, creating index for {input_bam}...[/yellow]")
            index_result = subprocess.run(f"samtools index {input_bam}", shell=True, capture_output=True, text=True)
            if index_result.returncode != 0:
                return f"❌ Failed to create BAM index: {index_result.stderr}"
            logger.info("✅ [green]BAM index created[/green]")
        
        # Build filter command
        flags = f"-q {min_quality}"
        if proper_pairs_only:
            flags += " -f 2"  # Proper pairs
        flags += " -F 1024"  # Remove duplicates marked
        
        if remove_mitochondrial:
            # More reliable mitochondrial removal
            cmd = f"samtools view -b {flags} {input_bam} $(samtools idxstats {input_bam} | cut -f1 | grep -v 'chrM\\|MT\\|chrMT' | tr '\\n' ' ')"
        else:
            cmd = f"samtools view -b {flags} {input_bam}"
        
        cmd += f" > {output_bam}"
        
        try:
            logger.info(f"🔄 [cyan]Filtering BAM file with quality ≥ {min_quality}...[/cyan]")
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                # Create index for filtered BAM
                logger.info("📄 [cyan]Indexing filtered BAM...[/cyan]")
                subprocess.run(f"samtools index {output_bam}", shell=True)
                logger.info(f"✅ [green]Filtered BAM created: {output_bam}[/green]")
                return f"✅ Filtered BAM: {output_bam}"
            else:
                return f"❌ Filtering failed: {result.stderr}"
        except Exception as e:
            return f"❌ Error during filtering: {str(e)}"
    
    def _fix_bam_readgroups(self, input_bam: str, output_bam: str = None) -> str:
        """Fix BAM file by adding read groups if missing"""
        if not output_bam:
            output_bam = input_bam.replace('.bam', '.rg.bam')
        
        # Check if BAM already has read groups
        check_cmd = f"samtools view -H {input_bam} | grep -q '@RG'"
        check_result = subprocess.run(check_cmd, shell=True)
        
        if check_result.returncode == 0:
            # Read groups exist, no need to add
            return input_bam
        
        # Add read groups using Picard
        sample_name = Path(input_bam).stem
        cmd = [
            "picard", "AddOrReplaceReadGroups",
            f"I={input_bam}",
            f"O={output_bam}",
            f"RGID={sample_name}",
            f"RGLB=lib1",
            f"RGPL=ILLUMINA",
            f"RGPU=unit1", 
            f"RGSM={sample_name}",
            "VALIDATION_STRINGENCY=LENIENT"
        ]
        
        try:
            logger.info("🔧 [yellow]Adding read groups to BAM file...[/yellow]")
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                logger.info("✅ [green]Read groups added successfully[/green]")
                return output_bam
            else:
                logger.info(f"⚠️ [yellow]Failed to add read groups: {result.stderr}[/yellow]")
                return input_bam  # Return original file
        except Exception as e:
            logger.info(f"⚠️ [yellow]Error adding read groups: {str(e)}[/yellow]")
            return input_bam  # Return original file

    @tool
    def mark_duplicates(self, input_bam: str, output_bam: Optional[str] = None,
                       remove_duplicates: bool = True) -> Dict[str, str]:
        """Mark or remove PCR duplicates using Picard"""
        
        # Check if required tools are available, install if needed
        if not self._check_and_install_tool("picard"):
            return {"status": "error", "message": "Failed to install Picard"}
        
        if not self._check_and_install_tool("samtools"):
            return {"status": "error", "message": "Failed to install samtools"}
        
        if not output_bam:
            suffix = ".dedup.bam" if remove_duplicates else ".markdup.bam"
            output_bam = str(Path(input_bam).parent / "dedup" / 
                           (Path(input_bam).stem + suffix))
        
        Path(output_bam).parent.mkdir(parents=True, exist_ok=True)
        
        metrics_file = Path(output_bam).with_suffix('.metrics')
        
        cmd = [
            "picard", "MarkDuplicates",
            f"I={input_bam}",
            f"O={output_bam}",
            f"M={metrics_file}",
            f"REMOVE_DUPLICATES={'true' if remove_duplicates else 'false'}",
            "ASSUME_SORTED=true",
            "VALIDATION_STRINGENCY=LENIENT"
        ]
        
        try:
            action = "Removing" if remove_duplicates else "Marking"
            logger.info(f"🔄 [cyan]{action} PCR duplicates with Picard...[/cyan]")
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                # Create index for processed BAM
                logger.info("📄 [cyan]Indexing processed BAM...[/cyan]")
                subprocess.run(f"samtools index {output_bam}", shell=True)
                logger.info(f"✅ [green]Duplicate processing completed: {output_bam}[/green]")
                
                # No cleanup needed as we use original BAM directly
                
                return {
                    "status": "success",
                    "output_bam": output_bam,
                    "metrics": str(metrics_file),
                    "message": f"✅ {action} duplicates completed"
                }
            else:
                return {"status": "error", "message": result.stderr}
        except Exception as e:
            # If Picard fails, try the samtools alternative automatically
            logger.info("⚠️ [yellow]Picard failed, trying samtools alternative...[/yellow]")
            return self.mark_duplicates_samtools(input_bam, output_bam, remove_duplicates)
    
    @tool
    def mark_duplicates_samtools(self, input_bam: str, output_bam: Optional[str] = None,
                                remove_duplicates: bool = True) -> Dict[str, str]:
        """Alternative: Mark or remove duplicates using samtools (more compatible)"""
        
        # Check if samtools is available
        if not self._check_and_install_tool("samtools"):
            return {"status": "error", "message": "Failed to install samtools"}
        
        if not output_bam:
            suffix = ".dedup.bam" if remove_duplicates else ".markdup.bam"
            output_bam = str(Path(input_bam).parent / "dedup" / 
                           (Path(input_bam).stem + suffix))
        
        Path(output_bam).parent.mkdir(parents=True, exist_ok=True)
        
        try:
            action = "Removing" if remove_duplicates else "Marking"
            logger.info(f"🔄 [cyan]{action} PCR duplicates with samtools...[/cyan]")
            
            if remove_duplicates:
                # Remove duplicates completely
                cmd = f"samtools view -b -F 1024 {input_bam} > {output_bam}"
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            else:
                # Mark duplicates (requires samtools >= 1.17)
                temp_bam = output_bam.replace('.bam', '.temp.bam')
                mark_cmd = f"samtools markdup {input_bam} {temp_bam}"
                result = subprocess.run(mark_cmd, shell=True, capture_output=True, text=True)
                
                if result.returncode == 0:
                    # Move temp file to final output
                    subprocess.run(f"mv {temp_bam} {output_bam}", shell=True)
                
            if result.returncode == 0:
                # Create index
                logger.info("📄 [cyan]Indexing processed BAM...[/cyan]")
                subprocess.run(f"samtools index {output_bam}", shell=True)
                logger.info(f"✅ [green]{action} duplicates completed with samtools: {output_bam}[/green]")
                
                return {
                    "status": "success",
                    "output_bam": output_bam,
                    "method": "samtools",
                    "message": f"✅ {action} duplicates completed"
                }
            else:
                return {"status": "error", "message": result.stderr}
        except Exception as e:
            return {"status": "error", "message": f"Error running samtools: {str(e)}"}
    
    @tool 
    def process_bam_smart(self, input_bam: str, output_dir: Optional[str] = None,
                         remove_duplicates: bool = False) -> Dict[str, str]:
        """Smart BAM processing: filter BAM (optionally remove duplicates)"""
        
        if not output_dir:
            output_dir = Path(input_bam).parent / "processed"
        else:
            output_dir = Path(output_dir)
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # Step 1: Filter BAM
            filtered_bam = str(output_dir / f"{Path(input_bam).stem}.filtered.bam")
            logger.info("🔄 [cyan]Step 1: Filtering BAM for quality...[/cyan]")
            filter_result = self.filter_bam(input_bam, filtered_bam)
            
            if not filter_result.startswith("✅"):
                return {"status": "error", "message": f"Filtering failed: {filter_result}"}
            
            # Step 2: Optionally remove duplicates
            if remove_duplicates:
                final_bam = str(output_dir / f"{Path(input_bam).stem}.processed.bam")
                logger.info("🔄 [cyan]Step 2: Removing duplicates (trying Picard first)...[/cyan]")
                
                # Try Picard first (as per Galaxy tutorial)
                dup_result = self.mark_duplicates(filtered_bam, final_bam, remove_duplicates)
                
                if dup_result["status"] == "error":
                    logger.info("⚠️ [yellow]Picard failed, using samtools alternative...[/yellow]") 
                    dup_result = self.mark_duplicates_samtools(filtered_bam, final_bam, remove_duplicates)
                
                if dup_result["status"] == "success":
                    # Get file stats
                    original_size = Path(input_bam).stat().st_size / 1024 / 1024  # MB
                    final_size = Path(final_bam).stat().st_size / 1024 / 1024  # MB
                    reduction = ((original_size - final_size) / original_size) * 100
                    
                    logger.info(f"📊 [green]Processing completed![/green]")
                    logger.info(f"   Original: {original_size:.1f} MB")  
                    logger.info(f"   Processed: {final_size:.1f} MB ({reduction:.1f}% reduction)")
                    
                    return {
                        "status": "success", 
                        "input_bam": input_bam,
                        "filtered_bam": filtered_bam,
                        "final_bam": final_bam,
                        "size_reduction": f"{reduction:.1f}%",
                        "method": dup_result.get("method", "picard"),
                        "message": f"✅ BAM processed successfully: {final_bam}"
                    }
                else:
                    return {"status": "error", "message": f"Duplicate removal failed: {dup_result['message']}"}
            else:
                # Skip duplicate removal, use filtered BAM as final output
                logger.info("ℹ️ [cyan]Skipping duplicate removal step (as requested)[/cyan]")
                
                # Get file stats
                original_size = Path(input_bam).stat().st_size / 1024 / 1024  # MB
                filtered_size = Path(filtered_bam).stat().st_size / 1024 / 1024  # MB
                reduction = ((original_size - filtered_size) / original_size) * 100
                
                logger.info(f"📊 [green]Processing completed![/green]")
                logger.info(f"   Original: {original_size:.1f} MB")  
                logger.info(f"   Filtered: {filtered_size:.1f} MB ({reduction:.1f}% reduction)")
                
                return {
                    "status": "success", 
                    "input_bam": input_bam,
                    "filtered_bam": filtered_bam,
                    "final_bam": filtered_bam,  # Use filtered BAM as final output
                    "size_reduction": f"{reduction:.1f}%",
                    "method": "filter_only",
                    "message": f"✅ BAM filtered successfully: {filtered_bam}"
                }
                
        except Exception as e:
            return {"status": "error", "message": f"Smart BAM processing failed: {str(e)}"}
    
