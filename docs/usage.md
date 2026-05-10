# Usage

## Accepted Field Names

| Concept | Supported keys |
|---|---|
| Timestamp | `timestamp`, `@timestamp`, `time`, `ts`, `datetime`, `date` |
| Trace id | `trace_id`, `traceId`, `request_id`, `requestId`, `correlation_id`, `correlationId`, `span_id` |
| Service | `service`, `service_name`, `serviceName`, `app`, `component` |
| Level | `level`, `severity`, `status` |
| Message | `message`, `msg`, `event`, `name` |

## Recipes

| Goal | Command |
|---|---|
| Profile a file | `log-latency-profiler logs.jsonl` |
| Read from stdin | `cat logs.jsonl | log-latency-profiler -` |
| Export Markdown | `log-latency-profiler logs.jsonl --format markdown -o report.md` |
| Inspect one service | `log-latency-profiler logs.jsonl --service payments` |
| Show all traces | `log-latency-profiler logs.jsonl --include-all` |
