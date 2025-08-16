"""
MarketSwimmer CLI - A modern command-line interface for financial analysis
Built with Typer for an excellent user experience
"""

import typer
from typing import Optional
from pathlib import Path
import os
import subprocess
import sys
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.progress import Progress, TextColumn
import time

# Initialize Rich console for beautiful output
console = Console()

# Create the main Typer app
app = typer.Typer(
    name="marketswimmer",
    help="MarketSwimmer - Warren Buffett's Owner Earnings Analysis Tool",
    epilog="For more help on a specific command, use: marketswimmer COMMAND --help",
    rich_markup_mode="rich"
)

def check_python_executable():
    """Find the best Python executable to use."""
    python_paths = [
        r"C:\Users\jerem\AppData\Local\Programs\Python\Python312\python.exe",
        "python",
        "python3",
        "py"
    ]
    
    for python_path in python_paths:
        try:
            result = subprocess.run([python_path, "--version"], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                return python_path
        except (subprocess.TimeoutExpired, FileNotFoundError):
            continue
    
    return "python"  # fallback

def run_python_script(script_name: str, args: list = None):
    """Run a Python script with the best available Python executable."""
    python_exe = check_python_executable()
    cmd = [python_exe, script_name]
    if args:
        cmd.extend(args)
    
    try:
        result = subprocess.run(cmd, cwd=Path.cwd())
        return result.returncode == 0
    except Exception as e:
        console.print(f"[red]Error running {script_name}: {e}[/red]")
        return False

@app.command()
def gui(
    safe_mode: bool = typer.Option(False, "--safe", "-s", help="Check for existing processes before launching"),
    test_mode: bool = typer.Option(False, "--test", "-t", help="Launch in test mode (no logging)")
):
    """
    Launch the MarketSwimmer GUI application
    
    The GUI provides an intuitive interface for:
    - Downloading financial data
    - Calculating owner earnings
    - Generating beautiful charts
    """
    with console.status("[bold green]Launching MarketSwimmer GUI...", spinner="dots"):
        time.sleep(1)  # Brief delay for visual feedback
    
    if safe_mode:
        console.print("[yellow]CHECKING: Looking for existing GUI processes...[/yellow]")
        # Check for existing processes (simplified)
        try:
            result = subprocess.run(['tasklist', '/FI', 'WINDOWTITLE eq MarketSwimmer*'], 
                                  capture_output=True, text=True)
            if 'python.exe' in result.stdout:
                console.print("[red]WARNING: MarketSwimmer GUI is already running![/red]")
                console.print("Please close existing windows before starting a new one.")
                raise typer.Exit(1)
        except:
            pass  # Continue if check fails
    
    console.print("[green]>> Starting MarketSwimmer GUI...[/green]")
    
    try:
        # Import and run the GUI module
        from .gui.main_window import main as gui_main
        gui_main()
    except ImportError as e:
        console.print(f"[red]ERROR: Failed to import GUI module: {e}[/red]")
        console.print("[yellow]NOTE: Make sure PyQt6 is installed: pip install PyQt6[/yellow]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]ERROR: Failed to launch GUI: {e}[/red]")
        raise typer.Exit(1)
    
    console.print("[green]>> GUI closed successfully.[/green]")

@app.command()
def analyze(
    ticker: str = typer.Argument(..., help="Stock ticker symbol (e.g., BRK.B, AAPL, TSLA)"),
    charts_only: bool = typer.Option(False, "--charts-only", "-c", help="Only generate charts from existing data"),
    force: bool = typer.Option(False, "--force", "-f", help="Force re-download even if data exists")
):
    """
    Analyze a stock ticker using Warren Buffett's Owner Earnings method
    
    This command will:
    1. Download the latest financial data
    2. Calculate owner earnings (annual & quarterly)
    3. Generate comprehensive charts and analysis
    4. Save results to organized directories
    
    Examples:
    - marketswimmer analyze BRK.B
    - marketswimmer analyze AAPL --charts-only
    - marketswimmer analyze TSLA --force
    """
    ticker = ticker.upper()
    
    # Handle special cases
    if ticker == "BRKB":
        ticker = "BRK.B"
    
    console.print(f"[bold blue]>> Analyzing {ticker}...[/bold blue]")
    
    if charts_only:
        console.print("[yellow]>> Generating charts from existing data...[/yellow]")
        from .core.analysis import visualize_existing_data
        success = visualize_existing_data()
    else:
        console.print(f"[cyan]>> Running complete analysis for {ticker}...[/cyan]")
        from .core.analysis import analyze_ticker_workflow
        success = analyze_ticker_workflow(ticker, force)
    
    if success is True:
        console.print("\n[green]>> Analysis complete![/green]")
        console.print("Check these directories for results:")
        console.print("  >> [bold]data/[/bold] - CSV files with financial analysis")
        console.print("  >> [bold]charts/[/bold] - PNG charts and visualizations")
        console.print("  >> [bold]downloaded_files/[/bold] - Raw Excel data")
    elif success == "guidance_provided":
        console.print("\n[blue]>> Guidance provided above. Follow the steps to complete your analysis.[/blue]")
    else:
        console.print("[red]ERROR: Analysis failed. Check the output above for details.[/red]")
        raise typer.Exit(1)

@app.command()
def status():
    """
    Show MarketSwimmer project status and health check
    """
    console.print("[bold blue]MarketSwimmer Project Status[/bold blue]\n")
    
    # Check directories
    directories = ["data", "charts", "downloaded_files", "logs", "scripts"]
    dir_table = Table(title=">> Directory Structure")
    dir_table.add_column("Directory", style="cyan")
    dir_table.add_column("Status", style="green")
    dir_table.add_column("Files", justify="right")
    
    for directory in directories:
        if Path(directory).exists():
            file_count = len(list(Path(directory).glob("*")))
            dir_table.add_row(directory, ">> Exists", str(file_count))
        else:
            dir_table.add_row(directory, ">> Missing", "0")
    
    console.print(dir_table)
    console.print()
    
    # Check Python installation
    python_exe = check_python_executable()
    console.print(f">> Python executable: [cyan]{python_exe}[/cyan]")
    
    try:
        result = subprocess.run([python_exe, "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            console.print(f">> Python version: [green]{result.stdout.strip()}[/green]")
        else:
            console.print("[red]ERROR: Python check failed[/red]")
    except:
        console.print("[red]ERROR: Python not accessible[/red]")
    
    # Check for package modules
    console.print("\n>> Package Modules:")
    modules_to_check = [
        ("marketswimmer.core.owner_earnings", "OwnerEarningsCalculator"),
        ("marketswimmer.core.analysis", "analyze_ticker_workflow"),
        ("marketswimmer.visualization", "OwnerEarningsVisualizer"),
        ("marketswimmer.gui.main_window", "MarketSwimmerGUI"),
    ]
    
    for module_name, class_name in modules_to_check:
        try:
            __import__(module_name)
            console.print(f"  >> {module_name}")
        except ImportError as e:
            console.print(f"  ERROR: {module_name} [red](import error: {e})[/red]")

@app.command()
def quick_start():
    """
    >> Quick start guide for new users
    """
    console.print(Panel.fit(
        "[bold blue]>> Welcome to MarketSwimmer![/bold blue]\n\n"
        "MarketSwimmer analyzes stocks using Warren Buffett's 'Owner Earnings' method.\n"
        "This approach focuses on the actual cash a business generates for its owners.",
        title="Welcome",
        border_style="blue"
    ))
    
    console.print("\n[bold green]>> Quick Start Steps:[/bold green]")
    
    steps = [
        ("1.", "Launch GUI", "marketswimmer gui", "Start with the user-friendly interface"),
        ("2.", "Analyze a Stock", "marketswimmer analyze AAPL", "Analyze Apple's owner earnings"),
        ("3.", "View Results", "Check data/ and charts/ folders", "See your analysis results"),
        ("4.", "Try More", "marketswimmer analyze BRK.B", "Analyze Berkshire Hathaway")
    ]
    
    for step, title, command, description in steps:
        console.print(f"\n{step} [bold]{title}[/bold]")
        console.print(f"   Command: [cyan]{command}[/cyan]")
        console.print(f"   {description}")
    
    console.print("\n[bold yellow]>> Pro Tips:[/bold yellow]")
    console.print("• Use [cyan]--help[/cyan] with any command for detailed options")
    console.print("• Check [cyan]marketswimmer status[/cyan] if you encounter issues")
    console.print("• The GUI is perfect for beginners, CLI for power users")
    console.print("• All data is saved locally - no cloud dependencies")

@app.command()
def examples():
    """
    >> Show practical examples and use cases
    """
    console.print("[bold blue]>> MarketSwimmer Examples & Use Cases[/bold blue]\n")
    
    # Create examples table
    examples_table = Table(title=">> Common Commands")
    examples_table.add_column("Use Case", style="cyan", width=25)
    examples_table.add_column("Command", style="green", width=35)
    examples_table.add_column("Description", width=30)
    
    examples = [
        ("First-time user", "marketswimmer quick-start", "Get oriented with the tool"),
        ("Launch GUI", "marketswimmer gui", "Use the visual interface"),
        ("Safe GUI launch", "marketswimmer gui --safe", "Check for existing processes"),
        ("Test mode GUI", "marketswimmer gui --test", "Launch without logging"),
        ("Analyze Berkshire", "marketswimmer analyze BRK.B", "Warren Buffett's company"),
        ("Analyze Apple", "marketswimmer analyze AAPL", "Tech giant analysis"),
        ("Analyze Tesla", "marketswimmer analyze TSLA", "EV company analysis"),
        ("Charts only", "marketswimmer analyze AAPL -c", "Skip download, make charts"),
        ("Force refresh", "marketswimmer analyze AAPL -f", "Re-download all data"),
        ("Check health", "marketswimmer status", "Verify installation"),
        ("Get help", "marketswimmer --help", "Show all commands"),
    ]
    
    for use_case, command, description in examples:
        examples_table.add_row(use_case, command, description)
    
    console.print(examples_table)
    
    console.print("\n[bold green]>> Recommended Workflow:[/bold green]")
    workflow = [
        "Start with the GUI to get familiar: [cyan]marketswimmer gui[/cyan]",
        "Try analyzing a well-known stock: [cyan]marketswimmer analyze BRK.B[/cyan]", 
        "Check the generated files in [bold]data/[/bold] and [bold]charts/[/bold]",
        "Use the CLI for batch processing multiple stocks",
        "Run [cyan]marketswimmer status[/cyan] if you encounter any issues"
    ]
    
    for i, step in enumerate(workflow, 1):
        console.print(f"{i}. {step}")

@app.command()
def version():
    """
    >> Show version and system information
    """
    console.print("[bold blue]>> MarketSwimmer Version Information[/bold blue]\n")
    
    console.print("Version: [green]2.4.1[/green] (CLI Edition)")
    console.print("Built with: [cyan]Typer + Rich[/cyan]")
    console.print("Purpose: [yellow]Warren Buffett's Owner Earnings Analysis[/yellow]")
    console.print(f"Working Directory: [blue]{Path.cwd()}[/blue]")
    
    # System info
    console.print(f"\nSystem: [cyan]{sys.platform}[/cyan]")
    console.print(f"Python: [cyan]{sys.version.split()[0]}[/cyan]")
    
    # Check for key dependencies
    try:
        import pandas
        console.print(f"Pandas: [green]{pandas.__version__}[/green]")
    except ImportError:
        console.print("Pandas: [red]Not installed[/red]")
    
    try:
        import matplotlib
        console.print(f"Matplotlib: [green]{matplotlib.__version__}[/green]")
    except ImportError:
        console.print("Matplotlib: [red]Not installed[/red]")

@app.command()
def fair_value(
    ticker: str = typer.Argument(..., help="Stock ticker symbol (e.g., BRK.B, LNC, AAPL)"),
    report: bool = typer.Option(True, "--report/--no-report", help="Save detailed report file")
):
    """
    Calculate enhanced fair value with balance sheet analysis
    
    This command performs comprehensive fair value analysis including:
    - Automatic preferred stock detection
    - Balance sheet adjustments (cash, debt, preferred shares)
    - Insurance company methodology 
    - Scenario analysis with multiple discount rates
    - Detailed valuation report
    
    Examples:
        marketswimmer fair-value LNC    # Analyze Lincoln National
        marketswimmer fair-value BRK.B --no-report  # Skip saving report
    """
    try:
        console.print(f"[bold blue]>> Enhanced Fair Value Analysis for {ticker.upper()}[/bold blue]")
        
        # Import the fair value calculator
        from .core.fair_value import FairValueCalculator
        
        # Run enhanced analysis
        calculator = FairValueCalculator()
        results = calculator.enhanced_fair_value_analysis(ticker, save_detailed_report=report)
        
        console.print("\n[bold green]>> Fair value analysis completed successfully![/bold green]")
        
        if report:
            console.print("[dim]>> Detailed report saved to current directory[/dim]")
        
    except ImportError as e:
        console.print(f"[red]ERROR: Could not import fair value calculator: {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]ERROR: Fair value calculation failed: {e}[/red]")
        console.print("[yellow]TIP: Make sure owner earnings data exists first (run 'analyze' command)[/yellow]")
        raise typer.Exit(1)

@app.command(name="enhanced-fair-value")
def enhanced_fair_value(
    ticker: str = typer.Argument(..., help="Stock ticker symbol (e.g., BRK.B, LNC, AAPL)"),
    report: bool = typer.Option(True, "--report/--no-report", help="Save detailed report file")
):
    """
    Calculate enhanced fair value with balance sheet analysis
    
    This command performs comprehensive fair value analysis including:
    - Automatic preferred stock detection
    - Balance sheet adjustments (cash, debt, preferred shares)
    - Insurance company methodology 
    - Scenario analysis with multiple discount rates
    - Detailed valuation report
    
    Examples:
        marketswimmer enhanced-fair-value LNC    # Analyze Lincoln National
        marketswimmer enhanced-fair-value BRK.B --no-report  # Skip saving report
    """
    try:
        console.print(f"[bold blue]>> Enhanced Fair Value Analysis for {ticker.upper()}[/bold blue]")
        
        # Import the fair value calculator
        from .core.fair_value import FairValueCalculator
        
        # Run enhanced analysis
        calculator = FairValueCalculator()
        results = calculator.enhanced_fair_value_analysis(ticker, save_detailed_report=report)
        
        console.print("\n[bold green]>> Fair value analysis completed successfully![/bold green]")
        
        if report:
            console.print("[dim]>> Detailed report saved to current directory[/dim]")
        
    except ImportError as e:
        console.print(f"[red]ERROR: Could not import fair value calculator: {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]ERROR: Fair value calculation failed: {e}[/red]")
        console.print("[yellow]TIP: Make sure owner earnings data exists first (run 'analyze' command)[/yellow]")
        raise typer.Exit(1)

@app.command()
def calculate(
    ticker: str = typer.Option(..., "--ticker", "-t", help="Stock ticker symbol"),
    force: bool = typer.Option(False, "--force", "-f", help="Force recalculation")
):
    """
    Calculate owner earnings for a specific ticker
    
    This command calculates Warren Buffett's owner earnings from financial data.
    Requires financial data to be available in the data/ directory.
    """
    console.print(f"[bold blue]Calculating owner earnings for {ticker.upper()}...[/bold blue]")
    
    try:
        from .core.owner_earnings import OwnerEarningsCalculator
        
        # This is a placeholder - would need to implement the full calculation workflow
        console.print(f"[yellow]WARNING: Owner earnings calculation not yet fully implemented.[/yellow]")
        console.print(f"[yellow]NOTE: To calculate owner earnings for {ticker.upper()}:[/yellow]")
        console.print("  1. Ensure you have downloaded financial data")
        console.print("  2. Place Excel files in downloaded_files/ directory")
        console.print("  3. The calculation module is available for development")
        
        console.print(f"[green]NOTE: Module loaded: OwnerEarningsCalculator available[/green]")
        
    except ImportError as e:
        console.print(f"[red]ERROR: Cannot import OwnerEarningsCalculator: {e}[/red]")


@app.command()
def fair_value(
    ticker: str = typer.Option(..., "--ticker", "-t", help="Stock ticker symbol"),
    growth_rate: float = typer.Option(0.02, "--growth", "-g", help="Annual growth rate (e.g., 0.02 for 2%)"),
    discount_rate: Optional[float] = typer.Option(None, "--discount", "-d", help="Discount rate (uses 10Y Treasury if not specified)"),
    terminal_multiple: float = typer.Option(15.0, "--terminal", help="Terminal value P/E multiple"),
    cash: Optional[float] = typer.Option(None, "--cash", help="Cash and short-term investments (auto-extracted if not provided)"),
    debt: Optional[float] = typer.Option(None, "--debt", help="Total debt (auto-extracted if not provided)"),
    shares: Optional[float] = typer.Option(None, "--shares", help="Shares outstanding in millions (auto-extracted if not provided)"),
    scenarios: bool = typer.Option(True, "--scenarios/--no-scenarios", help="Include scenario analysis"),
    manual: bool = typer.Option(False, "--manual", help="Force manual input mode (disable auto-extraction)")
):
    """
    Calculate fair value using Owner Earnings DCF methodology
    
    This command calculates intrinsic value by:
    1. Using 10-year average Owner Earnings as future cash flow
    2. Discounting at 10-year Treasury rate (or specified rate)
    3. AUTO-EXTRACTING cash/debt/shares from downloaded data (NEW!)
    4. Calculating per-share fair value
    
    Example (auto-extraction):
    ms fair-value --ticker AAPL --growth 0.03
    
    Example (manual mode):
    ms fair-value --ticker AAPL --growth 0.03 --cash 100000000000 --debt 20000000000 --shares 15000 --manual
    """
    console.print(f"[bold green]Fair Value Analysis for {ticker.upper()}[/bold green]")
    
    try:
        from .core.fair_value import FairValueCalculator
        from pathlib import Path
        
        # Look for owner earnings data
        data_folder = Path("data")
        clean_ticker = ticker.replace('.', '_').upper()
        
        annual_file = data_folder / f"owner_earnings_annual_{clean_ticker.lower()}.csv"
        
        if not annual_file.exists():
            console.print(f"[red]ERROR: Owner earnings data not found for {ticker.upper()}[/red]")
            console.print(f"[yellow]Expected file: {annual_file}[/yellow]")
            console.print(f"[yellow]TIP: Run 'ms analyze {ticker}' first to generate owner earnings data[/yellow]")
            return
        
        # Initialize calculator and load data
        calculator = FairValueCalculator()
        calculator.company_name = ticker.upper()
        
        if not calculator.load_owner_earnings_data(str(annual_file)):
            console.print(f"[red]ERROR: Failed to load owner earnings data[/red]")
            return
        
        # Calculate 10-year average
        avg_earnings = calculator.calculate_average_owner_earnings(years=10)
        if avg_earnings is None:
            console.print(f"[red]ERROR: Insufficient owner earnings data for analysis[/red]")
            return
        
        # Auto-extract balance sheet data unless manual mode or values provided
        if not manual and (cash is None or debt is None or shares is None):
            console.print(f"\n[bold blue]Auto-Extracting Balance Sheet Data[/bold blue]")
            
            # Use automatic extraction method
            base_results = calculator.calculate_fair_value_auto(
                ticker=ticker,
                average_owner_earnings=avg_earnings,
                discount_rate=discount_rate,
                growth_rate=growth_rate,
                terminal_multiple=terminal_multiple
            )
            
        else:
            # Use manual/provided values
            console.print(f"\n[bold blue]Manual Balance Sheet Mode[/bold blue]")
            
            # Convert shares from millions to actual count if provided
            shares_actual = shares * 1_000_000 if shares else None
            
            # Use provided values or defaults
            cash_value = cash if cash is not None else 0
            debt_value = debt if debt is not None else 0
            
            console.print(f"Using provided values:")
            console.print(f"   Cash & Investments: ${cash_value:,.0f}")
            console.print(f"   Total Debt: ${debt_value:,.0f}")
            if shares_actual:
                console.print(f"   Shares Outstanding: {shares_actual:,.0f}")
            
            base_results = calculator.calculate_fair_value(
                average_owner_earnings=avg_earnings,
                discount_rate=discount_rate,
                growth_rate=growth_rate,
                terminal_multiple=terminal_multiple,
                cash_and_investments=cash_value,
                total_debt=debt_value,
                shares_outstanding=shares_actual
            )
        
        # Show key results
        console.print(f"\n[bold green]FAIR VALUE SUMMARY[/bold green]")
        console.print(f"Enterprise Value: [green]${base_results['enterprise_value']:,.0f}[/green]")
        console.print(f"Equity Value: [green]${base_results['equity_value']:,.0f}[/green]")
        
        if base_results['fair_value_per_share']:
            console.print(f"Fair Value per Share: [bold green]${base_results['fair_value_per_share']:,.2f}[/bold green]")
        
        # Scenario analysis
        if scenarios:
            console.print(f"\n[bold blue]Scenario Analysis[/bold blue]")
            
            # For scenarios, use the extracted/provided balance sheet data
            cash_for_scenarios = base_results['cash_and_investments']
            debt_for_scenarios = base_results['total_debt']
            shares_for_scenarios = base_results['shares_outstanding']
            
            scenario_df = calculator.create_scenario_analysis(
                average_owner_earnings=avg_earnings,
                shares_outstanding=shares_for_scenarios,
                cash_and_investments=cash_for_scenarios,
                total_debt=debt_for_scenarios
            )
            
            # Display scenario table
            if base_results['fair_value_per_share']:
                console.print(f"\n[bold]Per-Share Fair Values:[/bold]")
                for _, row in scenario_df.iterrows():
                    if 'Fair Value per Share' in row:
                        console.print(f"  {row['Scenario']}: [green]${row['Fair Value per Share']:,.2f}[/green]")
        
        # Save report
        report_file = data_folder / f"fair_value_analysis_{clean_ticker.lower()}.txt"
        calculator.save_valuation_report(base_results, scenario_df if scenarios else None, str(report_file))
        
        console.print(f"\n[green]SUCCESS: Fair value analysis complete![/green]")
        console.print(f"[dim]Report saved to: {report_file}[/dim]")
        
    except ImportError as e:
        console.print(f"[red]ERROR: Cannot import FairValueCalculator: {e}[/red]")
    except Exception as e:
        console.print(f"[red]ERROR: Fair value calculation failed: {e}[/red]")

@app.command()
def visualize(
    ticker: str = typer.Option(None, "--ticker", "-t", help="Stock ticker symbol"),
    all_data: bool = typer.Option(False, "--all", "-a", help="Visualize all available data")
):
    """
    Create visualizations from calculated owner earnings data
    
    This command generates charts and graphs from owner earnings calculations.
    Requires calculated data to be available in the data/ directory.
    """
    if ticker:
        console.print(f"[bold blue]>> Creating visualizations for {ticker.upper()}...[/bold blue]")
    else:
        console.print("[bold blue]>> Creating visualizations from available data...[/bold blue]")
    
    try:
        # Check if visualization module is available
        try:
            from .visualization.charts import main as visualization_main
            visualization_available = True
        except ImportError:
            visualization_available = False
            
        if not visualization_available:
            console.print(f"[red]ERROR: Visualization dependencies not available[/red]")
            console.print(f"[yellow]NOTE: Install with: pip install matplotlib PyQt6[/yellow]")
            return
            
        console.print(f"[green]>> Running visualization for {ticker or 'available data'}...[/green]")
        
        # Ensure we're in the right directory for data files
        import os
        original_dir = os.getcwd()
        
        try:
            # Call the visualization main function
            visualization_main()
            
            console.print(f"[green]>> Visualization completed successfully![/green]")
            console.print("Check the charts/ directory for generated visualizations")
        finally:
            # Always restore original directory
            os.chdir(original_dir)
        
    except Exception as e:
        console.print(f"[red]ERROR: Error during visualization: {e}[/red]")

@app.command()
def shares_analysis(
    ticker: str = typer.Option(None, "--ticker", "-t", help="Stock ticker symbol"),
):
    """
    Create comprehensive shares outstanding analysis and visualization.
    
    This command analyzes all share-related metrics from downloaded financial data,
    including basic shares, diluted shares, weighted averages, and share classes.
    Creates detailed visualization showing share count evolution and dilution analysis.
    
    Example:
    ms shares-analysis --ticker CVNA
    """
    try:
        from .visualization.charts import create_shares_outstanding_analysis
        
        if not ticker:
            ticker = typer.prompt("Enter ticker symbol")
        
        console.print(f"[bold blue]Analyzing shares outstanding for {ticker.upper()}[/bold blue]")
        
        result = create_shares_outstanding_analysis(ticker.upper())
        
        if result:
            console.print(f"\n[bold green]SUCCESS: Shares analysis complete![/bold green]")
            console.print(f"Analysis saved to: ./analysis_output/{ticker.lower()}_shares_analysis.png")
        else:
            console.print(f"[bold red]ERROR: Failed to analyze shares for {ticker}[/bold red]")
            console.print("Make sure you have downloaded financial data first.")
            
    except ImportError:
        console.print("[red]Error: Visualization dependencies not available[/red]")
    except Exception as e:
        console.print(f"[red]Error in shares analysis: {e}[/red]")

def main():
    """Main entry point for the CLI."""
    app()

if __name__ == "__main__":
    app()
