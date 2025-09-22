# AB Code Reviewer Testing Workflow

This document explains how to use AB Code Reviewer to test and review separate projects with organized logging and reporting.

## 🎯 Overview

AB Code Reviewer now supports a comprehensive testing workflow that allows you to:
- Analyze project structure independently
- Run code reviews with organized logging
- Generate comprehensive reports
- Track progress over time
- Test multiple projects from a central location

## 📁 Directory Structure

```
AB_code_reviewer/
├── testing_projects/               # Independent project testing
│   ├── AB_santionAI/              # Test project 1
│   │   ├── structure/             # Project structure analysis
│   │   │   └── project_analysis.json
│   │   ├── reviews/               # Individual review runs
│   │   │   ├── 2024-09-21_18-07-53/
│   │   │   │   └── backend_2024-09-21_18-07-53.log
│   │   │   ├── 2024-09-21_18-15-22/
│   │   │   └── ...
│   │   └── reports/               # Generated reports
│   │       ├── report_2024-09-21_18-07-53.md
│   │       ├── report_2024-09-21_18-07-53.json
│   │       ├── report_2024-09-21_18-15-22.md
│   │       └── report_2024-09-21_18-15-22.json
│   ├── another_project/           # Test project 2
│   └── ...
├── logs/                          # Global application logs
└── config/                        # Global configuration
```

## 🚀 Quick Start

### 1. Project Analysis
```bash
# Analyze project structure
ab-reviewer --analyze --project-path /path/to/project --verbose

# Analyze with custom output directory
ab-reviewer --analyze --project-path /path/to/project --output-dir testing_projects/project_name/structure
```

### 2. Code Review
```bash
# Basic review
ab-reviewer --project-path /path/to/project

# Review with organized logging
ab-reviewer --project-path /path/to/project --output-dir testing_projects/project_name --timestamp-output --verbose

# Review with tool installation
ab-reviewer --project-path /path/to/project --output-dir testing_projects/project_name --install-tools --verbose
```

### 3. Report Generation
```bash
# Generate comprehensive reports
ab-reviewer --generate-report --project-dir testing_projects/project_name
```

## 🔧 Complete Workflow Example

### For AB_santionAI Project:
```bash
# 1. Setup
cd /Users/billyao/AB_code_reviewer
mkdir -p testing_projects/AB_santionAI/{structure,reviews,reports}

# 2. Analyze structure
ab-reviewer --analyze --project-path /Users/billyao/AB_santionAI/backend \
  --output-dir testing_projects/AB_santionAI/structure --verbose

# 3. Initial review
ab-reviewer --project-path /Users/billyao/AB_santionAI/backend \
  --output-dir testing_projects/AB_santionAI --timestamp-output \
  --verbose --install-tools

# 4. Generate reports
ab-reviewer --generate-report --project-dir testing_projects/AB_santionAI

# 5. View results
ls -la testing_projects/AB_santionAI/reports/
cat testing_projects/AB_santionAI/reports/report_2024-09-21_18-07-53.md
```

## 🤖 Automated Testing Script

Use the provided testing script for a complete automated workflow:

```bash
# Run complete testing workflow
python3 test_workflow.py
```

This script will:
1. Analyze project structure
2. Run initial code review
3. Generate comprehensive reports
4. Display results summary

## 📊 Report Types

### 1. Project Analysis Report
- **File:** `structure/project_analysis.json`
- **Content:** Project structure, file counts, dependencies, complexity analysis

### 2. Review Logs
- **File:** `reviews/TIMESTAMP/project_TIMESTAMP.log`
- **Content:** Detailed execution logs for each review run

### 3. Comprehensive Reports
- **Markdown:** `reports/report_YYYY-MM-DD_HH-MM-SS.md` - Human-readable report with timestamp
- **JSON:** `reports/report_YYYY-MM-DD_HH-MM-SS.json` - Machine-readable data with timestamp

**Report Features:**
- **Timestamped Filenames:** Each report includes generation timestamp for historical tracking
- **Comprehensive Analysis:** Project structure, quality gates, recommendations, and review history
- **Actionable Insights:** Priority-based recommendations with specific commands
- **Progress Tracking:** Historical review data for trend analysis

## 🎛️ CLI Options

### New Options Added:
- `--analyze`: Analyze project structure only
- `--output-dir`: Specify output directory for logs and reports
- `--timestamp-output`: Create timestamped output directories
- `--generate-report`: Generate comprehensive reports
- `--project-dir`: Project directory for report generation

### Example Commands:
```bash
# Analyze multiple projects
ab-reviewer --analyze --project-path /path/to/project1
ab-reviewer --analyze --project-path /path/to/project2

# Review with different configurations
ab-reviewer --project-path /path/to/project --output-dir testing_projects/project1 --timestamp-output
ab-reviewer --project-path /path/to/project --output-dir testing_projects/project2 --verbose

# Generate reports for all projects
ab-reviewer --generate-report --project-dir testing_projects/project1
ab-reviewer --generate-report --project-dir testing_projects/project2
```

## 📈 Benefits

1. **Independent Testing**: Each project is completely isolated
2. **Historical Tracking**: Compare results over time
3. **Structured Approach**: Analyze → Review → Fix → Review → Report
4. **Flexible Configuration**: Project-specific settings
5. **Comprehensive Reporting**: Multiple output formats
6. **Easy Management**: Clear directory structure

## 🔍 Troubleshooting

### Common Issues:

1. **Project not detected**: Ensure the project path contains Python files or requirements.txt
2. **Tools not found**: Use `--install-tools` to install missing dependencies
3. **Permission errors**: Ensure write permissions for output directories
4. **Timeout errors**: Large projects may need more time for analysis

### Debug Mode:
```bash
# Enable verbose logging
ab-reviewer --project-path /path/to/project --verbose --output-dir testing_projects/project_name
```

## 🚀 Next Steps

1. **Fix Issues**: Address any code quality issues found in the reports
2. **Re-run Reviews**: Use the same workflow to track improvements
3. **Compare Results**: Use the historical data to see progress
4. **Scale Up**: Apply this workflow to multiple projects
5. **Customize**: Modify configurations for specific project needs

## 📝 Configuration

### Project-Specific Configuration:
Create `testing_projects/project_name/config/.ab-reviewer.yaml`:
```yaml
project:
  name: "project_name"
  type: "python"

tools:
  formatter:
    enabled: true
    args: ["--check", "--diff"]
  linter:
    enabled: true
    args: ["--max-line-length=88"]
  security:
    enabled: true
  tests:
    enabled: true

ai:
  enabled: true
  context:
    include_git_diff: true
    max_context_lines: 2000
```

This testing workflow provides a professional, scalable approach to code review and quality assurance across multiple projects.
