import pandas as pd
import uuid
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
import logging
import numpy as np
import asyncio

class SlippageModel(Enum):
    """Slippage models."""
    FIXED = "fixed"
    PERCENTAGE = "percentage"
    VOLATILITY_ADJUSTED = "volatility_adjusted"

class OrderType(Enum):
    """Order types."""
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    VWAP = "vwap"
    TWAP = "twap"

class OrderStatus(Enum):
    """Order statuses."""
    PENDING = "pending"
    FILLED = "filled"
    CANCELLED = "cancelled"

class OrderDirection(Enum):
    """Order directions."""
    BUY = "buy"
    SELL = "sell"

class Order:
    """Represents a trading order."""
    def __init__(self, symbol: str, quantity: float, order_type: OrderType, direction: OrderDirection, price: Optional[float] = None, duration: Optional[int] = None):
        self.id = str(uuid.uuid4())
        self.symbol = symbol
        self.quantity = quantity
        self.order_type = order_type
        self.direction = direction
        self.price = price
        self.duration = duration
        self.status = OrderStatus.PENDING
        self.filled_price: Optional[float] = None
        self.filled_time: Optional[pd.Timestamp] = None
        self.commission = 0.0

    def to_dict(self):
        return {
            "id": self.id,
            "symbol": self.symbol,
            "quantity": self.quantity,
            "order_type": self.order_type.value,
            "direction": self.direction.value,
            "price": self.price,
            "duration": self.duration,
            "status": self.status.value,
            "filled_price": self.filled_price,
            "filled_time": self.filled_time,
            "commission": self.commission,
        }

class Position:
    """Represents a trading position."""
    def __init__(self, symbol: str, quantity: float, entry_price: float, entry_time: pd.Timestamp):
        self.id = str(uuid.uuid4())
        self.symbol = symbol
        self.quantity = quantity
        self.entry_price = entry_price
        self.entry_time = entry_time
        self.exit_price: Optional[float] = None
        self.exit_time: Optional[pd.Timestamp] = None
        self.commission = 0.0
        self.orders: List[Order] = []

    def is_open(self) -> bool:
        return self.exit_price is None

    def close(self, exit_price: float, exit_time: pd.Timestamp) -> None:
        self.exit_price = exit_price
        self.exit_time = exit_time

    def add_order(self, order: Order) -> None:
        self.orders.append(order)
        self.commission += order.commission

    def get_pnl(self) -> float:
        if self.is_open() or self.exit_price is None:
            return 0.0
        if self.quantity > 0:
            return (self.exit_price - self.entry_price) * self.quantity - self.commission
        else:
            return (self.entry_price - self.exit_price) * abs(self.quantity) - self.commission

    def get_return(self) -> float:
        if self.is_open() or self.exit_price is None:
            return 0.0
        if self.entry_price == 0:
            return 0.0
        if self.quantity > 0:
            return (self.exit_price - self.entry_price) / self.entry_price
        else:
            return (self.entry_price - self.exit_price) / self.entry_price

    def to_dict(self):
        return {
            "id": self.id,
            "symbol": self.symbol,
            "quantity": self.quantity,
            "entry_price": self.entry_price,
            "entry_time": self.entry_time,
            "exit_price": self.exit_price,
            "exit_time": self.exit_time,
            "commission": self.commission,
            "orders": [
                {
                    "id": o.id,
                    "symbol": o.symbol,
                    "quantity": o.quantity,
                    "order_type": o.order_type.value,
                    "direction": o.direction.value,
                    "price": o.price,
                    "duration": o.duration,
                    "status": o.status.value,
                    "filled_price": o.filled_price,
                    "filled_time": o.filled_time,
                    "commission": o.commission,
                }
                for o in self.orders
            ],
        }

class OrderManager:
    """Manage orders and positions with cash-aware accounting."""
    def __init__(self, commission: float = 0.001, slippage_model: SlippageModel = SlippageModel.PERCENTAGE, slippage: float = 0.0005, order_fill_delay_ms: int = 50):
        self.commission = commission
        self.slippage_model = slippage_model
        self.slippage = slippage
        self.order_fill_delay_ms = order_fill_delay_ms
        self.orders: Dict[str, Order] = {}
        self.positions: Dict[str, Position] = {}
        self.closed_positions: List[Position] = []
        self.logger = logging.getLogger(__name__)
        # Broker-like cash tracking (engine will initialize/own current capital; we expose helpers)
        self.cash: float = 0.0

    def create_order(self, symbol: str, quantity: float, order_type: OrderType, direction: OrderDirection, price: Optional[float] = None, duration: Optional[int] = None) -> Order:
        order = Order(symbol, quantity, order_type, direction, price, duration)
        self.orders[order.id] = order
        return order

    async def execute_order(self, order: Order, current_price: float, current_time: pd.Timestamp, data: Optional[pd.DataFrame] = None) -> Optional[Position]:
        if order.status != OrderStatus.PENDING:
            return None

        await asyncio.sleep(self.order_fill_delay_ms / 1000)

        execution_price = self._get_execution_price(order, current_price, current_time, data)
        if execution_price is None:
            return None

        # Slippage-adjusted execution used for accounting
        px = self._apply_slippage(order, execution_price, data)

        # Commission on executed notional
        comm = px * order.quantity * self.commission

        # Mark order as filled
        order.status = OrderStatus.FILLED
        order.filled_price = float(execution_price)  # benchmark price (pre-slippage) for reporting
        order.filled_time = current_time + pd.Timedelta(milliseconds=self.order_fill_delay_ms)
        order.commission = comm

        # Apply cash flow immediately (buy reduces cash; sell increases cash)
        cash_before = self.cash
        if order.direction == OrderDirection.BUY:
            self.cash -= (px * order.quantity + comm)
        else:
            self.cash += (px * order.quantity - comm)

        # Update positions (handles zero-cross and closures)
        position = self._update_position(order, px, order.filled_time)

        self.logger.debug(
            f"EXEC {order.direction.value} {order.symbol} qty={order.quantity} px={px:.4f} "
            f"comm={comm:.4f} cash:{cash_before:.2f}->{self.cash:.2f} "
            f"filled_time={order.filled_time}"
        )
        return position

    def _get_execution_price(self, order: Order, current_price: float, current_time: pd.Timestamp, data: Optional[pd.DataFrame] = None) -> Optional[float]:
        if order.order_type == OrderType.MARKET:
            return current_price
        elif order.order_type == OrderType.LIMIT:
            if order.price is None: return None
            if (order.direction == OrderDirection.BUY and current_price <= order.price) or (order.direction == OrderDirection.SELL and current_price >= order.price):
                return order.price
        elif order.order_type == OrderType.STOP:
            if order.price is None: return None
            if (order.direction == OrderDirection.BUY and current_price >= order.price) or (order.direction == OrderDirection.SELL and current_price <= order.price):
                return current_price
        elif order.order_type in [OrderType.VWAP, OrderType.TWAP]:
            if data is None or order.duration is None: return None
            # Select exactly the last 'duration' rows up to and including current_time to match tests
            # Fall back to label-based slicing if needed
            try:
                period_data = data.loc[:current_time].iloc[-order.duration:]
            except Exception:
                period_data = data.loc[current_time - pd.Timedelta(minutes=order.duration):current_time]
            if period_data.empty: return None
            if order.order_type == OrderType.VWAP:
                return float((period_data['close'] * period_data['volume']).sum() / period_data['volume'].sum())
            else:
                # Pure time-weighted average of 'close'
                return float(period_data['close'].mean())
        return None

    def _apply_slippage(self, order: Order, execution_price: float, data: Optional[pd.DataFrame] = None) -> float:
        if self.slippage_model == SlippageModel.FIXED:
            slippage_amount = self.slippage
        elif self.slippage_model == SlippageModel.PERCENTAGE:
            slippage_amount = execution_price * self.slippage
        elif self.slippage_model == SlippageModel.VOLATILITY_ADJUSTED:
            if data is None: return execution_price
            volatility = data['close'].pct_change().rolling(20).std().iloc[-1]
            slippage_amount = execution_price * volatility * self.slippage
        else:
            return execution_price

        return execution_price + slippage_amount if order.direction == OrderDirection.BUY else execution_price - slippage_amount

    def _update_position(self, order: Order, execution_price: float, current_time: pd.Timestamp) -> Optional[Position]:
        """Update/open/close positions ensuring no zero-qty positions persist."""
        open_position = next((p for p in self.positions.values() if p.is_open() and p.symbol == order.symbol), None)

        # Helper to attach order and commission to a position
        def _attach_order(pos: Position, ord: Order):
            pos.add_order(ord)

        if open_position is None:
            qty = order.quantity if order.direction == OrderDirection.BUY else -order.quantity
            if qty == 0:
                self.logger.debug("Skip opening zero-qty position")
                return None
            pos = Position(order.symbol, qty, execution_price, current_time)
            _attach_order(pos, order)
            self.positions[pos.id] = pos
            return pos

        # Modify existing
        delta = order.quantity if order.direction == OrderDirection.BUY else -order.quantity
        new_qty = open_position.quantity + delta

        _attach_order(open_position, order)

        # Zero-cross handling
        if np.sign(open_position.quantity) != np.sign(new_qty) and new_qty != 0:
            # Close old
            open_position.close(execution_price, current_time)
            self.closed_positions.append(open_position)
            # Open new with residual
            new_pos = Position(order.symbol, new_qty, execution_price, current_time)
            self.positions[new_pos.id] = new_pos
            self.logger.debug(
                f"ZERO-CROSS: closed {open_position.id} qty={open_position.quantity}, opened {new_pos.id} qty={new_pos.quantity}"
            )
            return new_pos
        elif new_qty == 0:
            # Close and do not open zero
            open_position.close(execution_price, current_time)
            self.closed_positions.append(open_position)
            self.logger.debug(f"CLOSE: closed {open_position.id} at {execution_price}")
            return None
        else:
            open_position.quantity = new_qty
            return open_position

    def get_open_positions(self) -> List[Position]:
        return [p for p in self.positions.values() if p.is_open()]

    def get_closed_positions(self) -> List[Position]:
        return self.closed_positions

    async def close_position(self, position_id: str, current_price: float, current_time: pd.Timestamp) -> Optional[Position]:
        position = self.positions.get(position_id)
        if not position or not position.is_open():
            return None
        direction = OrderDirection.SELL if position.quantity > 0 else OrderDirection.BUY
        order = self.create_order(position.symbol, abs(position.quantity), OrderType.MARKET, direction)
        closed_position = await self.execute_order(order, current_price, current_time)
        
        # The position is closed within _update_position, which is called by execute_order.
        # We return the original position object which is now marked as closed.
        if not position.is_open():
            return position
        return None
