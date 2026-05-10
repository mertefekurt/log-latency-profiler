"""Parse JSONL logs into normalized events."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Iterable

from .models import LogEvent, ParseError, ParseResult

TIMESTAMP_KEYS = ("timestamp", "@timestamp", "time", "ts", "datetime", "date")
TRACE_KEYS = ("trace_id", "traceId", "request_id", "requestId", "correlation_id", "correlationId", "span_id")
SERVICE_KEYS = ("service", "service_name", "serviceName", "app", "component")
LEVEL_KEYS = ("level", "severity", "status")
MESSAGE_KEYS = ("message", "msg", "event", "name")


def parse_jsonl(lines: Iterable[str], *, service_filter: str | None = None) -> ParseResult:
    events: list[LogEvent] = []
    errors: list[ParseError] = []

    for line_number, raw_line in enumerate(lines, start=1):
        line = raw_line.strip()
        if not line:
            continue

        try:
            item = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append(ParseError(line_number, f"invalid json: {exc.msg}", line))
            continue

        if not isinstance(item, dict):
            errors.append(ParseError(line_number, "json value must be an object", line))
            continue

        event = _to_event(item, line_number)
        if isinstance(event, ParseError):
            errors.append(event)
            continue

        if service_filter and event.service != service_filter:
            continue

        events.append(event)

    return ParseResult(tuple(events), tuple(errors))


def _to_event(item: dict[str, Any], line_number: int) -> LogEvent | ParseError:
    timestamp = _first_present(item, TIMESTAMP_KEYS)
    trace_id = _first_present(item, TRACE_KEYS)

    if timestamp is None:
        return ParseError(line_number, "missing timestamp field", json.dumps(item, sort_keys=True))
    if trace_id is None:
        return ParseError(line_number, "missing trace id field", json.dumps(item, sort_keys=True))

    occurred_at = _parse_timestamp(timestamp)
    if occurred_at is None:
        return ParseError(line_number, "timestamp is not ISO-8601 or unix time", json.dumps(item, sort_keys=True))

    service = str(_first_present(item, SERVICE_KEYS) or "unknown")
    level = str(_first_present(item, LEVEL_KEYS) or "info").lower()
    message = str(_first_present(item, MESSAGE_KEYS) or "")

    return LogEvent(
        occurred_at=occurred_at,
        trace_id=str(trace_id),
        service=service,
        level=level,
        message=message,
        raw=item,
        line_number=line_number,
    )


def _first_present(item: dict[str, Any], keys: tuple[str, ...]) -> Any | None:
    for key in keys:
        value = item.get(key)
        if value not in (None, ""):
            return value
    return None


def _parse_timestamp(value: Any) -> datetime | None:
    if isinstance(value, (int, float)):
        seconds = float(value) / 1000 if value > 9_999_999_999 else float(value)
        return datetime.fromtimestamp(seconds, tz=timezone.utc)

    if not isinstance(value, str):
        return None

    cleaned = value.strip()
    if cleaned.isdigit():
        return _parse_timestamp(int(cleaned))

    if cleaned.endswith("Z"):
        cleaned = f"{cleaned[:-1]}+00:00"

    try:
        parsed = datetime.fromisoformat(cleaned)
    except ValueError:
        return None

    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)
