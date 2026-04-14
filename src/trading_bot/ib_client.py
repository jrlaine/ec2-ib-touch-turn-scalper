import logging
from typing import Dict, List, Optional

from ib_insync import IB, Contract, MarketOrder, LimitOrder, Stock, util

from trading_bot.config import BotConfig

logger = logging.getLogger("trading_bot.ib_client")


class IBManager:
    def __init__(self, config: BotConfig) -> None:
        self.config = config
        self.ib = IB()
        self.contract: Optional[Contract] = None

    def connect(self) -> None:
        logger.info("Connecting to IB Gateway at %s:%s", self.config.ib_host, self.config.ib_port)
        self.ib.connect(self.config.ib_host, self.config.ib_port, clientId=self.config.ib_client_id)
        self.contract = Stock(self.config.symbol, self.config.exchange, self.config.currency)
        self.ib.qualifyContracts(self.contract)
        logger.info("Connected and qualified contract %s", self.contract.symbol)

    def disconnect(self) -> None:
        if self.ib.isConnected():
            logger.info("Disconnecting from IB Gateway")
            self.ib.disconnect()

    def request_daily_bars(self, duration: str = "14 D") -> List[Dict]:
        assert self.contract is not None
        bars = self.ib.reqHistoricalData(
            self.contract,
            endDateTime="",
            durationStr=duration,
            barSizeSetting="1 day",
            whatToShow="TRADES",
            useRTH=True,
            formatDate=1,
        )
        return [bar for bar in bars]

    def request_15m_bars(self, duration: str = "2 D") -> List[Dict]:
        assert self.contract is not None
        bars = self.ib.reqHistoricalData(
            self.contract,
            endDateTime="",
            durationStr=duration,
            barSizeSetting="15 mins",
            whatToShow="TRADES",
            useRTH=True,
            formatDate=1,
        )
        return [bar for bar in bars]

    def subscribe_level2(self, depth_callback) -> None:
        assert self.contract is not None
        logger.info("Subscribing to level 2 market depth for %s", self.contract.symbol)
        self.ib.reqMktDepth(self.contract, numRows=10, isSmartDepth=True)
        self.ib.pendingTickersEvent += depth_callback

    def place_limit_order(self, action: str, quantity: int, limit_price: float) -> str:
        assert self.contract is not None
        order = LimitOrder(action=action, totalQuantity=quantity, lmtPrice=limit_price)
        trade = self.ib.placeOrder(self.contract, order)
        logger.info("Placed limit order %s %s %s @ %.4f", trade.order.action, trade.order.totalQuantity, self.contract.symbol, limit_price)
        return trade.order.orderId

    def place_stop_limit_order(self, action: str, quantity: int, stop_price: float, limit_price: float) -> str:
        raise NotImplementedError("Stop-limit order implementation pending")

    def place_market_order(self, action: str, quantity: int) -> str:
        assert self.contract is not None
        order = MarketOrder(action=action, totalQuantity=quantity)
        trade = self.ib.placeOrder(self.contract, order)
        logger.info("Placed market order %s %s %s", trade.order.action, trade.order.totalQuantity, self.contract.symbol)
        return trade.order.orderId
