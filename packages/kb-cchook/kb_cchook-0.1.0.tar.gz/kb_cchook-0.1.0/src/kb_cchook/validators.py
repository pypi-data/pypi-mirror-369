import json
from .exceptions import HookError


def process_stdin(stdin):
    if isinstance(stdin, dict):
        data = stdin
    elif hasattr(stdin, "read"):
        data = json.loads(stdin.read())
    else:
        raise HookError("Invalid stdin")

    if not isinstance(data, dict) or "hook_event_name" not in data:
        raise HookError("Missing hook_event_name")

    return data
