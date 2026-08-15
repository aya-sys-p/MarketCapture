from config import Config
from collector import Collector
from graph.graph import Graph
from database.database import Database

import os


def process_symbols(symbols, db_path, output_dir):

    collector = Collector()
    graph = Graph()

    for symbol, info in symbols.items():

        ticker = info["ticker"]
        unit = info["unit"]
        name = info.get("name")
        name_en = info.get("name_en")

        print(f"Processing {symbol}...")

        collector.load_history(
            symbol,
            ticker,
            db_path
        )

        graph.draw(
            symbol,
            db_path,
            output_dir,
            unit,
            name,
            name_en,
            Config.history_days
        )

    #
    # CSV出力
    #
    print(f"\nExporting CSV ({db_path})...")

    db = Database(db_path)
    db.connect()

    csv_dir = os.path.join(output_dir, "csv")

    for symbol in db.get_symbols():

        filename = os.path.join(csv_dir, f"{symbol}.csv")

        db.export_csv(symbol, filename)

    db.close()


def main():

    process_symbols(
        Config.stock_symbols,
        Config.stock_db,
        Config.stock_output
    )

    process_symbols(
        Config.commodity_symbols,
        Config.commodity_db,
        Config.commodity_output
    )

    print("\nCompleted.")


if __name__ == "__main__":
    main()