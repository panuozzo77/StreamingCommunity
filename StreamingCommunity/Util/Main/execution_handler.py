# StreamingCommunity/execution_handler.py
import argparse
import logging
from typing import Callable, Dict, Tuple, Any

# External library
from rich.console import Console

# Internal utilities
from StreamingCommunity.global_search import global_search # Import global search function
from .user_interface import get_user_choice # Import interactive choice function
from .config_handler import CLOSE_CONSOLE, TELEGRAM_BOT # Import config flags
from StreamingCommunity.Util.Main.utils import restart_script, force_exit # Import exit/restart helpers
from StreamingCommunity.TelegramHelp.telegram_bot import get_bot_instance, TelegramSession # For Telegram cleanup

console = Console()

SearchFuncInfo = Tuple[Callable[..., Any], str] # Type hint for (search_function, use_for)

def _run_function_wrapper(
    func: Callable[..., Any],
    close_console_flag: bool,
    search_terms: str | None = None,
    **kwargs
) -> None:
    """
    Internal wrapper to run a function once or repeatedly.
    Handles the loop based on the 'close_console_flag' (which means "don't close").
    """
    if close_console_flag: # True means loop indefinitely
        while True: # Loop until explicitly broken or script exits
            try:
                func(string_to_search=search_terms, **kwargs)
                # Decide if loop should continue after one successful run
                # Maybe add a prompt "Search again? [y/N]" here if looping
                # For now, assumes user wants to exit after one run in loop mode
                # unless the function itself handles looping or restarting.
                # Let's refine: If close_console_flag is True, we *don't* exit,
                # so the loop should prompt or restart.
                logging.info(f"Function {func.__name__} completed. Looping enabled.")
                # Break or prompt here if single execution per loop is desired
                # Or let it loop back automatically
                # Let's assume it should restart the main menu after one run
                restart_script() # Restart to show menu again
                break # Should not be reached if restart works

            except Exception as e:
                 logging.error(f"Error during execution of {func.__name__}: {e}", exc_info=True)
                 console.print(f"[bold red]An error occurred during the operation:[/bold red] {e}")
                 # Decide whether to retry or break the loop on error
                 break # Exit loop on error
    else: # Run once
        try:
            func(string_to_search=search_terms, **kwargs)
            logging.info(f"Function {func.__name__} completed. Exiting.")
        except Exception as e:
            logging.error(f"Error during execution of {func.__name__}: {e}", exc_info=True)
            console.print(f"[bold red]An error occurred during the operation:[/bold red] {e}")
            # Script will exit naturally after this unless force_exit is called


def handle_execution(args: argparse.Namespace, search_functions: Dict[str, SearchFuncInfo]):
    """
    Determines which function to run based on arguments or user input
    and executes it using the wrapper.
    """
    search_terms = args.search
    arg_to_function: Dict[str, Callable] = {alias: func_info[0] for alias, func_info in search_functions.items()}
    # Mapping for interactive choice (index to function)
    input_to_function: Dict[str, Callable] = {
        str(i): func_info[0] for i, (alias, func_info) in enumerate(search_functions.items())
    }
    # Mapping for interactive choice labels (index to (label, category))
    choice_labels: Dict[str, Tuple[str, str]] = {
        str(i): (alias.split("_")[0].capitalize(), func_info[1])
        for i, (alias, func_info) in enumerate(search_functions.items())
    }

    # --- Priority 1: Non-Interactive Download ---
    if args.download_series and args.site and args.index and args.dl_season and args.dl_episodes:
        if args.site in input_to_function:
            selected_func = input_to_function[args.site]
            site_name = choice_labels[args.site][0] # Get name for logging
            console.print(f"[cyan]Running non-interactive download for '{args.download_series}' from site '{site_name}'...")
            _run_function_wrapper(
                selected_func,
                close_console_flag=CLOSE_CONSOLE, # Use loaded config value
                search_terms=args.download_series,
                direct_item=args.index, # Pass direct item index
                selections={'season': args.dl_season, 'episode': args.dl_episodes} # Pass selections
            )
            return # Non-interactive mode finished
        else:
            console.print(f"[red]Error:[/red] Invalid site index '{args.site}' provided for non-interactive download.")
            force_exit() # Exit on invalid non-interactive setup
            return

    # --- Priority 2: Global Search via Argument ---
    if getattr(args, 'global', False):
        console.print("[cyan]Running global search...")
        _run_function_wrapper(
            global_search,
            close_console_flag=CLOSE_CONSOLE,
            search_terms=search_terms
        )
        return # Global search finished

    # --- Priority 3: Specific Provider via Argument ---
    provider_func_to_run = None
    for arg_name, func in arg_to_function.items():
        if getattr(args, arg_name, False): # Check if the flag like --streamingcommunity_search is True
            provider_func_to_run = func
            provider_name = arg_name.split('_')[0]
            console.print(f"[cyan]Running search on '{provider_name}'...")
            break # Run the first one found

    if provider_func_to_run:
        _run_function_wrapper(
            provider_func_to_run,
            close_console_flag=CLOSE_CONSOLE,
            search_terms=search_terms
        )
        return # Provider search finished

    # --- Priority 4: Interactive Mode ---
    if not any(getattr(args, alias, False) for alias in arg_to_function) and not getattr(args, 'global', False):
        console.print("\n[bold yellow]Interactive Mode[/bold yellow]")
        chosen_category_index = get_user_choice(choice_labels, input_to_function)

        if chosen_category_index and chosen_category_index in input_to_function:
            selected_func = input_to_function[chosen_category_index]
            provider_name = choice_labels[chosen_category_index][0]
            console.print(f"\n[cyan]Selected provider: {provider_name}[/cyan]")
            _run_function_wrapper(
                selected_func,
                close_console_flag=CLOSE_CONSOLE,
                search_terms=search_terms # Pass search terms if provided via -s
            )
        elif chosen_category_index is None and TELEGRAM_BOT:
             # User chose 'back' or invalid input in Telegram
             console.print("[yellow]Exiting or returning to menu (Telegram).[/yellow]")
             # Clean up Telegram session if necessary
             bot = get_bot_instance()
             bot.send_message("Operation cancelled or invalid.", None)
             script_id_tg = TelegramSession.get_session()
             if script_id_tg != "unknown":
                 TelegramSession.deleteScriptId(script_id_tg)
             force_exit() # Or return control to a higher loop if applicable
        else:
             # Invalid choice in console or unhandled case
             console.print("[red]Invalid category or operation cancelled.[/red]")
             if CLOSE_CONSOLE:
                 restart_script()
             else:
                 force_exit()
                 # Clean up Telegram session if it was initiated
                 if TELEGRAM_BOT:
                     script_id_tg = TelegramSession.get_session()
                     if script_id_tg != "unknown":
                          TelegramSession.deleteScriptId(script_id_tg)
    else:
        # This case should ideally not be reached if logic above is complete
        logging.warning("Execution handler reached unexpected state. No action taken.")
        console.print("[yellow]No action specified or arguments conflict. Please check command.[/yellow]")
        if CLOSE_CONSOLE:
            restart_script()
        else:
            force_exit()