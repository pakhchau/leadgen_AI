#!/usr/bin/env python3

"""Small wrapper to invoke :mod:`agent_driver`.

Historically this file implemented a manual workflow with a ``web_search_stub``
helper. That logic has been removed in favour of the real Agent defined in
``agent_driver.py``. The file is kept only for backward compatibility so that
``python agent.py`` still works.
"""

from agent_driver import agent


if __name__ == "__main__":  # pragma: no cover - manual entry point
    result = agent.run("start")
    print(result.logs)

