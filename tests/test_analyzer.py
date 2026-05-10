import unittest
from datetime import datetime, timedelta, timezone

from log_latency_profiler.analyzer import profile_events
from log_latency_profiler.models import LogEvent


def event(trace_id: str, offset_ms: int, *, level: str = "info") -> LogEvent:
    return LogEvent(
        occurred_at=datetime(2026, 5, 10, tzinfo=timezone.utc) + timedelta(milliseconds=offset_ms),
        trace_id=trace_id,
        service="api",
        level=level,
        message=f"{trace_id}:{offset_ms}",
        raw={},
        line_number=1,
    )


class AnalyzerTest(unittest.TestCase):
    def test_profile_events_sorts_by_duration_and_counts_errors(self):
        report = profile_events(
            (
                event("fast", 0),
                event("fast", 50),
                event("slow", 0),
                event("slow", 1500, level="error"),
            ),
            slow_threshold_ms=1000,
        )

        self.assertEqual(report.trace_count, 2)
        self.assertEqual(report.max_ms, 1500)
        self.assertEqual(report.traces[0].trace_id, "slow")
        self.assertEqual(report.slow_traces[0].error_count, 1)


if __name__ == "__main__":
    unittest.main()
