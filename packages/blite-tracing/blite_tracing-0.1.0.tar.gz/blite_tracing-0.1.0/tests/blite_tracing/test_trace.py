import os
import json
import time
import sys

def test_start_end_event(monkeypatch, tmp_path):
    # Enable tracing for this test
    monkeypatch.setenv("BLITE_TRACING_ENABLED", "1")

    # Use the test directory as CWD so the trace file is created here
    orig_cwd = os.getcwd()
    os.chdir(tmp_path)
    print(f"tmp_path: {tmp_path}, original cwd: {orig_cwd}")
    try:
        # Ensure fresh import for env to take effect
        sys.modules.pop("blite_tracing", None)
        import blite_tracing
        blite_tracing.trace._disable_atexit = True
        event_name = "pytest_event"
        blite_tracing.start_event(event_name)
        time.sleep(0.01)
        blite_tracing.end_event(event_name)
        blite_tracing.write_trace()

        # Locate the trace file
        pid = os.getpid()
        trace_file = tmp_path / f"trace_{pid}.json"
        print(f"trace file path: {trace_file}")
        assert trace_file.exists(), f"Trace file not found: {trace_file}"

        with open(trace_file) as f:
            events = json.load(f)["traceEvents"]

        found = [e for e in events if e["name"] == event_name]
        assert found, "Event not recorded"
        event = found[0]
        assert event["dur"] > 0
        assert event["ph"] == "X"
        assert event["pid"] == pid
    finally:
        os.chdir(orig_cwd)
