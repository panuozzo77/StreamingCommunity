# StreamingCommunity/Util/Main/provider_loader.py
# Date: (use current date)

import os
import sys
import glob
import logging
import importlib

# Import TELEGRAM_BOT constant relative to current location
# Assuming config_handler is also in Util/Main
from .config_handler import TELEGRAM_BOT
# If config_handler is elsewhere (e.g., Util/), adjust:
# from ..config_handler import TELEGRAM_BOT

def load_search_functions():
    """
    Dynamically finds, imports, and sorts provider modules and their search functions.

    Returns:
        dict: A dictionary mapping unique module aliases to tuples of (search_function, use_for_category).
    """
    modules_info = []
    loaded_functions = {}

    # List of sites to exclude if TELEGRAM_BOT is active
    excluded_sites = {"cb01new", "ddlstreamitaly", "guardaserie", "ilcorsaronero", "mostraguarda"} if TELEGRAM_BOT else set()

    # --- Corrected Path Calculation ---
    try:
        if getattr(sys, 'frozen', False):  # PyInstaller mode
            # Base path in frozen mode (often the executable's dir or _MEIPASS)
            base_path = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
            # Assuming the Api/Site structure relative to base_path is consistent
            # If Api is directly under base_path:
            project_root = base_path
            # If Api is nested (e.g., under a 'StreamingCommunity' folder within base_path)
            # project_root = os.path.join(base_path, 'StreamingCommunity') # Adjust as needed
        else:
            # Development mode
            # 1. Get the directory of the current file (provider_loader.py)
            current_file_dir = os.path.dirname(os.path.abspath(__file__))
            # Expected: .../StreamingCommunity/Util/Main

            # 2. Go up two levels to reach the project root
            project_root = os.path.dirname(os.path.dirname(current_file_dir))
            # Expected: .../StreamingCommunity

        # 3. Construct the final path to the providers directory
        api_dir = os.path.join(project_root, 'Api', 'Site')

    except Exception as e:
        logging.error(f"Error calculating API directory path: {e}", exc_info=True)
        return {} # Cannot proceed without the path

    # --- End of Corrected Path Calculation ---

    logging.debug(f"Looking for provider modules in: {api_dir}")
    if not os.path.isdir(api_dir):
        logging.error(f"API directory not found: {api_dir}")
        # Provide more context if possible
        logging.error(f"Calculated from project root: {project_root}")
        return {} # Return empty if directory doesn't exist

    init_files = glob.glob(os.path.join(api_dir, '*', '__init__.py'))
    logging.debug(f"Found init files: {init_files}")

    # Retrieve modules and their metadata
    for init_file in init_files:
        module_name = os.path.basename(os.path.dirname(init_file))

        if module_name in excluded_sites:
            logging.info(f"Skipping module '{module_name}' due to Telegram exclusion.")
            continue
        if module_name.startswith('__'): # Skip __pycache__ etc.
            continue

        logging.info(f"Attempting to load module: {module_name}")
        try:
            # Dynamically import the module relative to the project structure
            # The import path assumes 'StreamingCommunity' is in PYTHONPATH
            # or the script is run from the directory containing 'StreamingCommunity'
            mod = importlib.import_module(f'StreamingCommunity.Api.Site.{module_name}')

            # Get metadata, providing defaults
            indice = getattr(mod, 'indice', 99) # Default to high index if missing
            use_for = getattr(mod, '_useFor', 'other')
            priority = getattr(mod, '_priority', 0) # Also load priority if needed elsewhere
            modules_info.append({'name': module_name, 'index': indice, 'use_for': use_for, 'priority': priority, 'module': mod})

        except ModuleNotFoundError:
             # Provide more info for debugging ModuleNotFoundError
             logging.error(f"Failed to import module 'StreamingCommunity.Api.Site.{module_name}'. Check PYTHONPATH and ensure the package structure is correct relative to the execution directory.")
        except Exception as e:
            logging.error(f"Failed to load metadata from module '{module_name}': {str(e)}", exc_info=True)


    # Sort modules primarily by 'indice', secondarily by 'priority' (lower is better)
    modules_info.sort(key=lambda x: (x['index'], x['priority']))

    # Load search functions in the sorted order
    for module_data in modules_info:
        module_name = module_data['name']
        mod = module_data['module']
        use_for = module_data['use_for']

        # Construct a unique alias (keep original logic)
        module_alias = f'{module_name}_search'

        try:
            # Get the search function
            search_function = getattr(mod, 'search')

            # Store the function and its category
            loaded_functions[module_alias] = (search_function, use_for)
            logging.info(f"Successfully loaded search function from: {module_name}")

        except AttributeError:
            logging.error(f"'search' function not found in module: {module_name}")
        except Exception as e:
            logging.error(f"Failed to get search function from module '{module_name}': {str(e)}", exc_info=True)

    return loaded_functions