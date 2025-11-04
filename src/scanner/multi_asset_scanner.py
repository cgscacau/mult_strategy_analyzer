"""
Multi Asset Scanner - Varre múltiplos ativos automaticamente
Analisa lista de ativos e retorna aqueles com convergência
"""

import pandas as pd
from typing import List, Dict
from src.data.market_data import get_daily_data, get_weekly_data
from src.backtest import StrategyBacktester
import time

class MultiAssetScanner:
    """
    Scanner que varre múltiplos ativos com uma estratégia
    
    Identifica ativos com convergência e boas métricas de backtest
    """
    
    def __init__(self, strategy):
        """
        Args:
            strategy: Instância de BaseStrategy configurada
        """
        self.strategy = strategy
        self.results = []
    
    def scan(self, tickers: List[str], 
             min_win_rate: float = 50.0,
             min_profit_factor: float = 1.5,
             lookback_days: int = 252,
             delay_seconds: float = 0.5) -> pd.DataFrame:
        """
        Varre lista de ativos
        
        Args:
            tickers: Lista de símbolos para analisar
            min_win_rate: Win rate mínimo para filtrar
            min_profit_factor: Profit factor mínimo
            lookback_days: Dias para backtest
            delay_seconds: Delay entre downloads (evitar rate limit)
            
        Returns:
            DataFrame com resultados ordenados
        """
        print(f"🔍 Iniciando scanner de {len(tickers)} ativos...")
        print(f"   📊 Estratégia: {self.strategy.get_strategy_name()}")
        print(f"   🎯 Filtros: Win Rate ≥ {min_win_rate}%, PF ≥ {min_profit_factor}")
        
        self.results = []
        successful = 0
        failed = 0
        
        for i, ticker in enumerate(tickers, 1):
            try:
                # Feedback de progresso
                if i % 5 == 0 or i == len(tickers):
                    print(f"   ⏳ Progresso: {i}/{len(tickers)} ({i/len(tickers)*100:.1f}%) - ✅ {successful} | ❌ {failed}")
                
                # Download de dados
                daily_data = get_daily_data(ticker, period="1y")
                weekly_data = get_weekly_data(ticker, period="2y")
                
                if daily_data is None or weekly_data is None or len(daily_data) < 100:
                    failed += 1
                    time.sleep(delay_seconds)
                    continue
                
                # Calcula indicadores
                daily_df = self.strategy.calculate_full(daily_data)
                weekly_df = self.strategy.calculate_full(weekly_data)
                
                # Verifica convergência
                has_conv, conv_info = self.strategy.check_convergence(daily_df, weekly_df)
                
                # Backtest
                backtester = StrategyBacktester(self.strategy)
                backtest_results = backtester.run(daily_df, weekly_df, lookback_days)
                
                metrics = backtest_results['metrics']
                
                # Pega preço atual
                current_price = daily_df['Close'].iloc[-1]
                
                # Salva resultados
                result = {
                    'ticker': ticker,
                    'convergence': has_conv,
                    'current_price': current_price,
                    'stop_loss': conv_info.get('stop_loss', 0),
                    'target': conv_info.get('target', 0),
                    'daily_signal': conv_info.get('daily_signal', False),
                    'weekly_signal': conv_info.get('weekly_signal', False),
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
                successful += 1
                
                # Delay para não sobrecarregar API
                time.sleep(delay_seconds)
                
            except Exception as e:
                failed += 1
                print(f"   ⚠️ Erro em {ticker}: {str(e)[:50]}")
                time.sleep(delay_seconds)
                continue
        
        # Converte para DataFrame
        results_df = pd.DataFrame(self.results)
        
        if results_df.empty:
            print("\n❌ Nenhum ativo analisado com sucesso")
            return results_df
        
        print(f"\n✅ Scanner concluído!")
        print(f"   ✅ Sucesso: {successful}/{len(tickers)}")
        print(f"   ❌ Falhas: {failed}/{len(tickers)}")
        
        # Filtra pelos critérios mínimos
        filtered_df = results_df[
            (results_df['total_trades'] >= 3) &
            (results_df['win_rate'] >= min_win_rate) &
            (results_df['profit_factor'] >= min_profit_factor)
        ].copy()
        
        print(f"   🎯 Ativos que passaram nos filtros: {len(filtered_df)}/{len(results_df)}")
        
        if not filtered_df.empty:
            # Ordena por convergência e profit factor
            filtered_df['score'] = (
                filtered_df['convergence'].astype(int) * 100 +
                filtered_df['profit_factor'] * 10 +
                filtered_df['win_rate']
            )
            filtered_df = filtered_df.sort_values('score', ascending=False)
            
            print(f"\n🏆 Top 5 Oportunidades:")
            for idx, row in filtered_df.head(5).iterrows():
                conv_emoji = "✅" if row['convergence'] else "❌"
                print(f"   {conv_emoji} {row['ticker']}: PF={row['profit_factor']:.2f}, WR={row['win_rate']:.1f}%, Ret={row['total_return']:.2f}%")
        
        return filtered_df if not filtered_df.empty else results_df
    
    def get_convergence_only(self) -> pd.DataFrame:
        """Retorna apenas ativos com convergência"""
        if not self.results:
            return pd.DataFrame()
        
        df = pd.DataFrame(self.results)
        return df[df['convergence'] == True].sort_values('profit_factor', ascending=False)
    
    def get_summary(self) -> Dict:
        """Retorna resumo do scanner"""
        if not self.results:
            return {}
        
        df = pd.DataFrame(self.results)
        
        return {
            'total_scanned': len(df),
            'with_convergence': df['convergence'].sum(),
            'avg_win_rate': df['win_rate'].mean(),
            'avg_profit_factor': df['profit_factor'].mean(),
            'best_ticker': df.loc[df['profit_factor'].idxmax(), 'ticker'] if not df.empty else None,
            'best_profit_factor': df['profit_factor'].max() if not df.empty else 0,
        }
