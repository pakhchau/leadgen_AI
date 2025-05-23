import os, asyncio, openai
from agents import Agent, Runner
from agents.models.openai_responses import OpenAIResponsesModel
from tools import TOOLS

openai_client = openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"])

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

model = OpenAIResponsesModel(openai_client, "gpt-4o-mini")

# Pass parameters by keyword to avoid accidentally providing duplicate values
# and to be compatible with different Agent versions.
agent = Agent(model=model,
              name="lead-gen-agent",
              tools=TOOLS,
              instructions=SYSTEM)


if __name__ == "__main__":
    asyncio.run(Runner.run(agent, "start"))

