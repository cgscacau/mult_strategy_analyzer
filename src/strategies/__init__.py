"""
Strategies Module - Sistema modular de estratégias de trading
Permite adicionar e trocar entre diferentes indicadores/estratégias
"""

from .base_strategy import BaseStrategy
from .cacas_channel_strategy import CacasChannelStrategy
from .moving_average_strategy import MovingAverageCrossStrategy
from .mss_strategy import MSSStrategy

# Registry de estratégias disponíveis
AVAILABLE_STRATEGIES = {
    'Cacas Channel': CacasChannelStrategy,
    'Moving Average Cross': MovingAverageCrossStrategy,
    'MSS (Market Structure)': MSSStrategy,
}

def get_strategy(strategy_name: str, **params) -> BaseStrategy:
    """
    Factory function para criar instância de estratégia
    
    Args:
        strategy_name: Nome da estratégia (key do AVAILABLE_STRATEGIES)
        **params: Parâmetros específicos da estratégia
        
    Returns:
        Instância da estratégia selecionada
    """
    if strategy_name not in AVAILABLE_STRATEGIES:
        raise ValueError(f"Estratégia '{strategy_name}' não encontrada. Disponíveis: {list(AVAILABLE_STRATEGIES.keys())}")
    
    strategy_class = AVAILABLE_STRATEGIES[strategy_name]
    return strategy_class(**params)

def list_strategies():
    """Retorna lista de estratégias disponíveis"""
    return list(AVAILABLE_STRATEGIES.keys())
