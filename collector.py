import yfinance as yf

from config import Config
from database.database import Database


class Collector:

    def __init__(self):
        self.db = None

    def open(self):
        pass

    def close(self):
        if self.db:
            self.db.close()
            self.db = None

    def load_history(self, symbol_name, yahoo_symbol, db_path):

        print(f"Downloading {symbol_name} ({yahoo_symbol})...")

        self.db = Database(db_path)
        self.db.connect()

        latest_date = self.db.get_latest_date(symbol_name)

        if latest_date:
            print(f"Latest date in DB : {latest_date}")
            start = latest_date
        else:
            print("No existing data.")
            start = None

        ticker = yf.Ticker(yahoo_symbol)

        if start is None:
            history = ticker.history(
                period=f"{Config.history_days}d",
                auto_adjust=False
            )
        else:
            history = ticker.history(
                start=start,
                auto_adjust=False
            )

        if history.empty:
            print("No new data.")
            self.close()
            return

        inserted = 0

        for date, row in history.iterrows():

            date_str = date.strftime("%Y-%m-%d")

            self.db.insert(
                symbol=symbol_name,
                date=date_str,
                open_price=float(row["Open"]),
                high=float(row["High"]),
                low=float(row["Low"]),
                close=float(row["Close"])
            )

            inserted += 1

        self.db.commit()

        print(f"{inserted} records processed.")

        self.close()