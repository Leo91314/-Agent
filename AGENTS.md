# Project AGENTS Instructions

## Project Goal
Deliver a fully runnable, presentation-ready MVP for:
Automated Financial Report Summarization & Sentiment Analysis Agent.

## MVP Scope (Must Include)
- Python CLI pipeline
- SEC EDGAR latest 10-K/10-Q metadata retrieval
- Static local news loading from JSON
- DeepSeek API summarization + sentiment analysis (with fallback)
- Markdown and HTML report generation
- Sample outputs and screenshots committed
- Complete README with run/demo guidance

## Forbidden / Out of Scope
- Airflow, Docker, database, multi-user system
- Complex frontend/backend split
- Real-time alerting, trading integration
- Live web-scale scraping
- Heavy framework dependencies
- Any non-essential feature expansion

## Validation Requirements
- Validate after each milestone in `PLAN.md`.
- Do not proceed with known failing validation.
- Final acceptance check must verify all Definition of Done items.

## Deliverable Requirements
- Required files: `requirements.txt`, `.env.example`, `.gitignore`, `README.md`
- Required outputs: `outputs/sample_report.md`, `outputs/sample_report.html`, `outputs/sample_run.json`
- Required screenshots: `screenshots/terminal_run.png`, `screenshots/report_preview.png`, `screenshots/repo_structure.png`
- Main command must run end-to-end: `python main.py --ticker AAPL`

## Code Style and Architecture
- Keep code simple, readable, and modular under `src/`.
- Prefer explicit error handling and deterministic fallback behavior.
- Avoid overengineering and heavy abstractions.

## README Priority
README is a core deliverable and must remain consistent with actual runnable commands and generated outputs.

## Secrets Handling Rules
- Never commit real API keys or secrets.
- Read secrets only from environment variables.
- Keep `.env` excluded via `.gitignore`.
