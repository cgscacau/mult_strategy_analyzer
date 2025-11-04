"""
Market Data Module - Download de dados históricos via yfinance
"""

import yfinance as yf
import pandas as pd
from typing import Optional

def download_data(ticker: str, period: str = "1y", interval: str = "1d") -> Optional[pd.DataFrame]:
    """
    Baixa dados históricos de um ativo
    
    Args:
        ticker: Símbolo do ativo (ex: PETR4.SA, AAPL, BTC-USD)
        period: Período de dados (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
        interval: Intervalo (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
        
    Returns:
        DataFrame com colunas OHLCV ou None se falhar
    """
    try:
        data = yf.download(ticker, period=period, interval=interval, progress=False)
        
        if data.empty:
            return None
        
        # Remove multi-index se necessário
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)
        
        return data
    
    except Exception as e:
        print(f"Erro ao baixar {ticker}: {e}")
        return None

def get_daily_data(ticker: str, period: str = "1y") -> Optional[pd.DataFrame]:
    """Baixa dados diários"""
    return download_data(ticker, period=period, interval="1d")

def get_weekly_data(ticker: str, period: str = "2y") -> Optional[pd.DataFrame]:
    """Baixa dados semanais"""
    return download_data(ticker, period=period, interval="1wk")
