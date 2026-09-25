"""
Shared Helpers — Common utilities used across the framework.
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


def get_model() -> str:
    """Get the configured model name."""
    return os.getenv("OPENAI_MODEL", "gpt-4o-mini")


def load_json(path: str) -> list | dict:
    """Load and parse a JSON file."""
    with open(path) as f:
        return json.load(f)


def save_json(data: list | dict, path: str) -> None:
    """Save data to a JSON file, creating directories as needed."""
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2, default=str)


def timestamp() -> str:
    """Return an ISO 8601 UTC timestamp."""
    return datetime.now(timezone.utc).isoformat()


def format_eval_report(results: dict, title: str = "Evaluation Report") -> str:
    """Format evaluation results as a readable markdown report."""
    lines = [
        f"# {title}",
        f"**Generated:** {timestamp()}",
        "",
        "## Summary",
        f"- **Total test cases:** {results.get('total', 'N/A')}",
        f"- **Passed:** {results.get('passed', 'N/A')}",
        f"- **Failed:** {results.get('failed', 'N/A')}",
        f"- **Pass rate:** {results.get('pass_rate', 0):.1%}",
        "",
    ]

    if "details" in results:
        lines.append("## Details")
        lines.append("")
        lines.append("| Input | Passed | Metrics |")
        lines.append("|---|---|---|")

        for detail in results["details"]:
            input_text = detail.get("input", "")[:50]
            status = "PASS" if detail.get("passed") else "FAIL"
            metrics_str = ", ".join(
                f"{name}: {data.get('score', 'N/A'):.2f}"
                for name, data in detail.get("metrics", {}).items()
                if isinstance(data.get("score"), (int, float))
            )
            lines.append(f"| {input_text} | {status} | {metrics_str} |")

    return "\n".join(lines)
