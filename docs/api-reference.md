# AB Code Reviewer - API Reference

## Core Modules

### `ab_reviewer.core.detector`

#### `ProjectDetector`

Detects project type and gathers project information.

```python
from ab_reviewer.core.detector import ProjectDetector

detector = ProjectDetector("/path/to/project")
project_info = detector.get_project_info()
```

**Methods:**

- `detect_project_type() -> str`: Detect project type (python, java, go, unknown)
- `get_project_info() -> Dict[str, Any]`: Get comprehensive project information
- `_is_python_project() -> bool`: Check if project is Python-based
- `_is_java_project() -> bool`: Check if project is Java-based
- `_is_go_project() -> bool`: Check if project is Go-based

### `ab_reviewer.core.runner`

#### `ToolRunner`

Orchestrates execution of quality gate tools.

```python
from ab_reviewer.core.runner import ToolRunner

runner = ToolRunner("/path/to/project", config, cache_enabled=True)
results = runner.run_quality_gates(parallel=True)
```

**Methods:**

- `run_quality_gates(parallel: bool = False) -> Dict[str, Any]`: Run all quality gates
- `get_failed_tools() -> List[str]`: Get list of failed tools
- `all_tools_passed() -> bool`: Check if all tools passed
- `_run_formatter() -> Tuple[bool, str]`: Run code formatter
- `_run_linter() -> Tuple[bool, str]`: Run code linter
- `_run_security() -> Tuple[bool, str]`: Run security scanner
- `_run_tests() -> Tuple[bool, str]`: Run test suite

### `ab_reviewer.core.reporter`

#### `Reporter`

Generates reports for code review results.

```python
from ab_reviewer.core.reporter import Reporter

reporter = Reporter("/path/to/project")
reporter.print_terminal_report(project_info, tool_results, ai_output)
report_path = reporter.save_markdown_report(project_info, tool_results, ai_output)
```

**Methods:**

- `print_terminal_report(project_info, tool_results, ai_output) -> None`: Print terminal report
- `save_markdown_report(project_info, tool_results, ai_output, output_file) -> str`: Save markdown report

## AI Integration

### `ab_reviewer.ai.gemini_client`

#### `GeminiClient`

Client for interacting with Gemini CLI.

```python
from ab_reviewer.ai.gemini_client import GeminiClient

client = GeminiClient("/path/to/project")
if client.is_available():
    success, output = client.run_review(tool_results, config)
```

**Methods:**

- `is_available() -> bool`: Check if Gemini CLI is available
- `run_review(tool_results, config) -> Tuple[bool, str]`: Run AI review
- `get_version() -> Optional[str]`: Get Gemini CLI version
- `_prepare_context(tool_results, config) -> str`: Prepare context for AI review

## Tool Integration

### `ab_reviewer.tools.python_tools`

#### `PythonTools`

Manages Python-specific code quality tools.

```python
from ab_reviewer.tools.python_tools import PythonTools

tools = PythonTools("/path/to/project")
is_valid, issues = tools.validate_environment()
if not is_valid:
    tools.install_tools()
```

**Methods:**

- `install_tools() -> bool`: Install required Python tools
- `validate_environment() -> Tuple[bool, List[str]]`: Validate environment
- `setup_project() -> bool`: Set up project configuration
- `get_tool_versions() -> Dict[str, str]`: Get versions of installed tools
- `_is_tool_installed(tool_name) -> bool`: Check if tool is installed

## Utilities

### `ab_reviewer.utils.exceptions`

Custom exceptions for AB Code Reviewer.

```python
from ab_reviewer.utils.exceptions import (
    ABReviewerError, ConfigurationError, ToolNotFoundError,
    ToolExecutionError, ProjectDetectionError, AIReviewError, ValidationError
)
```

**Exception Hierarchy:**

- `ABReviewerError`: Base exception
  - `ConfigurationError`: Configuration-related errors
  - `ToolNotFoundError`: Required tool not found
  - `ToolExecutionError`: Tool execution failed
  - `ProjectDetectionError`: Project type detection failed
  - `AIReviewError`: AI review failed
  - `ValidationError`: Input validation failed

### `ab_reviewer.utils.validation`

Input validation utilities.

```python
from ab_reviewer.utils.validation import (
    validate_project_path, validate_python_version, validate_configuration,
    validate_tool_arguments, validate_file_path, validate_directory_path
)
```

**Functions:**

- `validate_project_path(project_path: Path) -> None`: Validate project path
- `validate_python_version(min_version: tuple = (3, 8)) -> None`: Validate Python version
- `validate_configuration(config: Dict[str, Any]) -> None`: Validate configuration
- `validate_tool_arguments(tool_name: str, args: List[str]) -> None`: Validate tool arguments
- `validate_file_path(file_path: Path, must_exist: bool = True) -> None`: Validate file path
- `validate_directory_path(dir_path: Path, must_exist: bool = True) -> None`: Validate directory path

### `ab_reviewer.utils.cache`

Caching utilities for tool results.

```python
from ab_reviewer.utils.cache import ToolCache

cache = ToolCache(Path("/cache/dir"), ttl_seconds=3600)
cached_result = cache.get("tool_name", ["args"], project_path)
cache.set("tool_name", ["args"], project_path, result)
```

**Methods:**

- `get(tool_name, args, project_path) -> Optional[Dict[str, Any]]`: Get cached result
- `set(tool_name, args, project_path, result) -> None`: Cache result
- `clear() -> None`: Clear all cache entries

### `ab_reviewer.utils.git`

Git utilities for code review context.

```python
from ab_reviewer.utils.git import GitManager

git_manager = GitManager(Path("/project"))
if git_manager.is_git_repository():
    diff = git_manager.get_git_diff()
    branch_info = git_manager.get_branch_info()
```

**Methods:**

- `is_git_repository() -> bool`: Check if project is git repository
- `get_git_diff(staged_only: bool = False) -> Optional[str]`: Get git diff
- `get_recent_commits(count: int = 5) -> List[Dict[str, Any]]`: Get recent commits
- `get_branch_info() -> Dict[str, str]`: Get branch information
- `get_file_status() -> Dict[str, List[str]]`: Get file status

### `ab_reviewer.utils.logger`

Logging utilities.

```python
from ab_reviewer.utils.logger import setup_logger, get_logger

logger = setup_logger("my_module", level=logging.INFO, verbose=True)
logger = get_logger("my_module")
```

**Functions:**

- `setup_logger(name, level, log_file, verbose) -> logging.Logger`: Set up logger
- `get_logger(name) -> logging.Logger`: Get existing logger

## CLI Interface

### `ab_reviewer.cli`

Command-line interface for AB Code Reviewer.

```python
from ab_reviewer.cli import main, load_configuration, merge_configs
```

**Functions:**

- `main()`: Main CLI entry point
- `load_configuration(config_path, project_path) -> dict`: Load configuration
- `merge_configs(default, override) -> dict`: Merge configuration dictionaries

## Configuration Schema

### Default Configuration Structure

```yaml
project:
  type: python
  python_version: "3.8+"

tools:
  formatter:
    tool: black
    enabled: true
    args: ["--check", "--diff"]
  linter:
    tool: pylint
    enabled: true
    args: ["--output-format=text", "--score=no"]
  security:
    tool: bandit
    enabled: true
    args: ["-r", ".", "-f", "json"]
  tests:
    tool: pytest
    enabled: true
    args: ["--cov", "--cov-report=term-missing", "-v"]

ai:
  tool: gemini-cli
  enabled: true
  context:
    include_git_diff: true
    include_test_results: true
    max_context_lines: 1000
```

### Configuration Validation

The configuration is validated against the following rules:

1. **Required sections**: `project`, `tools`, `ai`
2. **Project type**: Must be one of `python`, `java`, `go`
3. **Tool configuration**: Each tool must have `enabled` (boolean) and `args` (list of strings)
4. **AI configuration**: Must have `enabled` (boolean) and `context` (dictionary)

## Error Handling

All modules use custom exceptions for consistent error handling:

```python
try:
    detector = ProjectDetector("/invalid/path")
except ProjectDetectionError as e:
    print(f"Project detection failed: {e}")
```

## Logging

Logging is configured with different levels:

- **DEBUG**: Detailed debugging information
- **INFO**: General information about operations
- **WARNING**: Warning messages for non-critical issues
- **ERROR**: Error messages for failures
- **CRITICAL**: Critical errors that prevent operation

## Caching

Tool results are cached to improve performance:

- **Cache key**: Based on tool name, arguments, project path, and file modification times
- **TTL**: Default 1 hour (3600 seconds)
- **Storage**: JSON files in `.ab-reviewer-cache/` directory
- **Invalidation**: Automatic based on file modification times

## Parallel Execution

Compatible tools can run in parallel:

- **Parallel tools**: formatter, linter, security
- **Sequential tools**: tests (depends on format/lint results)
- **Threading**: Uses `ThreadPoolExecutor` for parallel execution
- **Error handling**: Stops on first failure, cleans up running tasks
