
import datetime
import sqlite3
import json
import logging
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np
from order_manager import Position

DATABASE_URL = "./backtrader.db"

logger = logging.getLogger(__name__)

def get_db_connection():
    """Get a database connection."""
    conn = sqlite3.connect(DATABASE_URL)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database and create tables if they don't exist."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Create backtests table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS backtests (
                id TEXT PRIMARY KEY,
                strategy_name TEXT NOT NULL,
                symbol TEXT NOT NULL,
                start_date TEXT NOT NULL,
                end_date TEXT NOT NULL,
                initial_capital REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                results_json TEXT
            )
        """)
        
        conn.commit()
        conn.close()
        logger.info("Database initialized successfully.")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")

def save_backtest_result_db(backtest_id: str, result: Dict[str, Any]):
    """Save a backtest result to the database."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # A helper to convert non-serializable objects
        def default_serializer(o):
            if isinstance(o, (datetime.datetime, pd.Timestamp)):
                return o.isoformat()
            if isinstance(o, Position):
                return o.__dict__ # Simple serialization for now
            if isinstance(o, np.integer):
                return int(o)
            if isinstance(o, np.floating):
                return float(o)
            if isinstance(o, np.ndarray):
                return o.tolist()
            raise TypeError(f"Object of type {o.__class__.__name__} is not JSON serializable")

        results_json = json.dumps(result, default=default_serializer)

        cursor.execute("""
            INSERT INTO backtests (id, strategy_name, symbol, start_date, end_date, initial_capital, results_json)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            backtest_id,
            result.get('strategy_name'),
            result.get('symbol'),
            str(result.get('start_date')),
            str(result.get('end_date')),
            result.get('initial_capital'),
            results_json
        ))
        
        conn.commit()
        conn.close()
        logger.info(f"Backtest result {backtest_id} saved to database.")
    except Exception as e:
        logger.error(f"Error saving backtest result {backtest_id} to database: {e}")

def get_backtest_result_db(backtest_id: str) -> Optional[Dict[str, Any]]:
    """Get a backtest result from the database."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT results_json FROM backtests WHERE id = ?", (backtest_id,))
        row = cursor.fetchone()
        
        conn.close()
        
        if row:
            return json.loads(row['results_json'])
        return None
    except Exception as e:
        logger.error(f"Error getting backtest result {backtest_id} from database: {e}")
        return None

def list_backtests_db() -> List[Dict[str, Any]]:
    """List all backtests from the database."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, strategy_name, symbol, start_date, end_date, initial_capital, created_at FROM backtests ORDER BY created_at DESC")
        rows = cursor.fetchall()
        
        conn.close()
        
        return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Error listing backtests from database: {e}")
        return []

def delete_backtest_db(backtest_id: str) -> bool:
    """Delete a backtest from the database."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM backtests WHERE id = ?", (backtest_id,))
        
        conn.commit()
        deleted_rows = cursor.rowcount
        conn.close()
        
        return deleted_rows > 0
    except Exception as e:
        logger.error(f"Error deleting backtest {backtest_id} from database: {e}")
        return False
