"""Backward compatibility helpers for ``openai>=1``.

Importing this module patches :func:`openai.ChatCompletion.create` so that
existing code written for ``openai<1`` continues to work with newer releases.
The shim simply forwards calls to :func:`openai.chat.completions.create`.

Usage::

    import openai_compat  # noqa: F401 - applies the patch at import time

Nothing else needs to be done. If this module is imported when the new
``openai.chat`` API is available, ``openai.ChatCompletion.create`` will behave
as expected. When running against an older version of ``openai`` the patch is a
no-op.
"""

import openai

# Provide backward compatibility for code that still calls
# ``openai.ChatCompletion.create`` in environments with ``openai>=1``.

def _create_compat(*args, **kwargs):
    """Delegate to ``openai.chat.completions.create`` at call time."""
    return openai.chat.completions.create(*args, **kwargs)

if hasattr(openai, "chat"):
    openai.ChatCompletion = type(
        "ChatCompletionCompat",
        (),
        {"create": staticmethod(_create_compat)},
    )
