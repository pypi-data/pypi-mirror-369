# MarketSwimmer 🏊‍♂️📈

**Warren Buffett's Owner Earnings Analysis Tool**

MarketSwimmer is a comprehensive financial analysis tool that implements Warren Buffett's Owner Earnings methodology to calculate the true economic value of any publicly traded company.

[![PyPI version](https://badge.fury.io/py/marketswimmer.svg)](https://badge.fury.io/py/marketswimmer)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🎯 Features

- **Owner Earnings Calculation**: Implements Warren Buffett's formula: `Net Income + Depreciation/Amortization - CapEx - Working Capital Changes`
- **Professional CLI**: Modern command-line interface with rich formatting and comprehensive help
- **GUI Application**: PyQt6-based graphical interface for interactive analysis
- **Advanced Visualizations**: Professional charts including waterfall diagrams, trend analysis, and volatility studies
- **Multi-Format Support**: Handles both annual and quarterly financial data
- **Automated Data Processing**: Intelligent extraction from StockRow financial exports

## 🚀 Installation

### From PyPI (Recommended)

```bash
pip install marketswimmer
```

### From Source

```bash
git clone https://github.com/jeremevans/MarketSwimmer.git
cd MarketSwimmer
pip install -e .
```

## ⚡ Quick Start

### Command Line Interface

```bash
# Show help and available commands
ms --help

# Quick start guide
ms quick-start

# Analyze a ticker (launches GUI)
ms gui AAPL

# View examples
ms examples

# Check system status
ms status
```

### GUI Application

```bash
# Launch the GUI directly
ms gui

# Or with a specific ticker
ms gui TSLA
```

## 📊 Usage Examples

### Basic Analysis Workflow

1. **Download Financial Data**: Use StockRow.com to export financial statements as XLSX
2. **Run Analysis**: Use the CLI or GUI to process the data
3. **View Results**: Get comprehensive owner earnings analysis and visualizations

### CLI Commands

```bash
# Show version
ms version

# Get quick start guide
ms quick-start

# Launch GUI for specific ticker
ms gui AAPL

# Show usage examples
ms examples

# Check system status
ms status
```

### Python API

```python
from marketswimmer import OwnerEarningsCalculator

# Initialize calculator with financial data
calculator = OwnerEarningsCalculator("financials_export_aapl.xlsx")

# Load and analyze data
calculator.load_financial_statements()
owner_earnings = calculator.calculate_owner_earnings()

# Generate comprehensive report
calculator.print_analysis_report()
```

## 📈 Owner Earnings Methodology

Warren Buffett's Owner Earnings formula:

```
Owner Earnings = Net Income 
                + Depreciation/Amortization 
                - Capital Expenditures 
                - Working Capital Changes
```

This metric represents the true cash that a business generates for its owners, providing a more accurate picture of economic value than reported earnings.

## 📁 Data Requirements

MarketSwimmer works with financial data exported from StockRow.com in XLSX format. The tool automatically:

- Detects annual vs quarterly data
- Extracts key financial metrics
- Calculates working capital changes
- Handles various data formats and edge cases

## 📊 Visualizations

The tool generates professional charts including:

- **Owner Earnings Trends**: Annual and quarterly comparisons
- **Waterfall Charts**: Component breakdown showing how owner earnings are derived
- **Volatility Analysis**: Rolling averages, distributions, and trend analysis
- **Year-over-Year Comparisons**: Quarterly performance across years

## 🔧 System Requirements

- Python 3.8 or higher
- Windows, macOS, or Linux
- Internet connection for data downloads
- Modern web browser for StockRow data export

## 📦 Dependencies

Core dependencies are automatically installed:

- `pandas` - Data manipulation and analysis
- `matplotlib` & `seaborn` - Chart generation
- `PyQt6` - GUI framework
- `typer` & `rich` - Modern CLI interface
- `openpyxl` - Excel file processing

## 🛠️ Development

### Setting up Development Environment

```bash
# Clone the repository
git clone https://github.com/jeremevans/MarketSwimmer.git
cd MarketSwimmer

# Install in development mode with dev dependencies
pip install -e .[dev]

# Run tests
pytest

# Format code
black .

# Type checking
mypy marketswimmer/
```

### Project Structure

```
MarketSwimmer/
├── marketswimmer/           # Main package
│   ├── __init__.py         # Package initialization
│   ├── cli.py              # Command-line interface
│   ├── core/               # Core analysis modules
│   │   ├── __init__.py
│   │   └── owner_earnings.py
│   ├── gui/                # GUI components
│   │   ├── __init__.py
│   │   └── main_window.py
│   └── visualization/      # Chart generation
│       ├── __init__.py
│       └── charts.py
├── tests/                  # Test suite
├── docs/                   # Documentation
├── setup.py               # Package configuration
├── pyproject.toml         # Modern Python packaging
├── requirements.txt       # Dependencies
└── README.md              # This file
```

## 🤝 Contributing

We welcome contributions! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: See the built-in help system (`ms --help`)
- **Issues**: Report bugs on [GitHub Issues](https://github.com/jeremevans/MarketSwimmer/issues)
- **Discussions**: Use [GitHub Discussions](https://github.com/jeremevans/MarketSwimmer/discussions) for questions

## ⚠️ Disclaimer

This tool is for educational and research purposes. Always consult with qualified financial professionals before making investment decisions. Past performance does not guarantee future results.

## 🙏 Acknowledgments

- Warren Buffett for the Owner Earnings methodology
- StockRow.com for providing accessible financial data
- The Python community for excellent libraries

---

**Happy Investing! 🏊‍♂️📈**
