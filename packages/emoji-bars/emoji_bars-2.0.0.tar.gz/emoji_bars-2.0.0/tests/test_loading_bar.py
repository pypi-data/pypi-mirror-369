from emoji_bars.loadingBar import LoadingBar
import time

testBar = LoadingBar(10)
for i in range(0, testBar.capacity):
    testBar.incrememt_bar("Loading:")
    time.sleep(0.5)
