"""Command line interface for log-latency-profiler."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import TextIO

from .analyzer import profile_events
from .models import ProfileReport
from .parser import parse_jsonl
from .render import render_json, render_markdown, render_text


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line argument parser."""
    parser = argparse.ArgumentParser(
        prog="log-latency-profiler",
        description="Profile request latency from JSONL logs grouped by trace or request id.",
    )
    parser.add_argument("input", help="JSONL log file path, or '-' for stdin")
    parser.add_argument("--format", choices=("text", "markdown", "json"), default="text", help="output format")
    parser.add_argument("--output", "-o", help="write the report to a file instead of stdout")
    parser.add_argument("--limit", type=int, default=10, help="maximum number of traces to print")
    parser.add_argument("--slow-threshold-ms", type=float, default=1000.0, help="minimum duration for slow trace reporting")
    parser.add_argument("--service", help="only include events from this service")
    parser.add_argument("--include-all", action="store_true", help="show the slowest traces even when below the threshold")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the command-line profiler and return a process exit code."""
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        lines = _read_lines(args.input, sys.stdin)
    except OSError as exc:
        parser.error(str(exc))

    threshold = None if args.include_all else args.slow_threshold_ms
    parsed = parse_jsonl(lines, service_filter=args.service)
    report = profile_events(
        parsed.events,
        parse_error_count=len(parsed.errors),
        slow_threshold_ms=threshold,
        limit=args.limit,
    )
    output = _render(report, args.format)

    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
    else:
        sys.stdout.write(output)

    return 1 if parsed.errors and not parsed.events else 0


def _read_lines(path: str, stdin: TextIO) -> list[str]:
    """Read input from a path or stdin sentinel."""
    if path == "-":
        return stdin.readlines()
    return Path(path).read_text(encoding="utf-8").splitlines()


def _render(report: ProfileReport, output_format: str) -> str:
    """Render a profile report in the requested output format."""
    if output_format == "markdown":
        return render_markdown(report)
    if output_format == "json":
        return render_json(report)
    return render_text(report)


if __name__ == "__main__":
    raise SystemExit(main())
