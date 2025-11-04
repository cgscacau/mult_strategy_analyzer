"""
Strategy Backtester - Teste histórico genérico para qualquer estratégia
Funciona com qualquer classe que herde de BaseStrategy
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime

class StrategyBacktester:
    """
    Backtester genérico que funciona com qualquer estratégia
    
    Calcula métricas de performance:
    - Win Rate e Win Rate Ajustado
    - Retorno Total e Médio
    - Profit Factor
    - Maximum Drawdown
    - Sharpe Ratio
    - Expectância matemática
    """
    
    def __init__(self, strategy):
        """
        Args:
            strategy: Instância de BaseStrategy (qualquer estratégia)
        """
        self.strategy = strategy
        self.trades = []
        self.metrics = {}
    
    def run(self, daily_df: pd.DataFrame, weekly_df: pd.DataFrame, 
            lookback_days: int = 252) -> Dict:
        """
        Executa backtest da estratégia
        
        Args:
            daily_df: DataFrame com dados diários já processados
            weekly_df: DataFrame com dados semanais já processados
            lookback_days: Número de dias para análise
            
        Returns:
            Dicionário com métricas e histórico de trades
        """
        # Limita aos últimos N dias
        if len(daily_df) > lookback_days:
            test_df = daily_df.tail(lookback_days).copy()
        else:
            test_df = daily_df.copy()
        
        # Reset trades
        self.trades = []
        
        # Simula trades baseados nos sinais
        self._simulate_trades(test_df)
        
        # Calcula métricas
        self.metrics = self._calculate_metrics(test_df)
        
        return {
            'metrics': self.metrics,
            'trades': self.trades,
            'strategy_name': self.strategy.get_strategy_name()
        }
    
    def _simulate_trades(self, df: pd.DataFrame):
        """
        Simula trades baseados nos sinais da estratégia
        
        Lógica:
        - Entra quando signal=1 e não está em posição
        - Sai quando: preço atinge stop_loss OU target OU signal vira 0
        """
        in_position = False
        entry_price = 0
        entry_date = None
        stop_loss = 0
        target = 0
        
        for i in range(len(df)):
            row = df.iloc[i]
            
            # Verifica se tem dados válidos
            if pd.isna(row['signal']) or pd.isna(row['Close']):
                continue
            
            # Entrada: Sinal de compra e não está em posição
            if not in_position and row['signal'] == 1:
                in_position = True
                entry_price = row['Close']
                entry_date = row.name
                stop_loss = row.get('stop_loss', entry_price * 0.95)  # Fallback: 5%
                target = row.get('target', entry_price * 1.10)  # Fallback: 10%
                continue
            
            # Saída: Está em posição
            if in_position:
                exit_price = None
                exit_reason = None
                exit_date = row.name
                
                # Verifica stop loss
                if row['Low'] <= stop_loss:
                    exit_price = stop_loss
                    exit_reason = 'stop_loss'
                
                # Verifica target (prioridade: se bateu os dois, considera target)
                elif row['High'] >= target:
                    exit_price = target
                    exit_reason = 'target'
                
                # Verifica saída por sinal (perdeu convergência)
                elif row['signal'] == 0:
                    exit_price = row['Close']
                    exit_reason = 'signal_exit'
                
                # Se saiu, registra trade
                if exit_price:
                    pnl = exit_price - entry_price
                    pnl_pct = (pnl / entry_price) * 100
                    
                    self.trades.append({
                        'entry_date': entry_date,
                        'exit_date': exit_date,
                        'entry_price': entry_price,
                        'exit_price': exit_price,
                        'stop_loss': stop_loss,
                        'target': target,
                        'pnl': pnl,
                        'pnl_pct': pnl_pct,
                        'exit_reason': exit_reason,
                        'duration_days': (exit_date - entry_date).days
                    })
                    
                    # Reset posição
                    in_position = False
                    entry_price = 0
                    entry_date = None
                    stop_loss = 0
                    target = 0
        
        # Se ainda está em posição no final, fecha no último preço
        if in_position:
            last_row = df.iloc[-1]
            exit_price = last_row['Close']
            pnl = exit_price - entry_price
            pnl_pct = (pnl / entry_price) * 100
            
            self.trades.append({
                'entry_date': entry_date,
                'exit_date': last_row.name,
                'entry_price': entry_price,
                'exit_price': exit_price,
                'stop_loss': stop_loss,
                'target': target,
                'pnl': pnl,
                'pnl_pct': pnl_pct,
                'exit_reason': 'end_of_period',
                'duration_days': (last_row.name - entry_date).days
            })
    
    def _calculate_metrics(self, df: pd.DataFrame) -> Dict:
        """
        Calcula métricas de performance do backtest
        """
        if not self.trades:
            return {
                'total_trades': 0,
                'win_rate': 0,
                'win_rate_adjusted': 0,
                'total_return': 0,
                'avg_return': 0,
                'profit_factor': 0,
                'max_drawdown': 0,
                'sharpe_ratio': 0,
                'expectancy': 0,
                'winners': 0,
                'losers': 0,
                'targets_hit': 0,
                'stops_hit': 0,
                'avg_winner': 0,
                'avg_loser': 0,
                'largest_winner': 0,
                'largest_loser': 0,
                'avg_duration_days': 0
            }
        
        # Trades DataFrame para análise
        trades_df = pd.DataFrame(self.trades)
        
        # Métricas básicas
        total_trades = len(trades_df)
        winners = trades_df[trades_df['pnl'] > 0]
        losers = trades_df[trades_df['pnl'] <= 0]
        
        # Win Rate
        win_rate = (len(winners) / total_trades * 100) if total_trades > 0 else 0
        
        # Win Rate Ajustado (só targets vs stops)
        targets = trades_df[trades_df['exit_reason'] == 'target']
        stops = trades_df[trades_df['exit_reason'] == 'stop_loss']
        defined_exits = len(targets) + len(stops)
        win_rate_adjusted = (len(targets) / defined_exits * 100) if defined_exits > 0 else 0
        
        # Retornos
        total_return = trades_df['pnl_pct'].sum()
        avg_return = trades_df['pnl_pct'].mean()
        
        # Profit Factor
        gross_profit = winners['pnl'].sum() if len(winners) > 0 else 0
        gross_loss = abs(losers['pnl'].sum()) if len(losers) > 0 else 0
        profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else 0
        
        # Maximum Drawdown
        cumulative_returns = (1 + trades_df['pnl_pct'] / 100).cumprod()
        running_max = cumulative_returns.expanding().max()
        drawdown = (cumulative_returns - running_max) / running_max * 100
        max_drawdown = abs(drawdown.min())
        
        # Sharpe Ratio (anualizado)
        if len(trades_df) > 1:
            returns_std = trades_df['pnl_pct'].std()
            sharpe_ratio = (avg_return / returns_std * np.sqrt(252)) if returns_std > 0 else 0
        else:
            sharpe_ratio = 0
        
        # Expectância
        win_prob = len(winners) / total_trades if total_trades > 0 else 0
        avg_win = winners['pnl_pct'].mean() if len(winners) > 0 else 0
        loss_prob = len(losers) / total_trades if total_trades > 0 else 0
        avg_loss = losers['pnl_pct'].mean() if len(losers) > 0 else 0
        expectancy = (win_prob * avg_win) + (loss_prob * avg_loss)
        
        return {
            'total_trades': total_trades,
            'win_rate': win_rate,
            'win_rate_adjusted': win_rate_adjusted,
            'total_return': total_return,
            'avg_return': avg_return,
            'profit_factor': profit_factor,
            'max_drawdown': max_drawdown,
            'sharpe_ratio': sharpe_ratio,
            'expectancy': expectancy,
            'winners': len(winners),
            'losers': len(losers),
            'targets_hit': len(targets),
            'stops_hit': len(stops),
            'avg_winner': avg_win,
            'avg_loser': avg_loss,
            'largest_winner': winners['pnl_pct'].max() if len(winners) > 0 else 0,
            'largest_loser': losers['pnl_pct'].min() if len(losers) > 0 else 0,
            'avg_duration_days': trades_df['duration_days'].mean()
        }
    
    def get_trades_dataframe(self) -> pd.DataFrame:
        """Retorna trades como DataFrame"""
        if not self.trades:
            return pd.DataFrame()
        return pd.DataFrame(self.trades)
    
    def get_summary(self) -> str:
        """Retorna resumo textual das métricas"""
        if not self.metrics or self.metrics['total_trades'] == 0:
            return "Nenhum trade encontrado no período de análise."
        
        m = self.metrics
        summary = f"""
📊 **Backtest - {self.strategy.get_strategy_name()}**

**Performance Geral:**
- Total de Trades: {m['total_trades']}
- Win Rate: {m['win_rate']:.1f}%
- Win Rate Ajustado: {m['win_rate_adjusted']:.1f}% (apenas stops vs alvos)
- Retorno Total: {m['total_return']:.2f}%
- Retorno Médio: {m['avg_return']:.2f}%

**Análise Risk/Reward:**
- Profit Factor: {m['profit_factor']:.2f}
- Expectância: {m['expectancy']:.2f}%
- Sharpe Ratio: {m['sharpe_ratio']:.2f}
- Max Drawdown: {m['max_drawdown']:.2f}%

**Distribuição de Trades:**
- ✅ Alvos Atingidos: {m['targets_hit']} ({m['targets_hit']/m['total_trades']*100:.1f}%)
- ❌ Stops Atingidos: {m['stops_hit']} ({m['stops_hit']/m['total_trades']*100:.1f}%)
- 🔄 Saídas por Sinal: {m['total_trades'] - m['targets_hit'] - m['stops_hit']}

**Estatísticas:**
- Média de Ganhos: {m['avg_winner']:.2f}%
- Média de Perdas: {m['avg_loser']:.2f}%
- Maior Ganho: {m['largest_winner']:.2f}%
- Maior Perda: {m['largest_loser']:.2f}%
- Duração Média: {m['avg_duration_days']:.1f} dias
"""
        return summary
