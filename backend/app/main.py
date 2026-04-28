"""
FastAPI application entry point.

In .NET terms, this file plays a similar role to:
- `Program.cs` (where you create the WebApplication)
- plus parts of `Startup.cs` (where you configure routes / middleware)

We:
- Create the FastAPI app instance.
- Include the SnapTrade "router" (similar to a controller).
- Expose the `app` object that `uvicorn` will run.
"""

from fastapi import FastAPI

from app.routers.snaptrade import router as snaptrade_router


# Create the FastAPI application instance.
# This is like `var app = WebApplication.CreateBuilder(args).Build();`
app = FastAPI(
    title="Portfolio Tracker Backend",
    description="FastAPI backend using SnapTrade SDK for a personal portfolio tracker.",
    version="0.1.0",
)


# Register routers (similar to app.MapControllers() in ASP.NET)
# We mount all SnapTrade-related endpoints under the `/snaptrade` prefix.
app.include_router(snaptrade_router, prefix="/snaptrade", tags=["SnapTrade"])


@app.get("/", tags=["Health"])
def read_root():
    """
    Very simple health/check endpoint.

    In ASP.NET you might expose something like `/health` or `/`.
    This is useful to confirm the API is running.
    """

    return {"message": "Portfolio Tracker API is running. See /docs for Swagger UI."}


# Note:
# We do NOT call uvicorn.run(...) here.
# Instead, you run the server from the command line, e.g.:
#   uvicorn app.main:app --reload --port 8000
# (similar to `dotnet run` starting Kestrel for ASP.NET).

