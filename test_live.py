import os
from dotenv import load_dotenv
from dhanhq import DhanContext, MarketFeed

load_dotenv()

ctx = DhanContext(os.getenv("DHAN_CLIENT_ID"), os.getenv("DHAN_ACCESS_TOKEN"))

# 1333 = HDFC Bank, 11536 = TCS
instruments = [
    (MarketFeed.NSE, "1333", MarketFeed.Ticker),
    (MarketFeed.NSE, "11536", MarketFeed.Ticker),
]

feed = MarketFeed(ctx, instruments, "v2")

while True:
    feed.run_forever()
    print(feed.get_data())