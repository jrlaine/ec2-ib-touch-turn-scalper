import logging
from typing import Dict, List

logger = logging.getLogger("trading_bot.utils")


def calculate_atr(bars: List[Dict], window: int = 14) -> float:
    if len(bars) < window:
        raise ValueError("Not enough bars to calculate ATR")

    high_low = [float(bar.high) - float(bar.low) for bar in bars[-window:]]
    tr_values = []
    for i in range(1, len(bars[-window:])):
        prev_close = float(bars[-window:][i - 1].close)
        current_bar = bars[-window:][i]
        high = float(current_bar.high)
        low = float(current_bar.low)
        tr = max(high - low, abs(high - prev_close), abs(low - prev_close))
        tr_values.append(tr)

    atr = sum(tr_values) / len(tr_values)
    logger.debug("Calculated ATR=%.4f", atr)
    return atr


def fib_level(high: float, low: float, ratio: float) -> float:
    return high - (high - low) * ratio
