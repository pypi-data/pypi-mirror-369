#!/usr/bin/env python3
import sys
import re
import requests
import os
import urllib3
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, MofNCompleteColumn, TimeRemainingColumn
from rich.table import Table
from rich.panel import Panel

# Disable SSL warnings (since verify=False is used)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
console = Console()

HEADERS_TO_CHECK = [
    "Content-Security-Policy",
    "X-Content-Type-Options",
    "X-Frame-Options",
    "X-XSS-Protection",
    "Strict-Transport-Security",
    "Referrer-Policy",
    "Feature-Policy",
    "Permissions-Policy",
    "Expect-CT",
    "Cache-Control",
    "Pragma"
]

def generate_clickjacking_payload(url):
    payload_file = "clickjack_testing.html"
    html = f"""<!DOCTYPE html>
<html>
<head>
<title>Clickjacking Test</title>
</head>
<body>
<h1>Clickjacking Test for {url}</h1>
<iframe src="{url}" width="100%" height="500px" style="opacity:0.6;"></iframe>
</body>
</html>"""
    try:
        with open(payload_file, "w") as f:
            f.write(html)
        console.print(Panel.fit(
            f"[yellow]Clickjacking payload automatically created\nbecause {url} vulnerable:[/yellow] {payload_file}\n\nOpen it in a browser to test.",
            title="Payload Generated",
            border_style="yellow"
        ))
    except IOError as e:
        console.print(Panel.fit(f"[red]Error writing payload file: {e}[/red]", title="File Write Error"))

def check_security_headers(url):
    table = Table(title="", style="cyan")
    table.add_column("Header", style="bold white")
    table.add_column("Status", style="bold", justify="center")
    table.add_column("Value / Notes", style="dim")

    try:
        response = requests.head(url, allow_redirects=True, timeout=10, verify=False)
        all_headers = {k.lower(): v for k, v in response.headers.items()}
    except requests.exceptions.RequestException as e:
        console.print(Panel.fit(f"[red]Error accessing {url}: {e}[/red]", title="Network Error"))
        return

    with Progress(
        SpinnerColumn(spinner_name="dots"),
        TextColumn("[bold blue]{task.description}"),
        BarColumn(bar_width=30),
        TextColumn("{task.percentage:>3.0f}%"),
        MofNCompleteColumn(),
        TimeRemainingColumn(),
        console=console,
        transient=True
    ) as progress:
        task_id = progress.add_task("Checking headers...", total=len(HEADERS_TO_CHECK))

        clickjacking_vulnerable = False
        for header in HEADERS_TO_CHECK:
            value = all_headers.get(header.lower())
            if value:
                table.add_row(header, "[green]Present[/green]", f"[yellow]{value}[/yellow]")
            else:
                table.add_row(header, "[red]Missing[/red]", "")
            
            if header.lower() == "x-frame-options" and not value:
                clickjacking_vulnerable = True

            progress.update(task_id, advance=1)

    console.print(table)
    
    if clickjacking_vulnerable:
        console.print(f"")
        generate_clickjacking_payload(url)
    
    console.print(Panel.fit("Security headers check completed.", border_style="green"))

# --- CLI Entry Point ---
def main():
    """Main function to parse arguments and run the security header check."""
    if len(sys.argv) < 2:
        console.print(Panel.fit(f"Usage: python3 -m iris <url>", border_style="red"))
        sys.exit(1)

    input_url = sys.argv[1]
    url = input_url if re.match(r"^https?://", input_url, re.IGNORECASE) else "http://" + input_url

    if not re.match(r"^https?://", url, re.IGNORECASE):
        console.print(Panel.fit("Invalid URL format.", border_style="red"))
        sys.exit(1)

    os.system('cls' if os.name == 'nt' else 'clear')
    console.print(Panel.fit("🔍 Security Headers Checker", border_style="blue", title="Iris"))
    check_security_headers(url)

if __name__ == "__main__":
    main()