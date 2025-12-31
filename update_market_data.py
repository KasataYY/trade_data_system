import yfinance as yf
import pandas as pd
import json
from pathlib import Path

# =====================
# 設定
# =====================
BASE_DIR = Path("market_data")
SYMBOLS_FILE = BASE_DIR / "symbols.json"

BASE_DIR.mkdir(parents=True, exist_ok=True)

# =====================
# 銘柄リスト読み込み
# =====================
with open(SYMBOLS_FILE, "r", encoding="utf-8") as f:
    symbols = json.load(f)["symbols"]

# =====================
# 銘柄ごとに処理
# =====================
for s in symbols:
    code = s["code"]      # 例: 7203
    ticker = s["ticker"]  # 例: 7203.T

    print(f"\n=== Fetching {code} ({ticker}) ===")

    out_dir = BASE_DIR / code
    out_dir.mkdir(parents=True, exist_ok=True)

    # =====================
    # 5分足（直近3日）
    # =====================
    print("Fetching intraday 5m data...")

    intraday_df = yf.download(
        ticker,
        interval="5m",
        period="3d",
        progress=False
    )

    if intraday_df.empty:
        print("⚠ intraday data empty")
        continue

    intraday_df.columns = intraday_df.columns.get_level_values(0)

    idx = intraday_df.index
    if idx.tz is None:
        intraday_df.index = idx.tz_localize("UTC").tz_convert("Asia/Tokyo")
    else:
        intraday_df.index = idx.tz_convert("Asia/Tokyo")

    intraday_df = intraday_df.reset_index()

    intraday_data = []
    for _, row in intraday_df.iterrows():
        intraday_data.append({
            "time": row["Datetime"].strftime("%Y-%m-%d %H:%M"),
            "open": round(row["Open"], 2),
            "high": round(row["High"], 2),
            "low": round(row["Low"], 2),
            "close": round(row["Close"], 2),
            "volume": int(row["Volume"]),
        })

    with open(out_dir / "intraday_5m.json", "w", encoding="utf-8") as f:
        json.dump(intraday_data, f, ensure_ascii=False, indent=2)

    print("intraday_5m.json updated")

    # =====================
    # 日足（直近3年）
    # =====================
    print("Fetching daily data...")

    daily_df = yf.download(
        ticker,
        interval="1d",
        period="3y",
        progress=False
    )

    if daily_df.empty:
        print("⚠ daily data empty")
        continue

    daily_df.columns = daily_df.columns.get_level_values(0)

    idx = daily_df.index
    if idx.tz is None:
        daily_df.index = idx.tz_localize("UTC").tz_convert("Asia/Tokyo")
    else:
        daily_df.index = idx.tz_convert("Asia/Tokyo")

    daily_df = daily_df.reset_index()

    daily_data = []
    for _, row in daily_df.iterrows():
        daily_data.append({
            "date": row["Date"].strftime("%Y-%m-%d"),
            "open": round(row["Open"], 2),
            "high": round(row["High"], 2),
            "low": round(row["Low"], 2),
            "close": round(row["Close"], 2),
            "volume": int(row["Volume"]),
        })

    with open(out_dir / "daily.json", "w", encoding="utf-8") as f:
        json.dump(daily_data, f, ensure_ascii=False, indent=2)

    print("daily.json updated")

print("\n✅ Market data update completed")
