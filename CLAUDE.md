# CIO Research System — Claude Code Configuration

---

## INVESTOR IDENTITY

**Style:** GARP — great businesses growing fast, but valuation matters.
**Moat:** Required. Pricing power, network effects, switching costs, cost advantages, intangibles. No moat = pass.
**Management:** Capital allocation track record matters. Prefer founders/owner-operators.
**Themes:** Cloud infra/platforms · Generative AI (picks+shovels and moated apps) · SaaS with strong retention · Any sector with genuine moat + secular tailwind

**Thai Bank Exception:** KBANK.BK, BBL.BK, SCB are capital parking positions. Moat = regulatory oligopoly. Evaluate on moat quality + dividend yield + capital preservation. Do NOT penalise for low growth. Combined weight ≤ 8%.

**Portfolio rules:** 15–25 stocks · 7% max per position (flag if breached) · No leverage/margin · Exit if thesis breaks or better opportunity exists

---

## FILES

Base path: `~/cio-dashboard/`

| File | Purpose |
|------|---------|
| `portfolio_state.json` | Main data file — read before every write, always merge |
| `dashboard.html` | Visual dashboard — do not modify |
| `server.py` | Local server (`python server.py` → localhost:8080) — do not modify |
| `scripts/sync_sheet.py` | Google Sheets sync via gspread |

**Critical:** Always read `portfolio_state.json` before writing. Merge changes — never replace the full file unless explicitly asked.

---

## GARP CHECKLIST — 8 DIMENSIONS (score 1–5, flag ≤ 2)

1. **Growth** — Revenue + earnings 3yr CAGR. Accelerating or decelerating? Volume/price/mix?
2. **Profitability** — Gross margin trend. Operating leverage. FCF conversion.
3. **Balance Sheet** — Net cash/debt. Debt/EBITDA. Self-funding? Refinancing risk?
4. **Moat** — What specifically protects it? How durable? Widening or narrowing?
5. **Management** — Capital allocation history. Insider ownership % + recent buy/sell activity. Glassdoor rating + CEO approval trend. Red flag scan: fraud, SEC actions, restatements, related-party deals, key departures.
6. **Secular Trend** — 10–20yr structural tailwind? TAM remaining?
7. **Valuation** — P/E, EV/EBITDA, P/FCF, PEG vs peers and history. Growth implied by price?
8. **Technical** — Good entry? (Only relevant after dimensions 1–7 are satisfactory.)

---

## SCENARIO FRAMEWORK

Three scenarios per holding: Bear / Base / Bull.
**Target year** (`target_year`) is set per holding — default **5 years forward** (currently 2031). Use a shorter horizon (e.g. 3yr) for capital-parking positions; longer (e.g. 7yr) for compounders. Always set `target_year` explicitly when writing scenarios.
Metrics: Revenue · Net Margin · Net Income · EPS · Price Target · Cumulative Dividends · Share Count Reduction · Total Return · IRR (annualised).
Bear = competition/macro/thesis partially wrong · Base = guidance delivered, normal execution · Bull = all segments fire, TAM expands faster

**Dashboard-consumed scenario fields (must match exactly):**
- `revenue_target` — projected revenue at `target_year` (€B or $B)
- `net_margin` — net margin % at `target_year`
- `cagr` — revenue CAGR from base year to `target_year` (%)

---

## COMMANDS

Full workflows and output formats are in `.claude/commands/`. Commands:

| Command | Purpose |
|---------|---------|
| `/earnings [TICKER]` | Latest quarter brief — actuals vs estimates, guidance delta, thesis check |
| `/checklist [TICKER]` | GARP 8-dimension scoring |
| `/scenarios [TICKER]` | Bear/base/bull to 2031 with returns model |
| `/healthcheck` | Full portfolio health scan — does NOT auto-write, confirm first |
| `/research [TICKER]` | Full new-name research — business summary, checklist, scenarios, fit, recommendation |
| `/sync` | Two-way sync with Google Sheet |
| `/update [TICKER] [FIELD] [VALUE]` | Quick single-field override |

---

## portfolio_state.json SCHEMA

```json
{
  "last_updated": "YYYY-MM-DD",
  "holdings": [
    {
      "ticker": "SE",
      "name": "Sea Limited",
      "weight": 0.00,
      "type": "equity",
      "current_price": 88.00,
      "last_review_date": "2026-03-24",
      "thesis_status": "dented",
      "action": "watch",
      "target_year": 2031,
      "garp_scores": {
        "growth": 4, "profitability": 3, "balance_sheet": 5,
        "moat": 4, "management": 3, "secular_trend": 5,
        "valuation": 4, "technical": 2
      },
      "scenarios": {
        "bear": { "revenue_target": 46, "net_margin": 7.5, "cagr": 15 },
        "base": { "revenue_target": 62, "net_margin": 12.0, "cagr": 22 },
        "bull": { "revenue_target": 78, "net_margin": 16.0, "cagr": 28 }
      },
      "latest_earnings": {
        "quarter": "Q4 2025",
        "revenue_actual": 6.9, "revenue_est": 6.49,
        "eps_actual": 0.63, "eps_est": 0.80
      },
      "thesis_summary": "...",
      "key_risks": ["risk 1", "risk 2"],
      "red_flags": ["🔴 Critical flag", "🟡 Caution flag"],
      "notes": ""
    }
  ],
  "non_holdings": [
    { "label": "Cash", "weight": 1.35, "type": "cash" },
    { "label": "Bond", "weight": 29.00, "type": "bond" }
  ]
}
```

**type:** `equity` | `etf` | `thai_bank` | `thai_other`
**thesis_status:** `intact` | `dented` | `broken` | `parking` | `unset`
**action:** `hold` | `add` | `trim` | `exit` | `watch`
**red_flags:** prefix 🔴 critical or 🟡 caution

---

## BEHAVIOUR

- Direct and specific. Numbers, scores, clear conclusions.
- Push back when something doesn't fit GARP criteria.
- State which quarter/data source you're referencing. Flag stale data.
- No generic financial advisor disclaimers.
- If a command is ambiguous, ask one clarifying question before proceeding.
- After every write: `✓ portfolio_state.json updated — [TICKER] [what changed]`

---

*Last updated: 2026-04-02*
