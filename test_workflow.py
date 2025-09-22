#!/usr/bin/env python3
"""
AB Code Reviewer Testing Workflow Script

This script demonstrates the complete testing workflow for AB Code Reviewer.
It shows how to use the tool to analyze and review separate projects.
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd, description):
    """Run a command and display results."""
    print(f"\n{'='*60}")
    print(f"🔧 {description}")
    print(f"{'='*60}")
    print(f"Running: {' '.join(cmd)}")
    print("-" * 60)

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print("❌ Command timed out")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Main testing workflow."""
    print("🚀 AB Code Reviewer Testing Workflow")
    print("=" * 60)

    # Configuration
    project_path = "/Users/billyao/AB_santionAI/backend"
    testing_dir = Path("testing_projects/AB_santionAI")

    # Step 1: Project Analysis
    print("\n📋 Step 1: Project Structure Analysis")
    success = run_command(
        [
            "ab-reviewer",
            "--analyze",
            "--project-path",
            project_path,
            "--output-dir",
            str(testing_dir / "structure"),
            "--verbose",
        ],
        "Analyzing project structure",
    )

    if not success:
        print("❌ Project analysis failed")
        return 1

    # Step 2: Initial Review
    print("\n📋 Step 2: Initial Code Review")
    success = run_command(
        [
            "ab-reviewer",
            "--project-path",
            project_path,
            "--output-dir",
            str(testing_dir),
            "--timestamp-output",
            "--verbose",
            "--install-tools",
        ],
        "Running initial code review with tool installation",
    )

    if not success:
        print("⚠️  Initial review completed with issues (expected)")

    # Step 3: Generate Reports
    print("\n📋 Step 3: Generate Comprehensive Reports")
    success = run_command(
        ["ab-reviewer", "--generate-report", "--project-dir", str(testing_dir)],
        "Generating comprehensive reports",
    )

    if not success:
        print("❌ Report generation failed")
        return 1

    # Step 4: Show Results
    print("\n📋 Step 4: Review Results")
    print("=" * 60)

    # Show directory structure
    print("📁 Generated Directory Structure:")
    for item in testing_dir.rglob("*"):
        if item.is_file():
            rel_path = item.relative_to(testing_dir)
            print(f"  📄 {rel_path}")

    # Show report summary
    report_file = testing_dir / "reports" / "comprehensive_report.md"
    if report_file.exists():
        print(f"\n📊 Report Summary (from {report_file}):")
        with open(report_file, "r") as f:
            content = f.read()
            # Show first few lines
            lines = content.split("\n")[:10]
            for line in lines:
                if line.strip():
                    print(f"  {line}")

    print("\n✅ Testing workflow completed successfully!")
    print("\n💡 Next Steps:")
    print("  1. Review the generated reports in testing_projects/AB_santionAI/reports/")
    print("  2. Fix any code quality issues found")
    print("  3. Run another review to see improvements")
    print("  4. Use this workflow for other projects")

    return 0


if __name__ == "__main__":
    sys.exit(main())
