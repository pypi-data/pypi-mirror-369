import pandas as pd
import matplotlib
# Set non-interactive backend for headless operation - must be before pyplot import
matplotlib.use('Agg')
import matplotlib.pyplot as plt
# Ensure matplotlib is in non-interactive mode
plt.ioff()
import seaborn as sns
import numpy as np
from datetime import datetime
import os
import glob
import re
import sys

def is_bank_or_insurance(ticker):
    """
    Simple bank/insurance detection for visualization purposes.
    Returns True if the company should exclude working capital from charts.
    """
    if not ticker:
        return False
        
    ticker_upper = ticker.upper()
    
    # Known bank tickers
    bank_keywords = [
        'BANK', 'BANCORP', 'BANC', 'FINANCIAL', 'TRUST', 'CREDIT', 'SAVINGS',
        'FARGO', 'CHASE', 'MORGAN', 'GOLDMAN', 'CITI', 'AMERICA'
    ]
    
    # Insurance keywords
    insurance_keywords = [
        'INSURANCE', 'INSUR', 'LIFE', 'MUTUAL', 'ASSURANCE', 'REINSURANCE'
    ]
    
    # Check ticker symbols
    if any(keyword in ticker_upper for keyword in bank_keywords + insurance_keywords):
        return True
        
    # Common bank/insurance tickers
    financial_tickers = {
        'JPM', 'BAC', 'WFC', 'C', 'GS', 'MS', 'USB', 'PNC', 'TFC', 'SCHW',
        'BK', 'STT', 'NTRS', 'CFG', 'RF', 'KEY', 'FITB', 'HBAN', 'ZION',
        'MTB', 'CMA', 'EWBC', 'SIVB', 'WAL', 'PBCT', 'BRK.B', 'BRK.A',
        'AIG', 'PRU', 'MET', 'AFL', 'ALL', 'TRV', 'PGR', 'CB', 'AXP'
    }
    
    return ticker_upper in financial_tickers

def setup_plotting_style():
    """Set up a professional plotting style."""
    plt.style.use('default')
    sns.set_palette("husl")
    plt.rcParams['figure.figsize'] = (15, 10)
    plt.rcParams['font.size'] = 10
    plt.rcParams['axes.labelsize'] = 12
    plt.rcParams['axes.titlesize'] = 14
    plt.rcParams['legend.fontsize'] = 10
    plt.rcParams['xtick.labelsize'] = 9
    plt.rcParams['ytick.labelsize'] = 9

def detect_ticker_symbol():
    """Detect the ticker symbol from the most recent XLSX file."""
    try:
        # Check downloaded_files folder for recent files
        xlsx_files = glob.glob("./downloaded_files/*.xlsx")
        if xlsx_files:
            # Get the most recent file
            latest_file = max(xlsx_files, key=os.path.getmtime)
            filename = os.path.basename(latest_file)
            
            # Extract ticker from filename like "financials_export_brkb_2025_08_02_221804.xlsx"
            if 'financials_export_' in filename:
                parts = filename.split('_')
                if len(parts) >= 3:
                    ticker = parts[2].upper()
                    # Handle special cases like BRK.B
                    if ticker == 'BRKB':
                        ticker = 'BRK.B'
                    return ticker
        
        # Fallback: try to detect from data patterns
        return "TICKER"
    except:
        return "TICKER"

def create_shares_outstanding_analysis(ticker, output_dir='./charts'):
    """
    Create comprehensive analysis of shares outstanding data from downloaded financial statements.
    
    Args:
        ticker (str): Stock ticker symbol
    output_dir (str): Directory to save analysis charts (now defaults to './charts')
        
    Returns:
        bool: True if analysis was successful, False otherwise
    """
    def parse_quarter_date(date_str):
        """Convert quarter strings like "Jun '25" to readable format"""
        try:
            if "'" in date_str:
                # Handle formats like "Jun '25", "Mar '24"
                month_abbr, year_abbr = date_str.split(" '")
                year = int("20" + year_abbr) if int(year_abbr) < 50 else int("19" + year_abbr)
                
                # Convert month abbreviation to quarter
                month_to_quarter = {
                    'Mar': 'Q1', 'Jun': 'Q2', 'Sep': 'Q3', 'Dec': 'Q4'
                }
                quarter = month_to_quarter.get(month_abbr, 'Q1')
                return f"{quarter} {year}"
            else:
                return date_str
        except:
            return date_str
    
    try:
        # Find the most recent downloaded file for the ticker
        # Normalize ticker by replacing dots with underscores (e.g., BRK.B -> brk_b)
        normalized_ticker = ticker.lower().replace('.', '_')
        pattern = f'./downloaded_files/*{normalized_ticker}*.xlsx'
        xlsx_files = glob.glob(pattern)
        
        if not xlsx_files:
            print(f"No downloaded files found for ticker {ticker} (searched for pattern: {pattern})")
            return False
            
        # Get the most recent file
        latest_file = max(xlsx_files, key=os.path.getmtime)
        print(f"Analyzing shares data from: {os.path.basename(latest_file)}")
        
        # Read Excel file
        xl = pd.ExcelFile(latest_file)
        
        # Initialize data storage
        shares_data = {}
        issuance_data = {}  # For share issuance (positive bars)
        repurchase_data = {}  # For share repurchase (negative bars)
        debt_issuance_data = {}  # For debt issuance (positive bars)
        debt_repayment_data = {}  # For debt repayment (negative bars)
        debt_metrics_data = {}  # For debt level metrics (lines on debt chart)
        quarterly_data = []
        annual_data = []
        
        # Store stock price data for converting cash flow amounts to share counts
        stock_price_data = {}  # Will store {date: price} mapping
        
        # Process each sheet - Use quarterly balance sheet AND cash flow data
        for sheet_name in xl.sheet_names:
            # Process quarterly balance sheet data for share counts and quarterly cash flow for issuance
            if not ('q' in sheet_name.lower() and ('balance' in sheet_name.lower() or 'cash' in sheet_name.lower())):
                print(f"Skipping sheet '{sheet_name}' - only using quarterly balance sheet and cash flow data")
                continue
                
            try:
                df = pd.read_excel(latest_file, sheet_name=sheet_name)
                print(f"Processing quarterly sheet: {sheet_name}")
                
                # Look for share-related metrics and debt activities in quarterly data
                share_keywords = ['share', 'outstanding', 'diluted', 'basic', 'common', 'weighted', 'stock', 'issuance', 'issued', 'repurchase', 'buyback']
                debt_keywords = ['debt', 'borrowing', 'loan', 'bond', 'credit', 'financing']
                all_keywords = share_keywords + debt_keywords
                exclude_keywords = ['equity', 'liabilit', 'asset', 'book', 'value', 'price', 'market', 'treasury', 'common stock (net)', 'common stock net', 'financing cash flow']
                
                # Find rows with relevant keywords but exclude unwanted metrics
                relevant_rows = df[df.iloc[:, 0].astype(str).str.contains('|'.join(all_keywords), case=False, na=False)]
                if not relevant_rows.empty:
                    # Filter out unwanted metrics
                    filtered_rows = relevant_rows[~relevant_rows.iloc[:, 0].astype(str).str.contains('|'.join(re.escape(word) for word in exclude_keywords), case=False, na=False)]
                    share_rows = filtered_rows
                
                if not share_rows.empty:
                    print(f"Found {len(share_rows)} relevant metrics in {sheet_name}")
                    for idx, row in share_rows.iterrows():
                        metric_name = str(row.iloc[0]).strip()
                        
                        # Additional filtering to ensure we only get relevant metrics
                        if any(exclude_word in metric_name.lower() for exclude_word in ['equity', 'liabilit', 'asset', 'book', 'value', 'price', 'market', 'per share', 'ratio', 'treasury', 'common stock (net)', 'common stock net', 'financing cash flow', 'financing']):
                            continue
                            
                        # Process relevant metric
                        values = row.iloc[1:].dropna()
                        
                        # Determine the type of metric
                        is_share_issuance = any(keyword in metric_name.lower() for keyword in ['issuance', 'issued']) and 'share' in metric_name.lower()
                        is_share_repurchase = any(keyword in metric_name.lower() for keyword in ['repurchase', 'buyback']) and 'share' in metric_name.lower()
                        is_debt_issuance = any(keyword in metric_name.lower() for keyword in ['debt', 'borrowing', 'loan', 'bond']) and any(keyword in metric_name.lower() for keyword in ['issuance', 'issued', 'proceeds'])
                        is_debt_repayment = any(keyword in metric_name.lower() for keyword in ['debt', 'borrowing', 'loan', 'bond']) and any(keyword in metric_name.lower() for keyword in ['repayment', 'payment', 'retire'])
                        is_debt_metric = any(keyword in metric_name.lower() for keyword in ['long term debt', 'current part of debt', 'net debt', 'total debt', 'debt total'])
                        is_share_count = any(keyword in metric_name.lower() for keyword in ['outstanding', 'diluted', 'basic', 'common shares']) and not is_debt_metric
                        
                        # Handle combined metrics like "Issuance/Purchase of Shares" 
                        is_combined_share_activity = 'issuance' in metric_name.lower() and ('purchase' in metric_name.lower() or 'repurchase' in metric_name.lower())
                        
                        # Convert to numeric and store
                        numeric_values = []
                        dates = []
                        
                        for i, val in enumerate(values):
                            try:
                                if pd.notna(val) and str(val) != '—' and str(val) != '':
                                    # Handle different number formats
                                    if isinstance(val, str):
                                        # Remove commas, dollar signs, and other formatting
                                        clean_val = str(val).replace(',', '').replace('$', '').replace('%', '').strip()
                                        if clean_val and clean_val != '—':
                                            numeric_val = float(clean_val)
                                        else:
                                            continue
                                    else:
                                        numeric_val = float(val)
                                    
                                    # Apply appropriate threshold based on metric type
                                    should_include = False
                                    if is_share_issuance or is_share_repurchase:
                                        should_include = abs(numeric_val) > 1  # Very low threshold for share activities
                                    elif is_debt_issuance or is_debt_repayment:
                                        should_include = abs(numeric_val) > 10  # Low threshold for debt activities
                                    elif is_share_count:
                                        should_include = numeric_val > 1000  # Higher threshold for share counts
                                    else:
                                        should_include = numeric_val > 100  # Default threshold
                                    
                                    if should_include:
                                        numeric_values.append(numeric_val)
                                        # Get the actual column header as date
                                        if i + 1 < len(df.columns):
                                            date_str = str(df.columns[i + 1])
                                            # Parse and format the date
                                            formatted_date = parse_quarter_date(date_str)
                                            dates.append(formatted_date)
                                        else:
                                            dates.append(f"Period_{i+1}")
                                        
                            except (ValueError, TypeError):
                                continue
                        
                        if numeric_values:
                            key = f"{sheet_name}_{metric_name}"
                            
                            # Handle combined share activity metrics (like "Issuance/Purchase of Shares")
                            if is_combined_share_activity:
                                # Split positive and negative values based on cash flow direction
                                positive_values = []
                                positive_dates = []
                                negative_values = []
                                negative_dates = []
                                
                                # Note: Share issuance/repurchase bars are currently disabled for cleaner analysis
                                print(f"  Found combined metric '{metric_name}' - bars disabled for cleaner chart")
                                
                                for value, date in zip(numeric_values, dates):
                                    if value > 0:  # Positive = Net Issuance
                                        positive_values.append(value)
                                        positive_dates.append(date)
                                    elif value < 0:  # Negative = Net Repurchase
                                        negative_values.append(abs(value))  # Store as positive amount
                                        negative_dates.append(date)
                                
                                # Store positive cash flows as issuance (for potential future use)
                                if positive_values:
                                    issuance_data[f"{key}_positive"] = {
                                        'values': positive_values,
                                        'dates': positive_dates,
                                        'sheet': sheet_name,
                                        'metric': f"{metric_name} (Issuance)"
                                    }
                                
                                # Store negative cash flows as repurchase (for potential future use)
                                if negative_values:
                                    repurchase_data[f"{key}_negative"] = {
                                        'values': [-v for v in negative_values],  # Make negative for chart display
                                        'dates': negative_dates,
                                        'sheet': sheet_name,
                                        'metric': f"{metric_name} (Repurchase)"
                                    }
                            
                            # Store in appropriate data structure for single-purpose metrics
                            elif is_share_issuance:
                                issuance_data[key] = {
                                    'values': numeric_values,
                                    'dates': dates,
                                    'sheet': sheet_name,
                                    'metric': metric_name
                                }
                            elif is_share_repurchase:
                                repurchase_data[key] = {
                                    'values': [-abs(v) for v in numeric_values],  # Make negative for repurchases
                                    'dates': dates,
                                    'sheet': sheet_name,
                                    'metric': metric_name
                                }
                            elif is_debt_issuance:
                                debt_issuance_data[key] = {
                                    'values': numeric_values,
                                    'dates': dates,
                                    'sheet': sheet_name,
                                    'metric': metric_name
                                }
                            elif is_debt_repayment:
                                debt_repayment_data[key] = {
                                    'values': [-abs(v) for v in numeric_values],  # Make negative for repayments
                                    'dates': dates,
                                    'sheet': sheet_name,
                                    'metric': metric_name
                                }
                            elif is_debt_metric:
                                debt_metrics_data[key] = {
                                    'values': numeric_values,
                                    'dates': dates,
                                    'sheet': sheet_name,
                                    'metric': metric_name
                                }
                            else:
                                shares_data[key] = {
                                    'values': numeric_values,
                                    'dates': dates,
                                    'sheet': sheet_name,
                                    'metric': metric_name
                                }
                            
                            # Store for time series analysis
                            if 'q' in sheet_name.lower():
                                quarterly_data.extend([(d, v, metric_name) for d, v in zip(dates, numeric_values)])
                            else:
                                annual_data.extend([(d, v, metric_name) for d, v in zip(dates, numeric_values)])
                                
            except Exception as e:
                print(f"Warning: Could not process sheet {sheet_name}: {str(e)}")
                continue
        
        if not shares_data and not issuance_data and not repurchase_data and not debt_issuance_data and not debt_repayment_data and not debt_metrics_data:
            print(f"No relevant share or debt data found for {ticker}")
            return False
        
        # Extract stock price data from metrics ratios to convert cash flow amounts to share counts
        try:
            ratios_df = pd.read_excel(latest_file, sheet_name='Metrics Ratios, Q')
            
            # Look for Book value per Share to calculate approximate stock price
            book_value_per_share_row = ratios_df[ratios_df.iloc[:, 0].astype(str).str.contains('Book value per Share', case=False, na=False)]
            pb_ratio_row = ratios_df[ratios_df.iloc[:, 0].astype(str).str.contains('P/B ratio', case=False, na=False)]
            
            if not book_value_per_share_row.empty and not pb_ratio_row.empty:
                # Calculate estimated stock prices for share count conversion
                
                # Extract book value per share data
                bv_row = book_value_per_share_row.iloc[0]
                pb_row = pb_ratio_row.iloc[0]
                
                for i in range(1, len(bv_row)):
                    if pd.notna(bv_row.iloc[i]) and pd.notna(pb_row.iloc[i]):
                        try:
                            book_value = float(str(bv_row.iloc[i]).replace(',', '').replace('$', ''))
                            pb_ratio = float(str(pb_row.iloc[i]).replace(',', '').replace('$', ''))
                            stock_price = book_value * pb_ratio
                            
                            # Get the date for this column
                            date_str = str(ratios_df.columns[i])
                            formatted_date = parse_quarter_date(date_str)
                            stock_price_data[formatted_date] = stock_price
                        except (ValueError, TypeError):
                            continue
                            
                print(f"Extracted stock prices for {len(stock_price_data)} periods")
                if len(stock_price_data) > 0:
                    # Show a few examples of the calculated stock prices
                    sample_dates = list(stock_price_data.keys())[:3]
                    print("Sample stock price calculations:")
                    for date in sample_dates:
                        print(f"  {date}: ${stock_price_data[date]:.2f}")
            else:
                # No stock price data available - proceed without price conversion
                pass
        except Exception as e:
            print(f"Warning: Could not extract stock price data: {str(e)}")
        
        # Create visualizations
        os.makedirs(output_dir, exist_ok=True)
        
        # Create two separate charts: one for shares, one for debt
        plt.style.use('default')  # Clean, professional style
        
        # Sort dates chronologically - create a custom sort function
        def date_sort_key(date_str):
            """Sort dates like Q1 2023, Q2 2023, etc. chronologically"""
            try:
                if 'Q' in date_str and len(date_str.split()) == 2:
                    quarter, year = date_str.split()
                    quarter_num = int(quarter[1])  # Extract number from Q1, Q2, etc.
                    year_num = int(year)
                    return (year_num, quarter_num)
                else:
                    return (2000, 1)  # Default for unparseable dates
            except:
                return (2000, 1)
        
        # CHART 1: SHARES ANALYSIS
        if shares_data or issuance_data or repurchase_data:
            fig1, ax1 = plt.subplots(1, 1, figsize=(16, 10))
            fig1.suptitle(f'{ticker.upper()} - Shares Outstanding Analysis', fontsize=24, fontweight='bold', y=0.98)
            
            # Add more space at the top
            plt.subplots_adjust(top=0.92)
            
            # Find unique dates for shares data only
            shares_dates = set()
            for data_dict in [shares_data, issuance_data, repurchase_data]:
                for data in data_dict.values():
                    shares_dates.update(data['dates'])
            
            shares_timeline = sorted(list(shares_dates), key=date_sort_key)
            shares_date_to_x = {date: i for i, date in enumerate(shares_timeline)}
            # Always define shares_timeline_recent for downstream code
            if len(shares_timeline) > 12:
                shares_timeline_recent = shares_timeline[-12:]
            else:
                shares_timeline_recent = shares_timeline
            
            # Plot share count lines
            colors = plt.cm.Set1(np.linspace(0, 1, min(len(shares_data), 9)))
            
            for i, (key, data) in enumerate(shares_data.items()):
                values = data['values']
                dates = data['dates']

                # Convert values to millions and sort by date chronologically
                date_value_pairs = list(zip(dates, [v/1e6 for v in values]))
                date_value_pairs.sort(key=lambda x: date_sort_key(x[0]))

                # Always align to the last 12 quarters (even if missing data)
                y_values = []
                for date in shares_timeline_recent:
                    # Find value for this date, or 0 if missing
                    found = False
                    for d, v in date_value_pairs:
                        if d == date:
                            y_values.append(v)
                            found = True
                            break
                    if not found:
                        y_values.append(0)
                x_positions = list(range(len(shares_timeline_recent)))

                if any(y_values):
                    label = data['metric'][:40] if len(data['metric']) <= 40 else data['metric'][:37] + '...'
                    line_styles = ['-', '--', '-.', ':', '-', '--', '-.', ':', '-']
                    line_style = line_styles[i % len(line_styles)]

                    ax1.plot(x_positions, y_values, marker='o', label=label, color=colors[i % len(colors)],
                           linewidth=3, markersize=6, linestyle=line_style, alpha=0.8)
            
            # Commented out share issuance and repurchase bars for cleaner analysis
            # # Plot share issuance and repurchase bars
            # bar_width = 0.6
            # share_bar_data = {}
            # 
            # # Share issuance (positive, green bars) - Convert from dollars to shares
            # for key, data in issuance_data.items():
            #     for date, value in zip(data['dates'], data['values']):
            #         if date in shares_date_to_x:
            #             x_pos = shares_date_to_x[date]
            #             if x_pos not in share_bar_data:
            #                 share_bar_data[x_pos] = {'issuance': 0, 'repurchase': 0}
            #             
            #             # Convert from dollars to approximate shares using stock price
            #             if date in stock_price_data and stock_price_data[date] > 0:
            #                 shares_issued = value / stock_price_data[date]  # dollars / price per share = shares
            #                 
            #                 # Cap extremely large issuances (likely one-time events like IPO, SPAC, etc.)
            #                 # Flag if issuance would represent more than 25% of outstanding shares (~50M shares)
            #                 if shares_issued > 50e6:  # More than 50 million shares
            #                     print(f"  Large share issuance detected in {date}: ${value/1e6:.0f}M → {shares_issued/1e6:.1f}M shares (capped at 25M)")
            #                     shares_issued = min(shares_issued, 25e6)  # Cap at 25 million shares
            #                 
            #                 share_bar_data[x_pos]['issuance'] += shares_issued / 1e6  # Convert to millions
            #             else:
            #                 # Fallback: treat as millions of dollars if no stock price available
            #                 share_bar_data[x_pos]['issuance'] += value / 1e6
            # 
            # # Share repurchase (negative, red bars) - Convert from dollars to shares
            # for key, data in repurchase_data.items():
            #     for date, value in zip(data['dates'], data['values']):
            #         if date in shares_date_to_x:
            #             x_pos = shares_date_to_x[date]
            #             if x_pos not in share_bar_data:
            #                 share_bar_data[x_pos] = {'issuance': 0, 'repurchase': 0}
            #             
            #             # Convert from dollars to approximate shares using stock price
            #             if date in stock_price_data and stock_price_data[date] > 0:
            #                 shares_repurchased = abs(value) / stock_price_data[date]  # dollars / price per share = shares
            #                 
            #                 # Cap extremely large repurchases (likely one-time events)
            #                 if shares_repurchased > 100e6:  # More than 100 million shares
            #                     print(f"  Large share repurchase detected in {date}: ${abs(value)/1e6:.0f}M → {shares_repurchased/1e6:.1f}M shares (capped at 50M)")
            #                     shares_repurchased = min(shares_repurchased, 50e6)  # Cap at 50 million shares
            #                 
            #                 share_bar_data[x_pos]['repurchase'] += -shares_repurchased / 1e6  # Convert to millions, keep negative
            #             else:
            #                 # Fallback: treat as millions of dollars if no stock price available
            #                 share_bar_data[x_pos]['repurchase'] += value / 1e6
            # 
            # # Plot share bars
            # if share_bar_data:
            #     x_positions = list(share_bar_data.keys())
            #     issuance_vals = [share_bar_data[x]['issuance'] for x in x_positions]
            #     repurchase_vals = [share_bar_data[x]['repurchase'] for x in x_positions]
            #     
            #     # Determine labels based on whether we have stock price data
            #     if stock_price_data:
            #         issuance_label = 'Share Issuance (Est. Shares)'
            #         repurchase_label = 'Share Repurchase (Est. Shares)'
            #     else:
            #         issuance_label = 'Share Issuance ($M)'
            #         repurchase_label = 'Share Repurchase ($M)'
            #     
            #     if any(v != 0 for v in issuance_vals):
            #         ax1.bar(x_positions, issuance_vals, bar_width, label=issuance_label, color='green', alpha=0.7)
            #     if any(v != 0 for v in repurchase_vals):
            #         ax1.bar(x_positions, repurchase_vals, bar_width, label=repurchase_label, color='red', alpha=0.7)
            
            # Configure shares chart
            ax1.set_title('Historical Shares Outstanding (Millions)', fontsize=18, fontweight='bold', pad=30)
            ax1.set_xlabel('Time Period', fontsize=16, fontweight='bold')
            ax1.set_ylabel('Shares (Millions)', fontsize=16, fontweight='bold')
            
            # Fix x-axis for shares

            # Only show the most recent 3 years (12 quarters) on the x-axis
            if len(shares_timeline) > 12:
                shares_timeline_recent = shares_timeline[-12:]
            else:
                shares_timeline_recent = shares_timeline

            max_periods = len(shares_timeline_recent)
            ax1.set_xlim(-0.5, max_periods - 0.5)

            # Set x-ticks and labels for all recent quarters
            tick_positions = list(range(max_periods))
            tick_labels = [shares_timeline_recent[i] for i in tick_positions]
            ax1.set_xticks(tick_positions)
            ax1.set_xticklabels(tick_labels, rotation=45, ha='right')
            
            ax1.legend(bbox_to_anchor=(1.02, 1), loc='upper left', fontsize=12, frameon=True, 
                     fancybox=True, shadow=True)
            ax1.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
            ax1.tick_params(axis='both', which='major', labelsize=12)
            ax1.set_facecolor('#fafafa')
            
            # Save shares chart
            plt.tight_layout()
            shares_chart_path = os.path.join(output_dir, f'{ticker}_shares_analysis.png')
            plt.savefig(shares_chart_path, dpi=300, bbox_inches='tight')
            plt.close(fig1)
            print(f"Shares chart saved to: {shares_chart_path}")
        
        # CHART 2: DEBT ANALYSIS
        if debt_issuance_data or debt_repayment_data or debt_metrics_data:
            fig2, ax2 = plt.subplots(1, 1, figsize=(16, 10))
            fig2.suptitle(f'{ticker.upper()} - Debt Activity Analysis', fontsize=24, fontweight='bold', y=0.98)
            
            # Add subtitle explaining data availability
            fig2.text(0.5, 0.94, 'Note: Lines may start/end at different times based on data availability in financial reports', 
                     ha='center', fontsize=12, style='italic', alpha=0.7)
            
            # Add more space at the top
            plt.subplots_adjust(top=0.90)
            
            # Find unique dates for debt data including debt metrics
            debt_dates = set()
            for data_dict in [debt_issuance_data, debt_repayment_data, debt_metrics_data]:
                for data in data_dict.values():
                    debt_dates.update(data['dates'])
            
            debt_timeline = sorted(list(debt_dates), key=date_sort_key)
            debt_date_to_x = {date: i for i, date in enumerate(debt_timeline)}
            # Always define debt_timeline_recent for downstream code
            if len(debt_timeline) > 12:
                debt_timeline_recent = debt_timeline[-12:]
            else:
                debt_timeline_recent = debt_timeline
            
            # Plot debt level lines first (as background)
            debt_colors = plt.cm.Set2(np.linspace(0, 1, min(len(debt_metrics_data), 8)))
            
            for i, (key, data) in enumerate(debt_metrics_data.items()):
                values = data['values']
                dates = data['dates']

                # Convert values to millions and sort by date chronologically
                date_value_pairs = list(zip(dates, [v/1e6 for v in values]))
                date_value_pairs.sort(key=lambda x: date_sort_key(x[0]))

                # Always align to the last 12 quarters (even if missing data)
                y_values = []
                for date in debt_timeline_recent:
                    found = False
                    for d, v in date_value_pairs:
                        if d == date:
                            y_values.append(v)
                            found = True
                            break
                    if not found:
                        y_values.append(0)
                x_positions = list(range(len(debt_timeline_recent)))

                if any(y_values):
                    label = data['metric'][:40] if len(data['metric']) <= 40 else data['metric'][:37] + '...'
                    line_styles = ['-', '--', '-.', ':', '-', '--', '-.', ':', '-']
                    line_style = line_styles[i % len(line_styles)]

                    ax2.plot(x_positions, y_values, marker='o', label=label, color=debt_colors[i % len(debt_colors)],
                           linewidth=3, markersize=6, linestyle=line_style, alpha=0.8)
            
            # Plot debt bars
            bar_width = 0.6
            debt_bar_data = {}
            
            # Debt issuance (positive, blue bars)
            for key, data in debt_issuance_data.items():
                for date, value in zip(data['dates'], data['values']):
                    if date in debt_date_to_x:
                        x_pos = debt_date_to_x[date]
                        if x_pos not in debt_bar_data:
                            debt_bar_data[x_pos] = {'issuance': 0, 'repayment': 0}
                        debt_bar_data[x_pos]['issuance'] += value / 1e6
            
            # Debt repayment (negative, orange bars)
            for key, data in debt_repayment_data.items():
                for date, value in zip(data['dates'], data['values']):
                    if date in debt_date_to_x:
                        x_pos = debt_date_to_x[date]
                        if x_pos not in debt_bar_data:
                            debt_bar_data[x_pos] = {'issuance': 0, 'repayment': 0}
                        debt_bar_data[x_pos]['repayment'] += value / 1e6
            
            # Plot debt bars
            if debt_bar_data:
                x_positions = list(debt_bar_data.keys())
                debt_issuance_vals = [debt_bar_data[x]['issuance'] for x in x_positions]
                debt_repayment_vals = [debt_bar_data[x]['repayment'] for x in x_positions]
                
                if any(v != 0 for v in debt_issuance_vals):
                    ax2.bar(x_positions, debt_issuance_vals, bar_width, label='Debt Issuance', color='blue', alpha=0.7)
                if any(v != 0 for v in debt_repayment_vals):
                    ax2.bar(x_positions, debt_repayment_vals, bar_width, label='Debt Repayment', color='orange', alpha=0.7)
            
            # Configure debt chart
            ax2.set_title('Historical Debt Activity (Millions)', fontsize=18, fontweight='bold', pad=30)
            ax2.set_xlabel('Time Period', fontsize=16, fontweight='bold')
            ax2.set_ylabel('Amount (Millions)', fontsize=16, fontweight='bold')
            
            # Fix x-axis for debt
            # Only show the most recent 3 years (12 quarters) on the x-axis
            if len(debt_timeline) > 12:
                debt_timeline_recent = debt_timeline[-12:]
            else:
                debt_timeline_recent = debt_timeline

            max_periods = len(debt_timeline_recent)
            ax2.set_xlim(-0.5, max_periods - 0.5)

            # Set x-ticks and labels for all recent quarters
            tick_positions = list(range(max_periods))
            tick_labels = [debt_timeline_recent[i] for i in tick_positions]
            ax2.set_xticks(tick_positions)
            ax2.set_xticklabels(tick_labels, rotation=45, ha='right')
            
            ax2.legend(bbox_to_anchor=(1.02, 1), loc='upper left', fontsize=12, frameon=True, 
                     fancybox=True, shadow=True)
            ax2.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
            ax2.tick_params(axis='both', which='major', labelsize=12)
            ax2.set_facecolor('#fafafa')
            
            # Save debt chart
            plt.tight_layout()
            debt_chart_path = os.path.join(output_dir, f'{ticker}_debt_analysis.png')
            plt.savefig(debt_chart_path, dpi=300, bbox_inches='tight')
            plt.close(fig2)
            print(f"Debt chart saved to: {debt_chart_path}")
        
        # Print detailed summary to console
        print(f"\n=== {ticker.upper()} SHARES OUTSTANDING SUMMARY ===")
        
        # Group by sheet type for better organization
        balance_sheet_data = {}
        income_statement_data = {}
        other_data = {}
        
        for key, data in shares_data.items():
            sheet = data['sheet'].lower()
            metric = data['metric']
            current = data['values'][0] if data['values'] else 0
            
            if 'balance' in sheet:
                balance_sheet_data[metric] = current
            elif 'income' in sheet:
                income_statement_data[metric] = current
            else:
                other_data[metric] = current
        
        if balance_sheet_data:
            print("\nBalance Sheet (Shares Outstanding):")
            for metric, value in balance_sheet_data.items():
                print(f"  {metric}: {value:,.0f} shares ({value/1e6:.1f}M)")
        
        if income_statement_data:
            print("\nIncome Statement (Weighted Average Shares):")
            for metric, value in income_statement_data.items():
                print(f"  {metric}: {value:,.0f} shares ({value/1e6:.1f}M)")
        
        if other_data:
            print("\nOther Share Metrics:")
            for metric, value in other_data.items():
                print(f"  {metric}: {value:,.0f} shares ({value/1e6:.1f}M)")
        
        # Key insights
        print(f"\n=== KEY INSIGHTS ===")
        if balance_sheet_data and income_statement_data:
            balance_max = max(balance_sheet_data.values()) if balance_sheet_data else 0
            income_max = max(income_statement_data.values()) if income_statement_data else 0
            
            if balance_max > income_max * 1.1:  # More than 10% difference
                print(f"NOTICE: Balance sheet shows {balance_max/1e6:.1f}M shares outstanding")
                print(f"        Income statement shows {income_max/1e6:.1f}M weighted average shares")
                print(f"        Difference: {(balance_max-income_max)/1e6:.1f}M shares ({((balance_max-income_max)/income_max*100):.1f}%)")
                print("        This suggests significant share issuance during reporting periods")
        
        return True
        
    except Exception as e:
        print(f"Error in shares outstanding analysis: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def load_data(ticker=None):
    print("[DEBUG] >>>>> ENTERED load_data in charts.py <<<<<")
    """Load both annual and quarterly CSV data for a specific ticker."""
    try:
        import glob
        import os
        
        # Use provided ticker or detect it
        if not ticker:
            ticker = detect_ticker_symbol()
        
        # Clean ticker for filename
        clean_ticker = ticker.lower().replace('.', '') if ticker and ticker != "TICKER" else None
        
        # Search for annual data files - prioritize specific ticker files
        annual_files = []
        if clean_ticker:
            specific_patterns = [
                f'data/owner_earnings_annual_{clean_ticker}.csv',
                f'owner_earnings_annual_{clean_ticker}.csv',
                f'./data/owner_earnings_annual_{clean_ticker}.csv',
                f'../data/owner_earnings_annual_{clean_ticker}.csv',
                f'marketswimmer/gui/data/owner_earnings_annual_{clean_ticker}.csv'
            ]
            for pattern in specific_patterns:
                files = glob.glob(pattern)
                if files:
                    annual_files.extend(files)
                    print(f"[DEBUG] Found ticker-specific files with pattern '{pattern}': {files}")
                    break  # Use first match for specific ticker
        
        # If no specific files found, search for any files
        if not annual_files:
            general_patterns = [
                'data/owner_earnings_annual_*.csv',
                'owner_earnings_annual_*.csv', 
                './data/owner_earnings_annual_*.csv',
                '../data/owner_earnings_annual_*.csv',
                'marketswimmer/gui/data/owner_earnings_annual_*.csv'
            ]
            
            for pattern in general_patterns:
                files = glob.glob(pattern)
                if files:
                    annual_files.extend(files)
                    print(f"[DEBUG] General pattern '{pattern}' found: {files}")
        
        # Remove duplicates and sort by modification time (most recent first)
        annual_files = list(set(annual_files))
        if annual_files:
            annual_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        
        # Fallback to old filename format
        if not annual_files:
            fallback_patterns = [
                'data/owner_earnings_financials_annual.csv',
                'owner_earnings_financials_annual.csv'
            ]
            for pattern in fallback_patterns:
                files = glob.glob(pattern)
                annual_files.extend(files)
        
        if not annual_files:
            print("[ERROR] No annual data files found in any location")
            print(f"[DEBUG] Current directory contents: {os.listdir('.')}")
            if os.path.exists('data'):
                print(f"[DEBUG] Data directory contents: {os.listdir('data')}")
            return None, None
        
        annual_path = annual_files[0]  # Use the most recent file
        print(f"[DEBUG] Found annual files: {annual_files}")
        print(f"[DEBUG] Using most recent annual file: {annual_path}")
        
        annual_df = pd.read_csv(annual_path)
        # Strip whitespace from all column names for robustness
        annual_df.columns = [col.strip() for col in annual_df.columns]
        # Prefer Non-Bank, else Bank, for 'Owner Earnings'
        if 'Owner Earnings' not in annual_df.columns:
            if 'Owner Earnings (Non-Bank)' in annual_df.columns:
                annual_df['Owner Earnings'] = annual_df['Owner Earnings (Non-Bank)']
            elif 'Owner Earnings (Bank)' in annual_df.columns:
                annual_df['Owner Earnings'] = annual_df['Owner Earnings (Bank)']
        print(f"[DEBUG] Columns in annual_df after loading: {list(annual_df.columns)}")
        if 'Owner Earnings' not in annual_df.columns:
            print("[ERROR] 'Owner Earnings' column is missing after attempted aliasing!")
            print("[DEBUG] Available columns:", list(annual_df.columns))
            raise ValueError("Critical: 'Owner Earnings' column is missing from annual data. Check your CSV headers and aliasing logic.")
        print(f"[OK] Loaded annual data: {len(annual_df)} years from {annual_path}")
        
        # Search for quarterly data files - prioritize specific ticker files
        quarterly_files = []
        if clean_ticker:
            specific_patterns = [
                f'owner_earnings_quarterly_{clean_ticker}.csv',
                f'./data/owner_earnings_quarterly_{clean_ticker}.csv',
                f'../data/owner_earnings_quarterly_{clean_ticker}.csv',
                f'marketswimmer/gui/data/owner_earnings_quarterly_{clean_ticker}.csv'
            ]
            
            for pattern in specific_patterns:
                files = glob.glob(pattern)
                if files:
                    quarterly_files.extend(files)
                    print(f"[DEBUG] Found quarterly ticker-specific files with pattern '{pattern}': {files}")
                    break  # Use first match for specific ticker
        
        # If no specific files found, search for any quarterly files
        if not quarterly_files:
            general_patterns = [
                'data/owner_earnings_quarterly_*.csv',
                'owner_earnings_quarterly_*.csv',
                './data/owner_earnings_quarterly_*.csv',
                '../data/owner_earnings_quarterly_*.csv',
                'marketswimmer/gui/data/owner_earnings_quarterly_*.csv'
            ]
            
            for pattern in general_patterns:
                files = glob.glob(pattern)
                if files:
                    quarterly_files.extend(files)
                    print(f"[DEBUG] Quarterly general pattern '{pattern}' found: {files}")
        
        # Remove duplicates and sort by modification time
        quarterly_files = list(set(quarterly_files))
        if quarterly_files:
            quarterly_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        
        # Fallback to old filename format
        if not quarterly_files:
            fallback_patterns = [
                'data/owner_earnings_financials_quarterly.csv',
                'owner_earnings_financials_quarterly.csv'
            ]
            for pattern in fallback_patterns:
                files = glob.glob(pattern)
                quarterly_files.extend(files)
            
        if not quarterly_files:
            print("[ERROR] No quarterly data files found in any location")
            print(f"[DEBUG] Searched quarterly patterns for ticker: {clean_ticker}")
            return None, None
        
        quarterly_path = quarterly_files[0]  # Use the most recent file
        print(f"[DEBUG] Found quarterly files: {quarterly_files}")
        print(f"[DEBUG] Using most recent quarterly file: {quarterly_path}")
        quarterly_df = pd.read_csv(quarterly_path)
        print(f"[OK] Loaded quarterly data: {len(quarterly_df)} quarters from {quarterly_path}")
        
        return annual_df, quarterly_df
        
    except Exception as e:
        print(f"[ERROR] Error loading data: {e}")
        import traceback
        print(f"[DEBUG] Traceback: {traceback.format_exc()}")
        return None, None
        print(f"[DEBUG] Found quarterly files: {quarterly_files}")
        print(f"[DEBUG] Using most recent quarterly file: {quarterly_path}")
        quarterly_df = pd.read_csv(quarterly_path)
        print(f"[OK] Loaded quarterly data: {len(quarterly_df)} quarters from {quarterly_path}")
        
        return annual_df, quarterly_df
    
    except FileNotFoundError as e:
        print(f"[ERROR] Error loading CSV files: {e}")
        print("[INFO] Make sure to run owner_earnings_fixed.py first to generate the CSV files")
        print("[INFO] CSV files should be in the 'data/' directory")
        return None, None

def prepare_quarterly_data(df):
    """Prepare quarterly data for plotting."""
    # Convert period to datetime for better plotting
    df = df.copy()
    
    print(f"[DEBUG] Raw quarterly data shape: {df.shape}")
    print(f"[DEBUG] Period column sample values: {df['Period'].head().tolist()}")
    print(f"[DEBUG] Period column data types: {df['Period'].dtype}")
    
    # Ensure Period column is string type for string operations
    df['Period'] = df['Period'].astype(str)
    print(f"[DEBUG] Period column after string conversion: {df['Period'].head().tolist()}")
    
    # Check if this is actually annual data masquerading as quarterly data
    period_values = df['Period'].unique()
    is_annual_data = all(len(p) == 4 and p.isdigit() for p in period_values)
    
    if is_annual_data:
        print(f"[WARNING] Detected annual data in quarterly file - treating as annual")
        # This is annual data, so just parse as years
        df['year'] = df['Period'].astype(int)
        df['quarter'] = 2  # Use Q2 as a middle-of-year approximation
        df['date'] = pd.to_datetime(df[['year']].assign(month=7, day=1))  # July 1st
        print(f"[DEBUG] Converted annual-as-quarterly data: {df['date'].head().tolist()}")
    else:
        # Extract year and quarter from Period (format should be like "2024Q1")
        try:
            # Handle different Period formats more robustly
            print(f"[DEBUG] Attempting to parse quarterly Period values: {df['Period'].unique()}")
            
            if df['Period'].str.contains('Q').any():
                # Format like "2024Q1"
                df['year'] = df['Period'].str[:4].astype(int)
                df['quarter'] = df['Period'].str[-1].astype(int)
            elif df['Period'].str.contains('-').any():
                # Format like "2024-Q1" or "Q1-2024"
                # Try to extract 4-digit year and 1-digit quarter
                year_pattern = df['Period'].str.extract(r'(\d{4})')
                quarter_pattern = df['Period'].str.extract(r'Q(\d)')
                df['year'] = year_pattern[0].astype(int)
                df['quarter'] = quarter_pattern[0].astype(int)
            else:
                # Fallback: try to parse as much as possible
                print(f"[WARNING] Unknown Period format, attempting generic parsing")
                # Try to extract any 4-digit number as year
                year_match = df['Period'].str.extract(r'(\d{4})')
                if not year_match[0].isna().all():
                    df['year'] = year_match[0].astype(int)
                else:
                    df['year'] = 2024  # Default year
                
                # Try to extract quarter number
                quarter_match = df['Period'].str.extract(r'(\d)')
                if not quarter_match[0].isna().all():
                    df['quarter'] = quarter_match[0].astype(int)
                else:
                    df['quarter'] = 1  # Default quarter
            
            print(f"[DEBUG] Extracted years: {df['year'].tolist()}")
            print(f"[DEBUG] Extracted quarters: {df['quarter'].tolist()}")
            
            # Validate extracted values
            if df['year'].isna().any() or df['quarter'].isna().any():
                raise ValueError("Failed to extract valid year/quarter values")
            if (df['quarter'] < 1).any() or (df['quarter'] > 4).any():
                print(f"[WARNING] Invalid quarter values found: {df['quarter'].unique()}")
                df['quarter'] = df['quarter'].clip(1, 4)  # Clamp to valid range
                
        except Exception as e:
            print(f"[ERROR] Failed to extract year/quarter: {e}")
            print(f"[DEBUG] Period values causing issues: {df['Period'].unique()}")
            # Create fallback values to prevent complete failure
            df['year'] = 2024
            df['quarter'] = 1
            print(f"[WARNING] Using fallback year/quarter values")
        
        # Create a proper date column
        try:
            df['date'] = pd.to_datetime(df[['year']].assign(month=(df['quarter']-1)*3+1, day=1))
            print(f"[DEBUG] Successfully created date column: {df['date'].head().tolist()}")
        except Exception as e:
            print(f"[ERROR] Failed to create date column: {e}")
            print(f"[DEBUG] Year values: {df['year'].tolist()}")
            print(f"[DEBUG] Quarter values: {df['quarter'].tolist()}")
            # Create a simple date column based on just the year
            df['date'] = pd.to_datetime(df['year'], format='%Y')
            print(f"[WARNING] Using year-only dates: {df['date'].head().tolist()}")
    
    # Convert to millions for better readability - use the actual CSV column names
    financial_cols_map = {
        'Net Income': 'net_income',
        'Depreciation': 'depreciation', 
        'CapEx': 'capex',
        'Working Capital Change': 'working_capital_change',
        'Owner Earnings': 'owner_earnings',
        'Owner Earnings (Bank)': 'owner_earnings_bank',
        'Owner Earnings (Non-Bank)': 'owner_earnings_nonbank'
    }
    for csv_col, standard_col in financial_cols_map.items():
        if csv_col in df.columns:
            df[f'{standard_col}_millions'] = df[csv_col] / 1_000_000

    # Ensure 'owner_earnings_millions' exists for downstream code
    if 'owner_earnings_millions' not in df.columns:
        if 'owner_earnings_bank_millions' in df.columns:
            df['owner_earnings_millions'] = df['owner_earnings_bank_millions']
        elif 'owner_earnings_nonbank_millions' in df.columns:
            df['owner_earnings_millions'] = df['owner_earnings_nonbank_millions']

    # Sort by date for proper chronological plotting
    df = df.sort_values('date')
    return df

def prepare_annual_data(df):
    """Prepare annual data for plotting with robust error handling."""
    df = df.copy()
    
    print(f"[DEBUG] Annual Period column: {df['Period'].head().tolist()}")
    print(f"[DEBUG] Annual Period dtypes: {df['Period'].dtype}")
    
    # Try different date parsing approaches
    try:
        # First try: assume it's just years like "2024"
        df['date'] = pd.to_datetime(df['Period'], format='%Y')
        print(f"[DEBUG] Successfully parsed annual dates as years")
    except ValueError as e:
        print(f"[DEBUG] Year format failed: {e}")
        try:
            # Second try: generic datetime parsing
            df['date'] = pd.to_datetime(df['Period'], errors='coerce')
            print(f"[DEBUG] Successfully parsed annual dates with generic parser")
        except Exception as e2:
            print(f"[ERROR] All annual date parsing failed: {e2}")
            print(f"[DEBUG] Problematic Period values: {df['Period'].unique()}")
            # Create a dummy date column to prevent crashes
            df['date'] = pd.to_datetime('2020-01-01')
            print(f"[WARNING] Using dummy dates for annual data")
    

    # Ensure 'Owner Earnings' column exists for compatibility
    if 'Owner Earnings' not in df.columns:
        if 'Owner Earnings (Bank)' in df.columns:
            df['Owner Earnings'] = df['Owner Earnings (Bank)']
        elif 'Owner Earnings (Non-Bank)' in df.columns:
            df['Owner Earnings'] = df['Owner Earnings (Non-Bank)']

    # Convert to millions for better readability - use the actual CSV column names
    # Support both Bank and Non-Bank columns
    financial_cols_map = {
        'Net Income': 'net_income',
        'Depreciation': 'depreciation', 
        'CapEx': 'capex',
        'Working Capital Change': 'working_capital_change',
        'Owner Earnings (Bank)': 'owner_earnings_bank',
        'Owner Earnings (Non-Bank)': 'owner_earnings_nonbank',
        'Owner Earnings': 'owner_earnings'
    }
    for csv_col, standard_col in financial_cols_map.items():
        if csv_col in df.columns:
            df[f'{standard_col}_millions'] = df[csv_col] / 1_000_000

    # Ensure 'owner_earnings_millions' exists for downstream code
    if 'owner_earnings_millions' not in df.columns:
        if 'owner_earnings_bank_millions' in df.columns:
            df['owner_earnings_millions'] = df['owner_earnings_bank_millions']
        elif 'owner_earnings_nonbank_millions' in df.columns:
            df['owner_earnings_millions'] = df['owner_earnings_nonbank_millions']
        elif 'owner_earnings_millions' not in df.columns and 'owner_earnings_millions' in df:
            # fallback if already present
            pass

    # Sort by date for proper chronological plotting (oldest to newest)
    df = df.sort_values('date')
    return df

def create_owner_earnings_comparison(annual_df, quarterly_df, ticker):
    """Create a comparison chart of annual vs quarterly owner earnings."""
    # Create two sets of charts: Bank and Non-Bank
    figs = []
    for label, col in [("Bank", "owner_earnings_bank_millions"), ("Non-Bank", "owner_earnings_nonbank_millions")]:
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 12))
        # Annual chart
        if col in annual_df.columns:
            annual_df.plot(x='date', y=col, kind='line', 
                           ax=ax1, marker='o', linewidth=2, markersize=6, label=f'Owner Earnings ({label})')
            ax1.axhline(y=0, color='red', linestyle='--', alpha=0.7)
            ax1.set_title(f'{ticker} Annual Owner Earnings ({label})', fontweight='bold', fontsize=16)
            ax1.set_ylabel('Owner Earnings ($ Millions)')
            ax1.set_xlabel('Year')
            ax1.grid(True, alpha=0.3)
            ax1.legend([f'Owner Earnings ({label})', 'Break-even'], loc='upper left')
        # Quarterly chart (limit to most recent 12 quarters, sorted by date)
        if col in quarterly_df.columns:
            quarterly_sorted = quarterly_df.sort_values('date')
            quarterly_recent = quarterly_sorted.tail(12).copy()
            quarterly_recent.plot(x='date', y=col, kind='line', 
                                 ax=ax2, marker='s', linewidth=1.5, markersize=4, label=f'Owner Earnings ({label})', alpha=0.8)
            ax2.axhline(y=0, color='red', linestyle='--', alpha=0.7)
            ax2.set_title(f'{ticker} Quarterly Owner Earnings ({label})', fontweight='bold', fontsize=16)
            ax2.set_ylabel('Owner Earnings ($ Millions)')
            ax2.set_xlabel('Date')
            ax2.grid(True, alpha=0.3)
            ax2.legend([f'Owner Earnings ({label})', 'Break-even'], loc='upper left')
        plt.tight_layout()
        figs.append(fig)
    return figs

def create_components_breakdown(annual_df, quarterly_df, ticker, exclude_working_capital=False):
    """Create waterfall charts showing the components of owner earnings.
    
    Args:
        annual_df: annual data DataFrame
        quarterly_df: quarterly data DataFrame
        ticker: company ticker symbol
        exclude_working_capital: bool, if True excludes working capital (for banks/insurance)
    """
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 14))
    
    # Annual components waterfall
    create_annual_waterfall_chart(ax1, annual_df, ticker, exclude_working_capital)
    
    # Quarterly components (most recent 12 quarters for readability)
    # Sort by date to ensure correct order, then get the last 12 quarters
    quarterly_sorted = quarterly_df.sort_values('date')
    quarterly_recent = quarterly_sorted.tail(12).copy()
    
    # Create waterfall chart for quarterly data
    create_waterfall_chart(ax2, quarterly_recent, ticker, exclude_working_capital)
    
    # Rotate x-axis labels for better readability
    ax2.tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    return fig
    return fig

def create_annual_waterfall_chart(ax, df, ticker, exclude_working_capital=False):
    """Create a waterfall chart showing annual owner earnings components for all years.
    
    Args:
        ax: matplotlib axis
        df: dataframe with owner earnings data
        ticker: company ticker symbol
        exclude_working_capital: bool, if True excludes working capital (for banks/insurance)
    """
    
    # Use all years instead of limiting to recent ones
    recent_years = df.copy()
    
    # Set up the chart dimensions - adjust bar width based on number of years
    n_years = len(recent_years)
    bar_width = max(0.08, min(0.15, 2.0 / n_years))  # Dynamic bar width
    
    # Create positions for each year
    year_positions = np.arange(n_years)
    
    # Colors for each component
    colors = {
        'Net Income': '#2E86AB',
        'Depreciation': '#A23B72', 
        'CapEx': '#F18F01',
        'WC Changes': '#C73E1D',
        'Owner Earnings': '#4CAF50'
    }
    
    # Create grouped waterfall charts for each year
    for i, (_, year) in enumerate(recent_years.iterrows()):
        period = year['Period']

        # Component values
        net_income = year['net_income_millions']
        depreciation = year['depreciation_millions']
        capex = year['capex_millions']
        wc_change = year['working_capital_change_millions']
        owner_earnings = year['owner_earnings_millions']

        # Calculate cumulative positions for waterfall
        cumulative = [0]
        cumulative.append(net_income)
        cumulative.append(cumulative[-1] + depreciation)
        cumulative.append(cumulative[-1] + capex)  # Add CapEx as-is (should be negative)
        if not exclude_working_capital:
            cumulative.append(cumulative[-1] - wc_change)

        # Check that cumulative[-1] matches owner_earnings (allowing for small rounding error)
        expected_oe = cumulative[-1]
        if not np.isclose(expected_oe, owner_earnings, atol=1e-2):
            print(f"[WATERFALL WARNING] Owner Earnings mismatch for {period}: calculated {expected_oe}, reported {owner_earnings}")

        # X position for this year's bars
        x_base = i

        # Net Income (starts from 0)
        ax.bar(x_base - 2*bar_width, net_income, bar_width,
            bottom=0, color=colors['Net Income'], alpha=0.8,
            edgecolor='black', linewidth=0.3,
            label='Net Income' if i == 0 else "")

        # Depreciation (stacks on Net Income)
        ax.bar(x_base - bar_width, depreciation, bar_width,
            bottom=cumulative[1], color=colors['Depreciation'], alpha=0.8,
            edgecolor='black', linewidth=0.3,
            label='+ Depreciation' if i == 0 else "")

        # CapEx (use as-is, should be negative in data)
        ax.bar(x_base, capex, bar_width,  # Use raw value
            bottom=cumulative[2], color=colors['CapEx'], alpha=0.8,
            edgecolor='black', linewidth=0.3,
            label='- CapEx' if i == 0 else "")

        # Working Capital Changes (use as-is, should be positive in data)
        if not exclude_working_capital:
            wc_bar_value = -wc_change  # Subtract positive value
            wc_color = colors['WC Changes'] if wc_bar_value < 0 else '#90EE90'
            ax.bar(x_base + bar_width, wc_bar_value, bar_width,
                bottom=cumulative[3], color=wc_color, alpha=0.8,
                edgecolor='black', linewidth=0.3,
                label='WC Changes' if i == 0 else "")


        oe_x_position = x_base + 2*bar_width
        # Owner Earnings (plot as a total bar from zero)
        oe_color = colors['Owner Earnings'] if owner_earnings >= 0 else '#F44336'
        ax.bar(oe_x_position, owner_earnings, bar_width,
            bottom=0, color=oe_color, alpha=0.8,
            edgecolor='black', linewidth=0.5,
            label='Owner Earnings' if i == 0 else "")

        # Add value labels for Owner Earnings (in billions for annual)
        oe_billions = owner_earnings / 1000
        ax.text(oe_x_position, owner_earnings/2, f'${oe_billions:.1f}B',
            ha='center', va='center', fontweight='bold', fontsize=9, rotation=90)

        # Add connecting line to show the flow to final result
        if owner_earnings >= 0:
            last_cumulative_index = 3 if exclude_working_capital else 4
            ax.plot([x_base + bar_width + bar_width/2, x_base + 2*bar_width - bar_width/2],
                [cumulative[last_cumulative_index], owner_earnings/2], 'k--', alpha=0.3, linewidth=1)
    
    # Formatting
    ax.set_xticks(year_positions)
    ax.set_xticklabels([str(int(y['Period'])) for _, y in recent_years.iterrows()])
    ax.set_title(f'{ticker} Annual Owner Earnings Waterfall - All Years', fontweight='bold', fontsize=16)
    ax.set_ylabel('Amount ($ Millions)')
    
    # Create custom legend to show both positive and negative WC changes and Owner Earnings
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='#2E86AB', alpha=0.8, label='Net Income'),
        Patch(facecolor='#A23B72', alpha=0.8, label='+ Depreciation'),
        Patch(facecolor='#F18F01', alpha=0.8, label='- CapEx'),
    ]
    
    # Only add working capital legend elements if not excluded (i.e., not a bank/insurance)
    if not exclude_working_capital:
        legend_elements.extend([
            Patch(facecolor='#C73E1D', alpha=0.8, label='WC Changes (-)'),
            Patch(facecolor='#90EE90', alpha=0.8, label='WC Changes (+)'),
        ])
    
    legend_elements.extend([
        Patch(facecolor='#4CAF50', alpha=0.8, label='Owner Earnings (+)'),
        Patch(facecolor='#F44336', alpha=0.8, label='Owner Earnings (-)')
    ])
    ax.legend(handles=legend_elements, loc='upper left', fontsize=10)
    
    ax.grid(True, alpha=0.3, axis='y')
    ax.axhline(y=0, color='black', linestyle='-', alpha=0.8)

def create_waterfall_chart(ax, df, ticker, exclude_working_capital=False):
    """Create a waterfall chart showing owner earnings components for all quarters.
    
    Args:
        ax: matplotlib axis
        df: dataframe with owner earnings data
        ticker: company ticker symbol
        exclude_working_capital: bool, if True excludes working capital (for banks/insurance)
    """
    
    # Use all quarters instead of limiting to recent ones
    recent_quarters = df.copy()
    
    # Set up the chart dimensions - adjust bar width based on number of quarters
    n_quarters = len(recent_quarters)
    bar_width = max(0.08, min(0.15, 3.0 / n_quarters))  # Dynamic bar width
    
    # Create positions for each quarter
    quarter_positions = np.arange(n_quarters)
    # We'll use the center of the group of bars for each quarter as the x-tick
    group_centers = []
    
    # Colors for each component
    colors = {
        'Net Income': '#2E86AB',
        'Depreciation': '#A23B72', 
        'CapEx': '#F18F01',
        'WC Changes': '#C73E1D',
        'Owner Earnings': '#4CAF50'
    }
    
    # Create grouped waterfall charts for each quarter
    for i, (_, quarter) in enumerate(recent_quarters.iterrows()):
        period = quarter['Period']

        # Component values
        net_income = quarter['net_income_millions']
        depreciation = quarter['depreciation_millions']
        capex = quarter['capex_millions']
        wc_change = quarter['working_capital_change_millions']
        owner_earnings = quarter['owner_earnings_millions']

        # Calculate cumulative positions for waterfall
        cumulative = [0]
        cumulative.append(net_income)
        cumulative.append(cumulative[-1] + depreciation)
        cumulative.append(cumulative[-1] + capex)  # Add CapEx as-is (should be negative)
        cumulative.append(cumulative[-1] - wc_change)  # Subtract WC change

        # Check that cumulative[-1] matches owner_earnings (allowing for small rounding error)
        expected_oe = cumulative[-1]
        if not np.isclose(expected_oe, owner_earnings, atol=1e-2):
            print(f"[WATERFALL WARNING] Owner Earnings mismatch for {period}: calculated {expected_oe}, reported {owner_earnings}")

        # X position for this quarter's bars
        x_base = i
        # Center of the group for this quarter (middle between first and last bar)
        group_center = x_base + bar_width  # 5 bars: -2, -1, 0, +1, +2*bar_width; center is at +bar_width
        group_centers.append(group_center)

        # Net Income (starts from 0)
        ax.bar(x_base - 2*bar_width, net_income, bar_width,
            bottom=0, color=colors['Net Income'], alpha=0.8,
            edgecolor='black', linewidth=0.3,
            label='Net Income' if i == 0 else "")

        # Depreciation (stacks on Net Income)
        ax.bar(x_base - bar_width, depreciation, bar_width,
            bottom=cumulative[1], color=colors['Depreciation'], alpha=0.8,
            edgecolor='black', linewidth=0.3,
            label='+ Depreciation' if i == 0 else "")

        # CapEx (use as-is, should be negative in data)
        ax.bar(x_base, capex, bar_width,  # Use raw value
            bottom=cumulative[2], color=colors['CapEx'], alpha=0.8,
            edgecolor='black', linewidth=0.3,
            label='- CapEx' if i == 0 else "")

        # Working Capital Changes (use as-is, should be positive in data)
        wc_bar_value = -wc_change  # Subtract positive value
        wc_color = colors['WC Changes'] if wc_bar_value < 0 else '#90EE90'
        ax.bar(x_base + bar_width, wc_bar_value, bar_width,
            bottom=cumulative[3], color=wc_color, alpha=0.8,
            edgecolor='black', linewidth=0.3,
            label='WC Changes' if i == 0 else "")


        # Owner Earnings (plot as a total bar from zero)
        oe_color = colors['Owner Earnings'] if owner_earnings >= 0 else '#F44336'
        ax.bar(x_base + 2*bar_width, owner_earnings, bar_width,
            bottom=0, color=oe_color, alpha=0.8,
            edgecolor='black', linewidth=0.5,
            label='Owner Earnings' if i == 0 else "")

        # Add value labels for Owner Earnings
        ax.text(x_base + 2*bar_width, owner_earnings/2, f'${owner_earnings:,.0f}M',
            ha='center', va='center', fontweight='bold', fontsize=8, rotation=90)

        # Add connecting line to show the flow to final result
        if owner_earnings >= 0:
            last_cumulative_index = 4
            ax.plot([x_base + bar_width + bar_width/2, x_base + 2*bar_width - bar_width/2],
                [cumulative[last_cumulative_index], owner_earnings/2], 'k--', alpha=0.3, linewidth=1)
    
    # Formatting
    ax.set_xticks(group_centers)
    quarter_labels = [q['Period'] for _, q in recent_quarters.iterrows()]
    # Always show all quarter labels, centered
    ax.set_xticklabels(quarter_labels, rotation=45, ha='center')
    
    ax.set_title(f'{ticker} Owner Earnings Waterfall - All Quarters', fontweight='bold', fontsize=14)
    ax.set_ylabel('Amount ($ Millions)')
    
    # Create custom legend to show all components including negative owner earnings
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='#2E86AB', alpha=0.8, label='Net Income'),
        Patch(facecolor='#A23B72', alpha=0.8, label='+ Depreciation'),
        Patch(facecolor='#F18F01', alpha=0.8, label='- CapEx'),
    ]
    
    # Only add working capital legend elements if not excluded (i.e., not a bank/insurance)
    if not exclude_working_capital:
        legend_elements.extend([
            Patch(facecolor='#C73E1D', alpha=0.8, label='WC Changes (-)'),
            Patch(facecolor='#90EE90', alpha=0.8, label='WC Changes (+)'),
        ])
    
    legend_elements.extend([
        Patch(facecolor='#4CAF50', alpha=0.8, label='Owner Earnings (+)'),
        Patch(facecolor='#F44336', alpha=0.8, label='Owner Earnings (-)')
    ])
    ax.legend(handles=legend_elements, loc='upper left', fontsize=9)
    
    ax.grid(True, alpha=0.3, axis='y')
    ax.axhline(y=0, color='black', linestyle='-', alpha=0.8)

def save_and_show_plots(figures, filenames, ticker):
    """Save plots to files and display them."""
    # Ensure we're using non-interactive backend
    matplotlib.use('Agg')
    plt.ioff()
    
    # Create charts directory if it doesn't exist
    charts_dir = "charts"
    if not os.path.exists(charts_dir):
        os.makedirs(charts_dir)
        print(f"[DIR] Created directory: {charts_dir}/")
    
    for fig, filename in zip(figures, filenames):
        # Use the filename as-is since it's already properly formatted
        filepath = os.path.join(charts_dir, f"{filename}.png")
        fig.savefig(filepath, dpi=300, bbox_inches='tight', facecolor='white')
        print(f"[CHART] Saved chart: {filepath}")
        # Close the figure to free memory
        plt.close(fig)
    
    # Don't show interactive plots in GUI mode - just save them
    # plt.show()
    print("\n[OK] All charts displayed and saved!")

def main(ticker=None):
    """Main function to create all visualizations."""
    # Use provided ticker or detect it
    if ticker is None:
        ticker = detect_ticker_symbol()
    
    print(f"{ticker} Owner Earnings Visualization Tool")
    print("=" * 50)
    
    # Detect if this is a bank or insurance company
    is_financial = is_bank_or_insurance(ticker)
    if is_financial:
        print(f"[INFO] Detected {ticker} as bank/insurance - excluding working capital from charts")
    
    # Set up plotting style
    setup_plotting_style()
    
    # Load data with specific ticker
    annual_df, quarterly_df = load_data(ticker)
    if annual_df is None or quarterly_df is None:
        return
    
    # Prepare data
    print("[ANALYSIS] Preparing data for visualization...")
    annual_df = prepare_annual_data(annual_df)
    quarterly_df = prepare_quarterly_data(quarterly_df)
    
    print(f"[CHARTS] Creating visualizations...")
    
    # Create all charts
    figures = []
    filenames = []
    
    # 1. Owner earnings comparison (Bank and Non-Bank)
    figs1 = create_owner_earnings_comparison(annual_df, quarterly_df, ticker)
    for i, fig in enumerate(figs1):
        label = "bank" if i == 0 else "nonbank"
        figures.append(fig)
        filenames.append(f"{ticker.lower().replace('.', '')}_owner_earnings_comparison_{label}")
    
    # 2. Components breakdown (exclude working capital for banks/insurance)
    fig2 = create_components_breakdown(annual_df, quarterly_df, ticker, exclude_working_capital=is_financial)
    figures.append(fig2)
    filenames.append(f"{ticker.lower().replace('.', '')}_earnings_components_breakdown")
    
    # 3. Volatility analysis
    # fig3 = create_volatility_analysis(quarterly_df, ticker)
    # figures.append(fig3)
    # filenames.append(f"{ticker.lower().replace('.', '')}_volatility_analysis")
    
    # Save and show all plots
    save_and_show_plots(figures, filenames, ticker)
    
    # Print summary statistics
    print(f"\n[SUMMARY] {ticker} SUMMARY STATISTICS:")
    print(f"Annual Data Range: {annual_df['Period'].min()} to {annual_df['Period'].max()}")
    print(f"Quarterly Data Range: {quarterly_df['Period'].min()} to {quarterly_df['Period'].max()}")
    print(f"Best Annual Owner Earnings: ${annual_df['owner_earnings_millions'].max():.0f}M ({annual_df.loc[annual_df['owner_earnings_millions'].idxmax(), 'Period']})")
    print(f"Worst Annual Owner Earnings: ${annual_df['owner_earnings_millions'].min():.0f}M ({annual_df.loc[annual_df['owner_earnings_millions'].idxmin(), 'Period']})")
    print(f"Best Quarterly Owner Earnings: ${quarterly_df['owner_earnings_millions'].max():.0f}M ({quarterly_df.loc[quarterly_df['owner_earnings_millions'].idxmax(), 'Period']})")
    print(f"Worst Quarterly Owner Earnings: ${quarterly_df['owner_earnings_millions'].min():.0f}M ({quarterly_df.loc[quarterly_df['owner_earnings_millions'].idxmin(), 'Period']})")
    
    positive_quarters = len(quarterly_df[quarterly_df['owner_earnings_millions'] > 0])
    total_quarters = len(quarterly_df)
    print(f"Positive Quarters: {positive_quarters}/{total_quarters} ({positive_quarters/total_quarters*100:.1f}%)")

    # --- SHARES & DEBT ANALYSIS ---
    print(f"\n[SHARES/DEBT] Creating shares and debt analysis charts...")
    try:
        shares_result = create_shares_outstanding_analysis(ticker)
        if shares_result:
            print(f"[SHARES/DEBT] Shares and debt analysis charts created successfully!")
        else:
            print(f"[SHARES/DEBT] Shares and debt analysis failed or no data available.")
    except Exception as e:
        print(f"[SHARES/DEBT] Error during shares/debt analysis: {e}")

if __name__ == "__main__":
    # Check for command line argument
    ticker = None
    if len(sys.argv) > 1:
        ticker = sys.argv[1].upper()
    main(ticker)
