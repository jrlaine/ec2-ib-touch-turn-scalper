import logging
from dataclasses import dataclass
from typing import Optional

from trading_bot.config import BotConfig
from trading_bot.ib_client import IBManager

logger = logging.getLogger("trading_bot.execution")


@dataclass
class ExecutionManager:
    config: BotConfig
    ib_manager: IBManager

    def place_order(self, direction: str, entry_price: float, stop_price: float, target_price: float) -> Optional[int]:
        quantity = self._calculate_quantity(entry_price, stop_price)
        action = "BUY" if direction == "long" else "SELL"

        logger.info("Placing %s limit entry @ %.4f for %s contracts", action, entry_price, quantity)
        order_id = self.ib_manager.place_limit_order(action, quantity, entry_price)

        logger.info("Placing protective orders: stop=%.4f target=%.4f", stop_price, target_price)
        # TODO: implement bracket or contingent exit orders if desired.
        return order_id

    def _calculate_quantity(self, entry_price: float, stop_price: float) -> int:
        risk_per_share = abs(entry_price - stop_price)
        if risk_per_share <= 0:
            logger.warning("Invalid risk per share; defaulting to 1 contract")
            return 1
        max_risk = 100.0
        quantity = int(max_risk / risk_per_share)
        return max(1, quantity)
