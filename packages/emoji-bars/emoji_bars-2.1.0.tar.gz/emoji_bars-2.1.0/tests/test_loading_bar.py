import time
from emoji_bars.loading_bar import LoadingBar

testBar = LoadingBar(10)
for i in range(0, testBar.capacity):
    testBar.incrememt_bar("Loading:")
    time.sleep(0.5)
