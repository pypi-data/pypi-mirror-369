# Changelog

All notable changes to the MailBlock Python SDK will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.1] - 2025-08-12

### Fixed
- Corrected installation instructions in README from `pip install mailblock-python` to `pip install mailblock`
- Updated PyPI links to use correct package name `mailblock`
- Fixed all documentation references to use the correct package name

### Documentation
- Updated GitHub repository links
- Corrected PyPI project URL references

## [1.0.0] - 2025-08-12

### Added
- Initial release of MailBlock Python SDK
- Fluent builder pattern for email construction
- Both synchronous and asynchronous email sending
- Email scheduling support
- Comprehensive error handling and validation
- Advanced logging and debugging capabilities
- Automatic retry mechanism with exponential backoff
- Complete type hints and mypy support
- Context manager support for proper resource management
- Support for both text and HTML email content
- Custom logger integration
- Comprehensive test suite
- Full documentation and examples

### Dependencies
- `requests>=2.25.0` for HTTP client functionality
- `typing-extensions>=4.0.0` for Python <3.10 compatibility
- Optional `aiohttp>=3.8.0` for async support

### Supported Python Versions
- Python 3.8+
- Python 3.9
- Python 3.10
- Python 3.11
- Python 3.12