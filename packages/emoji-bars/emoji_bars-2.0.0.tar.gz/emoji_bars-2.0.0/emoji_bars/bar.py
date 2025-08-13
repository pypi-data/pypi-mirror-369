def get_bar(emoji: str, length: int):
    """
    Prints out a row of emojis

    Parameters:

    emoji(str) : The emoji to be repeated
    length(int) : The number of times the emoji should be repeated
    """
    output = ""
    for i in range(0, length):
        output += emoji
    return output
