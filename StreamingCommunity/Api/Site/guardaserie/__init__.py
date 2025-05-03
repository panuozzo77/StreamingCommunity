# 09.06.24
import sys
from urllib.parse import quote_plus


# External library
from rich.console import Console
from rich.prompt import Prompt


# Internal utilities
from StreamingCommunity.Api.Template.search_utils import unified_search

from StreamingCommunity.Api.Template import get_select_title
from StreamingCommunity.Api.Template.config_loader import site_constant
from StreamingCommunity.Api.Template.Class.SearchType import MediaItem


# Logic class
from .site import title_search, media_search_manager, table_show_manager
from .series import download_series

# Variable
indice = 5
_useFor = "serie"
_priority = 0
_engineDownload = "hls"

msg = Prompt()
console = Console()


def process_search_result(select_title, selections=None):
    """
    Handles the search result and initiates the download for either a film or series.
    
    Parameters:
        select_title (MediaItem): The selected media item
        selections (dict, optional): Dictionary containing selection inputs that bypass manual input
                                    {'season': season_selection, 'episode': episode_selection}
    """
    season_selection = None
    episode_selection = None
    
    if selections:
        season_selection = selections.get('season')
        episode_selection = selections.get('episode')
        
    download_series(select_title, season_selection, episode_selection)

def search(
    string_to_search: str = None,
    get_onlyDatabase: bool = False,
    direct_item: str = None, # Accept str index or dict
    selections: dict | None = None
):
    """
    Main search function for the streamingcommunity provider.
    Calls the unified search logic.
    """
    # Pass the current module to the unified function
    provider_module = sys.modules[__name__]

    # Call the unified search function with provider-specific settings
    unified_search(
        provider_module=provider_module,
        string_to_search=string_to_search,
        get_onlyDatabase=get_onlyDatabase,
        direct_item=direct_item,
        selections=selections,
        # Provider specific flags/details:
        use_telegram=(site_constant.TELEGRAM_BOT is True), # Check if Telegram is enabled
        use_quote_plus=False, # This provider didn't use quote_plus in the original search call
        provider_name=site_constant.SITE_NAME, # Get name from config
        search_func_args=None, # No extra args needed for this provider's title_search
        process_func_kwargs=None # No extra kwargs needed for this provider's process_search_result
    )
'''
def search(string_to_search: str = None, get_onlyDatabase: bool = False, direct_item: dict = None, selections: dict = None):
    """
    Main function of the application for search.

    Parameters:
        string_to_search (str, optional): String to search for
        get_onlyDatabase (bool, optional): If True, return only the database object
        direct_item (dict, optional): Direct item to process (bypass search)
        selections (dict, optional): Dictionary containing selection inputs that bypass manual input
                                    {'season': season_selection, 'episode': episode_selection}
    """
    if direct_item:
        select_title = MediaItem(**direct_item)
        process_search_result(select_title, selections)
        return

    if string_to_search is None:
        string_to_search = msg.ask(f"\n[purple]Insert word to search in [green]{site_constant.SITE_NAME}").strip()
    
    # Search on database
    len_database = title_search(quote_plus(string_to_search))

    # If only the database is needed, return the manager
    if get_onlyDatabase:
        return media_search_manager

    if len_database > 0:
        select_title = get_select_title(table_show_manager, media_search_manager)
        process_search_result(select_title, selections)

    else:

        # If no results are found, ask again
        console.print(f"\n[red]Nothing matching was found for[white]: [purple]{string_to_search}")
        search()
'''