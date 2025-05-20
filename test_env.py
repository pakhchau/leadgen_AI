"""Minimal example using ``openai_compat`` to maintain backwards compatibility."""

import openai_compat  # noqa: F401 - patches openai.ChatCompletion
import openai

# Example call. This will fail without an API key but demonstrates the interface.
if __name__ == "__main__":
    try:
        resp = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello"}],
        )
        print(resp)
    except Exception as exc:
        print("Request failed:", exc)
