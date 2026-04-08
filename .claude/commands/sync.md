Two-way sync between portfolio_state.json and Google Sheet.

Workflow:
1. Run `python scripts/sync_sheet.py --direction both`
2. This script:
   - Reads Holdings tab → updates weights + cost basis in portfolio_state.json
   - Reads portfolio_state.json → writes GARP scores, scenarios, thesis status, action, last review date to "Research Output" tab
   - Appends any action changes to "Decision Log" tab
3. Print sync summary: rows read, rows written, any conflicts