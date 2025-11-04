"""
Moving Average Cross Strategy - Estratégia de cruzamento de médias móveis
Estratégia clássica: Sinal de compra quando média rápida cruza acima da média lenta
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from .base_strategy import BaseStrategy

class MovingAverageCrossStrategy(BaseStrategy):
    """
    Estratégia de Cruzamento de Médias Móveis
    
    Sinal de compra: EMA rápida cruza acima da EMA lenta em ambos timeframes
    """
    
    def __init__(self, fast_period: int = 9, slow_period: int = 21, 
                 atr_period: int = 14, stop_multiplier: float = 1.5, 
                 target_multiplier: float = 2.0):
        """
        Args:
            fast_period: Período da média móvel rápida
            slow_period: Período da média móvel lenta
            atr_period: Período para cálculo do ATR
            stop_multiplier: Multiplicador do ATR para stop loss
            target_multiplier: Multiplicador do stop para alvo
        """
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.atr_period = atr_period
        self.stop_multiplier = stop_multiplier
        self.target_multiplier = target_multiplier
    
    def get_strategy_name(self) -> str:
        return "Moving Average Cross"
    
    def get_strategy_description(self) -> str:
        return (
            f"Cruzamento de médias móveis com convergência multi-timeframe. "
            f"Parâmetros: EMA Rápida={self.fast_period}, EMA Lenta={self.slow_period}"
        )
    
    def get_indicator_names(self) -> List[str]:
        return [
            'ema_fast',    # Média móvel rápida
            'ema_slow',    # Média móvel lenta
            'atr'          # ATR para gestão de risco
        ]
    
    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calcula as médias móveis exponenciais e ATR
        """
        df = df.copy()
        
        # Médias móveis exponenciais
        df['ema_fast'] = df['Close'].ewm(span=self.fast_period, adjust=False).mean()
        df['ema_slow'] = df['Close'].ewm(span=self.slow_period, adjust=False).mean()
        
        # ATR para gestão de risco
        high_low = df['High'] - df['Low']
        high_close = np.abs(df['High'] - df['Close'].shift())
        low_close = np.abs(df['Low'] - df['Close'].shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = ranges.max(axis=1)
        df['atr'] = true_range.rolling(self.atr_period).mean()
        
        return df
    
    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Gera sinais de compra baseados no cruzamento das médias
        
        Sinal de compra: EMA rápida > EMA lenta
        """
        df = df.copy()
        
        # Sinal: Média rápida acima da média lenta
        df['signal'] = (df['ema_fast'] > df['ema_slow']).astype(int)
        
        # Stop loss e alvo baseados em ATR
        df['stop_loss'] = df['Close'] - (df['atr'] * self.stop_multiplier)
        df['target'] = df['Close'] + (df['atr'] * self.stop_multiplier * self.target_multiplier)
        
        return df
    
    def check_convergence(self, daily_df: pd.DataFrame, weekly_df: pd.DataFrame) -> Tuple[bool, Dict]:
        """
        Verifica convergência entre timeframes diário e semanal
        
        Convergência = Sinal em AMBOS os timeframes (EMA rápida > EMA lenta)
        """
        # Pega últimos sinais válidos
        daily_signal = daily_df['signal'].iloc[-1] if not daily_df.empty else 0
        weekly_signal = weekly_df['signal'].iloc[-1] if not weekly_df.empty else 0
        
        has_convergence = (daily_signal == 1 and weekly_signal == 1)
        
        # Calcula distância entre médias (força do sinal)
        daily_distance = 0
        weekly_distance = 0
        if not daily_df.empty:
            daily_distance = ((daily_df['ema_fast'].iloc[-1] - daily_df['ema_slow'].iloc[-1]) / 
                            daily_df['ema_slow'].iloc[-1] * 100)
        if not weekly_df.empty:
            weekly_distance = ((weekly_df['ema_fast'].iloc[-1] - weekly_df['ema_slow'].iloc[-1]) / 
                             weekly_df['ema_slow'].iloc[-1] * 100)
        
        # Informações detalhadas
        info = {
            'daily_signal': bool(daily_signal),
            'weekly_signal': bool(weekly_signal),
            'convergence': has_convergence,
            'daily_ema_fast': float(daily_df['ema_fast'].iloc[-1]) if not daily_df.empty else 0,
            'daily_ema_slow': float(daily_df['ema_slow'].iloc[-1]) if not daily_df.empty else 0,
            'weekly_ema_fast': float(weekly_df['ema_fast'].iloc[-1]) if not weekly_df.empty else 0,
            'weekly_ema_slow': float(weekly_df['ema_slow'].iloc[-1]) if not weekly_df.empty else 0,
            'daily_distance_pct': float(daily_distance),
            'weekly_distance_pct': float(weekly_distance),
            'stop_loss': float(daily_df['stop_loss'].iloc[-1]) if not daily_df.empty else 0,
            'target': float(daily_df['target'].iloc[-1]) if not daily_df.empty else 0,
            'atr': float(daily_df['atr'].iloc[-1]) if not daily_df.empty else 0,
        }
        
        return has_convergence, info
