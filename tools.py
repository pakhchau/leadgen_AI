import os, json
from dotenv import load_dotenv
from supabase import create_client
from openai_agents import Tool
import openai.tools as oat   # built-in browsing tools

load_dotenv()                             # read .env once

# --- Supabase client -------------------------------------------------
client = create_client(
    os.environ["SUPABASE_URL"],
    os.environ["SUPABASE_SERVICE_ROLE_KEY"],
)

# --- tool: fetch_targets --------------------------------------------
def _fetch_targets():
    """Return every targets row where processed == false."""
    return (client.table("targets")
                   .select("*")
                   .eq("processed", False)
                   .execute()
                   .data)

fetch_targets = Tool(
    name="fetch_targets",
    description="Get all unprocessed targets from Supabase",
    function=_fetch_targets,
)

# --- tool: insert_lead ----------------------------------------------
def _insert_lead(target_id: int, lead: dict):
    out = (client.table("leads")
                 .insert({"target_id": target_id, "lead_data": lead})
                 .execute()
                 .data)
    return out[0]["id"]

insert_lead = Tool(
    name="insert_lead",
    description="Store one lead row",
    function=_insert_lead,
)

# --- tool: mark_processed -------------------------------------------
def _mark_processed(target_id: int):
    client.table("targets").update({"processed": True}).eq("id", target_id).execute()
    return True

mark_processed = Tool(
    name="mark_processed",
    description="Flag a target as processed so it is not re-queued",
    function=_mark_processed,
)

# --- built-in OpenAI browsing tool ----------------------------------
# exposes `browser.search` automatically
web_search = oat.web_search         # ← comes from the SDK docs
