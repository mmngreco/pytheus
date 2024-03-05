import requests
from datetime import datetime
import urllib.parse
import typer
from rich import print as rprint
from pathlib import Path
import json
import os
import pandas as pd

app = typer.Typer()

COOKIE_FILE = "~/.pytheus/cookie"
API_URL = os.environ.get("PYTHEUS_API_URL")

def read_cookie(cookie_file: Path) -> str:
    p = Path(cookie_file).expanduser().resolve()
    if p.exists():
        return p.read_text().strip()
    rprint(f"[bold red]Cookie file not found at: {p}[/bold red]")
    rprint("[bold red]Please create the file and add the cookie value to it.[/bold red]")
    raise typer.Abort()


@app.command()
def query_prometheus(
    start: str = typer.Option(..., help="Start date in YYYY-MM-DD (hh:mm:ss) format UTC"),
    end: str = typer.Option(..., help="End date in YYYY-MM-DD  (hh:mm:ss)format UTC"),
    step: str = typer.Option('3600', help="Step size in seconds"),
    query: str = typer.Option(..., help="Prometheus query"),
    route: str = typer.Option('query_range', help="Route to query, either 'query' or 'query_range'"),
    cookie: Path = typer.Option(COOKIE_FILE, help="File which contains the Cookie value for the header"),
    output: Path = typer.Option(None, help="Output file to save the results. Prints to stdout if not provided."),
    silent: bool = typer.Option(False, help="Suppress output")
):
    """
    Query Prometheus between a start and end date with the given query and step
    size, and save the result to an output file if provided.
    """

    # Convert start_str and end_str to timestamps
    start_int = pd.Timestamp(start).timestamp()
    end_int = pd.Timestamp(end).timestamp()
    step = step

    # Encode query for URL
    encoded_query= urllib.parse.quote(query)

    # Read cookie from the specified file
    cookie_value = read_cookie(cookie)

    # Set header for request
    headers = {
        'cookie': cookie_value
    }

    # Construct the query URL
    if route == "query":
        url = f"{API_URL}/{route}?query={encoded_query}"
    elif route == "query_range":
        url = f"{API_URL}/{route}?query={encoded_query}&start={start_int}&end={end_int}&step={step}"
    else:
        if not silent:
            rprint(f"[bold red]Invalid route: {route}[/bold red]")
        raise typer.Abort()

    # Perform the request
    response = requests.get(url, headers=headers)

    # Check response code for success/failure and handle output
    if response.ok:
        result = response.json()

        # Output to file if specified, else print it
        if output:
            with open(output, 'w') as file:
                json.dump(result, file, indent=4)
            if not silent:
                rprint(f"[bold green]Query successful! Results saved to: {output}[/bold green]")
        else:
            if not silent:
                rprint("[bold green]Query successful![/bold green]")
            rprint(result)
    else:
        rprint(f"[bold red]Query failed with status code: {response.status_code}[/bold red]")

if __name__ == "__main__":
    app()
