"""Render profile reports for terminals and Markdown files."""

from __future__ import annotations

import json
from dataclasses import asdict

from .models import ProfileReport, TraceSummary


def render_text(report: ProfileReport) -> str:
    lines = [
        "log latency profile",
        f"traces: {report.trace_count} | events: {report.event_count} | parse errors: {report.parse_error_count}",
        f"latency ms: min={report.min_ms:.1f} median={report.median_ms:.1f} p95={report.p95_ms:.1f} max={report.max_ms:.1f}",
        "",
        "slow traces",
        _trace_table(report.slow_traces or report.traces),
    ]
    return "\n".join(lines).rstrip() + "\n"


def render_markdown(report: ProfileReport) -> str:
    rows = "\n".join(_trace_row(trace) for trace in (report.slow_traces or report.traces))
    threshold = "disabled" if report.slow_threshold_ms is None else f"{report.slow_threshold_ms:.0f} ms"

    return "\n".join(
        [
            "# Log Latency Profile",
            "",
            "| Metric | Value |",
            "|---|---:|",
            f"| Traces | {report.trace_count} |",
            f"| Events | {report.event_count} |",
            f"| Parse errors | {report.parse_error_count} |",
            f"| Median latency | {report.median_ms:.1f} ms |",
            f"| P95 latency | {report.p95_ms:.1f} ms |",
            f"| Max latency | {report.max_ms:.1f} ms |",
            f"| Slow threshold | {threshold} |",
            "",
            "## Slow Traces",
            "",
            "| Trace | Duration | Events | Services | Errors | First -> Last |",
            "|---|---:|---:|---|---:|---|",
            rows or "| - | 0.0 ms | 0 | - | 0 | - |",
            "",
        ]
    )


def render_json(report: ProfileReport) -> str:
    return json.dumps(asdict(report), default=str, indent=2, sort_keys=True) + "\n"


def _trace_table(traces: tuple[TraceSummary, ...]) -> str:
    if not traces:
        return "  no traces found"

    lines = ["  trace             duration   events  errors  services"]
    for trace in traces:
        services = ",".join(trace.services)
        lines.append(f"  {trace.trace_id[:16]:<16} {trace.duration_ms:>8.1f}ms {trace.event_count:>6} {trace.error_count:>7}  {services}")
    return "\n".join(lines)


def _trace_row(trace: TraceSummary) -> str:
    services = ", ".join(trace.services)
    messages = f"{_clean_cell(trace.first_message)} -> {_clean_cell(trace.last_message)}"
    return f"| `{trace.trace_id}` | {trace.duration_ms:.1f} ms | {trace.event_count} | {services} | {trace.error_count} | {messages} |"


def _clean_cell(value: str) -> str:
    return value.replace("|", "\\|").strip() or "-"
