# IMPLEMENTATION RUNBOOK

Execution of this project must strictly follow `PLAN.md` milestone order.

## Mandatory Execution Rules
1. Complete milestones sequentially.
2. After each milestone, run the milestone validation command immediately.
3. If validation fails, fix the failure before moving forward.
4. Do not expand scope beyond the competition MVP deliverable.
5. Keep architecture minimal: Python CLI + SEC fetch + static news + DeepSeek/fallback + Markdown/HTML report.
6. Keep documentation synchronized continuously:
   - Update `DOCUMENTATION.md` after every milestone.
   - Keep sample outputs (`outputs/`) current after functional changes.
   - Keep `README.md` commands aligned with actual runnable commands.
7. Never commit secrets or real API keys.
8. Ensure graceful fallback when network/API access is unavailable.
9. Before finalizing, run full acceptance checks from `PLAN.md` Milestone 8.

## Required Deliverable Focus
- Working end-to-end command: `python main.py --ticker AAPL`
- Generated artifacts: markdown report, HTML report, run JSON
- Repo includes sample outputs and screenshots for no-key demo review
- README is presentation-ready and complete

## Failure Handling Strategy
- SEC parsing issue: fallback to reliable metadata retrieval and link first.
- LLM/API issue: fallback structured analysis and explicit warning in outputs.
- Screenshot issue: generate closest practical visual substitutes and document method.
