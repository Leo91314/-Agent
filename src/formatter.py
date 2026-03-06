from __future__ import annotations

from typing import Any


def render_topic_list(items: list[str]) -> str:
    if not items:
        return "- None"
    return "\n".join(f"- {item}" for item in items)


def render_risk_list(items: list[str]) -> str:
    if not items:
        return "- No risk factors extracted"
    return "\n".join(f"- {item}" for item in items)


def build_html_document(title: str, body_html: str) -> str:
    return f"""<!DOCTYPE html>
<html lang=\"en\">
<head>
  <meta charset=\"UTF-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />
  <title>{title}</title>
  <style>
    body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 2rem auto; max-width: 960px; line-height: 1.6; color: #202124; }}
    h1, h2, h3 {{ color: #0b3b61; }}
    .meta {{ background: #f3f7fb; padding: 0.75rem 1rem; border-left: 4px solid #0b3b61; }}
    a {{ color: #0b3b61; }}
    code {{ background: #f0f0f0; padding: 0.1rem 0.25rem; border-radius: 3px; }}
  </style>
</head>
<body>
{body_html}
</body>
</html>"""


def normalize_sentiment(sentiment: dict[str, Any]) -> dict[str, int]:
    return {
        "positive": int(sentiment.get("positive", 0)),
        "neutral": int(sentiment.get("neutral", 0)),
        "negative": int(sentiment.get("negative", 0)),
    }
