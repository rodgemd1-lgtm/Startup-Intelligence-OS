"""Module entrypoint for the Startup Intelligence Cockpit API."""

from __future__ import annotations

import uvicorn


def main() -> None:
    uvicorn.run("control_plane.main:app", host="127.0.0.1", port=8042, reload=False)


if __name__ == "__main__":
    main()
