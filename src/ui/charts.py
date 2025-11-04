"""
Charts Module - Geração de gráficos com Plotly
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from typing import Dict, List

def create_strategy_chart(df: pd.DataFrame, ticker: str, timeframe: str, 
                         strategy_name: str, indicator_names: List[str]) -> go.Figure:
    """
    Cria gráfico baseado na estratégia selecionada
    
    Args:
        df: DataFrame com dados e indicadores calculados
        ticker: Nome do ativo
        timeframe: 'Diário' ou 'Semanal'
        strategy_name: Nome da estratégia
        indicator_names: Lista de nomes dos indicadores a plotar
    """
    fig = make_subplots(
        rows=2, cols=1,
        row_heights=[0.7, 0.3],
        shared_xaxes=True,
        vertical_spacing=0.05,
        subplot_titles=(f'{ticker} - {timeframe}', 'Volume')
    )
    
    # Candlestick
    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name='Preço',
            showlegend=False
        ),
        row=1, col=1
    )
    
    # Plota indicadores específicos da estratégia
    if strategy_name == "Cacas Channel":
        _plot_cacas_indicators(fig, df)
    elif strategy_name == "Moving Average Cross":
        _plot_ma_indicators(fig, df)
    elif "MSS" in strategy_name or "Market Structure" in strategy_name:
        _plot_mss_indicators(fig, df)
    
    # Volume
    colors = ['red' if df['Close'].iloc[i] < df['Open'].iloc[i] else 'green' 
              for i in range(len(df))]
    
    fig.add_trace(
        go.Bar(
            x=df.index,
            y=df['Volume'],
            name='Volume',
            marker_color=colors,
            showlegend=False
        ),
        row=2, col=1
    )
    
    # Layout
    fig.update_layout(
        title=f'{strategy_name} - {ticker} ({timeframe})',
        xaxis_title='',
        yaxis_title='Preço',
        template='plotly_dark',
        height=600,
        xaxis_rangeslider_visible=False
    )
    
    return fig

def _plot_cacas_indicators(fig, df):
    """Plota indicadores do Cacas Channel"""
    # Verifica se colunas existem
    if 'cacas_upper' not in df.columns:
        return
    
    # Linha Superior (Vermelha/Resistência)
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df['cacas_upper'],
            name='Superior (Resistência)',
            line=dict(color='red', width=1.5),
            opacity=0.7
        ),
        row=1, col=1
    )
    
    # Linha Inferior (Verde/Suporte)
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df['cacas_under'],
            name='Inferior (Suporte)',
            line=dict(color='green', width=1.5),
            opacity=0.7
        ),
        row=1, col=1
    )
    
    # Linha Média (Branca/Tendência)
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df['cacas_mid'],
            name='Média (Tendência)',
            line=dict(color='white', width=2)
        ),
        row=1, col=1
    )
    
    # EMA (Laranja/Sinal)
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df['ema'],
            name='EMA (Sinal)',
            line=dict(color='orange', width=2)
        ),
        row=1, col=1
    )

def _plot_ma_indicators(fig, df):
    """Plota indicadores do Moving Average Cross"""
    # Verifica se colunas existem
    if 'ema_fast' not in df.columns:
        return
    
    # EMA Rápida (Azul)
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df['ema_fast'],
            name='EMA Rápida',
            line=dict(color='cyan', width=2)
        ),
        row=1, col=1
    )
    
    # EMA Lenta (Laranja)
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df['ema_slow'],
            name='EMA Lenta',
            line=dict(color='orange', width=2)
        ),
        row=1, col=1
    )
    
    # Marca cruzamentos
    crossovers = df[df['signal'].diff() == 1]
    if not crossovers.empty:
        fig.add_trace(
            go.Scatter(
                x=crossovers.index,
                y=crossovers['Close'],
                mode='markers',
                name='Cruzamento',
                marker=dict(color='lime', size=10, symbol='triangle-up')
            ),
            row=1, col=1
        )

def _plot_mss_indicators(fig, df):
    """Plota indicadores da estratégia MSS"""
    # Verifica se colunas existem
    if 'last_swing_high' not in df.columns:
        return
    
    # Swing Highs (Topos)
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df['last_swing_high'],
            name='Swing High',
            line=dict(color='red', width=2, dash='dash'),
            mode='lines'
        ),
        row=1, col=1
    )
    
    # Swing Lows (Fundos)
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df['last_swing_low'],
            name='Swing Low',
            line=dict(color='green', width=2, dash='dash'),
            mode='lines'
        ),
        row=1, col=1
    )
    
    # Linha da Estrutura
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df['structure_line'],
            name='Estrutura de Mercado',
            line=dict(color='yellow', width=1.5, dash='dot'),
            opacity=0.6
        ),
        row=1, col=1
    )
    
    # Marca pontos de BOS/MSS
    if 'signal_type' in df.columns:
        # BOS/MSS Bullish
        bull_signals = df[df['signal_type'].str.contains('BULL', na=False)]
        if not bull_signals.empty:
            fig.add_trace(
                go.Scatter(
                    x=bull_signals.index,
                    y=bull_signals['Close'],
                    mode='markers+text',
                    name='BOS/MSS Bullish',
                    marker=dict(color='lime', size=12, symbol='triangle-up'),
                    text=bull_signals['signal_type'],
                    textposition='bottom center',
                    textfont=dict(size=8)
                ),
                row=1, col=1
            )
        
        # BOS/MSS Bearish
        bear_signals = df[df['signal_type'].str.contains('BEAR', na=False)]
        if not bear_signals.empty:
            fig.add_trace(
                go.Scatter(
                    x=bear_signals.index,
                    y=bear_signals['Close'],
                    mode='markers+text',
                    name='BOS/MSS Bearish',
                    marker=dict(color='red', size=12, symbol='triangle-down'),
                    text=bear_signals['signal_type'],
                    textposition='top center',
                    textfont=dict(size=8)
                ),
                row=1, col=1
            )
