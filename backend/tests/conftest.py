import os


# Tests must never make paid external model calls, even when a developer has a local .env.
os.environ["GROQ_API_KEY"] = ""
