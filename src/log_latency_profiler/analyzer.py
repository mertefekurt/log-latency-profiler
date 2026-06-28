"""Build latency profiles from normalized log events."""

from __future__ import annotations

from collections import defaultdict

from .models import LogEvent, ProfileReport, TraceSummary


def profile_events(
    events: tuple[LogEvent, ...],
    *,
    parse_error_count: int = 0,
    slow_threshold_ms: float | None = 1000.0,
    limit: int = 10,
) -> ProfileReport:
    """Aggregate events into trace-level latency and error summaries."""
    groups: dict[str, list[LogEvent]] = defaultdict(list)
    for event in events:
        groups[event.trace_id].append(event)

    traces = tuple(
        sorted(
            (_summarize(trace_id, grouped) for trace_id, grouped in groups.items()),
            key=lambda item: item.duration_ms,
            reverse=True,
        )
    )
    durations = sorted(trace.duration_ms for trace in traces)
    slow_traces = tuple(
        trace
        for trace in traces
        if slow_threshold_ms is not None and trace.duration_ms >= slow_threshold_ms
    )[:limit]

    return ProfileReport(
        trace_count=len(traces),
        event_count=len(events),
        parse_error_count=parse_error_count,
        min_ms=durations[0] if durations else 0.0,
        median_ms=_percentile(durations, 50),
        p95_ms=_percentile(durations, 95),
        max_ms=durations[-1] if durations else 0.0,
        slow_threshold_ms=slow_threshold_ms,
        slow_traces=slow_traces,
        traces=traces[:limit],
    )


def _summarize(trace_id: str, events: list[LogEvent]) -> TraceSummary:
    """Create a single trace summary from normalized events."""
    ordered = sorted(events, key=lambda event: event.occurred_at)
    started_at = ordered[0].occurred_at
    ended_at = ordered[-1].occurred_at
    duration_ms = max((ended_at - started_at).total_seconds() * 1000, 0.0)
    services = tuple(sorted({event.service for event in ordered}))
    error_count = sum(1 for event in ordered if event.level in {"error", "fatal", "critical", "5xx"})

    return TraceSummary(
        trace_id=trace_id,
        started_at=started_at,
        ended_at=ended_at,
        duration_ms=duration_ms,
        event_count=len(ordered),
        services=services,
        error_count=error_count,
        first_message=ordered[0].message,
        last_message=ordered[-1].message,
    )


def _percentile(values: list[float], percentile: float) -> float:
    """Calculate a percentile using linear interpolation between ranks."""
    if not values:
        return 0.0
    if len(values) == 1:
        return values[0]

    rank = (len(values) - 1) * (percentile / 100)
    lower = int(rank)
    upper = min(lower + 1, len(values) - 1)
    weight = rank - lower
    return values[lower] * (1 - weight) + values[upper] * weight
