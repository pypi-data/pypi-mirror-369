"""
Visualization modules for MarketSwimmer.

This module contains chart generation and visualization functionality
for owner earnings analysis including waterfall charts, trend analysis,
and volatility studies.
"""

from .charts import (
    detect_ticker_symbol,
    load_data,
    prepare_quarterly_data,
    prepare_annual_data,
    create_owner_earnings_comparison,
    create_components_breakdown,
    create_volatility_analysis,
    save_and_show_plots,
    main as visualize_main
)

# Create a convenience class for the visualizer
class OwnerEarningsVisualizer:
    """Convenience wrapper for owner earnings visualization functions."""
    
    @staticmethod
    def create_all_charts(ticker=None):
        """Create all standard charts for owner earnings analysis."""
        return visualize_main()
    
    @staticmethod
    def detect_ticker():
        """Detect ticker symbol from most recent data file."""
        return detect_ticker_symbol()

__all__ = [
    "OwnerEarningsVisualizer",
    "detect_ticker_symbol", 
    "load_data",
    "prepare_quarterly_data",
    "prepare_annual_data", 
    "create_owner_earnings_comparison",
    "create_components_breakdown",
    "create_volatility_analysis",
    "save_and_show_plots",
    "visualize_main"
]
