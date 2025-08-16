"""
Download management module for MarketSwimmer.
Handles automatic detection and processing of financial data downloads.
"""

import os
import shutil
import time
import webbrowser
import glob
from pathlib import Path
from typing import Optional, List
from rich.console import Console

console = Console()

class DownloadManager:
    """Manages financial data downloads for MarketSwimmer."""
    
    def __init__(self):
        self.download_folder = self._get_download_folder()
        self.target_folder = Path("downloaded_files")
        self.target_folder.mkdir(exist_ok=True)
    
    def _get_download_folder(self) -> Optional[Path]:
        """Get the user's default download folder."""
        # First try Windows registry for actual Downloads location
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                               r'Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders')
            downloads_path = winreg.QueryValueEx(key, '{374DE290-123F-4565-9164-39C4925E467B}')[0]
            winreg.CloseKey(key)
            downloads_folder = Path(downloads_path)
            if downloads_folder.exists():
                return downloads_folder
        except Exception:
            pass
        
        # Fallback to common locations
        user_home = Path.home()
        download_folders = [
            user_home / "Downloads",
            user_home / "Download", 
            user_home / "OneDrive" / "Desktop" / "Downloads",
            user_home / "OneDrive" / "Downloads",
            Path("C:/Users") / os.getenv("USERNAME", "") / "Downloads"
        ]
        
        for folder in download_folders:
            if folder.exists():
                return folder
        return None
    
    def open_stockrow_download(self, ticker: str) -> str:
        """Open StockRow download page for the specified ticker."""
        base_url = "https://stockrow.com/vector/exports/financials/{}?direction=desc"
        url = base_url.format(ticker.upper())
        
        console.print(f"[blue]>> Opening StockRow download for {ticker.upper()}[/blue]")
        console.print(f"[dim]URL: {url}[/dim]")
        console.print("\n[yellow]>> Please download the XLSX file from your browser[/yellow]")
        console.print("[yellow]>> Waiting for download to complete...[/yellow]")
        
        webbrowser.open(url)
        return url
    
    def find_recent_xlsx_files(self, minutes_back: int = 5) -> List[Path]:
        """Find XLSX files modified in the last few minutes."""
        if not self.download_folder or not self.download_folder.exists():
            return []
        
        current_time = time.time()
        cutoff_time = current_time - (minutes_back * 60)
        recent_files = []
        
        for xlsx_file in self.download_folder.glob("*.xlsx"):
            if xlsx_file.stat().st_mtime > cutoff_time:
                recent_files.append(xlsx_file)
        
        return sorted(recent_files, key=lambda x: x.stat().st_mtime, reverse=True)
    
    def wait_for_download(self, ticker: str, timeout: int = 120) -> Optional[Path]:
        """Wait for a financial data download to complete."""
        console.print(f"[yellow]>> Monitoring downloads folder for {ticker} data...[/yellow]")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            # Check for recent files (increased from 2 to 10 minutes to catch existing downloads)
            recent_files = self.find_recent_xlsx_files(minutes_back=10)
            
            for file_path in recent_files:
                if self._is_financial_data_file(file_path, ticker):
                    console.print(f"[green]>> Found download: {file_path.name}[/green]")
                    return file_path
            
            time.sleep(2)  # Check every 2 seconds
        
        console.print(f"[red]>> Timeout waiting for download[/red]")
        return None
    
    def _is_financial_data_file(self, file_path: Path, ticker: str) -> bool:
        """Check if a file looks like financial data for the given ticker."""
        filename = file_path.name.lower()
        ticker_lower = ticker.lower().replace('.', '')
        
        # Ticker-specific patterns only - no generic matches to prevent cross-contamination
        patterns = [
            f"financials_export_{ticker_lower}",
            f"financial_{ticker_lower}",
            f"{ticker_lower}_financials",
        ]
        
        return any(pattern in filename for pattern in patterns)
    
    def copy_to_project(self, source_file: Path, ticker: str) -> Path:
        """Copy downloaded file to the project's downloaded_files directory."""
        # Create a clean filename
        clean_ticker = ticker.replace('.', '_').upper()
        timestamp = time.strftime("%Y_%m_%d_%H%M%S")
        target_filename = f"financials_export_{clean_ticker.lower()}_{timestamp}.xlsx"
        target_path = self.target_folder / target_filename
        
        try:
            shutil.copy2(source_file, target_path)
            console.print(f"[green]>> Copied to: {target_path}[/green]")
            return target_path
        except Exception as e:
            console.print(f"[red]ERROR: Error copying file: {e}[/red]")
            raise
    
    def get_latest_data_file(self, ticker: Optional[str] = None) -> Optional[Path]:
        """Get the most recent financial data file for a ticker."""
        pattern = "*.xlsx"
        if ticker:
            clean_ticker = ticker.replace('.', '_').lower()
            pattern = f"*{clean_ticker}*.xlsx"
        
        files = list(self.target_folder.glob(pattern))
        if not files:
            return None
        
        # Return the most recently modified file
        return max(files, key=lambda x: x.stat().st_mtime)
