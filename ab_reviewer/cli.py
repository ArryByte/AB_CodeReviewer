"""Command-line interface for AB Code Reviewer."""

import os
import sys
from pathlib import Path
from typing import Optional

import click
import yaml

from ab_reviewer.core.detector import ProjectDetector
from ab_reviewer.core.runner import ToolRunner
from ab_reviewer.core.reporter import Reporter
from ab_reviewer.ai.gemini_client import GeminiClient
from ab_reviewer.tools.python_tools import PythonTools
from ab_reviewer.utils.exceptions import (
    ABReviewerError, ConfigurationError, ProjectDetectionError,
    ToolNotFoundError, ToolExecutionError, AIReviewError, ValidationError
)
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
            raise ConfigurationError(f"Missing required configuration section: {section}")
    
    if config["project"]["type"] not in ["python"]:
        raise ConfigurationError(f"Unsupported project type: {config['project']['type']}")


@click.command()
@click.option(
    "--config", "-c",
    type=click.Path(exists=True, path_type=Path),
    help="Path to configuration file (.ab-reviewer.yaml)"
)
@click.option(
    "--report", "-r",
    type=click.Path(path_type=Path),
    help="Save markdown report to file"
)
@click.option(
    "--project-path", "-p",
    type=click.Path(exists=True, path_type=Path),
    default=".",
    help="Project path to review (default: current directory)"
)
@click.option(
    "--install-tools",
    is_flag=True,
    help="Install missing Python tools automatically"
)
@click.option(
    "--setup",
    is_flag=True,
    help="Set up project with default configuration"
)
@click.option(
    "--verbose", "-v",
    is_flag=True,
    help="Enable verbose output"
)
def main(
    config: Optional[Path],
    report: Optional[Path],
    project_path: Path,
    install_tools: bool,
    setup: bool,
    verbose: bool
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
            runner = ToolRunner(str(project_path), config_data)
            tool_results = runner.run_quality_gates()
        except (ToolNotFoundError, ToolExecutionError) as e:
            click.echo(f"❌ Tool execution error: {str(e)}")
            sys.exit(1)
        
        # Run AI review if quality gates passed
        ai_output = None
        if runner.all_tools_passed():
            click.echo("🤖 Running AI review...")
            try:
                gemini_client = GeminiClient(str(project_path))
                
                if gemini_client.is_available():
                    success, output = gemini_client.run_review(tool_results, config_data)
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
    with open(default_config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # Override with project-specific config if provided
    if config_path:
        with open(config_path, 'r', encoding='utf-8') as f:
            project_config = yaml.safe_load(f)
            config = merge_configs(config, project_config)
    else:
        # Look for .ab-reviewer.yaml in project root
        project_config_path = project_path / ".ab-reviewer.yaml"
        if project_config_path.exists():
            with open(project_config_path, 'r', encoding='utf-8') as f:
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
