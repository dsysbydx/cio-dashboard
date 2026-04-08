#!/usr/bin/env python3
"""
sync_sheet.py — Google Sheets ↔ portfolio_state.json sync
==========================================================
Usage:
    python scripts/sync_sheet.py --direction read    # Sheet → JSON only
    python scripts/sync_sheet.py --direction write   # JSON → Sheet only
    python scripts/sync_sheet.py --direction both    # Full two-way sync

SETUP (one time):
    1. pip install gspread google-auth
    2. Go to console.cloud.google.com
       → New project → Enable Google Sheets API + Google Drive API
       → Credentials → Service Account → Download JSON key
       → Save as ~/cio-dashboard/scripts/google_credentials.json
    3. Open your Google Sheet
       → Share → add the service account email (from the JSON key) as Editor
    4. Set SHEET_ID below to your Google Sheet ID
       (the long string in the URL: docs.google.com/spreadsheets/d/THIS_PART/edit)

TABS MANAGED:
    - "Holdings"        → read: ticker, weight, cost_basis (you maintain this)
    - "Thesis"          → read: ticker, bull_thesis, key_risks (you maintain this)
    - "Research Output" → write: GARP scores, scenarios, thesis status, action
    - "Decision Log"    → append: date, ticker, action, what changed
"""

import json
import argparse
from datetime import datetime
from pathlib import Path

# ── CONFIG ────────────────────────────────────────────────────────────────────

SHEET_ID = "YOUR_GOOGLE_SHEET_ID_HERE"  # ← replace this
CREDENTIALS_FILE = Path(__file__).parent / "google_credentials.json"
PORTFOLIO_FILE = Path(__file__).parent.parent / "portfolio_state.json"

# Tab names in your Google Sheet
TAB_HOLDINGS = "Holdings"
TAB_THESIS = "Thesis"
TAB_RESEARCH_OUTPUT = "Research Output"
TAB_DECISION_LOG = "Decision Log"

# ── HELPERS ───────────────────────────────────────────────────────────────────

def get_client():
    try:
        import gspread
        from google.oauth2.service_account import Credentials
    except ImportError:
        print("ERROR: Missing dependencies. Run:")
        print("  pip install gspread google-auth")
        raise SystemExit(1)

    if not CREDENTIALS_FILE.exists():
        print(f"ERROR: Credentials file not found: {CREDENTIALS_FILE}")
        print("See SETUP instructions at the top of this file.")
        raise SystemExit(1)

    scopes = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = Credentials.from_service_account_file(str(CREDENTIALS_FILE), scopes=scopes)
    return gspread.authorize(creds)


def load_portfolio():
    if not PORTFOLIO_FILE.exists():
        print(f"ERROR: {PORTFOLIO_FILE} not found. Run the dashboard first to create it.")
        raise SystemExit(1)
    with open(PORTFOLIO_FILE, "r") as f:
        return json.load(f)


def save_portfolio(data):
    data["last_updated"] = datetime.now().strftime("%Y-%m-%d")
    with open(PORTFOLIO_FILE, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"✓ Saved {PORTFOLIO_FILE}")


def get_or_create_tab(sheet, tab_name, headers):
    """Get worksheet by name, create with headers if missing."""
    try:
        ws = sheet.worksheet(tab_name)
    except Exception:
        ws = sheet.add_worksheet(title=tab_name, rows=200, cols=len(headers))
        ws.append_row(headers)
        print(f"  Created tab: {tab_name}")
    return ws


# ── READ: Sheet → portfolio_state.json ────────────────────────────────────────

def read_from_sheet(sheet, portfolio):
    print("\n── Reading from Google Sheet ──")
    holdings_map = {h["ticker"]: h for h in portfolio["holdings"]}
    updated = []

    # Read Holdings tab
    try:
        ws = sheet.worksheet(TAB_HOLDINGS)
        rows = ws.get_all_records()
        print(f"  Holdings tab: {len(rows)} rows")
        for row in rows:
            ticker = str(row.get("Ticker", "")).strip().upper()
            if not ticker:
                continue
            weight = _safe_float(row.get("Allocation", row.get("Weight", 0)))
            cost_basis = _safe_float(row.get("Cost Basis", None))
            if ticker in holdings_map:
                holdings_map[ticker]["weight"] = weight
                if cost_basis is not None:
                    holdings_map[ticker]["cost_basis"] = cost_basis
                updated.append(ticker)
            else:
                # New ticker not yet in portfolio_state — add skeleton
                from_raw = {
                    "ticker": ticker,
                    "name": str(row.get("Name", ticker)),
                    "weight": weight,
                    "cost_basis": cost_basis,
                    "type": str(row.get("Type", "equity")).lower(),
                    "current_price": None,
                    "last_review_date": None,
                    "thesis_status": "unset",
                    "action": "hold",
                    "garp_scores": {k: 0 for k in ["growth","profitability","balance_sheet","moat","management","secular_trend","valuation","technical"]},
                    "scenarios": {
                        "bear": {"revenue_2030": None, "net_margin": None, "cagr": None},
                        "base": {"revenue_2030": None, "net_margin": None, "cagr": None},
                        "bull": {"revenue_2030": None, "net_margin": None, "cagr": None},
                    },
                    "latest_earnings": {"quarter": None, "revenue_actual": None, "revenue_est": None, "eps_actual": None, "eps_est": None},
                    "thesis_summary": "",
                    "key_risks": [],
                    "red_flags": [],
                    "notes": "",
                }
                portfolio["holdings"].append(from_raw)
                holdings_map[ticker] = from_raw
                updated.append(f"{ticker} (NEW)")
        print(f"  Updated weights: {', '.join(updated)}")
    except Exception as e:
        print(f"  WARNING: Could not read Holdings tab: {e}")

    # Read Thesis tab (optional — if you maintain thesis notes in Sheet)
    try:
        ws = sheet.worksheet(TAB_THESIS)
        rows = ws.get_all_records()
        print(f"  Thesis tab: {len(rows)} rows")
        for row in rows:
            ticker = str(row.get("Ticker", "")).strip().upper()
            if ticker not in holdings_map:
                continue
            h = holdings_map[ticker]
            if row.get("Thesis Summary"):
                h["thesis_summary"] = str(row["Thesis Summary"])
            if row.get("Key Risks"):
                risks = [r.strip() for r in str(row["Key Risks"]).split("|") if r.strip()]
                if risks:
                    h["key_risks"] = risks
    except Exception:
        pass  # Thesis tab is optional

    return portfolio


# ── WRITE: portfolio_state.json → Sheet ───────────────────────────────────────

def write_to_sheet(sheet, portfolio):
    print("\n── Writing to Google Sheet ──")

    # ── Research Output tab ──
    headers = [
        "Ticker", "Name", "Weight %", "Thesis Status", "Action",
        "GARP Total", "Growth", "Profitability", "Balance Sheet",
        "Moat", "Management", "Secular Trend", "Valuation", "Technical",
        "Bear CAGR", "Base CAGR", "Bull CAGR",
        "Bear Rev 2030", "Base Rev 2030", "Bull Rev 2030",
        "Bear Margin", "Base Margin", "Bull Margin",
        "Last Earnings", "Rev Beat/Miss", "EPS Beat/Miss",
        "Red Flags", "Last Reviewed",
    ]
    ws = get_or_create_tab(sheet, TAB_RESEARCH_OUTPUT, headers)

    garp_keys = ["growth","profitability","balance_sheet","moat","management","secular_trend","valuation","technical"]

    rows = []
    for h in portfolio["holdings"]:
        g = h.get("garp_scores", {})
        sc = h.get("scenarios", {})
        e = h.get("latest_earnings", {})
        gt = sum(g.get(k, 0) for k in garp_keys)

        rev_delta = ""
        eps_delta = ""
        if e.get("revenue_actual") and e.get("revenue_est"):
            pct = (e["revenue_actual"] - e["revenue_est"]) / e["revenue_est"] * 100
            rev_delta = f"{'+' if pct >= 0 else ''}{pct:.1f}%"
        if e.get("eps_actual") and e.get("eps_est"):
            pct = (e["eps_actual"] - e["eps_est"]) / e["eps_est"] * 100
            eps_delta = f"{'+' if pct >= 0 else ''}{pct:.1f}%"

        flags = " | ".join(h.get("red_flags", []))

        rows.append([
            h.get("ticker", ""),
            h.get("name", ""),
            h.get("weight", 0),
            h.get("thesis_status", ""),
            h.get("action", ""),
            gt,
            g.get("growth", 0), g.get("profitability", 0), g.get("balance_sheet", 0),
            g.get("moat", 0), g.get("management", 0), g.get("secular_trend", 0),
            g.get("valuation", 0), g.get("technical", 0),
            sc.get("bear", {}).get("cagr", ""),
            sc.get("base", {}).get("cagr", ""),
            sc.get("bull", {}).get("cagr", ""),
            sc.get("bear", {}).get("revenue_2030", ""),
            sc.get("base", {}).get("revenue_2030", ""),
            sc.get("bull", {}).get("revenue_2030", ""),
            sc.get("bear", {}).get("net_margin", ""),
            sc.get("base", {}).get("net_margin", ""),
            sc.get("bull", {}).get("net_margin", ""),
            e.get("quarter", ""),
            rev_delta,
            eps_delta,
            flags,
            h.get("last_review_date", ""),
        ])

    # Clear existing data (keep header) and rewrite
    ws.resize(rows=max(len(rows) + 2, 50))
    if len(rows) > 0:
        # Clear from row 2 down
        ws.batch_clear([f"A2:AB{len(rows) + 5}"])
        ws.update(f"A2", rows)
    print(f"  Research Output: {len(rows)} rows written")

    return len(rows)


# ── DECISION LOG ──────────────────────────────────────────────────────────────

def append_decision_log(sheet, ticker, action, rationale=""):
    """Call this when an action changes — appends a row to Decision Log."""
    headers = ["Date", "Ticker", "Action", "Rationale", "Timestamp"]
    ws = get_or_create_tab(sheet, TAB_DECISION_LOG, headers)
    ws.append_row([
        datetime.now().strftime("%Y-%m-%d"),
        ticker,
        action,
        rationale,
        datetime.now().isoformat(),
    ])
    print(f"  Decision Log: appended {ticker} → {action}")


# ── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Sync portfolio_state.json ↔ Google Sheets")
    parser.add_argument("--direction", choices=["read","write","both"], default="both")
    parser.add_argument("--log", nargs=3, metavar=("TICKER","ACTION","RATIONALE"),
                        help="Append a decision log entry")
    args = parser.parse_args()

    if SHEET_ID == "YOUR_GOOGLE_SHEET_ID_HERE":
        print("ERROR: Set your SHEET_ID in scripts/sync_sheet.py first.")
        print("Find it in your Google Sheet URL:")
        print("  docs.google.com/spreadsheets/d/[SHEET_ID_HERE]/edit")
        raise SystemExit(1)

    print(f"Connecting to Google Sheets…")
    client = get_client()
    sheet = client.open_by_key(SHEET_ID)
    print(f"✓ Connected: '{sheet.title}'")

    portfolio = load_portfolio()

    if args.direction in ("read", "both"):
        portfolio = read_from_sheet(sheet, portfolio)
        save_portfolio(portfolio)

    if args.direction in ("write", "both"):
        write_to_sheet(sheet, portfolio)

    if args.log:
        append_decision_log(sheet, args.log[0], args.log[1], args.log[2])

    print(f"\n✓ Sync complete ({args.direction}) — {datetime.now().strftime('%H:%M:%S')}")


def _safe_float(val):
    if val is None or val == "":
        return None
    try:
        return float(str(val).replace("%", "").replace(",", "").strip())
    except (ValueError, TypeError):
        return None


if __name__ == "__main__":
    main()
