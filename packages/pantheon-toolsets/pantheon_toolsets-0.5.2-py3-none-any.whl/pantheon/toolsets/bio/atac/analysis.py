"""ATAC-seq Downstream Analysis - Peak calling, visualization, and reporting"""

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

class ATACSeqAnalysisToolSet(ToolSet):
    """ATAC-seq Downstream Analysis Toolset - Peak calling to final reports"""
    
    def __init__(
        self,
        name: str = "atac_analysis",
        workspace_path: str | Path | None = None,
        worker_params: dict | None = None,
        **kwargs,
    ):
        super().__init__(name, worker_params, **kwargs)
        self.workspace_path = Path(workspace_path) if workspace_path else Path.cwd()
        self.console = Console()

        
    def _initialize_config(self) -> Dict[str, Any]:
        """Initialize ATAC-seq pipeline configuration for downstream analysis"""
        return {
            "file_extensions": {
                "alignment": [".sam", ".bam", ".cram", ".bam.bai", ".cram.crai"],
                "peaks": [".narrowPeak", ".broadPeak", ".gappedPeak", ".xls", ".bedgraph", ".bdg"],
                "tracks": [".bw", ".bigwig", ".tdf"],
                "reports": [".html", ".json", ".txt", ".tsv", ".csv", ".pdf", ".png"]
            },
            "tools": {
                "peak_calling": ["macs2", "genrich", "hmmratac"],
                "coverage": ["deeptools", "bedtools", "ucsc-tools"],
                "annotation": ["homer", "meme", "chipseeker", "bedtools"],
                "qc": ["multiqc"]
            },
            "default_params": {
                "threads": 4,
                "memory": "8G",
                "peak_calling_fdr": 0.01
            }
        }

    # Downstream analysis functions extracted from core.py
    
    @tool
    def call_peaks_macs2(self, treatment_bam: str, 
                        control_bam: Optional[str] = None,
                        output_dir: Optional[str] = None,
                        genome_size: str = "hs",
                        fdr: float = 0.01,
                        paired_end: bool = True) -> Dict[str, str]:
        """Call peaks using MACS2"""
        
        # Check if macs2 is available, install if needed
        if not self._check_and_install_tool("macs2"):
            return {"status": "error", "message": "Failed to install MACS2"}
        
        if not output_dir:
            output_dir = self.workspace_path / "peaks" / "macs2"
        else:
            output_dir = Path(output_dir)
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        sample_name = Path(treatment_bam).stem
        
        cmd = [
            "macs2", "callpeak",
            "-t", treatment_bam,
            "-n", sample_name,
            "--outdir", str(output_dir),
            "-g", genome_size,
            "-q", str(fdr),
            "--nomodel",
            "--shift", "-100",
            "--extsize", "200",
            "-B",  # Generate bedGraph
            "--SPMR"  # Normalize signal
        ]
        
        if control_bam:
            cmd.extend(["-c", control_bam])
        
        if paired_end:
            cmd.extend(["-f", "BAMPE"])
        else:
            cmd.extend(["-f", "BAM"])
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                return {
                    "status": "success",
                    "peaks": str(output_dir / f"{sample_name}_peaks.narrowPeak"),
                    "summits": str(output_dir / f"{sample_name}_summits.bed"),
                    "treat_pileup": str(output_dir / f"{sample_name}_treat_pileup.bdg")
                }
            else:
                return {"status": "error", "message": result.stderr}
        except FileNotFoundError:
            return {"status": "error", "message": "MACS2 not found"}
    
    @tool
    def call_peaks_genrich(self, bam_files: List[str], 
                          output_prefix: str,
                          control_bams: Optional[List[str]] = None,
                          fdr: float = 0.01) -> Dict[str, str]:
        """Call peaks using Genrich (ATAC-seq optimized)"""
        output_peaks = f"{output_prefix}.narrowPeak"
        
        cmd = [
            "Genrich",
            "-t", ",".join(bam_files),
            "-o", output_peaks,
            "-q", str(fdr),
            "-j",  # ATAC-seq mode
            "-y",  # Remove PCR duplicates
            "-r",  # Remove mitochondrial reads
            "-e", "chrM",
            "-v"  # Verbose
        ]
        
        if control_bams:
            cmd.extend(["-c", ",".join(control_bams)])
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                return {
                    "status": "success",
                    "peaks": output_peaks,
                    "log": result.stderr
                }
            else:
                return {"status": "error", "message": result.stderr}
        except FileNotFoundError:
            return {"status": "error", "message": "Genrich not found"}
    
    @tool
    def bam_to_bigwig(self, input_bam: str, 
                     output_bigwig: Optional[str] = None,
                     normalize: str = "RPKM",
                     bin_size: int = 10) -> str:
        """Convert BAM to BigWig using deepTools"""
        
        # Check if deeptools is available, install if needed
        if not self._check_and_install_tool("deeptools"):
            return "❌ Failed to install deepTools"
        
        if not output_bigwig:
            output_bigwig = str(Path(input_bam).with_suffix('.bw'))
        
        # Create output directory if it doesn't exist
        output_path = Path(output_bigwig)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"🔄 [cyan]Generating BigWig coverage track: {output_bigwig}[/cyan]")
        
        cmd = [
            "bamCoverage",
            "-b", input_bam,
            "-o", output_bigwig,
            "--normalizeUsing", normalize,
            "--binSize", str(bin_size),
            "-p", str(self.pipeline_config["default_params"]["threads"])
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                logger.info(f"✅ [green]BigWig created: {output_bigwig}[/green]")
                return f"✅ BigWig created: {output_bigwig}"
            else:
                logger.info(f"❌ [red]BigWig creation failed: {result.stderr}[/red]")
                return f"❌ BigWig creation failed: {result.stderr}"
        except FileNotFoundError:
            return "❌ deepTools not found. Install with: pip install deeptools"
    
    @tool
    def compute_matrix(self, bigwig_files: List[str], 
                      bed_file: str,
                      output_matrix: str,
                      mode: str = "reference-point",
                      upstream: int = 3000,
                      downstream: int = 3000) -> str:
        """Compute matrix for deepTools plots"""
        cmd = [
            "computeMatrix", mode,
            "-S"] + bigwig_files + [
            "-R", bed_file,
            "-o", output_matrix,
            "-a", str(downstream),
            "-b", str(upstream),
            "-p", str(self.pipeline_config["default_params"]["threads"])
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                return f"✅ Matrix computed: {output_matrix}"
            else:
                return f"❌ Matrix computation failed: {result.stderr}"
        except FileNotFoundError:
            return "❌ deepTools not found"
    
    @tool
    def plot_heatmap(self, matrix_file: str, output_plot: str,
                    colormap: str = "RdBu_r") -> str:
        """Plot heatmap from matrix using deepTools"""
        cmd = [
            "plotHeatmap",
            "-m", matrix_file,
            "-o", output_plot,
            "--colorMap", colormap,
            "--whatToShow", "heatmap and colorbar"
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                return f"✅ Heatmap created: {output_plot}"
            else:
                return f"❌ Heatmap plotting failed: {result.stderr}"
        except FileNotFoundError:
            return "❌ deepTools not found"
    
    @tool
    def find_motifs(self, peak_file: str, genome: str,
                   output_dir: Optional[str] = None,
                   size: int = 200) -> str:
        """Find enriched motifs using HOMER"""
        if not output_dir:
            output_dir = self.workspace_path / "motifs" / Path(peak_file).stem
        else:
            output_dir = Path(output_dir)
        
        cmd = [
            "findMotifsGenome.pl",
            peak_file,
            genome,
            str(output_dir),
            "-size", str(size),
            "-mask"
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                return f"✅ Motif analysis completed: {output_dir}"
            else:
                return f"❌ Motif finding failed: {result.stderr}"
        except FileNotFoundError:
            return "❌ HOMER not found"
    
    @tool
    def generate_atac_qc_report(self, bam_file: str, 
                               peak_file: str,
                               output_dir: Optional[str] = None,
                               include_multiqc: bool = True,
                               qc_data_dirs: Optional[List[str]] = None) -> Dict[str, Any]:
        """Generate comprehensive ATAC-seq QC report with MultiQC integration"""
        
        # Rich console header
        logger.info("\n" + "="*70)
        logger.info("  [bold cyan]Generating ATAC-seq QC Report[/bold cyan]", justify="center")
        logger.info("="*70)
        
        if not output_dir:
            output_dir = self.workspace_path / "reports"
        else:
            output_dir = Path(output_dir)
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        qc_metrics = {
            "sample": Path(bam_file).stem,
            "metrics": {}
        }
        
        logger.info(f"📁 [yellow]Output directory:[/yellow] {output_dir}")
        logger.info(f"📄 [yellow]BAM file:[/yellow] {bam_file}")
        logger.info(f"🏔️ [yellow]Peak file:[/yellow] {peak_file}\n")
        
        # Progress tracking
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=self.console
        ) as progress:
            task_metrics = progress.add_task("Collecting QC metrics...", total=4)
            
            # Get alignment stats
            try:
                progress.update(task_metrics, description="📊 Analyzing alignment statistics...")
                result = subprocess.run(
                    f"samtools flagstat {bam_file}",
                    shell=True, capture_output=True, text=True
                )
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')
                    qc_metrics["metrics"]["total_reads"] = int(lines[0].split()[0])
                    qc_metrics["metrics"]["mapped_reads"] = int(lines[4].split()[0])
                    qc_metrics["metrics"]["properly_paired"] = int(lines[8].split()[0])
                    
                    # Calculate mapping rate
                    mapping_rate = (qc_metrics["metrics"]["mapped_reads"] / qc_metrics["metrics"]["total_reads"]) * 100
                    qc_metrics["metrics"]["mapping_rate"] = f"{mapping_rate:.2f}%"
                    
                progress.advance(task_metrics)
            except Exception as e:
                logger.info(f"⚠️ [yellow]Warning: Could not get alignment stats: {e}[/yellow]")
                progress.advance(task_metrics)
            
            # Count peaks
            try:
                progress.update(task_metrics, description="🏔️ Counting peaks...")
                with open(peak_file) as f:
                    peak_count = sum(1 for line in f if not line.startswith('#'))
                qc_metrics["metrics"]["peak_count"] = peak_count
                progress.advance(task_metrics)
            except Exception as e:
                logger.info(f"⚠️ [yellow]Warning: Could not count peaks: {e}[/yellow]")
                progress.advance(task_metrics)
            
            # Calculate FRiP (Fraction of Reads in Peaks)
            try:
                progress.update(task_metrics, description="🎯 Calculating FRiP score...")
                cmd = f"bedtools intersect -a {bam_file} -b {peak_file} -c | " \
                      f"awk '{{sum+=$NF}} END {{print sum}}'"
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                if result.returncode == 0:
                    reads_in_peaks = int(result.stdout.strip())
                    total_reads = qc_metrics["metrics"]["total_reads"]
                    frip = reads_in_peaks / total_reads if total_reads > 0 else 0
                    qc_metrics["metrics"]["FRiP"] = f"{frip:.3f}"
                    qc_metrics["metrics"]["reads_in_peaks"] = reads_in_peaks
                progress.advance(task_metrics)
            except Exception as e:
                logger.info(f"⚠️ [yellow]Warning: Could not calculate FRiP: {e}[/yellow]")
                progress.advance(task_metrics)
            
            # Generate MultiQC report if requested
            if include_multiqc:
                progress.update(task_metrics, description="📈 Generating MultiQC report...")
                try:
                    self._generate_multiqc_report(output_dir, qc_data_dirs)
                    qc_metrics["multiqc_report"] = str(output_dir / "multiqc_report.html")
                except Exception as e:
                    logger.info(f"⚠️ [yellow]Warning: MultiQC generation failed: {e}[/yellow]")
                progress.advance(task_metrics)
        
        # Display results table
        results_table = Table(title="ATAC-seq QC Summary", show_header=True, header_style="bold magenta")
        results_table.add_column("Metric", style="cyan")
        results_table.add_column("Value", justify="right", style="green")
        
        # Add metrics to table
        for metric, value in qc_metrics["metrics"].items():
            metric_display = metric.replace("_", " ").title()
            results_table.add_row(metric_display, str(value))
        
        logger.info("\n")
        logger.info("", rich=results_table)
        
        # Save JSON report
        report_file = output_dir / f"{Path(bam_file).stem}_qc.json"
        with open(report_file, 'w') as f:
            json.dump(qc_metrics, f, indent=2)
        
        # Final status
        success_panel = Panel(
            f" [green]QC report generated successfully![/green]\n" +
            f" JSON report: {report_file}\n" + 
            (f" MultiQC report: {output_dir}/multiqc_report.html\n" if include_multiqc else "") +
            f" Total peaks: {qc_metrics['metrics'].get('peak_count', 'N/A')}\n" +
            f" FRiP score: {qc_metrics['metrics'].get('FRiP', 'N/A')}",
            title="QC Report Complete",
            border_style="green"
        )
        logger.info("", rich=success_panel)
        logger.info("="*70 + "\n")
        
        return qc_metrics
    
    def _generate_multiqc_report(self, output_dir: Path, qc_data_dirs: Optional[List[str]] = None):
        """Generate MultiQC report from available QC data"""
        
        # Default QC directories to search
        if qc_data_dirs is None:
            qc_data_dirs = [
                str(self.workspace_path / "qc"),
                str(self.workspace_path / "qc/fastqc"),
                str(self.workspace_path / "alignment"),
                str(self.workspace_path / "peaks"),
                str(output_dir)
            ]
        
        # Add existing directories to search path
        search_dirs = []
        for qc_dir in qc_data_dirs:
            qc_path = Path(qc_dir)
            if qc_path.exists():
                search_dirs.append(str(qc_path))
        
        if not search_dirs:
            logger.info("⚠️ [yellow]No QC directories found for MultiQC[/yellow]")
            return
        
        # Check if MultiQC is available
        try:
            subprocess.run(["multiqc", "--version"], 
                         capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.info("⚠️ [yellow]MultiQC not found. Installing...[/yellow]")
            try:
                subprocess.run(["conda", "install", "-c", "bioconda", "multiqc", "-y"], 
                             capture_output=True, check=True)
                logger.info("✅ [green]MultiQC installed successfully[/green]")
            except subprocess.CalledProcessError:
                raise Exception("Failed to install MultiQC. Please install manually: conda install -c bioconda multiqc")
        
        # Run MultiQC
        multiqc_cmd = [
            "multiqc",
            "--outdir", str(output_dir),
            "--filename", "multiqc_report.html",
            "--title", "ATAC-seq Analysis Report",
            "--force"
        ] + search_dirs
        
        result = subprocess.run(multiqc_cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            raise Exception(f"MultiQC failed: {result.stderr}")
        
        logger.info("✅ [green]MultiQC report generated successfully[/green]")
    
    @tool
    def run_full_pipeline(self, sample_sheet: str, 
                         genome_index: str,
                         genome_size: str = "hs") -> str:
        """Run complete ATAC-seq pipeline from FASTQ to peaks"""
        # This would orchestrate the entire pipeline
        # Reading sample sheet, running each step, etc.
        return "Full pipeline execution - implement based on sample sheet"
    
    @tool
    def suggest_next_step(self, completed_steps: List[str]) -> str:
        """Suggest next step in ATAC-seq analysis based on completed steps"""
        pipeline_order = [
            "fastqc", "trim_adapters", "align", "filter_bam", 
            "mark_duplicates", "call_peaks", "bigwig", "motifs", "qc_report"
        ]
        
        for step in pipeline_order:
            if step not in completed_steps:
                suggestions = {
                    "fastqc": "Run FastQC on raw FASTQ files: run_fastqc()",
                    "trim_adapters": "Trim adapters: trim_adapters()",
                    "align": "Align reads to genome: align_bwa()",
                    "filter_bam": "Filter BAM for quality: filter_bam()",
                    "mark_duplicates": "Remove PCR duplicates: mark_duplicates()",
                    "call_peaks": "Call peaks with MACS2 or Genrich: call_peaks_macs2()",
                    "bigwig": "Generate BigWig tracks: bam_to_bigwig()",
                    "motifs": "Find enriched motifs: find_motifs()",
                    "qc_report": "Generate QC report: generate_atac_qc_report()"
                }
                return suggestions.get(step, "Continue with downstream analysis")
        
