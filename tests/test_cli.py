import tempfile
import unittest
from pathlib import Path

from log_latency_profiler.cli import main


class CliTest(unittest.TestCase):
    def test_cli_writes_markdown_report(self):
        with tempfile.TemporaryDirectory() as directory:
            tmp_path = Path(directory)
            input_file = tmp_path / "logs.jsonl"
            output_file = tmp_path / "report.md"
            input_file.write_text(
                "\n".join(
                    [
                        '{"timestamp":"2026-05-10T08:00:00Z","trace_id":"t1","service":"api","message":"start"}',
                        '{"timestamp":"2026-05-10T08:00:02Z","trace_id":"t1","service":"worker","level":"error","message":"done"}',
                    ]
                ),
                encoding="utf-8",
            )

            code = main([str(input_file), "--format", "markdown", "--output", str(output_file)])

            self.assertEqual(code, 0)
            content = output_file.read_text(encoding="utf-8")
            self.assertIn("Log Latency Profile", content)
            self.assertIn("`t1`", content)


if __name__ == "__main__":
    unittest.main()
