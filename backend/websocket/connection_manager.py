"""
WebSocket connection manager.

Manages WebSocket connections, subscriptions, and real-time data broadcasting.
"""

import json
import logging
from typing import Dict, List, Set
from fastapi import WebSocket, WebSocketDisconnect
from datetime import datetime


logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections and subscriptions."""
    
    def __init__(self):
        """Initialize the connection manager."""
        self.active_connections: List[WebSocket] = []
        self.market_data_subscriptions: Dict[str, Set[WebSocket]] = {}
        self.portfolio_subscriptions: Set[WebSocket] = set()
        self.order_subscriptions: Set[WebSocket] = set()
    
    async def connect(self, websocket: WebSocket):
        """Accept a new WebSocket connection."""
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")
    
    async def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection."""
        self.active_connections.remove(websocket)
        await self._cleanup_subscriptions(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")
    
    async def send_personal_message(self, websocket: WebSocket, message: Dict):
        """Send a message to a specific WebSocket connection."""
        try:
            await websocket.send_json(message)
        except WebSocketDisconnect:
            await self.disconnect(websocket)
    
    async def broadcast(self, message: Dict):
        """Broadcast a message to all connected clients."""
        for connection in self.active_connections:
            await self.send_personal_message(connection, message)

    async def subscribe_to_market_data(self, websocket: WebSocket, symbol: str):
        """Subscribe a WebSocket to market data for a symbol."""
        if symbol not in self.market_data_subscriptions:
            self.market_data_subscriptions[symbol] = set()
        self.market_data_subscriptions[symbol].add(websocket)
        logger.info(f"WebSocket subscribed to market data for {symbol}")

    async def unsubscribe_from_market_data(self, websocket: WebSocket, symbol: str):
        """Unsubscribe a WebSocket from market data for a symbol."""
        if symbol in self.market_data_subscriptions:
            self.market_data_subscriptions[symbol].discard(websocket)
            if not self.market_data_subscriptions[symbol]:
                del self.market_data_subscriptions[symbol]
        logger.info(f"WebSocket unsubscribed from market data for {symbol}")

    async def broadcast_market_data(self, symbol: str, data: Dict):
        """Broadcast market data to subscribed clients."""
        if symbol in self.market_data_subscriptions:
            message = {
                'type': 'market_data_update',
                'symbol': symbol,
                'data': data,
                'timestamp': datetime.now().isoformat()
            }
            for websocket in self.market_data_subscriptions[symbol]:
                await self.send_personal_message(websocket, message)

    async def subscribe_to_portfolio(self, websocket: WebSocket):
        """Subscribe a WebSocket to portfolio updates."""
        self.portfolio_subscriptions.add(websocket)
        logger.info("WebSocket subscribed to portfolio updates")

    async def broadcast_portfolio_update(self, portfolio_data: Dict):
        """Broadcast portfolio updates to subscribed clients."""
        message = {
            'type': 'portfolio_update',
            'data': portfolio_data,
            'timestamp': datetime.now().isoformat()
        }
        for websocket in self.portfolio_subscriptions:
            await self.send_personal_message(websocket, message)

    async def subscribe_to_orders(self, websocket: WebSocket):
        """Subscribe a WebSocket to order updates."""
        self.order_subscriptions.add(websocket)
        logger.info("WebSocket subscribed to order updates")

    async def broadcast_order_update(self, order_data: Dict):
        """Broadcast order updates to subscribed clients."""
        message = {
            'type': 'order_update',
            'data': order_data,
            'timestamp': datetime.now().isoformat()
        }
        for websocket in self.order_subscriptions:
            await self.send_personal_message(websocket, message)

    def get_subscribed_symbols(self) -> List[str]:
        """Get all symbols that have active subscriptions."""
        return list(self.market_data_subscriptions.keys())

    async def _cleanup_subscriptions(self, websocket: WebSocket):
        """Clean up all subscriptions for a disconnected WebSocket."""
        for symbol in list(self.market_data_subscriptions.keys()):
            self.market_data_subscriptions[symbol].discard(websocket)
            if not self.market_data_subscriptions[symbol]:
                del self.market_data_subscriptions[symbol]
        self.portfolio_subscriptions.discard(websocket)
        self.order_subscriptions.discard(websocket)