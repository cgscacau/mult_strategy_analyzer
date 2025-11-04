"""
Base Strategy - Classe abstrata para todas as estratégias de trading
Define interface comum que todas as estratégias devem implementar
"""

from abc import ABC, abstractmethod
import pandas as pd
from typing import Dict, List, Tuple

class BaseStrategy(ABC):
    """
    Classe abstrata base para estratégias de trading
    
    Todas as estratégias devem herdar desta classe e implementar:
    - calculate_indicators(): Calcula indicadores técnicos
    - generate_signals(): Gera sinais de compra/venda
    - check_convergence(): Verifica convergência multi-timeframe
    """
    
    @abstractmethod
    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calcula todos os indicadores da estratégia
        
        Args:
            df: DataFrame com dados OHLCV
            
        Returns:
            DataFrame com colunas dos indicadores adicionadas
        """
        pass
    
    @abstractmethod
    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Gera sinais de trading baseados nos indicadores
        
        Args:
            df: DataFrame com indicadores já calculados
            
        Returns:
            DataFrame com coluna 'signal' (1=compra, 0=sem sinal)
            e colunas 'stop_loss' e 'target'
        """
        pass
    
    @abstractmethod
    def check_convergence(self, daily_df: pd.DataFrame, 
                         weekly_df: pd.DataFrame) -> Tuple[bool, Dict]:
        """
        Verifica convergência entre timeframes diário e semanal
        
        Args:
            daily_df: DataFrame com dados e sinais diários
            weekly_df: DataFrame com dados e sinais semanais
            
        Returns:
            Tupla (has_convergence, info_dict) onde:
            - has_convergence: True se há convergência
            - info_dict: Dicionário com informações detalhadas
        """
        pass
    
    @abstractmethod
    def get_strategy_name(self) -> str:
        """Retorna nome da estratégia"""
        pass
    
    @abstractmethod
    def get_strategy_description(self) -> str:
        """Retorna descrição da estratégia"""
        pass
    
    @abstractmethod
    def get_indicator_names(self) -> List[str]:
        """Retorna lista de nomes dos indicadores usados"""
        pass
    
    def calculate_full(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Pipeline completo: calcula indicadores + gera sinais
        
        Método helper que pode ser usado por todas as estratégias
        """
        df = self.calculate_indicators(df)
        df = self.generate_signals(df)
        return df
