import logging
import os
import signal
import sys
from typing import Optional

from trading_bot.config import BotConfig
from trading_bot.ib_client import IBManager
from trading_bot.strategy import TouchTurnStrategy
from trading_bot.execution import ExecutionManager
from trading_bot.depth_confirm import Level2Confirm

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("trading_bot")


def main() -> int:
    config = BotConfig.from_env()
    logger.info("Starting trading bot in %s mode", "paper" if config.paper_trade else "live")

    ib_manager = IBManager(config)
    execution = ExecutionManager(config, ib_manager)
    level2 = Level2Confirm(config)
    strategy = TouchTurnStrategy(config, level2)

    try:
        ib_manager.connect()
        strategy.initialize()
        strategy.execute_market_open_routine(execution)
        return 0
    except Exception as exc:
        logger.exception("Unhandled exception in trading bot: %s", exc)
        return 1
    finally:
        ib_manager.disconnect()


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
