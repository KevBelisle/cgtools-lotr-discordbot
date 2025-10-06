import re
from typing import Union

from src.discord_client import icon_emojis, sphere_emojis


def format_number(value: int) -> Union[str, int]:
    """Format special numeric values for card stats."""
    if value == 255:
        return "-"
    elif value == 254:
        return "X"
    elif value == 253:
        return "✽"
    else:
        return value


# Text replacement patterns for Discord formatting
TEXT_REPLACEMENTS = [
    {
        "pattern": r"When Revealed:",
        "replacement": "**When Revealed:**",
    },
    {
        "pattern": r"Setup:",
        "replacement": "**Setup:**",
    },
    {
        "pattern": r"Valour Planning Action:",
        "replacement": "**Valour Planning Action:**",
    },
    {
        "pattern": r"Refresh Action:",
        "replacement": "**Refresh Action:**",
    },
    {
        "pattern": r"Planning Action:",
        "replacement": "**Planning Action:**",
    },
    {
        "pattern": r"Travel Action:",
        "replacement": "**Travel Action:**",
    },
    {
        "pattern": r"Valour Action:",
        "replacement": "**Valour Action:**",
    },
    {
        "pattern": r"Combat Action:",
        "replacement": "**Combat Action:**",
    },
    {
        "pattern": r"Quest Action:",
        "replacement": "**Quest Action:**",
    },
    {
        "pattern": r"Action:",
        "replacement": "**Action:**",
    },
    {
        "pattern": r"Forced:",
        "replacement": "**Forced:**",
    },
    {
        "pattern": r"Travel:",
        "replacement": "**Travel:**",
    },
    {
        "pattern": r"Valour Response:",
        "replacement": "**Valour Response:**",
    },
    {
        "pattern": r"Response:",
        "replacement": "**Response:**",
    },
    {
        "pattern": r"Riddle:",
        "replacement": "**Riddle:**",
    },
    {
        "pattern": r"Attack(?=\W)",
        "replacement": icon_emojis["Attack"],
    },
    {
        "pattern": r"Defense(?=\W)",
        "replacement": icon_emojis["Defense"],
    },
    {
        "pattern": r"Hit Points(?=\W)",
        "replacement": icon_emojis["HitPoints"],
    },
    {
        "pattern": r"Threat(?=\W)",
        "replacement": icon_emojis["Threat"],
    },
    {
        "pattern": r"Willpower(?=\W)",
        "replacement": icon_emojis["Willpower"],
    },
    {
        "pattern": r"\(\|\)",
        "replacement": icon_emojis["SauronsEye"],
    },
    {
        "pattern": r"Leadership",
        "replacement": sphere_emojis["Leadership"],
    },
    {
        "pattern": r"Lore",
        "replacement": sphere_emojis["Lore"],
    },
    {
        "pattern": r"Spirit",
        "replacement": sphere_emojis["Spirit"],
    },
    {
        "pattern": r"Tactics",
        "replacement": sphere_emojis["Tactics"],
    },
    {
        "pattern": r"Baggins(?= resource)|(?<=non-)Baggins",
        "replacement": sphere_emojis["Baggins"],
    },
    {
        "pattern": r"Fellowship",
        "replacement": sphere_emojis["Fellowship"],
    },
]


def format_card_text(text: str) -> str:
    """
    Format card text by applying replacements for game terms and icons.

    Args:
        text: The raw card text to format

    Returns:
        Formatted text with Discord markdown and emoji icons
    """
    output = text

    for replacement_rule in TEXT_REPLACEMENTS:
        pattern = replacement_rule["pattern"]
        replacement = replacement_rule["replacement"]
        output = re.sub(pattern, replacement, output)

    return output
