# Bankinter Converter

A CLI tool to convert Bankinter bank statements (checking accounts and credit cards) from Excel to CSV format.

## Features

- **Checking Account Conversion**: Convert checking account statements by removing specified rows and selecting columns
- **Credit Card Conversion**: Convert credit card statements with automatic column detection and clean output
- **Language Agnostic**: Works with statements in different languages
- **Flexible Column Selection**: Automatically detects transaction structure

## Installation

### Using uvx (Recommended)

```bash
# Install and run directly
uvx bankinter-converter --help

# Or install globally
uvx install bankinter-converter
```

### Using uv

```bash
# Install globally as a tool
uv tool install bankinter-converter

# Or install in development mode
uv sync
```

### Alternative: Using pip

```bash
pip install bankinter-converter
```

## Usage

### Checking Account Conversion

```bash
bankinter-converter checking input.xls output.csv
```

**Options:**
- `--skip-rows N`: Number of rows to skip at the beginning (default: 3)
- `--columns A-E`: Columns to include (default: A-E)
- `--sheet SHEET`: Sheet name or index (default: 0)
- `--verbose`: Show detailed processing information

**Example:**
```bash
bankinter-converter checking statement.xls transactions.csv --skip-rows 5 --columns A-D
```

### Credit Card Conversion

```bash
bankinter-converter credit input.xls output.csv
```

**Options:**
- `--verbose`: Show detailed processing information

**Example:**
```bash
bankinter-converter credit credit_statement.xls credit_transactions.csv
```

## Credit Card Converter Logic

The credit card converter automatically:

1. **Removes metadata**: Card number, available balance, arranged balance, and blank lines
2. **Detects transaction structure**: 
   - If Column D contains transaction types → Output: Date, Description, Type, Amount (A-D)
   - If Column D is empty → Output: Date, Description, Amount (A-C)
3. **Removes totals**: Total credit/debit sections and pending transactions
4. **Outputs clean CSV**: Only transaction data with proper headers

The detection is language-agnostic and relies on data content rather than header names.

## Development

### Setup with uv (Recommended)

```bash
# Clone the repository
git clone https://github.com/barbarity/bankinter-converter.git
cd bankinter-converter

# Create virtual environment and install dependencies (uses Python 3.13)
uv sync --extra dev
```

### Alternative Setup with pip

```bash
# Clone the repository
git clone https://github.com/barbarity/bankinter-converter.git
cd bankinter-converter

# Create virtual environment (Python 3.8+ required)
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"
```

### Running Tests

```bash
# With uv
uv run pytest

# With pip (after activating virtual environment)
pytest
```

### Code Quality

```bash
# Check code with ruff
uv run ruff check .

# Format code with ruff
uv run ruff format .

# Fix issues automatically
uv run ruff check --fix .
```

### Testing the Tool

```bash
# With uv
uv run bankinter-converter --help

# With pip (after activating virtual environment)
bankinter-converter --help
```

## Project Structure

```
bankinter-converter/
├── src/
│   └── bankinter_converter/
│       ├── __init__.py
│       ├── cli.py              # Command-line interface
│       ├── checking_account.py # Checking account conversion logic
│       └── credit_card.py      # Credit card conversion logic
├── tests/
│   ├── test_checking_account.py
│   └── test_credit_card.py
├── pyproject.toml          # Project configuration
├── README.md              # This file
├── LICENSE                # MIT License
└── .gitignore
```

## License

This project is licensed under the MIT License.
