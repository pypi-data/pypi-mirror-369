import json
import os
import threading
import time

# Internal state
_tracing_enabled = os.environ.get("BLITE_TRACING_ENABLED", "0") == "1"
_recorder = None

# TODO(pankaj): Get rid of this
_event_starts = {}

_lock = threading.Lock()
_disable_atexit = False


def _create_recorder():
    output_file = f"trace_{os.getpid()}.json"
    return TraceRecorder(output_file)


def _get_recorder():
    global _recorder
    if _recorder is None and _tracing_enabled:
        _recorder = _create_recorder()
    return _recorder


class TraceRecorder:
    """Manages trace events and writes them to a Chrome Tracing JSON file."""

    def __init__(self, output_file):
        self._output_file = output_file
        self._events = []
        self._lock = threading.Lock()
        self._start_time_us = time.perf_counter() * 1_000_000

    def add_event(self, name, start_time_us, end_time_us, tid=None):
        event = {
            "name": name,
            "cat": "performance",
            "ph": "X",
            "ts": start_time_us - self._start_time_us,
            "dur": end_time_us - start_time_us,
            "pid": os.getpid(),
            "tid": tid if tid is not None else threading.get_ident(),
            "args": {},
        }
        with self._lock:
            self._events.append(event)

    def write(self):
        with self._lock:
            with open(self._output_file, "w") as f:
                json.dump({"traceEvents": self._events}, f)
            print(f"Trace data written to {self._output_file}")

    def reset(self):
        with self._lock:
            self._events = []
            self._start_time_us = time.perf_counter() * 1_000_000


def start_event(name):
    """Mark the start of a named event."""
    if not _tracing_enabled:
        return

    now = time.perf_counter() * 1_000_000
    with _lock:
        _event_starts[name] = now


def end_event(name):
    """Mark the end of a named event and record its duration."""
    if not _tracing_enabled:
        return
    now = time.perf_counter() * 1_000_000
    with _lock:
        start = _event_starts.pop(name, None)
    if start is not None:
        _get_recorder().add_event(name, start, now)


def event(name, start_time_us, end_time_us):
    """Directly record an event with given times (in microseconds)."""
    if not _tracing_enabled:
        return
    _get_recorder().add_event(name, start_time_us, end_time_us)


def write_trace():
    """Force writing of trace events to the output file."""
    if not _tracing_enabled:
        return

    if _recorder is not None:
        _recorder.write()


def _write_trace_at_exit():
    if not _disable_atexit:
        write_trace()


def reset():
    """Write current trace, then clear events and reset the trace start time."""
    if not _tracing_enabled:
        return

    write_trace()
    global _recorder, _event_starts
    with _lock:
        _recorder = _create_recorder()
        _event_starts.clear()


import atexit

atexit.register(_write_trace_at_exit)
