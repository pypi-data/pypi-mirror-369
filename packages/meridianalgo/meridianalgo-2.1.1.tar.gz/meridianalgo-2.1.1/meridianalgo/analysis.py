"""
Advanced technical analysis functions and indicators
Enhanced from previous MeridianAlgo versions with additional functionality
"""

import pandas as pd
import numpy as np
from typing import Tuple, List, Dict, Optional
import warnings
warnings.filterwarnings('ignore')

def calculate_rsi(prices: pd.Series, period: int = 14) -> pd.Series:
    """
    Calculate Relative Strength Index (RSI)
    
    Args:
        prices: Price series (typically closing prices)
        period: RSI period (default: 14)
    
    Returns:
        RSI values as pandas Series
    """
    try:
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.fillna(50)
    except Exception:
        return pd.Series([50] * len(prices), index=prices.index)

def calculate_macd(prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict[str, pd.Series]:
    """
    Calculate MACD (Moving Average Convergence Divergence)
    
    Args:
        prices: Price series
        fast: Fast EMA period (default: 12)
        slow: Slow EMA period (default: 26)
        signal: Signal line EMA period (default: 9)
    
    Returns:
        Dictionary with MACD, Signal, and Histogram
    """
    try:
        ema_fast = prices.ewm(span=fast).mean()
        ema_slow = prices.ewm(span=slow).mean()
        macd = ema_fast - ema_slow
        signal_line = macd.ewm(span=signal).mean()
        histogram = macd - signal_line
        
        return {
            'MACD': macd,
            'Signal': signal_line,
            'Histogram': histogram
        }
    except Exception:
        return {
            'MACD': pd.Series([0] * len(prices), index=prices.index),
            'Signal': pd.Series([0] * len(prices), index=prices.index),
            'Histogram': pd.Series([0] * len(prices), index=prices.index)
        }

def calculate_bollinger_bands(prices: pd.Series, period: int = 20, std_dev: float = 2) -> Dict[str, pd.Series]:
    """
    Calculate Bollinger Bands
    
    Args:
        prices: Price series
        period: Moving average period (default: 20)
        std_dev: Standard deviation multiplier (default: 2)
    
    Returns:
        Dictionary with Upper, Middle, and Lower bands
    """
    try:
        middle = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()
        upper = middle + (std * std_dev)
        lower = middle - (std * std_dev)
        
        return {
            'Upper': upper,
            'Middle': middle,
            'Lower': lower,
            'Width': upper - lower,
            'Position': (prices - lower) / (upper - lower)
        }
    except Exception:
        return {
            'Upper': prices * 1.02,
            'Middle': prices,
            'Lower': prices * 0.98,
            'Width': prices * 0.04,
            'Position': pd.Series([0.5] * len(prices), index=prices.index)
        }

def calculate_moving_averages(prices: pd.Series, periods: List[int] = [5, 10, 20, 50, 200]) -> Dict[str, pd.Series]:
    """
    Calculate multiple moving averages
    
    Args:
        prices: Price series
        periods: List of periods for moving averages
    
    Returns:
        Dictionary with SMA and EMA for each period
    """
    try:
        result = {}
        for period in periods:
            result[f'SMA_{period}'] = prices.rolling(window=period).mean()
            result[f'EMA_{period}'] = prices.ewm(span=period).mean()
        return result
    except Exception:
        result = {}
        for period in periods:
            result[f'SMA_{period}'] = prices
            result[f'EMA_{period}'] = prices
        return result

def calculate_stochastic(high: pd.Series, low: pd.Series, close: pd.Series, 
                        k_period: int = 14, d_period: int = 3) -> Dict[str, pd.Series]:
    """
    Calculate Stochastic Oscillator
    
    Args:
        high: High prices
        low: Low prices
        close: Close prices
        k_period: %K period (default: 14)
        d_period: %D period (default: 3)
    
    Returns:
        Dictionary with %K and %D values
    """
    try:
        low_min = low.rolling(window=k_period).min()
        high_max = high.rolling(window=k_period).max()
        k_percent = 100 * ((close - low_min) / (high_max - low_min))
        d_percent = k_percent.rolling(window=d_period).mean()
        
        return {
            'K': k_percent.fillna(50),
            'D': d_percent.fillna(50)
        }
    except Exception:
        return {
            'K': pd.Series([50] * len(close), index=close.index),
            'D': pd.Series([50] * len(close), index=close.index)
        }

def calculate_williams_r(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
    """
    Calculate Williams %R
    
    Args:
        high: High prices
        low: Low prices
        close: Close prices
        period: Period (default: 14)
    
    Returns:
        Williams %R values
    """
    try:
        high_max = high.rolling(window=period).max()
        low_min = low.rolling(window=period).min()
        williams_r = -100 * ((high_max - close) / (high_max - low_min))
        return williams_r.fillna(-50)
    except Exception:
        return pd.Series([-50] * len(close), index=close.index)

def calculate_cci(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 20) -> pd.Series:
    """
    Calculate Commodity Channel Index (CCI)
    
    Args:
        high: High prices
        low: Low prices
        close: Close prices
        period: Period (default: 20)
    
    Returns:
        CCI values
    """
    try:
        typical_price = (high + low + close) / 3
        sma = typical_price.rolling(window=period).mean()
        mad = typical_price.rolling(window=period).apply(lambda x: np.mean(np.abs(x - x.mean())))
        cci = (typical_price - sma) / (0.015 * mad)
        return cci.fillna(0)
    except Exception:
        return pd.Series([0] * len(close), index=close.index)

def calculate_atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
    """
    Calculate Average True Range (ATR)
    
    Args:
        high: High prices
        low: Low prices
        close: Close prices
        period: Period (default: 14)
    
    Returns:
        ATR values
    """
    try:
        high_low = high - low
        high_close = np.abs(high - close.shift())
        low_close = np.abs(low - close.shift())
        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = true_range.rolling(window=period).mean()
        return atr.fillna(1)
    except Exception:
        return pd.Series([1] * len(close), index=close.index)

def calculate_obv(close: pd.Series, volume: pd.Series) -> pd.Series:
    """
    Calculate On-Balance Volume (OBV)
    
    Args:
        close: Close prices
        volume: Volume data
    
    Returns:
        OBV values
    """
    try:
        obv = [0]
        for i in range(1, len(close)):
            if close.iloc[i] > close.iloc[i-1]:
                obv.append(obv[-1] + volume.iloc[i])
            elif close.iloc[i] < close.iloc[i-1]:
                obv.append(obv[-1] - volume.iloc[i])
            else:
                obv.append(obv[-1])
        return pd.Series(obv, index=close.index)
    except Exception:
        return pd.Series([0] * len(close), index=close.index)

def calculate_mfi(high: pd.Series, low: pd.Series, close: pd.Series, volume: pd.Series, period: int = 14) -> pd.Series:
    """
    Calculate Money Flow Index (MFI)
    
    Args:
        high: High prices
        low: Low prices
        close: Close prices
        volume: Volume data
        period: Period (default: 14)
    
    Returns:
        MFI values
    """
    try:
        typical_price = (high + low + close) / 3
        money_flow = typical_price * volume
        
        positive_flow = []
        negative_flow = []
        
        for i in range(1, len(typical_price)):
            if typical_price.iloc[i] > typical_price.iloc[i-1]:
                positive_flow.append(money_flow.iloc[i])
                negative_flow.append(0)
            elif typical_price.iloc[i] < typical_price.iloc[i-1]:
                positive_flow.append(0)
                negative_flow.append(money_flow.iloc[i])
            else:
                positive_flow.append(0)
                negative_flow.append(0)
        
        positive_flow = [0] + positive_flow
        negative_flow = [0] + negative_flow
        
        positive_mf = pd.Series(positive_flow, index=close.index).rolling(window=period).sum()
        negative_mf = pd.Series(negative_flow, index=close.index).rolling(window=period).sum()
        
        mfi = 100 - (100 / (1 + (positive_mf / negative_mf)))
        return mfi.fillna(50)
    except Exception:
        return pd.Series([50] * len(close), index=close.index)

def get_support_resistance(prices: pd.Series, window: int = 20) -> Dict[str, List[float]]:
    """
    Identify support and resistance levels
    
    Args:
        prices: Price series
        window: Window for local extrema detection
    
    Returns:
        Dictionary with support and resistance levels
    """
    try:
        # Find local minima (support) and maxima (resistance)
        support_levels = []
        resistance_levels = []
        
        for i in range(window, len(prices) - window):
            if prices.iloc[i] == prices.iloc[i-window:i+window+1].min():
                support_levels.append(prices.iloc[i])
            elif prices.iloc[i] == prices.iloc[i-window:i+window+1].max():
                resistance_levels.append(prices.iloc[i])
        
        # Remove duplicates and sort
        support_levels = sorted(list(set(support_levels)))
        resistance_levels = sorted(list(set(resistance_levels)), reverse=True)
        
        return {
            'support': support_levels[:5],  # Top 5 support levels
            'resistance': resistance_levels[:5]  # Top 5 resistance levels
        }
    except Exception:
        current_price = prices.iloc[-1]
        return {
            'support': [current_price * 0.95, current_price * 0.90],
            'resistance': [current_price * 1.05, current_price * 1.10]
        }

def analyze_trends(prices: pd.Series, short_window: int = 20, long_window: int = 50) -> Dict[str, str]:
    """
    Analyze price trends
    
    Args:
        prices: Price series
        short_window: Short-term moving average window
        long_window: Long-term moving average window
    
    Returns:
        Dictionary with trend analysis
    """
    try:
        short_ma = prices.rolling(window=short_window).mean()
        long_ma = prices.rolling(window=long_window).mean()
        
        current_short = short_ma.iloc[-1]
        current_long = long_ma.iloc[-1]
        current_price = prices.iloc[-1]
        
        # Determine trend direction
        if current_short > current_long and current_price > current_short:
            trend = "Strong Uptrend"
        elif current_short > current_long:
            trend = "Uptrend"
        elif current_short < current_long and current_price < current_short:
            trend = "Strong Downtrend"
        elif current_short < current_long:
            trend = "Downtrend"
        else:
            trend = "Sideways"
        
        # Calculate trend strength
        ma_diff = abs(current_short - current_long) / current_long * 100
        if ma_diff > 5:
            strength = "Strong"
        elif ma_diff > 2:
            strength = "Moderate"
        else:
            strength = "Weak"
        
        return {
            'trend': trend,
            'strength': strength,
            'short_ma': current_short,
            'long_ma': current_long,
            'ma_difference': ma_diff
        }
    except Exception:
        return {
            'trend': "Unknown",
            'strength': "Unknown",
            'short_ma': prices.iloc[-1],
            'long_ma': prices.iloc[-1],
            'ma_difference': 0
        }

def calculate_volatility(prices: pd.Series, period: int = 20) -> Dict[str, float]:
    """
    Calculate various volatility measures
    
    Args:
        prices: Price series
        period: Period for calculations
    
    Returns:
        Dictionary with volatility measures
    """
    try:
        returns = prices.pct_change().dropna()
        
        # Historical volatility (annualized)
        hist_vol = returns.rolling(window=period).std() * np.sqrt(252) * 100
        
        # Average True Range based volatility
        high = prices * 1.01  # Approximate high
        low = prices * 0.99   # Approximate low
        atr = calculate_atr(high, low, prices, period)
        atr_vol = (atr / prices) * 100
        
        return {
            'historical_volatility': hist_vol.iloc[-1] if not hist_vol.empty else 20.0,
            'atr_volatility': atr_vol.iloc[-1] if not atr_vol.empty else 2.0,
            'recent_volatility': returns.tail(5).std() * np.sqrt(252) * 100,
            'volatility_trend': 'Increasing' if hist_vol.iloc[-1] > hist_vol.iloc[-5] else 'Decreasing'
        }
    except Exception:
        return {
            'historical_volatility': 20.0,
            'atr_volatility': 2.0,
            'recent_volatility': 15.0,
            'volatility_trend': 'Stable'
        }

def get_market_sentiment(prices: pd.Series, volume: pd.Series = None) -> Dict[str, str]:
    """
    Analyze market sentiment based on price and volume
    
    Args:
        prices: Price series
        volume: Volume series (optional)
    
    Returns:
        Dictionary with sentiment analysis
    """
    try:
        # Price-based sentiment
        returns = prices.pct_change().dropna()
        recent_returns = returns.tail(5)
        
        if recent_returns.mean() > 0.02:
            price_sentiment = "Very Bullish"
        elif recent_returns.mean() > 0.005:
            price_sentiment = "Bullish"
        elif recent_returns.mean() < -0.02:
            price_sentiment = "Very Bearish"
        elif recent_returns.mean() < -0.005:
            price_sentiment = "Bearish"
        else:
            price_sentiment = "Neutral"
        
        # Volume-based sentiment (if available)
        volume_sentiment = "Unknown"
        if volume is not None:
            try:
                avg_volume = volume.rolling(window=20).mean()
                recent_volume = volume.tail(5).mean()
                
                if recent_volume > avg_volume.iloc[-1] * 1.5:
                    volume_sentiment = "High Interest"
                elif recent_volume > avg_volume.iloc[-1] * 1.2:
                    volume_sentiment = "Increased Interest"
                elif recent_volume < avg_volume.iloc[-1] * 0.8:
                    volume_sentiment = "Low Interest"
                else:
                    volume_sentiment = "Normal Interest"
            except:
                volume_sentiment = "Unknown"
        
        # Overall sentiment
        if "Very" in price_sentiment:
            overall = price_sentiment
        elif price_sentiment in ["Bullish", "Bearish"] and "High" in volume_sentiment:
            overall = f"Strong {price_sentiment}"
        else:
            overall = price_sentiment
        
        return {
            'overall_sentiment': overall,
            'price_sentiment': price_sentiment,
            'volume_sentiment': volume_sentiment,
            'confidence': 'High' if 'Very' in price_sentiment or 'High' in volume_sentiment else 'Medium'
        }
    except Exception:
        return {
            'overall_sentiment': 'Neutral',
            'price_sentiment': 'Neutral',
            'volume_sentiment': 'Unknown',
            'confidence': 'Low'
        }

def calculate_fibonacci_levels(high: float, low: float) -> Dict[str, float]:
    """
    Calculate Fibonacci retracement levels
    
    Args:
        high: Recent high price
        low: Recent low price
    
    Returns:
        Dictionary with Fibonacci levels
    """
    try:
        diff = high - low
        
        levels = {
            'level_0': high,
            'level_236': high - (diff * 0.236),
            'level_382': high - (diff * 0.382),
            'level_500': high - (diff * 0.500),
            'level_618': high - (diff * 0.618),
            'level_786': high - (diff * 0.786),
            'level_100': low
        }
        
        # Add extension levels
        levels.update({
            'ext_1272': high + (diff * 0.272),
            'ext_1618': high + (diff * 0.618),
            'ext_2618': high + (diff * 1.618)
        })
        
        return levels
    except Exception:
        return {
            'level_0': high,
            'level_236': high * 0.95,
            'level_382': high * 0.92,
            'level_500': high * 0.90,
            'level_618': high * 0.88,
            'level_786': high * 0.85,
            'level_100': low,
            'ext_1272': high * 1.05,
            'ext_1618': high * 1.10,
            'ext_2618': high * 1.15
        }

# Convenience function to calculate all indicators at once
def calculate_all_indicators(data: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate all technical indicators for a stock dataset
    
    Args:
        data: DataFrame with OHLCV data
    
    Returns:
        DataFrame with all indicators added
    """
    try:
        df = data.copy()
        
        # Basic indicators
        df['RSI'] = calculate_rsi(df['Close'])
        
        # MACD
        macd_data = calculate_macd(df['Close'])
        df['MACD'] = macd_data['MACD']
        df['MACD_Signal'] = macd_data['Signal']
        df['MACD_Histogram'] = macd_data['Histogram']
        
        # Bollinger Bands
        bb_data = calculate_bollinger_bands(df['Close'])
        df['BB_Upper'] = bb_data['Upper']
        df['BB_Middle'] = bb_data['Middle']
        df['BB_Lower'] = bb_data['Lower']
        df['BB_Width'] = bb_data['Width']
        df['BB_Position'] = bb_data['Position']
        
        # Moving Averages
        ma_data = calculate_moving_averages(df['Close'])
        for key, value in ma_data.items():
            df[key] = value
        
        # Stochastic
        stoch_data = calculate_stochastic(df['High'], df['Low'], df['Close'])
        df['Stoch_K'] = stoch_data['K']
        df['Stoch_D'] = stoch_data['D']
        
        # Other indicators
        df['Williams_R'] = calculate_williams_r(df['High'], df['Low'], df['Close'])
        df['CCI'] = calculate_cci(df['High'], df['Low'], df['Close'])
        df['ATR'] = calculate_atr(df['High'], df['Low'], df['Close'])
        
        # Volume indicators
        if 'Volume' in df.columns:
            df['OBV'] = calculate_obv(df['Close'], df['Volume'])
            df['MFI'] = calculate_mfi(df['High'], df['Low'], df['Close'], df['Volume'])
        
        return df
        
    except Exception as e:
        print(f"Error calculating indicators: {e}")
        return data