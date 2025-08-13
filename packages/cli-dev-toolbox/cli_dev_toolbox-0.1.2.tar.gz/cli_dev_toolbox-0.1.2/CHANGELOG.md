# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.2] - 2024-08-12

### Added
- Comprehensive test suite with 42 tests and 92% coverage
- Development tools configuration (black, flake8, mypy, isort, pytest)
- CI/CD workflows for GitHub Actions
- Pre-commit hooks for code quality
- Documentation files (DEVELOPMENT.md, DEPLOYMENT.md)
- Examples and documentation in docs/ folder
- Project structure improvements with proper packaging

### Changed
- Enhanced project structure with proper Python packaging
- Improved code quality with type hints and linting
- Better error handling and user experience
- Updated README with comprehensive documentation

### Fixed
- Import optimization and code formatting
- Type checking issues resolved
- All linting and formatting issues fixed

## [0.1.0] - 2024-08-12

### Added
- Initial release of CLI Dev Toolbox
- JSON to CSV conversion functionality
- Pretty JSON printing with customizable indentation
- URL fetching with timing and response analysis
- Comprehensive test suite with 92% coverage
- Development tools: black, flake8, mypy, isort, pytest
- CI/CD workflows for GitHub Actions
- Pre-commit hooks for code quality

### Features
- `json2csv` command: Convert JSON files to CSV format
- `prettyjson` command: Format JSON with proper indentation
- `fetch` command: Fetch URLs with timing and response analysis
- Support for nested JSON structures
- Error handling for invalid JSON and network issues
- Verbose output options for detailed information

### Technical
- Python 3.10+ compatibility
- Type hints throughout the codebase
- Comprehensive error handling
- Modular architecture with separate modules for converters and fetchers
