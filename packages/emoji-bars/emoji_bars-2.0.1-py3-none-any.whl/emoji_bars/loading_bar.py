"""
The module for creating a loading bar in the terminal using emojis.
"""

import warnings

# These are just for the nice terminal colour
GREEN = "\033[32m"
RED = "\033[31m"

RESET = "\033[0m"  # Resets to default terminal color


class LoadingBar:
    """A basic loading bar for the terminal.

    Parameters:

    on_emoji(str) : The emoji sr string to show a completed part of the bar
    off_emoji(str) : The emoji to show a non-completed part of the bar
    capacity(int) : The total length of the bar
    isPercentage(bool) : True if the status should be represented in percentage format, else in fraction format
    """

    def __init__(
        self,
        capacity: int,
        on_emoji: str = "█",
        off_emoji: str = "▒",
        is_percentage: bool = False,
    ):
        self.on_emoji = on_emoji
        self.off_emoji = off_emoji
        self.capacity = capacity
        self.is_percentage = is_percentage
        self.value = 0

    def incrememt_bar(self, prefix: str = "", suffix: str = "", display_status=True):
        """
        Prints out the loading bar

        Parameters:

        self.value(int) : The number specifying how much of the bar is complete e.g. 5
        prefix(str) : A message to come before the loading bar
        display_status(bool) : Whether to display the status
        end(bool) : This is to state whether the loading bar will end or not
        """
        output = ""
        status = ""
        self.value += 1
        if self.value > self.capacity:
            warnings.warn("self.value must be smaller than total capacity")
        else:
            for i in range(0, 20):
                # CHANGE THIS
                if i < (self.value / self.capacity) * 20:
                    output = output + self.on_emoji
                else:
                    output = output + self.off_emoji

        if self.is_percentage:
            status = round(self.value / self.capacity * 100)
            if not self.value >= self.capacity:
                print(
                    f"{prefix} {GREEN} {output} {suffix} {GREEN if self.value == self.capacity else RED} {status if display_status else ''}% {RESET}",
                    end="\r",
                )
            else:
                print(
                    f"{prefix} {GREEN} {output} {suffix} {GREEN if self.value == self.capacity else RED} {status if display_status else ''}% {RESET}",
                    end="\n",
                )
        else:
            status = str(self.value) + "/" + str(self.capacity)
            if not self.value >= self.capacity:
                print(
                    f"{prefix} {GREEN} {output} {suffix} {GREEN if self.value == self.capacity else RED} {status if display_status else ''} {RESET}",
                    end="\r",
                )
            else:
                print(
                    f"{prefix} {GREEN} {output} {suffix} {GREEN if self.value == self.capacity else RED} {status if display_status else ''} {RESET}",
                    end="\n",
                )
