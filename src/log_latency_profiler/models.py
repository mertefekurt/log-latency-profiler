"""Domain models used by the latency profiler."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class LogEvent:
    occurred_at: datetime
    trace_id: str
    service: str
    level: str
    message: str
    raw: dict[str, Any]
    line_number: int


@dataclass(frozen=True)
class ParseError:
    line_number: int
    reason: str
    content: str


@dataclass(frozen=True)
class ParseResult:
    events: tuple[LogEvent, ...]
    errors: tuple[ParseError, ...]


@dataclass(frozen=True)
class TraceSummary:
    trace_id: str
    started_at: datetime
    ended_at: datetime
    duration_ms: float
    event_count: int
    services: tuple[str, ...]
    error_count: int
    first_message: str
    last_message: str


@dataclass(frozen=True)
class ProfileReport:
    trace_count: int
    event_count: int
    parse_error_count: int
    min_ms: float
    median_ms: float
    p95_ms: float
    max_ms: float
    slow_threshold_ms: float | None
    slow_traces: tuple[TraceSummary, ...]
    traces: tuple[TraceSummary, ...]
