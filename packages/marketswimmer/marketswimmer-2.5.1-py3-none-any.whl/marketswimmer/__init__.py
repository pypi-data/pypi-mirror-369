"""
MarketSwimmer - Warren Buffett's Owner Earnings Analysis Tool

A comprehensive financial analysis tool that implements Warren Buffett's Owner Earnings 
methodology to calculate the true economic value of any publicly traded company.

Owner Earnings = Net Income + Depreciation/Amortization - CapEx - Working Capital Changes

Features:
- Professional CLI with rich formatting
- PyQt6-based GUI application
- Advanced financial visualizations
- Multi-format data support (annual/quarterly)
- Automated data processing from StockRow exports

Usage:
    # Command line
    from marketswimmer.cli import main
    main()
    
    # Python API
    from marketswimmer import OwnerEarningsCalculator
    calculator = OwnerEarningsCalculator("financial_data.xlsx")
    results = calculator.calculate_owner_earnings()
"""

__version__ = "2.5.0"
__author__ = "Jeremy Evans"
__email__ = "jeremyevans@hey.com"
__license__ = "MIT"

# Import main classes for easy access
from .core.owner_earnings import OwnerEarningsCalculator
from .core.fair_value import FairValueCalculator

# Lazy import for visualization to avoid dependency issues when matplotlib/PyQt6 not available
try:
    from .visualization import OwnerEarningsVisualizer
    _VISUALIZATION_AVAILABLE = True
except ImportError:
    _VISUALIZATION_AVAILABLE = False
    OwnerEarningsVisualizer = None

from .cli import main as cli_main

# Define what gets imported with "from marketswimmer import *"
__all__ = [
    "OwnerEarningsCalculator",
    "FairValueCalculator",
    "OwnerEarningsVisualizer", 
    "cli_main",
    "__version__",
    "__author__",
]

# Package metadata
PACKAGE_NAME = "marketswimmer"
DESCRIPTION = "Warren Buffett's Owner Earnings Analysis Tool"
LONG_DESCRIPTION = """
MarketSwimmer implements Warren Buffett's Owner Earnings methodology to provide 
true economic analysis of publicly traded companies. Features include professional
CLI, GUI application, and comprehensive financial visualizations.
"""

# Configuration constants
DEFAULT_DATA_DIR = "data"
DEFAULT_CHARTS_DIR = "charts"
DEFAULT_DOWNLOADS_DIR = "downloaded_files"
DEFAULT_LOGS_DIR = "logs"

# Supported file formats
SUPPORTED_FORMATS = [".xlsx", ".xls"]
SUPPORTED_DATA_TYPES = ["Annual", "Quarterly"]

def get_version():
    """Return the package version."""
    return __version__

def get_package_info():
    """Return package information dictionary."""
    return {
        "name": PACKAGE_NAME,
        "version": __version__,
        "author": __author__,
        "description": DESCRIPTION,
        "license": __license__,
    }
