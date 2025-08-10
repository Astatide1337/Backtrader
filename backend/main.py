"""
FastAPI main application server.

This module implements the main FastAPI server with:
- RESTful API endpoints
- WebSocket connections for real-time data
- Service layer integration
- CORS configuration for frontend integration
"""

import asyncio
import logging
import sys
import os
import json
from contextlib import asynccontextmanager
from uuid import uuid4

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from backend.services.backtest_service import BacktestService
from backend.services.order_service import OrderService
from backend.services.market_data_service import MarketDataService
from backend.services.portfolio_service import PortfolioService
from backend.websocket.connection_manager import ConnectionManager
from backend.models.api_models import (
    BacktestRequest,
    BacktestResponse,
    OrderRequest,
    OrderResponse,
    PortfolioSnapshot,
    CustomStrategyRequest,
    CustomStrategyResponse,
    CustomStrategyListResponse,
    ValidationRequest,
    ValidationResponse,
    ErrorResponse,
    StrategySchemaV1
)
from backend.database import init_db, save_custom_strategy_db, get_custom_strategy_db, list_custom_strategies_db, delete_custom_strategy_db


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events for the FastAPI application."""
    # Startup
    logger.info("Starting FastAPI application...")
    
    # Initialize database
    init_db()
    
    # Initialize services
    app.state.backtest_service = BacktestService()
    app.state.order_service = OrderService()
    app.state.market_data_service = MarketDataService()
    app.state.portfolio_service = PortfolioService()
    app.state.connection_manager = ConnectionManager()
    
    # Start background tasks
    asyncio.create_task(market_data_broadcaster(app))
    asyncio.create_task(portfolio_broadcaster(app))
    
    yield
    
    # Shutdown
    logger.info("Shutting down FastAPI application...")


# Create FastAPI app
app = FastAPI(
    title="Backtrader API",
    description="RESTful API for backtesting and trading operations",
    version="2.0.0",
    lifespan=lifespan
)


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],  # Next.js default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "message": "Backtrader API is running"}


# Backtest endpoints
@app.post("/api/v1/backtest", response_model=BacktestResponse)
async def run_backtest(request: BacktestRequest):
    """Run a backtest with the specified parameters."""
    try:
        backtest_service = app.state.backtest_service
        result = await backtest_service.run_backtest(
            strategy_name=request.strategy_name,
            symbol=request.symbol,
            start_date=request.start_date,
            end_date=request.end_date,
            initial_capital=request.initial_capital,
            parameters=request.parameters
        )
        
        return BacktestResponse(**result)
    
    except Exception as e:
        logger.error(f"Backtest error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/backtest/{backtest_id}")
async def get_backtest_results(backtest_id: str):
    """Get backtest results by ID."""
    try:
        backtest_service = app.state.backtest_service
        result = await backtest_service.get_backtest_results(backtest_id)
        
        if not result:
            raise HTTPException(status_code=404, detail="Backtest not found")
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving backtest results: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/backtests")
async def list_backtests():
    """List all backtests."""
    try:
        backtest_service = app.state.backtest_service
        backtests = await backtest_service.list_backtests()
        return {"backtests": backtests}
    
    except Exception as e:
        logger.error(f"Error listing backtests: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/v1/backtest/{backtest_id}")
async def delete_backtest(backtest_id: str):
    """Delete a backtest by ID."""
    try:
        from backend.database import delete_backtest_db
        deleted = delete_backtest_db(backtest_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Backtest not found")
        # 204 No Content is conventional for delete success
        return JSONResponse(status_code=204, content=None)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting backtest {backtest_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Order management endpoints
@app.post("/api/v1/orders", response_model=OrderResponse)
async def create_order(request: OrderRequest):
    """Create a new order."""
    try:
        order_service = app.state.order_service
        order = await order_service.create_order(
            symbol=request.symbol,
            quantity=request.quantity,
            order_type=request.order_type,
            direction=request.direction,
            price=request.price
        )
        
        # Broadcast order update via WebSocket
        await broadcast_order_update(order.__dict__)
        
        return OrderResponse.from_order(order)
    
    except Exception as e:
        logger.error(f"Order creation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/orders")
async def list_orders():
    """List all orders."""
    try:
        order_service = app.state.order_service
        orders = await order_service.list_orders()
        return {"orders": [OrderResponse.from_order(order) for order in orders]}
    
    except Exception as e:
        logger.error(f"Error listing orders: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/orders/{order_id}")
async def get_order(order_id: str):
    """Get order by ID."""
    try:
        order_service = app.state.order_service
        order = await order_service.get_order(order_id)
        
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        return OrderResponse.from_order(order)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving order: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Portfolio endpoints
@app.get("/api/v1/portfolio")
async def get_portfolio():
    """Get current portfolio snapshot."""
    try:
        portfolio_service = app.state.portfolio_service
        portfolio = await portfolio_service.get_portfolio_snapshot()
        return portfolio
    
    except Exception as e:
        logger.error(f"Error retrieving portfolio: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Market data endpoints
@app.get("/api/v1/market-data/{symbol}")
async def get_market_data(symbol: str, timeframe: str = "1d", start_date: Optional[str] = None, end_date: Optional[str] = None):
    """Get market data for a symbol."""
    try:
        # If no dates are provided, fetch data for the last 150 days as a default.
        if not start_date or not end_date:
            from datetime import datetime, timedelta
            end_dt = datetime.now()
            start_dt = end_dt - timedelta(days=150)
            start_date = start_dt.strftime("%Y-%m-%d")
            end_date = end_dt.strftime("%Y-%m-%d")

        market_data_service = app.state.market_data_service
        data = await market_data_service.get_market_data(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            timeframe=timeframe
        )
        
        # Limit the data to the most recent 100 records for the UI
        return {"symbol": symbol, "data": data[-100:]}
    
    except Exception as e:
        logger.error(f"Error retrieving market data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/strategies")
async def list_strategies():
    """List available strategies."""
    try:
        backtest_service = app.state.backtest_service
        strategies = await backtest_service.list_strategies()
        return {"strategies": strategies}
    
    except Exception as e:
        logger.error(f"Error listing strategies: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Custom Strategy endpoints
@app.post("/api/v1/strategies/custom", response_model=CustomStrategyResponse)
async def create_custom_strategy(request: CustomStrategyRequest):
    """Create a new custom strategy."""
    try:
        strategy_id = str(uuid4())
        strategy_json = request.strategy.json()
        
        save_custom_strategy_db(strategy_id, request.status, strategy_json)
        
        return CustomStrategyResponse(
            id=strategy_id,
            status=request.status,
            created_at="",
            updated_at="",
            strategy=request.strategy
        )
    
    except Exception as e:
        logger.error(f"Error creating custom strategy: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/strategies/custom", response_model=CustomStrategyListResponse)
async def list_custom_strategies():
    """List all custom strategies."""
    try:
        strategies_db = list_custom_strategies_db()
        strategies = []
        
        for strategy_data in strategies_db:
            strategy_json = json.loads(strategy_data['strategy_json'])
            strategies.append(CustomStrategyResponse(
                id=strategy_data['id'],
                status=strategy_data['status'],
                created_at=strategy_data['created_at'],
                updated_at=strategy_data['updated_at'],
                strategy=StrategySchemaV1(**strategy_json)
            ))
        
        return CustomStrategyListResponse(strategies=strategies)
    
    except Exception as e:
        logger.error(f"Error listing custom strategies: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/strategies/custom/{strategy_id}", response_model=CustomStrategyResponse)
async def get_custom_strategy(strategy_id: str):
    """Get a specific custom strategy."""
    try:
        strategy_data = get_custom_strategy_db(strategy_id)
        
        if not strategy_data:
            raise HTTPException(status_code=404, detail="Custom strategy not found")
        
        strategy_json = json.loads(strategy_data['strategy_json'])
        
        return CustomStrategyResponse(
            id=strategy_data['id'],
            status=strategy_data['status'],
            created_at=strategy_data['created_at'],
            updated_at=strategy_data['updated_at'],
            strategy=StrategySchemaV1(**strategy_json)
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting custom strategy {strategy_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/v1/strategies/custom/{strategy_id}", response_model=CustomStrategyResponse)
async def update_custom_strategy(strategy_id: str, request: CustomStrategyRequest):
    """Update a custom strategy."""
    try:
        # Check if strategy exists
        existing_strategy = get_custom_strategy_db(strategy_id)
        if not existing_strategy:
            raise HTTPException(status_code=404, detail="Custom strategy not found")
        
        strategy_json = request.strategy.json()
        
        save_custom_strategy_db(strategy_id, request.status, strategy_json)
        
        return CustomStrategyResponse(
            id=strategy_id,
            status=request.status,
            created_at=existing_strategy['created_at'],
            updated_at=strategy_json,
            strategy=request.strategy
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating custom strategy {strategy_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/v1/strategies/custom/{strategy_id}")
async def delete_custom_strategy(strategy_id: str):
    """Delete a custom strategy."""
    try:
        deleted = delete_custom_strategy_db(strategy_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Custom strategy not found")
        
        return JSONResponse(status_code=204, content=None)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting custom strategy {strategy_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/strategies/custom/{strategy_id}/validate", response_model=ValidationResponse)
async def validate_custom_strategy(strategy_id: str, request: ValidationRequest):
    """Validate a custom strategy."""
    try:
        # Check if strategy exists
        strategy_data = get_custom_strategy_db(strategy_id)
        if not strategy_data:
            raise HTTPException(status_code=404, detail="Custom strategy not found")
        
        # Basic validation - check if strategy has required fields
        strategy_json = json.loads(strategy_data['strategy_json'])
        strategy = StrategySchemaV1(**strategy_json)
        
        notes = []
        
        # Validate basics
        if not strategy.basics.name or not strategy.basics.name.strip():
            notes.append("Strategy name is required")
        
        # Validate entry rules
        if not strategy.entry.groups or len(strategy.entry.groups) == 0:
            notes.append("At least one entry group is required")
        else:
            for i, group in enumerate(strategy.entry.groups):
                if not group.conditions or len(group.conditions) == 0:
                    notes.append(f"Entry group {i+1} must have at least one condition")
        
        # Validate indicators
        if not strategy.indicators or len(strategy.indicators) == 0:
            notes.append("At least one indicator is required")
        else:
            seen_ids = set()
            for indicator in strategy.indicators:
                if not indicator.id or not indicator.id.strip():
                    notes.append(f"Indicator {indicator.type} must have an ID")
                elif indicator.id in seen_ids:
                    notes.append(f"Duplicate indicator ID: {indicator.id}")
                else:
                    seen_ids.add(indicator.id)
        
        return ValidationResponse(
            ok=len(notes) == 0,
            notes=notes if notes else ["Validation passed"]
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error validating custom strategy {strategy_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time communication."""
    connection_manager = app.state.connection_manager
    await connection_manager.connect(websocket)
    
    try:
        while True:
            data = await websocket.receive_json()
            message_type = data.get("type")
            
            if message_type == "subscribe_market_data":
                await connection_manager.subscribe_to_market_data(websocket, data.get("symbol"))
            elif message_type == "unsubscribe_market_data":
                await connection_manager.unsubscribe_from_market_data(websocket, data.get("symbol"))
            elif message_type == "subscribe_portfolio":
                await connection_manager.subscribe_to_portfolio(websocket)
            elif message_type == "subscribe_orders":
                await connection_manager.subscribe_to_orders(websocket)
            elif message_type == "ping":
                await websocket.send_json({"type": "pong"})
    
    except WebSocketDisconnect:
        await connection_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        await connection_manager.disconnect(websocket)


# Background tasks
async def market_data_broadcaster(app: FastAPI):
    """Background task to broadcast market data updates."""
    market_data_service = app.state.market_data_service
    connection_manager = app.state.connection_manager
    
    async def broadcast_callback(symbol, trade_data):
        await connection_manager.broadcast_market_data(symbol, trade_data)

    # This will run forever
    await market_data_service.start_streaming(["AAPL", "GOOG"], broadcast_callback)

async def portfolio_broadcaster(app: FastAPI):
    """Background task to broadcast portfolio updates."""
    connection_manager = app.state.connection_manager
    portfolio_service = app.state.portfolio_service
    
    while True:
        try:
            portfolio_data = await portfolio_service.get_portfolio_snapshot()
            await connection_manager.broadcast_portfolio_update(portfolio_data)
            await asyncio.sleep(5) # Broadcast every 5 seconds
        except Exception as e:
            logger.error(f"Portfolio broadcaster error: {str(e)}")
            await asyncio.sleep(10)

async def broadcast_order_update(order_data: Dict):
    """Broadcast order updates to connected clients."""
    connection_manager = app.state.connection_manager
    await connection_manager.broadcast_order_update(order_data)


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
