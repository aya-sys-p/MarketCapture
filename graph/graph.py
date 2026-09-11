from pathlib import Path
from datetime import datetime, timedelta
import math

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

        # ==========================================
        # DBから取得したデータを確認
        # ==========================================

        valid_rows = []

        for row in rows:

            date_value = row[0]
            price_value = row[4]

            # NULLデータを除外
            if price_value is None:
                print(
                    f"Skipped invalid data : "
                    f"{symbol} {date_value} (None)"
                )
                continue

            # 数値でないデータを除外
            try:
                price_value = float(price_value)

            except (TypeError, ValueError):

                print(
                    f"Skipped invalid data : "
                    f"{symbol} {date_value} ({price_value})"
                )
                continue

            # NaN / infinity を除外
            if not math.isfinite(price_value):

                print(
                    f"Skipped invalid data : "
                    f"{symbol} {date_value} ({price_value})"
                )
                continue

            # 0以下の価格を除外
            if price_value <= 0:

                print(
                    f"Skipped invalid data : "
                    f"{symbol} {date_value} ({price_value})"
                )
                continue

            # 日付をdatetimeに変換
            try:

                date = datetime.strptime(
                    date_value,
                    "%Y-%m-%d"
                )

            except (TypeError, ValueError):

                print(
                    f"Skipped invalid date : "
                    f"{symbol} {date_value}"
                )
                continue

            valid_rows.append(
                (date, price_value)
            )

        # ==========================================
        # 有効なデータがない場合
        # ==========================================

        if not valid_rows:

            print(
                f"No valid price data found for {symbol}"
            )

            return

        # ==========================================
        # 最新日を基準に表示期間を決定
        # ==========================================

        latest_date = max(
            date for date, price in valid_rows
        )

        start_date = (
            latest_date
            - timedelta(days=history_days - 1)
        )

        # ==========================================
        # 最新日から指定日数だけ抽出
        # ==========================================

        dates = []
        prices = []

        for date, price in valid_rows:

            if start_date <= date <= latest_date:

                dates.append(date)
                prices.append(price)

        # 日付順に並べ替え
        combined = sorted(
            zip(dates, prices),
            key=lambda x: x[0]
        )

        dates = [
            item[0]
            for item in combined
        ]

        prices = [
            item[1]
            for item in combined
        ]

        # ==========================================
        # 表示対象データがない場合
        # ==========================================

        if not dates or not prices:

            print(
                f"No data available "
                f"for the selected period : {symbol}"
            )

            return

        print(
            f"Graph period : "
            f"{dates[0]:%Y-%m-%d} "
            f"to "
            f"{dates[-1]:%Y-%m-%d}"
        )

        # ==========================================
        # 出力先
        # ==========================================

        output_dir = Path(output_dir)

        output_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        output_file = (
            output_dir
            / f"{symbol}.png"
        )

        # ==========================================
        # グラフ作成
        # ==========================================

        fig, ax = plt.subplots(
            figsize=(12, 6)
        )

        # Price
        ax.plot(
            dates,
            prices,
            linewidth=2
        )

        # ==========================================
        # 最新ポイント
        # ==========================================

        last_date = dates[-1]
        last_price = prices[-1]

        ax.scatter(
            last_date,
            last_price,
            s=35,
            zorder=5
        )

        # ==========================================
        # Title
        # ==========================================

        if name and name_en:

            title = (
                f"{symbol} "
                f"{name} "
                f"({name_en})"
            )

        elif name:

            title = (
                f"{symbol} "
                f"{name}"
            )

        else:

            title = symbol

        ax.set_title(
            title,
            loc="left",
            fontsize=14,
            fontweight="bold"
        )

        ax.set_xlabel("Date")

        ax.set_ylabel(
            f"Price ({unit})"
        )

        # ==========================================
        # X軸
        # ==========================================

        locator = mdates.AutoDateLocator()

        formatter = mdates.ConciseDateFormatter(
            locator
        )

        ax.xaxis.set_major_locator(
            locator
        )

        ax.xaxis.set_major_formatter(
            formatter
        )

        # ==========================================
        # Grid
        # ==========================================

        ax.grid(
            True,
            linestyle="--",
            alpha=0.35
        )

        fig.autofmt_xdate()

        # ==========================================
        # 右側の情報パネル用余白
        # ==========================================

        plt.subplots_adjust(
            right=0.80
        )

        # ==========================================
        # 情報パネル
        # ==========================================

        info_items = [
            (
                "Latest Price",
                f"{last_price:.2f} {unit}"
            ),
            (
                "Latest Date",
                f"{last_date:%Y-%m-%d}"
            ),
            (
                "Period",
                f"{history_days} days"
            ),
        ]

        start_y = 0.95
        line_height = 0.08

        for index, (label, value) in enumerate(
            info_items
        ):

            y = (
                start_y
                - index * line_height
            )

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

        # ==========================================
        # 保存
        # ==========================================

        plt.savefig(
            output_file,
            dpi=300,
            bbox_inches="tight"
        )

        plt.close(fig)

        print(
            f"Saved graph : "
            f"{output_file}"
        )