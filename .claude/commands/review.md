Full review and update of an existing holding for $ARGUMENTS.

Updates every field in portfolio_state.json for this ticker in one pass:
latest_earnings · garp_scores · scenarios · red_flags · key_risks · thesis_summary · thesis_status · action · last_review_date · target_year

Workflow:
1. Read current state from `portfolio_state.json` for $ARGUMENTS — note what's stale or null
2. Web search (run in parallel where possible):
   - Latest earnings results + guidance (actuals vs estimates)
   - Analyst consensus price targets and revenue/EPS forecasts
   - Recent news (last 90 days): management changes, product launches, competitive moves
   - Long-term targets: TAM, management guidance, investor day updates
   - Management: insider ownership %, recent buy/sell activity
   - Glassdoor: overall rating, CEO approval %, trend
   - Red flag scan: "[TICKER] fraud", "[TICKER] SEC investigation", "[TICKER] restatement", "[TICKER] related party", "[TICKER] executive departure"
3. Update `latest_earnings` — most recent reported quarter (or half-year if that's how they report)
   - Include `revenue_growth` (YoY %) and `eps_growth` (YoY %) in addition to actuals vs estimates
4. Score all 8 GARP dimensions 1–5 with rationale
5. Build bear/base/bull scenarios to `target_year` (default: currentYear+5 = 2031)
   - Set `target_year` explicitly on the holding
   - Use `revenue_target`, `net_margin`, `cagr` as the three dashboard fields
   - Also compute: net_income, eps, exit_pe, price_target, total_return_pct, irr
6. Reassess red_flags — replace entirely (do not append to stale list):
   - 🔴 prefix for critical issues (thesis-breaking, fraud, major miss)
   - 🟡 prefix for caution items (watch closely, one-quarter issue)
7. Reassess thesis_status: intact | dented | broken | parking
8. Reassess action: hold | add | trim | exit | watch
9. Update thesis_summary (2–3 sentences: what the business does, why it wins, what to watch)
10. Update key_risks (3–5 bullets — specific, not generic)
11. Write ALL updated fields to `portfolio_state.json` — merge, do not replace the full file
12. Run `python3 scripts/schema.py` and confirm clean
13. Print confirmation: "✓ portfolio_state.json updated — $ARGUMENTS full review"

Output format:

```
## [TICKER] — Full Review
Reviewed: [DATE]  |  Price: $[X]  |  Target year: [YEAR]

### Earnings — [Quarter]
| Metric  | Actual | Est    | Delta  |
|---------|--------|--------|--------|
| Revenue | $XB    | $XB    | +X%    |
| EPS     | $X.XX  | $X.XX  | +X%    |
[1–2 sentence commentary: guidance delta, key beat/miss driver]

### GARP Checklist  (Total: [X]/40)
| # | Dimension      | Score | Rationale |
|---|----------------|-------|-----------|
| 1 | Growth         | [1-5] | ...       |
| 2 | Profitability  | [1-5] | ...       |
| 3 | Balance Sheet  | [1-5] | ...       |
| 4 | Moat           | [1-5] | ...       |
| 5 | Management     | [1-5] | Ownership: X%. Glassdoor X.X/5, CEO X% approval. Red flags: [none/list] |
| 6 | Secular Trend  | [1-5] | ...       |
| 7 | Valuation      | [1-5] | ...       |
| 8 | Technical      | [1-5] | ...       |

### Scenarios to [YEAR]
|                        | Bear    | Base    | Bull    |
|------------------------|---------|---------|---------|
| Revenue [YEAR]         | $XB     | $XB     | $XB     |
| Revenue CAGR           | X%      | X%      | X%      |
| Net Margin             | X%      | X%      | X%      |
| EPS                    | $X.XX   | $X.XX   | $X.XX   |
| Exit Multiple (P/E)    | Xx      | Xx      | Xx      |
| Price Target           | $XXX    | $XXX    | $XXX    |
| Cumulative Dividends   | $X.XX   | $X.XX   | $X.XX   |
| Total Return           | XX%     | XX%     | XX%     |
| IRR (annualised)       | X%      | X%      | X%      |

### Flags & Risks
[Red flags list — 🔴/🟡 prefixed]

Key risks:
[3–5 bullet points]

### Verdict
Thesis: [intact | dented | broken | parking]
Action: [hold | add | trim | exit | watch]
Summary: [2–3 sentences]
[One sentence on what would change the verdict — the single most important thing to watch]
```
