"""
Core analysis functions for MarketSwimmer.
This module provides the main analysis workflow.
"""

import os
import sys
import subprocess
import webbrowser
from pathlib import Path
from typing import Optional
from rich.console import Console

console = Console()

def clean_ticker_for_filename(ticker: str) -> str:
    """Clean ticker symbol for use in filenames."""
    return ticker.replace('.', '_').upper()

def analyze_ticker_workflow(ticker: str, force: bool = False) -> bool:
    """
    Run the complete analysis workflow for a ticker.
    
    Args:
        ticker: Stock ticker symbol
        force: Force re-download even if data exists
        
    Returns:
        bool: True if analysis completed successfully
    """
    try:
        from .workflow import AnalysisWorkflow
        
        workflow = AnalysisWorkflow()
        return workflow.run_complete_analysis(ticker, force_download=force)
        
    except Exception as e:
        console.print(f"[red]ERROR: Error during analysis: {e}[/red]")
        
        # Fallback to guidance if automated workflow fails
        console.print(f"[yellow]NOTE: Falling back to manual guidance for {ticker}:[/yellow]")
        console.print(f"  1. Visit: https://stockrow.com/vector/exports/financials/{ticker.upper()}")
        console.print(f"  2. Download the Excel file")
        console.print(f"  3. Run: ms calculate --ticker {ticker}")
        console.print(f"  4. Run: ms visualize --ticker {ticker}")
        
        return "guidance_provided"

def visualize_existing_data() -> bool:
    """
    Generate visualizations from existing data.
    
    Returns:
        bool: True if visualization completed successfully
    """
    try:
        console.print(">> Generating charts from existing data...")
        
        # For now, provide a helpful message
        console.print("[yellow]WARNING: Visualization from existing data not yet implemented in package version.[/yellow]")
        console.print("[yellow]NOTE: To create visualizations:[/yellow]")
        console.print("  1. Ensure you have data files in the data/ directory")
        console.print("  2. Run: ms visualize")
        
        return "guidance_provided"  # Not implemented yet, but guidance given
        
    except Exception as e:
        console.print(f"[red]ERROR: Error during visualization: {e}[/red]")
        return False
