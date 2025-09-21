# AB Code Reviewer - Project Design

## Overview
A reusable, automated code review workflow that integrates traditional quality gates with AI-powered review using Gemini CLI. Designed for Python projects initially, with clear extension points for Java, Go, and additional AI tools.

## Core Workflow
```
Code Changes → Quality Gates → AI Review → Report
     ↓              ↓            ↓         ↓
  Git Diff    Format→Lint→    Gemini    Terminal
              Security→Test    CLI      Output
```

## Architecture

### MVP Scope (Phase 1)
- **Languages**: Python only
- **AI Integration**: Gemini CLI only (shell out to local binary)
- **Output**: Terminal + optional markdown report
- **Configuration**: Defaults in YAML, optional overrides
- **Dependencies**: Virtualenv + pip (self-contained)

### Quality Gates (Sequential)
1. **Format Check**: `black --check`
2. **Lint Check**: `pylint` (default)
3. **Security Scan**: `bandit`
4. **Test Execution**: `pytest` with coverage

### AI Review
- Executes only if quality gates pass
- Prepares context: git diff, test results, tool outputs
- Shells out to local `gemini` binary
- Captures stdout, saves to terminal + optional `review_report.md`

## File Structure

```
ab-reviewer/
├── ab_reviewer/
│   ├── cli.py                    # Main CLI entry point
│   ├── core/
│   │   ├── detector.py           # Python project detection
│   │   ├── runner.py             # Tool execution orchestrator
│   │   └── reporter.py           # Terminal reporting
│   ├── tools/
│   │   └── python_tools.py       # Python tool integrations
│   ├── ai/
│   │   └── gemini_client.py      # Gemini CLI wrapper
│   └── config/
│       └── default_config.yaml   # Default Python configuration
├── pyproject.toml                # Package definition
├── requirements.txt              # Dependencies (click, pyyaml, etc.)
└── README.md                     # Setup and usage
```

## Configuration

### MVP Approach
- **Defaults**: All tools configured in `default_config.yaml` (black, pylint, bandit, pytest)
- **Override**: Optional `.ab-reviewer.yaml` to override specific settings
- **No config overload**: Start simple, add complexity later

### Example `.ab-reviewer.yaml` (Optional)
```yaml
# Override only what you need to change
tools:
  linter:
    args: ["--max-line-length=100"]  # Override default 88
ai:
  enabled: false  # Skip AI review for this run
```

## Usage

```bash
# Install (creates virtualenv automatically)
pip install ab-reviewer

# Basic usage (uses defaults)
ab-reviewer

# With custom config
ab-reviewer --config .ab-reviewer.yaml

# Generate markdown report
ab-reviewer --report review_report.md
```

## Extension Points

### Language Support
- `tools/java_tools.py` - Java tooling (checkstyle, spotbugs, maven test)
- `tools/go_tools.py` - Go tooling (gofmt, golint, go test)

### AI Integration
- `ai/claude_client.py` - Claude CLI integration
- `ai/copilot_client.py` - GitHub Copilot CLI support

### Output Formats
- Markdown reports (MVP)
- HTML reports with Streamlit dashboard (Phase 5)
- JSON output for CI/CD integration (Future)

## Future Phases

- **Phase 2**: Add Java support
- **Phase 3**: Add Go support
- **Phase 4**: Add Claude CLI integration
- **Phase 5**: HTML reports with Streamlit
- **Phase 6**: CI/CD integration templates

## Design Principles

1. **Simple MVP**: Start with Python + Gemini CLI only
2. **Self-contained**: Virtualenv + pip, manages own dependencies
3. **Defaults-first**: Sensible defaults, minimal config needed
4. **Extensible**: Clear architecture for adding languages and AI tools
5. **Fail-fast**: Stop on critical issues, don't waste AI time on style
6. **Actionable**: Provide specific, implementable recommendations

## Success Metrics

- **Speed**: Complete review in <2 minutes for typical Python project
- **Accuracy**: Catch 90%+ of issues before AI review
- **Usability**: Single command execution with minimal setup
- **Extensibility**: Add new language support in <100 lines of code
