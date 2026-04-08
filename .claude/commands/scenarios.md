Update bear/base/bull scenarios to 2031 for $ARGUMENTS.

Workflow:
1. Read current scenarios from `portfolio_state.json` for $ARGUMENTS
2. Web search for latest analyst consensus, management guidance, TAM estimates, competitive dynamics, dividend policy, and buyback history/authorization
3. Produce updated scenarios with clear reasoning for each case
4. For total return calculation:
   - Project cumulative dividends per share to 2031
   - Project share count reduction from buybacks, estimate EPS uplift
   - Calculate total return = (price target − current price + cumulative dividends) / current price
   - State assumed exit multiple explicitly
5. Update `portfolio_state.json` scenarios object for this ticker
6. Print confirmation: "✓ portfolio_state.json updated — $ARGUMENTS scenarios"

Output format:

```
## [TICKER] — Scenarios to 2031
Updated: [DATE]  |  Base year: [YEAR]  |  Current price: $[X]

|                        | Bear    | Base    | Bull    |
|------------------------|---------|---------|---------|
| Revenue 2031           | $XB     | $XB     | $XB     |
| Revenue CAGR           | X%      | X%      | X%      |
| Net Margin 2031        | X%      | X%      | X%      |
| Net Income 2031        | $XB     | $XB     | $XB     |
| EPS 2031               | $X.XX   | $X.XX   | $X.XX   |
| Exit Multiple (P/E)    | Xx      | Xx      | Xx      |
| Price Target 2031      | $XXX    | $XXX    | $XXX    |
| Cumulative Dividends   | $X.XX   | $X.XX   | $X.XX   |
| Share Count Reduction  | X%      | X%      | X%      |
| Total Return (to 2031) | XX%     | XX%     | XX%     |
| IRR (annualised)       | X%      | X%      | X%      |

Bear rationale: ...
Base rationale: ...
Bull rationale: ...

Key assumptions: [exit multiple rationale, buyback pace, dividend growth rate]
```