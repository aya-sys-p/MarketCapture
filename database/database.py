import csv
import sqlite3
from pathlib import Path


class Database:

    def __init__(self, db_path):

        self.db_path = Path(db_path)
        self.connection = None

    def connect(self):

        db_file = self.db_path.resolve()

        print(f"Using database : {db_file}")

        # データベースの親フォルダが無ければ作成
        db_file.parent.mkdir(parents=True, exist_ok=True)

        self.connection = sqlite3.connect(db_file)

        self.create_table()

    def create_table(self):

        cursor = self.connection.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS market_data (
            symbol TEXT NOT NULL,
            date TEXT NOT NULL,
            open REAL,
            high REAL,
            low REAL,
            close REAL,
            PRIMARY KEY(symbol, date)
        )
        """)

        self.connection.commit()

    def insert(self, symbol, date, open_price, high, low, close):

        cursor = self.connection.cursor()

        cursor.execute("""
        INSERT OR REPLACE INTO market_data
        (symbol, date, open, high, low, close)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (
            symbol,
            date,
            open_price,
            high,
            low,
            close
        ))

    def commit(self):

        self.connection.commit()

    def read_all(self, symbol):

        cursor = self.connection.cursor()

        cursor.execute("""
        SELECT date,
               open,
               high,
               low,
               close
        FROM market_data
        WHERE symbol = ?
        ORDER BY date DESC
        """, (symbol,))

        return cursor.fetchall()

    def get_latest_date(self, symbol):

        cursor = self.connection.cursor()

        cursor.execute("""
        SELECT MAX(date)
        FROM market_data
        WHERE symbol = ?
        """, (symbol,))

        result = cursor.fetchone()

        if result is None:
            return None

        return result[0]

    def get_symbols(self):

        cursor = self.connection.cursor()

        cursor.execute("""
        SELECT DISTINCT symbol
        FROM market_data
        ORDER BY symbol
        """)

        return [row[0] for row in cursor.fetchall()]

    def export_csv(self, symbol, filename):

        cursor = self.connection.cursor()

        cursor.execute("""
        SELECT symbol,
               date,
               open,
               high,
               low,
               close
        FROM market_data
        WHERE symbol = ?
        ORDER BY date
        """, (symbol,))

        rows = cursor.fetchall()

        output = Path(filename)
        output.parent.mkdir(parents=True, exist_ok=True)

        with open(output, "w", newline="", encoding="utf-8-sig") as f:

            writer = csv.writer(f)

            writer.writerow([
                "symbol",
                "date",
                "open",
                "high",
                "low",
                "close"
            ])

            writer.writerows(rows)

        print(f"CSV exported : {output.resolve()}")

    def close(self):

        if self.connection:
            self.connection.close()
            self.connection = None