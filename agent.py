#!/usr/bin/env python3
"""Compatibility entry point for the lead generation agent.

This script previously contained a simplified demo that returned stubbed
data. It now delegates to :func:`lead_generation_agent.run_agent` to perform
real web searches and Supabase writes.
"""

from lead_generation_agent import run_agent


if __name__ == "__main__":
    run_agent()
