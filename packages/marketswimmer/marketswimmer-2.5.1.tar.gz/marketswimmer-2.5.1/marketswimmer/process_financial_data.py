#!/usr/bin/env python3
"""
Financial Data Processor for MarketSwimmer
Converts downloaded XLSX files into processed annual data for analysis
"""

import pandas as pd
import json
from pathlib import Path
import sys
from datetime import datetime

def process_xlsx_to_quarterly_data(xlsx_file, ticker, output_path=Path("data")):
    """
    Process XLSX financial export to extract quarterly data
    """
    print(f">> Processing quarterly financial data for {ticker}...")
    
    # Read the quarterly income statement
    df = pd.read_excel(xlsx_file, sheet_name='Income Statement, Q')
    print(f">> Loaded quarterly data with shape: {df.shape}")
    
    # Extract quarterly periods from column headers (like "Jun '25", "Mar '25", etc.)
    quarterly_periods = []
    for col in df.columns[1:]:  # Skip first column (row labels)
        if "'" in str(col):  # Quarterly format like "Jun '25"
            quarterly_periods.append(str(col))
    
    print(f">> Found {len(quarterly_periods)} quarterly data points: {quarterly_periods[:12]}")  # Show first 12
    
    # Extract quarterly financial data
    quarterly_data = {}
    
    for period in quarterly_periods[:40]:  # Limit to last 40 quarters (10 years)
        try:
            # Convert period format from "Jun '25" to "2025Q2" 
            month_part, year_part = period.split(" '")
            year = 2000 + int(year_part) if int(year_part) < 50 else 1900 + int(year_part)
            
            # Map months to quarters
            month_to_quarter = {
                'Mar': 'Q1', 'Jun': 'Q2', 'Sep': 'Q3', 'Dec': 'Q4'
            }
            quarter = month_to_quarter.get(month_part, 'Q1')
            period_key = f"{year}{quarter}"
            
            # Extract financial metrics for this quarter
            quarter_data = {}
            
            # Find and extract each metric
            for idx, row in df.iterrows():
                metric_name = str(row.iloc[0]).strip()
                value = row[period]
                
                if pd.notna(value) and metric_name:
                    # Convert to numeric if it's not already
                    try:
                        numeric_value = float(value)
                        quarter_data[metric_name] = numeric_value
                    except:
                        pass
            
            if quarter_data:
                quarterly_data[period_key] = quarter_data
                
        except Exception as e:
            print(f"   Warning: Could not process period {period}: {e}")
            continue
    
    # Save processed quarterly data
    json_file = output_path / f"{ticker.lower()}_quarterly_data.json"
    with open(json_file, 'w') as f:
        json.dump(quarterly_data, f, indent=2)
    print(f">> Saved quarterly JSON data to: {json_file}")
    
    # Create MarketSwimmer format CSV for quarterly data
    periods = []
    net_incomes = []
    depreciations = []
    capexs = []
    
    for period, period_data in quarterly_data.items():
        periods.append(period)
        # Use the actual column names from quarterly data
        net_incomes.append(period_data.get('Net Income Common', 0))
        # For now, use zeros for data we don't have in income statement
        depreciations.append(0) 
        capexs.append(0)
    
    quarterly_df = pd.DataFrame({
        'Period': periods,
        'Net Income': net_incomes,
        'Depreciation': depreciations,
        'CapEx': capexs,
        'Working Capital Change': [0] * len(periods),
        'Owner Earnings': net_incomes  # For now, just use net income
    })
    
    # Sort by period for chronological order
    quarterly_df = quarterly_df.sort_values('Period')
    
    csv_file = output_path / f"owner_earnings_quarterly_{ticker.lower()}.csv"
    quarterly_df.to_csv(csv_file, index=False)
    print(f">> Saved MarketSwimmer quarterly CSV to: {csv_file}")
    
    return quarterly_data

def process_xlsx_to_annual_data(xlsx_file, ticker, output_path=Path("data")):
    """
    Process downloaded XLSX financial data into annual summary format
    
    Args:
        xlsx_file: Path to the downloaded XLSX file
        ticker: Stock ticker symbol
        output_path: Directory to save processed data
    
    Returns:
        dict: Processed annual financial data
    """
    print(f">> Processing financial data for {ticker}...")
    
    # Read the XLSX file
    try:
        df = pd.read_excel(xlsx_file)
        print(f">> Loaded data with shape: {df.shape}")
    except Exception as e:
        print(f"ERROR: Could not read XLSX file: {e}")
        return None
    
    # Create output directory
    output_path.mkdir(exist_ok=True)
    
    # Extract financial metrics
    metrics_data = {}
    
    # Set the first column as index (metric names)
    df = df.set_index(df.columns[0])
    
    # Get annual columns (December quarters)
    annual_columns = [col for col in df.columns if "Dec" in str(col)]
    print(f">> Found {len(annual_columns)} annual data points: {annual_columns}")
    
    # Extract key metrics for owner earnings calculation
    key_metrics = [
        'Revenue',
        'Net Income Common',
        'Operating Cash Flow Margin',
        'EPS (Diluted)',
        'Shares (Diluted, Weighted)',
        'Operating Income',
        'EBITDA Margin'
    ]
    
    annual_data = {}
    for year_col in annual_columns[:10]:  # Last 10 years
        year_data = {}
        for metric in key_metrics:
            if metric in df.index:
                value = df.loc[metric, year_col]
                if pd.notna(value):
                    year_data[metric] = float(value) if isinstance(value, (int, float)) else value
                else:
                    year_data[metric] = None
            else:
                year_data[metric] = None
        
        # Extract year from column name (e.g., "Dec '24" -> "2024")
        try:
            year_str = year_col.split("'")[1]
            if len(year_str) == 2:
                year = f"20{year_str}" if int(year_str) < 50 else f"19{year_str}"
            else:
                year = year_str
            annual_data[year] = year_data
        except:
            annual_data[year_col] = year_data
    
    # Save processed data
    output_file = output_path / f"{ticker.lower()}_annual_data.json"
    
    # Also save in MarketSwimmer expected format
    csv_file = output_path / f"owner_earnings_annual_{ticker.lower()}.csv"
    json_file = output_path / f"{ticker.lower()}_annual_data.json"  # Keep backup
    
    annual_df = pd.DataFrame(annual_data).T
    
    # Create the expected CSV format with correct column names
    expected_df = pd.DataFrame()
    expected_df['Period'] = annual_df.index
    
    # Convert financial data to expected format (in dollars, not millions)
    for col in expected_df['Period']:
        year_data = annual_data.get(str(col), {})
        # Extract values and convert to full dollars
        revenue = year_data.get('Revenue (in millions)', 0) * 1_000_000
        net_income = year_data.get('Net Income (in millions)', 0) * 1_000_000
        depreciation = year_data.get('Depreciation & Amortization (in millions)', 0) * 1_000_000
        capex = year_data.get('Capital Expenditures (in millions)', 0) * 1_000_000
        
    # Use actual data from our processed results
    periods = []
    net_incomes = []
    depreciations = []
    capexs = []
    
    for year, year_data in annual_data.items():
        periods.append(year)
        # Use the actual column names from our data
        net_incomes.append(year_data.get('Net Income Common', 0))
        # For now, use zeros for data we don't have
        depreciations.append(0) 
        capexs.append(0)
    
    expected_df = pd.DataFrame({
        'Period': periods,
        'Net Income': net_incomes,
        'Depreciation': depreciations,
        'CapEx': capexs,
        'Working Capital Change': [0] * len(periods),  # We don't have this data yet
        'Owner Earnings': net_incomes  # For now, just use net income
    })
    
    expected_df.to_csv(csv_file, index=False)
    print(f">> Saved MarketSwimmer format CSV to: {csv_file}")
    
    # Save original format too
    backup_csv = output_path / f"{ticker.lower()}_annual_data.csv"
    annual_df.to_csv(backup_csv)
    print(f">> Saved backup CSV to: {backup_csv}")
    
    # JSON
    with open(json_file, 'w') as f:
        json.dump(annual_data, f, indent=2)
    print(f">> Saved JSON data to: {json_file}")
    
    return annual_data

def find_and_process_downloaded_files(ticker=None):
    """
    Find downloaded XLSX files and process them
    """
    downloads_dir = Path("downloaded_files")
    if not downloads_dir.exists():
        print("ERROR: downloaded_files directory not found")
        return False
    
    # Find XLSX files
    xlsx_files = list(downloads_dir.glob("*.xlsx"))
    if not xlsx_files:
        print("ERROR: No XLSX files found in downloaded_files directory")
        return False
    
    print(f">> Found {len(xlsx_files)} XLSX files")
    
    # Process each file
    for xlsx_file in xlsx_files:
        # Extract ticker from filename if not provided
        if ticker is None:
            # Try to extract from filename like "financials_export_ally_2025_08_04_125820.xlsx"
            parts = xlsx_file.stem.split('_')
            if len(parts) >= 3:
                file_ticker = parts[2].upper()
            else:
                file_ticker = "UNKNOWN"
        else:
            file_ticker = ticker.upper()
        
        print(f"\n>> Processing {xlsx_file.name} for ticker {file_ticker}")
        
        # Process both annual and quarterly data
        annual_result = process_xlsx_to_annual_data(xlsx_file, file_ticker)
        quarterly_result = process_xlsx_to_quarterly_data(xlsx_file, file_ticker)
        
        if annual_result or quarterly_result:
            print(f"✅ Successfully processed {file_ticker} data")
            return True
        else:
            print(f"❌ Failed to process {file_ticker} data")
    
    return False

def main():
    """Main function for command line usage"""
    if len(sys.argv) > 1:
        ticker = sys.argv[1].upper()
        print(f"Processing data for specific ticker: {ticker}")
        success = find_and_process_downloaded_files(ticker)
    else:
        print("Processing all downloaded files...")
        success = find_and_process_downloaded_files()
    
    if success:
        print("\n🎉 Data processing completed successfully!")
        print("You can now use the 'Calculate Owner Earnings' and 'Create Visualizations' buttons")
    else:
        print("\n❌ Data processing failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
