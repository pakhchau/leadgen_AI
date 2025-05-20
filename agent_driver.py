import os, json, openai
from agents import Agent, OpenAIResponsesModel, Runner
from tools import TOOLS

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

agent = Agent(
    name="lead-gen-agent",
    model=OpenAIResponsesModel("gpt-4o-mini"),
    tools=TOOLS,
    system_message=SYSTEM,
)


if __name__ == "__main__":
    import asyncio
    result = asyncio.run(Runner.run(agent, "start"))
    print(result.final_output)

