#!/usr/bin/env python3

"""Compatibility wrapper for :mod:`lead_generation_agent`.

This module previously contained a standalone implementation that returned
dummy data via a ``web_search_stub`` function. It now simply delegates to the
real agent in :mod:`lead_generation_agent`, which performs actual web searches
and writes results to Supabase when proper credentials are configured.


"""

from lead_generation_agent import run_agent


if __name__ == "__main__":  # pragma: no cover - manual entry point
    run_agent()
