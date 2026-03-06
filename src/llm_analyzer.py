from __future__ import annotations

import json
from collections import Counter
from typing import Any

import requests

from prompts import FILING_AND_SENTIMENT_SYSTEM, build_filing_and_news_prompt


POSITIVE_HINTS = {
    "growth",
    "beat",
    "record",
    "strong",
    "upgrade",
    "expands",
    "partnership",
    "gain",
}
NEGATIVE_HINTS = {
    "lawsuit",
    "decline",
    "cut",
    "downgrade",
    "risk",
    "probe",
    "delay",
    "weak",
    "miss",
}


class LLMAnalyzer:
    def __init__(self, api_key: str, base_url: str, model: str, timeout: int = 30):
        self.api_key = api_key.strip()
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout

    def analyze(
        self,
        filing: dict[str, Any],
        news_items: list[dict[str, str]],
        skip_llm: bool = False,
    ) -> dict[str, Any]:
        if skip_llm or not self.api_key:
            fallback = self._fallback_analysis(filing, news_items)
            fallback["analysis_mode"] = "fallback"
            fallback["analysis_notes"] = "DeepSeek API key missing or --skip-llm enabled."
            return fallback

        try:
            return self._deepseek_analysis(filing, news_items)
        except Exception as exc:
            fallback = self._fallback_analysis(filing, news_items)
            fallback["analysis_mode"] = "fallback"
            fallback["analysis_notes"] = f"DeepSeek call failed: {exc}"
            return fallback

    def _deepseek_analysis(
        self, filing: dict[str, Any], news_items: list[dict[str, str]]
    ) -> dict[str, Any]:
        prompt = build_filing_and_news_prompt(
            filing_info={
                "company_name": filing.get("company_name", ""),
                "ticker": filing.get("ticker", ""),
                "form_type": filing.get("form_type", ""),
                "filing_date": filing.get("filing_date", ""),
                "accession_number": filing.get("accession_number", ""),
            },
            filing_snippet=filing.get("filing_snippet", ""),
            news_items=news_items,
        )

        url = f"{self.base_url}/chat/completions"
        payload = {
            "model": self.model,
            "temperature": 0.2,
            "messages": [
                {"role": "system", "content": FILING_AND_SENTIMENT_SYSTEM},
                {"role": "user", "content": prompt},
            ],
            "response_format": {"type": "json_object"},
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        resp = requests.post(url, json=payload, headers=headers, timeout=self.timeout)
        resp.raise_for_status()
        data = resp.json()

        content = data["choices"][0]["message"]["content"]
        parsed = json.loads(content)

        merged = self._fallback_analysis(filing, news_items)
        merged.update(parsed)
        merged["analysis_mode"] = "deepseek"
        merged["analysis_notes"] = "DeepSeek API response used."
        return self._normalize(merged)

    def _fallback_analysis(
        self, filing: dict[str, Any], news_items: list[dict[str, str]]
    ) -> dict[str, Any]:
        sentiment_counts = Counter({"positive": 0, "neutral": 0, "negative": 0})
        positive_topics: Counter[str] = Counter()
        negative_topics: Counter[str] = Counter()

        for item in news_items:
            title = item.get("title", "")
            words = {w.strip(".,:;!?()[]{}\"'").lower() for w in title.split()}
            pos_hits = words & POSITIVE_HINTS
            neg_hits = words & NEGATIVE_HINTS

            if len(pos_hits) > len(neg_hits):
                sentiment_counts["positive"] += 1
                for w in pos_hits:
                    positive_topics[w] += 1
            elif len(neg_hits) > len(pos_hits):
                sentiment_counts["negative"] += 1
                for w in neg_hits:
                    negative_topics[w] += 1
            else:
                sentiment_counts["neutral"] += 1

        company = filing.get("company_name", "the company")
        form_type = filing.get("form_type", "10-Q/10-K")

        return {
            "financial_summary": f"{company} latest {form_type} metadata was collected. Detailed body parsing may be limited in demo mode.",
            "management_view": "Management appears focused on execution continuity, product strategy, and cost/risk balancing based on filing context and news tone.",
            "risk_factors": [
                "Macroeconomic uncertainty and demand fluctuations",
                "Regulatory and legal exposure",
                "Supply chain and operational execution risks",
            ],
            "sentiment_distribution": {
                "positive": int(sentiment_counts["positive"]),
                "neutral": int(sentiment_counts["neutral"]),
                "negative": int(sentiment_counts["negative"]),
            },
            "positive_topics": [k for k, _ in positive_topics.most_common(5)]
            or ["product momentum", "services growth"],
            "negative_topics": [k for k, _ in negative_topics.most_common(5)]
            or ["regulatory risk", "competition pressure"],
        }

    @staticmethod
    def _normalize(data: dict[str, Any]) -> dict[str, Any]:
        risk_factors = data.get("risk_factors", [])
        if not isinstance(risk_factors, list):
            risk_factors = [str(risk_factors)]

        pos_topics = data.get("positive_topics", [])
        if not isinstance(pos_topics, list):
            pos_topics = [str(pos_topics)]

        neg_topics = data.get("negative_topics", [])
        if not isinstance(neg_topics, list):
            neg_topics = [str(neg_topics)]

        sent = data.get("sentiment_distribution", {})
        if not isinstance(sent, dict):
            sent = {}

        return {
            "financial_summary": str(data.get("financial_summary", "")),
            "management_view": str(data.get("management_view", "")),
            "risk_factors": [str(x) for x in risk_factors],
            "sentiment_distribution": {
                "positive": int(sent.get("positive", 0)),
                "neutral": int(sent.get("neutral", 0)),
                "negative": int(sent.get("negative", 0)),
            },
            "positive_topics": [str(x) for x in pos_topics],
            "negative_topics": [str(x) for x in neg_topics],
            "analysis_mode": str(data.get("analysis_mode", "fallback")),
            "analysis_notes": str(data.get("analysis_notes", "")),
        }
