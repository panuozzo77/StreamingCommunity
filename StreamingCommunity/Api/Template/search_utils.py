# StreamingCommunity/Api/Template/search_utils.py

import sys
import subprocess
from urllib.parse import quote_plus
import types  # To access the provider module

# External library
from rich.console import Console
from rich.prompt import Prompt

# Internal utilities
# Note: Adjust path if necessary, assuming Template is sibling to TelegramHelp
from StreamingCommunity.Api.Template import get_select_title
from StreamingCommunity.Api.Template.config_loader import site_constant
from StreamingCommunity.Api.Template.Class.SearchType import MediaItem
from StreamingCommunity.TelegramHelp.telegram_bot import get_bot_instance

# Global instances (can be shared)
console = Console()
msg = Prompt()

'''
def process_search_result(provider_module, select_title, selections=None):
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

        provider_module.series.download_series(select_title, season_selection, episode_selection)

    else:
        provider_module.film.download_film(select_title)
'''

def unified_get_user_input(
    provider_name: str,
    string_to_search: str = None,
    use_telegram: bool = False
) -> str | None:
    """
    Handles getting the search term from the user, supporting console and Telegram.
    Returns the search string or None if the user wants to go back (Telegram).
    """
    if string_to_search is not None:
        return string_to_search

    if use_telegram and site_constant.TELEGRAM_BOT:
        bot = get_bot_instance()
        string_to_search = bot.ask(
            "key_search",
            f"Enter the search term for {provider_name}\nor type 'back' to return to the menu: ",
            None
        )
        if string_to_search == 'back':
            # Restart the script - This might be better handled by the main loop calling the provider
            console.print("[yellow]Returning to main menu...")
            # Instead of restarting here, signal back to the caller
            # subprocess.Popen([sys.executable] + sys.argv)
            # sys.exit()
            return None # Indicate 'back' was chosen
        return string_to_search.strip()
    else:
        return msg.ask(f"\n[purple]Insert a word to search in [green]{provider_name}").strip()


def unified_search(
    provider_module: types.ModuleType,
    string_to_search: str = None,
    get_onlyDatabase: bool = False,
    direct_item: str = None,
    selections: dict | None = None,
    use_telegram: bool = False,
    use_quote_plus: bool = False,
    provider_name: str = "Unknown",
    search_func_args: list | None = None, # Extra positional args for title_search (e.g., proxy)
    process_func_kwargs: dict | None = None # Extra kwargs for process_search_result (e.g., proxy)
):
    """
    Unified search function for various providers.

    Parameters:
        provider_module: The module object of the specific provider (e.g., streamingcommunity).
                         Must contain: title_search, media_search_manager,
                         table_show_manager, process_search_result.
        string_to_search (str, optional): Predefined search term.
        get_onlyDatabase (bool, optional): If True, return only the database object.
        direct_item (dict | str, optional): Direct item dict (MediaItem compatible)
                                            or index string (for pre-selection).
        selections (dict, optional): Predefined season/episode selections.
        use_telegram (bool): Whether to use Telegram bot integration for input/messages.
        use_quote_plus (bool): Whether to URL-encode the search string.
        provider_name (str): Display name of the provider site.
        search_func_args (list, optional): Additional positional args for provider_module.title_search.
        process_func_kwargs (dict, optional): Additional keyword args for provider_module.process_search_result.
    """
    if search_func_args is None:
        search_func_args = [] # is for additionalData in title_search for StreamingWatch
    if process_func_kwargs is None:
        process_func_kwargs = {} # is for proxy in process_search_result for StreamingWatch

    select_title = None

    # --- Direct Item Handling ---
    if direct_item is not None:
            try:
                provider_module.site.title_search(string_to_search, *search_func_args)
                select_title = get_select_title(provider_module.site.table_show_manager, provider_module.site.media_search_manager, preselected_index=int(direct_item))
                # Directly process if we have the full object
                #process_search_result(provider_module, select_title, selections, **process_func_kwargs)
                provider_module.process_search_result(select_title, selections, **process_func_kwargs)
                return
            except Exception as e:
                console.print(f"[red]Error processing direct_item dict: {e}")
                # Fallback to searching if direct processing fails or isn't intended like this
                select_title = None # Reset select_title
                if string_to_search is None: # Need a search term if direct item failed
                     console.print("[yellow]Direct item processing failed, please provide a search term.")
                     return # Or prompt? For now, just exit.


    if string_to_search is None:
        string_to_search = msg.ask(f"\n[purple]Insert a word to search in [green]{site_constant.SITE_NAME}").strip()

        # Search on database
    len_database = provider_module.title_search(string_to_search, *search_func_args)

    # If only the database is needed, return the manager
    if get_onlyDatabase:
        return provider_module.media_search_manager

    if len_database > 0:
        select_title = get_select_title(provider_module.table_show_manager, provider_module.media_search_manager)
        provider_module.process_search_result(select_title, selections, **process_func_kwargs)

    else:
        # If no results are found, ask again
        console.print(f"\n[red]Nothing matching was found for[white]: [purple]{string_to_search}")
        unified_search(provider_module = provider_module, use_telegram=use_telegram, use_quote_plus=use_quote_plus, provider_name=provider_name, search_func_args=search_func_args, process_func_kwargs=process_func_kwargs)