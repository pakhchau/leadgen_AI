import os, json, openai, openai_agents
from tools import fetch_targets, insert_lead, mark_processed, web_search

openai.api_key = os.environ["OPENAI_API_KEY"]

SYSTEM = """
You are a lead-generation agent.

For each target from fetch_targets():
1. Read target.criteria (a JSON blob).
2. Produce ONE concise Google query that will find companies or people
   matching those criteria.
3. Call browser.search(query) to get live results.
4. For each result item (title, link, snippet), call insert_lead().
5. Call mark_processed(target_id) when done.

Return nothing else.
"""

agent = openai_agents.Agent.from_openai(
    name="lead-gen-agent",
    model="gpt-4o",
    tools=[fetch_targets, web_search, insert_lead, mark_processed],
    system_message=SYSTEM,
)

if __name__ == "__main__":
    result = agent.run("start")
    print(result.logs)      # full tool-call trace

