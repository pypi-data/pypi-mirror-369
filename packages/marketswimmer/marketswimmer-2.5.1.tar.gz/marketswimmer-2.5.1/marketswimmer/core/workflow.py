"""
Complete analysis workflow for MarketSwimmer.
Orchestrates the full end-to-end analysis process.
"""

import os
import time
from pathlib import Path
from typing import Optional, Tuple
from rich.console import Console
from rich.progress import Progress, TextColumn, BarColumn, TimeElapsedColumn

from .download_manager import DownloadManager
from .owner_earnings import OwnerEarningsCalculator
from .fair_value import FairValueCalculator

console = Console()

class AnalysisWorkflow:
    """Orchestrates the complete MarketSwimmer analysis workflow."""
    
    def __init__(self):
        self.download_manager = DownloadManager()
        self.data_folder = Path("data")
        self.charts_folder = Path("charts")
        
        # Ensure directories exist
        self.data_folder.mkdir(exist_ok=True)
        self.charts_folder.mkdir(exist_ok=True)
    
    def run_complete_analysis(self, ticker: str, force_download: bool = False) -> bool:
        """
        Run the complete analysis workflow for a ticker.
        
        Args:
            ticker: Stock ticker symbol
            force_download: Force new download even if data exists
            
        Returns:
            bool: True if analysis completed successfully
        """
        try:
            console.print(f"[bold blue]>> Starting complete analysis for {ticker.upper()}[/bold blue]")
            
            # Step 1: Handle data download
            data_file = self._handle_data_download(ticker, force_download)
            if not data_file:
                return False
            
            # Step 2: Calculate owner earnings
            if not self._calculate_owner_earnings(data_file, ticker):
                return False
            
            # Step 3: Calculate enhanced fair value
            if not self._calculate_enhanced_fair_value(ticker):
                return False
            
            # Step 4: Generate visualizations
            if not self._generate_visualizations(ticker):
                return False
            
            # Step 5: Generate shares analysis
            if not self._generate_shares_analysis(ticker):
                return False
            
            console.print(f"\n[bold green]>> Complete analysis finished for {ticker.upper()}![/bold green]")
            self._show_results_summary(ticker)
            return True
            
        except Exception as e:
            console.print(f"[red]ERROR: Analysis failed: {e}[/red]")
            return False
    
    def _handle_data_download(self, ticker: str, force_download: bool) -> Optional[Path]:
        """Handle the data download process."""
        with Progress(
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            
            # Check for existing data
            if not force_download:
                task = progress.add_task("Checking for existing data...", total=None)
                existing_file = self.download_manager.get_latest_data_file(ticker)
                if existing_file:
                    console.print(f"[green]>> Using existing data: {existing_file.name}[/green]")
                    return existing_file
            
            # Open download page
            task = progress.add_task("Opening StockRow download page...", total=None)
            self.download_manager.open_stockrow_download(ticker)
            
            # Wait for download
            progress.update(task, description="Waiting for download...")
            downloaded_file = self.download_manager.wait_for_download(ticker, timeout=300)  # 5 minutes
            
            if downloaded_file:
                progress.update(task, description="Copying file to project...")
                return self.download_manager.copy_to_project(downloaded_file, ticker)
            else:
                console.print("[red]ERROR: Download not detected. Please ensure you downloaded the XLSX file.[/red]")
                return None
    
    def _calculate_owner_earnings(self, data_file: Path, ticker: str) -> bool:
        """Calculate owner earnings from the data file."""
        try:
            with Progress(
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Calculating owner earnings...", total=None)
                
                # Create separate calculator instances for annual and quarterly data
                annual_calculator = OwnerEarningsCalculator()
                quarterly_calculator = OwnerEarningsCalculator()
                
                # Calculate annual data
                progress.update(task, description="Loading financial data...")
                annual_calculator.load_financial_data(str(data_file))
                
                progress.update(task, description="Calculating annual owner earnings...")
                annual_results = annual_calculator.calculate_annual_owner_earnings()
                
                # Calculate quarterly data with fresh calculator
                progress.update(task, description="Calculating quarterly owner earnings...")
                quarterly_calculator.load_financial_data(str(data_file))
                quarterly_results = quarterly_calculator.calculate_quarterly_owner_earnings()
                
                # Save results
                progress.update(task, description="Saving results...")
                clean_ticker = ticker.replace('.', '_').upper()
                
                annual_output = self.data_folder / f"owner_earnings_annual_{clean_ticker.lower()}.csv"
                quarterly_output = self.data_folder / f"owner_earnings_quarterly_{clean_ticker.lower()}.csv"
                
                # Debug information
                console.print(f"[dim]DEBUG: Saving to {annual_output}[/dim]")
                console.print(f"[dim]DEBUG: Annual results shape: {annual_results.shape}[/dim]")
                console.print(f"[dim]DEBUG: Quarterly results shape: {quarterly_results.shape}[/dim]")
                
                # Ensure directory exists
                self.data_folder.mkdir(parents=True, exist_ok=True)
                
                # Save with error handling
                try:
                    annual_results.to_csv(annual_output, index=False)
                    console.print(f"[dim]DEBUG: Annual CSV saved successfully[/dim]")
                except Exception as e:
                    console.print(f"[red]ERROR: Failed to save annual CSV: {e}[/red]")
                    
                try:
                    quarterly_results.to_csv(quarterly_output, index=False)
                    console.print(f"[dim]DEBUG: Quarterly CSV saved successfully[/dim]")
                except Exception as e:
                    console.print(f"[red]ERROR: Failed to save quarterly CSV: {e}[/red]")
                
                # Verify files were created
                if annual_output.exists():
                    console.print(f"[green]>> Annual file created: {annual_output.stat().st_size} bytes[/green]")
                else:
                    console.print(f"[red]ERROR: Annual file NOT created: {annual_output}[/red]")
                    
                if quarterly_output.exists():
                    console.print(f"[green]>> Quarterly file created: {quarterly_output.stat().st_size} bytes[/green]")
                else:
                    console.print(f"[red]ERROR: Quarterly file NOT created: {quarterly_output}[/red]")
                
                console.print(f"[green]>> Owner earnings calculated and saved[/green]")
                console.print(f"[dim]Annual: {annual_output}[/dim]")
                console.print(f"[dim]Quarterly: {quarterly_output}[/dim]")
                
                return True
                
        except Exception as e:
            console.print(f"[red]ERROR: Owner earnings calculation failed: {e}[/red]")
            return False
    
    def _calculate_enhanced_fair_value(self, ticker: str) -> bool:
        """Calculate enhanced fair value analysis."""
        try:
            with Progress(
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Calculating enhanced fair value...", total=None)
                
                # Create fair value calculator
                fair_value_calc = FairValueCalculator()
                
                progress.update(task, description="Running enhanced fair value analysis...")
                
                # Run the enhanced analysis which includes:
                # - Balance sheet data extraction with preferred stock detection
                # - Fair value calculation with proper adjustments
                # - Scenario analysis
                # - Enhanced reporting
                results = fair_value_calc.enhanced_fair_value_analysis(ticker, save_detailed_report=True)
                
                console.print(f"[green]>> Enhanced fair value analysis completed[/green]")
                console.print(f"[dim]Results include balance sheet analysis and scenario modeling[/dim]")
                
                return True
                
        except Exception as e:
            console.print(f"[red]ERROR: Fair value calculation failed: {e}[/red]")
            console.print(f"[yellow]TIP: Ensure owner earnings data exists first[/yellow]")
            return False
    
    def _generate_shares_analysis(self, ticker: str) -> bool:
        """Generate shares outstanding and debt analysis."""
        try:
            with Progress(
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Generating shares analysis...", total=None)
                
                # Import shares analysis module with graceful fallback
                try:
                    from ..visualization.charts import create_shares_outstanding_analysis
                    
                    # Generate shares and debt analysis charts
                    progress.update(task, description="Creating shares and debt analysis...")
                    success = create_shares_outstanding_analysis(ticker)
                    
                    if success:
                        console.print(f"[green]>> Shares analysis generated[/green]")
                        console.print(f"[dim]Check analysis_output/ for shares and debt charts[/dim]")
                    else:
                        console.print(f"[yellow]WARNING: Shares analysis could not be generated[/yellow]")
                    
                    return True  # Don't fail the workflow even if shares analysis fails
                    
                except ImportError:
                    console.print(f"[yellow]WARNING: Shares analysis dependencies not available[/yellow]")
                    return True  # Don't fail the entire workflow
                    
        except Exception as e:
            console.print(f"[red]ERROR: Shares analysis generation failed: {e}[/red]")
            return True  # Don't fail the workflow
    
    def _generate_visualizations(self, ticker: str) -> bool:
        """Generate charts and visualizations."""
        try:
            with Progress(
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Generating visualizations...", total=None)
                
                # Import visualization module with graceful fallback
                try:
                    from ..visualization.charts import main as visualization_main
                    
                    # Generate charts using the working charts module
                    progress.update(task, description="Creating owner earnings charts...")
                    visualization_main(ticker)
                    
                    console.print(f"[green]>> Visualizations generated[/green]")
                    return True
                    
                except ImportError:
                    console.print(f"[yellow]WARNING: Visualization dependencies not available[/yellow]")
                    console.print(f"[yellow]Install with: pip install matplotlib PyQt6[/yellow]")
                    return True  # Don't fail the entire workflow
                    
        except Exception as e:
            console.print(f"[red]ERROR: Visualization generation failed: {e}[/red]")
            return False
    
    def _show_results_summary(self, ticker: str):
        """Show a summary of analysis results."""
        console.print(f"\n[bold]>> Analysis Results for {ticker.upper()}:[/bold]")
        console.print("=" * 50)
        
        # Check what files were created
        clean_ticker = ticker.replace('.', '_').lower()
        
        files_to_check = [
            (self.data_folder / f"owner_earnings_annual_{clean_ticker}.csv", ">> Annual Owner Earnings"),
            (self.data_folder / f"owner_earnings_quarterly_{clean_ticker}.csv", ">> Quarterly Owner Earnings"),
            (self.charts_folder / f"{clean_ticker}_owner_earnings_comparison.png", ">> Comparison Chart"),
            (self.charts_folder / f"{clean_ticker}_earnings_components_breakdown.png", ">> Components Chart"),
            (Path("analysis_output") / f"{ticker.upper()}_shares_analysis.png", ">> Shares Analysis Chart"),
            (Path("analysis_output") / f"{ticker.upper()}_debt_analysis.png", ">> Debt Analysis Chart"),
        ]
        
        for file_path, description in files_to_check:
            if file_path.exists():
                console.print(f">> {description}: [dim]{file_path}[/dim]")
            else:
                console.print(f">> {description}: [dim]Not generated[/dim]")
        
        # Check for fair value reports (they have timestamps, so look for pattern)
        import glob
        fair_value_reports = glob.glob(f"{ticker.upper()}_enhanced_fair_value_*.txt")
        if fair_value_reports:
            latest_report = max(fair_value_reports)  # Get most recent
            console.print(f">> Enhanced Fair Value Report: [dim]{latest_report}[/dim]")
        else:
            console.print(f">> Enhanced Fair Value Report: [dim]Not generated[/dim]")
        
        console.print("\n[green]>> Next steps:[/green]")
        console.print("• Review the CSV files for detailed calculations")
        console.print("• Check the enhanced fair value report for valuation analysis")
        console.print("• Check the charts folder for visualizations")
        console.print("• Check the analysis_output folder for shares and debt analysis")
        console.print(f"• Run [bold]ms visualize --ticker {ticker}[/bold] for additional charts")
