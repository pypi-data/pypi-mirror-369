"""
Portfolio analysis and risk management tools
Enhanced functionality for portfolio optimization and performance tracking
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

class PortfolioAnalyzer:
    """
    Comprehensive portfolio analysis and optimization
    """
    
    def __init__(self, symbols: List[str], weights: Optional[List[float]] = None):
        self.symbols = symbols
        self.weights = weights or [1.0 / len(symbols)] * len(symbols)
        self.returns_data = None
        self.prices_data = None
    
    def load_data(self, data: Dict[str, pd.DataFrame]):
        """Load price data for portfolio symbols"""
        try:
            self.prices_data = {}
            self.returns_data = {}
            
            for symbol in self.symbols:
                if symbol in data:
                    self.prices_data[symbol] = data[symbol]['Close']
                    self.returns_data[symbol] = data[symbol]['Close'].pct_change().dropna()
        except Exception as e:
            print(f"Error loading portfolio data: {e}")
    
    def calculate_portfolio_metrics(self) -> Dict[str, float]:
        """Calculate comprehensive portfolio metrics"""
        try:
            if not self.returns_data:
                return {}
            
            # Combine returns into DataFrame
            returns_df = pd.DataFrame(self.returns_data)
            
            # Portfolio returns
            portfolio_returns = (returns_df * self.weights).sum(axis=1)
            
            # Basic metrics
            total_return = (1 + portfolio_returns).prod() - 1
            annualized_return = (1 + portfolio_returns.mean()) ** 252 - 1
            volatility = portfolio_returns.std() * np.sqrt(252)
            sharpe_ratio = annualized_return / volatility if volatility > 0 else 0
            
            # Risk metrics
            max_drawdown = self.calculate_max_drawdown(portfolio_returns)
            var_95 = np.percentile(portfolio_returns, 5)
            cvar_95 = portfolio_returns[portfolio_returns <= var_95].mean()
            
            return {
                'total_return': total_return,
                'annualized_return': annualized_return,
                'volatility': volatility,
                'sharpe_ratio': sharpe_ratio,
                'max_drawdown': max_drawdown,
                'var_95': var_95,
                'cvar_95': cvar_95,
                'calmar_ratio': annualized_return / abs(max_drawdown) if max_drawdown != 0 else 0
            }
        except Exception as e:
            print(f"Error calculating portfolio metrics: {e}")
            return {}
    
    def calculate_max_drawdown(self, returns: pd.Series) -> float:
        """Calculate maximum drawdown"""
        try:
            cumulative = (1 + returns).cumprod()
            running_max = cumulative.expanding().max()
            drawdown = (cumulative - running_max) / running_max
            return drawdown.min()
        except Exception:
            return 0.0
    
    def get_correlation_matrix(self) -> pd.DataFrame:
        """Get correlation matrix of portfolio assets"""
        try:
            if not self.returns_data:
                return pd.DataFrame()
            
            returns_df = pd.DataFrame(self.returns_data)
            return returns_df.corr()
        except Exception:
            return pd.DataFrame()
    
    def optimize_weights(self, target_return: Optional[float] = None) -> Dict[str, float]:
        """Optimize portfolio weights (simplified mean-variance optimization)"""
        try:
            if not self.returns_data:
                return dict(zip(self.symbols, self.weights))
            
            returns_df = pd.DataFrame(self.returns_data)
            mean_returns = returns_df.mean()
            cov_matrix = returns_df.cov()
            
            # Simple equal-risk contribution approach
            inv_vol = 1 / np.sqrt(np.diag(cov_matrix))
            weights = inv_vol / inv_vol.sum()
            
            return dict(zip(self.symbols, weights))
        except Exception:
            return dict(zip(self.symbols, self.weights))

class RiskManager:
    """
    Risk management and assessment tools
    """
    
    @staticmethod
    def calculate_var(returns: pd.Series, confidence_level: float = 0.95) -> float:
        """Calculate Value at Risk (VaR)"""
        try:
            return np.percentile(returns, (1 - confidence_level) * 100)
        except Exception:
            return 0.0
    
    @staticmethod
    def calculate_cvar(returns: pd.Series, confidence_level: float = 0.95) -> float:
        """Calculate Conditional Value at Risk (CVaR)"""
        try:
            var = RiskManager.calculate_var(returns, confidence_level)
            return returns[returns <= var].mean()
        except Exception:
            return 0.0
    
    @staticmethod
    def calculate_beta(stock_returns: pd.Series, market_returns: pd.Series) -> float:
        """Calculate beta relative to market"""
        try:
            covariance = np.cov(stock_returns, market_returns)[0][1]
            market_variance = np.var(market_returns)
            return covariance / market_variance if market_variance > 0 else 1.0
        except Exception:
            return 1.0
    
    @staticmethod
    def assess_risk_level(volatility: float, max_drawdown: float, beta: float) -> str:
        """Assess overall risk level"""
        try:
            risk_score = 0
            
            # Volatility component
            if volatility > 0.3:
                risk_score += 3
            elif volatility > 0.2:
                risk_score += 2
            elif volatility > 0.15:
                risk_score += 1
            
            # Drawdown component
            if abs(max_drawdown) > 0.3:
                risk_score += 3
            elif abs(max_drawdown) > 0.2:
                risk_score += 2
            elif abs(max_drawdown) > 0.1:
                risk_score += 1
            
            # Beta component
            if beta > 1.5:
                risk_score += 2
            elif beta > 1.2:
                risk_score += 1
            
            if risk_score >= 6:
                return "Very High"
            elif risk_score >= 4:
                return "High"
            elif risk_score >= 2:
                return "Medium"
            else:
                return "Low"
        except Exception:
            return "Unknown"

class PerformanceTracker:
    """
    Track and analyze investment performance
    """
    
    def __init__(self):
        self.trades = []
        self.positions = {}
    
    def add_trade(self, symbol: str, quantity: float, price: float, 
                  trade_type: str, timestamp: str):
        """Add a trade to the tracker"""
        try:
            trade = {
                'symbol': symbol,
                'quantity': quantity,
                'price': price,
                'type': trade_type,  # 'buy' or 'sell'
                'timestamp': timestamp,
                'value': quantity * price
            }
            self.trades.append(trade)
            
            # Update positions
            if symbol not in self.positions:
                self.positions[symbol] = {'quantity': 0, 'avg_price': 0}
            
            if trade_type == 'buy':
                old_value = self.positions[symbol]['quantity'] * self.positions[symbol]['avg_price']
                new_quantity = self.positions[symbol]['quantity'] + quantity
                new_value = old_value + trade['value']
                self.positions[symbol]['quantity'] = new_quantity
                self.positions[symbol]['avg_price'] = new_value / new_quantity if new_quantity > 0 else 0
            elif trade_type == 'sell':
                self.positions[symbol]['quantity'] -= quantity
                
        except Exception as e:
            print(f"Error adding trade: {e}")
    
    def calculate_realized_pnl(self) -> float:
        """Calculate realized profit and loss"""
        try:
            realized_pnl = 0
            temp_positions = {}
            
            for trade in self.trades:
                symbol = trade['symbol']
                if symbol not in temp_positions:
                    temp_positions[symbol] = []
                
                if trade['type'] == 'buy':
                    temp_positions[symbol].append({
                        'quantity': trade['quantity'],
                        'price': trade['price']
                    })
                elif trade['type'] == 'sell':
                    remaining_sell = trade['quantity']
                    while remaining_sell > 0 and temp_positions[symbol]:
                        buy_trade = temp_positions[symbol][0]
                        if buy_trade['quantity'] <= remaining_sell:
                            # Full position closed
                            pnl = buy_trade['quantity'] * (trade['price'] - buy_trade['price'])
                            realized_pnl += pnl
                            remaining_sell -= buy_trade['quantity']
                            temp_positions[symbol].pop(0)
                        else:
                            # Partial position closed
                            pnl = remaining_sell * (trade['price'] - buy_trade['price'])
                            realized_pnl += pnl
                            buy_trade['quantity'] -= remaining_sell
                            remaining_sell = 0
            
            return realized_pnl
        except Exception:
            return 0.0
    
    def get_performance_summary(self, current_prices: Dict[str, float]) -> Dict[str, float]:
        """Get comprehensive performance summary"""
        try:
            realized_pnl = self.calculate_realized_pnl()
            
            # Calculate unrealized PnL
            unrealized_pnl = 0
            total_invested = 0
            current_value = 0
            
            for symbol, position in self.positions.items():
                if position['quantity'] > 0:
                    invested = position['quantity'] * position['avg_price']
                    current = position['quantity'] * current_prices.get(symbol, position['avg_price'])
                    
                    total_invested += invested
                    current_value += current
                    unrealized_pnl += (current - invested)
            
            total_pnl = realized_pnl + unrealized_pnl
            total_return = (total_pnl / total_invested * 100) if total_invested > 0 else 0
            
            return {
                'realized_pnl': realized_pnl,
                'unrealized_pnl': unrealized_pnl,
                'total_pnl': total_pnl,
                'total_invested': total_invested,
                'current_value': current_value,
                'total_return_pct': total_return,
                'number_of_trades': len(self.trades),
                'active_positions': len([p for p in self.positions.values() if p['quantity'] > 0])
            }
        except Exception:
            return {}

# Utility functions
def calculate_sharpe_ratio(returns: pd.Series, risk_free_rate: float = 0.02) -> float:
    """Calculate Sharpe ratio"""
    try:
        excess_returns = returns.mean() * 252 - risk_free_rate
        volatility = returns.std() * np.sqrt(252)
        return excess_returns / volatility if volatility > 0 else 0
    except Exception:
        return 0.0

def calculate_max_drawdown(prices: pd.Series) -> float:
    """Calculate maximum drawdown from price series"""
    try:
        returns = prices.pct_change().dropna()
        cumulative = (1 + returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        return drawdown.min()
    except Exception:
        return 0.0

def calculate_beta(stock_returns: pd.Series, market_returns: pd.Series) -> float:
    """Calculate beta coefficient"""
    try:
        # Align the series
        aligned_data = pd.concat([stock_returns, market_returns], axis=1).dropna()
        if len(aligned_data) < 2:
            return 1.0
        
        stock_aligned = aligned_data.iloc[:, 0]
        market_aligned = aligned_data.iloc[:, 1]
        
        covariance = np.cov(stock_aligned, market_aligned)[0][1]
        market_variance = np.var(market_aligned)
        
        return covariance / market_variance if market_variance > 0 else 1.0
    except Exception:
        return 1.0

def optimize_portfolio(returns_data: Dict[str, pd.Series], 
                      target_return: Optional[float] = None) -> Dict[str, float]:
    """
    Optimize portfolio weights using mean-variance optimization
    
    Args:
        returns_data: Dictionary of return series for each asset
        target_return: Target return (optional)
    
    Returns:
        Dictionary with optimized weights
    """
    try:
        if not returns_data:
            return {}
        
        symbols = list(returns_data.keys())
        returns_df = pd.DataFrame(returns_data)
        
        # Calculate expected returns and covariance matrix
        expected_returns = returns_df.mean() * 252  # Annualized
        cov_matrix = returns_df.cov() * 252  # Annualized
        
        # Simple equal-risk contribution approach
        inv_vol = 1 / np.sqrt(np.diag(cov_matrix))
        weights = inv_vol / inv_vol.sum()
        
        return dict(zip(symbols, weights))
    except Exception:
        # Equal weights fallback
        symbols = list(returns_data.keys())
        equal_weight = 1.0 / len(symbols)
        return {symbol: equal_weight for symbol in symbols}

def backtest_strategy(prices_data: Dict[str, pd.Series], 
                     strategy_func, 
                     initial_capital: float = 10000) -> Dict[str, float]:
    """
    Backtest a trading strategy
    
    Args:
        prices_data: Dictionary of price series
        strategy_func: Function that returns buy/sell signals
        initial_capital: Starting capital
    
    Returns:
        Dictionary with backtest results
    """
    try:
        # This is a simplified backtest framework
        # In practice, you would implement more sophisticated backtesting
        
        portfolio_value = initial_capital
        positions = {}
        trades = 0
        
        # Simple buy-and-hold strategy as example
        symbols = list(prices_data.keys())
        weight_per_symbol = 1.0 / len(symbols)
        
        for symbol in symbols:
            if len(prices_data[symbol]) > 0:
                initial_price = prices_data[symbol].iloc[0]
                final_price = prices_data[symbol].iloc[-1]
                
                shares = (portfolio_value * weight_per_symbol) / initial_price
                final_value = shares * final_price
                
                positions[symbol] = {
                    'shares': shares,
                    'initial_value': portfolio_value * weight_per_symbol,
                    'final_value': final_value,
                    'return': (final_value / (portfolio_value * weight_per_symbol) - 1) * 100
                }
                trades += 1
        
        total_final_value = sum(pos['final_value'] for pos in positions.values())
        total_return = (total_final_value / initial_capital - 1) * 100
        
        return {
            'initial_capital': initial_capital,
            'final_value': total_final_value,
            'total_return': total_return,
            'number_of_trades': trades,
            'positions': positions
        }
    except Exception:
        return {
            'initial_capital': initial_capital,
            'final_value': initial_capital,
            'total_return': 0.0,
            'number_of_trades': 0,
            'positions': {}
        }