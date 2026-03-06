# MVP Delivery Plan - Automated Financial Report Summarization & Sentiment Analysis Agent

## Milestone 1 - Control Files and Execution Governance
- Objective: Establish enforceable execution workflow and acceptance standards before coding.
- Deliverables: `PLAN.md`, `IMPLEMENT.md`, `DOCUMENTATION.md`, project-level `AGENTS.md`.
- Acceptance Criteria:
  - All four files exist with non-placeholder, actionable content.
  - Milestones include objective, deliverables, acceptance criteria, and validation command.
  - Documentation file has an initialized audit trail.
- Validation Command:
  - `Get-ChildItem PLAN.md,IMPLEMENT.md,DOCUMENTATION.md,AGENTS.md`

## Milestone 2 - Project Skeleton and Core Config Files
- Objective: Create the runnable repository layout and basic dependency/config files.
- Deliverables: folders (`src`, `data`, `outputs`, `screenshots`), `requirements.txt`, `.env.example`, `.gitignore`, `main.py`, `config.py`, `prompts.py`, `utils.py`.
- Acceptance Criteria:
  - Required files and folders exist.
  - `python main.py --help` runs without import/path errors.
  - `.env.example` includes DeepSeek key variable and optional SEC user-agent identity.
- Validation Command:
  - `python main.py --help`

## Milestone 3 - SEC Filing Retrieval Module
- Objective: Implement latest 10-K/10-Q metadata retrieval from SEC EDGAR with graceful fallback.
- Deliverables: `src/sec_fetcher.py` integrated with main flow.
- Acceptance Criteria:
  - Retrieves (or gracefully falls back for) `company_name`, `ticker`, `form_type`, `filing_date`, `accession_number`, `filing_url`.
  - Handles SEC/network errors with explicit message in output artifact.
- Validation Command:
  - `python main.py --ticker AAPL --skip-llm --output-dir outputs`

## Milestone 4 - Static News Data and Loader
- Objective: Add static sample news dataset and loader.
- Deliverables: `data/sample_news_aapl.json`, `src/news_loader.py`.
- Acceptance Criteria:
  - Dataset includes at least 10 items with `date`, `source`, `title`.
  - Loader validates required fields and returns clean list.
- Validation Command:
  - `python -c "from src.news_loader import load_news_items; print(len(load_news_items('data/sample_news_aapl.json')))" `

## Milestone 5 - DeepSeek Analysis Integration and Fallback
- Objective: Implement filing summarization + sentiment analysis pipeline using DeepSeek API with robust fallback mode.
- Deliverables: `src/llm_analyzer.py`, updates to `prompts.py`.
- Acceptance Criteria:
  - Reads API key from environment variable.
  - Produces structured keys: `financial_summary`, `management_view`, `risk_factors`, `sentiment_distribution`, `positive_topics`, `negative_topics`.
  - If API unavailable, fallback analysis still returns complete structure.
- Validation Command:
  - `python main.py --ticker AAPL --output-dir outputs`

## Milestone 6 - Report Generation (Markdown + HTML)
- Objective: Generate presentable markdown and HTML reports from pipeline output.
- Deliverables: `src/report_generator.py`, `src/formatter.py`.
- Acceptance Criteria:
  - Generates `outputs/sample_report.md` and `outputs/sample_report.html`.
  - Report includes required sections and disclaimer.
- Validation Command:
  - `python main.py --ticker AAPL --output-dir outputs`

## Milestone 7 - README, Sample Outputs, and Screenshots
- Objective: Deliver presentation-ready repository assets.
- Deliverables: complete `README.md`, `outputs/sample_run.json`, screenshot assets in `screenshots/`.
- Acceptance Criteria:
  - README covers all mandatory sections and references actual paths.
  - At least 3 screenshot files exist and are embedded in README.
  - Sample output files are committed for no-key demo review.
- Validation Command:
  - `Get-ChildItem outputs/sample_report.md,outputs/sample_report.html,outputs/sample_run.json,screenshots/terminal_run.png,screenshots/report_preview.png,screenshots/repo_structure.png`

## Milestone 8 - Final Acceptance Check and Consistency Pass
- Objective: Verify full Definition of Done and remove inconsistencies.
- Deliverables: updated `DOCUMENTATION.md` final checklist and any required fixes.
- Acceptance Criteria:
  - Main command works from clean environment using README instructions.
  - No obvious path/import/README-command mismatches.
  - Definition of Done checklist fully mapped and satisfied.
- Validation Command:
  - `python main.py --ticker AAPL --output-dir outputs`
  - `python -c "import main, config, prompts, utils; from src import sec_fetcher, news_loader, llm_analyzer, report_generator, formatter; print('imports_ok')"`
