"""
Multi-Strategy Scanner v2.0
Com Scanner Automático e Otimizador de Parâmetros
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import time

# Imports dos módulos
from src.data.asset_loader import AssetLoader
from src.data.market_data import get_daily_data, get_weekly_data
from src.strategies import get_strategy, list_strategies
from src.ui.charts import create_strategy_chart
from src.backtest import StrategyBacktester
from src.scanner import MultiAssetScanner
from src.optimizer import StrategyOptimizer

# Imports das classes de estratégias
from src.strategies.cacas_channel_strategy import CacasChannelStrategy
from src.strategies.moving_average_strategy import MovingAverageCrossStrategy

# Configuração da página
st.set_page_config(
    page_title="Multi-Strategy Scanner v2",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #262730;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .signal-positive {
        color: #00ff00;
        font-weight: bold;
    }
    .signal-negative {
        color: #ff4444;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Inicializa session state
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
    """Carrega todos os ativos (cached)"""
    loader = AssetLoader("data")
    assets = loader.load_all_assets()
    counts = loader.count_assets()
    return assets, counts

def main():
    # Header
    st.markdown('<h1 class="main-header">🚀 Multi-Strategy Scanner v2.0</h1>', unsafe_allow_html=True)
    st.markdown("**✨ Com Scanner Automático e Otimizador de Parâmetros**")
    st.markdown("---")
    
    # Carrega ativos
    if not st.session_state.assets_loaded:
        with st.spinner("Carregando base de ativos..."):
            st.session_state.all_assets, st.session_state.asset_counts = load_all_assets()
            st.session_state.assets_loaded = True
    
    # Sidebar - Modo de Operação
    st.sidebar.header("🎯 Modo de Operação")
    mode = st.sidebar.radio(
        "Selecione:",
        ["📊 Análise Individual", "🔍 Scanner Automático", "⚙️ Otimizador de Parâmetros"],
        index=0
    )
    
    st.sidebar.markdown("---")
    
    # ========== MODO 1: ANÁLISE INDIVIDUAL ==========
    if mode == "📊 Análise Individual":
        show_individual_analysis()
    
    # ========== MODO 2: SCANNER AUTOMÁTICO ==========
    elif mode == "🔍 Scanner Automático":
        show_scanner_mode()
    
    # ========== MODO 3: OTIMIZADOR ==========
    elif mode == "⚙️ Otimizador de Parâmetros":
        show_optimizer_mode()

def show_individual_analysis():
    """Modo de análise individual de um ativo"""
    
    st.sidebar.subheader("⚙️ Configurações")
    
    # Seletor de Estratégia
    st.sidebar.subheader("📈 Estratégia")
    available_strategies = list_strategies()
    selected_strategy_name = st.sidebar.selectbox(
        "Escolha:",
        available_strategies
    )
    
    # Parâmetros da estratégia
    st.sidebar.subheader("🔧 Parâmetros")
    
    if selected_strategy_name == "Cacas Channel":
        upper = st.sidebar.slider("Upper", 10, 50, 20)
        under = st.sidebar.slider("Under", 10, 50, 30)
        ema = st.sidebar.slider("EMA", 5, 20, 9)
        strategy_params = {'upper': upper, 'under': under, 'ema': ema}
    
    elif selected_strategy_name == "Moving Average Cross":
        fast_period = st.sidebar.slider("EMA Rápida", 5, 30, 9)
        slow_period = st.sidebar.slider("EMA Lenta", 10, 50, 21)
        strategy_params = {'fast_period': fast_period, 'slow_period': slow_period}
    
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
    
    analyze_button = st.sidebar.button("🔍 Analisar", type="primary", use_container_width=True)
    
    # Análise
    if analyze_button or st.session_state.current_ticker != selected_ticker:
        st.session_state.current_ticker = selected_ticker
        
        with st.spinner(f"Analisando {selected_ticker}..."):
            daily_data = get_daily_data(selected_ticker, period="1y")
            weekly_data = get_weekly_data(selected_ticker, period="2y")
            
            if daily_data is None or weekly_data is None:
                st.error(f"❌ Erro ao baixar {selected_ticker}")
                return
            
            daily_df = strategy.calculate_full(daily_data)
            weekly_df = strategy.calculate_full(weekly_data)
            
            has_convergence, conv_info = strategy.check_convergence(daily_df, weekly_df)
            
            st.session_state.daily_df = daily_df
            st.session_state.weekly_df = weekly_df
            st.session_state.convergence_info = conv_info
            
            backtester = StrategyBacktester(strategy)
            st.session_state.backtest_results = backtester.run(daily_df, weekly_df, 252)
    
    # Exibe resultados
    if st.session_state.current_ticker and st.session_state.daily_df is not None:
        display_individual_results(strategy)

def show_scanner_mode():
    """Modo scanner automático"""
    
    st.header("🔍 Scanner Automático de Ativos")
    st.write("Varre múltiplos ativos automaticamente e identifica oportunidades")
    
    st.sidebar.subheader("⚙️ Configurações do Scanner")
    
    # Estratégia
    strategy_name = st.sidebar.selectbox("Estratégia:", list_strategies())
    
    # Parâmetros
    if strategy_name == "Cacas Channel":
        upper = st.sidebar.slider("Upper", 10, 50, 20, key="scan_upper")
        under = st.sidebar.slider("Under", 10, 50, 30, key="scan_under")
        ema = st.sidebar.slider("EMA", 5, 20, 9, key="scan_ema")
        params = {'upper': upper, 'under': under, 'ema': ema}
    else:
        fast = st.sidebar.slider("EMA Rápida", 5, 30, 9, key="scan_fast")
        slow = st.sidebar.slider("EMA Lenta", 10, 50, 21, key="scan_slow")
        params = {'fast_period': fast, 'slow_period': slow}
    
    # Filtros
    st.sidebar.subheader("🎯 Filtros")
    min_win_rate = st.sidebar.slider("Win Rate Mín (%)", 30.0, 90.0, 50.0, 5.0)
    min_pf = st.sidebar.slider("Profit Factor Mín", 1.0, 5.0, 1.5, 0.1)
    
    # Seleção de ativos
    st.sidebar.subheader("📋 Ativos para Varrer")
    market = st.sidebar.selectbox("Mercado:", list(st.session_state.all_assets.keys()), key="scan_market")
    category = st.sidebar.selectbox("Categoria:", list(st.session_state.all_assets[market].keys()), key="scan_cat")
    
    tickers_to_scan = st.session_state.all_assets[market][category]
    
    st.sidebar.info(f"📊 Total: {len(tickers_to_scan)} ativos")
    
    # Botão de scanner
    if st.sidebar.button("🚀 Iniciar Scanner", type="primary", use_container_width=True):
        strategy = get_strategy(strategy_name, **params)
        scanner = MultiAssetScanner(strategy)
        
        with st.spinner(f"Varrendo {len(tickers_to_scan)} ativos..."):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            results = scanner.scan(
                tickers_to_scan,
                min_win_rate=min_win_rate,
                min_profit_factor=min_pf,
                lookback_days=252,
                delay_seconds=0.3
            )
            
            progress_bar.progress(100)
            status_text.success("✅ Scanner concluído!")
            
            st.session_state.scanner_results = results
    
    # Exibe resultados
    if st.session_state.scanner_results is not None and not st.session_state.scanner_results.empty:
        display_scanner_results()

def show_optimizer_mode():
    """Modo otimizador de parâmetros"""
    
    st.header("⚙️ Otimizador de Parâmetros")
    st.write("Encontra a melhor configuração de parâmetros para um ativo")
    
    st.sidebar.subheader("⚙️ Configurações")
    
    # Estratégia
    strategy_name = st.sidebar.selectbox("Estratégia:", list_strategies(), key="opt_strat")
    
    # Ativo
    st.sidebar.subheader("🎯 Ativo")
    market = st.sidebar.selectbox("Mercado:", list(st.session_state.all_assets.keys()), key="opt_market")
    category = st.sidebar.selectbox("Categoria:", list(st.session_state.all_assets[market].keys()), key="opt_cat")
    ticker = st.sidebar.selectbox("Ativo:", st.session_state.all_assets[market][category], key="opt_ticker")
    
    # Grid de parâmetros
    st.sidebar.subheader("🔢 Grid de Parâmetros")
    
    param_grid = {}
    
    if strategy_name == "Cacas Channel":
        st.sidebar.write("**Upper (Resistência)**")
        upper_min = st.sidebar.number_input("Mín", 10, 40, 15, key="opt_upper_min")
        upper_max = st.sidebar.number_input("Máx", 15, 50, 25, key="opt_upper_max")
        upper_step = st.sidebar.number_input("Passo", 1, 10, 5, key="opt_upper_step")
        
        st.sidebar.write("**Under (Suporte)**")
        under_min = st.sidebar.number_input("Mín", 15, 40, 25, key="opt_under_min")
        under_max = st.sidebar.number_input("Máx", 20, 50, 35, key="opt_under_max")
        under_step = st.sidebar.number_input("Passo", 1, 10, 5, key="opt_under_step")
        
        st.sidebar.write("**EMA (Sinal)**")
        ema_min = st.sidebar.number_input("Mín", 5, 15, 7, key="opt_ema_min")
        ema_max = st.sidebar.number_input("Máx", 10, 20, 11, key="opt_ema_max")
        ema_step = st.sidebar.number_input("Passo", 1, 5, 2, key="opt_ema_step")
        
        param_grid = {
            'upper': list(range(upper_min, upper_max + 1, upper_step)),
            'under': list(range(under_min, under_max + 1, under_step)),
            'ema': list(range(ema_min, ema_max + 1, ema_step))
        }
    
    else:  # Moving Average
        st.sidebar.write("**EMA Rápida**")
        fast_min = st.sidebar.number_input("Mín", 5, 20, 7, key="opt_fast_min")
        fast_max = st.sidebar.number_input("Máx", 10, 30, 13, key="opt_fast_max")
        fast_step = st.sidebar.number_input("Passo", 1, 5, 2, key="opt_fast_step")
        
        st.sidebar.write("**EMA Lenta**")
        slow_min = st.sidebar.number_input("Mín", 15, 30, 18, key="opt_slow_min")
        slow_max = st.sidebar.number_input("Máx", 20, 50, 26, key="opt_slow_max")
        slow_step = st.sidebar.number_input("Passo", 1, 10, 4, key="opt_slow_step")
        
        param_grid = {
            'fast_period': list(range(fast_min, fast_max + 1, fast_step)),
            'slow_period': list(range(slow_min, slow_max + 1, slow_step))
        }
    
    # Métrica de otimização
    st.sidebar.subheader("📊 Métrica")
    metric = st.sidebar.selectbox(
        "Otimizar por:",
        ["profit_factor", "win_rate", "total_return", "sharpe_ratio"]
    )
    
    # Calcula combinações
    total_combos = 1
    for values in param_grid.values():
        total_combos *= len(values)
    
    st.sidebar.info(f"🔢 Total de combinações: {total_combos}")
    
    # Botão otimizar
    if st.sidebar.button("🚀 Otimizar", type="primary", use_container_width=True):
        with st.spinner(f"Baixando dados de {ticker}..."):
            daily_data = get_daily_data(ticker, period="1y")
            weekly_data = get_weekly_data(ticker, period="2y")
        
        if daily_data is None or weekly_data is None:
            st.error("❌ Erro ao baixar dados")
            return
        
        # Escolhe classe da estratégia
        strategy_class = CacasChannelStrategy if strategy_name == "Cacas Channel" else MovingAverageCrossStrategy
        
        # Otimiza
        with st.spinner(f"Otimizando {total_combos} combinações..."):
            optimizer = StrategyOptimizer(strategy_class, daily_data, weekly_data)
            best_params, results_df = optimizer.optimize(param_grid, metric=metric)
            
            st.session_state.optimizer_results = {
                'best_params': best_params,
                'results_df': results_df,
                'ticker': ticker,
                'strategy_name': strategy_name,
                'metric': metric
            }
    
    # Exibe resultados
    if st.session_state.optimizer_results is not None:
        display_optimizer_results()

def display_individual_results(strategy):
    """Exibe resultados da análise individual"""
    ticker = st.session_state.current_ticker
    conv_info = st.session_state.convergence_info
    daily_df = st.session_state.daily_df
    backtest_results = st.session_state.backtest_results
    
    st.header(f"📊 {ticker}")
    
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
        st.metric("Preço", f"${daily_df['Close'].iloc[-1]:.2f}")
    
    # Gestão de risco
    st.subheader("🎯 Gestão de Risco")
    rcol1, rcol2, rcol3 = st.columns(3)
    
    with rcol1:
        st.metric("Stop Loss", f"${conv_info.get('stop_loss', 0):.2f}")
    
    with rcol2:
        st.metric("Alvo", f"${conv_info.get('target', 0):.2f}")
    
    with rcol3:
        current = daily_df['Close'].iloc[-1]
        stop = conv_info.get('stop_loss', current)
        target = conv_info.get('target', current)
        rr = ((target - current) / (current - stop)) if (current - stop) > 0 else 0
        st.metric("R/R Ratio", f"{rr:.2f}")
    
    # Gráfico
    st.subheader("📈 Gráfico")
    timeframe = st.selectbox("Timeframe:", ["Diário", "Semanal"])
    
    df_to_plot = daily_df if timeframe == "Diário" else st.session_state.weekly_df
    fig = create_strategy_chart(
        df_to_plot.tail(100),
        ticker,
        timeframe,
        strategy.get_strategy_name(),
        strategy.get_indicator_names()
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Backtest
    st.subheader("📊 Backtest")
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
    
    st.success(f"✅ Scanner encontrou {len(results)} ativos")
    
    # Filtros
    col1, col2 = st.columns(2)
    with col1:
        show_conv_only = st.checkbox("Apenas com convergência", value=True)
    
    df_display = results[results['convergence'] == True] if show_conv_only else results
    
    if df_display.empty:
        st.warning("Nenhum ativo encontrado com os filtros")
        return
    
    # Tabela
    st.dataframe(
        df_display[[
            'ticker', 'convergence', 'current_price', 'win_rate', 
            'profit_factor', 'total_return', 'sharpe_ratio'
        ]].round(2),
        use_container_width=True,
        height=400
    )
    
    # Download
    csv = df_display.to_csv(index=False)
    st.download_button(
        "📥 Download CSV",
        csv,
        f"scanner_results_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
        "text/csv"
    )

def display_optimizer_results():
    """Exibe resultados do otimizador"""
    opt_data = st.session_state.optimizer_results
    
    st.success(f"✅ Otimização concluída para {opt_data['ticker']}")
    
    # Melhores parâmetros
    st.subheader("🏆 Melhor Configuração")
    st.json(opt_data['best_params'])
    
    # Top 10
    st.subheader("📊 Top 10 Configurações")
    top10 = opt_data['results_df'].head(10)
    st.dataframe(top10, use_container_width=True)
    
    # Download
    csv = opt_data['results_df'].to_csv(index=False)
    st.download_button(
        "📥 Download Resultados",
        csv,
        f"optimizer_{opt_data['ticker']}_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
        "text/csv"
    )

if __name__ == "__main__":
    main()
