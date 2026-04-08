Full earnings brief for the latest quarter of $ARGUMENTS.

Workflow:
1. Web search for "$ARGUMENTS Q[N] [YEAR] earnings results"
2. Fetch the actual earnings release (SEC 6-K/8-K or IR page)
3. Fetch the earnings call transcript if available
4. Produce the brief in the format below
5. Update `portfolio_state.json` for this ticker:
   - `latest_earnings` object (quarter, actuals vs estimates)
   - Add red flags if EPS/rev miss, guidance cut, tone shift
   - Update `last_review_date` to today
6. Print confirmation: "✓ portfolio_state.json updated — $ARGUMENTS [what changed]"

Output format:

```
## [TICKER] — [Quarter] Earnings Brief
Report date: [DATE]

### Executive Summary
| Metric | Actual | Estimate | Delta |
...

### Segment Breakdown
[One line per segment: revenue, growth, key note]

### Guidance Delta
[What changed, what held, management narrative — prose not table]

### Key Quotes
[2–3 direct quotes from CEO/CFO on outlook or thesis-relevant topics]

### Thesis Check
[Does this quarter reinforce, dent, or break the bull case? Be direct.]

### Red Flags
[Anything warranting attention: tone shift, margin pressure, guidance language]
```
