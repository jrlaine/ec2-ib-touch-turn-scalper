import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class BotConfig:
    ib_host: str
    ib_port: int
    ib_client_id: int
    symbol: str
    exchange: str
    currency: str
    paper_trade: bool
    atr_window: int
    atr_threshold_pct: float
    target_ratio: float
    max_trading_minutes: int

    @staticmethod
    def from_env() -> "BotConfig":
        return BotConfig(
            ib_host=os.getenv("IB_HOST", "127.0.0.1"),
            ib_port=int(os.getenv("IB_PORT", "4002")),
            ib_client_id=int(os.getenv("IB_CLIENT_ID", "101")),
            symbol=os.getenv("SYMBOL", "NFLX"),
            exchange=os.getenv("EXCHANGE", "SMART"),
            currency=os.getenv("CURRENCY", "USD"),
            paper_trade=os.getenv("PAPER_TRADE", "true").lower() in ("1", "true", "yes"),
            atr_window=int(os.getenv("ATR_WINDOW", "14")),
            atr_threshold_pct=float(os.getenv("ATR_THRESHOLD_PCT", "0.25")),
            target_ratio=float(os.getenv("TARGET_RATIO", "2.0")),
            max_trading_minutes=int(os.getenv("MAX_TRADING_MINUTES", "90")),
        )
