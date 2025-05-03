# 03.05.2025

import sys
import time
import logging
import argparse # Keep import here for type hinting if needed

# --- Setup Logging ---

from .Util.logger import Logger # Assuming Logger setup logging on import
log_not = Logger() # Instantiating might configure it

# --- Import Modularized Components ---
try:
    from StreamingCommunity.Util.Main.config_handler import apply_config_updates_from_args, TELEGRAM_BOT, CLOSE_CONSOLE
    from StreamingCommunity.Util.Main.provider_loader import load_search_functions
    from StreamingCommunity.Util.Main.argument_parser import setup_parser
    from StreamingCommunity.Util.Main.initialization import initialize_app
    from StreamingCommunity.Util.Main.execution_handler import handle_execution
    from StreamingCommunity.Util.Main.utils import restart_script, force_exit # Import utils
    from StreamingCommunity.TelegramHelp.telegram_bot import get_bot_instance, TelegramSession # For init/cleanup
except ImportError as e:
    print(f"Fatal Error: Failed to import core modules. Check structure and dependencies: {e}", file=sys.stderr)
    sys.exit(1)


def main(script_id_arg="unknown"):
    """Main function encapsulating the application logic."""

    if TELEGRAM_BOT:
        # Initialize bot instance early if needed globally
        try:
            bot = get_bot_instance()
            bot.send_message(f"Script instance '{script_id_arg}' started.", None)
            # Store script_id in session
            if script_id_arg != "unknown":
                 TelegramSession.set_session(script_id_arg)
        except Exception as e:
            logging.error(f"Failed to initialize or notify Telegram Bot: {e}")
            # Decide if this is fatal or continue without bot features
            print("[Warning] Could not initialize Telegram features.", file=sys.stderr)


    start_time = time.time()
    logging.info(f"--- Application Start (ID: {script_id_arg}) ---")

    try:
        # 1. Initialization
        initialize_app()

        # 2. Load Providers
        logging.info("Loading provider functions...")
        search_functions = load_search_functions()
        if not search_functions:
             logging.warning("No provider search functions were loaded. Check logs.")
             # Decide if execution can continue or should exit
             print("[Warning] No search providers loaded. Functionality will be limited.", file=sys.stderr)
             # force_exit() # Exit if providers are essential

        logging.info(f"Providers loaded in: {time.time() - start_time:.2f} s")

        # 3. Setup and Parse Arguments
        parser = setup_parser(search_functions)
        args = parser.parse_args()

        # Update script_id if provided via args (overrides default/generated)
        script_id = args.script_id if args.script_id != "unknown" else script_id_arg
        if script_id == "unknown":
             # Generate a default ID if none provided
             script_id = f"session_{int(time.time())}"
             logging.info(f"Using generated script ID: {script_id}")


        # 4. Apply Config Updates from Args
        apply_config_updates_from_args(args) # This also updates runtime constants like CLOSE_CONSOLE

        # 5. Handle Execution based on Args/Interaction
        handle_execution(args, search_functions)

        logging.info(f"--- Execution Completed (ID: {script_id}) ---")

    except KeyboardInterrupt:
        print("\nKeyboard interrupt received. Exiting...")
        logging.warning("KeyboardInterrupt received.")
        # Perform cleanup before forced exit
        if TELEGRAM_BOT:
            script_id_tg = TelegramSession.get_session()
            if script_id_tg != "unknown":
                 TelegramSession.deleteScriptId(script_id_tg)
        force_exit()
    except Exception as e:
        logging.critical(f"An unhandled critical error occurred: {e}", exc_info=True)
        print(f"\n[bold red]A critical error occurred. Check logs for details.[/bold red]")
        # Perform cleanup before forced exit
        if TELEGRAM_BOT:
             script_id_tg = TelegramSession.get_session()
             if script_id_tg != "unknown":
                  TelegramSession.deleteScriptId(script_id_tg)
        force_exit() # Ensure exit even on critical error

    finally:
        # Final cleanup, might be redundant if force_exit used os._exit
        logging.info(f"--- Application End (ID: {script_id}) ---")
        # Ensure Telegram session is cleared if script exits normally without force_exit
        # (e.g., non-looping mode finishes)
        if TELEGRAM_BOT and not CLOSE_CONSOLE: # Only cleanup if not looping/restarting
             script_id_tg = TelegramSession.get_session()
             if script_id_tg != "unknown":
                 TelegramSession.deleteScriptId(script_id_tg)


if __name__ == "__main__":
    # Pass script_id from command line if available, else default 'unknown'
    # Note: argparse handles this, but we might want it before parsing for early TG message
    sid = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith('-') else "unknown"
    run_main(script_id_arg=sid)