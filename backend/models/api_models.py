from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Union, Any
from datetime import datetime
import json


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


# Custom Strategy models
class StrategyBasics(BaseModel):
    name: str
    description: Optional[str] = None
    tags: Optional[List[str]] = []


class IndicatorParam(BaseModel):
    key: str
    value: Union[int, float, str, bool]


class IndicatorSpec(BaseModel):
    id: str
    type: str
    params: Optional[List[IndicatorParam]] = []
    source: Optional[Dict[str, Any]] = None
    timeframe: Optional[str] = None


class Operand(BaseModel):
    kind: str
    value: Optional[Union[int, float, str, bool]] = None
    ref: Optional[str] = None
    field: Optional[str] = None
    expr: Optional[str] = None


class Condition(BaseModel):
    left: Operand
    op: str
    right: Operand


class ConditionGroup(BaseModel):
    op: str
    conditions: List[Condition]


class EntryRules(BaseModel):
    side: str
    groups: List[ConditionGroup]


class ExitRules(BaseModel):
    side: str
    groups: List[ConditionGroup]


class RiskControls(BaseModel):
    maxPositions: Optional[int] = None
    stopLossPct: Optional[float] = None
    takeProfitPct: Optional[float] = None
    trailingStopPct: Optional[float] = None


class SizingConfig(BaseModel):
    mode: str
    params: Optional[Dict[str, Union[int, float, str]]] = {}
    risk: Optional[RiskControls] = None


class AdvancedExpression(BaseModel):
    id: str
    expr: str


class StrategySchemaV1(BaseModel):
    version: str
    basics: StrategyBasics
    indicators: List[IndicatorSpec]
    entry: EntryRules
    exit: Optional[ExitRules] = None
    sizing: SizingConfig
    advanced: Optional[Dict[str, Any]] = None


class CustomStrategyRequest(BaseModel):
    status: str
    strategy: StrategySchemaV1


class CustomStrategyResponse(BaseModel):
    id: str
    status: str
    created_at: str
    updated_at: str
    strategy: StrategySchemaV1


class CustomStrategyListResponse(BaseModel):
    strategies: List[CustomStrategyResponse]


class ValidationRequest(BaseModel):
    options: Optional[Dict[str, Any]] = {}


class ValidationResponse(BaseModel):
    ok: bool
    notes: List[str]


class ErrorResponse(BaseModel):
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None

