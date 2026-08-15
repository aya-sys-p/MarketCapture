from pathlib import Path
from datetime import datetime

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from database.database import Database


# Windows 環境で繁體中文を表示
plt.rcParams["font.family"] = "Microsoft JhengHei"

# マイナス記号の文字化け防止
plt.rcParams["axes.unicode_minus"] = False


class Graph:

    def draw(
        self,
        symbol,
        db_path,
        output_dir,
        unit,
        name=None,
        name_en=None,
        history_days=365
    ):

        db = Database(db_path)
        db.connect()

        rows = db.read_all(symbol)

        db.close()

        if not rows:
            print(f"No data found for {symbol}")
            return

        dates = []
        prices = []

        # read_all() returns newest first
        for row in reversed(rows):
            dates.append(datetime.strptime(row[0], "%Y-%m-%d"))
            prices.append(row[4])

        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        output_file = output_dir / f"{symbol}.png"

        fig, ax = plt.subplots(figsize=(12, 6))

        # Price
        ax.plot(
            dates,
            prices,
            linewidth=2
        )

        # Latest point
        last_date = dates[-1]
        last_price = prices[-1]

        ax.scatter(
            last_date,
            last_price,
            s=35,
            zorder=5
        )

        # Title
        if name and name_en:
            title = f"{symbol} {name} ({name_en})"
        elif name:
            title = f"{symbol} {name}"
        else:
            title = symbol

        ax.set_title(
            title,
            loc="left",
            fontsize=14,
            fontweight="bold"
        )

        ax.set_xlabel("Date")
        ax.set_ylabel(f"Price ({unit})")

        locator = mdates.AutoDateLocator()
        formatter = mdates.ConciseDateFormatter(locator)

        ax.xaxis.set_major_locator(locator)
        ax.xaxis.set_major_formatter(formatter)

        ax.grid(
            True,
            linestyle="--",
            alpha=0.35
        )

        fig.autofmt_xdate()

        # 右側の情報パネル用余白
        plt.subplots_adjust(right=0.80)

        info_items = [
            ("Latest Price", f"{last_price:.2f} {unit}"),
            ("Latest Date", f"{last_date:%Y-%m-%d}"),
            ("Period", f"{history_days} days"),
        ]

                # 情報パネル（ラベル列・値列）
        start_y = 0.95
        line_height = 0.08

        for index, (label, value) in enumerate(info_items):

            y = start_y - index * line_height

            # ラベル
            ax.text(
                1.04,
                y,
                label,
                transform=ax.transAxes,
                ha="left",
                va="top",
                fontsize=10,
                fontweight="bold"
            )

            # 値
            ax.text(
                1.20,
                y,
                value,
                transform=ax.transAxes,
                ha="left",
                va="top",
                fontsize=10
            )

        plt.savefig(
            output_file,
            dpi=300,
            bbox_inches="tight"
        )

        plt.close(fig)

        print(f"Saved graph : {output_file}")