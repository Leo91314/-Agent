FILING_AND_SENTIMENT_SYSTEM = """You are a financial analysis assistant.
Return only valid JSON.
No markdown or explanatory text.
"""


def build_filing_and_news_prompt(filing_info: dict, filing_snippet: str, news_items: list[dict]) -> str:
    return f"""
Analyze the SEC filing metadata/snippet and the provided news headlines.

Return JSON with these keys exactly:
- financial_summary (string)
- management_view (string)
- risk_factors (array of strings)
- sentiment_distribution (object with keys positive, neutral, negative as integers)
- positive_topics (array of strings)
- negative_topics (array of strings)

SEC Filing Info:
{filing_info}

Filing Snippet:
{filing_snippet[:3000]}

News Items:
{news_items}
""".strip()
