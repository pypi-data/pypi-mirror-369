import json
import os
import typer
import httpx
from typing import Any, List, Optional
from rich.console import Console
from rich.table import Table

from .client import Earth2Client


def _to_int(value: Any) -> int:
    try:
        if value is None or value == "":
            return 0
        if isinstance(value, bool):
            return int(value)
        if isinstance(value, (int, float)):
            return int(value)
        if isinstance(value, str):
            return int(value)
        return 0
    except Exception:
        return 0


def _to_float(value: Any) -> float:
    try:
        if value is None or value == "":
            return 0.0
        if isinstance(value, bool):
            return float(value)
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            return float(value)
        return 0.0
    except Exception:
        return 0.0


app = typer.Typer(help="Earth2 API CLI (Python)")
console = Console()


def _client_from_env() -> Earth2Client:
    return Earth2Client(cookie_jar=os.getenv("E2_COOKIE"), csrf_token=os.getenv("E2_CSRF"))


def format_price(price: float) -> str:
    return f"${price:,.2f}"


def format_number(num: int) -> str:
    return f"{num:,}"


def log_success(message: str) -> None:
    console.print(f"✓ {message}", style="green")


def log_error(message: str) -> None:
    console.print(f"✗ {message}", style="red")


def log_info(message: str) -> None:
    console.print(f"ℹ {message}", style="blue")


@app.command()
def login(
    email: Optional[str] = typer.Option(None, "--email", "-e", help="Email address"),
    password: Optional[str] = typer.Option(
        None, "--password", "-p", help="Password", hide_input=True
    )
):
    """Authenticate with Earth2 using Kinde OAuth flow"""
    client = Earth2Client()

    email = email or os.getenv("E2_EMAIL")
    password = password or os.getenv("E2_PASSWORD")

    if not email or not password:
        log_error(
            "Email and password are required. Use --email and --password or set "
            "E2_EMAIL and E2_PASSWORD environment variables."
        )
        raise typer.Exit(1)

    log_info("Starting Earth2 Kinde OAuth authentication flow...")
    log_info("This may take a moment as we navigate through multiple redirects...")

    result = client.authenticate(email, password)

    if result["success"]:
        log_success(result["message"])
        log_info("Session cookies have been stored for this session.")
        log_info('Session is now ready for authenticated operations.')

        # Test the session
        log_info("Testing session validity...")
        session_check = client.check_session_validity()
        if session_check["isValid"]:
            log_success("Session is valid and ready to use!")
        else:
            log_error("Session validation failed. You may need to try again.")
    else:
        log_error(result["message"])
        log_error("OAuth authentication failed. Please check your credentials and try again.")
        raise typer.Exit(1)


@app.command()
def check_session():
    """Check if current session is still valid"""
    client = _client_from_env()

    if not client.cookie_jar:
        log_error('No session found. Please run "e2 login" first.')
        raise typer.Exit(1)

    log_info("Checking session validity...")
    result = client.check_session_validity()

    if result["isValid"]:
        log_success("Session is valid!")
    else:
        log_error("Session is invalid or expired.")
        if result["needsReauth"]:
            log_info('Please run "e2 login" to re-authenticate.')
        raise typer.Exit(1)


@app.command()
def trending(json_output: bool = typer.Option(False, "--json", help="Output raw JSON")):
    """Get trending places"""
    client = _client_from_env()
    res = client.get_trending_places()

    if json_output:
        typer.echo(json.dumps(res, indent=2))
        return

    console.print("\n🌍 [bold blue]Trending Places[/bold blue]\n")

    if not res["data"]:
        log_info("No trending places found")
        return

    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Place")
    table.add_column("Country")
    table.add_column("Tier")
    table.add_column("Tiles Sold")
    table.add_column("Tile Price")
    table.add_column("Days")

    for place in res["data"]:
        attrs = place.get("attributes", {})
        table.add_row(
            attrs.get("placeName") or "N/A",
            attrs.get("country") or "N/A",
            f"T{attrs['landfieldTier']}" if attrs.get("landfieldTier") else "N/A",
            format_number(attrs["tilesSold"]) if attrs.get("tilesSold") else "N/A",
            format_price(attrs["tilePrice"]) if attrs.get("tilePrice") else "N/A",
            format_number(attrs["timeframeDays"]) if attrs.get("timeframeDays") else "N/A"
        )

    console.print(table)


@app.command()
def territory_winners():
    client = _client_from_env()
    res = client.get_territory_release_winners()
    typer.echo(json.dumps(res, indent=2))


@app.command()
def property(id: str):  # noqa: A002
    client = _client_from_env()
    res = client.get_property(id)
    typer.echo(json.dumps(res, indent=2))


@app.command()
def market(
    country: str = typer.Option(None),
    tier: str = typer.Option(None),
    tile_class: str = typer.Option(None),
    tile_count: str = typer.Option(None),
    page: int = typer.Option(1),
    items: int = typer.Option(100),
    search: str = typer.Option(""),
    term: List[str] = typer.Option(None),
    json_output: bool = typer.Option(False, "--json", help="Output raw JSON")
):
    """Search marketplace"""
    client = _client_from_env()
    res = client.search_market(
        country=country,
        landfieldTier=tier,
        tileClass=tile_class,
        tileCount=tile_count,
        page=page,
        items=items,
        search=search,
        searchTerms=term or [],
    )

    if json_output:
        typer.echo(json.dumps(res, indent=2))
        return

    console.print("\n🏪 [bold blue]Marketplace Search Results[/bold blue]\n")
    log_info(f"Found {format_number(res['count'])} total properties")

    landfields = res.get("landfields", [])
    if not landfields:
        log_info("No properties match your search criteria")
        return

    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Description", max_width=30)
    table.add_column("Location", max_width=25)
    table.add_column("Country")
    table.add_column("Tier")
    table.add_column("Tiles")
    table.add_column("Total Price")
    table.add_column("Price/Tile")

    items_limit = int(items)

    for item in landfields[:items_limit]:  # Show requested number of items
        description = (item.get("description") or "N/A")
        if len(description) > 30:
            description = description[:27] + "..."

        location = (item.get("location") or "N/A")
        if len(location) > 25:
            location = location[:22] + "..."

        # Calculate price per tile with safe numeric parsing
        price_value = _to_float(item.get("price"))
        tile_count_value = _to_int(item.get("tileCount"))
        ppt_value = price_value / tile_count_value if tile_count_value > 0 else 0.0

        table.add_row(
            description,
            location,
            item.get("country") or "N/A",
            f"T{item['tier']}" if item.get("tier") else "N/A",
            format_number(item["tileCount"]) if item.get("tileCount") else "N/A",
            format_price(item["price"]) if item.get("price") else "N/A",
            format_price(ppt_value) if ppt_value > 0 else "N/A"
        )

    console.print(table)

    if len(landfields) > items_limit:
        log_info(f"Showing first {items_limit} of {len(landfields)} results. Use --json to see all.")


@app.command()
def leaderboard_players(**params):
    """Get players leaderboard"""
    client = _client_from_env()
    res = client.get_leaderboard_players(**params)
    typer.echo(json.dumps(res, indent=2))


@app.command()
def leaderboard_countries(**params):
    """Get countries leaderboard"""
    client = _client_from_env()
    res = client.get_leaderboard_countries(**params)
    typer.echo(json.dumps(res, indent=2))


@app.command()
def leaderboard_player_countries(**params):
    """Get player countries leaderboard"""
    client = _client_from_env()
    res = client.get_leaderboard_player_countries(**params)
    typer.echo(json.dumps(res, indent=2))


@app.command()
def resources(property_id: str):
    client = _client_from_env()
    try:
        res = client.get_resources(property_id)
        typer.echo(json.dumps(res, indent=2))
    except httpx.HTTPStatusError as e:
        status = e.response.status_code if e.response is not None else None
        if status == 401:
            log_error(
                "401 Unauthorized from resources API. This endpoint typically requires a verified (KYC) Earth2 account "
                "and an authenticated session. Please verify your account and log in, then try again."
            )
        else:
            log_error(f"Resources request failed: HTTP {status}")
    except Exception as e:
        log_error(f"Resources request failed: {str(e)}")


@app.command()
def avatar_sales():
    client = _client_from_env()
    res = client.get_avatar_sales()
    typer.echo(json.dumps(res, indent=2))


@app.command()
def user(user_id: str):
    client = _client_from_env()
    res = client.get_user_info(user_id)
    typer.echo(json.dumps(res, indent=2))


@app.command()
def users(user_ids: List[str] = typer.Argument(..., help="List of user IDs")):
    client = _client_from_env()
    res = client.get_users(user_ids)
    typer.echo(json.dumps(res, indent=2))


@app.command()
def stats():
    """Show rate limiting and usage statistics"""
    client = _client_from_env()
    stats = client.get_rate_limit_stats()

    if stats.get("rate_limiting") == "disabled":
        log_info("Rate limiting is disabled for this client")
        return

    console.print("\n📊 [bold blue]API Usage Statistics[/bold blue]\n")

    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Metric")
    table.add_column("Value")

    table.add_row("Total Requests", format_number(stats.get("total_requests", 0)))
    table.add_row("Blocked Requests", format_number(stats.get("blocked_requests", 0)))
    table.add_row("Current RPM", format_number(stats.get("current_rpm", 0)))
    table.add_row("Cache Size", format_number(stats.get("cache_size", 0)))
    table.add_row("Efficiency", f"{stats.get('efficiency', 0):.1f}%")

    console.print(table)

    error_counts = stats.get("error_counts", {})
    if error_counts:
        console.print("\n⚠️  [bold yellow]Error Counts by Endpoint[/bold yellow]\n")
        error_table = Table(show_header=True, header_style="bold yellow")
        error_table.add_column("Endpoint Category")
        error_table.add_column("Error Count")

        for endpoint, count in error_counts.items():
            if count > 0:
                error_table.add_row(endpoint, format_number(count))

        console.print(error_table)


@app.command()
def clear_cache():
    """Clear the response cache"""
    client = _client_from_env()
    client.clear_cache()
    log_success("Response cache cleared")


@app.command()
def set_cache_ttl(seconds: int = typer.Argument(..., help="Cache TTL in seconds")):
    """Set cache time-to-live in seconds"""
    if seconds < 0:
        log_error("Cache TTL must be non-negative")
        raise typer.Exit(1)

    client = _client_from_env()
    client.set_cache_ttl(seconds)
    log_success(f"Cache TTL set to {seconds} seconds")


if __name__ == "__main__":
    app()
