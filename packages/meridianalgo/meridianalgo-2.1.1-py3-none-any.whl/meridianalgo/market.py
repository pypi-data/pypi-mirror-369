"""
Market data utilities and analysis tools
Enhanced market data functions for comprehensive analysis
"""

import pandas as pd
import numpy as np
import yfinance as yf
from typing import Dict, List, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

def get_market_data(symbols: List[str], period: str = "1y", interval: str = "1d") -> Dict[str, pd.DataFrame]:
    """
    Get market data for multiple symbols
    
    Args:
        symbols: List of stock symbols
        period: Data period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
        interval: Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
    
    Returns:
        Dictionary with DataFrames for each symbol
    """
    try:
        data = {}
        for symbol in symbols:
            try:
                ticker = yf.Ticker(symbol)
                df = ticker.history(period=period, interval=interval)
                if not df.empty:
                    data[symbol] = df
                else:
                    print(f"No data available for {symbol}")
            except Exception as e:
                print(f"Error fetching data for {symbol}: {e}")
        
        return data
    except Exception as e:
        print(f"Error in get_market_data: {e}")
        return {}

def get_economic_indicators() -> Dict[str, float]:
    """
    Get key economic indicators (simplified version)
    
    Returns:
        Dictionary with economic indicators
    """
    try:
        # In a real implementation, you would fetch from economic data APIs
        # This is a simplified version with mock data
        
        indicators = {
            'vix': 20.5,  # Volatility Index
            'dxy': 103.2,  # Dollar Index
            'ten_year_yield': 4.2,  # 10-Year Treasury Yield
            'fed_rate': 5.25,  # Federal Funds Rate
            'inflation_rate': 3.1,  # CPI Inflation Rate
            'unemployment_rate': 3.7,  # Unemployment Rate
            'gdp_growth': 2.4,  # GDP Growth Rate
        }
        
        # Try to get some real data
        try:
            # VIX
            vix = yf.Ticker("^VIX")
            vix_data = vix.history(period="1d")
            if not vix_data.empty:
                indicators['vix'] = vix_data['Close'].iloc[-1]
            
            # 10-Year Treasury
            tnx = yf.Ticker("^TNX")
            tnx_data = tnx.history(period="1d")
            if not tnx_data.empty:
                indicators['ten_year_yield'] = tnx_data['Close'].iloc[-1]
            
            # Dollar Index
            dxy = yf.Ticker("DX-Y.NYB")
            dxy_data = dxy.history(period="1d")
            if not dxy_data.empty:
                indicators['dxy'] = dxy_data['Close'].iloc[-1]
                
        except Exception:
            pass  # Use default values
        
        return indicators
    except Exception:
        return {
            'vix': 20.0,
            'dxy': 103.0,
            'ten_year_yield': 4.0,
            'fed_rate': 5.0,
            'inflation_rate': 3.0,
            'unemployment_rate': 3.5,
            'gdp_growth': 2.0
        }

def get_sector_performance(period: str = "1mo") -> Dict[str, Dict[str, float]]:
    """
    Get sector performance data
    
    Args:
        period: Performance period
    
    Returns:
        Dictionary with sector performance data
    """
    try:
        # Major sector ETFs
        sector_etfs = {
            'Technology': 'XLK',
            'Healthcare': 'XLV',
            'Financials': 'XLF',
            'Consumer Discretionary': 'XLY',
            'Communication Services': 'XLC',
            'Industrials': 'XLI',
            'Consumer Staples': 'XLP',
            'Energy': 'XLE',
            'Utilities': 'XLU',
            'Real Estate': 'XLRE',
            'Materials': 'XLB'
        }
        
        sector_performance = {}
        
        for sector, etf in sector_etfs.items():
            try:
                ticker = yf.Ticker(etf)
                data = ticker.history(period=period)
                
                if not data.empty and len(data) > 1:
                    start_price = data['Close'].iloc[0]
                    end_price = data['Close'].iloc[-1]
                    performance = ((end_price - start_price) / start_price) * 100
                    
                    sector_performance[sector] = {
                        'return': performance,
                        'current_price': end_price,
                        'volume': data['Volume'].iloc[-1],
                        'volatility': data['Close'].pct_change().std() * np.sqrt(252) * 100
                    }
                else:
                    sector_performance[sector] = {
                        'return': 0.0,
                        'current_price': 100.0,
                        'volume': 1000000,
                        'volatility': 15.0
                    }
            except Exception:
                sector_performance[sector] = {
                    'return': 0.0,
                    'current_price': 100.0,
                    'volume': 1000000,
                    'volatility': 15.0
                }
        
        return sector_performance
    except Exception:
        return {}

def get_market_news(symbols: List[str] = None) -> List[Dict[str, str]]:
    """
    Get market news (simplified version)
    
    Args:
        symbols: List of symbols to get news for (optional)
    
    Returns:
        List of news items
    """
    try:
        # In a real implementation, you would fetch from news APIs
        # This is a simplified mock version
        
        news_items = [
            {
                'title': 'Market Update: Stocks Rise on Economic Data',
                'summary': 'Major indices gained as economic indicators showed strength',
                'source': 'Market News',
                'timestamp': '2025-08-02 10:00:00',
                'sentiment': 'Positive'
            },
            {
                'title': 'Fed Officials Signal Cautious Approach',
                'summary': 'Federal Reserve officials indicate measured approach to policy',
                'source': 'Economic News',
                'timestamp': '2025-08-02 09:30:00',
                'sentiment': 'Neutral'
            },
            {
                'title': 'Tech Sector Shows Resilience',
                'summary': 'Technology stocks continue to outperform broader market',
                'source': 'Sector News',
                'timestamp': '2025-08-02 09:00:00',
                'sentiment': 'Positive'
            }
        ]
        
        return news_items
    except Exception:
        return []

def get_earnings_calendar(days_ahead: int = 7) -> List[Dict[str, str]]:
    """
    Get upcoming earnings calendar (simplified version)
    
    Args:
        days_ahead: Number of days to look ahead
    
    Returns:
        List of earnings events
    """
    try:
        # Mock earnings data - in practice, you'd fetch from financial APIs
        earnings_events = [
            {
                'symbol': 'AAPL',
                'company': 'Apple Inc.',
                'date': '2025-08-05',
                'time': 'After Market Close',
                'estimate': '$1.25',
                'previous': '$1.20'
            },
            {
                'symbol': 'MSFT',
                'company': 'Microsoft Corporation',
                'date': '2025-08-06',
                'time': 'After Market Close',
                'estimate': '$2.85',
                'previous': '$2.80'
            },
            {
                'symbol': 'GOOGL',
                'company': 'Alphabet Inc.',
                'date': '2025-08-07',
                'time': 'After Market Close',
                'estimate': '$1.45',
                'previous': '$1.40'
            }
        ]
        
        return earnings_events
    except Exception:
        return []

def get_dividend_calendar(days_ahead: int = 30) -> List[Dict[str, str]]:
    """
    Get upcoming dividend calendar (simplified version)
    
    Args:
        days_ahead: Number of days to look ahead
    
    Returns:
        List of dividend events
    """
    try:
        # Mock dividend data
        dividend_events = [
            {
                'symbol': 'AAPL',
                'company': 'Apple Inc.',
                'ex_date': '2025-08-10',
                'pay_date': '2025-08-15',
                'amount': '$0.25',
                'yield': '0.45%'
            },
            {
                'symbol': 'MSFT',
                'company': 'Microsoft Corporation',
                'ex_date': '2025-08-12',
                'pay_date': '2025-08-18',
                'amount': '$0.75',
                'yield': '0.68%'
            },
            {
                'symbol': 'JNJ',
                'company': 'Johnson & Johnson',
                'ex_date': '2025-08-15',
                'pay_date': '2025-08-22',
                'amount': '$1.19',
                'yield': '2.85%'
            }
        ]
        
        return dividend_events
    except Exception:
        return []

def compare_stocks(symbols: List[str], period: str = "1y") -> Dict[str, Dict[str, float]]:
    """
    Compare multiple stocks across various metrics
    
    Args:
        symbols: List of stock symbols to compare
        period: Period for comparison
    
    Returns:
        Dictionary with comparison metrics
    """
    try:
        comparison_data = {}
        
        for symbol in symbols:
            try:
                ticker = yf.Ticker(symbol)
                
                # Get price data
                hist_data = ticker.history(period=period)
                info = ticker.info
                
                if not hist_data.empty:
                    # Calculate metrics
                    start_price = hist_data['Close'].iloc[0]
                    end_price = hist_data['Close'].iloc[-1]
                    total_return = ((end_price - start_price) / start_price) * 100
                    
                    returns = hist_data['Close'].pct_change().dropna()
                    volatility = returns.std() * np.sqrt(252) * 100
                    
                    # Max drawdown
                    cumulative = (1 + returns).cumprod()
                    running_max = cumulative.expanding().max()
                    drawdown = (cumulative - running_max) / running_max
                    max_drawdown = drawdown.min() * 100
                    
                    # Sharpe ratio (assuming 2% risk-free rate)
                    excess_return = returns.mean() * 252 - 0.02
                    sharpe_ratio = excess_return / (volatility / 100) if volatility > 0 else 0
                    
                    comparison_data[symbol] = {
                        'total_return': total_return,
                        'volatility': volatility,
                        'max_drawdown': max_drawdown,
                        'sharpe_ratio': sharpe_ratio,
                        'current_price': end_price,
                        'market_cap': info.get('marketCap', 0),
                        'pe_ratio': info.get('trailingPE', 0),
                        'dividend_yield': info.get('dividendYield', 0) * 100 if info.get('dividendYield') else 0,
                        'beta': info.get('beta', 1.0)
                    }
                else:
                    comparison_data[symbol] = {
                        'total_return': 0.0,
                        'volatility': 20.0,
                        'max_drawdown': -10.0,
                        'sharpe_ratio': 0.0,
                        'current_price': 100.0,
                        'market_cap': 0,
                        'pe_ratio': 15.0,
                        'dividend_yield': 0.0,
                        'beta': 1.0
                    }
            except Exception as e:
                print(f"Error comparing {symbol}: {e}")
                comparison_data[symbol] = {
                    'total_return': 0.0,
                    'volatility': 20.0,
                    'max_drawdown': -10.0,
                    'sharpe_ratio': 0.0,
                    'current_price': 100.0,
                    'market_cap': 0,
                    'pe_ratio': 15.0,
                    'dividend_yield': 0.0,
                    'beta': 1.0
                }
        
        return comparison_data
    except Exception:
        return {}

def get_correlation_matrix(symbols: List[str], period: str = "1y") -> pd.DataFrame:
    """
    Get correlation matrix for a list of symbols
    
    Args:
        symbols: List of stock symbols
        period: Period for correlation calculation
    
    Returns:
        Correlation matrix as DataFrame
    """
    try:
        price_data = {}
        
        for symbol in symbols:
            try:
                ticker = yf.Ticker(symbol)
                data = ticker.history(period=period)
                if not data.empty:
                    price_data[symbol] = data['Close']
            except Exception:
                continue
        
        if price_data:
            df = pd.DataFrame(price_data)
            returns_df = df.pct_change().dropna()
            return returns_df.corr()
        else:
            return pd.DataFrame()
    except Exception:
        return pd.DataFrame()

def get_market_indices(period: str = "1d") -> Dict[str, Dict[str, float]]:
    """
    Get major market indices data
    
    Args:
        period: Data period
    
    Returns:
        Dictionary with index data
    """
    try:
        indices = {
            'S&P 500': '^GSPC',
            'Dow Jones': '^DJI',
            'NASDAQ': '^IXIC',
            'Russell 2000': '^RUT',
            'VIX': '^VIX'
        }
        
        index_data = {}
        
        for name, symbol in indices.items():
            try:
                ticker = yf.Ticker(symbol)
                data = ticker.history(period=period)
                
                if not data.empty:
                    current_price = data['Close'].iloc[-1]
                    if len(data) > 1:
                        prev_price = data['Close'].iloc[-2]
                        change = current_price - prev_price
                        change_pct = (change / prev_price) * 100
                    else:
                        change = 0
                        change_pct = 0
                    
                    index_data[name] = {
                        'price': current_price,
                        'change': change,
                        'change_pct': change_pct,
                        'volume': data['Volume'].iloc[-1] if 'Volume' in data.columns else 0
                    }
            except Exception:
                index_data[name] = {
                    'price': 4500.0 if 'S&P' in name else 35000.0 if 'Dow' in name else 14000.0,
                    'change': 0.0,
                    'change_pct': 0.0,
                    'volume': 0
                }
        
        return index_data
    except Exception:
        return {}

def analyze_market_sentiment() -> Dict[str, str]:
    """
    Analyze overall market sentiment
    
    Returns:
        Dictionary with sentiment analysis
    """
    try:
        # Get VIX for fear/greed indicator
        vix_data = yf.Ticker("^VIX").history(period="1d")
        vix_level = vix_data['Close'].iloc[-1] if not vix_data.empty else 20
        
        # Get major indices performance
        sp500_data = yf.Ticker("^GSPC").history(period="5d")
        sp500_change = 0
        if not sp500_data.empty and len(sp500_data) > 1:
            sp500_change = ((sp500_data['Close'].iloc[-1] - sp500_data['Close'].iloc[0]) / 
                           sp500_data['Close'].iloc[0]) * 100
        
        # Determine sentiment based on VIX and market performance
        if vix_level < 15 and sp500_change > 2:
            sentiment = "Very Bullish"
        elif vix_level < 20 and sp500_change > 0:
            sentiment = "Bullish"
        elif vix_level > 30 or sp500_change < -3:
            sentiment = "Bearish"
        elif vix_level > 25 or sp500_change < -1:
            sentiment = "Cautious"
        else:
            sentiment = "Neutral"
        
        # Fear & Greed level
        if vix_level < 12:
            fear_greed = "Extreme Greed"
        elif vix_level < 18:
            fear_greed = "Greed"
        elif vix_level < 25:
            fear_greed = "Neutral"
        elif vix_level < 35:
            fear_greed = "Fear"
        else:
            fear_greed = "Extreme Fear"
        
        return {
            'overall_sentiment': sentiment,
            'fear_greed_index': fear_greed,
            'vix_level': vix_level,
            'market_trend': 'Up' if sp500_change > 0 else 'Down',
            'confidence': 'High' if abs(sp500_change) > 1 else 'Medium'
        }
    except Exception:
        return {
            'overall_sentiment': 'Neutral',
            'fear_greed_index': 'Neutral',
            'vix_level': 20.0,
            'market_trend': 'Sideways',
            'confidence': 'Low'
        }