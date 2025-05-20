# leadgen_AI

This repository contains a simple Python module for building an AI-driven
lead generation agent using Supabase as a backend. The core logic lives in
`lead_generation_agent.py` and demonstrates how you might pull lead generation
jobs from a Supabase table, perform a web search and then
store discovered leads back into the database. The module now includes an
implementation of the **OpenAI Agents SDK** to orchestrate these steps.

The agent expects the following environment variables:

- `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` for database access.
- `OPENAI_API_KEY` for generating search queries and performing web searches.

When the `openai.agents` package is available, `run_agent()` will construct
an `Agent` with a set of tools to fetch jobs, generate queries, search the web
and store leads. If the Agents SDK is not installed, it falls back to the
original manual workflow.

See the docstrings in `lead_generation_agent.py` for details.
