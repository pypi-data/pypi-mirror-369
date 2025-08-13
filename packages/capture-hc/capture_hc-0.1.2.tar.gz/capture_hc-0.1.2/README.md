# Honeycomb Python Client

A simple, user-friendly wrapper for sending events to Honeycomb using libhoney, for use across any Python codebase.

## Installation

Copy the `honeycomb_client.py` file (and `__init__.py`) into your project, or install as a public package if set up.

## Usage

```python
from capture_hc.honeycomb_client import HoneycombClient

# Initialize the client (use your own writekey and dataset)
honey = HoneycombClient(writekey="<YOUR_WRITE_KEY>", dataset="<YOUR_DATASET>")

# Send an event (fields as a dictionary)
honey.send_event({
    "alert_name": "Test Alert",
    "priority": "P1",
    "message": "Something happened!",
    "duration_ms": 123.4
})

# Use the timed decorator to automatically measure and send duration
@honey.timed({"alert_name": "important_task"})
def important_task(x, y, event=None):
    # ... your code ...
    event.add_field("result", x + y)
    return x + y

important_task(1, 2)

# You can also customize the event variable name
@honey.timed({"alert_name": "custom_var"}, event_arg='track')
def another_task(x, y, track=None):
    track.add_field("custom_field", x * y)
    return x * y

another_task(2, 3)
```

## Features
- Only initialize once per process.
- Simple `send_event(dict)` interface.
- All fields are added to the event.
- Handles flush automatically.
- `@honey.timed({...})` decorator to measure and send function execution time automatically.

## Advanced
You can pass `debug=True`

## Integration Example

Set your environment variables and run the script to send a test event and a timed event:

```bash
export HONEYCOMB_WRITEKEY=your_writekey
export HONEYCOMB_DATASET=your_dataset
python -m integration_example
```

This will:
- Send a simple event to Honeycomb
- Use the `@honey.timed` decorator to send a timed event with custom fields

Example from `integration_example.py`:
```python
@honey.timed({'alert_name': 'decorator_test'})
def test_func(event=None):
    event.add_field('custom_field', 123)
    return 'decorator event sent!'
```

## Lazy decorator (module or class)

Use a one-liner lazy decorator that initializes at call-time and works with legacy functions:

```python
from capture_hc import lazy_timed

@lazy_timed(extra_fields={'alert_name': 'legacy_task'}, event_arg=None)
def legacy_task(x, y):
    return x + y
```

Or use it via the class for discoverability:
```python
from capture_hc import HoneycombClient

@HoneycombClient.lazy_timed(extra_fields={'alert_name': 'legacy_task'}, event_arg=None)
def legacy_task(x, y):
    return x + y
```

- Credentials resolve from env by default (`HONEYCOMB_WRITEKEY`, `HONEYCOMB_DATASET`).
- Set `event_arg=None` if your function can't accept the event kwarg.

### Airflow note
- Prefer lazy decorators or initialize the client inside the task function to avoid DAG-parse-time side effects.