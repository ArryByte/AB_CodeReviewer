"""Report generation for AB Code Reviewer."""

import os
from pathlib import Path
from typing import Dict, Any, Optional
from colorama import Fore, Style, init

# Initialize colorama for cross-platform colored output
init(autoreset=True)


class Reporter:
    """Generates reports for code review results."""

    def __init__(self, project_path: str = "."):
        """Initialize reporter with project path."""
        self.project_path = Path(project_path).resolve()

    def print_terminal_report(
        self,
        project_info: Dict[str, Any],
        tool_results: Dict[str, Any],
        ai_output: Optional[str] = None,
    ) -> None:
        """Print formatted terminal report."""
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"{Fore.CYAN}AB CODE REVIEWER REPORT")
        print(f"{Fore.CYAN}{'='*60}")

        # Project info
        print(f"\n{Fore.YELLOW}📁 Project Information:")
        print(f"  Type: {project_info.get('type', 'unknown')}")
        print(f"  Path: {project_info.get('path', 'unknown')}")
        print(f"  Git Repo: {'Yes' if project_info.get('is_git_repo') else 'No'}")

        # Tool results
        print(f"\n{Fore.YELLOW}🔧 Quality Gates:")
        for tool_name, result in tool_results.items():
            status = "✅ PASSED" if result.get("success") else "❌ FAILED"
            color = Fore.GREEN if result.get("success") else Fore.RED
            print(f"  {tool_name.capitalize()}: {color}{status}")

            # Show output for failed tools
            if not result.get("success") and result.get("output"):
                print(f"    {Fore.RED}Output: {result['output'][:200]}...")

        # AI Review
        if ai_output:
            print(f"\n{Fore.YELLOW}🤖 AI Review (Gemini CLI):")
            print(f"{Fore.WHITE}{ai_output}")
        else:
            print(f"\n{Fore.YELLOW}🤖 AI Review: Skipped (quality gates failed)")

        # Summary
        failed_tools = [
            name for name, result in tool_results.items() if not result.get("success")
        ]

        if failed_tools:
            print(f"\n{Fore.RED}❌ Review failed due to: {', '.join(failed_tools)}")
            print(f"{Fore.RED}Fix these issues before running AI review.")
        else:
            print(f"\n{Fore.GREEN}✅ All quality gates passed!")
            if ai_output:
                print(f"{Fore.GREEN}AI review completed successfully.")

        print(f"\n{Fore.CYAN}{'='*60}")

    def save_markdown_report(
        self,
        project_info: Dict[str, Any],
        tool_results: Dict[str, Any],
        ai_output: Optional[str] = None,
        output_file: str = "review_report.md",
    ) -> str:
        """Save report to markdown file."""
        report_path = self.project_path / output_file

        with open(report_path, "w", encoding="utf-8") as f:
            f.write("# AB Code Reviewer Report\n\n")

            # Project info
            f.write("## Project Information\n\n")
            f.write(f"- **Type**: {project_info.get('type', 'unknown')}\n")
            f.write(f"- **Path**: {project_info.get('path', 'unknown')}\n")
            f.write(
                f"- **Git Repository**: {'Yes' if project_info.get('is_git_repo') else 'No'}\n\n"
            )

            # Tool results
            f.write("## Quality Gates\n\n")
            for tool_name, result in tool_results.items():
                status = "✅ PASSED" if result.get("success") else "❌ FAILED"
                f.write(f"- **{tool_name.capitalize()}**: {status}\n")

                if not result.get("success") and result.get("output"):
                    f.write(f"  ```\n  {result['output'][:500]}...\n  ```\n")

            # AI Review
            if ai_output:
                f.write("\n## AI Review (Gemini CLI)\n\n")
                f.write("```\n")
                f.write(ai_output)
                f.write("\n```\n")
            else:
                f.write("\n## AI Review\n\nSkipped due to failed quality gates.\n")

            # Summary
            failed_tools = [
                name
                for name, result in tool_results.items()
                if not result.get("success")
            ]

            f.write("\n## Summary\n\n")
            if failed_tools:
                f.write(f"❌ **Review failed** due to: {', '.join(failed_tools)}\n")
                f.write("Fix these issues before running AI review.\n")
            else:
                f.write("✅ **All quality gates passed!**\n")
                if ai_output:
                    f.write("AI review completed successfully.\n")

        return str(report_path)
