Full portfolio health check across all holdings.

Workflow:
1. Read `portfolio_state.json` — load all holdings
2. Also read Holdings tab from Google Sheet via `python scripts/sync_sheet.py` to get latest weights and cost basis
3. For each holding with weight > 0:
   a. Check if thesis_status is intact/dented/broken
   b. Check if last_review_date is stale (> 90 days = warning)
   c. Check weight against 7% limit
   d. Check garp_scores for any dimension ≤ 2
4. Check portfolio-level concentration:
   - Any single theme > 30% of equity weight?
   - Thai bank total > 8%?
   - Any position drifted above 7%?
5. Produce output below
6. Do NOT update portfolio_state.json automatically — print findings and ask me to confirm before writing

Output format:

```
## Portfolio Health Check — [DATE]

### 🚨 Immediate Attention
[Positions with broken thesis, > 7% weight, or score ≤ 2 on any dimension]

### ⚠ Watch List
[Dented thesis, stale reviews > 90 days, approaching 7% limit]

### ✅ Healthy
[Intact thesis, recently reviewed, within limits]

### Concentration Check
[Theme/sector exposure analysis]

### Suggested Actions
[Specific trim/exit/add suggestions with reasoning tied to GARP criteria]

### Gaps
[Themes or types of businesses I should be looking at that I'm not]
```