# 03.05.2025

import sys

# External library
from rich.console import Console
from rich.prompt import Prompt


# Internal utilities
from StreamingCommunity.Api.Template.search_utils import unified_search

from StreamingCommunity.Api.Template import get_select_title
from StreamingCommunity.Lib.Proxies.proxy import ProxyFinder
from StreamingCommunity.Api.Template.config_loader import site_constant
from StreamingCommunity.Api.Template.Class.SearchType import MediaItem


# Logic class
from .site import title_search, table_show_manager, media_search_manager
from .film import download_film
from .series import download_series


# Variable
indice = 8
_useFor = "film_serie"
_priority = 10          # !!! MOLTO LENTO
_engineDownload = "hls"

msg = Prompt()
console = Console()


def get_user_input(string_to_search: str = None):
    """
    Asks the user to input a search term.
    Handles both Telegram bot input and direct input.
    """
    string_to_search = msg.ask(f"\n[purple]Insert a word to search in [green]{site_constant.SITE_NAME}").strip()
    return string_to_search

def process_search_result(select_title, selections=None, proxy=None):
    """
    Handles the search result and initiates the download for either a film or series.
    
    Parameters:
        select_title (MediaItem): The selected media item
        selections (dict, optional): Dictionary containing selection inputs that bypass manual input
                                    {'season': season_selection, 'episode': episode_selection}
    """
    if select_title.type == 'tv':
        season_selection = None
        episode_selection = None
        
        if selections:
            season_selection = selections.get('season')
            episode_selection = selections.get('episode')

        download_series(select_title, season_selection, episode_selection, proxy)

    else:
        download_film(select_title, proxy)

def search(
    string_to_search: str = None,
    get_onlyDatabase: bool = False,
    direct_item: dict | None = None, # Assuming dict is standard now
    selections: dict | None = None
):
    """Search wrapper for streamingwatch, handles proxy finding."""
    provider_module = sys.modules[__name__]

    # --- Provider-Specific Setup (Proxy Finding) ---
    proxy = None
    search_args = []
    process_kwargs = {}
    try:
        # Note: Finding proxy might need adjustment based on actual ProxyFinder usage
        # This is just illustrative. You might want error handling here.
        finder = ProxyFinder(url=f"{site_constant.FULL_URL}/serie/euphoria/") # Example URL
        proxy, response_serie, _ = finder.find_fast_proxy()
        if proxy:
            search_args = [[proxy, response_serie]] # Pass proxy info to title_search
            process_kwargs = {'proxy': proxy} # Pass proxy to process_search_result
        else:
            console.print("[red]Could not find a working proxy for streamingwatch.")
            # Decide how to proceed: return, raise error, try without proxy?
            # For now, let unified_search proceed without proxy args, it might fail later.
            pass
    except Exception as e:
         console.print(f"[red]Error finding proxy: {e}")
         # Proceed without proxy?

    # Call unified search
    unified_search(
        provider_module=provider_module,
        string_to_search=string_to_search,
        get_onlyDatabase=get_onlyDatabase,
        direct_item=direct_item,
        selections=selections,
        # Provider specific flags/details:
        use_telegram=False, # This provider didn't use Telegram
        use_quote_plus=False, # This provider didn't use quote_plus
        provider_name=site_constant.SITE_NAME, # Adjust if needed
        search_func_args=search_args, # Pass proxy info list
        process_func_kwargs=process_kwargs # Pass proxy dict
    )