#!/usr/bin/env python3
"""lead_generation_agent.py

A simple AI agent framework to pull target specifications from a Supabase
table, generate search queries using OpenAI, perform a web search and store
discovered leads back to Supabase. This module uses `supabase-py` for database
access and expects a search API for retrieving potential leads. Table and
column names are aligned with the expected schema.
"""

from __future__ import annotations

from dotenv import load_dotenv
load_dotenv()

import os
from dataclasses import dataclass
from typing import Any, List

from supabase import create_client, Client
import openai
import json


# Apply compatibility patch for `openai.ChatCompletion.create` when using
# `openai` version 1.x. The `openai_compat` module performs the patch at import
# time and is a no-op for older versions.
try:  # pragma: no cover - optional dependency
    import openai_compat  # noqa: F401
except Exception:
    pass


try:
    # The openai-agents package exposes its functionality via the
    # ``openai_agents`` module rather than ``openai.agents``. Importing the
    # top-level module registers the Agent/Tool API and makes the classes
    # available for import.
    import openai_agents  # noqa: F401
    from openai_agents import Agent, Tool
except Exception:  # pragma: no cover - optional dependency
    Agent = None  # type: ignore
    Tool = None   # type: ignore

# Constants for environment variable names
SUPABASE_URL_ENV = "SUPABASE_URL"
SUPABASE_KEY_ENV = "SUPABASE_SERVICE_ROLE_KEY"
OPENAI_KEY_ENV = "OPENAI_API_KEY"

# Table names used by this agent
JOB_TABLE = "targets"
LEADS_TABLE = "leads"


def create_chat_completion(**kwargs: Any) -> Any:
    """Compatibility wrapper to support both old and new OpenAI APIs."""
    if hasattr(openai, "chat") and hasattr(openai.chat, "completions"):
        return openai.chat.completions.create(**kwargs)
    return openai.ChatCompletion.create(**kwargs)

@dataclass
class Target:
    """Represents a single lead generation target."""

    id: int
    name: str
    criteria: str
    processed: bool
    created_at: str

@dataclass
class Lead:
    """Represents a lead generated from a target."""

    target_id: int
    data: dict[str, Any]

def get_supabase_client() -> Client:
    """Create and return a Supabase client using environment variables."""
    url = os.getenv(SUPABASE_URL_ENV)
    key = os.getenv(SUPABASE_KEY_ENV)
    if not url or not key:
        raise RuntimeError(
            "Supabase credentials not found. Set SUPABASE_URL and "
            "SUPABASE_SERVICE_ROLE_KEY"
        )
    return create_client(url, key)


def fetch_jobs(client: Client) -> List[Target]:
    """Fetch unprocessed lead generation jobs from Supabase."""
    response = (
        client.table(JOB_TABLE).select("*").eq("processed", False).execute()
    )
    jobs = [Target(**item) for item in response.data]
    return jobs


def generate_query(job: Target) -> str:
    """Generate a web-search query for a given target using OpenAI."""

    openai.api_key = os.getenv(OPENAI_KEY_ENV)
    if not openai.api_key:
        raise RuntimeError("OPENAI_API_KEY environment variable not set")

    messages = [
        {
            "role": "system",
            "content": "You generate search queries for lead generation tasks.",
        },
        {"role": "user", "content": f"Target name: {job.name}. Criteria: {job.criteria}"},
    ]

    resp = create_chat_completion(
        model="gpt-4o",
        messages=messages,
        temperature=0.2,
    )

    query = resp.choices[0].message.content.strip()
    return query


def search_web(query: str) -> List[dict[str, Any]]:
    """Perform a web search using OpenAI's built-in browsing tool."""

    openai.api_key = os.getenv(OPENAI_KEY_ENV)
    if not openai.api_key:
        raise RuntimeError("OPENAI_API_KEY environment variable not set")

    messages = [
        {
            "role": "system",
            "content": (
                "Use web search to gather leads. Return results as JSON in the "
                'format {"results": [...]}.'
            ),
        },
        {"role": "user", "content": query},
    ]

    functions = [
        {
            "name": "search_web",
            "description": "Perform a web search and return results",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query string",
                    }
                },
                "required": ["query"],
            },
        }
    ]

    resp = create_chat_completion(
        model="gpt-4o",
        messages=messages,
        response_format={"type": "json_object"},
        functions=functions,
        function_call={"name": "search_web"},
    )

    try:
        results = json.loads(resp.choices[0].message.content)["results"]
    except Exception:
        results = []
    return results


def browse_page(url: str) -> str:
    """Fetch raw HTML from a URL using ``requests``.

    This serves as a simple example of wiring a custom web retrieval
    function into the Agents SDK. It returns the page's text content or an
    error string if the request fails.
    """

    import requests

    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        return resp.text
    except Exception as exc:  # pragma: no cover - network errors
        return f"Error fetching {url}: {exc}"


def insert_lead(client: Client, job: Target, lead_data: dict[str, Any]) -> None:
    """Insert a single lead row into the database."""


    store_leads(client, [Lead(target_id=job.id, data=lead_data)])


def search_leads(job: Target) -> List[Lead]:
    """Use OpenAI and a web-search tool to find leads for a target."""

    query = generate_query(job)
    results = search_web(query)
    leads = [Lead(target_id=job.id, data=result) for result in results]
    return leads


def store_leads(client: Client, leads: List[Lead]) -> None:
    """Insert discovered leads into the Supabase leads table."""
    if not leads:
        return
    payload = [lead.__dict__ for lead in leads]
    client.table(LEADS_TABLE).insert(payload).execute()


def mark_job_processed(client: Client, job: Target) -> None:
    """Mark a job as processed to avoid duplicate work."""
    client.table(JOB_TABLE).update({"processed": True}).eq("id", job.id).execute()


def run_agent() -> None:
    """Run the lead generation workflow using the OpenAI Agents SDK."""

    client = get_supabase_client()

    # If the Agents SDK is unavailable fall back to the original manual loop.
    if Agent is None or Tool is None:
        targets = fetch_jobs(client)
        print(f"\U0001F50D Found {len(targets)} targets to process.")
        for t in targets:
            leads = search_leads(t)
            store_leads(client, leads)
            print(f"[Target {t.id}] Inserted {len(leads)} leads")
            mark_job_processed(client, t)
        return

    tools = [
        Tool("fetch_jobs", lambda: fetch_jobs(client), "Get unprocessed targets"),
        Tool(
            "generate_query",
            generate_query,
            "Build a web-search query using OpenAI",
        ),
        Tool("search_web", search_web, "Perform the actual HTTP search"),
        Tool("browse_page", browse_page, "Fetch raw HTML from a URL"),
        Tool(
            "insert_lead",
            lambda job, lead: insert_lead(client, job, lead),
            "Write leads back to Supabase",
        ),
        Tool(
            "mark_processed",
            lambda job: mark_job_processed(client, job),
            "Mark the job done",
        ),
    ]

    agent = Agent.from_openai(
        name="lead-gen-agent",
        model="gpt-4o",
        tools=tools,
        system_message=(
            "You are a lead generation agent. Fetch targets, generate search "
            "queries, search the web, optionally fetch pages with `browse_page`, "
            "insert leads and mark jobs processed."
        ),
    )

    agent.run()


if __name__ == "__main__":
    run_agent()
