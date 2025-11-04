"""
Asset Loader - Carrega listas de ativos de múltiplos mercados
"""

import pandas as pd
import os
from typing import Dict, List

class AssetLoader:
    """Carregador de ativos multi-mercado"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.assets = {}
    
    def load_all_assets(self) -> Dict[str, List[str]]:
        """
        Carrega todos os ativos disponíveis
        
        Returns:
            Dict com mercados e listas de tickers
        """
        self.assets = {
            'Brasil': {
                'Ações': self._load_csv('b3_acoes.csv'),
                'FIIs': self._load_csv('b3_fiis.csv'),
                'ETFs': self._load_csv('b3_etfs.csv'),
                'BDRs': self._load_csv('b3_bdrs.csv'),
            },
            'EUA': {
                'Stocks': self._load_csv('us_stocks.csv'),
                'ETFs': self._load_csv('us_etfs.csv'),
                'REITs': self._load_csv('us_reits.csv'),
            },
            'Crypto': {
                'Principais': self._load_csv('crypto.csv'),
            }
        }
        
        return self.assets
    
    def _load_csv(self, filename: str) -> List[str]:
        """Carrega CSV e retorna lista de tickers"""
        filepath = os.path.join(self.data_dir, filename)
        
        if not os.path.exists(filepath):
            return []
        
        try:
            df = pd.read_csv(filepath)
            # Assume que primeira coluna é ticker
            tickers = df.iloc[:, 0].tolist()
            return [str(t).strip() for t in tickers if pd.notna(t)]
        except Exception as e:
            print(f"Erro ao carregar {filename}: {e}")
            return []
    
    def get_all_tickers(self) -> List[str]:
        """Retorna lista flat de todos os tickers"""
        all_tickers = []
        for market in self.assets.values():
            for category in market.values():
                all_tickers.extend(category)
        return all_tickers
    
    def count_assets(self) -> Dict:
        """Conta número de ativos por categoria"""
        counts = {}
        for market, categories in self.assets.items():
            counts[market] = {}
            for category, tickers in categories.items():
                counts[market][category] = len(tickers)
        return counts
