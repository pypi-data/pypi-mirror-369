# To use

```sh
export BLITE_TRACING_ENABLED=1
```

```py
from blite_tracing.trace import start_event, end_event, write_trace

start_event("event_name")
your_code_here
end_event("event_name")
write_trace()
```

It's just a one file codebase, very tine, just refer to `trace.py` for any details. Basically we just
write to json in the format that chorme://tracing undertands.

