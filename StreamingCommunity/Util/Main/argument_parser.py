# 03/05/2025c

import argparse

# Helper to generate unique short options if needed
def _generate_unique_short_option(alias, used_short_options):
    base_short = alias[:3].upper()
    short_option = base_short
    count = 1
    while short_option in used_short_options:
        # Try adding numbers, ensure length doesn't exceed common limits if needed
        short_option = f"{base_short[:2]}{count}" # Example: SC1, SC2
        count += 1
        if count > 9: # Avoid excessive length or infinite loop
             short_option = None # Cannot generate unique short
             break
    return short_option

def setup_parser(search_functions):
    """
    Creates and configures the ArgumentParser.

    Parameters:
        search_functions (dict): Dictionary from load_search_functions.

    Returns:
        argparse.ArgumentParser: The configured parser object.
    """
    parser = argparse.ArgumentParser(
        description='Script to download movies and series from the internet. Use command-line arguments to configure or perform actions non-interactively.',
        formatter_class=argparse.RawTextHelpFormatter # Improves help text formatting
    )

    # --- Non-interactive Download Arguments ---
    download_group = parser.add_argument_group('Non-Interactive Download')
    download_group.add_argument('--download-series', type=str, metavar='SERIES_NAME',
                                help='Name of the series to download non-interactively.')
    download_group.add_argument('--site', type=str, metavar='SITE_INDEX',
                                help='Site index (number from interactive menu, e.g., 0) to download from.\nRequired with --download-series.')
    download_group.add_argument('--index', type=str, metavar='RESULT_INDEX',
                                help='Search result index (usually 0 for the first match) to select.\nRequired with --download-series.')
    download_group.add_argument('--dl-season', type=str, metavar='SEASON',
                                help='Season number or range (e.g., "1", "1-3", "*").\nRequired with --download-series.')
    download_group.add_argument('--dl-episodes', type=str, metavar='EPISODES',
                                help='Episode number, range, or "*" (e.g., "5", "4-6", "*").\nRequired with --download-series.')

    # --- Configuration Arguments ---
    config_group = parser.add_argument_group('Configuration Overrides (Optional)')
    config_group.add_argument('--add_siteName', type=str, choices=['true', 'false'], metavar='BOOL',
                              help='Add site name to downloaded file name (true/false).')
    config_group.add_argument('--not_close', type=str, choices=['true', 'false'], metavar='BOOL',
                              help='Keep console open after script finishes (true/false).')
    config_group.add_argument('--default_video_worker', type=int, metavar='N',
                              help='Number of workers for video download (M3U8).')
    config_group.add_argument('--default_audio_worker', type=int, metavar='N',
                              help='Number of workers for audio download (M3U8).')
    config_group.add_argument('--specific_list_audio', type=str, metavar='LANGS',
                              help='Comma-separated list of specific audio languages (e.g., ita,eng).')
    config_group.add_argument('--specific_list_subtitles', type=str, metavar='LANGS',
                              help='Comma-separated list of subtitle languages (e.g., eng,spa).')

    # --- Search Mode Arguments ---
    search_mode_group = parser.add_argument_group('Search Modes')
    search_mode_group.add_argument('--global', action='store_true',
                                   help='Perform a global search across multiple sites.')
    search_mode_group.add_argument('-s', '--search', type=str, metavar='TERMS', default=None,
                                   help='Search terms to use with a selected site or global search.')

    # --- Dynamic Provider Selection Arguments ---
    provider_group = parser.add_argument_group('Provider Selection (Alternative to Interactive Menu)')
    used_short_options = {'s'} # Initialize with manually defined short options

    # Sort aliases for consistent help message order
    sorted_aliases = sorted(search_functions.keys())

    for alias in sorted_aliases:
        provider_name = alias.split("_")[0]
        short_option = _generate_unique_short_option(alias, used_short_options)
        if short_option:
            provider_group.add_argument(f'-{short_option}', f'--{alias}', action='store_true',
                                      help=f'Search on site: {provider_name}')
            used_short_options.add(short_option)
        else:
             # If a unique short couldn't be generated, only add the long option
             provider_group.add_argument(f'--{alias}', action='store_true',
                                       help=f'Search on site: {provider_name}')
             logging.warning(f"Could not generate unique short option for --{alias}. Only long option available.")


    # --- General Arguments ---
    parser.add_argument("script_id", nargs="?", default="unknown", help=argparse.SUPPRESS) # Hide from standard help

    return parser