## Backend + Streamlit - Portfolio Tracker

This folder contains:
- **FastAPI backend** (`app/`) exposed on port **8000**
- **Streamlit UI** (`streamlit_app.py`) exposed on port **8501**

### Quick start (local development)

1. **Create your `.env` file**
   - Copy `.env.example` to `.env`
   - Fill in:
     - `SNAPTRADE_CLIENT_ID=...`
     - `SNAPTRADE_CONSUMER_KEY=...`

2. **Install Python dependencies** (inside the `backend` folder):

```bash
pip install -r requirements.txt
```

3. **Run the FastAPI backend (port 8000)**:

```bash
uvicorn app.main:app --reload --port 8000
```

   - Open `http://localhost:8000/docs` for the interactive Swagger UI.

4. **Run the Streamlit dashboard (port 8501)** in another terminal:

```bash
streamlit run streamlit_app.py --server.port 8501
```

   - Open `http://localhost:8501` to use the UI.

### Project layout (conceptual map to .NET)

- `app/main.py`
  - Similar to `Program.cs` / `Startup.cs`.
  - Creates the FastAPI application and wires up routers.

- `app/core/config.py`
  - Similar to strongly-typed options bound from `appsettings.json`.
  - Uses Pydantic Settings to load environment variables (`SNAPTRADE_*`).

- `app/external/snaptrade_client.py`
  - Similar to an `ISnapTradeClient` service in ASP.NET.
  - Wraps the official SnapTrade SDK and exposes higher-level methods:
    - register user
    - create login link
    - get holdings

- `app/routers/snaptrade.py`
  - Similar to an ASP.NET Web API controller:
    - `/snaptrade/users/register`
    - `/snaptrade/users/login-link`
    - `/snaptrade/holdings`

- `streamlit_app.py`
  - Lightweight Python-only UI (no JavaScript).
  - Talks to the FastAPI backend using HTTP (like a Blazor or SPA client would).

