#!/usr/bin/env python3
"""
ssec-seo CLI - Main entry point
"""
import click
import asyncio
import webbrowser
import os
import sys
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from ssec_seo.core.ultimate_engine import UltimateSEOEngine
    from ssec_seo.core.config import ScanConfig
    HAS_ENGINE = True
except ImportError as e:
    HAS_ENGINE = False
    print(f"Warning: {e}")

console = Console()

@click.group()
def cli():
    """🔍 ssec-seo - SEO Intelligence Platform by ssecgroup"""
    pass

@cli.command()
@click.argument('url')
@click.option('--max-pages', default=100, help='Maximum pages to scan')
@click.option('--concurrent', default=10, help='Concurrent requests')
@click.option('--output', '-o', help='Output file')
def scan(url, max_pages, concurrent, output):
    """Scan a website for SEO issues"""
    
    console.print(Panel.fit(
        "[bold cyan]🔍 ssec-seo[/bold cyan] - SEO Intelligence Platform\n"
        "[yellow]by ssecgroup[/yellow]",
        border_style="cyan"
    ))
    
    if not HAS_ENGINE:
        console.print("[red]Error: ssec-seo engine not available[/red]")
        return
    
    # Rest of scan function...
    # (keep same functionality but update any spyglass references)

def main():
    cli()

if __name__ == '__main__':
    main()
