"""
Cacas Channel Strategy - Implementação da estratégia original usando arquitetura modular
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from .base_strategy import BaseStrategy

class CacasChannelStrategy(BaseStrategy):
    """
    Estratégia Cacas Channel - Canal de tendência com 4 linhas
    
    Sinal: Convergência quando Linha Branca > Linha Laranja em ambos timeframes
    """
    
    def __init__(self, upper: int = 20, under: int = 30, ema: int = 9, 
                 atr_period: int = 14, stop_multiplier: float = 1.5, 
                 target_multiplier: float = 2.0):
        """
        Args:
            upper: Período para linha superior (resistência)
            under: Período para linha inferior (suporte)
            ema: Período para EMA (sinal)
            atr_period: Período para cálculo do ATR
            stop_multiplier: Multiplicador do ATR para stop loss
            target_multiplier: Multiplicador do stop para alvo
        """
        self.upper = upper
        self.under = under
        self.ema = ema
        self.atr_period = atr_period
        self.stop_multiplier = stop_multiplier
        self.target_multiplier = target_multiplier
    
    def get_strategy_name(self) -> str:
        return "Cacas Channel"
    
    def get_strategy_description(self) -> str:
        return (
            f"Canal de tendência com convergência multi-timeframe. "
            f"Parâmetros: Upper={self.upper}, Under={self.under}, EMA={self.ema}"
        )
    
    def get_indicator_names(self) -> List[str]:
        return [
            'cacas_upper',    # Linha superior (vermelha/resistência)
            'cacas_under',    # Linha inferior (verde/suporte)
            'cacas_mid',      # Linha média (branca/tendência)
            'ema',            # EMA (laranja/sinal)
            'atr'             # ATR para gestão de risco
        ]
    
    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calcula os indicadores do Cacas Channel
        
        Fórmulas:
        - Linha Superior: Média das máximas de 'upper' períodos
        - Linha Inferior: Média das mínimas de 'under' períodos
        - Linha Média: (Superior + Inferior) / 2
        - EMA: Exponencial do fechamento
        """
        df = df.copy()
        
        # Cacas Channel - 4 linhas
        df['cacas_upper'] = df['High'].rolling(window=self.upper).mean()
        df['cacas_under'] = df['Low'].rolling(window=self.under).mean()
        df['cacas_mid'] = (df['cacas_upper'] + df['cacas_under']) / 2
        df['ema'] = df['Close'].ewm(span=self.ema, adjust=False).mean()
        
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
        Gera sinais de compra baseados na convergência
        
        Sinal de compra: cacas_mid > ema (Linha Branca > Linha Laranja)
        """
        df = df.copy()
        
        # Sinal simples: Linha Média > EMA
        df['signal'] = (df['cacas_mid'] > df['ema']).astype(int)
        
        # Stop loss e alvo baseados em ATR
        df['stop_loss'] = df['Close'] - (df['atr'] * self.stop_multiplier)
        df['target'] = df['Close'] + (df['atr'] * self.stop_multiplier * self.target_multiplier)
        
        return df
    
    def check_convergence(self, daily_df: pd.DataFrame, weekly_df: pd.DataFrame) -> Tuple[bool, Dict]:
        """
        Verifica convergência entre timeframes diário e semanal
        
        Convergência = Sinal em AMBOS os timeframes
        """
        # Pega últimos sinais válidos
        daily_signal = daily_df['signal'].iloc[-1] if not daily_df.empty else 0
        weekly_signal = weekly_df['signal'].iloc[-1] if not weekly_df.empty else 0
        
        has_convergence = (daily_signal == 1 and weekly_signal == 1)
        
        # Informações detalhadas
        info = {
            'daily_signal': bool(daily_signal),
            'weekly_signal': bool(weekly_signal),
            'convergence': has_convergence,
            'daily_mid': float(daily_df['cacas_mid'].iloc[-1]) if not daily_df.empty else 0,
            'daily_ema': float(daily_df['ema'].iloc[-1]) if not daily_df.empty else 0,
            'weekly_mid': float(weekly_df['cacas_mid'].iloc[-1]) if not weekly_df.empty else 0,
            'weekly_ema': float(weekly_df['ema'].iloc[-1]) if not weekly_df.empty else 0,
            'stop_loss': float(daily_df['stop_loss'].iloc[-1]) if not daily_df.empty else 0,
            'target': float(daily_df['target'].iloc[-1]) if not daily_df.empty else 0,
            'atr': float(daily_df['atr'].iloc[-1]) if not daily_df.empty else 0,
        }
        
        return has_convergence, info
