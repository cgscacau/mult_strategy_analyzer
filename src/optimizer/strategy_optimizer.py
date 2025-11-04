"""
Strategy Optimizer - Otimização automática de parâmetros
Testa múltiplas combinações de parâmetros e encontra a melhor configuração
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any
from itertools import product
from src.backtest import StrategyBacktester

class StrategyOptimizer:
    """
    Otimizador de parâmetros para estratégias
    
    Usa grid search para testar todas as combinações possíveis
    e encontra a configuração com melhor performance
    """
    
    def __init__(self, strategy_class, daily_df: pd.DataFrame, weekly_df: pd.DataFrame):
        """
        Args:
            strategy_class: Classe da estratégia (não instância)
            daily_df: DataFrame com dados diários (OHLCV)
            weekly_df: DataFrame com dados semanais (OHLCV)
        """
        self.strategy_class = strategy_class
        self.daily_df = daily_df
        self.weekly_df = weekly_df
        self.results = []
    
    def optimize(self, param_grid: Dict[str, List], 
                 metric: str = 'profit_factor',
                 lookback_days: int = 252) -> Tuple[Dict, pd.DataFrame]:
        """
        Otimiza parâmetros usando grid search
        
        Args:
            param_grid: Dicionário com ranges de parâmetros
                       Ex: {'upper': [15, 20, 25], 'under': [25, 30, 35]}
            metric: Métrica para otimização ('profit_factor', 'win_rate', 
                    'total_return', 'sharpe_ratio')
            lookback_days: Dias para backtest
            
        Returns:
            Tupla (melhores_params, df_resultados)
        """
        print(f"🔍 Iniciando otimização com {self._count_combinations(param_grid)} combinações...")
        
        # Gera todas as combinações
        param_names = list(param_grid.keys())
        param_values = list(param_grid.values())
        combinations = list(product(*param_values))
        
        self.results = []
        
        # Testa cada combinação
        for i, combo in enumerate(combinations, 1):
            params = dict(zip(param_names, combo))
            
            try:
                # Cria estratégia com esses parâmetros
                strategy = self.strategy_class(**params)
                
                # Calcula indicadores
                daily_processed = strategy.calculate_full(self.daily_df.copy())
                weekly_processed = strategy.calculate_full(self.weekly_df.copy())
                
                # Verifica convergência
                has_conv, conv_info = strategy.check_convergence(daily_processed, weekly_processed)
                
                # Executa backtest
                backtester = StrategyBacktester(strategy)
                backtest_results = backtester.run(daily_processed, weekly_processed, lookback_days)
                
                metrics = backtest_results['metrics']
                
                # Salva resultados
                result = {
                    **params,
                    'convergence': has_conv,
                    'total_trades': metrics['total_trades'],
                    'win_rate': metrics['win_rate'],
                    'win_rate_adjusted': metrics['win_rate_adjusted'],
                    'profit_factor': metrics['profit_factor'],
                    'total_return': metrics['total_return'],
                    'sharpe_ratio': metrics['sharpe_ratio'],
                    'max_drawdown': metrics['max_drawdown'],
                    'expectancy': metrics['expectancy'],
                }
                
                self.results.append(result)
                
                if i % 10 == 0 or i == len(combinations):
                    print(f"   ⏳ Progresso: {i}/{len(combinations)} ({i/len(combinations)*100:.1f}%)")
                
            except Exception as e:
                print(f"   ⚠️ Erro na combinação {params}: {e}")
                continue
        
        # Converte para DataFrame
        results_df = pd.DataFrame(self.results)
        
        if results_df.empty:
            print("❌ Nenhum resultado válido encontrado")
            return {}, results_df
        
        # Filtra apenas com trades suficientes
        results_df = results_df[results_df['total_trades'] >= 3]
        
        if results_df.empty:
            print("❌ Nenhuma configuração gerou trades suficientes (mín 3)")
            return {}, pd.DataFrame(self.results)
        
        # Ordena pela métrica escolhida
        results_df = results_df.sort_values(metric, ascending=False)
        
        # Melhor configuração
        best_row = results_df.iloc[0]
        best_params = {k: best_row[k] for k in param_names}
        
        print(f"\n✅ Otimização concluída!")
        print(f"   🏆 Melhor {metric}: {best_row[metric]:.2f}")
        print(f"   ⚙️ Parâmetros: {best_params}")
        
        return best_params, results_df
    
    def _count_combinations(self, param_grid: Dict) -> int:
        """Conta total de combinações"""
        total = 1
        for values in param_grid.values():
            total *= len(values)
        return total
    
    def get_top_n(self, n: int = 5, metric: str = 'profit_factor') -> pd.DataFrame:
        """Retorna top N configurações"""
        if not self.results:
            return pd.DataFrame()
        
        df = pd.DataFrame(self.results)
        df = df[df['total_trades'] >= 3]
        return df.sort_values(metric, ascending=False).head(n)
