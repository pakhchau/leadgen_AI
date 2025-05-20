#!/usr/bin/env python3
import os, json
import openai
from supabase_helpers import fetch_targets, insert_lead

openai.api_key = os.getenv("OPENAI_API_KEY")

def build_search_query(criteria: dict) -> str:
    resp = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Turn this JSON into a concise web-search query."},
            {"role": "user",   "content": json.dumps(criteria)}
        ],
        max_tokens=32
    )
    return resp.choices[0].message.content.strip()

def web_search_stub(query: str) -> list[dict]:
    return [
        {"name": "Alice Example", "company": "ExampleCorp", "url": "https://example.com/a"},
        {"name": "Bob Example",   "company": "ExampleInc",  "url": "https://example.com/b"}
    ]

def run_agent():
    targets = fetch_targets()
    for t in targets:
        criteria = t.get("criteria")
        if isinstance(criteria, str):
            criteria = json.loads(criteria)
        query = build_search_query(criteria)
        leads = web_search_stub(query)
        for lead in leads:
            insert_lead(t["id"], lead, query)
        print(f"[Target {t['id']}] Inserted {len(leads)} leads")

if __name__ == "__main__":
    run_agent()
