"""
GUI modules for MarketSwimmer.

This module contains the PyQt6-based graphical user interface
for interactive owner earnings analysis.
"""

try:
    from .main_window import MarketSwimmerGUI, main as gui_main
    GUI_AVAILABLE = True
    # Alias for backward compatibility
    MarketSwimmerApp = MarketSwimmerGUI
except ImportError:
    # PyQt6 not available
    GUI_AVAILABLE = False
    
    def gui_main(*args, **kwargs):
        """Stub function when GUI is not available."""
        print("GUI not available. Please install PyQt6: pip install PyQt6")
        return None
    
    class MarketSwimmerApp:
        """Stub class when GUI is not available."""
        def __init__(self, *args, **kwargs):
            print("GUI not available. Please install PyQt6: pip install PyQt6")

    # Also create the alias
    MarketSwimmerGUI = MarketSwimmerApp

__all__ = ["MarketSwimmerApp", "MarketSwimmerGUI", "gui_main", "GUI_AVAILABLE"]
