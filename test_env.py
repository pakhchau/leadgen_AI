
#!/usr/bin/env python3
import os
from dotenv import load_dotenv
from supabase import create_client
import openai

load_dotenv()

supa_url = os.getenv("SUPABASE_URL")
supa_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
print("SUPABASE_URL =", supa_url)
assert supa_url and supa_key, "Supabase vars missing in .env"

client = create_client(supa_url, supa_key)
res = client.table("targets").select("id").limit(1).execute()
print("✅ Supabase responded (preview):", res.data)

openai.api_key = os.getenv("OPENAI_API_KEY")
assert openai.api_key, "OPENAI_API_KEY missing in .env"

resp = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[{"role":"system","content":"Say hello"}],
    max_tokens=5
)
print("✅ OpenAI response:", resp.choices[0].message.content)
