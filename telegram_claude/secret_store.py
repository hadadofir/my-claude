"""Secrets live outside the repo and outside the environment.

Under systemd, each service gets its secrets via LoadCredential= in $CREDENTIALS_DIRECTORY.
When run by hand (e.g. `garmin_sync.py --login`), they are read from ~/.config/credstore.
"""
import os

CREDSTORE = os.path.expanduser("~/.config/credstore")

# Only these variables are passed to Claude subprocesses, so no secret can leak into them.
_CHILD_ENV_KEYS = ("HOME", "USER", "LOGNAME", "PATH", "SHELL", "LANG", "LC_ALL", "TZ", "TERM", "XDG_RUNTIME_DIR")


def get_secret(name: str) -> str:
    for base in (os.environ.get("CREDENTIALS_DIRECTORY"), CREDSTORE):
        if base and os.path.isfile(os.path.join(base, name)):
            with open(os.path.join(base, name)) as f:
                return f.read().strip()
    raise RuntimeError(f"secret '{name}' not found in $CREDENTIALS_DIRECTORY or {CREDSTORE}")


def child_env() -> dict:
    return {k: os.environ[k] for k in _CHILD_ENV_KEYS if k in os.environ}
