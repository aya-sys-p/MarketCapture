import json
from pathlib import Path


class Config:

    with open("settings.json", "r", encoding="utf-8") as f:
        config = json.load(f)

    history_days = config["history_days"]

    stock_db = Path(config["database"]["stock"])
    commodity_db = Path(config["database"]["commodity"])

    stock_output = Path(config["output"]["stock"])
    commodity_output = Path(config["output"]["commodity"])

    stock_symbols = config["stocks"]
    commodity_symbols = config["commodities"]