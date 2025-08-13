from __future__ import annotations

import random
import sys
from .screen_compat import Screen

from .util.settings import load_settings_from_sources
from .app import run as _run


def run_with_resize(settings) -> None:
    """Run the app, restarting the Screen on terminal resize.

    This wraps Screen.wrapper and catches ResizeScreenError to recreate
    the screen, without changing application behavior.
    """
    # Import terminal dependencies lazily to avoid import-time costs in other backends
    from asciimatics.screen import Screen as _RealScreen  # type: ignore
    from asciimatics.exceptions import ResizeScreenError  # type: ignore
    while True:
        try:
            _RealScreen.wrapper(lambda scr: _run(scr, settings))
            break
        except ResizeScreenError:
            continue


def main(argv: list[str] | None = None) -> None:
    # Ensure we forward the actual CLI argv to settings so --config pre-scan works.
    if argv is None:
        argv = sys.argv[1:]
    try:
        settings = load_settings_from_sources(argv)
    except FileNotFoundError as e:
        print(str(e), file=sys.stderr)
        sys.exit(2)
    if settings.seed is not None:
        random.seed(settings.seed)
    backend = getattr(settings, "ui_backend", "terminal")
    if backend == "web":
        # Simple local server to host the web assets
        from .web_server import serve_web
        serve_web(port=int(getattr(settings, 'web_port', 8000)), open_browser=bool(getattr(settings, 'web_open', False)))
        return
    if backend == "tk":
        try:
            # Preflight to provide a clearer error if Tk isn't present
            import tkinter  # type: ignore
            from .backend.tk import run_tk
            run_tk(settings)
            return
        except Exception as e:
            print(f"Tk backend unavailable ({e}); falling back to terminal.", file=sys.stderr)
    # Default: terminal backend
    run_with_resize(settings)
