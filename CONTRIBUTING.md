# Contributing to AB Code Reviewer

Thank you for your interest in contributing to AB Code Reviewer! This document provides guidelines and information for contributors.

## 🚀 Quick Start

### 1. Fork and Clone
```bash
git clone https://github.com/your-username/AB_CodeReviewer.git
cd AB_CodeReviewer
```

### 2. Set Up Development Environment
```bash
# Automated setup (recommended)
python3 setup_dev.py

# Or manual setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
pip install -e .
```

### 3. Run Tests
```bash
pytest tests/ -v
```

## 📋 Development Workflow

### Code Standards

- **Python Version**: 3.8+ (tested on 3.8, 3.9, 3.10, 3.11)
- **Formatting**: Black (line length 88)
- **Linting**: Ruff (fast, modern linter)
- **Type Checking**: MyPy (gradual adoption)
- **Testing**: Pytest with 90%+ coverage
- **Security**: Bandit for security scanning

### Pre-commit Setup

```bash
# Install pre-commit hooks
pip install pre-commit
pre-commit install

# Run on all files
pre-commit run --all-files
```

### Running Quality Checks

```bash
# Format code
black ab_reviewer/ tests/ *.py

# Lint code
ruff check ab_reviewer/ tests/

# Type checking
mypy ab_reviewer/

# Security scan
bandit -r ab_reviewer/

# Run all tests
pytest tests/ -v --cov=ab_reviewer
```

## 🧪 Testing

### Test Structure
- `tests/` - All test files
- `tests/fixtures/` - Test data and fixtures
- Unit tests: Fast, isolated, mocked
- Integration tests: Marked with `@pytest.mark.integration`

### Running Tests

```bash
# Unit tests only (fast)
pytest tests/ -v

# All tests including integration
pytest tests/ -v -m integration

# Specific test file
pytest tests/test_gemini_client.py -v

# With coverage
pytest tests/ -v --cov=ab_reviewer --cov-report=html
```

### Writing Tests

```python
import pytest
from unittest.mock import patch, MagicMock

class TestNewFeature:
    """Test cases for new feature."""
    
    def test_basic_functionality(self):
        """Test basic functionality."""
        # Arrange
        expected = "expected_result"
        
        # Act
        result = function_under_test()
        
        # Assert
        assert result == expected
    
    @pytest.mark.integration
    def test_integration_with_external_service(self):
        """Test integration with external service."""
        # This test requires external dependencies
        pass
```

## 📝 Pull Request Process

### 1. Create Feature Branch
```bash
git checkout -b feature/your-feature-name
```

### 2. Make Changes
- Write code following our standards
- Add tests for new functionality
- Update documentation if needed
- Ensure all tests pass

### 3. Commit Changes
```bash
git add .
git commit -m "feat: add new feature description"
```

### 4. Push and Create PR
```bash
git push origin feature/your-feature-name
```

### Commit Message Format
```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test changes
- `chore`: Maintenance tasks

## 🏗️ Architecture Guidelines

### Code Organization
```
ab_reviewer/
├── ai/           # AI integration (Gemini, future providers)
├── core/         # Core functionality (runners, gates, config)
├── tools/        # Tool integrations (black, pylint, etc.)
├── utils/        # Utilities (git, logging, exceptions)
└── cli.py        # Command-line interface
```

### Design Principles
- **Single Responsibility**: Each module has one clear purpose
- **Dependency Injection**: Use interfaces and dependency injection
- **Error Handling**: Comprehensive error handling with custom exceptions
- **Logging**: Structured logging with appropriate levels
- **Security**: No shell injection, secure subprocess execution

### Adding New AI Providers

```python
from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple

class AIClient(ABC):
    """Abstract base class for AI clients."""
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if AI service is available."""
        pass
    
    @abstractmethod
    def review(self, context: str, config: Dict[str, Any]) -> Tuple[bool, str]:
        """Run AI review."""
        pass

class NewAIClient(AIClient):
    """Implementation for new AI provider."""
    
    def is_available(self) -> bool:
        # Implementation
        pass
    
    def review(self, context: str, config: Dict[str, Any]) -> Tuple[bool, str]:
        # Implementation
        pass
```

## 🐛 Bug Reports

### Before Submitting
1. Check existing issues
2. Try latest version
3. Test with `--dry-run` mode
4. Check logs with `--verbose`

### Bug Report Template
```markdown
**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Run command '...'
3. See error

**Expected behavior**
What you expected to happen.

**Environment**
- OS: [e.g. macOS, Linux, Windows]
- Python version: [e.g. 3.9.6]
- AB Code Reviewer version: [e.g. 0.1.0]

**Additional context**
Add any other context about the problem here.
```

## 💡 Feature Requests

### Before Submitting
1. Check existing feature requests
2. Consider if it fits the project scope
3. Think about implementation complexity

### Feature Request Template
```markdown
**Is your feature request related to a problem?**
A clear description of what the problem is.

**Describe the solution you'd like**
A clear description of what you want to happen.

**Describe alternatives you've considered**
Alternative solutions or workarounds.

**Additional context**
Add any other context or screenshots about the feature request.
```

## 📚 Documentation

### Documentation Standards
- Use clear, concise language
- Include code examples
- Keep documentation up-to-date
- Use markdown formatting

### Documentation Structure
- `README.md` - Main documentation
- `docs/` - Detailed documentation
- `CONTRIBUTING.md` - This file
- Inline docstrings for all public APIs

## 🔒 Security

### Security Guidelines
- Never commit secrets or API keys
- Use environment variables for sensitive data
- Follow secure coding practices
- Report security issues privately

### Reporting Security Issues
Email security issues to: [security@example.com]

## 🎯 Roadmap

### Current Focus
- Enhanced AI provider support
- Improved error handling
- Better CI/CD integration
- Performance optimizations

### Future Plans
- Multi-language support (Java, Go)
- Web interface
- Plugin system
- Advanced reporting

## 🤝 Community

### Getting Help
- GitHub Discussions for questions
- GitHub Issues for bugs and features
- Code reviews for learning

### Code of Conduct
- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to AB Code Reviewer! 🚀
