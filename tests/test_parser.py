import unittest

from log_latency_profiler.parser import parse_jsonl


class ParserTest(unittest.TestCase):
    def test_parse_jsonl_accepts_common_field_names(self):
        lines = [
            '{"@timestamp":"2026-05-10T08:00:00Z","traceId":"abc","service":"api","level":"INFO","message":"start"}',
            '{"ts":1778400001000,"request_id":"abc","service_name":"db","severity":"error","msg":"query failed"}',
        ]

        result = parse_jsonl(lines)

        self.assertEqual(len(result.events), 2)
        self.assertEqual(result.events[0].trace_id, "abc")
        self.assertEqual(result.events[1].service, "db")
        self.assertEqual(result.events[1].level, "error")
        self.assertFalse(result.errors)

    def test_parse_jsonl_reports_bad_lines(self):
        result = parse_jsonl(["not json", '{"timestamp":"2026-05-10T08:00:00Z"}'])

        self.assertEqual(len(result.events), 0)
        self.assertEqual(len(result.errors), 2)
        self.assertEqual(result.errors[0].line_number, 1)


if __name__ == "__main__":
    unittest.main()
