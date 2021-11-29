import yfinance
import datetime
import time 

class Ticker():
    def __init__(self, symbol):
        self.last_update = datetime.datetime.now()
        self.symbol = symbol
        self.inner = yfinance.Ticker(symbol)
        self.info = self.inner.info
        try:
            self.current_price = self.inner.history(period="1d")["Close"][0]
            self.exists = True
        except:
            self.exists = False
    def about(self):
        self.update()
        if not self.exists:
            return "No such company"
        if "longBusinessSummary" in self.info:
            return self.info["longBusinessSummary"]
        if "shortBusinessSummary" in self.info:
            return self.info["shortBusinessSummary"]
        else:
            return f"Sorry, I don`t no anything ${self.symbol}"
    def open(self):
        self.update()
        if self.exists and "open" in self.info:
            return self.info["open"]
        return None
    def price(self):
        self.update()
        if self.exists:
            return self.current_price
        return None
    def update(self):
        #   print(datetime.date(time.time()) - self.last_update)
        if self.exists and datetime.datetime.now() - self.last_update > datetime.timedelta(minutes=10):
            self.last_update = datetime.datetime.now()
            self.inner = yfinance.Ticker(self.symbol)
            self.info = self.inner.info
            self.current_price = self.inner.history(period="1d")["Close"][0]
            print(f"${self.symbol} data updated")


class StockingFetcher(object):
    def __init__(self):
        self.cache = {}
    def fetch(self, symbol):
        if not symbol in self.cache:
            self.cache[symbol] = Ticker(symbol)
        return self.cache[symbol]

if __name__ == "__main__":
    fetcher = StockingFetcher()
    while True:
        print(fetcher.fetch(input()).about())
