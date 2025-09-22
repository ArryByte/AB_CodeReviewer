"""Command-line interface for AB Code Reviewer."""

import os
import sys
from pathlib import Path
from typing import Optional

import click
import yaml

from ab_reviewer.core.detector import ProjectDetector
from ab_reviewer.core.runner import ToolRunner
from ab_reviewer.core.enhanced_runner import EnhancedToolRunner
from ab_reviewer.core.reporter import Reporter
from ab_reviewer.ai.gemini_client import GeminiClient
from ab_reviewer.tools.python_tools import PythonTools
from ab_reviewer.utils.exceptions import (
    ABReviewerError,
    ConfigurationError,
    ProjectDetectionError,
    ToolNotFoundError,
    ToolExecutionError,
    AIReviewError,
    ValidationError,
)
from ab_reviewer.utils.logger import setup_logger
from ab_reviewer.utils.project_analyzer import ProjectAnalyzer
from ab_reviewer.utils.report_generator import ReportGenerator


# Simple validation functions for MVP
def validate_python_version():
    """Validate Python version."""
    if sys.version_info < (3, 8):
        raise ValidationError(f"Python 3.8+ required, found {sys.version}")


def validate_configuration(config):
    """Validate configuration structure."""
    required_sections = ["project", "tools", "ai"]
    for section in required_sections:
        if section not in config:
            raise ConfigurationError(
                f"Missing required configuration section: {section}"
            )

    if config["project"]["type"] not in ["python"]:
        raise ConfigurationError(
            f"Unsupported project type: {config['project']['type']}"
        )


@click.command()
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True, path_type=Path),
    help="Path to configuration file (.ab-reviewer.yaml)",
)
@click.option(
    "--report",
    "-r",
    type=click.Path(path_type=Path),
    help="Save markdown report to file",
)
@click.option(
    "--project-path",
    "-p",
    type=click.Path(exists=True, path_type=Path),
    default=".",
    help="Project path to review (default: current directory)",
)
@click.option(
    "--install-tools", is_flag=True, help="Install missing Python tools automatically"
)
@click.option("--setup", is_flag=True, help="Set up project with default configuration")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.option("--analyze", is_flag=True, help="Analyze project structure only")
@click.option(
    "--output-dir",
    type=click.Path(path_type=Path),
    help="Output directory for logs and reports",
)
@click.option(
    "--timestamp-output", is_flag=True, help="Create timestamped output directories"
)
@click.option("--generate-report", is_flag=True, help="Generate comprehensive report")
@click.option(
    "--project-dir",
    type=click.Path(path_type=Path),
    help="Project directory for report generation",
)
@click.option(
    "--progressive",
    is_flag=True,
    help="Use progressive quality gates (continue even if some fail)",
)
@click.option(
    "--dry-run",
    "--skip-gemini",
    is_flag=True,
    help="Skip AI review (dry run mode) - useful for testing without Gemini CLI",
)
def main(
    config: Optional[Path],
    report: Optional[Path],
    project_path: Path,
    install_tools: bool,
    setup: bool,
    verbose: bool,
    analyze: bool,
    output_dir: Optional[Path],
    timestamp_output: bool,
    generate_report: bool,
    project_dir: Optional[Path],
    progressive: bool,
    dry_run: bool,
) -> None:
    """
    AB Code Reviewer - Automated code review workflow with AI integration.

    Args:
        config: Path to configuration file
        report: Path to save markdown report
        project_path: Project path to review
        install_tools: Install missing tools automatically
        setup: Set up project with default configuration
        verbose: Enable verbose output
    """
    try:
        # Validate Python version
        validate_python_version()

        # Handle project analysis mode
        if analyze:
            click.echo(f"🔍 Analyzing project structure at: {project_path}")
            analyzer = ProjectAnalyzer(project_path)

            # Set up output directory
            if output_dir:
                output_path = output_dir
            else:
                output_path = Path("testing_projects") / project_path.name / "structure"

            analysis_file = analyzer.save_analysis(output_path)
            click.echo(f"✅ Project analysis saved to: {analysis_file}")
            return

        # Handle report generation mode
        if generate_report:
            if not project_dir:
                click.echo("❌ --project-dir is required for report generation")
                sys.exit(1)

            click.echo(f"📊 Generating report for project: {project_dir}")

            try:
                report_generator = ReportGenerator(project_dir)

                # Generate and save reports
                md_report = report_generator.save_markdown_report()
                json_report = report_generator.save_json_report()

                click.echo(f"✅ Markdown report saved to: {md_report}")
                click.echo(f"✅ JSON report saved to: {json_report}")

                # Show summary
                report_data = report_generator.generate_comprehensive_report()
                summary = report_data.get("summary", {})
                click.echo("\n📈 Summary:")
                click.echo(f"  - Total Reviews: {summary.get('total_reviews', 0)}")
                click.echo(
                    f"  - Project Health: {summary.get('overall_health', 'unknown').title()}"
                )
                click.echo(
                    f"  - Recommendations: {len(report_data.get('recommendations', []))}"
                )

            except Exception as e:
                click.echo(f"❌ Report generation failed: {str(e)}")
                sys.exit(1)

            return

        # Set up logging
        log_dir = None
        if output_dir:
            if timestamp_output:
                from datetime import datetime

                timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                log_dir = output_dir / f"reviews/{timestamp}"
            else:
                log_dir = output_dir / "reviews/latest"

        setup_logger(
            level=20 if verbose else 30, log_dir=log_dir, project_name=project_path.name
        )

        # Change to project directory
        os.chdir(project_path)

        if verbose:
            click.echo(f"🔍 Reviewing project at: {project_path}")

        # Set up project if requested
        if setup:
            click.echo("🔧 Setting up project...")
            try:
                python_tools = PythonTools(str(project_path))
                if python_tools.setup_project():
                    click.echo("✅ Project setup completed")
                else:
                    click.echo("❌ Project setup failed")
                    sys.exit(1)
            except Exception as e:
                click.echo(f"❌ Project setup failed: {str(e)}")
                sys.exit(1)
            return

        # Load configuration
        try:
            config_data = load_configuration(config, project_path)
            validate_configuration(config_data)
        except ConfigurationError as e:
            click.echo(f"❌ Configuration error: {str(e)}")
            sys.exit(1)

        # Detect project type
        try:
            detector = ProjectDetector(str(project_path))
            project_info = detector.get_project_info()
        except ProjectDetectionError as e:
            click.echo(f"❌ Project detection error: {str(e)}")
            sys.exit(1)

        if project_info["type"] != "python":
            click.echo(f"❌ Unsupported project type: {project_info['type']}")
            click.echo("Currently only Python projects are supported.")
            sys.exit(1)

        # Validate environment
        try:
            python_tools = PythonTools(str(project_path))
            env_valid, issues = python_tools.validate_environment()
        except Exception as e:
            click.echo(f"❌ Environment validation failed: {str(e)}")
            sys.exit(1)

        if not env_valid:
            click.echo("⚠️  Environment issues found:")
            for issue in issues:
                click.echo(f"  - {issue}")

            if install_tools:
                click.echo("🔧 Installing missing tools...")
                try:
                    if python_tools.install_tools():
                        click.echo("✅ Tools installed successfully")
                    else:
                        click.echo("❌ Failed to install tools")
                        sys.exit(1)
                except Exception as e:
                    click.echo(f"❌ Tool installation failed: {str(e)}")
                    sys.exit(1)
            else:
                click.echo("💡 Run with --install-tools to install missing dependencies")
                sys.exit(1)

        # Run quality gates
        try:
            # Choose runner based on progressive flag
            if progressive:
                runner = EnhancedToolRunner(str(project_path), config_data)
                click.echo(
                    "🚀 Using progressive quality gates (continuing even if some fail)"
                )
            else:
                runner = ToolRunner(str(project_path), config_data)
                click.echo("🔒 Using strict quality gates (all must pass)")

            tool_results = runner.run_quality_gates()
        except (ToolNotFoundError, ToolExecutionError) as e:
            click.echo(f"❌ Tool execution error: {str(e)}")
            sys.exit(1)

        # Run AI review if quality gates allow it
        ai_output = None
        if runner.can_proceed_to_ai_review():
            click.echo("🤖 Running AI review...")
            try:
                gemini_client = GeminiClient(str(project_path), dry_run=dry_run)

                if gemini_client.is_available():
                    success, output = gemini_client.run_review(
                        tool_results, config_data
                    )
                    if success:
                        ai_output = output
                        click.echo("✅ AI review completed")
                    else:
                        click.echo(f"❌ AI review failed: {output}")
                else:
                    click.echo("⚠️  Gemini CLI not found, skipping AI review")
            except AIReviewError as e:
                click.echo(f"❌ AI review error: {str(e)}")
        else:
            click.echo("⏭️  Skipping AI review due to failed quality gates")

            # Show recovery suggestions if using enhanced runner
            if progressive and hasattr(runner, "get_recovery_suggestions"):
                suggestions = runner.get_recovery_suggestions()
                if suggestions:
                    click.echo("\n💡 Recovery suggestions:")
                    for suggestion in suggestions:
                        priority_emoji = {
                            "high": "🔴",
                            "medium": "🟡",
                            "low": "🟢",
                        }.get(suggestion["priority"], "⚪")
                        click.echo(
                            f"  {priority_emoji} {suggestion['gate']}: {suggestion['suggestion']}"
                        )
                        click.echo(f"     Command: {suggestion['command']}")

        # Generate reports
        try:
            reporter = Reporter(str(project_path))

            # Terminal report
            reporter.print_terminal_report(project_info, tool_results, ai_output)

            # Markdown report if requested
            if report:
                report_path = reporter.save_markdown_report(
                    project_info, tool_results, ai_output, str(report)
                )
                click.echo(f"📄 Report saved to: {report_path}")
        except Exception as e:
            click.echo(f"❌ Report generation failed: {str(e)}")
            sys.exit(1)

        # Exit with appropriate code
        if not runner.all_tools_passed():
            sys.exit(1)

    except ABReviewerError as e:
        click.echo(f"❌ AB Code Reviewer error: {str(e)}")
        sys.exit(1)
    except KeyboardInterrupt:
        click.echo("\n⚠️  Review interrupted by user")
        sys.exit(130)
    except Exception as e:
        click.echo(f"❌ Unexpected error: {str(e)}")
        if verbose:
            import traceback

            click.echo(traceback.format_exc())
        sys.exit(1)


def load_configuration(config_path: Optional[Path], project_path: Path) -> dict:
    """Load configuration from file or use defaults."""
    # Load default configuration
    default_config_path = Path(__file__).parent / "config" / "default_config.yaml"
    with open(default_config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    # Override with project-specific config if provided
    if config_path:
        with open(config_path, "r", encoding="utf-8") as f:
            project_config = yaml.safe_load(f)
            config = merge_configs(config, project_config)
    else:
        # Look for .ab-reviewer.yaml in project root
        project_config_path = project_path / ".ab-reviewer.yaml"
        if project_config_path.exists():
            with open(project_config_path, "r", encoding="utf-8") as f:
                project_config = yaml.safe_load(f)
                config = merge_configs(config, project_config)

    return config


def merge_configs(default: dict, override: dict) -> dict:
    """Recursively merge configuration dictionaries."""
    result = default.copy()

    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_configs(result[key], value)
        else:
            result[key] = value

    return result


if __name__ == "__main__":
    main()
