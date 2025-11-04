"""
MSS (Market Structure Shift) Strategy
Baseado no indicador ICT - Detecta BOS e MSS para sinais de compra/venda
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from .base_strategy import BaseStrategy

class MSSStrategy(BaseStrategy):
    """
    Estratégia Market Structure Shift (MSS)
    
    Detecta mudanças na estrutura de mercado:
    - BOS (Break of Structure): Quebra da estrutura
    - MSS (Market Structure Shift): Mudança de estrutura (mais forte)
    
    Sinal de compra: MSS ou BOS bullish
    Sinal de venda: MSS ou BOS bearish
    """
    
    def __init__(self, swing_length: int = 5, atr_period: int = 14,
                 stop_multiplier: float = 1.5, target_multiplier: float = 2.0):
        """
        Args:
            swing_length: Comprimento para detectar swing highs/lows
            atr_period: Período para cálculo do ATR
            stop_multiplier: Multiplicador do ATR para stop loss
            target_multiplier: Multiplicador do stop para alvo
        """
        self.swing_length = swing_length
        self.atr_period = atr_period
        self.stop_multiplier = stop_multiplier
        self.target_multiplier = target_multiplier
        
        self.market_structure = 0  # 1 = bullish, -1 = bearish, 0 = neutral
    
    def get_strategy_name(self) -> str:
        return "MSS (Market Structure)"
    
    def get_strategy_description(self) -> str:
        return (
            f"Market Structure Shift - Detecta BOS/MSS. "
            f"Parâmetros: Swing={self.swing_length}, ATR={self.atr_period}"
        )
    
    def get_indicator_names(self) -> List[str]:
        return [
            'swing_high',    # Topos do swing
            'swing_low',     # Fundos do swing
            'structure_line',# Linha da estrutura de mercado
            'atr'            # ATR para gestão de risco
        ]
    
    def _detect_swing_high(self, df: pd.DataFrame, length: int) -> pd.Series:
        """Detecta swing highs (topos)"""
        swing_high = pd.Series(np.nan, index=df.index)
        
        for i in range(length, len(df) - length):
            is_high = True
            current_high = df['High'].iloc[i]
            
            # Verifica se é o maior nos períodos anteriores e posteriores
            for j in range(1, length + 1):
                if (df['High'].iloc[i - j] >= current_high or 
                    df['High'].iloc[i + j] >= current_high):
                    is_high = False
                    break
            
            if is_high:
                swing_high.iloc[i] = current_high
        
        return swing_high
    
    def _detect_swing_low(self, df: pd.DataFrame, length: int) -> pd.Series:
        """Detecta swing lows (fundos)"""
        swing_low = pd.Series(np.nan, index=df.index)
        
        for i in range(length, len(df) - length):
            is_low = True
            current_low = df['Low'].iloc[i]
            
            # Verifica se é o menor nos períodos anteriores e posteriores
            for j in range(1, length + 1):
                if (df['Low'].iloc[i - j] <= current_low or 
                    df['Low'].iloc[i + j] <= current_low):
                    is_low = False
                    break
            
            if is_low:
                swing_low.iloc[i] = current_low
        
        return swing_low
    
    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calcula indicadores MSS
        
        Detecta swing highs/lows e estrutura de mercado
        """
        df = df.copy()
        
        # Detecta swing highs e lows
        df['swing_high'] = self._detect_swing_high(df, self.swing_length)
        df['swing_low'] = self._detect_swing_low(df, self.swing_length)
        
        # Preenche valores forward para visualização
        df['last_swing_high'] = df['swing_high'].fillna(method='ffill')
        df['last_swing_low'] = df['swing_low'].fillna(method='ffill')
        
        # Linha da estrutura (média dos swings)
        df['structure_line'] = (df['last_swing_high'] + df['last_swing_low']) / 2
        
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
        Gera sinais baseados em MSS/BOS
        
        BOS Bullish: Preço quebra último swing high
        BOS Bearish: Preço quebra último swing low
        MSS: Quando muda de tendência (bull->bear ou bear->bull)
        """
        df = df.copy()
        
        # Inicializa sinais
        df['signal'] = 0
        df['signal_type'] = ''  # 'BOS_BULL', 'BOS_BEAR', 'MSS_BULL', 'MSS_BEAR'
        
        previous_structure = 0  # Estrutura anterior
        
        for i in range(1, len(df)):
            current_price = df['Close'].iloc[i]
            last_swing_high = df['last_swing_high'].iloc[i-1]
            last_swing_low = df['last_swing_low'].iloc[i-1]
            
            # Detecta BOS Bullish (quebra swing high anterior)
            if current_price > last_swing_high:
                if previous_structure <= 0:  # Era bearish ou neutro
                    df.loc[df.index[i], 'signal_type'] = 'MSS_BULL'  # Mudança de estrutura
                    df.loc[df.index[i], 'signal'] = 1
                else:
                    df.loc[df.index[i], 'signal_type'] = 'BOS_BULL'  # Continuação bullish
                    df.loc[df.index[i], 'signal'] = 1
                
                previous_structure = 1  # Agora é bullish
            
            # Detecta BOS Bearish (quebra swing low anterior)
            elif current_price < last_swing_low:
                if previous_structure >= 0:  # Era bullish ou neutro
                    df.loc[df.index[i], 'signal_type'] = 'MSS_BEAR'  # Mudança de estrutura
                    df.loc[df.index[i], 'signal'] = 0  # Venda/sai
                else:
                    df.loc[df.index[i], 'signal_type'] = 'BOS_BEAR'  # Continuação bearish
                    df.loc[df.index[i], 'signal'] = 0
                
                previous_structure = -1  # Agora é bearish
            
            else:
                # Mantém estrutura anterior
                if previous_structure > 0:
                    df.loc[df.index[i], 'signal'] = 1  # Mantém comprado
                else:
                    df.loc[df.index[i], 'signal'] = 0  # Mantém fora
        
        # Stop loss e alvo baseados em ATR
        df['stop_loss'] = df['Close'] - (df['atr'] * self.stop_multiplier)
        df['target'] = df['Close'] + (df['atr'] * self.stop_multiplier * self.target_multiplier)
        
        return df
    
    def check_convergence(self, daily_df: pd.DataFrame, weekly_df: pd.DataFrame) -> Tuple[bool, Dict]:
        """
        Verifica convergência entre timeframes
        
        Convergência = MSS ou BOS em ambos timeframes na mesma direção
        """
        # Pega últimos sinais
        daily_signal = daily_df['signal'].iloc[-1] if not daily_df.empty else 0
        weekly_signal = weekly_df['signal'].iloc[-1] if not weekly_df.empty else 0
        
        daily_type = daily_df['signal_type'].iloc[-1] if not daily_df.empty else ''
        weekly_type = weekly_df['signal_type'].iloc[-1] if not weekly_df.empty else ''
        
        # Convergência: ambos bullish (signal=1)
        has_convergence = (daily_signal == 1 and weekly_signal == 1)
        
        # Informações detalhadas
        info = {
            'daily_signal': bool(daily_signal),
            'weekly_signal': bool(weekly_signal),
            'convergence': has_convergence,
            'daily_signal_type': daily_type,
            'weekly_signal_type': weekly_type,
            'daily_swing_high': float(daily_df['last_swing_high'].iloc[-1]) if not daily_df.empty else 0,
            'daily_swing_low': float(daily_df['last_swing_low'].iloc[-1]) if not daily_df.empty else 0,
            'weekly_swing_high': float(weekly_df['last_swing_high'].iloc[-1]) if not weekly_df.empty else 0,
            'weekly_swing_low': float(weekly_df['last_swing_low'].iloc[-1]) if not weekly_df.empty else 0,
            'stop_loss': float(daily_df['stop_loss'].iloc[-1]) if not daily_df.empty else 0,
            'target': float(daily_df['target'].iloc[-1]) if not daily_df.empty else 0,
            'atr': float(daily_df['atr'].iloc[-1]) if not daily_df.empty else 0,
            'entry_price': float(daily_df['Close'].iloc[-1]) if not daily_df.empty else 0,
        }
        
        return has_convergence, info
