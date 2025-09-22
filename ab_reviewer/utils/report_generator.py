"""Report generation utilities for AB Code Reviewer."""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional


class ReportGenerator:
    """Generates comprehensive reports from review results."""

    def __init__(self, project_dir: Path):
        """
        Initialize report generator.

        Args:
            project_dir: Directory containing project review data
        """
        self.project_dir = project_dir.resolve()
        self.project_name = self.project_dir.name

    def generate_comprehensive_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive report from all available data.

        Returns:
            Dictionary containing comprehensive report data
        """
        report = {
            "project_name": self.project_name,
            "generated_at": datetime.now().isoformat(),
            "project_analysis": self._load_project_analysis(),
            "review_history": self._load_review_history(),
            "summary": self._generate_summary(),
            "recommendations": self._generate_recommendations(),
        }

        return report

    def _load_project_analysis(self) -> Optional[Dict[str, Any]]:
        """Load project analysis data."""
        analysis_file = self.project_dir / "structure" / "project_analysis.json"
        if analysis_file.exists():
            with open(analysis_file, "r") as f:
                return json.load(f)
        return None

    def _load_review_history(self) -> List[Dict[str, Any]]:
        """Load review history from all review runs."""
        reviews_dir = self.project_dir / "reviews"
        if not reviews_dir.exists():
            return []

        review_history = []

        # Get all review directories, sorted by timestamp
        review_dirs = sorted([d for d in reviews_dir.iterdir() if d.is_dir()])

        for review_dir in review_dirs:
            review_data = self._load_single_review(review_dir)
            if review_data:
                review_history.append(review_data)

        return review_history

    def _load_single_review(self, review_dir: Path) -> Optional[Dict[str, Any]]:
        """Load data from a single review run."""
        review_data = {
            "timestamp": review_dir.name,
            "log_file": None,
            "quality_gates": None,
            "ai_review": None,
            "summary": None,
        }

        # Look for log file
        log_files = list(review_dir.glob("*.log"))
        if log_files:
            review_data["log_file"] = str(log_files[0])

        # Look for quality gates results
        quality_file = review_dir / "quality_gates.json"
        if quality_file.exists():
            with open(quality_file, "r") as f:
                review_data["quality_gates"] = json.load(f)

        # Look for AI review
        ai_review_file = review_dir / "ai_review.md"
        if ai_review_file.exists():
            with open(ai_review_file, "r") as f:
                review_data["ai_review"] = f.read()

        # Look for summary
        summary_file = review_dir / "summary.json"
        if summary_file.exists():
            with open(summary_file, "r") as f:
                review_data["summary"] = json.load(f)

        return review_data

    def _generate_summary(self) -> Dict[str, Any]:
        """Generate summary statistics."""
        analysis = self._load_project_analysis()
        reviews = self._load_review_history()

        summary = {
            "total_reviews": len(reviews),
            "project_complexity": "unknown",
            "overall_health": "unknown",
            "quality_trends": {},
            "common_issues": [],
        }

        if analysis:
            summary["project_complexity"] = analysis.get(
                "estimated_complexity", {}
            ).get("complexity_level", "unknown")
            summary["total_files"] = analysis.get("file_structure", {}).get(
                "total_files", 0
            )
            summary["python_files"] = analysis.get("python_files", {}).get(
                "total_python_files", 0
            )

        # Analyze quality trends
        if reviews:
            quality_trends = {
                "formatter": {"passed": 0, "failed": 0},
                "linter": {"passed": 0, "failed": 0},
                "security": {"passed": 0, "failed": 0},
                "tests": {"passed": 0, "failed": 0},
            }

            for review in reviews:
                if review.get("quality_gates"):
                    gates = review["quality_gates"]
                    for tool, result in gates.items():
                        if tool in quality_trends:
                            if result.get("success", False):
                                quality_trends[tool]["passed"] += 1
                            else:
                                quality_trends[tool]["failed"] += 1

            summary["quality_trends"] = quality_trends

            # Determine overall health
            total_checks = sum(sum(trend.values()) for trend in quality_trends.values())
            total_passed = sum(trend["passed"] for trend in quality_trends.values())

            if total_checks > 0:
                pass_rate = total_passed / total_checks
                if pass_rate >= 0.8:
                    summary["overall_health"] = "good"
                elif pass_rate >= 0.6:
                    summary["overall_health"] = "fair"
                else:
                    summary["overall_health"] = "needs_improvement"

        return summary

    def _generate_recommendations(self) -> List[Dict[str, str]]:
        """Generate actionable recommendations."""
        recommendations = []
        analysis = self._load_project_analysis()
        reviews = self._load_review_history()

        # Project structure recommendations
        if analysis:
            file_structure = analysis.get("file_structure", {})
            if file_structure.get("total_files", 0) > 100:
                recommendations.append(
                    {
                        "category": "structure",
                        "priority": "medium",
                        "title": "Consider modularizing large project",
                        "description": f"Project has {file_structure['total_files']} files. Consider breaking into smaller modules.",
                    }
                )

            python_files = analysis.get("python_files", {})
            if python_files.get("total_python_files", 0) > 50:
                recommendations.append(
                    {
                        "category": "structure",
                        "priority": "low",
                        "title": "Add type hints",
                        "description": "Large Python codebase would benefit from type hints for better maintainability.",
                    }
                )

        # Quality gate recommendations
        if reviews:
            latest_review = reviews[-1] if reviews else None
            if latest_review and latest_review.get("quality_gates"):
                gates = latest_review["quality_gates"]

                if not gates.get("formatter", {}).get("success", True):
                    recommendations.append(
                        {
                            "category": "code_quality",
                            "priority": "high",
                            "title": "Fix code formatting",
                            "description": "Run black formatter to fix code style issues.",
                        }
                    )

                if not gates.get("linter", {}).get("success", True):
                    recommendations.append(
                        {
                            "category": "code_quality",
                            "priority": "high",
                            "title": "Fix linting issues",
                            "description": "Address pylint warnings and errors.",
                        }
                    )

                if not gates.get("security", {}).get("success", True):
                    recommendations.append(
                        {
                            "category": "security",
                            "priority": "high",
                            "title": "Fix security issues",
                            "description": "Address security vulnerabilities found by bandit.",
                        }
                    )

                if not gates.get("tests", {}).get("success", True):
                    recommendations.append(
                        {
                            "category": "testing",
                            "priority": "medium",
                            "title": "Fix failing tests",
                            "description": "Ensure all tests pass before deployment.",
                        }
                    )

        # General recommendations
        if not analysis or not analysis.get("git_info", {}).get("is_git_repo", False):
            recommendations.append(
                {
                    "category": "version_control",
                    "priority": "medium",
                    "title": "Initialize git repository",
                    "description": "Project should be under version control.",
                }
            )

        return recommendations

    def save_markdown_report(self, output_path: Optional[Path] = None) -> Path:
        """
        Save comprehensive report as Markdown.

        Args:
            output_path: Path to save report (defaults to project_dir/reports/)

        Returns:
            Path to saved report file
        """
        if output_path is None:
            reports_dir = self.project_dir / "reports"
            reports_dir.mkdir(exist_ok=True)
            # Use timestamped filename format
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            output_path = reports_dir / f"report_{timestamp}.md"

        report_data = self.generate_comprehensive_report()

        with open(output_path, "w") as f:
            f.write(self._format_markdown_report(report_data))

        return output_path

    def _format_markdown_report(self, report_data: Dict[str, Any]) -> str:
        """Format report data as Markdown."""
        md = []

        # Header
        md.append(f"# AB Code Reviewer Report: {report_data['project_name']}")
        md.append(f"**Generated:** {report_data['generated_at']}")
        md.append("")

        # Summary
        summary = report_data.get("summary", {})
        md.append("## 📊 Summary")
        md.append(f"- **Total Reviews:** {summary.get('total_reviews', 0)}")
        md.append(
            f"- **Project Complexity:** {summary.get('project_complexity', 'unknown').title()}"
        )
        md.append(
            f"- **Overall Health:** {summary.get('overall_health', 'unknown').title()}"
        )
        md.append("")

        # Project Analysis
        analysis = report_data.get("project_analysis")
        if analysis:
            md.append("## 🔍 Project Analysis")
            file_structure = analysis.get("file_structure", {})
            md.append(f"- **Total Files:** {file_structure.get('total_files', 0)}")
            md.append(
                f"- **Python Files:** {analysis.get('python_files', {}).get('total_python_files', 0)}"
            )
            md.append(
                f"- **Directories:** {file_structure.get('total_directories', 0)}"
            )
            md.append("")

        # Quality Trends
        quality_trends = summary.get("quality_trends", {})
        if quality_trends:
            md.append("## 🔧 Quality Trends")
            for tool, trend in quality_trends.items():
                total = trend["passed"] + trend["failed"]
                if total > 0:
                    pass_rate = (trend["passed"] / total) * 100
                    md.append(
                        f"- **{tool.title()}:** {trend['passed']}/{total} ({pass_rate:.1f}% pass rate)"
                    )
            md.append("")

        # Recommendations
        recommendations = report_data.get("recommendations", [])
        if recommendations:
            md.append("## 💡 Recommendations")
            for rec in recommendations:
                priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(
                    rec["priority"], "⚪"
                )
                md.append(f"### {priority_emoji} {rec['title']}")
                md.append(f"**Category:** {rec['category']}")
                md.append(f"**Description:** {rec['description']}")
                md.append("")

        # Review History
        reviews = report_data.get("review_history", [])
        if reviews:
            md.append("## 📈 Review History")
            for review in reviews[-5:]:  # Show last 5 reviews
                md.append(f"### {review['timestamp']}")
                if review.get("quality_gates"):
                    gates = review["quality_gates"]
                    for tool, result in gates.items():
                        status = "✅" if result.get("success", False) else "❌"
                        md.append(f"- **{tool.title()}:** {status}")
                md.append("")

        return "\n".join(md)

    def save_json_report(self, output_path: Optional[Path] = None) -> Path:
        """
        Save comprehensive report as JSON.

        Args:
            output_path: Path to save report (defaults to project_dir/reports/)

        Returns:
            Path to saved report file
        """
        if output_path is None:
            reports_dir = self.project_dir / "reports"
            reports_dir.mkdir(exist_ok=True)
            # Use timestamped filename format
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            output_path = reports_dir / f"report_{timestamp}.json"

        report_data = self.generate_comprehensive_report()

        with open(output_path, "w") as f:
            json.dump(report_data, f, indent=2)

        return output_path
