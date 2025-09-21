# AB Code Reviewer

Automated code review workflow with AI integration. Runs quality gates (format, lint, security, tests) then uses Gemini CLI for intelligent code review.

## Features

- **Quality Gates**: Automated format, lint, security, and test checks
- **AI Integration**: Gemini CLI for intelligent code review
- **Python Focus**: Optimized for Python projects (extensible to other languages)
- **Self-contained**: Manages its own dependencies
- **Configurable**: YAML-based configuration with sensible defaults
- **Error Handling**: Robust error handling with helpful error messages
- **Git Integration**: Automatic git diff for AI context

## Installation

### pip3 Installation (Recommended)

```bash
# Install from PyPI (when published)
pip3 install ab-reviewer

# Or install from source
git clone https://github.com/ab-code-reviewer/ab-reviewer.git
cd ab-reviewer
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

## Examples

### Basic Usage
```bash
# Review current directory
ab-reviewer

# Review specific project
ab-reviewer --project-path /path/to/project

# Generate report
ab-reviewer --report my_review.md
```

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

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

- **Issues**: [GitHub Issues](https://github.com/ab-code-reviewer/ab-reviewer/issues)
- **Documentation**: [Project Wiki](https://github.com/ab-code-reviewer/ab-reviewer/wiki)
- **Discussions**: [GitHub Discussions](https://github.com/ab-code-reviewer/ab-reviewer/discussions)
