import openai

# Provide backward compatibility for code that still calls
# ``openai.ChatCompletion.create`` in environments with ``openai>=1``.

if hasattr(openai, "chat") and hasattr(openai.chat, "completions"):
    openai.ChatCompletion = type(
        "ChatCompletionCompat",
        (),
        {"create": staticmethod(openai.chat.completions.create)},
    )
