#!/usr/bin/env python3
"""
Portfolio state schema — dataclasses + validator.

Usage:
  python3 scripts/schema.py              # validate portfolio_state.json
  python3 scripts/schema.py <path>       # validate a specific file
  python3 scripts/schema.py --dump SE    # print normalised holding as JSON

Called automatically as a post-write hook by Claude Code.
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional

# ── Paths ─────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).parent.parent
PORTFOLIO_FILE = ROOT / "portfolio_state.json"

# ── Allowed values ─────────────────────────────────────────────────────────────
VALID_TYPES    = {"equity", "etf", "thai_bank", "thai_other"}
VALID_THESIS   = {"intact", "dented", "broken", "parking", "unset"}
VALID_ACTIONS  = {"hold", "add", "trim", "exit", "watch"}
GARP_KEYS      = {"growth", "profitability", "balance_sheet", "moat",
                  "management", "secular_trend", "valuation", "technical"}
SCENARIO_KEYS  = {"bear", "base", "bull"}

# Fields the dashboard JS actually reads — must be present in every scenario
DASHBOARD_SCENARIO_FIELDS = {"revenue_target", "net_margin", "cagr"}


# ── Dataclasses ────────────────────────────────────────────────────────────────

@dataclass
class ScenarioData:
    # Dashboard-consumed (required)
    revenue_target: Optional[float] = None
    net_margin:     Optional[float] = None
    cagr:           Optional[int]   = None
    # Supplementary (written by /scenarios command, not read by dashboard)
    net_income:              Optional[float] = None
    eps:                     Optional[float] = None
    exit_pe:                 Optional[int]   = None
    price_target:            Optional[float] = None
    cumulative_dividends:    Optional[float] = None
    share_count_reduction_pct: Optional[float] = None
    total_return_pct:        Optional[float] = None
    irr:                     Optional[float] = None


@dataclass
class Scenarios:
    bear: ScenarioData = field(default_factory=ScenarioData)
    base: ScenarioData = field(default_factory=ScenarioData)
    bull: ScenarioData = field(default_factory=ScenarioData)


@dataclass
class GarpScores:
    growth:        int = 0
    profitability: int = 0
    balance_sheet: int = 0
    moat:          int = 0
    management:    int = 0
    secular_trend: int = 0
    valuation:     int = 0
    technical:     int = 0


@dataclass
class LatestEarnings:
    quarter:         Optional[str]   = None
    revenue_actual:  Optional[float] = None
    revenue_est:     Optional[float] = None
    eps_actual:      Optional[float] = None
    eps_est:         Optional[float] = None


@dataclass
class Holding:
    ticker:         str
    name:           str
    weight:         float
    type:           str                         # VALID_TYPES
    current_price:  Optional[float] = None
    last_review_date: Optional[str] = None
    thesis_status:  str = "unset"               # VALID_THESIS
    action:         str = "hold"                # VALID_ACTIONS
    target_year:    Optional[int]  = None       # projection horizon; default = currentYear+5
    garp_scores:    GarpScores     = field(default_factory=GarpScores)
    scenarios:      Scenarios      = field(default_factory=Scenarios)
    latest_earnings: LatestEarnings = field(default_factory=LatestEarnings)
    thesis_summary: str  = ""
    key_risks:      list = field(default_factory=list)
    red_flags:      list = field(default_factory=list)
    notes:          str  = ""


@dataclass
class NonHolding:
    label:  str
    weight: float
    type:   str   # cash | bond


@dataclass
class PortfolioState:
    last_updated:  str
    holdings:      list
    non_holdings:  list


# ── Validator ──────────────────────────────────────────────────────────────────

def validate(path: Path = PORTFOLIO_FILE) -> list[str]:
    """Return list of error strings. Empty list = valid."""
    errors: list[str] = []

    try:
        with open(path) as f:
            data = json.load(f)
    except Exception as e:
        return [f"PARSE ERROR: {e}"]

    if "last_updated" not in data:
        errors.append("Missing top-level field: last_updated")
    if "holdings" not in data:
        errors.append("Missing top-level field: holdings")
        return errors

    for h in data["holdings"]:
        t = h.get("ticker", "?")

        # Enum fields
        if h.get("type") not in VALID_TYPES:
            errors.append(f"{t}: invalid type '{h.get('type')}' — must be one of {sorted(VALID_TYPES)}")
        if h.get("thesis_status") not in VALID_THESIS:
            errors.append(f"{t}: invalid thesis_status '{h.get('thesis_status')}'")
        if h.get("action") not in VALID_ACTIONS:
            errors.append(f"{t}: invalid action '{h.get('action')}'")

        # GARP scores — all 8 keys required
        gs = h.get("garp_scores", {})
        missing_garp = GARP_KEYS - set(gs.keys())
        if missing_garp:
            errors.append(f"{t}: garp_scores missing keys: {sorted(missing_garp)}")

        # Scenarios — all 3 cases required, all 3 dashboard fields required
        sc = h.get("scenarios", {})
        missing_cases = SCENARIO_KEYS - set(sc.keys())
        if missing_cases:
            errors.append(f"{t}: scenarios missing cases: {sorted(missing_cases)}")

        has_data = False
        for s in SCENARIO_KEYS:
            c = sc.get(s, {})
            missing_fields = DASHBOARD_SCENARIO_FIELDS - set(c.keys())
            if missing_fields:
                errors.append(
                    f"{t}.scenarios.{s}: missing dashboard field(s): {sorted(missing_fields)}"
                )
            if any(c.get(f) is not None for f in DASHBOARD_SCENARIO_FIELDS):
                has_data = True

        # target_year must be set when scenario data is populated
        if has_data and h.get("target_year") is None:
            errors.append(
                f"{t}: scenario data present but target_year is null — set it explicitly"
            )

    return errors


# ── CLI ────────────────────────────────────────────────────────────────────────

def main() -> None:
    args = sys.argv[1:]

    # --dump TICKER: pretty-print a blank Holding as JSON (useful for new entries)
    if args and args[0] == "--dump":
        ticker = args[1] if len(args) > 1 else "TICKER"
        h = Holding(ticker=ticker, name="", weight=0.0, type="equity")
        print(json.dumps(asdict(h), indent=2))
        return

    path = Path(args[0]) if args and not args[0].startswith("--") else PORTFOLIO_FILE

    errors = validate(path)

    if not errors:
        print(f"✓ schema valid — {path.name}")
        sys.exit(0)
    else:
        print(f"✗ {len(errors)} schema error(s) in {path.name}:")
        for e in errors:
            print(f"  · {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
