"""Quick script to list available Gemini models for the current API key."""
from google import genai
from config import settings

client = genai.Client(api_key=settings.GEMINI_API_KEY)

print(f"Using API key: {settings.GEMINI_API_KEY[:15]}...")
print("\n=== Available models ===")
for m in client.models.list():
    actions = getattr(m, "supported_actions", None) or getattr(m, "supported_generation_methods", [])
    print(f"  {m.name}  | actions: {actions}")
