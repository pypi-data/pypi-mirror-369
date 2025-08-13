# CLI Dev Toolbox

A Python CLI utility for developers to enhance productivity and streamline workflows. This toolbox provides essential tools for data conversion, JSON formatting, and HTTP operations.

## 🚀 Features

- **JSON to CSV Conversion**: Convert JSON files to CSV format for data analysis
- **Pretty JSON Printing**: Format JSON files with proper indentation and readability
- **URL Fetching**: Fetch URLs and measure response times (coming soon)

## 📦 Installation

### Prerequisites
- Python 3.10 or higher
- pip package manager

### Install from source
```bash
# Clone the repository
git clone https://github.com/rahulkumar/cli-dev-toolbox.git
cd cli-dev-toolbox

# Create and activate virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install the package in development mode
pip install -e .

# For development (includes testing and linting tools)
pip install -e ".[dev]"
```

### Install from PyPI (when published)
```bash
pip install cli-dev-toolbox
```

## 🛠️ Usage

The CLI tool provides several commands to help with common development tasks:

### JSON to CSV Conversion

Convert JSON files to CSV format for easier data analysis:

```bash
cli-dev-toolbox json2csv input.json output.csv
```

**Example:**
```bash
# Convert a JSON file containing employee data
cli-dev-toolbox json2csv data.json employees.csv
```

The converter expects JSON files with an array of objects structure, where each object represents a row in the CSV file.

### Pretty JSON Printing

Format JSON files with proper indentation for better readability:

```bash
cli-dev-toolbox prettyjson input.json
```

**Example:**
```bash
# Format a JSON file for better readability
cli-dev-toolbox prettyjson config.json
```

### URL Fetching (Coming Soon)

Fetch URLs and measure response times:

```bash
cli-dev-toolbox fetch https://example.com
```

## 📁 Project Structure

```
cli-dev-toolbox/
├── cli_dev_toolbox/           # Main package directory
│   ├── __init__.py           # Package initialization and metadata
│   ├── toolbox.py            # Main CLI interface and argument parsing
│   ├── converters.py         # Data conversion utilities (JSON↔CSV)
│   └── fetcher.py            # HTTP fetching utilities (planned)
├── docs/                     # Documentation
│   ├── README.md             # Documentation overview
│   ├── api.md                # API documentation
│   ├── development.md        # Development guide
│   └── examples.md           # Usage examples
├── examples/                 # Example files
│   └── sample_data.json      # Sample data for testing
├── tests/                    # Test suite
│   ├── __init__.py           # Test package initialization
│   ├── test_basic.py         # Basic test suite
│   ├── test_converters.py    # Converter module tests
│   └── test_toolbox.py       # CLI toolbox tests
├── .github/                  # GitHub configuration
│   └── workflows/            # CI/CD workflows
├── pyproject.toml            # Project configuration and dependencies
├── requirements.txt          # Core dependencies
├── requirements-dev.txt      # Development dependencies
├── setup.py                  # Setup script (for compatibility)
├── MANIFEST.in               # Package manifest
├── Makefile                  # Development tasks
├── .pre-commit-config.yaml   # Pre-commit hooks configuration
├── CHANGELOG.md              # Version history
└── README.md                 # This file
```

## 🧪 Testing

Run the test suite to ensure everything works correctly:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=cli_dev_toolbox

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_converters.py
```

## 🔧 Development

### Quick Start

```bash
# Install development dependencies
make install-dev

# Run all checks
make check-all

# Format code
make format

# Run tests
make test
```

### Setting up development environment

1. Fork and clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment
4. Install development dependencies: `pip install -e ".[dev]"`
5. Install pre-commit hooks: `pre-commit install`

### Adding new features

1. Create your feature branch: `git checkout -b feature/amazing-feature`
2. Make your changes and add tests
3. Run all checks: `make check-all`
4. Commit your changes: `git commit -m 'Add amazing feature'`
5. Push to the branch: `git push origin feature/amazing-feature`
6. Open a Pull Request

### Available Make Commands

```bash
make help          # Show all available commands
make install       # Install package in development mode
make install-dev   # Install development dependencies
make test          # Run tests
make test-cov      # Run tests with coverage
make lint          # Run linting checks
make format        # Format code
make type-check    # Run type checking
make clean         # Clean build artifacts
make build         # Build package
make dist          # Create distribution files
```

## 📝 Dependencies

### Core Dependencies
- **requests>=2.31.0**: HTTP library for URL fetching operations

### Development Dependencies
- **pytest>=7.4.0**: Testing framework
- **pytest-cov>=4.1.0**: Coverage reporting
- **black>=23.0.0**: Code formatting
- **flake8>=6.0.0**: Linting
- **mypy>=1.5.0**: Type checking
- **twine>=4.0.0**: Package uploading
- **build>=1.0.0**: Package building
- **pre-commit>=3.3.0**: Git hooks

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Development Guidelines

1. Follow PEP 8 style guidelines
2. Add tests for new features
3. Update documentation as needed
4. Ensure all tests pass before submitting

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Rahul Kumar**
- Email: pkrk14@gmail.com
- GitHub: [@hvtrk](https://github.com/hvtrk)

## 🐛 Issues

If you encounter any issues or have suggestions for improvements, please [open an issue](https://github.com/rahulkumar/cli-dev-toolbox/issues) on GitHub.

## 📈 Roadmap

- [ ] Implement pretty JSON printing functionality
- [ ] Add URL fetching with response time measurement
- [ ] Add CSV to JSON conversion
- [ ] Add support for different JSON structures
- [ ] Add configuration file support
- [ ] Add more data format conversions (XML, YAML, etc.)

---

**Note**: This project is currently in active development. Some features may be incomplete or subject to change.
