"""
Core analysis modules for MarketSwimmer.

This module contains the core financial analysis functionality including
the OwnerEarningsCalculator class that implements Warren Buffett's 
Owner Earnings methodology and the FairValueCalculator for intrinsic
value analysis using DCF methodology.
"""

from .owner_earnings import OwnerEarningsCalculator
from .fair_value import FairValueCalculator

__all__ = ["OwnerEarningsCalculator", "FairValueCalculator"]
