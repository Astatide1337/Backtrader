import pandas as pd
import numpy as np
import itertools
from typing import Dict, List, Optional, Tuple, Any, Union, Callable
from datetime import datetime
import logging
from concurrent.futures import ProcessPoolExecutor, as_completed
import os

from src.engine import BacktestEngine
from src.config import Config
from src.strategy_manager import StrategyManager

class BasicOptimizer:
    """Basic grid search optimizer for strategy parameters."""
    
    def __init__(self, config: Optional[Config] = None,
                 metric: str = 'sharpe_ratio',
                 maximize: bool = True,
                 n_jobs: int = 1,
                 strategy_manager: Optional[StrategyManager] = None):
        """
        Initialize the optimizer.
        
        Args:
            config: Configuration object
            metric: Performance metric to optimize (default: 'sharpe_ratio')
            maximize: Whether to maximize the metric (default: True)
            n_jobs: Number of parallel jobs (default: 1)
            strategy_manager: Optional custom strategy manager
        """
        self.config = config or Config()
        self.metric = metric
        self.maximize = maximize
        self.n_jobs = n_jobs
        self.strategy_manager = strategy_manager
        self.logger = logging.getLogger(__name__)
        self.engine = BacktestEngine(self.config, strategy_manager)

    def grid_search(self,
                    strategy_name: str,
                    symbol: str,
                    start_date: Union[str, datetime],
                    end_date: Union[str, datetime],
                    param_grid: Dict[str, List[Any]]) -> Dict[str, Any]:
        """
        Synchronous grid search wrapper to satisfy tests.
        Internally executes async backtests and returns a dict result.
        """
        # Generate all parameter combinations
        param_names = list(param_grid.keys())
        param_values = list(param_grid.values())
        param_combinations = list(itertools.product(*param_values))

        self.logger.info(f"Starting grid search with {len(param_combinations)} parameter combinations")

        # Sequential execution for determinism in tests
        results = []
        import asyncio

        for i, combination in enumerate(param_combinations):
            params = dict(zip(param_names, combination))
            self.logger.info(f"Testing combination {i+1}/{len(param_combinations)}: {params}")

            # Run async engine.run_backtest in a synchronous context
            async def _run_once():
                engine = BacktestEngine(self.config, self.strategy_manager)
                return await engine.run_backtest(strategy_name, symbol, start_date, end_date, **params)

            try:
                res = asyncio.run(_run_once())
            except RuntimeError:
                # In case already inside a running loop (unlikely in these tests), use a new loop
                loop = asyncio.new_event_loop()
                try:
                    asyncio.set_event_loop(loop)
                    res = loop.run_until_complete(_run_once())
                finally:
                    loop.close()
                    asyncio.set_event_loop(None)

            score = res.get('performance', {}).get(self.metric, 0)

            results.append({
                'params': params,
                'score': score,
                'metrics': res.get('performance', {}),
                'final_capital': res.get('final_capital', 0)
            })

        best_result = self._find_best_result(results) if results else {}

        return {
            'best_params': best_result.get('params', {}),
            'best_score': best_result.get('score', 0),
            'best_metrics': best_result.get('metrics', {}),
            'all_results': results
        }
    
    async def _run_sequential_backtests(self, 
                                 strategy_name: str, 
                                 symbol: str, 
                                 start_date: Union[str, datetime], 
                                 end_date: Union[str, datetime],
                                 param_names: List[str], 
                                 param_combinations: List[Tuple]) -> List[Dict[str, Any]]:
        """
        Run backtests sequentially for each parameter combination.
        
        Args:
            strategy_name: Name of the strategy to optimize
            symbol: Symbol to test
            start_date: Start date
            end_date: End date
            param_names: List of parameter names
            param_combinations: List of parameter value combinations
            
        Returns:
            List of results for each parameter combination
        """
        results = []
        
        for i, combination in enumerate(param_combinations):
            # Create parameter dictionary
            params = dict(zip(param_names, combination))
            
            self.logger.info(f"Testing combination {i+1}/{len(param_combinations)}: {params}")
            
            # Run backtest
            engine = BacktestEngine(self.config, self.strategy_manager)
            result = await engine.run_backtest(strategy_name, symbol, start_date, end_date, **params)
            
            # Extract score
            score = result.get('performance', {}).get(self.metric, 0)
            
            # Store result
            results.append({
                'params': params,
                'score': score,
                'metrics': result.get('performance', {}),
                'final_capital': result.get('final_capital', 0)
            })
        
        return results
    
    async def _run_parallel_backtests(self, 
                               strategy_name: str, 
                               symbol: str, 
                               start_date: Union[str, datetime], 
                               end_date: Union[str, datetime],
                               param_names: List[str], 
                               param_combinations: List[Tuple]) -> List[Dict[str, Any]]:
        """
        Run backtests in parallel for each parameter combination.
        
        Args:
            strategy_name: Name of the strategy to optimize
            symbol: Symbol to test
            start_date: Start date
            end_date: End date
            param_names: List of parameter names
            param_combinations: List of parameter value combinations
            
        Returns:
            List of results for each parameter combination
        """
        results = []
        
        # Create a function to run a single backtest
        async def run_single_backtest(combination):
            # Create parameter dictionary
            params = dict(zip(param_names, combination))
            
            # Run backtest
            engine = BacktestEngine(self.config)
            result = await engine.run_backtest(strategy_name, symbol, start_date, end_date, **params)
            
            # Extract score
            score = result.get('performance', {}).get(self.metric, 0)
            
            # Return result
            return {
                'params': params,
                'score': score,
                'metrics': result.get('performance', {}),
                'final_capital': result.get('final_capital', 0)
            }
        
        # Run backtests in parallel
        with ProcessPoolExecutor(max_workers=self.n_jobs) as executor:
            # Submit all tasks
            futures = [executor.submit(run_single_backtest, combination) 
                      for combination in param_combinations]
            
            # Collect results as they complete
            for i, future in enumerate(as_completed(futures)):
                try:
                    result = future.result()
                    results.append(result)
                    self.logger.info(f"Completed combination {i+1}/{len(param_combinations)}: {result['params']}") # type: ignore
                except Exception as e:
                    self.logger.error(f"Error in backtest: {e}")
        
        return results
    
    def _find_best_result(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Find the best result from all backtest results.
        
        Args:
            results: List of backtest results
            
        Returns:
            Best result
        """
        if not results:
            return {}
        
        # Sort results by score
        sorted_results = sorted(results, key=lambda x: x['score'], reverse=self.maximize)
        
        return sorted_results[0]
    
    def generate_optimization_report(self, optimization_results: Dict[str, Any]) -> str:
        """
        Generate a text-based optimization report.
        
        Args:
            optimization_results: Results from grid search
            
        Returns:
            Formatted optimization report
        """
        if not optimization_results:
            return "No optimization results to report."
        
        best_params = optimization_results.get('best_params', {})
        best_score = optimization_results.get('best_score', 0)
        best_metrics = optimization_results.get('best_metrics', {})
        all_results = optimization_results.get('all_results', [])
        
        # Format report
        report = f"""
=== OPTIMIZATION RESULTS ===

Optimization Metric: {self.metric} ({'Maximize' if self.maximize else 'Minimize'})
Total Combinations Tested: {len(all_results)}

=== BEST PARAMETERS ===
"""
        
        for param, value in best_params.items():
            report += f"{param}: {value}\n"
        
        report += f"\nBest {self.metric} Score: {best_score:.4f}\n\n"
        
        report += "=== BEST PERFORMANCE METRICS ===\n"
        for metric, value in best_metrics.items():
            if isinstance(value, float):
                report += f"{metric}: {value:.4f}\n"
            else:
                report += f"{metric}: {value}\n"
        
        # Top 5 results
        report += "\n=== TOP 5 RESULTS ===\n"
        sorted_results = sorted(all_results, key=lambda x: x['score'], reverse=self.maximize)
        
        for i, result in enumerate(sorted_results[:5]):
            report += f"\nRank {i+1} (Score: {result['score']:.4f}):\n"
            for param, value in result['params'].items():
                report += f"  {param}: {value}\n"
            report += f"  Final Capital: ${result['final_capital']:.2f}\n"
        
        return report