"""
External integrations for the backend application.

Think of this as a place for "API clients" in .NET:
- HttpClient wrappers
- SDK abstractions

Here we expose a single SnapTrade client wrapper that hides raw SDK details
behind a simpler Python interface tailored to our app.
"""

"""
External service clients used by the application.

These clients should remain thin wrappers over third-party APIs so that
services can compose them without leaking implementation details.
"""

