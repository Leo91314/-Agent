from __future__ import annotations

from pathlib import Path
from typing import Any

try:
    import markdown as markdown_lib
except ImportError:
    markdown_lib = None

from src.formatter import (
    build_html_document,
    normalize_sentiment,
    render_risk_list,
    render_topic_list,
)


def build_markdown_report(run_data: dict[str, Any]) -> str:
    filing = run_data["filing"]
    analysis = run_data["analysis"]
    news_items = run_data["news_items"]
    sentiment = normalize_sentiment(analysis.get("sentiment_distribution", {}))

    return f"""# Automated Financial Report - {filing.get('ticker', '')}

## 1. Project / Report Title
Automated Financial Report Summarization & Sentiment Analysis (Demo MVP)

## 2. Company Information
- Company: {filing.get('company_name', '')}
- Ticker: {filing.get('ticker', '')}
- Generated At (UTC): {run_data.get('generated_at', '')}

## 3. Filing Basic Information
- Form Type: {filing.get('form_type', '')}
- Filing Date: {filing.get('filing_date', '')}
- Accession Number: {filing.get('accession_number', '')}
- Data Source: {filing.get('source', '')}

## 4. Filing Summary
{analysis.get('financial_summary', '')}

## 5. Management View
{analysis.get('management_view', '')}

## 6. Risk Factors
{render_risk_list(analysis.get('risk_factors', []))}

## 7. News Count
- Total News Items: {len(news_items)}

## 8. Sentiment Distribution
- Positive: {sentiment['positive']}
- Neutral: {sentiment['neutral']}
- Negative: {sentiment['negative']}

## 9. Main Positive Topics
{render_topic_list(analysis.get('positive_topics', []))}

## 10. Main Negative Topics
{render_topic_list(analysis.get('negative_topics', []))}

## 11. Original Filing Link
- Filing URL: {filing.get('filing_url', '')}

## 12. Disclaimer
This report is a competition/demo MVP based on SEC public filings and static local news samples.
It is for information aggregation and technical demonstration only and does not constitute investment advice.

---

### Execution Notes
- Analysis Mode: {analysis.get('analysis_mode', 'unknown')}
- Analysis Notes: {analysis.get('analysis_notes', '')}
- SEC Errors: {', '.join(filing.get('errors', [])) if filing.get('errors') else 'None'}
"""


def _markdown_to_html(md_text: str) -> str:
    if markdown_lib is None:
        escaped = (
            md_text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace("\n", "<br/>\n")
        )
        return f"<pre>{escaped}</pre>"
    return markdown_lib.markdown(md_text, extensions=["tables", "fenced_code"])


def generate_reports(run_data: dict[str, Any], output_dir: str) -> dict[str, str]:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    md_report = build_markdown_report(run_data)
    md_path = output_path / "sample_report.md"
    md_path.write_text(md_report, encoding="utf-8")

    body_html = _markdown_to_html(md_report)
    html = build_html_document("Automated Financial Report", body_html)
    html_path = output_path / "sample_report.html"
    html_path.write_text(html, encoding="utf-8")

    return {
        "markdown_report": str(md_path),
        "html_report": str(html_path),
    }
