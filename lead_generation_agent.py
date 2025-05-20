"""lead_generation_agent.py

A simple AI agent framework to pull target specifications from a Supabase
table, generate search queries using OpenAI, perform a web search and store
discovered leads back to Supabase. This module uses `supabase-py` for database
access and expects a search API for retrieving potential leads. Table and
column names are aligned with the expected schema.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, List

from supabase import create_client, Client
import requests
import openai
import json

# Constants for environment variable names
SUPABASE_URL_ENV = "SUPABASE_URL"
SUPABASE_KEY_ENV = "SUPABASE_SERVICE_ROLE_KEY"
OPENAI_KEY_ENV = "OPENAI_API_KEY"
SEARCH_API_KEY_ENV = "SEARCH_API_KEY"

# Table names used by this agent
JOB_TABLE = "targets"
LEADS_TABLE = "leads"

@dataclass
class Target:
    """Represents a single lead generation target."""

    id: int
    name: str
    criteria: str
    processed: bool

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


def search_leads(job: Target) -> List[Lead]:
    """Use OpenAI and a web-search tool to find leads for a target."""

    openai.api_key = os.getenv(OPENAI_KEY_ENV)
    if not openai.api_key:
        raise RuntimeError("OPENAI_API_KEY environment variable not set")

    messages = [
        {
            "role": "system",
            "content": "You generate search queries for lead generation tasks.",
        },
        {
            "role": "user",
            "content": f"Target name: {job.name}. Criteria: {job.criteria}",
        },
    ]

    functions = [
        {
            "name": "search_web",
            "description": "Perform a web search and return JSON results.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "search query string",
                    }
                },
                "required": ["query"],
            },
        }
    ]

    resp = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0613",
        messages=messages,
        functions=functions,
        function_call={"name": "search_web"},
    )

    query = json.loads(resp.choices[0].message.function_call.arguments)["query"]

    search_key = os.getenv(SEARCH_API_KEY_ENV)
    if not search_key:
        raise RuntimeError(f"{SEARCH_API_KEY_ENV} environment variable not set")

    response = requests.get(
        "https://example.com/search",
        params={"q": query, "api_key": search_key},
        timeout=10,
    )
    response.raise_for_status()
    results = response.json().get("results", [])

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
    """Main entry point for running the agent once."""
    client = get_supabase_client()
    jobs = fetch_jobs(client)

    for job in jobs:
        leads = search_leads(job)
        store_leads(client, leads)
        mark_job_processed(client, job)


if __name__ == "__main__":
    run_agent()
