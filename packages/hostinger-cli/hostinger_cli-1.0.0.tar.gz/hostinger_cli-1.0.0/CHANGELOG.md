# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-12-XX

### Added
- Initial release of Hostinger CLI
- Complete domain management functionality
  - List, show, check availability, purchase domains
  - Domain lock and privacy protection controls
  - Nameserver management
  - Domain forwarding support
  - WHOIS profile management
- Comprehensive VPS management
  - List, show, start, stop, restart VPS instances
  - VPS recreation with OS template selection
  - Backup management and restoration
  - Metrics and monitoring
  - SSH key management and attachment
  - Action history tracking
- Full DNS management capabilities
  - List, add, update, delete DNS records
  - DNS zone import/export (JSON format)
  - DNS snapshots and restoration
  - Record validation
  - Zone reset functionality
- Billing and subscription management
  - View subscriptions and payment methods
  - Browse service catalog with pricing
  - Subscription cancellation
  - Payment method management
- Rich CLI interface with Click framework
- Multiple output formats (table, JSON)
- Secure API key management and configuration
- Comprehensive error handling and validation
- Colored output with status indicators
- Both `hostinger` and `hapi` command aliases

### Security
- Secure API key storage with restricted file permissions
- Input validation for all API calls
- Error messages that don't leak sensitive information

### Developer Experience
- Modern Python packaging with pyproject.toml
- Comprehensive test suite with pytest
- Code formatting with Black
- Type checking with MyPy
- Linting with Flake8
- GitHub Actions CI/CD pipeline
- Automated PyPI publishing on releases

## [Unreleased]

### Planned Features
- Docker integration for VPS management
- Firewall management
- Post-install script management
- Malware scanner (Monarx) management
- PTR record management
- Recovery mode management
- Snapshot management
- Advanced filtering and search capabilities
- Configuration profiles for multiple accounts
- Bulk operations support
- Interactive mode for complex operations
- Shell completion support

---

For more details about changes, see the [GitHub releases page](https://github.com/hostinger/hostinger-cli/releases).
