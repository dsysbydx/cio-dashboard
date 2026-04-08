Full GARP checklist scoring with rationale for $ARGUMENTS.

Workflow:
1. Web search for latest financials, analyst reports, recent news on $ARGUMENTS
2. For dimension 5 (Management), explicitly research:
   - **Skin in the game:** insider ownership % and recent Form 4 / insider buy/sell activity
   - **Glassdoor:** overall rating, CEO approval %, trend (improving or declining)
   - **Red flag scan:** search "[TICKER] CEO fraud", "[TICKER] SEC investigation", "[TICKER] accounting restatement", "[TICKER] related party", "[TICKER] executive departure" — flag anything material
3. Score all 8 GARP dimensions 1–5 with one-sentence rationale each
4. Flag any dimension ≤ 2 explicitly
4. Update `portfolio_state.json` for this ticker:
   - `garp_scores` object with all 8 scores
   - `last_review_date` to today
5. Print confirmation: "✓ portfolio_state.json updated — $ARGUMENTS garp_scores"

Output format:

```
## [TICKER] — GARP Checklist
Scored: [DATE]  |  Total: [X]/40

| # | Dimension      | Score | Rationale |
|---|----------------|-------|-----------|
| 1 | Growth         | [1-5] | ...       |
| 2 | Profitability  | [1-5] | ...       |
| 3 | Balance Sheet  | [1-5] | ...       |
| 4 | Moat           | [1-5] | ...       |
| 5 | Management     | [1-5] | Capital allocation: ... Ownership: X% insider, recent [buys/sells/none]. Glassdoor: X.X/5 (CEO X% approval, [rising/falling/stable]). Red flags: [none / list issues] |
| 6 | Secular Trend  | [1-5] | ...       |
| 7 | Valuation      | [1-5] | ...       |
| 8 | Technical      | [1-5] | ...       |

🚩 Red flags: [list any score ≤ 2]
Overall: [one sentence verdict]
```
