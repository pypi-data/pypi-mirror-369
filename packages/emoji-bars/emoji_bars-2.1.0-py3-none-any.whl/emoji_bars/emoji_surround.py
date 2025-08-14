"""
Module for surrounding text with emojis. Use the function get_emoji_surrounder
"""


def get_emoji_surrounder(emoji: str, text: str):
    """
    Returns an instance of EmojiSurrounder with the specified emoji.

    Parameters:
    emoji (str): The emoji to be used for surrounding text.
    """
    return f"{emoji} {text} {emoji}"
