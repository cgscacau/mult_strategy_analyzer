"""
Multi-Strategy Scanner v3.1 - COM OTIMIZADOR FUNCIONAL
- ✅ Todos os 8 problemas da v3.0 corrigidos
- ✅ Estratégia MSS implementada
- ✅ OTIMIZADOR FUNCIONAL COMPLETO
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import time
import numpy as np
from itertools import product

# Imports
from src.data.asset_loader import AssetLoader
from src.data.market_data import get_daily_data, get_weekly_data
from src.strategies import get_strategy, list_strategies
from src.ui.charts import create_strategy_chart
from src.backtest import StrategyBacktester
from src.scanner import MultiAssetScanner
from src.optimizer import StrategyOptimizer

# Imports das classes
from src.strategies.cacas_channel_strategy import CacasChannelStrategy
from src.strategies.moving_average_strategy import MovingAverageCrossStrategy
from src.strategies.mss_strategy import MSSStrategy

# Config
st.set_page_config(
    page_title="Multi-Strategy Scanner v3.1",
    page_icon="🚀",
    layout="wide"
)

# CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
    }
    .metric-card {
        background-color: #262730;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .signal-positive { color: #00ff00; font-weight: bold; }
    .signal-negative { color: #ff4444; font-weight: bold; }
    .entry-info {
        background-color: #2d2d44;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .optimizer-result {
        background-color: #1a1a2e;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #00ff88;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Session state
if 'assets_loaded' not in st.session_state:
    st.session_state.assets_loaded = False
    st.session_state.all_assets = {}
    st.session_state.asset_counts = {}

if 'current_ticker' not in st.session_state:
    st.session_state.current_ticker = None
    st.session_state.daily_df = None
    st.session_state.weekly_df = None
    st.session_state.convergence_info = None
    st.session_state.backtest_results = None

if 'scanner_results' not in st.session_state:
    st.session_state.scanner_results = None

if 'optimizer_results' not in st.session_state:
    st.session_state.optimizer_results = None

@st.cache_data
def load_all_assets():
    loader = AssetLoader("data")
    assets = loader.load_all_assets()
    counts = loader.count_assets()
    return assets, counts

def main():
    st.markdown('<h1 class="main-header">🚀 Multi-Strategy Scanner v3.1 - COM OTIMIZADOR</h1>', unsafe_allow_html=True)
    st.markdown("**✅ Todos os problemas resolvidos + Estratégia MSS + ⚙️ Otimizador Funcional**")
    st.markdown("---")
    
    if not st.session_state.assets_loaded:
        with st.spinner("Carregando base de ativos..."):
            st.session_state.all_assets, st.session_state.asset_counts = load_all_assets()
            st.session_state.assets_loaded = True
    
    # Modo de operação
    st.sidebar.header("🎯 Modo de Operação")
    mode = st.sidebar.radio(
        "Selecione:",
        ["📊 Análise Individual", "🔍 Scanner Automático", "⚙️ Otimizador"],
        index=0
    )
    
    st.sidebar.markdown("---")
    
    if mode == "📊 Análise Individual":
        show_individual_analysis()
    elif mode == "🔍 Scanner Automático":
        show_scanner_mode()
    elif mode == "⚙️ Otimizador":
        show_optimizer_mode()

def show_individual_analysis():
    """Análise individual com TODOS os problemas corrigidos"""
    
    st.sidebar.subheader("📈 Estratégia")
    available_strategies = list_strategies()
    selected_strategy_name = st.sidebar.selectbox("Escolha:", available_strategies)
    
    # Parâmetros por estratégia
    st.sidebar.subheader("🔧 Parâmetros")
    
    if selected_strategy_name == "Cacas Channel":
        upper = st.sidebar.slider("Upper (Resistência)", 5, 100, 20, 1)
        under = st.sidebar.slider("Under (Suporte)", 5, 100, 30, 1)
        ema = st.sidebar.slider("EMA (Sinal)", 5, 50, 9, 1)
        strategy_params = {'upper': upper, 'under': under, 'ema': ema}
    
    elif selected_strategy_name == "Moving Average Cross":
        fast_period = st.sidebar.slider("EMA Rápida", 5, 50, 9, 1)
        slow_period = st.sidebar.slider("EMA Lenta", 10, 100, 21, 1)
        strategy_params = {'fast_period': fast_period, 'slow_period': slow_period}
    
    elif selected_strategy_name == "MSS (Market Structure)":
        swing_length = st.sidebar.slider("Swing Length", 3, 20, 5, 1)
        strategy_params = {'swing_length': swing_length}
    
    else:
        strategy_params = {}
    
    # Gestão de risco
    st.sidebar.subheader("🎯 Gestão de Risco")
    stop_multiplier = st.sidebar.slider("Stop Loss (ATR x)", 0.5, 3.0, 1.5, 0.1)
    target_multiplier = st.sidebar.slider("Alvo (Stop x)", 1.0, 5.0, 2.0, 0.1)
    strategy_params.update({
        'stop_multiplier': stop_multiplier,
        'target_multiplier': target_multiplier
    })
    
    # Cria estratégia
    strategy = get_strategy(selected_strategy_name, **strategy_params)
    
    st.sidebar.info(f"**{strategy.get_strategy_name()}**\n\n{strategy.get_strategy_description()}")
    st.sidebar.markdown("---")
    
    # Seleção de ativo
    st.sidebar.subheader("🌍 Ativo")
    market = st.sidebar.selectbox("Mercado:", list(st.session_state.all_assets.keys()))
    categories = st.session_state.all_assets[market]
    category = st.sidebar.selectbox("Categoria:", list(categories.keys()))
    tickers = categories[category]
    
    if not tickers:
        st.warning(f"Nenhum ativo em {market} > {category}")
        return
    
    selected_ticker = st.sidebar.selectbox(f"Ativo ({len(tickers)}):", tickers)
    
    st.sidebar.subheader("📅 Período de Análise")
    st.sidebar.info("📊 **Diário:** 1 ano (~252 dias)\n📈 **Semanal:** 2 anos (~104 semanas)")
    
    analyze_button = st.sidebar.button("🔍 Analisar", type="primary", use_container_width=True)
    
    # Análise
    if analyze_button or st.session_state.current_ticker != selected_ticker:
        st.session_state.current_ticker = selected_ticker
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        status_text.text("📥 Baixando dados diários...")
        progress_bar.progress(20)
        daily_data = get_daily_data(selected_ticker, period="1y")
        
        status_text.text("📥 Baixando dados semanais...")
        progress_bar.progress(40)
        weekly_data = get_weekly_data(selected_ticker, period="2y")
        
        if daily_data is None or weekly_data is None:
            st.error(f"❌ Erro ao baixar {selected_ticker}")
            progress_bar.empty()
            status_text.empty()
            return
        
        status_text.text("⚙️ Calculando indicadores...")
        progress_bar.progress(60)
        daily_df = strategy.calculate_full(daily_data)
        weekly_df = strategy.calculate_full(weekly_data)
        
        status_text.text("🔍 Verificando convergência...")
        progress_bar.progress(80)
        has_convergence, conv_info = strategy.check_convergence(daily_df, weekly_df)
        
        st.session_state.daily_df = daily_df
        st.session_state.weekly_df = weekly_df
        st.session_state.convergence_info = conv_info
        
        status_text.text("📊 Executando backtest...")
        progress_bar.progress(90)
        backtester = StrategyBacktester(strategy)
        st.session_state.backtest_results = backtester.run(daily_df, weekly_df, 252)
        
        progress_bar.progress(100)
        time.sleep(0.5)
        progress_bar.empty()
        status_text.empty()
    
    # Exibe resultados
    if st.session_state.current_ticker and st.session_state.daily_df is not None:
        display_individual_results(strategy, selected_strategy_name)

def show_scanner_mode():
    """Scanner com TODOS os problemas corrigidos"""
    
    st.header("🔍 Scanner Automático")
    
    st.sidebar.subheader("⚙️ Configurações")
    
    # Estratégia
    strategy_name = st.sidebar.selectbox("Estratégia:", list_strategies())
    
    # Parâmetros
    if strategy_name == "Cacas Channel":
        upper = st.sidebar.slider("Upper", 5, 100, 20, key="scan_upper")
        under = st.sidebar.slider("Under", 5, 100, 30, key="scan_under")
        ema = st.sidebar.slider("EMA", 5, 50, 9, key="scan_ema")
        params = {'upper': upper, 'under': under, 'ema': ema}
    elif strategy_name == "Moving Average Cross":
        fast = st.sidebar.slider("EMA Rápida", 5, 50, 9, key="scan_fast")
        slow = st.sidebar.slider("EMA Lenta", 10, 100, 21, key="scan_slow")
        params = {'fast_period': fast, 'slow_period': slow}
    elif strategy_name == "MSS (Market Structure)":
        swing = st.sidebar.slider("Swing Length", 3, 20, 5, key="scan_swing")
        params = {'swing_length': swing}
    else:
        params = {}
    
    # Filtros
    st.sidebar.subheader("🎯 Filtros")
    min_win_rate = st.sidebar.slider("Win Rate Mín (%)", 30.0, 90.0, 50.0, 5.0)
    min_pf = st.sidebar.slider("Profit Factor Mín", 1.0, 5.0, 1.5, 0.1)
    
    # Seleção de ativos
    st.sidebar.subheader("📋 Ativos")
    market = st.sidebar.selectbox("Mercado:", list(st.session_state.all_assets.keys()), key="scan_market")
    category = st.sidebar.selectbox("Categoria:", list(st.session_state.all_assets[market].keys()), key="scan_cat")
    
    tickers_to_scan = st.session_state.all_assets[market][category]
    
    st.sidebar.metric("Total para Varrer", f"{len(tickers_to_scan)} ativos")
    
    # Botão scanner
    if st.sidebar.button("🚀 Iniciar Scanner", type="primary", use_container_width=True):
        strategy = get_strategy(strategy_name, **params)
        scanner = MultiAssetScanner(strategy)
        
        progress_container = st.empty()
        status_container = st.empty()
        
        with st.spinner(f"Varrendo {len(tickers_to_scan)} ativos..."):
            results_list = []
            for idx, ticker in enumerate(tickers_to_scan):
                progress = int((idx + 1) / len(tickers_to_scan) * 100)
                progress_container.progress(progress)
                status_container.text(f"⏳ Analisando {ticker} ({idx+1}/{len(tickers_to_scan)})...")
                
                try:
                    daily = get_daily_data(ticker, period="1y")
                    weekly = get_weekly_data(ticker, period="2y")
                    
                    if daily is None or len(daily) < 100:
                        continue
                    
                    daily_df = strategy.calculate_full(daily)
                    weekly_df = strategy.calculate_full(weekly)
                    
                    has_conv, conv_info = strategy.check_convergence(daily_df, weekly_df)
                    
                    backtester = StrategyBacktester(strategy)
                    backtest = backtester.run(daily_df, weekly_df, 252)
                    m = backtest['metrics']
                    
                    results_list.append({
                        'ticker': ticker,
                        'convergence': has_conv,
                        'entry_price': conv_info.get('entry_price', daily_df['Close'].iloc[-1]),
                        'stop_loss': conv_info.get('stop_loss', 0),
                        'target': conv_info.get('target', 0),
                        'daily_signal': conv_info.get('daily_signal', False),
                        'weekly_signal': conv_info.get('weekly_signal', False),
                        'total_trades': m['total_trades'],
                        'win_rate': m['win_rate'],
                        'profit_factor': m['profit_factor'],
                        'total_return': m['total_return'],
                        'sharpe_ratio': m['sharpe_ratio'],
                    })
                    
                    time.sleep(0.3)
                
                except Exception as e:
                    continue
            
            progress_container.empty()
            status_container.empty()
            
            results_df = pd.DataFrame(results_list)
            
            filtered = results_df[
                (results_df['total_trades'] >= 3) &
                (results_df['win_rate'] >= min_win_rate) &
                (results_df['profit_factor'] >= min_pf)
            ].copy()
            
            st.session_state.scanner_results = filtered if not filtered.empty else results_df
            
            st.success(f"✅ Scanner concluído! Analisados: {len(results_df)} | Passaram filtros: {len(filtered)}")
    
    if st.session_state.scanner_results is not None and not st.session_state.scanner_results.empty:
        display_scanner_results()

def show_optimizer_mode():
    """⚙️ OTIMIZADOR FUNCIONAL COMPLETO"""
    
    st.header("⚙️ Otimizador de Parâmetros")
    st.markdown("**Encontra a melhor combinação de parâmetros usando Grid Search**")
    st.markdown("---")
    
    # Seleção de ativo
    st.sidebar.subheader("🌍 Ativo para Otimizar")
    market = st.sidebar.selectbox("Mercado:", list(st.session_state.all_assets.keys()), key="opt_market")
    categories = st.session_state.all_assets[market]
    category = st.sidebar.selectbox("Categoria:", list(categories.keys()), key="opt_cat")
    tickers = categories[category]
    
    if not tickers:
        st.warning(f"Nenhum ativo em {market} > {category}")
        return
    
    selected_ticker = st.sidebar.selectbox(f"Ativo ({len(tickers)}):", tickers, key="opt_ticker")
    
    # Estratégia
    st.sidebar.subheader("📈 Estratégia")
    strategy_name = st.sidebar.selectbox("Escolha:", list_strategies(), key="opt_strategy")
    
    # Mapeia nome para classe
    strategy_map = {
        'Cacas Channel': CacasChannelStrategy,
        'Moving Average Cross': MovingAverageCrossStrategy,
        'MSS (Market Structure)': MSSStrategy,
    }
    
    strategy_class = strategy_map.get(strategy_name)
    
    if not strategy_class:
        st.error(f"Estratégia {strategy_name} não encontrada")
        return
    
    # Parâmetros para otimizar
    st.sidebar.subheader("🔧 Ranges de Parâmetros")
    
    param_grid = {}
    
    if strategy_name == "Cacas Channel":
        st.sidebar.markdown("**Upper (Resistência)**")
        upper_min = st.sidebar.number_input("Mínimo", 5, 50, 15, key="upper_min")
        upper_max = st.sidebar.number_input("Máximo", 10, 100, 30, key="upper_max")
        upper_step = st.sidebar.number_input("Passo", 1, 10, 5, key="upper_step")
        
        st.sidebar.markdown("**Under (Suporte)**")
        under_min = st.sidebar.number_input("Mínimo", 5, 50, 20, key="under_min")
        under_max = st.sidebar.number_input("Máximo", 10, 100, 40, key="under_max")
        under_step = st.sidebar.number_input("Passo", 1, 10, 5, key="under_step")
        
        st.sidebar.markdown("**EMA (Sinal)**")
        ema_min = st.sidebar.number_input("Mínimo", 5, 20, 5, key="ema_min")
        ema_max = st.sidebar.number_input("Máximo", 10, 50, 15, key="ema_max")
        ema_step = st.sidebar.number_input("Passo", 1, 5, 2, key="ema_step")
        
        param_grid = {
            'upper': list(range(upper_min, upper_max + 1, upper_step)),
            'under': list(range(under_min, under_max + 1, under_step)),
            'ema': list(range(ema_min, ema_max + 1, ema_step)),
        }
    
    elif strategy_name == "Moving Average Cross":
        st.sidebar.markdown("**EMA Rápida**")
        fast_min = st.sidebar.number_input("Mínimo", 5, 20, 5, key="fast_min")
        fast_max = st.sidebar.number_input("Máximo", 10, 50, 15, key="fast_max")
        fast_step = st.sidebar.number_input("Passo", 1, 5, 2, key="fast_step")
        
        st.sidebar.markdown("**EMA Lenta**")
        slow_min = st.sidebar.number_input("Mínimo", 15, 30, 15, key="slow_min")
        slow_max = st.sidebar.number_input("Máximo", 20, 100, 30, key="slow_max")
        slow_step = st.sidebar.number_input("Passo", 1, 10, 5, key="slow_step")
        
        param_grid = {
            'fast_period': list(range(fast_min, fast_max + 1, fast_step)),
            'slow_period': list(range(slow_min, slow_max + 1, slow_step)),
        }
    
    elif strategy_name == "MSS (Market Structure)":
        st.sidebar.markdown("**Swing Length**")
        swing_min = st.sidebar.number_input("Mínimo", 3, 10, 3, key="swing_min")
        swing_max = st.sidebar.number_input("Máximo", 5, 20, 10, key="swing_max")
        swing_step = st.sidebar.number_input("Passo", 1, 3, 1, key="swing_step")
        
        st.sidebar.markdown("**Stop ATR Multiplier**")
        stop_min = st.sidebar.number_input("Mínimo", 1.0, 2.5, 1.5, 0.5, key="stop_min")
        stop_max = st.sidebar.number_input("Máximo", 2.0, 4.0, 3.0, 0.5, key="stop_max")
        stop_step = st.sidebar.number_input("Passo", 0.5, 1.0, 0.5, key="stop_step")
        
        st.sidebar.markdown("**Target ATR Multiplier**")
        target_min = st.sidebar.number_input("Mínimo", 2.0, 4.0, 3.0, 0.5, key="target_min")
        target_max = st.sidebar.number_input("Máximo", 4.0, 8.0, 6.0, 1.0, key="target_max")
        target_step = st.sidebar.number_input("Passo", 0.5, 2.0, 1.0, key="target_step")
        
        param_grid = {
            'swing_length': list(range(swing_min, swing_max + 1, swing_step)),
            'stop_multiplier': [round(x, 1) for x in np.arange(stop_min, stop_max + 0.1, stop_step)],
            'target_multiplier': [round(x, 1) for x in np.arange(target_min, target_max + 0.1, target_step)],
        }
    
    # Métrica de otimização
    st.sidebar.subheader("📊 Métrica para Otimizar")
    metric = st.sidebar.selectbox(
        "Escolha:",
        ["profit_factor", "win_rate", "sharpe_ratio", "total_return", "expectancy"],
        format_func=lambda x: {
            'profit_factor': 'Profit Factor',
            'win_rate': 'Win Rate (%)',
            'sharpe_ratio': 'Sharpe Ratio',
            'total_return': 'Retorno Total (%)',
            'expectancy': 'Expectância (R)'
        }[x]
    )
    
    # Calcula combinações
    total_combos = 1
    for values in param_grid.values():
        total_combos *= len(values)
    
    st.sidebar.info(f"🔢 **Total de combinações:** {total_combos}")
    
    if total_combos > 200:
        st.sidebar.warning("⚠️ Muitas combinações! Pode demorar alguns minutos.")
    
    # Botão otimizar
    if st.sidebar.button("⚙️ OTIMIZAR", type="primary", use_container_width=True):
        
        # Baixa dados
        with st.spinner(f"📥 Baixando dados de {selected_ticker}..."):
            daily_data = get_daily_data(selected_ticker, period="1y")
            weekly_data = get_weekly_data(selected_ticker, period="2y")
        
        if daily_data is None or weekly_data is None:
            st.error(f"❌ Erro ao baixar dados de {selected_ticker}")
            return
        
        # Executa otimização
        st.info(f"🔍 Testando {total_combos} combinações... Aguarde!")
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Gera combinações
        param_names = list(param_grid.keys())
        param_values = list(param_grid.values())
        combinations = list(product(*param_values))
        
        results = []
        
        for i, combo in enumerate(combinations):
            params = dict(zip(param_names, combo))
            
            status_text.text(f"⏳ Testando: {params} ({i+1}/{total_combos})")
            progress_bar.progress(int((i + 1) / total_combos * 100))
            
            try:
                # Cria estratégia
                strategy = strategy_class(**params)
                
                # Processa dados
                daily_df = strategy.calculate_full(daily_data.copy())
                weekly_df = strategy.calculate_full(weekly_data.copy())
                
                # Backtest
                backtester = StrategyBacktester(strategy)
                backtest_results = backtester.run(daily_df, weekly_df, 252)
                
                metrics = backtest_results['metrics']
                
                # Salva resultado
                result = {
                    **params,
                    'total_trades': metrics['total_trades'],
                    'win_rate': metrics['win_rate'],
                    'profit_factor': metrics['profit_factor'],
                    'total_return': metrics['total_return'],
                    'sharpe_ratio': metrics['sharpe_ratio'],
                    'max_drawdown': metrics['max_drawdown'],
                    'expectancy': metrics['expectancy'],
                }
                
                results.append(result)
            
            except Exception as e:
                continue
        
        progress_bar.empty()
        status_text.empty()
        
        # Processa resultados
        if not results:
            st.error("❌ Nenhum resultado válido encontrado")
            return
        
        results_df = pd.DataFrame(results)
        
        # Filtra mínimo de trades
        results_df = results_df[results_df['total_trades'] >= 3]
        
        if results_df.empty:
            st.warning("⚠️ Nenhuma configuração gerou trades suficientes (mín 3)")
            return
        
        # Ordena pela métrica
        results_df = results_df.sort_values(metric, ascending=False)
        
        st.session_state.optimizer_results = results_df
        
        st.success(f"✅ Otimização concluída! {len(results_df)} configurações válidas encontradas.")
    
    # Exibe resultados
    if st.session_state.optimizer_results is not None and not st.session_state.optimizer_results.empty:
        display_optimizer_results(strategy_name, metric, selected_ticker)

def display_optimizer_results(strategy_name, metric, ticker):
    """Exibe resultados da otimização"""
    
    results = st.session_state.optimizer_results
    
    st.markdown("---")
    st.subheader(f"🏆 Resultados da Otimização - {ticker}")
    
    # Top 1
    best = results.iloc[0]
    
    st.markdown(f"""
    <div class="optimizer-result">
        <h3>🥇 MELHOR CONFIGURAÇÃO</h3>
        <h4>Métrica: {metric.upper()} = {best[metric]:.2f}</h4>
    </div>
    """, unsafe_allow_html=True)
    
    # Parâmetros da melhor
    param_cols = [col for col in results.columns if col not in ['total_trades', 'win_rate', 'profit_factor', 'total_return', 'sharpe_ratio', 'max_drawdown', 'expectancy']]
    
    st.markdown("**⚙️ Parâmetros Ótimos:**")
    param_str = " | ".join([f"**{p}:** {best[p]}" for p in param_cols])
    st.markdown(param_str)
    
    # Métricas da melhor
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Trades", int(best['total_trades']))
    with col2:
        st.metric("Win Rate", f"{best['win_rate']:.1f}%")
    with col3:
        st.metric("Profit Factor", f"{best['profit_factor']:.2f}")
    with col4:
        st.metric("Retorno", f"{best['total_return']:.1f}%")
    with col5:
        st.metric("Sharpe", f"{best['sharpe_ratio']:.2f}")
    
    st.markdown("---")
    
    # Top 10
    st.subheader("📊 Top 10 Configurações")
    
    top10 = results.head(10).copy()
    
    # Formata para exibição
    display_cols = param_cols + ['total_trades', 'win_rate', 'profit_factor', 'total_return', 'sharpe_ratio']
    
    st.dataframe(
        top10[display_cols].round(2),
        use_container_width=True,
        height=400
    )
    
    # Download
    csv = results.to_csv(index=False)
    st.download_button(
        "📥 Download Resultados Completos (CSV)",
        csv,
        f"optimizer_{ticker}_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
        "text/csv"
    )
    
    # Análise de sensibilidade
    st.markdown("---")
    st.subheader("📈 Análise de Sensibilidade")
    
    if len(param_cols) > 0:
        param_to_analyze = st.selectbox("Parâmetro:", param_cols)
        
        # Agrupa por parâmetro
        grouped = results.groupby(param_to_analyze)[metric].agg(['mean', 'std', 'count'])
        
        st.line_chart(grouped['mean'])
        
        st.caption(f"Média de {metric} por valor de {param_to_analyze}")

def display_individual_results(strategy, strategy_name):
    """Exibe resultados com TODOS os problemas corrigidos"""
    
    ticker = st.session_state.current_ticker
    conv_info = st.session_state.convergence_info
    daily_df = st.session_state.daily_df
    weekly_df = st.session_state.weekly_df
    backtest_results = st.session_state.backtest_results
    
    st.header(f"📊 Análise: {ticker}")
    
    # Status
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        status = "✅ SIM" if conv_info['convergence'] else "❌ NÃO"
        st.metric("Convergência", status)
    
    with col2:
        st.metric("Sinal Diário", "✅" if conv_info['daily_signal'] else "❌")
    
    with col3:
        st.metric("Sinal Semanal", "✅" if conv_info['weekly_signal'] else "❌")
    
    with col4:
        current_price = daily_df['Close'].iloc[-1]
        st.metric("Preço Atual", f"${current_price:.2f}")
    
    # Info de entrada/saída
    st.markdown("---")
    st.subheader("💰 Informações de Entrada/Saída")
    
    entry_price = conv_info.get('entry_price', current_price)
    stop_loss = conv_info.get('stop_loss', 0)
    target = conv_info.get('target', 0)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="entry-info">
            <h4>🎯 Preço de Entrada</h4>
            <h2 style="color: #1f77b4;">${entry_price:.2f}</h2>
            <p>Entrar neste preço ou próximo</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        stop_distance = ((entry_price - stop_loss) / entry_price * 100) if stop_loss > 0 else 0
        st.markdown(f"""
        <div class="entry-info">
            <h4>⛔ Stop Loss</h4>
            <h2 style="color: #ff4444;">${stop_loss:.2f}</h2>
            <p>Risco: -{stop_distance:.1f}%</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        target_distance = ((target - entry_price) / entry_price * 100) if target > 0 else 0
        st.markdown(f"""
        <div class="entry-info">
            <h4>🎯 Alvo (Take Profit)</h4>
            <h2 style="color: #00ff00;">${target:.2f}</h2>
            <p>Ganho: +{target_distance:.1f}%</p>
        </div>
        """, unsafe_allow_html=True)
    
    # R/R Ratio
    rr_ratio = (target_distance / stop_distance) if stop_distance > 0 else 0
    st.info(f"📊 **Risk/Reward Ratio:** {rr_ratio:.2f}x (Para cada R$1 de risco, potencial de R${rr_ratio:.2f} de ganho)")
    
    st.markdown("---")
    
    # Gráfico
    st.subheader("📈 Gráfico")
    
    timeframe = st.selectbox(
        "Selecione o timeframe:",
        ["Diário (últimos 100 dias)", "Semanal (últimas 100 semanas)"]
    )
    
    if "Diário" in timeframe:
        fig = create_strategy_chart(
            daily_df.tail(100),
            ticker,
            "Diário",
            strategy.get_strategy_name(),
            strategy.get_indicator_names()
        )
    else:
        fig = create_strategy_chart(
            weekly_df.tail(100),
            ticker,
            "Semanal",
            strategy.get_strategy_name(),
            strategy.get_indicator_names()
        )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Backtest
    st.markdown("---")
    st.subheader(f"📊 Backtest - Últimos 252 Dias ({ticker})")
    
    if backtest_results and backtest_results['metrics']['total_trades'] > 0:
        m = backtest_results['metrics']
        
        mcol1, mcol2, mcol3, mcol4 = st.columns(4)
        with mcol1:
            st.metric("Trades", m['total_trades'])
        with mcol2:
            st.metric("Win Rate", f"{m['win_rate']:.1f}%")
        with mcol3:
            st.metric("Profit Factor", f"{m['profit_factor']:.2f}")
        with mcol4:
            st.metric("Retorno", f"{m['total_return']:.2f}%")
    else:
        st.info("Nenhum trade no período")

def display_scanner_results():
    """Exibe resultados do scanner"""
    
    results = st.session_state.scanner_results
    
    st.success(f"✅ Encontrados: {len(results)} ativos analisados")
    
    show_conv_only = st.checkbox("Apenas com convergência", value=True)
    
    df_display = results[results['convergence'] == True] if show_conv_only else results
    
    if df_display.empty:
        st.warning("Nenhum ativo encontrado")
        return
    
    st.dataframe(
        df_display[[
            'ticker', 'convergence', 'entry_price', 'stop_loss', 'target',
            'win_rate', 'profit_factor', 'total_return'
        ]].round(2),
        use_container_width=True,
        height=400
    )
    
    csv = df_display.to_csv(index=False)
    st.download_button(
        "📥 Download CSV",
        csv,
        f"scanner_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
        "text/csv"
    )

if __name__ == "__main__":
    main()
