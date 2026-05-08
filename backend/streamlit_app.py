"""
Streamlit dashboard for the personal portfolio tracker.

Calls the FastAPI backend (default http://localhost:8000). Keep the API running
in a separate terminal while you use this app.

Beginner tip:
- `st.cache_data` avoids refetching on every widget interaction; use "Refresh
  Portfolio" to clear cached data and pull fresh numbers from SnapTrade.
"""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
import plotly.express as px
import requests
import streamlit as st

DEFAULT_API_BASE_URL = "http://localhost:8000"


def request_json(
    base_url: str,
    method: str,
    path: str,
    params: Optional[Dict[str, Any]] = None,
    timeout: int = 60,
) -> Tuple[Optional[Any], Optional[str]]:
    """
    Call FastAPI and return (json_or_none, error_message_or_none).

    Similar to checking `response.IsSuccessStatusCode` in HttpClient.
    """

    url = f"{base_url.rstrip('/')}{path}"
    try:
        response = requests.request(method, url, params=params, timeout=timeout)
        if response.status_code >= 400:
            try:
                payload = response.json()
                detail = payload.get("detail", response.text)
                if isinstance(detail, list):
                    detail = "; ".join(str(x) for x in detail)
            except Exception:
                detail = response.text or f"HTTP {response.status_code}"
            return None, str(detail)
        return response.json(), None
    except requests.RequestException as ex:
        return None, f"Network error: {ex}"


@st.cache_data(ttl=120, show_spinner=False)
def cached_portfolio_summary(
    base_url: str,
    user_id: str,
    user_secret: str,
    refresh_token: int,
) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """Cached wrapper; `refresh_token` bumps when user clicks Refresh."""

    return request_json(
        base_url,
        "GET",
        "/snaptrade/portfolio/summary",
        params={"user_id": user_id, "user_secret": user_secret},
    )


@st.cache_data(ttl=120, show_spinner=False)
def cached_transactions(
    base_url: str,
    user_id: str,
    user_secret: str,
    start_s: Optional[str],
    end_s: Optional[str],
    refresh_token: int,
) -> Tuple[Optional[List[Dict[str, Any]]], Optional[str]]:
    params: Dict[str, Any] = {"user_id": user_id, "user_secret": user_secret}
    if start_s:
        params["start_date"] = start_s
    if end_s:
        params["end_date"] = end_s
    return request_json("GET", "/snaptrade/transactions", params=params, timeout=120)


def render_setup_expander(api_base: str) -> None:
    """Register user + connection portal link (same as before, grouped)."""

    with st.expander("Setup: register user & connect brokerage", expanded=False):
        st.markdown("Use these once per SnapTrade user, then use the portfolio tabs below.")

        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Register")
            reg_uid = st.text_input("User ID", key="reg_uid", value="demo-user-1")
            if st.button("Register with SnapTrade", key="btn_reg"):
                with st.spinner("Calling API…"):
                    data, err = request_json(
                        api_base,
                        "POST",
                        "/snaptrade/users/register",
                        params={"user_id": reg_uid},
                    )
                if err:
                    st.error(err)
                else:
                    st.success("Registered. Save `userSecret` from the response.")
                    st.json(data)

        with c2:
            st.subheader("Connection link")
            link_uid = st.text_input("User ID", key="link_uid", value="demo-user-1")
            link_secret = st.text_input("User secret", type="password", key="link_secret")
            redirect = st.text_input("Redirect URI", value="http://localhost:8501", key="link_redir")
            if st.button("Get login link", key="btn_link"):
                if not link_uid or not link_secret:
                    st.warning("Enter user id and secret.")
                else:
                    with st.spinner("Calling API…"):
                        data, err = request_json(
                            api_base,
                            "GET",
                            "/snaptrade/users/login-link",
                            params={
                                "user_id": link_uid,
                                "user_secret": link_secret,
                                "redirect_uri": redirect,
                            },
                        )
                    if err:
                        st.error(err)
                    else:
                        st.success("Open the redirect URL from the response in your browser.")
                        st.json(data)


def allocation_pie_chart(allocation: List[Dict[str, Any]]) -> None:
    """Plotly pie for asset allocation by symbol."""

    if not allocation:
        st.info("No positions to chart.")
        return

    df = pd.DataFrame(allocation).sort_values("market_value", ascending=False)
    if len(df) > 14:
        top = df.head(13)
        tail = df.iloc[13:]
        other_val = float(tail["market_value"].sum())
        top = pd.concat(
            [top, pd.DataFrame([{"symbol": "Other", "market_value": other_val, "pct": 0.0}])],
            ignore_index=True,
        )
        df_use = top
    else:
        df_use = df

    fig = px.pie(
        df_use,
        names="symbol",
        values="market_value",
        title="Asset allocation (by market value)",
        hole=0.35,
    )
    fig.update_traces(textposition="inside", textinfo="percent+label")
    fig.update_layout(margin=dict(t=40, b=20, l=20, r=20))
    st.plotly_chart(fig, use_container_width=True)


def main() -> None:
    st.set_page_config(
        page_title="Portfolio Tracker",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.title("Portfolio Tracker")
    st.caption("SnapTrade · FastAPI backend · Streamlit UI")

    if "refresh_token" not in st.session_state:
        st.session_state.refresh_token = 0

    with st.sidebar:
        st.header("Connection")
        api_base = st.text_input(
            "API base URL",
            value=DEFAULT_API_BASE_URL,
            help="Where uvicorn is running.",
        )
        user_id = st.text_input("SnapTrade user id", value="demo-user-1")
        user_secret = st.text_input("SnapTrade user secret", type="password")

        st.divider()
        if st.button("Refresh portfolio", type="primary", use_container_width=True):
            st.session_state.refresh_token += 1
            cached_portfolio_summary.clear()
            cached_transactions.clear()
            st.success("Cache cleared. Data will reload.")

        st.caption("Tip: after linking a brokerage in SnapTrade, click Refresh.")

    api_base = api_base.rstrip("/")

    render_setup_expander(api_base)

    if not user_id or not user_secret:
        st.warning("Enter **user id** and **user secret** in the sidebar to load your portfolio.")
        st.stop()

    with st.spinner("Loading portfolio summary from API…"):
        summary, err = cached_portfolio_summary(
            api_base,
            user_id,
            user_secret,
            st.session_state.refresh_token,
        )

    if err:
        st.error(f"Could not load portfolio: {err}")
        st.info("Check that FastAPI is running (`uvicorn app.main:app --reload --port 8000`) and credentials are correct.")
        st.stop()

    assert summary is not None
    total_val = float(summary.get("total_portfolio_value") or 0)
    n_accounts = int(summary.get("num_accounts") or 0)
    n_holdings = int(summary.get("num_holdings") or 0)
    holdings_table = summary.get("holdings_table") or []
    allocation = summary.get("allocation") or []
    accounts_raw = summary.get("accounts_raw") or []

    # --- Portfolio overview (above tabs) ---
    st.subheader("Portfolio overview")
    m1, m2, m3 = st.columns(3)
    m1.metric("Total portfolio value (est.)", f"${total_val:,.2f}")
    m2.metric("Accounts", n_accounts)
    m3.metric("Positions", n_holdings)
    if summary.get("note"):
        st.caption(str(summary["note"]))

    tab_overview, tab_holdings, tab_accounts, tab_tx = st.tabs(
        ["Overview", "Holdings", "Accounts", "Transactions"]
    )

    with tab_overview:
        col_chart, col_empty = st.columns([2, 1])
        with col_chart:
            allocation_pie_chart(allocation)
        with col_empty:
            st.markdown("**Quick tips**")
            st.markdown(
                "- Total value sums **units × price** per SnapTrade position.\n"
                "- Use **Refresh portfolio** after connecting a new account.\n"
                "- Transactions tab can be slow for long histories; narrow the date range."
            )

    with tab_holdings:
        if not holdings_table:
            st.info("No positions returned. Connect a brokerage or refresh after sync.")
        else:
            hdf = pd.DataFrame(holdings_table)
            fmt = {
                "Quantity": "{:.4f}",
                "Price": "${:,.2f}",
                "Market Value": "${:,.2f}",
                "% of Portfolio": "{:.2f}%",
            }
            st.dataframe(
                hdf.style.format(fmt, na_rep="—"),
                use_container_width=True,
                hide_index=True,
            )

    with tab_accounts:
        if not accounts_raw:
            st.info("No accounts returned yet.")
        else:
            adf = pd.json_normalize(accounts_raw)
            st.dataframe(adf, use_container_width=True, hide_index=True)

    with tab_tx:
        c1, c2 = st.columns(2)
        default_end = date.today()
        default_start = default_end - timedelta(days=90)
        start_d = c1.date_input("Start date", value=default_start)
        end_d = c2.date_input("End date", value=default_end)
        if start_d > end_d:
            st.error("Start date must be on or before end date.")
        else:
            with st.spinner("Loading transactions…"):
                txs, tx_err = cached_transactions(
                    api_base,
                    user_id,
                    user_secret,
                    start_d.isoformat(),
                    end_d.isoformat(),
                    st.session_state.refresh_token,
                )
            if tx_err:
                st.error(tx_err)
            elif not txs:
                st.info("No transactions in this range (or brokerage has not synced yet).")
            else:
                tdf = pd.DataFrame(txs)
                show = [c for c in [
                    "trade_date",
                    "type",
                    "symbol",
                    "description",
                    "units",
                    "price",
                    "amount",
                    "account",
                ] if c in tdf.columns]
                st.dataframe(tdf[show], use_container_width=True, hide_index=True)


if __name__ == "__main__":
    main()
