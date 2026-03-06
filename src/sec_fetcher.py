from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from typing import Any

import requests

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None


SEC_TICKER_URL = "https://www.sec.gov/files/company_tickers.json"
SEC_SUBMISSIONS_URL = "https://data.sec.gov/submissions/CIK{cik}.json"
SEC_ARCHIVES_BASE = "https://www.sec.gov/Archives/edgar/data"
SEC_ATOM_URL = (
    "https://www.sec.gov/cgi-bin/browse-edgar"
    "?action=getcompany&CIK={ticker}&type=10-&owner=exclude&count=40&output=atom"
)


class SecFetcher:
    def __init__(self, user_agent: str, timeout: int = 30):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": user_agent,
                "Accept-Encoding": "gzip, deflate",
            }
        )

    def fetch_latest_filing(self, ticker: str) -> dict[str, Any]:
        ticker_norm = ticker.upper().strip()
        result: dict[str, Any] = {
            "company_name": "",
            "ticker": ticker_norm,
            "form_type": "",
            "filing_date": "",
            "accession_number": "",
            "filing_url": "",
            "filing_snippet": "",
            "errors": [],
            "source": "sec_live",
        }

        try:
            cik = self._get_cik_for_ticker(ticker_norm)
            submissions = self._get_submissions(cik)
            filing = self._pick_latest_10k_or_10q(submissions)
            result.update(filing)
            result["company_name"] = submissions.get("name", "")
            result["ticker"] = ticker_norm
            if result.get("filing_url"):
                result["filing_snippet"] = self._fetch_filing_snippet(result["filing_url"])
            return result
        except Exception as primary_exc:
            result["errors"].append(f"SEC JSON endpoint failed: {primary_exc}")

        try:
            atom_result = self._fetch_from_atom_feed(ticker_norm)
            result.update(atom_result)
            result["source"] = "sec_atom_feed"
            if result.get("filing_url"):
                result["filing_snippet"] = self._fetch_filing_snippet(result["filing_url"])
            return result
        except Exception as atom_exc:
            result["errors"].append(f"SEC Atom endpoint failed: {atom_exc}")

        result["source"] = "sec_fallback"
        result.update(self._fallback_filing(ticker_norm))
        return result

    def _get_cik_for_ticker(self, ticker: str) -> str:
        resp = self.session.get(SEC_TICKER_URL, timeout=self.timeout)
        resp.raise_for_status()
        raw = resp.json()

        for _, item in raw.items():
            if str(item.get("ticker", "")).upper() == ticker:
                cik_int = int(item["cik_str"])
                return f"{cik_int:010d}"
        raise ValueError(f"Ticker not found in SEC ticker list: {ticker}")

    def _get_submissions(self, cik: str) -> dict[str, Any]:
        url = SEC_SUBMISSIONS_URL.format(cik=cik)
        resp = self.session.get(url, timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()

    def _pick_latest_10k_or_10q(self, submissions: dict[str, Any]) -> dict[str, Any]:
        recent = submissions.get("filings", {}).get("recent", {})
        forms = recent.get("form", [])
        accession_numbers = recent.get("accessionNumber", [])
        filing_dates = recent.get("filingDate", [])
        primary_documents = recent.get("primaryDocument", [])

        target_index = -1
        for idx, form in enumerate(forms):
            if form in {"10-K", "10-Q"}:
                target_index = idx
                break

        if target_index == -1:
            raise ValueError("No recent 10-K or 10-Q found in SEC submissions")

        accession = accession_numbers[target_index]
        accession_nodash = accession.replace("-", "")
        filing_date = filing_dates[target_index]
        form_type = forms[target_index]
        primary_doc = primary_documents[target_index]

        cik_no_leading = str(int(submissions.get("cik", "0")))
        filing_url = (
            f"{SEC_ARCHIVES_BASE}/{cik_no_leading}/{accession_nodash}/{primary_doc}"
        )

        return {
            "form_type": form_type,
            "filing_date": filing_date,
            "accession_number": accession,
            "filing_url": filing_url,
        }

    def _fetch_from_atom_feed(self, ticker: str) -> dict[str, Any]:
        url = SEC_ATOM_URL.format(ticker=ticker)
        resp = self.session.get(url, timeout=self.timeout)
        resp.raise_for_status()

        root = ET.fromstring(resp.text)
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        entries = root.findall("atom:entry", ns)
        if not entries:
            raise ValueError("No entries found in SEC Atom feed")

        for entry in entries:
            title = (entry.findtext("atom:title", default="", namespaces=ns) or "").strip()
            if "10-Q" not in title and "10-K" not in title:
                continue

            updated = (entry.findtext("atom:updated", default="", namespaces=ns) or "").strip()
            link_node = entry.find("atom:link", ns)
            filing_url = link_node.attrib.get("href", "").strip() if link_node is not None else ""
            form_type = "10-Q" if "10-Q" in title else "10-K"

            accession = self._extract_accession_from_url(filing_url)
            company = self._extract_company_from_feed(root)

            return {
                "company_name": company or f"{ticker} (SEC Feed)",
                "ticker": ticker,
                "form_type": form_type,
                "filing_date": updated[:10] if updated else "",
                "accession_number": accession,
                "filing_url": filing_url,
            }

        raise ValueError("No 10-Q/10-K entries found in Atom feed")

    @staticmethod
    def _extract_company_from_feed(root: ET.Element) -> str:
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        subtitle = (root.findtext("atom:subtitle", default="", namespaces=ns) or "").strip()
        if subtitle:
            return subtitle
        feed_title = (root.findtext("atom:title", default="", namespaces=ns) or "").strip()
        return feed_title

    @staticmethod
    def _extract_accession_from_url(url: str) -> str:
        match = re.search(r"accession_number=(\d{10}-\d{2}-\d{6})", url)
        if match:
            return match.group(1)
        return "N/A"

    def _fetch_filing_snippet(self, filing_url: str) -> str:
        resp = self.session.get(filing_url, timeout=self.timeout)
        resp.raise_for_status()

        if BeautifulSoup:
            text_source = resp.text.lstrip()
            parser = "xml" if text_source.startswith("<?xml") else "lxml"
            soup = BeautifulSoup(resp.text, parser)
            text = soup.get_text(" ", strip=True)
        else:
            text = re.sub(r"<[^>]+>", " ", resp.text)

        text = re.sub(r"\s+", " ", text)
        return text[:2000]

    @staticmethod
    def _fallback_filing(ticker: str) -> dict[str, Any]:
        if ticker == "AAPL":
            return {
                "company_name": "Apple Inc. (Fallback Sample)",
                "ticker": "AAPL",
                "form_type": "10-Q",
                "filing_date": "2025-02-01",
                "accession_number": "0000320193-25-000001",
                "filing_url": "https://www.sec.gov/edgar/browse/?CIK=320193",
                "filing_snippet": "Fallback snippet used because SEC live retrieval was unavailable.",
            }

        return {
            "company_name": f"{ticker} (Fallback Sample)",
            "ticker": ticker,
            "form_type": "10-Q",
            "filing_date": "N/A",
            "accession_number": "N/A",
            "filing_url": "https://www.sec.gov/edgar/search/",
            "filing_snippet": "Fallback snippet used because SEC live retrieval was unavailable.",
        }
