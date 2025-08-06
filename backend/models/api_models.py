from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Union
from datetime import datetime


class BacktestRequest(BaseModel):
    strategy_name: str
    symbol: str
    start_date: Union[str, datetime]
    end_date: Union[str, datetime]
    initial_capital: Optional[float] = 10000
    parameters: Optional[Dict[str, Union[str, float, int]]] = {}


class BacktestResponse(BaseModel):
    backtest_id: str
    strategy_name: str
    symbol: str
    start_date: Union[str, datetime]
    end_date: Union[str, datetime]
    initial_capital: float
    final_capital: float
    equity_curve: List[Dict[str, Union[float, datetime]]]
    positions: List[Dict[str, Union[str, float, datetime]]]
    performance: Dict[str, float]


class OrderRequest(BaseModel):
    symbol: str
    quantity: float
    order_type: str
    direction: str
    price: Optional[float]


class OrderResponse(BaseModel):
    order_id: str
    symbol: str
    quantity: float
    order_type: str
    direction: str
    price: Optional[float]
    status: str

    @staticmethod
    def from_order(order) -> "OrderResponse":
        return OrderResponse(
            order_id=order.id,
            symbol=order.symbol,
            quantity=order.quantity,
            order_type=order.order_type,
            direction=order.direction,
            price=order.price,
            status=order.status
        )


class PortfolioSnapshot(BaseModel):
    timestamp: datetime
    equity: float
    available_cash: float
    positions: List[Dict[str, Union[str, float]]]

