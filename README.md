# leadgen_AI

This repository contains a simple Python module for building an AI-driven
lead generation agent using Supabase as a backend. The core logic lives in
`lead_generation_agent.py` and demonstrates how you might pull lead generation
jobs from a Supabase table, perform a web search and then store discovered
leads back into the database. The short `agent.py` script now simply imports
and calls `run_agent()` from this module for backward compatibility.

The module now includes an
implementation of the **OpenAI Agents SDK** to orchestrate these steps.

The agent expects the following environment variables:

- `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` for database access.
- `OPENAI_API_KEY` for generating search queries and performing web searches.

### .env
SUPABASE_URL=...
SUPABASE_SERVICE_ROLE_KEY=...
OPENAI_API_KEY=...

No SerpAPI key needed.

When the `openai_agents` package is installed and imported, `run_agent()` will
construct an `Agent` with a set of tools to fetch jobs, generate queries,
search the web, optionally fetch raw HTML pages using a custom `browse_page`
tool and store leads. If the Agents SDK is not installed, it falls
back to the
original manual workflow.

You can verify the package is available with:

```bash
python -c "import openai_agents, supabase, requests; print('OK')"
```

## Using the virtual environment

If you receive `ModuleNotFoundError: openai_agents`, ensure that the
interpreter you are invoking is the one from your virtual environment.
Check with:

```bash
which python
which python3
```

Both should point inside `./venv/bin/`. If they do not, either activate the
environment with:

```bash
source venv/bin/activate
```

or call the venv's interpreter explicitly:

```bash
./venv/bin/python - <<'EOF'
import openai_agents
print("Loaded:", openai_agents)
EOF
```

## Compatibility

For projects that still call `openai.ChatCompletion.create` directly, the
`openai_compat` module patches this method to forward requests to the new
`openai.chat.completions.create` function introduced in `openai>=1`.

Make sure to import ``openai_compat`` **before** issuing any API calls:

```python
import openai_compat  # applies the patch
import openai
```

Alternatively, simply use `lead_generation_agent.py`, which imports it
automatically. A minimal example is provided in `test_env.py`.

## Running the agent

After configuring your environment variables, start the agent with the
interpreter from your virtual environment:

```bash
./venv/bin/python lead_generation_agent.py
```

This will process any unprocessed targets from Supabase and insert newly
discovered leads. See the docstrings in `lead_generation_agent.py` for
further details.
