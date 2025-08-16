import pandas as pd
import os
import sys
import glob
from pathlib import Path

class OwnerEarningsCalculator:
    def _calculate_owner_earnings_value(self, net_income, depreciation, capex, wc_change, *, is_bank=False, is_insurance=False):
        """
        Centralized calculation for owner earnings.
        For banks/insurance: OE = Net Income + Depreciation - |CapEx|
        For non-banks:      OE = Net Income + Depreciation - |CapEx| - WC Change
        """
        if is_bank or is_insurance:
            return net_income + depreciation - abs(capex)
        else:
            return net_income + depreciation - abs(capex) - wc_change
    """
    Calculate Warren Buffett's Owner Earnings from financial statement data.
    
    Owner Earnings = Net Income + Depreciation/Amortization - Capital Expenditures - Working Capital Changes
    """
    
    def __init__(self, xlsx_file_path=None, force_bank=False, force_insurance=False):
        """
        Initialize the calculator.
        
        Args:
            xlsx_file_path (str, optional): Path to the XLSX file with financial data
            force_bank (bool, optional): Force treatment as bank financials
            force_insurance (bool, optional): Force treatment as insurance financials
        """
        self.file_path = xlsx_file_path
        self.company_name = None
        self.income_statement = None
        self.balance_sheet = None
        self.cash_flow = None
        self.owner_earnings_data = {}
        self.force_bank = force_bank  # NEW: Flag to force bank treatment
        self.force_insurance = force_insurance  # NEW: Flag to force insurance treatment
        
        # If file path provided, load immediately for backward compatibility
        if xlsx_file_path:
            self.load_financial_data(xlsx_file_path)
    
    def load_financial_data(self, xlsx_file_path):
        """
        Load financial data from an XLSX file.
        
        Args:
            xlsx_file_path (str): Path to the XLSX file with financial data
        """
        self.file_path = xlsx_file_path
        file_basename = os.path.basename(xlsx_file_path)
        
        # Extract company name and ticker from filename
        if '_' in file_basename:
            parts = file_basename.split('_')
            # For standard format "financials_export_TICKER_date", ticker is at index 2
            if len(parts) >= 3 and parts[0] == "financials" and parts[1] == "export":
                self.ticker = parts[2].upper()
                self.company_name = self.ticker  # Use ticker as company name
            else:
                # Look for ticker in filename (usually after 'export' and before date)
                for part in parts:
                    if 'export' in part.lower():
                        idx = parts.index(part)
                        if idx + 1 < len(parts):
                            self.ticker = parts[idx + 1].upper()
                            self.company_name = self.ticker
                            break
                else:
                    # Fallback: use first part as ticker
                    self.ticker = parts[0].upper() if parts else "UNKNOWN"
                    self.company_name = self.ticker
        else:
            self.company_name = file_basename.split('.')[0]
            self.ticker = self.company_name.upper()
            
        print(f"[COMPANY] Detected: {self.company_name}, Ticker: {getattr(self, 'ticker', 'UNKNOWN')}")
        return self.load_financial_statements()
        
    def load_financial_statements(self):
        """Load all financial statement tabs from the XLSX file."""
        try:
            print(f"[DATA] Loading financial data from: {os.path.basename(self.file_path)}")
            
            # Get all sheet names
            xl_file = pd.ExcelFile(self.file_path)
            sheet_names = xl_file.sheet_names
            print(f"[INFO] Available sheets: {sheet_names}")
            
            # Try to identify sheets by common names - prefer Annual (A) over Quarterly (Q)
            # Look for annual data first, then fall back to quarterly
            income_sheet = (self._find_sheet(sheet_names, ['Income Statement, A']) or 
                           self._find_sheet(sheet_names, ['Income Statement, Q']) or
                           self._find_sheet(sheet_names, ['income', 'profit', 'earnings', 'statement']))
            
            balance_sheet = (self._find_sheet(sheet_names, ['Balance Sheet, A']) or 
                            self._find_sheet(sheet_names, ['Balance Sheet, Q']) or
                            self._find_sheet(sheet_names, ['balance', 'position', 'sheet']))
            
            cashflow_sheet = (self._find_sheet(sheet_names, ['Cash Flow, A']) or 
                             self._find_sheet(sheet_names, ['Cash Flow, Q']) or
                             self._find_sheet(sheet_names, ['cash', 'flow', 'cashflow']))
            
            # Load the sheets
            if income_sheet:
                self.income_statement = pd.read_excel(self.file_path, sheet_name=income_sheet)
                print(f"[OK] Loaded Income Statement: {income_sheet}")
                print(f"   [DATA] Shape: {self.income_statement.shape}")
                data_type = "Annual" if ", A" in income_sheet else "Quarterly" if ", Q" in income_sheet else "Unknown"
                print(f"   [DATE] Data type: {data_type}")
            
            if balance_sheet:
                self.balance_sheet = pd.read_excel(self.file_path, sheet_name=balance_sheet)
                print(f"[OK] Loaded Balance Sheet: {balance_sheet}")
                print(f"   [DATA] Shape: {self.balance_sheet.shape}")
                data_type = "Annual" if ", A" in balance_sheet else "Quarterly" if ", Q" in balance_sheet else "Unknown"
                print(f"   [DATE] Data type: {data_type}")
            
            if cashflow_sheet:
                self.cash_flow = pd.read_excel(self.file_path, sheet_name=cashflow_sheet)
                print(f"[OK] Loaded Cash Flow Statement: {cashflow_sheet}")
                print(f"   [DATA] Shape: {self.cash_flow.shape}")
                data_type = "Annual" if ", A" in cashflow_sheet else "Quarterly" if ", Q" in cashflow_sheet else "Unknown"
                print(f"   [DATE] Data type: {data_type}")
            
            return True
            
        except Exception as e:
            print(f"[ERROR] Error loading financial statements: {e}")
            return False
    
    def load_financial_statements_by_type(self, data_type):
        """Load financial statements of a specific type (Annual or Quarterly)."""
        try:
            print(f"[DATA] Loading {data_type.lower()} financial data from: {os.path.basename(self.file_path)}")
            
            # Get all sheet names
            xl_file = pd.ExcelFile(self.file_path)
            sheet_names = xl_file.sheet_names
            
            # Map data type to sheet suffix
            suffix = ', A' if data_type == 'Annual' else ', Q'
            
            # Look for sheets with the specific suffix
            income_sheet = self._find_sheet(sheet_names, [f'Income Statement{suffix}'])
            balance_sheet = self._find_sheet(sheet_names, [f'Balance Sheet{suffix}'])
            cashflow_sheet = self._find_sheet(sheet_names, [f'Cash Flow{suffix}'])
            
            # Fallback to any income/balance/cashflow sheet if specific type not found
            if not income_sheet:
                income_sheet = self._find_sheet(sheet_names, ['income', 'profit', 'earnings', 'statement'])
            if not balance_sheet:
                balance_sheet = self._find_sheet(sheet_names, ['balance', 'position', 'sheet'])
            if not cashflow_sheet:
                cashflow_sheet = self._find_sheet(sheet_names, ['cash', 'flow', 'cashflow'])
            
            # Load the sheets
            sheets_loaded = 0
            
            if income_sheet:
                self.income_statement = pd.read_excel(self.file_path, sheet_name=income_sheet)
                print(f"[OK] Loaded Income Statement: {income_sheet}")
                print(f"   [DATA] Shape: {self.income_statement.shape}")
                sheets_loaded += 1
            
            if balance_sheet:
                self.balance_sheet = pd.read_excel(self.file_path, sheet_name=balance_sheet)
                print(f"[OK] Loaded Balance Sheet: {balance_sheet}")
                print(f"   [DATA] Shape: {self.balance_sheet.shape}")
                sheets_loaded += 1
            
            if cashflow_sheet:
                self.cash_flow = pd.read_excel(self.file_path, sheet_name=cashflow_sheet)
                print(f"[OK] Loaded Cash Flow Statement: {cashflow_sheet}")
                print(f"   [DATA] Shape: {self.cash_flow.shape}")
                sheets_loaded += 1
            
            return sheets_loaded >= 2  # Need at least 2 statements for analysis
            
        except Exception as e:
            print(f"[ERROR] Error loading {data_type.lower()} financial statements: {e}")
            return False
    
    def _find_sheet(self, sheet_names, keywords):
        """Find sheet name that contains any of the keywords."""
        for sheet in sheet_names:
            for keyword in keywords:
                if keyword.lower() in sheet.lower():
                    return sheet
        return None
    
    def _quarter_to_number(self, month_name):
        """Convert month name to quarter number."""
        if month_name.startswith('Dec'):
            return 4
        elif month_name.startswith('Sep'):
            return 3
        elif month_name.startswith('Jun'):
            return 2
        elif month_name.startswith('Mar'):
            return 1
        else:
            return 1  # Default fallback
    
    def debug_financial_data(self):
        """Print available financial line items for debugging."""
        print(f"\n[SEARCH] DEBUG: Available financial line items...")
        
        if self.income_statement is not None:
            print(f"\n[DATA] INCOME STATEMENT ({self.income_statement.shape}):")
            print(f"   Columns: {list(self.income_statement.columns)}")
            print(f"   First few rows of first column:")
            try:
                first_col = self.income_statement.iloc[:, 0]
                for i, item in enumerate(first_col.head(15)):
                    if pd.notna(item):
                        print(f"   {i}: {item}")
            except Exception as e:
                print(f"   Error reading income statement: {e}")
        
        if self.cash_flow is not None:
            print(f"\n[MONEY] CASH FLOW STATEMENT ({self.cash_flow.shape}):")
            print(f"   Columns: {list(self.cash_flow.columns)}")
            print(f"   First few rows of first column:")
            try:
                first_col = self.cash_flow.iloc[:, 0]
                for i, item in enumerate(first_col.head(15)):
                    if pd.notna(item):
                        print(f"   {i}: {item}")
            except Exception as e:
                print(f"   Error reading cash flow: {e}")
        
        if self.balance_sheet is not None:
            print(f"\n[INFO] BALANCE SHEET ({self.balance_sheet.shape}):")
            print(f"   Columns: {list(self.balance_sheet.columns)}")
            print(f"   First few rows of first column:")
            try:
                first_col = self.balance_sheet.iloc[:, 0]
                for i, item in enumerate(first_col.head(15)):
                    if pd.notna(item):
                        print(f"   {i}: {item}")
            except Exception as e:
                print(f"   Error reading balance sheet: {e}")

    def _find_financial_item(self, df, search_terms, years_to_extract=40):
        """
        Find a financial line item in a dataframe and extract values for recent years.
        
        Args:
            df: DataFrame to search
            search_terms: List of terms to search for in the first column
            years_to_extract: Number of recent periods to extract (40 for ~10 years quarterly)
        
        Returns:
            dict: Period -> Value mapping
        """
        if df is None or df.empty:
            return {}
        
        print(f"   [SEARCH] Searching for: {search_terms}")
        
        # Try different approaches to find the data
        # Approach 1: Use first column as index
        try:
            search_df = df.copy()
            if len(search_df.columns) > 0:
                search_df = search_df.set_index(search_df.columns[0])
        except:
            search_df = df.copy()
        
        # Search for the item
        for search_term in search_terms:
            print(f"      Looking for: '{search_term}'")
            
            # Try exact match first
            for idx in search_df.index:
                if pd.notna(idx) and search_term.lower() in str(idx).lower():
                    print(f"      [OK] Found match: '{idx}'")
                    
                    # Found the row, extract recent years
                    row_data = search_df.loc[idx]
                    
                    # Get year columns - handle quarterly data like "Jun '25", "Dec '24", etc.
                    year_cols = []
                    for col in search_df.columns:
                        col_str = str(col)
                        try:
                            # Handle StockRow quarterly format like "Dec '24", "Jun '25", etc.
                            if "'" in col_str:
                                parts = col_str.split("'")
                                if len(parts) == 2:
                                    month_part = parts[0].strip()
                                    year_str = parts[1].strip()
                                    
                                    if len(year_str) == 2 and year_str.isdigit():
                                        # Convert 2-digit year to 4-digit
                                        year_int = int(year_str)
                                        if year_int <= 30:  # Assume 00-30 means 2000-2030
                                            year = 2000 + year_int
                                        else:  # 31-99 means 1931-1999
                                            year = 1900 + year_int
                                        
                                        # For quarterly data, we'll use the year-end quarters (Dec) 
                                        # as the primary annual data points, but include all quarters
                                        quarter_priority = 0
                                        if month_part.startswith('Dec'):
                                            quarter_priority = 4  # Highest priority for year-end
                                        elif month_part.startswith('Sep'):
                                            quarter_priority = 3  # Q3
                                        elif month_part.startswith('Jun'):
                                            quarter_priority = 2  # Q2
                                        elif month_part.startswith('Mar'):
                                            quarter_priority = 1  # Q1
                                        
                                        year_cols.append((col, year, quarter_priority, month_part))
                                        continue
                            
                            # Handle other year formats
                            if any(char.isdigit() for char in col_str):
                                # Extract 4-digit year from column name
                                year_match = None
                                for part in col_str.split():
                                    if len(part) == 4 and part.isdigit():
                                        year = int(part)
                                        if 2010 <= year <= 2030:
                                            year_match = year
                                            break
                                
                                if year_match:
                                    year_cols.append((col, year_match, 5, "Annual"))  # Highest priority for annual
                                    continue
                                
                                # Try to extract year from beginning of string
                                if len(col_str) >= 4 and col_str[:4].isdigit():
                                    year = int(col_str[:4])
                                    if 2010 <= year <= 2030:
                                        year_cols.append((col, year, 5, "Annual"))
                                        continue
                        except:
                            continue
                    
                    # Sort by year (most recent first), then by quarter priority (Dec quarters first)
                    year_cols.sort(key=lambda x: (x[1], x[2]), reverse=True)
                    
                    print(f"      [DATES] Found year columns: {[(f'{col}({year}-{quarter})' if len(col_data) > 3 else f'{col}({year})') for col_data in year_cols[:10] for col, year, priority, quarter in [col_data]]}")
                    
                    # Extract values for recent years/quarters
                    result = {}
                    processed_periods = set()
                    
                    for col, year, priority, period in year_cols:
                        try:
                            value = row_data[col]
                            if pd.notna(value):
                                # Convert to float if possible
                                if isinstance(value, str):
                                    # Clean up the value - remove commas, parentheses, etc.
                                    clean_value = value.replace(',', '').replace('$', '').strip()
                                    
                                    # Handle negative values in parentheses
                                    if clean_value.startswith('(') and clean_value.endswith(')'):
                                        clean_value = '-' + clean_value[1:-1]
                                    
                                    # Try to convert to float
                                    try:
                                        numeric_value = float(clean_value)
                                    except ValueError:
                                        continue
                                else:
                                    # Already numeric
                                    numeric_value = float(value)
                                
                                # Create proper period key
                                if hasattr(self, 'preferred_data_type') and self.preferred_data_type == 'Quarterly':
                                    # For quarterly data, use full quarter identifier
                                    period_key = f"{year}Q{self._quarter_to_number(period)}" if period != "Annual" else year
                                else:
                                    # For annual data, use just the year
                                    period_key = year
                                
                                if period_key not in processed_periods:
                                    result[period_key] = numeric_value
                                    processed_periods.add(period_key)
                                    
                                    # Stop after we have enough periods
                                    if len(processed_periods) >= years_to_extract:
                                        break
                                        
                        except Exception as e:
                            print(f"      [WARNING]  Error processing {col}: {e}")
                            continue
                    
                    if result:
                        print(f"      [CHART] Extracted data: {result}")
                        return result
                    else:
                        print(f"      [ERROR] No valid numeric data found")
        
        print(f"      [ERROR] No matches found for any search terms")
        return {}
    
    def extract_owner_earnings_components(self):
        """Extract all components needed for owner earnings calculation."""
        print(f"\n[SEARCH] Extracting Owner Earnings components for {self.company_name}...")
        
        # Determine how many periods to extract based on data type
        if hasattr(self, 'preferred_data_type') and self.preferred_data_type == 'Quarterly':
            periods_to_extract = 40  # About 10 years of quarterly data
        else:
            periods_to_extract = 10  # 10 years of annual data
        
        # Net Income (from Income Statement)
        net_income_terms = [
            'net income', 'net earnings', 'profit after tax', 'net profit',
            'income from continuing operations', 'earnings'
        ]
        net_income = self._find_financial_item(self.income_statement, net_income_terms, periods_to_extract)
        
        # Operating Cash Flow (from Cash Flow Statement) - NEW for alternative methods
        operating_cash_flow_terms = [
            'cash flow from operating activities', 'operating cash flow', 'net cash from operations',
            'cash flow from operations', 'operating activities', 'cash from operations'
        ]
        operating_cash_flow = self._find_financial_item(self.cash_flow, operating_cash_flow_terms, periods_to_extract)
        
        # Depreciation & Amortization (from Cash Flow Statement or Income Statement)
        depreciation_terms = [
            'depreciation', 'amortization', 'depreciation and amortization',
            'depletion', 'depreciation & amortization'
        ]
        depreciation = self._find_financial_item(self.cash_flow, depreciation_terms, periods_to_extract)
        if not depreciation:
            depreciation = self._find_financial_item(self.income_statement, depreciation_terms, periods_to_extract)
        
        # Capital Expenditures (from Cash Flow Statement)
        capex_terms = [
            'capital expenditures', 'capex', 'capital expenditure',
            'purchase of property', 'investments in property', 'additions to property'
        ]
        capex = self._find_financial_item(self.cash_flow, capex_terms, periods_to_extract)
        
        # Working Capital Changes - try multiple approaches
        working_capital_change = {}
        
        # Method 1: Direct working capital line item
        working_capital_terms = [
            'working capital', 'change in working capital', 'changes in working capital',
            'working capital changes', 'change in net working capital'
        ]
        working_capital_change = self._find_financial_item(self.cash_flow, working_capital_terms, periods_to_extract)
        
        # Method 2: Calculate from balance sheet (more accurate)
        if not working_capital_change and self.balance_sheet is not None:
            print(f"   [TIP] Calculating working capital changes from balance sheet...")
            working_capital_change = self._calculate_working_capital_from_balance_sheet(periods_to_extract)
        
        # Method 3: If still not found, calculate from cash flow components
        if not working_capital_change:
            print(f"   [TIP] Direct working capital not found, calculating from cash flow components...")
            
            # Get individual working capital components
            receivables_change = self._find_financial_item(self.cash_flow, 
                ['accounts receivable', 'receivables change', 'change in receivables'], periods_to_extract)
            
            inventory_change = self._find_financial_item(self.cash_flow, 
                ['inventory', 'change in inventory', 'change in inventories', 'inventories'], periods_to_extract)
            
            payables_change = self._find_financial_item(self.cash_flow, 
                ['accounts payable', 'payables change', 'change in payables', 'change in payables and accrued'], periods_to_extract)
            
            # Calculate working capital change if we have the components
            if receivables_change or inventory_change or payables_change:
                print(f"   [DATA] Found working capital components:")
                if receivables_change:
                    print(f"      - Receivables changes: {receivables_change}")
                if inventory_change:
                    print(f"      - Inventory changes: {inventory_change}")
                if payables_change:
                    print(f"      - Payables changes: {payables_change}")
                
                # Calculate combined working capital change
                # Note: Increases in receivables/inventory are negative for cash flow
                # Increases in payables are positive for cash flow
                all_years = set()
                if receivables_change:
                    all_years.update(receivables_change.keys())
                if inventory_change:
                    all_years.update(inventory_change.keys())
                if payables_change:
                    all_years.update(payables_change.keys())
                
                for year in all_years:
                    wc_change = 0
                    components = []
                    
                    if receivables_change and year in receivables_change:
                        wc_change += receivables_change[year]
                        components.append(f"Receivables: {receivables_change[year]:,.0f}")
                    
                    if inventory_change and year in inventory_change:
                        wc_change += inventory_change[year]
                        components.append(f"Inventory: {inventory_change[year]:,.0f}")
                    
                    if payables_change and year in payables_change:
                        wc_change += payables_change[year]
                        components.append(f"Payables: {payables_change[year]:,.0f}")
                    
                    working_capital_change[year] = wc_change
                    print(f"      [YEAR] {year}: {' + '.join(components)} = ${wc_change:,.0f}")
        
        # Store the components
        self.owner_earnings_data = {
            'net_income': net_income,
            'operating_cash_flow': operating_cash_flow,  # NEW: For alternative methods
            'depreciation': depreciation,
            'capex': capex,
            'working_capital_change': working_capital_change
        }
        
        return self.owner_earnings_data
    
    def _calculate_working_capital_from_balance_sheet(self, periods_to_extract=40):
        """
        Calculate working capital changes from balance sheet data.
        Working Capital = Current Assets - Current Liabilities
        """
        print(f"   [DATA] Extracting working capital components from balance sheet...")
        
        # Find current assets and current liabilities
        current_assets = self._find_financial_item(self.balance_sheet, 
            ['total current assets', 'current assets'], periods_to_extract)
        
        current_liabilities = self._find_financial_item(self.balance_sheet, 
            ['total current liabilities', 'current liabilities'], periods_to_extract)
        
        if not current_assets and not current_liabilities:
            print(f"   [ERROR] Could not find current assets or liabilities in balance sheet")
            return {}
        
        # Calculate working capital for each year
        working_capital_levels = {}
        all_years = set()
        
        if current_assets:
            all_years.update(current_assets.keys())
            print(f"   [CHART] Current Assets: {current_assets}")
        
        if current_liabilities:
            all_years.update(current_liabilities.keys())
            print(f"   [DECLINE] Current Liabilities: {current_liabilities}")
        
        # Calculate working capital level for each year
        for year in all_years:
            assets = current_assets.get(year, 0) if current_assets else 0
            liabilities = current_liabilities.get(year, 0) if current_liabilities else 0
            working_capital_levels[year] = assets - liabilities
        
        print(f"   [MONEY] Working Capital Levels: {working_capital_levels}")
        
        # Also extract long-term debt to check for debt restructuring
        print(f"\n   [SEARCH] DEBT ANALYSIS FOR RESTRUCTURING CHECK:")
        debt_search_terms = ['long term debt', 'long-term debt', 'total debt', 'debt total']
        
        debt_data = None
        for search_term in debt_search_terms:
            debt_data = self._find_financial_item(self.balance_sheet, [search_term], periods_to_extract)
            if debt_data:
                print(f"   [DATA] Long-term Debt Levels: {debt_data}")
                # Calculate debt changes (limit display to avoid clutter)
                debt_periods = sorted(debt_data.keys())
                for i in range(1, min(len(debt_periods), 8)):  # Show max 7 periods to avoid clutter
                    prev_period = debt_periods[i-1]
                    curr_period = debt_periods[i]
                    debt_change = debt_data[curr_period] - debt_data[prev_period]
                    print(f"   [CREDIT] {curr_period}: Debt change from ${debt_data[prev_period]:,.0f} to ${debt_data[curr_period]:,.0f} = ${debt_change:,.0f}")
                break
        
        if not debt_data:
            print("   [ERROR] Could not find long-term debt information")
        
        print(f"\n   [DATA] WORKING CAPITAL CHANGES:")
        working_capital_changes = {}
        sorted_years = sorted(working_capital_levels.keys())
        
        for i in range(1, len(sorted_years)):
            current_year = sorted_years[i]
            previous_year = sorted_years[i-1]
            
            current_wc = working_capital_levels[current_year]
            previous_wc = working_capital_levels[previous_year]
            
            # Change in working capital (positive when working capital increases)
            wc_change = (current_wc - previous_wc)  # Positive when working capital increases
            working_capital_changes[current_year] = wc_change
            
            print(f"   [YEAR] {current_year}: WC change from ${previous_wc:,.0f} to ${current_wc:,.0f} = ${wc_change:,.0f}")
        
        return working_capital_changes

    def _detect_insurance_company(self):
        """
        Detect if this appears to be an insurance company based on financial patterns.

        Returns:
            bool: True if appears to be insurance company
        """
        # Check for typical insurance company indicators
        indicators = 0

        # 1. Company name contains insurance-related terms
        if self.company_name:
            insurance_terms = ['insurance', 'life', 'health', 'casualty', 'assurance', 'reinsurance', 'lnc']
            company_lower = self.company_name.lower()
            for term in insurance_terms:
                if term in company_lower:
                    indicators += 1
                    print(f"   [DETECT] Found insurance term '{term}' in company name")
                    break

        # 2. Ticker symbol indicates insurance (LNC, AIG, MET, etc.)
        if hasattr(self, 'ticker') and self.ticker:
            insurance_tickers = ['lnc', 'aig', 'met', 'pru', 'afl', 'unh', 'hum', 'ci']
            if self.ticker.lower() in insurance_tickers:
                indicators += 1
                print(f"   [DETECT] Insurance ticker detected: {self.ticker}")

        # 3. Very large working capital changes relative to net income (typical of insurance reserves)
        if hasattr(self, 'owner_earnings_data') and self.owner_earnings_data:
            wc_changes = self.owner_earnings_data.get('working_capital_change', {})
            net_incomes = self.owner_earnings_data.get('net_income', {})
            
            if wc_changes and net_incomes:
                large_wc_count = 0
                total_years = len(wc_changes)
                
                for year in wc_changes:
                    wc_change = abs(wc_changes.get(year, 0))
                    net_income = abs(net_incomes.get(year, 1))  # Avoid division by zero
                    
                    if net_income > 0 and wc_change > 2 * net_income:  # WC change > 2x net income
                        large_wc_count += 1
                
                if total_years > 0 and large_wc_count / total_years > 0.3:  # 30% of years
                    indicators += 1
                    print(f"   [DETECT] Large working capital pattern detected ({large_wc_count}/{total_years} years)")

        return indicators >= 2  # Need 2+ indicators to classify as insurance company

    def _detect_bank(self):
        """
        Detect if this appears to be a bank based on financial patterns and identifiers.

        Returns:
            bool: True if appears to be a bank
        """
        # Check for typical bank indicators
        indicators = 0

        # 1. Company name contains banking-related terms
        if self.company_name:
            banking_terms = ['bank', 'bancorp', 'financial', 'credit union', 'savings', 'trust', 'bancshares']
            company_lower = self.company_name.lower()
            for term in banking_terms:
                if term in company_lower:
                    indicators += 1
                    print(f"   [DETECT] Found banking term '{term}' in company name")
                    break

        # 2. Ticker symbol indicates banking (common bank tickers)
        if hasattr(self, 'ticker') and self.ticker:
            bank_tickers = ['jpm', 'bac', 'wfc', 'c', 'gs', 'ms', 'usb', 'pnc', 'td', 'bk', 'tfc', 'cof', 'schw', 'zion', 'rf', 'hban', 'fitb', 'mtb', 'stl', 'cma']
            if self.ticker.lower() in bank_tickers:
                indicators += 1
                print(f"   [DETECT] Banking ticker detected: {self.ticker}")

        # 3. Massive working capital changes (typical of banks due to deposits/loans)
        if hasattr(self, 'owner_earnings_data') and self.owner_earnings_data:
            wc_changes = self.owner_earnings_data.get('working_capital_change', {})
            net_incomes = self.owner_earnings_data.get('net_income', {})
            
            if wc_changes and net_incomes:
                large_wc_count = 0
                total_years = len(wc_changes)
                
                for year in wc_changes:
                    wc_change = abs(wc_changes.get(year, 0))
                    net_income = abs(net_incomes.get(year, 1))  # Avoid division by zero
                    
                    # Banks often have WC changes 5-10x larger than net income
                    if net_income > 0 and wc_change > 5 * net_income:
                        large_wc_count += 1
                
                if total_years > 0 and large_wc_count / total_years > 0.5:  # 50% of years
                    indicators += 1
                    print(f"   [DETECT] Banking working capital pattern detected ({large_wc_count}/{total_years} years)")

        # 4. Very low CapEx relative to income (banks don't need much physical capital)
        if hasattr(self, 'owner_earnings_data') and self.owner_earnings_data:
            capex_data = self.owner_earnings_data.get('capex', {})
            net_incomes = self.owner_earnings_data.get('net_income', {})
            
            if capex_data and net_incomes:
                low_capex_count = 0
                total_years = len(capex_data)
                
                for year in capex_data:
                    capex = abs(capex_data.get(year, 0))
                    net_income = abs(net_incomes.get(year, 1))
                    
                    # Banks typically have CapEx < 20% of net income
                    if net_income > 0 and capex < 0.2 * net_income:
                        low_capex_count += 1
                
                if total_years > 0 and low_capex_count / total_years > 0.6:  # 60% of years
                    indicators += 1
                    print(f"   [DETECT] Banking low-CapEx pattern detected ({low_capex_count}/{total_years} years)")

        return indicators >= 2  # Need 2+ indicators to classify as bank
        """
        Detect if this appears to be an insurance company based on financial patterns.
        
        Returns:
            bool: True if appears to be insurance company
        """
        # Check for typical insurance company indicators
        indicators = 0
        
        # 1. Company name contains insurance-related terms
        if self.company_name:
            insurance_terms = ['insurance', 'life', 'health', 'casualty', 'assurance', 'reinsurance', 'lnc']
            company_lower = self.company_name.lower()
            for term in insurance_terms:
                if term in company_lower:
                    indicators += 1
                    print(f"   [DETECT] Found insurance term '{term}' in company name")
                    break
        
        # 2. Ticker symbol indicates insurance (LNC, AIG, MET, etc.)
        if hasattr(self, 'ticker') and self.ticker:
            insurance_tickers = ['lnc', 'aig', 'met', 'pru', 'afl', 'unh', 'hum', 'ci']
            if self.ticker.lower() in insurance_tickers:
                indicators += 1
                print(f"   [DETECT] Insurance ticker detected: {self.ticker}")
        
        # 3. Very large working capital changes relative to net income (typical of insurance reserves)
        if hasattr(self, 'owner_earnings_data') and self.owner_earnings_data:
            wc_changes = self.owner_earnings_data.get('working_capital_change', {})
            net_incomes = self.owner_earnings_data.get('net_income', {})
            
            if wc_changes and net_incomes:
                # Check if working capital changes are often larger than net income
                large_wc_count = 0
                total_comparisons = 0
                
                for year in wc_changes:
                    if year in net_incomes:
                        wc = abs(wc_changes[year])
                        ni = abs(net_incomes[year])
                        if ni > 0 and wc > ni * 2:  # WC change > 2x net income
                            large_wc_count += 1
                        total_comparisons += 1
                
                if total_comparisons > 0 and large_wc_count / total_comparisons > 0.5:
                    indicators += 1
                    print(f"   [DETECT] Large working capital pattern detected ({large_wc_count}/{total_comparisons} years)")
        
        # 4. Minimal capital expenditures (insurance companies don't need much CapEx)
        if hasattr(self, 'owner_earnings_data') and self.owner_earnings_data:
            capex_data = self.owner_earnings_data.get('capex', {})
            net_incomes = self.owner_earnings_data.get('net_income', {})
            
            if capex_data and net_incomes:
                low_capex_count = 0
                total_comparisons = 0
                
                for year in capex_data:
                    if year in net_incomes:
                        capex = abs(capex_data[year])
                        ni = abs(net_incomes[year])
                        if ni > 0 and capex < ni * 0.1:  # CapEx < 10% of net income
                            low_capex_count += 1
                        total_comparisons += 1
                
                if total_comparisons > 0 and low_capex_count / total_comparisons > 0.7:
                    indicators += 1
                    print(f"   [DETECT] Low capital expenditure pattern detected")
        
        # If 2 or more indicators, likely an insurance company
        is_insurance = indicators >= 2
        
        if is_insurance:
            print(f"   [DETECT] Insurance company detected ({indicators} indicators)")
            print(f"   [INSURANCE] For insurance companies, working capital changes reflect policy reserves and float")
            print(f"   [INSURANCE] Using Owner Earnings ≈ Net Income + Depreciation for valuation")
        else:
            print(f"   [DETECT] Traditional company detected ({indicators} indicators)")
        
        return is_insurance

    def calculate_owner_earnings(self):
        """Calculate owner earnings for each available year."""
        if not self.owner_earnings_data:
            self.extract_owner_earnings_components()
        
        print(f"\n[MONEY] Calculating Owner Earnings for {self.company_name}...")
        
        # Get all available years
        all_years = set()
        for component in self.owner_earnings_data.values():
            all_years.update(component.keys())
        
        owner_earnings = {}
        
        for year in sorted(all_years, reverse=True):
            try:
                # Get components for this year
                net_income = self.owner_earnings_data.get('net_income', {}).get(year, 0)
                depreciation = self.owner_earnings_data.get('depreciation', {}).get(year, 0)
                capex = self.owner_earnings_data.get('capex', {}).get(year, 0)
                wc_change = self.owner_earnings_data.get('working_capital_change', {}).get(year, 0)

                # Determine calculation path
                if self.force_bank or self.force_insurance:
                    owner_earnings_value = self._calculate_owner_earnings_value(
                        net_income, depreciation, capex, wc_change,
                        is_bank=self.force_bank, is_insurance=self.force_insurance
                    )
                    if self.force_bank:
                        print(f"   [BANK] Forced banking methodology (excluding working capital changes)")
                    if self.force_insurance:
                        print(f"   [INSURANCE] Forced insurance methodology (excluding working capital changes)")
                else:
                    is_insurance_company = self._detect_insurance_company()
                    is_bank = self._detect_bank()
                    owner_earnings_value = self._calculate_owner_earnings_value(
                        net_income, depreciation, capex, wc_change,
                        is_bank=is_bank, is_insurance=is_insurance_company
                    )
                    if is_insurance_company:
                        print(f"   [INSURANCE] Using insurance company methodology (excluding working capital changes)")
                    elif is_bank:
                        print(f"   [BANK] Using banking methodology (excluding working capital changes)")

                owner_earnings[year] = {
                    'net_income': net_income,
                    'depreciation': depreciation,
                    'capex': capex,
                    'working_capital_change': wc_change,
                    'owner_earnings': owner_earnings_value
                }

            except Exception as e:
                print(f"[WARNING]  Error calculating owner earnings for {year}: {e}")
                continue
        
        return owner_earnings
    
    def calculate_alternative_owner_earnings_methods(self):
        """
        Calculate Owner Earnings using multiple methodologies for comparison.
        
        Returns a dictionary with different calculation methods:
        1. Traditional Method: Net Income + Depreciation - CapEx - Working Capital Changes
        2. Operating Cash Flow Method: Operating Cash Flow - CapEx
        3. Free Cash Flow Method: Operating Cash Flow - CapEx (simplified)
        
        This provides multiple perspectives on the true cash generation of the business.
        """
        if not self.owner_earnings_data:
            self.extract_owner_earnings_components()
        
        print(f"\n[ALTERNATIVE] Calculating Alternative Owner Earnings Methods for {self.company_name}...")
        print(f"[INFO] These methods provide different perspectives on cash generation")
        
        # Get all available years
        all_years = set()
        for component in self.owner_earnings_data.values():
            if component:  # Check if component exists
                all_years.update(component.keys())
        
        alternative_methods = {}
        
        for year in sorted(all_years, reverse=True):
            try:
                # Get components for this year
                net_income = self.owner_earnings_data.get('net_income', {}).get(year, 0)
                operating_cash_flow = self.owner_earnings_data.get('operating_cash_flow', {}).get(year, 0)
                depreciation = self.owner_earnings_data.get('depreciation', {}).get(year, 0)
                capex = self.owner_earnings_data.get('capex', {}).get(year, 0)
                wc_change = self.owner_earnings_data.get('working_capital_change', {}).get(year, 0)
                
                # Check if this appears to be an insurance company or bank
                is_insurance_company = self._detect_insurance_company()
                is_bank = self._detect_bank()
                
                year_methods = {}
                
                # Method 1: Traditional Buffett Formula
                if is_insurance_company:
                    traditional_oe = net_income + depreciation - abs(capex)
                    method_note = "Insurance methodology (excludes working capital)"
                elif is_bank:
                    traditional_oe = net_income + depreciation - abs(capex)
                    method_note = "Banking methodology (excludes working capital)"
                else:
                    traditional_oe = net_income + depreciation - abs(capex) - wc_change
                    method_note = "Standard methodology"
                
                year_methods['traditional'] = {
                    'value': traditional_oe,
                    'method': 'Net Income + Depreciation - CapEx - Working Capital Changes',
                    'note': method_note,
                    'components': {
                        'net_income': net_income,
                        'depreciation': depreciation,
                        'capex': capex,
                        'working_capital_change': wc_change
                    }
                }
                
                # Method 2: Operating Cash Flow Method (Buffett's alternative approach)
                if operating_cash_flow != 0:
                    ocf_oe = operating_cash_flow - abs(capex)
                    year_methods['operating_cash_flow'] = {
                        'value': ocf_oe,
                        'method': 'Operating Cash Flow - CapEx',
                        'note': 'Uses actual cash flow from operations',
                        'components': {
                            'operating_cash_flow': operating_cash_flow,
                            'capex': capex
                        }
                    }
                
                # Method 3: Free Cash Flow Method (commonly used alternative)
                if operating_cash_flow != 0:
                    fcf_oe = operating_cash_flow - abs(capex)  # Same as OCF method for simplicity
                    year_methods['free_cash_flow'] = {
                        'value': fcf_oe,
                        'method': 'Free Cash Flow (Operating Cash Flow - CapEx)',
                        'note': 'Standard free cash flow definition',
                        'components': {
                            'operating_cash_flow': operating_cash_flow,
                            'capex': capex
                        }
                    }
                
                alternative_methods[year] = year_methods
                
            except Exception as e:
                print(f"[WARNING] Error calculating alternative methods for {year}: {e}")
                continue
        
        return alternative_methods
    
    def print_alternative_methods_analysis(self):
        """Print a comprehensive comparison of alternative Owner Earnings methods."""
        alternative_methods = self.calculate_alternative_owner_earnings_methods()
        
        if not alternative_methods:
            print("[ERROR] No alternative methods data could be calculated.")
            return
        
        print(f"\n" + "=" * 80)
        print(f"[ALTERNATIVE] OWNER EARNINGS METHODS COMPARISON - {self.company_name.upper()}")
        print("=" * 80)
        
        print(f"\n[METHODOLOGY] Three Approaches to Owner Earnings:")
        print(f"1. TRADITIONAL: Net Income + Depreciation - CapEx - Working Capital Changes")
        print(f"2. OPERATING CASH FLOW: Operating Cash Flow - CapEx")
        print(f"3. FREE CASH FLOW: Operating Cash Flow - CapEx (alternative perspective)")
        print(f"\nWarren Buffett has discussed both approaches depending on the business type.")
        
        # Show detailed comparison by year
        print(f"\n[COMPARISON] YEAR-BY-YEAR BREAKDOWN:")
        print("-" * 80)
        
        for year in sorted(alternative_methods.keys(), reverse=True):
            year_data = alternative_methods[year]
            print(f"\n[YEAR] {year}:")
            
            for method_name, method_data in year_data.items():
                value = method_data['value']
                method_desc = method_data['method']
                note = method_data.get('note', '')
                
                print(f"   {method_name.upper():20s}: ${value:>15,.0f}  ({method_desc})")
                if note:
                    print(f"   {' '*20}   Note: {note}")
        
        # Calculate averages for each method
        print(f"\n[AVERAGES] 10-YEAR AVERAGE COMPARISON:")
        print("-" * 80)
        
        method_averages = {}
        for method_name in ['traditional', 'operating_cash_flow', 'free_cash_flow']:
            values = []
            for year_data in alternative_methods.values():
                if method_name in year_data:
                    values.append(year_data[method_name]['value'])
            
            if values:
                avg_value = sum(values) / len(values)
                method_averages[method_name] = avg_value
                
                # Get method description from first occurrence
                method_desc = next(
                    (data[method_name]['method'] for data in alternative_methods.values() 
                     if method_name in data), method_name
                )
                
                print(f"{method_name.upper():20s}: ${avg_value:>15,.0f}  (Average of {len(values)} years)")
        
        # Show differences between methods
        if len(method_averages) > 1:
            print(f"\n[ANALYSIS] DIFFERENCES BETWEEN METHODS:")
            print("-" * 80)
            
            traditional_avg = method_averages.get('traditional', 0)
            ocf_avg = method_averages.get('operating_cash_flow', 0)
            fcf_avg = method_averages.get('free_cash_flow', 0)
            
            if traditional_avg != 0 and ocf_avg != 0:
                diff_pct = ((ocf_avg - traditional_avg) / abs(traditional_avg)) * 100
                print(f"Operating Cash Flow vs Traditional: {diff_pct:+.1f}% difference")
                print(f"   If positive: OCF method shows higher cash generation")
                print(f"   If negative: Traditional method shows higher cash generation")
                
                if abs(diff_pct) > 20:
                    print(f"   [WARNING] Large difference suggests reviewing working capital assumptions")
                elif abs(diff_pct) < 5:
                    print(f"   [OK] Methods are very consistent")
        
        # Recommendations
        print(f"\n[RECOMMENDATIONS] WHICH METHOD TO USE:")
        print("-" * 80)
        
        is_insurance = self._detect_insurance_company()
        is_bank = self._detect_bank()
        
        if is_insurance:
            print(f"   For insurance companies: Use TRADITIONAL method (working capital excluded)")
            print(f"   Reason: Working capital changes reflect insurance float, not operations")
        elif is_bank:
            print(f"   For banks: Use TRADITIONAL method (working capital excluded)")
            print(f"   Reason: Working capital changes reflect deposits/loans, not operations")
        else:
            print(f"   For traditional businesses: Compare TRADITIONAL vs OPERATING CASH FLOW")
            print(f"   - If similar: Either method works well")
            print(f"   - If different: OCF method may be more accurate for cash generation")
            print(f"   - Traditional method: Better for businesses with predictable working capital")
            print(f"   - OCF method: Better for businesses with volatile working capital")
        
        return alternative_methods

    def calculate_annual_owner_earnings(self):
        """Calculate owner earnings using annual financial data."""
        # Set preference for annual data processing
        self.preferred_data_type = 'Annual'
        # Load annual data specifically
        self.load_financial_statements_by_type('Annual')
        owner_earnings = self.calculate_owner_earnings()
        # Convert to DataFrame for consistency with workflow expectations
        if owner_earnings:
            df_data = []
            is_bank = self.force_bank or self._detect_bank()
            for year, data in owner_earnings.items():
                oe_bank = self._calculate_owner_earnings_value(
                    data['net_income'], data['depreciation'], data['capex'], data['working_capital_change'], is_bank=True)
                oe_nonbank = self._calculate_owner_earnings_value(
                    data['net_income'], data['depreciation'], data['capex'], data['working_capital_change'], is_bank=False, is_insurance=False)
                # Populate 'Owner Earnings' with the correct value
                owner_earnings_value = oe_bank if is_bank else oe_nonbank
                row = {
                    'Period': year,
                    'Net Income': data['net_income'],
                    'Depreciation': data['depreciation'],
                    'CapEx': data['capex'],
                    'Working Capital Change': data['working_capital_change'],
                    'Owner Earnings (Bank)': oe_bank,
                    'Owner Earnings (Non-Bank)': oe_nonbank,
                    'Owner Earnings': owner_earnings_value
                }
                df_data.append(row)
            import pandas as pd
            return pd.DataFrame(df_data)
        else:
            import pandas as pd
            return pd.DataFrame()
    
    def calculate_quarterly_owner_earnings(self):
        """Calculate owner earnings using quarterly financial data."""
        # Set preference for quarterly data processing
        self.preferred_data_type = 'Quarterly'
        # Load quarterly data specifically
        self.load_financial_statements_by_type('Quarterly')
        owner_earnings = self.calculate_owner_earnings()
        # Convert to DataFrame for consistency with workflow expectations
        if owner_earnings:
            df_data = []
            is_bank = self.force_bank or self._detect_bank()
            for period, data in owner_earnings.items():
                oe_bank = self._calculate_owner_earnings_value(
                    data['net_income'], data['depreciation'], data['capex'], data['working_capital_change'], is_bank=True)
                oe_nonbank = self._calculate_owner_earnings_value(
                    data['net_income'], data['depreciation'], data['capex'], data['working_capital_change'], is_bank=False, is_insurance=False)
                # Populate 'Owner Earnings' with the correct value
                owner_earnings_value = oe_bank if is_bank else oe_nonbank
                row = {
                    'Period': period,
                    'Net Income': data['net_income'],
                    'Depreciation': data['depreciation'],
                    'CapEx': data['capex'],
                    'Working Capital Change': data['working_capital_change'],
                    'Owner Earnings (Bank)': oe_bank,
                    'Owner Earnings (Non-Bank)': oe_nonbank,
                    'Owner Earnings': owner_earnings_value
                }
                df_data.append(row)
            import pandas as pd
            return pd.DataFrame(df_data)
        else:
            import pandas as pd
            return pd.DataFrame()
    
    def print_analysis_report(self):
        """Print a comprehensive analysis report."""
        owner_earnings = self.calculate_owner_earnings()
        
        if not owner_earnings:
            print("[ERROR] No owner earnings data could be calculated.")
            return
        
        print(f"\n" + "=" * 60)
        print(f"[DATA] OWNER EARNINGS ANALYSIS - {self.company_name.upper()}")
        print("=" * 60)
        
        print(f"\n[TIP] Owner Earnings Formula:")
        print(f"   Net Income + Depreciation/Amortization - CapEx - Working Capital Changes")
        
        print(f"\n[CHART] DETAILED BREAKDOWN BY YEAR:")
        print("-" * 60)
        
        for year in sorted(owner_earnings.keys(), reverse=True):
            data = owner_earnings[year]
            print(f"\n[YEAR] {year}:")
            print(f"   Net Income:           ${data['net_income']:>15,.0f}")
            print(f"   + Depreciation:       ${data['depreciation']:>15,.0f}")
            print(f"   + CapEx:              ${data['capex']:>15,.0f}")
            print(f"   + WC Change:          ${data['working_capital_change']:>15,.0f}")
            print(f"   = Owner Earnings:     ${data['owner_earnings']:>15,.0f}")
            
            # Calculate margin
            if data['net_income'] != 0:
                margin = (data['owner_earnings'] / data['net_income']) * 100
                print(f"   Owner Earnings/NI:    {margin:>15.1f}%")
        
        # Calculate trends
        years_list = sorted(owner_earnings.keys(), reverse=True)
        if len(years_list) >= 2:
            recent_oe = owner_earnings[years_list[0]]['owner_earnings']
            older_oe = owner_earnings[years_list[1]]['owner_earnings']
            
            if older_oe != 0:
                growth = ((recent_oe - older_oe) / abs(older_oe)) * 100
                print(f"\n[DATA] YEAR-OVER-YEAR GROWTH:")
                print(f"   {years_list[1]} to {years_list[0]}: {growth:+.1f}%")
        
        # Calculate average
        oe_values = [data['owner_earnings'] for data in owner_earnings.values()]
        avg_oe = sum(oe_values) / len(oe_values)
        print(f"\n[DATA] SUMMARY STATISTICS:")
        print(f"   Average Owner Earnings: ${avg_oe:,.0f}")
        
        # Show correct period type based on data type
        period_type = "Quarters" if hasattr(self, 'preferred_data_type') and self.preferred_data_type == 'Quarterly' else "Years"
        print(f"   {period_type} analyzed: {len(owner_earnings)}")
        
        return owner_earnings

def find_recent_xlsx_file(directory="./downloaded_files"):
    """Find the most recently modified XLSX file in the directory."""
    if not os.path.exists(directory):
        return None
    
    xlsx_files = glob.glob(os.path.join(directory, "*.xlsx"))
    if not xlsx_files:
        return None
    
    # Sort by modification time (most recent first)
    xlsx_files.sort(key=os.path.getmtime, reverse=True)
    return xlsx_files[0]

def find_ticker_xlsx_file(ticker, directory="./downloaded_files"):
    """Find the most recent XLSX file for a specific ticker."""
    if not os.path.exists(directory):
        return None
    
    # Clean ticker (replace dots with underscores, make lowercase)
    clean_ticker = ticker.replace('.', '_').lower()
    
    # Look for files matching the ticker pattern
    pattern = os.path.join(directory, f"*{clean_ticker}*.xlsx")
    xlsx_files = glob.glob(pattern)
    
    if not xlsx_files:
        print(f"[ERROR] No XLSX files found for ticker '{ticker}' in {directory}")
        print(f"[SEARCH] Looked for pattern: *{clean_ticker}*.xlsx")
        return None
    
    # Sort by modification time (most recent first) 
    xlsx_files.sort(key=os.path.getmtime, reverse=True)
    print(f"[FOUND] Using ticker-specific file: {os.path.basename(xlsx_files[0])}")
    return xlsx_files[0]

def main():
    """Main function to run the owner earnings analysis."""
    print("Warren Buffett Owner Earnings Calculator")
    print("=" * 45)
    
    # Get XLSX file path
    xlsx_file = None
    
    if len(sys.argv) > 1:
        # Check if argument is a ticker or file path
        arg = sys.argv[1]
        
        if arg.endswith('.xlsx') and os.path.exists(arg):
            # Direct file path provided
            xlsx_file = arg
            print(f"[FILE] Using specified file: {os.path.basename(xlsx_file)}")
        else:
            # Treat as ticker symbol
            ticker = arg.upper()
            print(f"[TICKER] Looking for files for ticker: {ticker}")
            xlsx_file = find_ticker_xlsx_file(ticker)
            
            if not xlsx_file:
                print(f"[FALLBACK] No ticker-specific files found, using most recent file...")
                xlsx_file = find_recent_xlsx_file()
    else:
        # Look for recent file in downloaded_files directory
        xlsx_file = find_recent_xlsx_file()
        if not xlsx_file:
            print("[ERROR] No XLSX files found in ./downloaded_files directory")
            print("[TIP] Usage: python owner_earnings_fixed.py <TICKER_SYMBOL>")
            print("[TIP] Usage: python owner_earnings_fixed.py <path_to_xlsx_file>")
            print("[TIP] Or place XLSX files in ./downloaded_files directory")
            return
        
        print(f"[FILE] Using most recent file: {os.path.basename(xlsx_file)}")
    
    if not xlsx_file:
        print("[ERROR] No suitable XLSX file found")
        return
    # Process both Annual and Quarterly data
    data_types = ['Annual', 'Quarterly']
    
    for data_type in data_types:
        print(f"\n{'='*60}")
        print(f"[DATA] PROCESSING {data_type.upper()} DATA")
        print(f"{'='*60}")
        
        # Create calculator and configure for specific data type
        calculator = OwnerEarningsCalculator(xlsx_file)
        calculator.preferred_data_type = data_type
        
        if calculator.load_financial_statements_by_type(data_type):
            # Show debug info to understand the data structure
            if data_type == 'Annual':  # Only show debug for first run
                calculator.debug_financial_data()
            
            owner_earnings = calculator.print_analysis_report()
            
            # Save results to CSV
            if owner_earnings:
                # Create data directory if it doesn't exist
                data_dir = "data"
                if not os.path.exists(data_dir):
                    os.makedirs(data_dir)
                
                suffix = 'annual' if data_type == 'Annual' else 'quarterly'
                output_file = os.path.join(data_dir, f"owner_earnings_{calculator.company_name}_{suffix}.csv")
                
                # Convert to DataFrame for easy CSV export
                df_data = []
                for year, data in owner_earnings.items():
                    row = {'Period': year}
                    row.update(data)
                    df_data.append(row)
                
                df = pd.DataFrame(df_data)
                df.to_csv(output_file, index=False)
                print(f"\n[SAVE] Results saved to: {output_file}")
        else:
            print(f"[ERROR] Failed to load {data_type.lower()} financial statements")

if __name__ == "__main__":
    main()

