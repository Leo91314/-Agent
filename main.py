from __future__ import annotations

import argparse
from pathlib import Path

from config import load_config
from src.llm_analyzer import LLMAnalyzer
from src.news_loader import load_news_items
from src.report_generator import generate_reports
from src.sec_fetcher import SecFetcher
from utils import ensure_dir, utc_now_iso, write_json


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Automated Financial Report Summarization & Sentiment Analysis Agent (Demo MVP)"
    )
    parser.add_argument("--ticker", default="AAPL", help="Stock ticker, default: AAPL")
    parser.add_argument(
        "--news-file",
        default="data/sample_news_aapl.json",
        help="Path to local static news JSON file",
    )
    parser.add_argument("--output-dir", default="outputs", help="Output directory path")
    parser.add_argument(
        "--skip-llm",
        action="store_true",
        help="Skip DeepSeek call and use fallback analysis",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    cfg = load_config()

    ensure_dir(args.output_dir)

    sec = SecFetcher(user_agent=cfg.sec_user_agent, timeout=cfg.request_timeout)
    filing = sec.fetch_latest_filing(args.ticker)

    news_items = load_news_items(args.news_file)

    analyzer = LLMAnalyzer(
        api_key=cfg.deepseek_api_key,
        base_url=cfg.deepseek_base_url,
        model=cfg.deepseek_model,
        timeout=cfg.request_timeout,
    )
    analysis = analyzer.analyze(filing=filing, news_items=news_items, skip_llm=args.skip_llm)

    run_data = {
        "generated_at": utc_now_iso(),
        "filing": filing,
        "news_items": news_items,
        "analysis": analysis,
    }

    report_paths = generate_reports(run_data=run_data, output_dir=args.output_dir)

    run_json_path = Path(args.output_dir) / "sample_run.json"
    write_json(str(run_json_path), run_data)

    print("Run completed.")
    print(f"Ticker: {filing.get('ticker')}")
    print(f"Company: {filing.get('company_name')}")
    print(f"Form: {filing.get('form_type')} | Filing Date: {filing.get('filing_date')}")
    print(f"Filing URL: {filing.get('filing_url')}")
    print(f"Markdown report: {report_paths['markdown_report']}")
    print(f"HTML report: {report_paths['html_report']}")
    print(f"Run artifact: {run_json_path}")

    if filing.get("errors"):
        print(f"SEC warnings: {filing['errors']}")
    if analysis.get("analysis_notes"):
        print(f"Analysis notes: {analysis['analysis_notes']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
