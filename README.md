# leadgen_AI

This repository contains a simple Python module for building an AI-driven
lead generation agent using Supabase as a backend. The core logic lives in
`lead_generation_agent.py` and demonstrates how you might pull lead generation
jobs from a Supabase table, perform a search via a third-party API, and then
store discovered leads back into the database.

The agent expects the following environment variables:

- `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` for database access.
- `OPENAI_API_KEY` for generating search queries.
- `SEARCH_API_KEY` for the underlying web search service.

See the docstrings in `lead_generation_agent.py` for details.
