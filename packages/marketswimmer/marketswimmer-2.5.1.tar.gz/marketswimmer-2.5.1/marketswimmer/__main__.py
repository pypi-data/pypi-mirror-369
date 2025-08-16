#!/usr/bin/env python3
"""
Main entry point for MarketSwimmer when run as a module.
Handles: python -m marketswimmer [command] [args]
"""

if __name__ == "__main__":
    from .cli import main
    main()
