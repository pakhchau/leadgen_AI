import os, json
from dotenv import load_dotenv
from supabase import create_client
from agents import function_tool, WebSearchTool
load_dotenv()                             # read .env once

# --- Supabase client -------------------------------------------------
client = create_client(
    os.environ["SUPABASE_URL"],
    os.environ["SUPABASE_SERVICE_ROLE_KEY"],
)

# --- tool: fetch_targets --------------------------------------------
@function_tool
def fetch_targets() -> list[dict]:
    """Return every un-processed row in the targets table."""
    return (
        client.table("targets")
              .select("*")
              .eq("processed", False)
              .execute()
              .data
    )

# --- tool: insert_lead ----------------------------------------------
@function_tool
def insert_lead(target_id: int, lead: dict) -> int:
    out = (
        client.table("leads")
              .insert({"target_id": target_id, "lead_data": lead})
              .execute()
              .data
    )
    return out[0]["id"]

# --- tool: mark_processed -------------------------------------------
@function_tool
def mark_processed(target_id: int) -> bool:
    client.table("targets").update({"processed": True}).eq("id", target_id).execute()
    return True

# --- built-in OpenAI browsing tool ----------------------------------
# exposes `browser.search` automatically
web_search = WebSearchTool()

TOOLS = [
    fetch_targets,
    insert_lead,
    mark_processed,
    web_search,
]

__all__ = ["fetch_targets", "insert_lead", "mark_processed", "web_search", "TOOLS"]

