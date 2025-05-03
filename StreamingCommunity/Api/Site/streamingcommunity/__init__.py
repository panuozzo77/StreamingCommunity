# 03.05.2025

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