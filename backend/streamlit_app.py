"""
Streamlit frontend for the personal portfolio tracker.

Why Streamlit?
- Very low boilerplate for data apps (compared to React / Angular).
- Python-only, which is friendly if you come from .NET + Python ML.

This app will:
- Talk to the FastAPI backend (running on port 8000).
- Let you:
  - Register a user with SnapTrade.
  - Get a login link to connect brokerage accounts.
  - Fetch and display holdings with tables and (later) charts.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import pandas as pd
import requests
import streamlit as st


# Base URL for your FastAPI backend.
# If you run uvicorn locally with `--port 8000`, this is correct.
API_BASE_URL = "http://localhost:8000"


def call_api(
    method: str,
    path: str,
    params: Optional[Dict[str, Any]] = None,
) -> Any:
    """
    Small helper to call the FastAPI backend from Streamlit.

    In a React or Blazor app you would use `fetch` / HttpClient.
    Here we use the `requests` library.
    """

    url = f"{API_BASE_URL}{path}"
    try:
        response = requests.request(method, url, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as ex:
        st.error(f"API call failed: {ex}")
        return None


def page_user_registration() -> None:
    """
    Simple UI for registering a user with SnapTrade.
    """

    st.header("1. Register user with SnapTrade")

    user_id = st.text_input(
        "Internal user ID",
        help="This can be any identifier you choose (e.g., 'demo-user-1').",
        value="demo-user-1",
    )

    if st.button("Register user"):
        if not user_id:
            st.warning("Please enter a user ID.")
            return

        data = call_api("POST", "/snaptrade/users/register", params={"user_id": user_id})
        if data is not None:
            st.success("User registered with SnapTrade.")
            st.json(data)


def page_connection_link() -> None:
    """
    UI for generating a SnapTrade login / connection link.
    """

    st.header("2. Generate brokerage connection link")

    user_id = st.text_input(
        "User ID (already registered)",
        value="demo-user-1",
    )
    user_secret = st.text_input(
        "User secret (from register response)",
        type="password",
    )
    redirect_uri = st.text_input(
        "Redirect URI",
        help="Must match the redirect URL configured in your SnapTrade app.",
        value="http://localhost:8501",
    )

    if st.button("Get login link"):
        if not user_id or not user_secret or not redirect_uri:
            st.warning("Please fill in all fields.")
            return

        data = call_api(
            "GET",
            "/snaptrade/users/login-link",
            params={"user_id": user_id, "user_secret": user_secret, "redirect_uri": redirect_uri},
        )
        if data is not None:
            # SnapTrade returns various fields; one of them will be the URL.
            # For now we just show the entire payload.
            st.success("Login link generated.")
            st.json(data)


def page_holdings() -> None:
    """
    UI for fetching and displaying holdings.
    """

    st.header("3. View holdings")

    user_id = st.text_input(
        "User ID (with connected accounts)",
        value="demo-user-1",
    )
    user_secret = st.text_input(
        "User secret",
        type="password",
    )

    if st.button("Fetch holdings"):
        if not user_id or not user_secret:
            st.warning("Please enter user ID and user secret.")
            return

        data: Optional[List[Dict[str, Any]]] = call_api(
            "GET",
            "/snaptrade/holdings",
            params={"user_id": user_id, "user_secret": user_secret},
        )

        if not data:
            st.info("No holdings returned (either error or empty portfolio).")
            return

        # Load into a DataFrame so we can display and later plot.
        df = pd.json_normalize(data)
        st.dataframe(df)

        # Placeholder for future Plotly charts.
        st.caption("Later we will add charts summarizing allocations, P/L, etc.")


def main() -> None:
    """
    Top-level Streamlit app entry point.

    In ASP.NET you might have a layout page with navigation.
    Streamlit gives us a sidebar we can use for simple navigation.
    """

    st.set_page_config(page_title="Portfolio Tracker", layout="wide")

    st.title("Personal Portfolio Tracker (SnapTrade + FastAPI + Streamlit)")

    page = st.sidebar.radio(
        "Navigation",
        options=[
            "Register user",
            "Generate login link",
            "View holdings",
        ],
    )

    if page == "Register user":
        page_user_registration()
    elif page == "Generate login link":
        page_connection_link()
    else:
        page_holdings()


if __name__ == "__main__":
    # This allows running with `streamlit run streamlit_app.py`.
    main()

