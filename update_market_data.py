import yfinance as yf
import pandas as pd
import json
from pathlib import Path

# =====================
# パス設定
# =====================
BASE_DIR = Path("market_data")
BASE_DIR.mkdir(parents=True, exist_ok=True)

SYMBOLS_FILE = BASE_DIR / "symbols.json"

# =====================
# 銘柄マスタ読み込み
# =====================
with open(SYMBOLS_FILE, "r", encoding="utf-8") as f:
    SYMBOLS = json.load(f)

# =====================
# 各銘柄処理
# =====================
for code, info in SYMBOLS.items():
    symbol = info["ticker"]
    print(f"=== Fetching data for {code} ({symbol}) ===")

    stock_dir = BASE_DIR / code
    stock_dir.mkdir(parents=True, exist_ok=True)

    # ===== 1分足 (intraday_1m.json) =====
    # アニメーションや5分足合成のベースデータ
    # period="5d" 程度が取得の安定性とデータ量のバランスが良いです
    min1_df = yf.download(
        symbol,
        interval="1m",
        period="5d",
        progress=False
    )

    if not min1_df.empty:
        # マルチインデックス対策
        min1_df.columns = min1_df.columns.get_level_values(0)

        # タイムゾーンを東京に変換
        idx = min1_df.index
        min1_df.index = (
            idx.tz_localize("UTC").tz_convert("Asia/Tokyo")
            if idx.tz is None else idx.tz_convert("Asia/Tokyo")
        )

        min1_df = min1_df.reset_index()

        min1_data = [
            {
                "time": row["Datetime"].strftime("%Y-%m-%d %H:%M"),
                "open": round(float(row["Open"]), 2),
                "high": round(float(row["High"]), 2),
                "low": round(float(row["Low"]), 2),
                "close": round(float(row["Close"]), 2),
                "volume": int(row["Volume"])
            }
            for _, row in min1_df.iterrows()
        ]

        with open(stock_dir / "intraday_1m.json", "w", encoding="utf-8") as f:
            json.dump(min1_data, f, ensure_ascii=False, indent=2)

    # ===== 日足 (daily.json) =====
    # 長期チャート用
    daily_df = yf.download(
        symbol,
        interval="1d",
        period="3y",
        progress=False
    )

    if not daily_df.empty:
        daily_df.columns = daily_df.columns.get_level_values(0)

        idx = daily_df.index
        daily_df.index = (
            idx.tz_localize("UTC").tz_convert("Asia/Tokyo")
            if idx.tz is None else idx.tz_convert("Asia/Tokyo")
        )

        daily_df = daily_df.reset_index()

        daily_data = [
            {
                "date": row["Date"].strftime("%Y-%m-%d"),
                "open": round(float(row["Open"]), 2),
                "high": round(float(row["High"]), 2),
                "low": round(float(row["Low"]), 2),
                "close": round(float(row["Close"]), 2),
                "volume": int(row["Volume"])
            }
            for _, row in daily_df.iterrows()
        ]

        with open(stock_dir / "daily.json", "w", encoding="utf-8") as f:
            json.dump(daily_data, f, ensure_ascii=False, indent=2)

    print(f"=== {code} completed ===\n")

print("🎉 All market data update completed (1m & Daily)")
