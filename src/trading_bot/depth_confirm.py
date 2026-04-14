import logging
from typing import TYPE_CHECKING, Dict, Optional

from trading_bot.config import BotConfig

if TYPE_CHECKING:
    from trading_bot.strategy import OpeningRange

logger = logging.getLogger("trading_bot.depth_confirm")


class Level2Confirm:
    def __init__(self, config: BotConfig) -> None:
        self.config = config
        self.last_depth: Optional[Dict] = None

    def validate_entry_side(self, opening_range: "OpeningRange", entry_price: float) -> bool:
        logger.info("Validating entry side using level 2 confirmation")
        if self.last_depth is None:
            logger.warning("No level 2 depth data available. Defaulting to accept trade.")
            return True
        if opening_range.direction == "long":
            return self._check_bid_support(entry_price)
        return self._check_ask_supply(entry_price)

    def _check_bid_support(self, entry_price: float) -> bool:
        bids = self.last_depth.get("bids", [])
        if not bids:
            logger.warning("No bid depth available")
            return False
        top_bid = bids[0][0]
        logger.debug("Top bid price=%.4f entry=%.4f", top_bid, entry_price)
        return top_bid >= entry_price

    def _check_ask_supply(self, entry_price: float) -> bool:
        asks = self.last_depth.get("asks", [])
        if not asks:
            logger.warning("No ask depth available")
            return False
        top_ask = asks[0][0]
        logger.debug("Top ask price=%.4f entry=%.4f", top_ask, entry_price)
        return top_ask <= entry_price

    def process_depth_update(self, depth_data: Dict) -> None:
        self.last_depth = depth_data
        logger.debug("Updated level 2 depth: %s", depth_data)
