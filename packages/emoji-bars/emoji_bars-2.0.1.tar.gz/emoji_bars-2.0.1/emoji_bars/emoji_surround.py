class EmojiSurrounder:
    "Used to surround text with a specified emoji. E.x. 🌟 Hello! 🌟"

    def __init__(self, emoji: str):
        self.emoji = emoji

    def surround(self, text: str):
        return f"{self.emoji} {text} {self.emoji}"


def get_emoji_surrounder(emoji: str, text: str):
    """
    Returns an instance of EmojiSurrounder with the specified emoji.

    Parameters:
    emoji (str): The emoji to be used for surrounding text.
    """
    return f"{emoji} {text} {emoji}"
