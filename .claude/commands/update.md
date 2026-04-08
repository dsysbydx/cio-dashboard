Quick manual override for a single field in portfolio_state.json.

Arguments format: [TICKER] [FIELD] [VALUE]

Examples:
- `SE thesis_status dented`
- `META action trim`
- `GOOGL garp.valuation 3`
- `SE scenarios.base.cagr 22`

Workflow:
1. Parse $ARGUMENTS into ticker, field path, and value
2. Read current portfolio_state.json
3. Update only the specified field using dot-notation path (e.g. garp.valuation → garp_scores.valuation)
4. Set last_review_date to today for that ticker
5. Write back to portfolio_state.json
6. Print confirmation: "✓ portfolio_state.json updated — [TICKER] [FIELD] = [VALUE]"