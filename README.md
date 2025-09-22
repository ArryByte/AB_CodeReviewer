# AB Code Reviewer

[![CI](https://github.com/ArryByte/AB_CodeReviewer/workflows/CI/badge.svg)](https://github.com/ArryByte/AB_CodeReviewer/actions)
[![codecov](https://codecov.io/gh/ArryByte/AB_CodeReviewer/branch/main/graph/badge.svg)](https://codecov.io/gh/ArryByte/AB_CodeReviewer)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Enterprise-grade automated code review workflow with AI integration.** Runs quality gates (format, lint, security, tests) then uses Gemini CLI for intelligent code review.

## ✨ Features

- **🔒 Security-First**: Zero shell injection vulnerabilities, secure subprocess execution
- **🛡️ Quality Gates**: Automated format, lint, security, and test checks
- **🤖 AI Integration**: Gemini CLI for intelligent code review with retry logic
- **🐍 Python Focus**: Optimized for Python projects (extensible to other languages)
- **📦 Self-contained**: Manages its own dependencies with virtual environments
- **⚙️ Configurable**: YAML-based configuration with sensible defaults
- **🔄 Progressive**: Continue workflow even if some quality gates fail
- **🧪 Testable**: Dry-run mode for testing without external dependencies
- **📊 Reporting**: Comprehensive reports with actionable insights

## 🚀 Quick Start

### Production Installation

```bash
# Install from PyPI (when published)
pip3 install ab-reviewer

# Or install from source
git clone https://github.com/ArryByte/AB_CodeReviewer.git
cd AB_CodeReviewer
pip3 install -e .
```

### Development Setup

```bash
# 1. Clone the repository
git clone https://github.com/ArryByte/AB_CodeReviewer.git
cd AB_CodeReviewer

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt
pip install -e .

# 4. Run tests
pytest tests/ -v

# 5. Test the tool
python3 -m ab_reviewer --project-path . --dry-run
```

### Automated Development Setup

```bash
# One-command setup (recommended)
python3 setup_dev.py
```

## 📋 Prerequisites

- **Python 3.8+** (tested on 3.8, 3.9, 3.10, 3.11)
- **Git** (for git integration features)
- **Gemini CLI** (optional, for AI review features)

### Installing Gemini CLI

```bash
# Install Gemini CLI for AI features
# Follow official Gemini CLI installation guide
# https://docs.gemini.com/cli/installation
```

## 🛠️ Development Workflow

### Running Tests

```bash
# Unit tests only (fast)
pytest tests/ -v

# All tests including integration
pytest tests/ -v -m integration

# With coverage
pytest tests/ -v --cov=ab_reviewer --cov-report=html
```

### Code Quality Checks

```bash
# Format code
black ab_reviewer/ tests/ *.py

# Lint code
ruff check ab_reviewer/ tests/

# Type checking
mypy ab_reviewer/

# Security scan
bandit -r ab_reviewer/
```

### Testing the Tool

```bash
# Dry run (no external dependencies)
python3 -m ab_reviewer --project-path . --dry-run

# Full workflow (requires Gemini CLI)
python3 -m ab_reviewer --project-path . --progressive
```

## Installation

### pip3 Installation (Recommended)

```bash
# Install from PyPI (when published)
pip3 install ab-reviewer

# Or install from source
git clone https://github.com/ArryByte/AB_CodeReviewer.git
cd AB_CodeReviewer
pip3 install -e .
```

### Homebrew Installation (macOS)

```bash
# Add tap (when published)
brew tap ab-code-reviewer/ab-reviewer

# Install
brew install ab-reviewer
```

## Quick Start

```bash
# Navigate to your Python project
cd /path/to/your/python/project

# Run code review (uses defaults)
ab-reviewer

# Set up project with default configuration
ab-reviewer --setup

# Install missing tools automatically
ab-reviewer --install-tools

# Generate markdown report
ab-reviewer --report review_report.md

# Enable verbose output
ab-reviewer --verbose
```

## Configuration

### Default Configuration

AB Code Reviewer comes with sensible defaults for Python projects:

- **Formatter**: `black --check --diff`
- **Linter**: `pylint --output-format=text --score=no`
- **Security**: `bandit -r . -f json`
- **Tests**: `pytest --cov --cov-report=term-missing -v`

### Custom Configuration

Create `.ab-reviewer.yaml` in your project root to override defaults:

```yaml
# Override only what you need to change
tools:
  linter:
    args: ["--max-line-length=100"]  # Override default 88
  security:
    args: ["-r", ".", "-f", "json", "-ll"]  # Add low-level issues
ai:
  enabled: false  # Skip AI review for this run
```

## Workflow

1. **Project Detection**: Automatically detects Python projects
2. **Quality Gates**: Runs format → lint → security → tests
3. **AI Review**: Uses Gemini CLI for intelligent review (if gates pass)
4. **Reporting**: Terminal output + optional markdown report

## Requirements

### System Requirements
- Python 3.8+
- Git repository (recommended)

### Python Tools (Auto-installed)
- `black` - Code formatter
- `pylint` - Code linter
- `bandit` - Security scanner
- `pytest` - Test runner
- `pytest-cov` - Coverage reporting

### AI Tools
- `gemini` CLI - For AI-powered code review

## CLI Options

```bash
ab-reviewer [OPTIONS]

Options:
  -c, --config PATH     Path to configuration file
  -r, --report PATH     Save markdown report to file
  -p, --project-path    Project path to review (default: current directory)
  --install-tools       Install missing Python tools automatically
  --setup              Set up project with default configuration
  -v, --verbose        Enable verbose output
  --help               Show help message
```

## 📖 Usage

### Basic Usage
```bash
# Review current directory
python3 -m ab_reviewer

# Review specific project
python3 -m ab_reviewer --project-path /path/to/project

# Generate report
python3 -m ab_reviewer --report my_review.md
```

### Advanced Usage

```bash
# Progressive mode (continue even if some gates fail)
python3 -m ab_reviewer --progressive

# Dry run mode (skip AI review, test without external dependencies)
python3 -m ab_reviewer --dry-run

# Install missing tools automatically
python3 -m ab_reviewer --install-tools

# Verbose output for debugging
python3 -m ab_reviewer --verbose

# Generate comprehensive report
python3 -m ab_reviewer --generate-report --output-dir reports/
```

### CI/CD Integration

```yaml
# .github/workflows/code-review.yml
name: Code Review
on: [pull_request]

jobs:
  review:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    - name: Install AB Code Reviewer
      run: |
        pip install -r requirements.txt
        pip install -e .
    - name: Run Code Review
      run: |
        python3 -m ab_reviewer --project-path . --dry-run --generate-report
      env:
        GEMINI_INTEGRATION: 1  # Enable integration tests if needed
```

### Environment Variables

```bash
# Gemini CLI configuration
export GEMINI_API_KEY="your-api-key"  # If using API instead of CLI
export GEMINI_MODEL="gemini-pro"      # Model selection

# Logging configuration
export AB_REVIEWER_LOG_LEVEL="INFO"   # DEBUG, INFO, WARNING, ERROR
export AB_REVIEWER_LOG_FORMAT="json"  # json, text

# CI/CD mode
export CI="true"                      # Enable CI-specific behavior
```

## Examples

### Project Setup
```bash
# Set up new project
ab-reviewer --setup

# Install missing tools
ab-reviewer --install-tools
```

### Custom Configuration
```bash
# Use custom config file
ab-reviewer --config my-config.yaml

# Disable AI review
echo "ai:\n  enabled: false" > .ab-reviewer.yaml
ab-reviewer

# Run with verbose output and report
ab-reviewer --verbose --report full_report.md
```

## Output

### Terminal Output
- Colored, formatted results
- Clear pass/fail indicators
- AI review feedback
- Actionable recommendations

### Markdown Report
- Project information
- Quality gate results
- AI review output
- Summary and next steps

## Troubleshooting

### Common Issues

**"Tool not found" errors**
```bash
# Install missing tools
ab-reviewer --install-tools
```

**"Gemini CLI not found"**
```bash
# Install Gemini CLI separately
# See: https://github.com/google/gemini-cli
```

**"Not in virtual environment"**
```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Environment Validation

AB Code Reviewer validates your environment and provides helpful suggestions:

```bash
ab-reviewer --verbose
```

## Development

### Setup Development Environment
```bash
git clone https://github.com/ab-code-reviewer/ab-reviewer.git
cd ab-reviewer
python3 -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
```

### Running Tests
```bash
pytest
```

### Code Quality
```bash
# Format code
black ab_reviewer/

# Lint code
pylint ab_reviewer/

# Security check
bandit -r ab_reviewer/
```

## Roadmap

- **Phase 2**: Java support
- **Phase 3**: Go support
- **Phase 4**: Claude CLI integration
- **Phase 5**: HTML reports with Streamlit
- **Phase 6**: CI/CD integration templates

## 🔧 Troubleshooting

### Common Issues

**Q: "Gemini CLI not found" error**
```bash
# Install Gemini CLI or use dry-run mode
python3 -m ab_reviewer --dry-run
```

**Q: "Tool not found" errors**
```bash
# Install missing tools automatically
python3 -m ab_reviewer --install-tools
```

**Q: Tests failing in CI**
```bash
# Run with integration tests disabled
pytest tests/ -v -m "not integration"
```

**Q: Permission errors on macOS/Linux**
```bash
# Ensure proper permissions
chmod +x install.sh
./install.sh
```

### Debug Mode

```bash
# Enable debug logging
export AB_REVIEWER_LOG_LEVEL="DEBUG"
python3 -m ab_reviewer --verbose
```

### Getting Help

- 📖 [Documentation](docs/)
- 🐛 [Issues](https://github.com/ArryByte/AB_CodeReviewer/issues)
- 💬 [Discussions](https://github.com/ArryByte/AB_CodeReviewer/discussions)

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

```bash
# 1. Fork and clone
git clone https://github.com/your-username/AB_CodeReviewer.git
cd AB_CodeReviewer

# 2. Set up development environment
python3 setup_dev.py

# 3. Make your changes
git checkout -b feature/your-feature
# ... make changes ...

# 4. Run tests
pytest tests/ -v

# 5. Submit PR
git push origin feature/your-feature
```

### Code Standards

- **Formatting**: `black` (line length 88)
- **Linting**: `ruff` for fast linting
- **Type Checking**: `mypy` for static analysis
- **Testing**: `pytest` with 90%+ coverage
- **Security**: `bandit` for security scanning

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with ❤️ for the developer community
- Inspired by modern CI/CD best practices
- Powered by Gemini AI for intelligent code review

## Support

- **Issues**: [GitHub Issues](https://github.com/ab-code-reviewer/ab-reviewer/issues)
- **Documentation**: [Project Wiki](https://github.com/ab-code-reviewer/ab-reviewer/wiki)
- **Discussions**: [GitHub Discussions](https://github.com/ab-code-reviewer/ab-reviewer/discussions)
