# 03.05.2025

import os
import sys
import platform
import logging

# External library
from rich.console import Console

# Internal utilities
from StreamingCommunity.Util.message import start_message
from StreamingCommunity.Util.os import os_summary
from StreamingCommunity.Upload.update import update as git_update
from StreamingCommunity.Lib.TMBD import tmdb
from .config_handler import SHOW_TRENDING # Get config value

console = Console()

def initialize_app():
    """Performs initial setup tasks for the application."""

    # Display start message
    start_message()

    # Log system info
    try:
        os_summary.get_system_summary()
    except Exception as e:
        logging.warning(f"Could not get system summary: {e}")

    # Set terminal size for specific Windows versions if needed
    if platform.system() == "Windows" and platform.release() == "7":
        try:
            os.system('mode 120, 40')
        except Exception as e:
             logging.warning(f"Failed to set console mode: {e}")

    # Check Python version
    if sys.version_info < (3, 8): # Recommended minimum nowadays
        console.print("[bold red]Warning:[/bold red] Python 3.8 or higher is recommended.")
        # Consider exiting if below a critical version like 3.7
        # if sys.version_info < (3, 7):
        #     console.print("[bold red]Fatal Error:[/bold red] Python 3.7+ is required. Please update Python.")
        #     sys.exit(1)

    # Display TMDB trending content if enabled
    if SHOW_TRENDING:
        console.print("\n[bold cyan]Fetching Trending Titles from TMDB...[/bold cyan]")
        try:
            # Add checks or wrappers in tmdb module if display functions can fail
            tmdb.display_trending_films()
            tmdb.display_trending_tv_shows()
        except Exception as e:
            logging.error(f"Failed to display trending content: {e}")
            console.print("[yellow]Could not fetch or display trending titles.[/yellow]")

    # Attempt GitHub update
    console.print("\n[bold cyan]Checking for updates...[/bold cyan]")
    try:
        updated = git_update() # Assuming git_update returns True if updated
        if not updated:
             console.print("[green]Application is up to date.[/green]")
    except Exception as e:
        logging.error(f"Error during GitHub update check: {e}", exc_info=False) # Set exc_info=True for full traceback
        console.print("[yellow]Could not check for updates. Please check manually if needed.[/yellow]")