from .constants import SUPPORTED_HOOK_EVENTS
from .validators import process_stdin
from .exceptions import HookError


def hook(hook_event_name, stdin, callback):
    if hook_event_name not in SUPPORTED_HOOK_EVENTS:
        raise HookError(f"Unsupported event: {hook_event_name}")

    if not callable(callback):
        raise HookError("Callback must be callable")

    data = process_stdin(stdin)

    if data["hook_event_name"] != hook_event_name:
        raise HookError("Event name mismatch")

    return callback(data)
