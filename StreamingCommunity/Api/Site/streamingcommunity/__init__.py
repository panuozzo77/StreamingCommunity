'''
# 21.05.24

import sys
import subprocess
from urllib.parse import quote_plus


# External library
from rich.console import Console
from rich.prompt import Prompt


# Internal utilities
from StreamingCommunity.Api.Template import get_select_title
from StreamingCommunity.Api.Template.config_loader import site_constant
from StreamingCommunity.Api.Template.Class.SearchType import MediaItem
from StreamingCommunity.TelegramHelp.telegram_bot import get_bot_instance


# Logic class
from .site import title_search, table_show_manager, media_search_manager
from .film import download_film
from .series import download_series


# Variable
indice = 0
_useFor = "film_serie"
_priority = 0
_engineDownload = "hls"

msg = Prompt()
console = Console()


def get_user_input(string_to_search: str = None):
    """
    Asks the user to input a search term.
    Handles both Telegram bot input and direct input.
    """
    if string_to_search is None:
        if site_constant.TELEGRAM_BOT:
            bot = get_bot_instance()
            string_to_search = bot.ask(
                "key_search",
                f"Enter the search term\nor type 'back' to return to the menu: ",
                None
            )

            if string_to_search == 'back':

                # Restart the script
                subprocess.Popen([sys.executable] + sys.argv)
                sys.exit()
        else:
            string_to_search = msg.ask(f"\n[purple]Insert a word to search in [green]{site_constant.SITE_NAME}").strip()

    return string_to_search

def process_search_result(select_title, selections=None):
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

        download_series(select_title, season_selection, episode_selection)

    else:
        download_film(select_title)

def search(string_to_search: str = None, get_onlyDatabase: bool = False, direct_item: str = None, selections: dict = None):
    """
    Main function of the application for search.

    Parameters:
        string_to_search (str, optional): String to search for
        get_onlyDatabase (bool, optional): If True, return only the database object
        direct_item (dict, optional): Direct item to process (bypass search)
        selections (dict, optional): Dictionary containing selection inputs that bypass manual input
                                    {'season': season_selection, 'episode': episode_selection}
    """

    if direct_item is not None:
        if string_to_search:
            title_search(string_to_search)
            # Directly select the first search result (index 0)
            select_title = get_select_title(table_show_manager, media_search_manager, preselected_index=int(direct_item))
            # Process the automatically selected title
            process_search_result(select_title, selections)
        else:
            # Handle the case where the search yielded no results
            print("No search results found for direct selection.")
        return

    if string_to_search is None:
        string_to_search = msg.ask(f"\n[purple]Insert a word to search in [green]{site_constant.SITE_NAME}").strip()

    # Search on database
    len_database = title_search(string_to_search)

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
# StreamingCommunity/Api/Site/streamingcommunity/__init__.py
# Date: (use current date)

import sys # Keep for module access if needed elsewhere

# --- Common Imports (Keep) ---
from urllib.parse import quote_plus # Needed if used elsewhere, but search handles it now

# External library
from rich.console import Console # Keep if used elsewhere
from rich.prompt import Prompt # Keep if used elsewhere

# Internal utilities
# Import the unified search logic
from StreamingCommunity.Api.Template.search_utils import unified_search
# Keep MediaItem if needed for type hinting or other logic here
from StreamingCommunity.Api.Template.Class.SearchType import MediaItem
from StreamingCommunity.Api.Template.config_loader import site_constant # Keep for provider_name, TELEGRAM_BOT check

# --- Provider Specific Imports ---
# Logic class (relative imports for this provider)
from .site import title_search, table_show_manager, media_search_manager # Needed by unified_search
from .film import download_film      # Needed by process_search_result
from .series import download_series  # Needed by process_search_result

# --- Provider Specific Variables ---
indice = 0 # Keep provider-specific metadata if used elsewhere
_useFor = "film_serie"
_priority = 0
_engineDownload = "hls"

# Keep console/msg if used directly in this file (e.g., in process_search_result)
console = Console()
msg = Prompt()

# --- Provider Specific Functions ---

# Keep get_user_input if it has *very specific* logic not covered by unified one.
# Otherwise, it can be removed as unified_get_user_input handles the core logic.
# Let's assume unified_get_user_input is sufficient for now.

def process_search_result(select_title: MediaItem, selections: dict | None = None, **kwargs):
    """
    Handles the search result for this specific provider.
    Initiates the download for either a film or series.

    Parameters:
        select_title (MediaItem): The selected media item.
        selections (dict, optional): Dictionary containing selection inputs.
        **kwargs: Catches potential extra arguments (like proxy) if added later.
    """
    # NOTE: This function *must* exist and be callable by unified_search
    # It contains the provider-specific download logic.

    if select_title.type == 'tv':
        season_selection = None
        episode_selection = None

        if selections:
            season_selection = selections.get('season')
            episode_selection = selections.get('episode')

        # Call the specific download function for this provider
        download_series(select_title, season_selection, episode_selection)

    else:
        # Call the specific download function for this provider
        download_film(select_title)


# --- The Main Search Function (Now a Wrapper) ---

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

    # The unified_search handles printing messages for success/failure/no results.
    # No need for the recursive call `search()` here if no results found.