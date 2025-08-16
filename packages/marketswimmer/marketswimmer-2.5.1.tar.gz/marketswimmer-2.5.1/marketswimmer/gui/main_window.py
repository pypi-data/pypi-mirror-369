import sys
import os
import subprocess
from pathlib import Path
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
                             QWidget, QPushButton, QLabel, QInputDialog, QTextEdit,
                             QMessageBox, QProgressBar, QGroupBox, QGridLayout)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QTextCursor

# Optional logging - only import if available
try:
    from logger_config import setup_logger, log_function_entry, log_gui_event, log_subprocess_call, log_function_exit
    LOGGING_ENABLED = True
    logger = setup_logger()
except ImportError:
    # Fallback dummy functions if logging not available
    def log_function_entry(*args, **kwargs): pass
    def log_gui_event(*args, **kwargs): pass
    def log_subprocess_call(*args, **kwargs): pass
    def log_function_exit(*args, **kwargs): pass
    
    class DummyLogger:
        def info(self, msg): print(f"[INFO] {msg}")
        def debug(self, msg): pass
        def warning(self, msg): print(f"[WARNING] {msg}")
        def error(self, msg): print(f"[ERROR] {msg}")
    
    LOGGING_ENABLED = False
    logger = DummyLogger()

class WorkerThread(QThread):
    output_signal = pyqtSignal(str)
    finished_signal = pyqtSignal()
    error_signal = pyqtSignal(str)

    def __init__(self, command, timeout=10):
        super().__init__()
        self.command = command
        self.timeout = timeout

    def run(self):
        log_function_entry(f"WorkerThread.run() args=[{self.command}]")
        logger.info(f"Starting subprocess: {self.command}")
        
        if LOGGING_ENABLED:
            log_subprocess_call()
        
        try:
            # Keep the original working directory instead of changing to GUI directory
            # This ensures files are created where the user expects them
            original_cwd = os.getcwd()
            logger.debug(f"Using working directory: {original_cwd}")
            
            # Create the subprocess with unbuffered output
            logger.debug(f"Creating subprocess: {self.command}")
            env = os.environ.copy()
            env['PYTHONUNBUFFERED'] = '1'  # Force unbuffered output
            
            process = subprocess.Popen(
                self.command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=0,  # Unbuffered
                universal_newlines=True,
                cwd=original_cwd,
                env=env  # Use environment with unbuffered Python
            )
            
            logger.info(f"Subprocess PID: {process.pid}")
            
            # Read output with timeout using threading for Windows compatibility
            import time
            import threading
            import queue
            
            def read_output(proc, q):
                """Read output in a separate thread to avoid blocking"""
                try:
                    for line in iter(proc.stdout.readline, ''):
                        if line:
                            q.put(line.rstrip())
                        if proc.poll() is not None:
                            break
                except Exception as e:
                    q.put(f"Error reading output: {e}")
                finally:
                    q.put(None)  # Signal end of output
            
            output_queue = queue.Queue()
            reader_thread = threading.Thread(target=read_output, args=(process, output_queue))
            reader_thread.daemon = True
            reader_thread.start()
            
            start_time = time.time()
            last_output_time = start_time
            
            while True:
                # Check if process has finished
                if process.poll() is not None:
                    break
                    
                # Check for timeout
                current_time = time.time()
                if current_time - start_time > self.timeout:
                    if self.timeout > 60:  # If using the longer timeout for downloads
                        self.output_signal.emit("⏱️ Download timeout reached")
                        self.output_signal.emit("📁 Browser should be open - please download XLSX file manually")
                        self.output_signal.emit("🔄 Click 'Calculate Owner Earnings' once download completes")
                    else:
                        self.output_signal.emit("⚠️ Process timeout - this command requires manual interaction")
                        self.output_signal.emit("📁 Opening browser for manual download...")
                    process.terminate()
                    process.wait()
                    self.error_signal.emit(f"Process timed out after {self.timeout} seconds - download manually and use Calculate Owner Earnings")
                    return
                
                # Try to get output from queue with short timeout
                try:
                    line = output_queue.get(timeout=0.5)
                    if line is None:  # End of output signal
                        break
                    self.output_signal.emit(line)
                    last_output_time = current_time
                except queue.Empty:
                    # No output available, continue checking
                    time.sleep(0.1)
            
            # Wait for process to complete and get final output
            process.wait()
            
            # Get any remaining output from queue
            while True:
                try:
                    line = output_queue.get_nowait()
                    if line is None:
                        break
                    self.output_signal.emit(line)
                except queue.Empty:
                    break
            
            if process.returncode == 0:
                logger.info(f"Subprocess completed successfully with return code: {process.returncode}")
                self.finished_signal.emit()
            else:
                error_msg = f"Process failed with return code: {process.returncode}"
                logger.error(error_msg)
                self.error_signal.emit(error_msg)
                
        except Exception as e:
            error_msg = f"Error running subprocess: {str(e)}"
            logger.error(error_msg)
            self.error_signal.emit(error_msg)

class MarketSwimmerGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        log_function_entry("MarketSwimmerGUI.__init__()")
        log_gui_event("GUI_INIT_START")
        
        self.setWindowTitle("MarketSwimmer - Financial Analysis Tool")
        self.setGeometry(100, 100, 1000, 700)
        
        # Set application style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #ffffff;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #d0d0d0;
                border-radius: 8px;
                margin-top: 1ex;
                padding-top: 15px;
                background-color: #fafafa;
                color: #333333;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px 0 8px;
                color: #2c3e50;
                background-color: #fafafa;
            }
            QPushButton {
                background-color: #ffffff;
                border: 2px solid #3498db;
                color: #3498db;
                padding: 10px 20px;
                text-align: center;
                font-size: 14px;
                border-radius: 6px;
                font-weight: 500;
                min-height: 20px;
            }
            QPushButton:hover {
                background-color: #3498db;
                color: #ffffff;
            }
            QPushButton:pressed {
                background-color: #2980b9;
                border-color: #2980b9;
                color: #ffffff;
            }
            QPushButton:disabled {
                background-color: #f5f5f5;
                border-color: #cccccc;
                color: #999999;
            }
            QTextEdit {
                border: 1px solid #d0d0d0;
                border-radius: 6px;
                padding: 10px;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 12px;
                background-color: #ffffff;
                color: #333333;
                line-height: 1.4;
            }
            QLabel {
                font-size: 13px;
                color: #2c3e50;
            }
            QInputDialog {
                background-color: #ffffff;
            }
        """)

        # Initialize UI
        self.init_ui()
        
        # Current ticker
        self.current_ticker = ""
        
        logger.info("GUI window created successfully")

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Title
        title_label = QLabel("MarketSwimmer Financial Analysis")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50; margin: 10px;")
        main_layout.addWidget(title_label)
        
        # Ticker input section
        ticker_group = QGroupBox("Stock Ticker Selection")
        ticker_layout = QHBoxLayout(ticker_group)
        
        self.ticker_label = QLabel("Selected Ticker: None")
        self.ticker_label.setStyleSheet("font-size: 16px; font-weight: 600; color: #2980b9; padding: 5px;")
        
        self.select_ticker_button = QPushButton("Select Ticker")
        self.select_ticker_button.clicked.connect(self.select_ticker)
        
        ticker_layout.addWidget(self.ticker_label)
        ticker_layout.addStretch()
        ticker_layout.addWidget(self.select_ticker_button)
        
        main_layout.addWidget(ticker_group)
        
        # Analysis buttons section
        analysis_group = QGroupBox("Analysis Options")
        analysis_layout = QGridLayout(analysis_group)
        
        # Complete analysis button (only button needed)
        self.complete_button = QPushButton("Complete Analysis (All Steps)")
        self.complete_button.clicked.connect(self.run_complete_analysis)
        self.complete_button.setEnabled(False)
        self.complete_button.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                border: 2px solid #e74c3c;
                color: #e74c3c;
                font-size: 16px;
                padding: 15px 30px;
                font-weight: 600;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #e74c3c;
                color: #ffffff;
            }
            QPushButton:pressed {
                background-color: #c0392b;
                border-color: #c0392b;
                color: #ffffff;
            }
        """)
        
        # Arrange buttons in grid
        analysis_layout.addWidget(self.complete_button, 0, 0, 1, 2)  # Span 2 columns  # Complete analysis button
        
        # Add Open Charts Folder button
        self.open_charts_button = QPushButton("Open Charts Folder")
        self.open_charts_button.clicked.connect(self.open_charts_folder)
        self.open_charts_button.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                border: 2px solid #27ae60;
                color: #27ae60;
                font-size: 14px;
                padding: 12px 20px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #27ae60;
                color: #ffffff;
            }
            QPushButton:pressed {
                background-color: #229954;
                border-color: #229954;
                color: #ffffff;
            }
        """)
        analysis_layout.addWidget(self.open_charts_button, 2, 0, 1, 1)  # Left column
        
        # Add Cleanup button
        self.cleanup_button = QPushButton("🧹 Cleanup Analysis")
        self.cleanup_button.clicked.connect(self.run_cleanup)
        self.cleanup_button.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                border: 2px solid #f39c12;
                color: #f39c12;
                font-size: 14px;
                padding: 12px 20px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #f39c12;
                color: #ffffff;
            }
            QPushButton:pressed {
                background-color: #e67e22;
                border-color: #e67e22;
                color: #ffffff;
            }
        """)
        analysis_layout.addWidget(self.cleanup_button, 2, 1, 1, 1)  # Right column
        
        main_layout.addWidget(analysis_group)
        
        # Console output section
        console_group = QGroupBox("Console Output")
        console_layout = QVBoxLayout(console_group)
        
        self.console_output = QTextEdit()
        self.console_output.setReadOnly(True)
        self.console_output.setMinimumHeight(300)
        console_layout.addWidget(self.console_output)
        
        # Clear console button
        clear_button = QPushButton("Clear Console")
        clear_button.clicked.connect(self.clear_console)
        clear_button.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                border: 2px solid #95a5a6;
                color: #95a5a6;
                max-width: 150px;
                padding: 8px 16px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #95a5a6;
                color: #ffffff;
            }
            QPushButton:pressed {
                background-color: #7f8c8d;
                border-color: #7f8c8d;
                color: #ffffff;
            }
        """)
        console_layout.addWidget(clear_button)
        
        main_layout.addWidget(console_group)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)
        
        # Status bar
        self.statusBar().showMessage("Ready - Select a ticker to begin analysis")

    def select_ticker(self):
        log_gui_event("BUTTON_CLICK", "Select Ticker button clicked")
        
        ticker, ok = QInputDialog.getText(self, 'Select Ticker', 'Enter stock ticker symbol:')
        
        if ok and ticker:
            ticker = ticker.upper().strip()
            self.current_ticker = ticker
            self.ticker_label.setText(f"Selected Ticker: {ticker}")
            
            # Enable complete analysis button
            self.complete_button.setEnabled(True)
            
            self.console_output.append(f">> Ticker selected: {ticker}")
            self.statusBar().showMessage(f"Ticker selected: {ticker} - Ready for complete analysis")
            
            logger.info(f"Ticker selected: {ticker}")

    def download_and_analyze(self):
        """Download financial data and perform owner earnings analysis with visualizations."""
        if not self.current_ticker:
            box = QMessageBox(self)
            box.setIcon(QMessageBox.Icon.Warning)
            box.setWindowTitle("Warning")
            box.setText("Please select a ticker first.")
            force_light_mode_dialog(box)
            box.exec()
            return
            
        log_gui_event("BUTTON_CLICK", "Download & Process Data button clicked")
        logger.info(f"Starting data download and analysis for ticker: {self.current_ticker}")
        
        self.console_output.append(f"\n>> Starting data download and analysis for {self.current_ticker}...")
        self.console_output.append("This will:")
        self.console_output.append("  1. Download financial data from StockRow")
        self.console_output.append("  2. Calculate owner earnings")
        self.console_output.append("  3. Create visualizations")
        self.console_output.append("🌐 Opening browser for download...")
        self.console_output.append("📥 Will monitor Downloads folder for new XLSX files...")
        self.console_output.append("⏱️ Timeout: 5 minutes (plenty of time for manual download)")
        self.disable_buttons()
        self.show_progress()
        
        # Use the modern CLI for data analysis with proper timeout (5 minutes)
        command = f'python -m marketswimmer analyze {self.current_ticker} --force'
        self.worker_thread = WorkerThread(command, timeout=300)  # 5 minutes like the original
        self.worker_thread.output_signal.connect(self.update_console)
        self.worker_thread.finished_signal.connect(self.on_download_finished)
        self.worker_thread.error_signal.connect(self.on_download_timeout)
        self.worker_thread.start()

    def run_complete_analysis(self):
        """Run the complete analysis workflow including enhanced fair value calculation."""
        if not self.current_ticker:
            QMessageBox.warning(self, "Warning", "Please select a ticker first.")
            return
            
        log_gui_event("BUTTON_CLICK", "Complete Analysis button clicked")
        logger.info(f"Starting complete analysis for ticker: {self.current_ticker}")
        
        self.console_output.append(f"\n>> Starting COMPLETE analysis for {self.current_ticker}...")
        self.console_output.append("This will run ALL steps in sequence:")
        self.console_output.append("  1. Download financial data from StockRow")
        self.console_output.append("  2. Calculate owner earnings")
        self.console_output.append("  3. Calculate enhanced fair value (with balance sheet analysis)")
        self.console_output.append("  4. Create visualizations")
        self.console_output.append("  5. Generate shares and debt analysis")
        self.console_output.append("🌐 Opening browser for download...")
        self.console_output.append("📥 Will monitor Downloads folder for new XLSX files...")
        self.console_output.append("⏱️ Timeout: 5 minutes (plenty of time for manual download)")
        self.console_output.append("Please wait...\n")
        
        self.disable_buttons()
        self.show_progress()
        
        # First run the complete analysis (includes enhanced fair value)
        command = f'python -m marketswimmer analyze {self.current_ticker} --force'
        logger.info(f"Complete analysis command: {command}")
        
        self.worker_thread = WorkerThread(command, timeout=300)
        self.worker_thread.output_signal.connect(self.update_console)
        self.worker_thread.finished_signal.connect(self.on_complete_analysis_phase1_finished)
        self.worker_thread.error_signal.connect(self.on_process_error)
        self.worker_thread.start()

    def calculate_fair_value(self):
        if not self.current_ticker:
            QMessageBox.warning(self, "Warning", "Please select a ticker first.")
            return

        log_gui_event("BUTTON_CLICK", "Calculate Fair Value button clicked")
        logger.info(f"Starting fair value calculation for ticker: {self.current_ticker}")

        # Check if owner earnings data exists
        data_folder = Path("data")
        clean_ticker = self.current_ticker.replace('.', '_').upper()
        annual_file = data_folder / f"owner_earnings_annual_{clean_ticker.lower()}.csv"

        if not annual_file.exists():
            QMessageBox.warning(self, "Missing Data", 
                                f"Owner earnings data not found for {self.current_ticker}.\n"
                                f"Please calculate owner earnings first.")
            return

        # Ask user which analysis mode they want
        from PyQt6.QtWidgets import QMessageBox
        dialog = QMessageBox(self)
        dialog.setIcon(QMessageBox.Icon.Question)
        dialog.setWindowTitle("Fair Value Analysis Mode")
        dialog.setText("Choose your fair value analysis method:\n\n"
                      "• YES: Enhanced Analysis (Recommended)\n"
                      "  - Automatic preferred stock detection\n"
                      "  - Insurance company methodology\n"
                      "  - Comprehensive scenario analysis\n"
                      "  - Detailed balance sheet breakdown\n\n"
                      "• NO: Manual Analysis (Legacy)\n"
                      "  - Enter values manually\n"
                      "  - Basic calculation only")
        dialog.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        dialog.setDefaultButton(QMessageBox.StandardButton.Yes)
        force_light_mode_dialog(dialog)
        reply = dialog.exec()
        use_enhanced_analysis = (reply == QMessageBox.StandardButton.Yes)

        if use_enhanced_analysis:
            # Use enhanced analysis - no additional inputs needed
            self.console_output.append(f"\n>> Starting enhanced fair value analysis for {self.current_ticker}...")
            self.console_output.append(f">> This includes automatic balance sheet detection and scenario analysis")

            command = f'python -m marketswimmer enhanced-fair-value {self.current_ticker} --no-report'

        else:
            # Legacy manual mode
            # Get growth rate (always required)
            growth_rate, ok1 = QInputDialog.getDouble(self, "Growth Rate", 
                                                     "Enter annual growth rate (e.g., 0.02 for 2%):", 
                                                     0.02, -0.1, 0.2, 3)
            if not ok1:
                return

            # Ask if user wants to use automatic extraction or manual input
            dialog2 = QMessageBox(self)
            dialog2.setIcon(QMessageBox.Icon.Question)
            dialog2.setWindowTitle("Data Input Mode")
            dialog2.setText("Do you want to automatically extract balance sheet data from downloaded files?\n\n"
                            "• YES: Auto-extract cash, debt, and shares from XLSX files\n"
                            "• NO: Manually enter values")
            dialog2.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            dialog2.setDefaultButton(QMessageBox.StandardButton.Yes)
            force_light_mode_dialog(dialog2)
            reply2 = dialog2.exec()
            use_auto_extraction = (reply2 == QMessageBox.StandardButton.Yes)

            # Build command based on mode
            if use_auto_extraction:
                self.console_output.append(f"\n>> Calculating fair value for {self.current_ticker} (AUTO-EXTRACTION MODE)...")
                self.console_output.append(f">> Growth Rate: {growth_rate:.1%}")
                self.console_output.append(f">> Auto-extracting cash, debt, and shares from downloaded data...")

                command = (f'python -m marketswimmer fair-value --ticker {self.current_ticker} '
                           f'--growth {growth_rate}')
            else:
                # Manual input mode - get all values
                cash_investments, ok2 = QInputDialog.getDouble(self, "Cash & Investments", 
                                                              "Enter cash and short-term investments ($):", 
                                                              0, 0, 1e12, 0)
                if not ok2:
                    return

                total_debt, ok3 = QInputDialog.getDouble(self, "Total Debt", 
                                                        "Enter total debt ($):", 
                                                        0, 0, 1e12, 0)
                if not ok3:
                    return

                shares_millions, ok4 = QInputDialog.getDouble(self, "Shares Outstanding", 
                                                             "Enter shares outstanding (millions):", 
                                                             1000, 1, 100000, 0)
                if not ok4:
                    return

                self.console_output.append(f"\n>> Calculating fair value for {self.current_ticker} (MANUAL MODE)...")
                self.console_output.append(f">> Growth Rate: {growth_rate:.1%}")
                self.console_output.append(f">> Cash & Investments: ${cash_investments:,.0f}")
                self.console_output.append(f">> Total Debt: ${total_debt:,.0f}")
                self.console_output.append(f">> Shares Outstanding: {shares_millions:,.0f}M")

                command = (f'python -m marketswimmer fair-value --ticker {self.current_ticker} '
                           f'--growth {growth_rate} '
                           f'--cash {cash_investments} '
                           f'--debt {total_debt} '
                           f'--shares {shares_millions} '
                           f'--manual')

        self.disable_buttons()
        self.show_progress()

        self.worker_thread = WorkerThread(command, timeout=120)  # Increased timeout for enhanced analysis
        self.worker_thread.output_signal.connect(self.update_console)
        self.worker_thread.finished_signal.connect(self.on_fair_value_finished)
        self.worker_thread.error_signal.connect(self.on_fair_value_error)
        self.worker_thread.start()

    def create_visualizations(self):
        if not self.current_ticker:
            box = QMessageBox(self)
            box.setIcon(QMessageBox.Icon.Warning)
            box.setWindowTitle("Warning")
            box.setText("Please select a ticker first.")
            force_light_mode_dialog(box)
            box.exec()
            return
            
        log_gui_event("BUTTON_CLICK", "Create Visualizations button clicked")
        logger.info(f"Starting visualization creation for ticker: {self.current_ticker}")
        
        self.console_output.append(f"\n>> Creating visualizations for {self.current_ticker}...")
        self.disable_buttons()
        self.show_progress()
        
        # Use the MarketSwimmer visualization command instead of a standalone script
        # Use python command which is available in PATH
        command = f'python -m marketswimmer visualize --ticker {self.current_ticker}'
        self.run_command(command)

    def on_complete_analysis_phase1_finished(self):
        """Handle completion of complete analysis workflow (enhanced fair value already included)."""
        self.console_output.append("\n✓ COMPLETE ANALYSIS FINISHED!")
        self.console_output.append("Check these directories for results:")
        self.console_output.append("  >> data/ - CSV files with financial analysis")
        self.console_output.append("  >> charts/ - PNG charts and visualizations") 
        self.console_output.append("  >> analysis_output/ - Shares and debt analysis charts")
        self.console_output.append("  >> downloaded_files/ - Raw Excel data")
        self.console_output.append("  >> Enhanced fair value report (TXT file with timestamp)")
        self.console_output.append("")
        self.console_output.append(">> All analysis steps completed successfully!")
        self.console_output.append(">> ENHANCED FAIR VALUE ANALYSIS INCLUDES:")
        self.console_output.append("   ✓ Automatic balance sheet data extraction")
        self.console_output.append("   ✓ Cash & Short-term Investments analysis")
        self.console_output.append("   ✓ Total Debt analysis") 
        self.console_output.append("   ✓ Common Shares Outstanding")
        self.console_output.append("   ✓ Scenario Analysis (Conservative, Base, Optimistic, Pessimistic)")
        self.console_output.append("   ✓ Comprehensive valuation report")
        self.console_output.append("")
        self.console_output.append(">> The shares and debt analysis you requested is now complete!")
        
        self.hide_progress()
        self.enable_buttons()
        
        # Clean up temp variable
        if hasattr(self, 'temp_growth_rate'):
            delattr(self, 'temp_growth_rate')
    
    def on_complete_analysis_finished(self):
        """Handle completion of complete analysis workflow."""
        self.console_output.append("\nSUCCESS: COMPLETE ANALYSIS FINISHED!")
        self.console_output.append("Check these directories for results:")
        self.console_output.append("  >> data/ - CSV files with financial analysis")
        self.console_output.append("  >> charts/ - PNG charts and visualizations") 
        self.console_output.append("  >> downloaded_files/ - Raw Excel data")
        self.console_output.append("")
        self.console_output.append(">> All analysis steps completed successfully!")
        self.console_output.append(">> Owner earnings, fair value, and visualizations are ready")
        self.console_output.append(">> You can view charts or run individual analysis steps")
        
        self.hide_progress()
        self.enable_buttons()
        
        # Clean up temp variable
        if hasattr(self, 'temp_growth_rate'):
            delattr(self, 'temp_growth_rate')
    
    def on_complete_analysis_error(self, error_message):
        """Handle errors in complete analysis workflow."""
        self.console_output.append(f"\n>> ERROR in complete analysis: {error_message}")
        self.console_output.append(">> Phase 1 completed but fair value calculation failed")
        self.console_output.append(">> You can try running fair value calculation manually")
        
        self.hide_progress()
        self.enable_buttons()
        
        # Clean up temp variable
        if hasattr(self, 'temp_growth_rate'):
            delattr(self, 'temp_growth_rate')

    def run_command(self, command):
        """Run a command in a separate thread"""
        self.worker_thread = WorkerThread(command)
        self.worker_thread.output_signal.connect(self.update_console)
        self.worker_thread.finished_signal.connect(self.on_process_finished)
        self.worker_thread.error_signal.connect(self.on_process_error)
        self.worker_thread.start()

    def update_console(self, text):
        """Update console output with new text"""
        self.console_output.append(text)
        
        # Auto-scroll to bottom
        cursor = self.console_output.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.console_output.setTextCursor(cursor)

    def on_process_finished(self):
        """Handle process completion"""
        self.console_output.append("\n>> Process completed successfully!")
        self.hide_progress()
        self.enable_buttons()
        self.statusBar().showMessage(f"Analysis completed for {self.current_ticker}")
        
        logger.info("Process completed successfully")

    def on_process_error(self, error_msg):
        """Handle process error"""
        self.console_output.append(f"\nERROR: {error_msg}")
        self.hide_progress()
        self.enable_buttons()
        self.statusBar().showMessage("Error occurred during analysis")
        
        logger.error(f"Process error: {error_msg}")

    def on_download_finished(self):
        """Handle download process completion (shouldn't happen due to manual nature)"""
        self.console_output.append("\n>> Download process completed!")
        self.console_output.append(">> Please manually download the XLSX file if it hasn't started automatically")
        self.console_output.append(">> Then click 'Calculate Owner Earnings' to process the data")
        self.hide_progress()
        self.enable_buttons()
        self.statusBar().showMessage("Download completed - ready to process data")
        
        logger.info("Download process completed")

    def on_download_timeout(self, error_msg):
        """Handle download timeout (expected behavior)"""
        self.console_output.append(f"\n>> {error_msg}")
        self.console_output.append(">> This is normal - the browser should have opened for manual download")
        self.console_output.append(">> Download the XLSX file manually, then click 'Calculate Owner Earnings'")
        self.hide_progress()
        self.enable_buttons()
        self.statusBar().showMessage("Ready to process downloaded data")
        
        logger.info("Download timeout - normal behavior")

    def on_data_processed(self):
        """Handle data processing completion"""
        self.console_output.append("\n>> Data processing completed successfully!")
        self.console_output.append(">> Financial data has been converted to analysis format")
        self.console_output.append(">> You can now run owner earnings calculations and visualizations")
        self.hide_progress()
        self.enable_buttons()
        self.statusBar().showMessage(f"Data processed for {self.current_ticker} - ready for analysis")
        
        logger.info("Data processing completed successfully")

    def on_fair_value_finished(self):
        """Handle fair value calculation completion"""
        log_function_exit("WorkerThread.run()")
        
        self.console_output.append("\n>> Fair value calculation completed successfully!")
        self.console_output.append(">> Fair value analysis report has been generated")
        self.console_output.append(">> Check the data/ folder for the detailed report")
        self.hide_progress()
        self.enable_buttons()
        self.statusBar().showMessage(f"Fair value calculated for {self.current_ticker}")
        
        logger.info("Fair value calculation completed successfully")

    def on_fair_value_error(self, error_msg):
        """Handle fair value calculation error/timeout"""
        log_function_exit("WorkerThread.run() - ERROR")
        
        self.console_output.append(f"\n>> ERROR in fair value calculation: {error_msg}")
        self.console_output.append(">> Please check that owner earnings data exists")
        self.console_output.append(">> Try calculating owner earnings first")
        self.hide_progress()
        self.enable_buttons()
        self.statusBar().showMessage("Fair value calculation failed")
        
        logger.error(f"Fair value calculation failed: {error_msg}")

    def disable_buttons(self):
        """Disable analysis button during processing"""
        self.complete_button.setEnabled(False)

    def enable_buttons(self):
        """Enable analysis button after processing"""
        if self.current_ticker:
            self.complete_button.setEnabled(True)

    def show_progress(self):
        """Show indeterminate progress bar"""
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress

    def hide_progress(self):
        """Hide progress bar"""
        self.progress_bar.setVisible(False)

    def clear_console(self):
        """Clear the console output"""
        self.console_output.clear()
        self.console_output.append("Console cleared.")
        
        logger.info("Console cleared by user")

    def open_charts_folder(self):
        """Open the charts folder in Windows Explorer"""
        log_gui_event("BUTTON_CLICK", "Open Charts Folder button clicked")
        
        charts_folder = Path("charts")
        if not charts_folder.exists():
            charts_folder.mkdir(parents=True, exist_ok=True)
            self.console_output.append(">> Created charts folder")
        
        # Open the folder in Windows Explorer
        try:
            os.startfile(str(charts_folder.absolute()))
            self.console_output.append(f">> Opened charts folder: {charts_folder.absolute()}")
            logger.info(f"Opened charts folder: {charts_folder.absolute()}")
        except Exception as e:
            error_msg = f"Could not open charts folder: {str(e)}"
            self.console_output.append(f"ERROR: {error_msg}")
            logger.error(error_msg)

    def run_cleanup(self):
        """Run the cleanup script to remove analysis artifacts"""
        log_gui_event("BUTTON_CLICK", "Cleanup Analysis button clicked")

        # Ask for confirmation
        dialog = QMessageBox(self)
        dialog.setIcon(QMessageBox.Icon.Question)
        dialog.setWindowTitle("Confirm Cleanup")
        dialog.setText("This will remove all analysis artifacts:\n\n"
                      "• analysis_output/ folder (charts and reports)\n"
                      "• charts/ folder (visualizations)\n"
                      "• data/ folder (CSV files)\n"
                      "• downloaded_files/ folder (Excel files)\n"
                      "• All .txt report files\n\n"
                      "Are you sure you want to proceed?")
        dialog.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        dialog.setDefaultButton(QMessageBox.StandardButton.No)
        force_light_mode_dialog(dialog)
        reply = dialog.exec()
        if reply == QMessageBox.StandardButton.Yes:
            self.console_output.append("\n🧹 Starting cleanup process...")
            self.console_output.append(">> Removing analysis artifacts...")

            try:
                # Use the Python cleanup script
                import shutil
                import time
                from pathlib import Path

                # Folders to remove
                folders_to_remove = ["analysis_output", "charts", "data", "downloaded_files"]

                def remove_readonly(func, path, _):
                    """Error handler for Windows readonly files"""
                    import stat
                    os.chmod(path, stat.S_IWRITE)
                    func(path)

                for folder in folders_to_remove:
                    folder_path = Path(folder)
                    if folder_path.exists():
                        try:
                            # Windows-safe removal with retry
                            if os.name == 'nt':  # Windows
                                shutil.rmtree(folder_path, onerror=remove_readonly)
                            else:
                                shutil.rmtree(folder_path)
                            self.console_output.append(f"   ✓ Removed {folder}/ folder")
                        except PermissionError:
                            # Try alternative approach for Windows
                            try:
                                import subprocess
                                subprocess.run(['rmdir', '/s', '/q', str(folder_path)], 
                                               shell=True, check=False)
                                self.console_output.append(f"   ✓ Removed {folder}/ folder (using rmdir)")
                            except Exception as e2:
                                self.console_output.append(f"   ❌ Could not remove {folder}/: {str(e2)}")
                        except Exception as e:
                            self.console_output.append(f"   ❌ Could not remove {folder}/: {str(e)}")
                    else:
                        self.console_output.append(f"   - {folder}/ folder not found")

                # Remove .txt files (reports)
                txt_files = list(Path(".").glob("*.txt"))
                for txt_file in txt_files:
                    # Skip common files that shouldn't be deleted
                    if txt_file.name.lower() not in ["readme.txt", "license.txt", "requirements.txt"]:
                        txt_file.unlink()
                        self.console_output.append(f"   ✓ Removed {txt_file.name}")

                if not txt_files:
                    self.console_output.append("   - No .txt report files found")

                self.console_output.append("\n✅ Cleanup completed successfully!")
                self.console_output.append(">> All analysis artifacts have been removed")
                self.console_output.append(">> You can now run a fresh analysis")

                logger.info("Cleanup completed successfully")

            except Exception as e:
                error_msg = f"Cleanup failed: {str(e)}"
                self.console_output.append(f"\n❌ ERROR: {error_msg}")
                box = QMessageBox(self)
                box.setIcon(QMessageBox.Icon.Critical)
                box.setWindowTitle("Cleanup Error")
                box.setText(f"Failed to cleanup files:\n{error_msg}")
                force_light_mode_dialog(box)
                box.exec()
                logger.error(error_msg)
        else:
            self.console_output.append(">> Cleanup cancelled by user")
            logger.info("Cleanup cancelled by user")

# Utility function to force light mode on QMessageBox
from PyQt6.QtGui import QPalette, QColor


def force_light_mode_dialog(dialog):
    palette = dialog.palette()
    palette.setColor(QPalette.ColorRole.Window, QColor("#ffffff"))
    palette.setColor(QPalette.ColorRole.WindowText, QColor("#222222"))
    palette.setColor(QPalette.ColorRole.Base, QColor("#ffffff"))
    palette.setColor(QPalette.ColorRole.Text, QColor("#222222"))
    palette.setColor(QPalette.ColorRole.Button, QColor("#f5f5f5"))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor("#222222"))
    dialog.setPalette(palette)
    dialog.setStyleSheet("QLabel{color:#222222;} QPushButton{color:#222222; background:#f5f5f5;}")

# Patch all QMessageBox usages to force light mode
# Example for question dialogs:
# reply = QMessageBox.question(self, ...)
# After creating the dialog, call force_light_mode_dialog(dialog)

# Patch warning/info dialogs
# Example:
# box = QMessageBox(self)
# force_light_mode_dialog(box)

def main():
    log_function_entry("main()")
    
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("MarketSwimmer")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("MarketSwimmer Analytics")
    
    # Create and show the main window
    window = MarketSwimmerGUI()
    window.show()
    
    logger.info("MarketSwimmer GUI started successfully")
    
    # Start the event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
