# 03.05.2025

from StreamingCommunity.Util.config_json import config_manager

# Load constants directly from config_manager at module load time
SHOW_TRENDING = config_manager.get_bool('DEFAULT', 'show_trending')
CLOSE_CONSOLE = config_manager.get_bool('DEFAULT', 'not_close') # Note: Original script had `not_close`, mapping might be inverted? Assuming True means "don't close"
TELEGRAM_BOT = config_manager.get_bool('DEFAULT', 'telegram_bot')

def apply_config_updates_from_args(args):
    """Applies configuration updates based on parsed command-line arguments."""
    config_updates = {}

    # Map command-line arguments to the config values
    if args.add_siteName is not None:
        config_updates['DEFAULT.add_siteName'] = str(args.add_siteName).lower() == 'true'
    if args.not_close is not None:
         # Assuming args.not_close=True means CLOSE_CONSOLE=False
        config_updates['DEFAULT.not_close'] = str(args.not_close).lower() == 'true'
    if args.default_video_worker is not None:
        config_updates['M3U8_DOWNLOAD.default_video_worker'] = args.default_video_worker
    if args.default_audio_worker is not None:
        config_updates['M3U8_DOWNLOAD.default_audio_worker'] = args.default_audio_worker
    if args.specific_list_audio is not None:
        # Ensure it's saved as a list if that's how config_manager expects it
        config_updates['M3U8_DOWNLOAD.specific_list_audio'] = args.specific_list_audio.split(',')
    if args.specific_list_subtitles is not None:
        config_updates['M3U8_DOWNLOAD.specific_list_subtitles'] = args.specific_list_subtitles.split(',')

    # Apply the updates to the config file
    updated = False
    for key, value in config_updates.items():
        section, option = key.split('.')
        # Only update if the value is different from current to avoid unnecessary writes
        current_value = config_manager.get_key(section, option)
        # Basic type comparison might be needed here if types differ
        if str(current_value) != str(value):
             config_manager.set_key(section, option, value)
             updated = True

    if updated:
        config_manager.save_config()
        print("Configuration updated based on command-line arguments.")

    # Update constants in this module *after* saving, if needed for the current run
    # This is tricky, often requires re-reading or careful state management.
    # It might be simpler to rely on the values read initially for the current run.
    global CLOSE_CONSOLE, TELEGRAM_BOT # Example if you need to update runtime state
    CLOSE_CONSOLE = config_manager.get_bool('DEFAULT', 'not_close')
    TELEGRAM_BOT = config_manager.get_bool('DEFAULT', 'telegram_bot')