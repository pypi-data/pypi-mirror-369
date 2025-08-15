"""
MeridianAlgo - Advanced AI Stock Analysis Package
Enhanced with Ara AI's ensemble ML system, intelligent caching, and multi-GPU support

This package provides:
- Ensemble ML models (Random Forest + Gradient Boosting + LSTM)
- Multi-vendor GPU acceleration (NVIDIA, AMD, Intel, Apple)
- Intelligent prediction caching with accuracy tracking
- Real-time market data integration
- Advanced technical indicators
- Automated model validation and learning

Version: 2.0.0
"""

__version__ = "2.1.1"
__author__ = "MeridianAlgo Team"
__email__ = "support@meridianalgo.com"
__license__ = "MIT"

# Core imports for easy access
from .core import AraAI, StockPredictor
from .models import EnsembleMLSystem, LSTMModel
from .data import MarketDataManager, TechnicalIndicators
from .utils import GPUManager, CacheManager, AccuracyTracker

# Main prediction function for backward compatibility
from .core import predict_stock, analyze_stock

# Additional analysis functions
try:
    from .analysis import (
        calculate_rsi, calculate_macd, calculate_bollinger_bands,
        calculate_moving_averages, calculate_stochastic, calculate_williams_r,
        calculate_cci, calculate_atr, calculate_obv, calculate_mfi,
        get_support_resistance, analyze_trends, calculate_volatility,
        get_market_sentiment, calculate_fibonacci_levels, calculate_all_indicators
    )
except ImportError:
    # Fallback functions if analysis module fails to import
    def calculate_rsi(prices, period=14): return prices * 0 + 50
    def calculate_macd(prices, fast=12, slow=26, signal=9): return {'MACD': prices*0, 'Signal': prices*0, 'Histogram': prices*0}
    def calculate_bollinger_bands(prices, period=20, std_dev=2): return {'Upper': prices*1.02, 'Middle': prices, 'Lower': prices*0.98}

# Portfolio and risk management
try:
    from .portfolio import (
        PortfolioAnalyzer, RiskManager, PerformanceTracker,
        calculate_sharpe_ratio, calculate_max_drawdown, calculate_beta,
        optimize_portfolio, backtest_strategy
    )
except ImportError:
    # Fallback classes if portfolio module fails to import
    class PortfolioAnalyzer: pass
    class RiskManager: pass
    class PerformanceTracker: pass

# Market data utilities
try:
    from .market import (
        get_market_data, get_economic_indicators, get_sector_performance,
        get_market_news, get_earnings_calendar, get_dividend_calendar,
        compare_stocks, get_correlation_matrix, get_market_indices, analyze_market_sentiment
    )
except ImportError:
    # Fallback functions if market module fails to import
    def get_market_data(symbols, period="1y", interval="1d"): return {}
    def get_economic_indicators(): return {}
    def compare_stocks(symbols, period="1y"): return {}

# Version info
VERSION_INFO = {
    'version': __version__,
    'features': [
        'Ensemble ML Models (RF + GB + LSTM)',
        'Multi-GPU Support (NVIDIA/AMD/Intel/Apple)',
        'Intelligent Prediction Caching',
        'Automated Accuracy Tracking',
        'Real-time Market Data',
        'Advanced Technical Indicators',
        'Online Learning System'
    ],
    'gpu_support': [
        'NVIDIA CUDA',
        'AMD ROCm/DirectML', 
        'Intel XPU',
        'Apple MPS'
    ],
    'python_versions': ['3.8+', '3.9+', '3.10+', '3.11+', '3.12+']
}

def get_version_info():
    """Get detailed version and feature information"""
    return VERSION_INFO

def check_gpu_support():
    """Check available GPU acceleration options"""
    from .utils import GPUManager
    return GPUManager.detect_gpu_vendor()

# Convenience functions
def quick_predict(symbol, days=5, use_cache=True):
    """
    Quick stock prediction with intelligent caching
    
    Args:
        symbol (str): Stock symbol (e.g., 'AAPL', 'TSLA')
        days (int): Number of days to predict (default: 5)
        use_cache (bool): Use cached predictions if available (default: True)
    
    Returns:
        dict: Prediction results with prices, accuracy info, and metadata
    """
    from .core import AraAI
    ara = AraAI()
    return ara.predict(symbol, days=days, use_cache=use_cache)

def analyze_accuracy(symbol=None):
    """
    Analyze prediction accuracy for a symbol or all symbols
    
    Args:
        symbol (str, optional): Specific symbol to analyze, or None for all
    
    Returns:
        dict: Accuracy statistics and performance metrics
    """
    from .utils import AccuracyTracker
    tracker = AccuracyTracker()
    return tracker.analyze_accuracy(symbol)

# Package metadata
__all__ = [
    # Core classes
    'AraAI',
    'StockPredictor', 
    'EnsembleMLSystem',
    'LSTMModel',
    'MarketDataManager',
    'TechnicalIndicators',
    'GPUManager',
    'CacheManager',
    'AccuracyTracker',
    
    # Main functions
    'predict_stock',
    'analyze_stock',
    'quick_predict',
    'analyze_accuracy',
    
    # Technical Analysis Functions
    'calculate_rsi',
    'calculate_macd',
    'calculate_bollinger_bands',
    'calculate_moving_averages',
    'calculate_stochastic',
    'calculate_williams_r',
    'calculate_cci',
    'calculate_atr',
    'calculate_obv',
    'calculate_mfi',
    'get_support_resistance',
    'analyze_trends',
    'calculate_volatility',
    'get_market_sentiment',
    'calculate_fibonacci_levels',
    'calculate_all_indicators',
    
    # Portfolio Management
    'PortfolioAnalyzer',
    'RiskManager',
    'PerformanceTracker',
    'calculate_sharpe_ratio',
    'calculate_max_drawdown',
    'calculate_beta',
    'optimize_portfolio',
    'backtest_strategy',
    
    # Market Data Functions
    'get_market_data',
    'get_economic_indicators',
    'get_sector_performance',
    'get_market_news',
    'get_earnings_calendar',
    'get_dividend_calendar',
    'compare_stocks',
    'get_correlation_matrix',
    'get_market_indices',
    'analyze_market_sentiment',
    
    # Utility functions
    'get_version_info',
    'check_gpu_support',
    
    # Version info
    '__version__',
    'VERSION_INFO'
]