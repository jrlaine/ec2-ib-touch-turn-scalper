import logging
from dataclasses import dataclass
from typing import Dict, Optional

from trading_bot.config import BotConfig
from trading_bot.depth_confirm import Level2Confirm
from trading_bot.execution import ExecutionManager
from trading_bot.utils import calculate_atr, fib_level

logger = logging.getLogger("trading_bot.strategy")


@dataclass
class OpeningRange:
    high: float
    low: float
    size: float
    direction: str


class TouchTurnStrategy:
    def __init__(self, config: BotConfig, level2: Level2Confirm) -> None:
        self.config = config
        self.level2 = level2
        self.opening_range: Optional[OpeningRange] = None
        self.target_price: Optional[float] = None
        self.stop_price: Optional[float] = None
        self.entry_price: Optional[float] = None

    def initialize(self) -> None:
        logger.info("Initializing touch-and-turn strategy for %s", self.config.symbol)

    def execute_market_open_routine(self, execution: ExecutionManager) -> None:
        logger.info("Executing market open routine")
        bars = execution.ib_manager.request_15m_bars(duration="2 D")
        opening_bar = bars[-1]
        atr = calculate_atr(execution.ib_manager.request_daily_bars(duration="14 D"), self.config.atr_window)

        self.opening_range = self._build_opening_range(opening_bar)
        if not self._is_liquidity_candle(self.opening_range, atr):
            logger.warning("Opening range is not a liquidity candle. Skipping today.")
            return

        self.entry_price = self._entry_price(self.opening_range)
        self.target_price = self._profit_target(self.opening_range)
        self.stop_price = self._stop_loss(self.opening_range)

        logger.info(
            "Trade plan: entry=%.4f target=%.4f stop=%.4f direction=%s",
            self.entry_price,
            self.target_price,
            self.stop_price,
            self.opening_range.direction,
        )

        if not self.level2.validate_entry_side(self.opening_range, self.entry_price):
            logger.warning("Level 2 confirmation failed. No order placed.")
            return

        execution.place_order(self.opening_range.direction, self.entry_price, self.stop_price, self.target_price)

    def _build_opening_range(self, bar: Dict) -> OpeningRange:
        high = float(bar.high)
        low = float(bar.low)
        direction = "long" if bar.close < bar.open else "short"
        size = high - low
        return OpeningRange(high=high, low=low, size=size, direction=direction)

    def _is_liquidity_candle(self, opening_range: OpeningRange, atr: float) -> bool:
        threshold = atr * self.config.atr_threshold_pct
        logger.debug("ATR=%.4f threshold=%.4f range_size=%.4f", atr, threshold, opening_range.size)
        return opening_range.size >= threshold

    def _entry_price(self, opening_range: OpeningRange) -> float:
        return opening_range.low if opening_range.direction == "long" else opening_range.high

    def _profit_target(self, opening_range: OpeningRange) -> float:
        if opening_range.direction == "long":
            return fib_level(opening_range.high, opening_range.low, 0.382)
        return fib_level(opening_range.high, opening_range.low, 0.618)

    def _stop_loss(self, opening_range: OpeningRange) -> float:
        target = self._profit_target(opening_range)
        entry = self._entry_price(opening_range)
        distance = abs(target - entry)
        return entry - distance / self.config.target_ratio if opening_range.direction == "long" else entry + distance / self.config.target_ratio
