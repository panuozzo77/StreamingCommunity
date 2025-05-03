# 03.05.2025

from rich.console import Console
from rich.prompt import Prompt

# Internal utilities (assuming get_bot_instance is accessible)
from StreamingCommunity.TelegramHelp.telegram_bot import get_bot_instance
from .config_handler import TELEGRAM_BOT  # Get config value

console = Console()
msg = Prompt()

# Define color map centrally if used in multiple places
COLOR_MAP = {
    "anime": "red",
    "film_serie": "yellow",
    "film": "blue",
    "serie": "green",
    "other": "white"
}


def display_legend():
    """Displays the category color legend."""
    legend_text = " | ".join([f"[{color}]{category.replace('_', ' ').capitalize()}[/{color}]"
                              for category, color in COLOR_MAP.items()])
    console.print(f"\n[bold green]Category Legend:[/bold green] {legend_text}")


def get_user_choice(choice_labels, input_to_function):
    """
    Prompts the user to select a provider/category interactively.

    Parameters:
        choice_labels (dict): Maps index string to (label, category_key).
        input_to_function (dict): Maps index string to the function to call.

    Returns:
        str | None: The chosen category index string, or None if invalid/back.
    """

    if TELEGRAM_BOT:
        bot = get_bot_instance()  # Get instance when needed

        # Build Telegram prompt message
        category_legend_str = "Categories:\n" + " | ".join(
            [f"{cat.replace('_', ' ').capitalize()}" for cat in COLOR_MAP.keys()]
        )
        provider_list_str = "\n".join(
            [f"{key}: {label[0]}" for key, label in choice_labels.items()]
        )
        prompt_message_tg = f"{category_legend_str}\n\nSelect provider:\n{provider_list_str}\n\nType 'back' to exit."

        # Ask user via Telegram
        # Provide choices for potential button interface in Telegram
        tg_choices = list(choice_labels.keys()) + ['back']
        chosen_category = bot.ask(
            key="select_provider",  # Unique key for this question
            question=prompt_message_tg,
            # choices=tg_choices # Optional: Pass choices if bot framework supports buttons
            default_value=None
        )

        if chosen_category == 'back':
            return None
        if chosen_category in input_to_function:
            return chosen_category
        else:
            bot.send_message("Invalid selection.", None)
            return None  # Indicate invalid choice

    else:  # Console interaction
        display_legend()

        # Build console prompt message with colors
        prompt_options = ", ".join(
            [f"{key}: [{COLOR_MAP.get(label[1], 'white')}]{label[0]}[/{COLOR_MAP.get(label[1], 'white')}]"
             for key, label in choice_labels.items()]
        )
        prompt_message_console = f"[green]Select category [white]({prompt_options}[white])"

        # Ask user via console
        chosen_category = msg.ask(
            prompt_message_console,
            choices=list(choice_labels.keys()),
            default="0",
            show_choices=False,  # Keep choices inline in prompt
            show_default=False  # Don't show "(default is 0)"
        )

        if chosen_category in input_to_function:
            return chosen_category
        else:
            # Should not happen if choices constraint works, but good practice
            console.print("[red]Invalid category selected.[/red]")
            return None

