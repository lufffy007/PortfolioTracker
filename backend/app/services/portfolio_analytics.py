"""
Portfolio analytics built on raw SnapTrade holdings payloads.

We keep this separate from FastAPI routes so you can unit-test math easily.
Comparable to a small "domain service" in .NET.
"""

from __future__ import annotations

from typing import Any, Dict, List, Tuple

import pandas as pd


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def flatten_holdings(holdings_payload: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Turn SnapTrade `get_all_user_holdings` list into flat rows (one per position).
    """

    rows: List[Dict[str, Any]] = []
    for account_block in holdings_payload:
        account = account_block.get("account") or {}
        account_id = account.get("id") or account.get("account_id")
        account_name = (
            account.get("name")
            or account.get("institution_name")
            or (account.get("meta", {}) or {}).get("name")
            or str(account_id or "Account")
        )

        positions = account_block.get("positions") or []
        for pos in positions:
            symbol_wrapper = pos.get("symbol") or {}
            universal = symbol_wrapper.get("symbol") or {}
            ticker = universal.get("symbol") or symbol_wrapper.get("description") or "—"
            company = universal.get("description") or ticker
            quantity = _safe_float(pos.get("units"))
            price = _safe_float(pos.get("price"))
            market_value = quantity * price

            rows.append(
                {
                    "account_id": account_id,
                    "account_name": account_name,
                    "symbol": ticker,
                    "company_name": company,
                    "quantity": quantity,
                    "price": price,
                    "market_value": market_value,
                }
            )

    return rows


def holdings_summary_dataframe(rows: List[Dict[str, Any]]) -> Tuple[pd.DataFrame, float]:
    """
    Build display DataFrame with Market Value and % of Portfolio.
    Returns (df, total_value).
    """

    if not rows:
        empty = pd.DataFrame(
            columns=[
                "Symbol",
                "Company Name",
                "Account",
                "Quantity",
                "Price",
                "Market Value",
                "% of Portfolio",
            ]
        )
        return empty, 0.0

    df = pd.DataFrame(rows)
    total = float(df["market_value"].sum())
    df["pct"] = df["market_value"].apply(lambda v: (v / total * 100.0) if total > 0 else 0.0)

    out = df.rename(
        columns={
            "symbol": "Symbol",
            "company_name": "Company Name",
            "account_name": "Account",
            "quantity": "Quantity",
            "price": "Price",
            "market_value": "Market Value",
            "pct": "% of Portfolio",
        }
    )
    display_cols = [
        "Symbol",
        "Company Name",
        "Account",
        "Quantity",
        "Price",
        "Market Value",
        "% of Portfolio",
    ]
    return out[display_cols], total


def allocation_by_symbol(rows: List[Dict[str, Any]]) -> pd.DataFrame:
    """Aggregate market value by ticker for pie charts."""

    if not rows:
        return pd.DataFrame(columns=["symbol", "market_value", "pct"])

    df = pd.DataFrame(rows)
    grouped = df.groupby("symbol", as_index=False)["market_value"].sum()
    total = float(grouped["market_value"].sum())
    grouped["pct"] = grouped["market_value"].apply(
        lambda v: (v / total * 100.0) if total > 0 else 0.0
    )
    grouped = grouped.sort_values("market_value", ascending=False)
    return grouped


def total_market_value(rows: List[Dict[str, Any]]) -> float:
    if not rows:
        return 0.0
    return float(pd.DataFrame(rows)["market_value"].sum())


def activity_to_row(activity: Dict[str, Any]) -> Dict[str, Any]:
    """
    Flatten a UniversalActivity-style dict for tabular display.
    """

    account = activity.get("account") or {}
    sym = activity.get("symbol")
    ticker = ""
    if isinstance(sym, dict):
        inner = sym.get("symbol")
        if isinstance(inner, dict):
            ticker = inner.get("symbol") or inner.get("raw_symbol") or ""
        else:
            ticker = str(sym.get("raw_symbol") or "")

    return {
        "id": activity.get("id"),
        "trade_date": str(activity.get("trade_date") or ""),
        "settlement_date": str(activity.get("settlement_date") or ""),
        "type": activity.get("type"),
        "description": activity.get("description"),
        "symbol": ticker or "—",
        "units": activity.get("units"),
        "price": activity.get("price"),
        "amount": activity.get("amount"),
        "account": account.get("name") or account.get("id") or "—",
    }
