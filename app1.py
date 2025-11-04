"""
Cacas Channel Multi-Strategy Scanner - Versão com Múltiplas Estratégias
Scanner de ativos brasileiros, americanos e criptomoedas com análise multi-timeframe
Suporta múltiplas estratégias de trading com backtest completo
"""

import streamlit as st
import pandas as pd
from datetime import datetime

# Imports dos módulos
from src.data.asset_loader import AssetLoader
from src.data.market_data import get_daily_data, get_weekly_data
from src.strategies import get_strategy, list_strategies
from src.ui.charts import create_strategy_chart
from src.backtest import StrategyBacktester

# Configuração da página
st.set_page_config(
    page_title="Multi-Strategy Scanner",
    page_icon="📊",
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

@st.cache_data
def load_all_assets():
    """Carrega todos os ativos (cached)"""
    loader = AssetLoader("data")
    assets = loader.load_all_assets()
    counts = loader.count_assets()
    return assets, counts

def main():
    # Header
    st.markdown('<h1 class="main-header">📊 Multi-Strategy Scanner</h1>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Carrega ativos
    if not st.session_state.assets_loaded:
        with st.spinner("Carregando base de ativos..."):
            st.session_state.all_assets, st.session_state.asset_counts = load_all_assets()
            st.session_state.assets_loaded = True
    
    # Sidebar - Seleção de Estratégia
    st.sidebar.header("⚙️ Configurações")
    
    # Seletor de Estratégia
    st.sidebar.subheader("📈 Estratégia de Trading")
    available_strategies = list_strategies()
    selected_strategy_name = st.sidebar.selectbox(
        "Escolha a estratégia:",
        available_strategies,
        help="Selecione qual estratégia de trading usar para análise"
    )
    
    # Parâmetros específicos da estratégia
    st.sidebar.subheader("🔧 Parâmetros")
    
    if selected_strategy_name == "Cacas Channel":
        upper = st.sidebar.slider("Upper (Resistência)", 10, 50, 20)
        under = st.sidebar.slider("Under (Suporte)", 10, 50, 30)
        ema = st.sidebar.slider("EMA (Sinal)", 5, 20, 9)
        strategy_params = {'upper': upper, 'under': under, 'ema': ema}
    
    elif selected_strategy_name == "Moving Average Cross":
        fast_period = st.sidebar.slider("EMA Rápida", 5, 30, 9)
        slow_period = st.sidebar.slider("EMA Lenta", 10, 50, 21)
        strategy_params = {'fast_period': fast_period, 'slow_period': slow_period}
    
    else:
        strategy_params = {}
    
    # Parâmetros de gestão de risco (comuns a todas estratégias)
    st.sidebar.subheader("🎯 Gestão de Risco")
    stop_multiplier = st.sidebar.slider("Stop Loss (ATR x)", 0.5, 3.0, 1.5, 0.1)
    target_multiplier = st.sidebar.slider("Alvo (Stop x)", 1.0, 5.0, 2.0, 0.1)
    strategy_params.update({
        'stop_multiplier': stop_multiplier,
        'target_multiplier': target_multiplier
    })
    
    # Cria instância da estratégia
    strategy = get_strategy(selected_strategy_name, **strategy_params)
    
    # Exibe descrição da estratégia
    st.sidebar.info(f"**{strategy.get_strategy_name()}**\n\n{strategy.get_strategy_description()}")
    
    st.sidebar.markdown("---")
    
    # Seleção de Mercado e Ativo
    st.sidebar.subheader("🌍 Seleção de Ativo")
    
    # Conta total de ativos
    total_assets = sum(
        sum(cats.values()) for cats in st.session_state.asset_counts.values()
    )
    st.sidebar.metric("Total de Ativos", f"{total_assets:,}")
    
    # Seletor de mercado
    market = st.sidebar.selectbox(
        "Mercado:",
        list(st.session_state.all_assets.keys())
    )
    
    # Seletor de categoria
    categories = st.session_state.all_assets[market]
    category = st.sidebar.selectbox(
        "Categoria:",
        list(categories.keys())
    )
    
    # Seletor de ativo
    tickers = categories[category]
    
    if not tickers:
        st.warning(f"Nenhum ativo encontrado em {market} > {category}")
        return
    
    selected_ticker = st.sidebar.selectbox(
        f"Ativo ({len(tickers)} disponíveis):",
        tickers
    )
    
    # Botão de análise
    analyze_button = st.sidebar.button("🔍 Analisar Ativo", type="primary", use_container_width=True)
    
    # Análise do ativo
    if analyze_button or st.session_state.current_ticker != selected_ticker:
        st.session_state.current_ticker = selected_ticker
        
        with st.spinner(f"Baixando dados de {selected_ticker}..."):
            # Download dos dados
            daily_data = get_daily_data(selected_ticker, period="1y")
            weekly_data = get_weekly_data(selected_ticker, period="2y")
            
            if daily_data is None or weekly_data is None:
                st.error(f"❌ Não foi possível baixar dados de {selected_ticker}")
                return
            
            # Calcula indicadores da estratégia
            daily_df = strategy.calculate_full(daily_data)
            weekly_df = strategy.calculate_full(weekly_data)
            
            # Verifica convergência
            has_convergence, conv_info = strategy.check_convergence(daily_df, weekly_df)
            
            # Salva no session state
            st.session_state.daily_df = daily_df
            st.session_state.weekly_df = weekly_df
            st.session_state.convergence_info = conv_info
            
            # Executa backtest
            backtester = StrategyBacktester(strategy)
            backtest_results = backtester.run(daily_df, weekly_df, lookback_days=252)
            st.session_state.backtest_results = backtest_results
    
    # Exibe resultados (se houver)
    if st.session_state.current_ticker and st.session_state.daily_df is not None:
        ticker = st.session_state.current_ticker
        daily_df = st.session_state.daily_df
        weekly_df = st.session_state.weekly_df
        conv_info = st.session_state.convergence_info
        backtest_results = st.session_state.backtest_results
        
        # Status de Convergência
        st.header(f"📊 Análise: {ticker}")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            convergence_status = "✅ SIM" if conv_info['convergence'] else "❌ NÃO"
            status_class = "signal-positive" if conv_info['convergence'] else "signal-negative"
            st.markdown(f'<div class="metric-card"><h3>Convergência</h3><p class="{status_class}">{convergence_status}</p></div>', 
                       unsafe_allow_html=True)
        
        with col2:
            daily_status = "✅" if conv_info['daily_signal'] else "❌"
            st.markdown(f'<div class="metric-card"><h3>Sinal Diário</h3><p>{daily_status}</p></div>', 
                       unsafe_allow_html=True)
        
        with col3:
            weekly_status = "✅" if conv_info['weekly_signal'] else "❌"
            st.markdown(f'<div class="metric-card"><h3>Sinal Semanal</h3><p>{weekly_status}</p></div>', 
                       unsafe_allow_html=True)
        
        with col4:
            current_price = daily_df['Close'].iloc[-1]
            st.markdown(f'<div class="metric-card"><h3>Preço Atual</h3><p>${current_price:.2f}</p></div>', 
                       unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Gestão de Risco
        st.subheader("🎯 Gestão de Risco")
        
        risk_col1, risk_col2, risk_col3 = st.columns(3)
        
        with risk_col1:
            stop_loss = conv_info.get('stop_loss', 0)
            stop_distance = ((current_price - stop_loss) / current_price * 100) if stop_loss > 0 else 0
            st.metric("Stop Loss", f"${stop_loss:.2f}", f"-{stop_distance:.1f}%")
        
        with risk_col2:
            target = conv_info.get('target', 0)
            target_distance = ((target - current_price) / current_price * 100) if target > 0 else 0
            st.metric("Alvo", f"${target:.2f}", f"+{target_distance:.1f}%")
        
        with risk_col3:
            rr_ratio = target_distance / stop_distance if stop_distance > 0 else 0
            st.metric("R/R Ratio", f"{rr_ratio:.2f}", "Risk/Reward")
        
        st.markdown("---")
        
        # Gráficos
        st.subheader("📈 Gráficos")
        
        timeframe_selector = st.selectbox(
            "Selecione o timeframe:",
            ["Diário", "Semanal"],
            key="timeframe_selector"
        )
        
        if timeframe_selector == "Diário":
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
        
        st.markdown("---")
        
        # Backtest
        st.subheader("📊 Backtest - Últimos 252 Dias")
        
        if backtest_results and backtest_results['metrics']['total_trades'] > 0:
            metrics = backtest_results['metrics']
            
            # Métricas principais
            met_col1, met_col2, met_col3, met_col4, met_col5 = st.columns(5)
            
            with met_col1:
                st.metric("Total Trades", metrics['total_trades'])
            
            with met_col2:
                st.metric("Win Rate", f"{metrics['win_rate']:.1f}%")
            
            with met_col3:
                st.metric("Win Rate Ajustado", f"{metrics['win_rate_adjusted']:.1f}%",
                         help="Apenas stops vs alvos")
            
            with met_col4:
                st.metric("Retorno Total", f"{metrics['total_return']:.2f}%")
            
            with met_col5:
                st.metric("Profit Factor", f"{metrics['profit_factor']:.2f}")
            
            # Métricas secundárias
            met_col6, met_col7, met_col8, met_col9 = st.columns(4)
            
            with met_col6:
                st.metric("Sharpe Ratio", f"{metrics['sharpe_ratio']:.2f}")
            
            with met_col7:
                st.metric("Max Drawdown", f"{metrics['max_drawdown']:.2f}%")
            
            with met_col8:
                st.metric("Expectância", f"{metrics['expectancy']:.2f}%")
            
            with met_col9:
                st.metric("Duração Média", f"{metrics['avg_duration_days']:.1f} dias")
            
            # Distribuição de trades
            st.markdown("#### 📊 Distribuição de Trades")
            dist_col1, dist_col2, dist_col3 = st.columns(3)
            
            with dist_col1:
                st.metric("✅ Alvos Atingidos", 
                         f"{metrics['targets_hit']} ({metrics['targets_hit']/metrics['total_trades']*100:.1f}%)")
            
            with dist_col2:
                st.metric("❌ Stops Atingidos", 
                         f"{metrics['stops_hit']} ({metrics['stops_hit']/metrics['total_trades']*100:.1f}%)")
            
            with dist_col3:
                other_exits = metrics['total_trades'] - metrics['targets_hit'] - metrics['stops_hit']
                st.metric("🔄 Outras Saídas", 
                         f"{other_exits} ({other_exits/metrics['total_trades']*100:.1f}%)")
            
            # Tabela de trades
            with st.expander("📋 Ver Histórico Completo de Trades"):
                trades_df = pd.DataFrame(backtest_results['trades'])
                if not trades_df.empty:
                    trades_df['entry_date'] = pd.to_datetime(trades_df['entry_date']).dt.strftime('%Y-%m-%d')
                    trades_df['exit_date'] = pd.to_datetime(trades_df['exit_date']).dt.strftime('%Y-%m-%d')
                    
                    # Formata colunas
                    display_df = trades_df[[
                        'entry_date', 'exit_date', 'entry_price', 'exit_price', 
                        'pnl_pct', 'exit_reason', 'duration_days'
                    ]].copy()
                    
                    display_df.columns = [
                        'Entrada', 'Saída', 'Preço Entrada', 'Preço Saída',
                        'Retorno %', 'Motivo Saída', 'Duração (dias)'
                    ]
                    
                    st.dataframe(display_df, use_container_width=True)
        else:
            st.info("ℹ️ Nenhum trade encontrado no período de análise (últimos 252 dias)")
    
    else:
        # Mensagem inicial
        st.info("👈 Selecione um ativo na barra lateral e clique em 'Analisar Ativo' para começar")
        
        # Exibe estatísticas da base de dados
        st.subheader("📊 Base de Dados")
        
        for market, categories in st.session_state.asset_counts.items():
            with st.expander(f"🌍 {market}"):
                for category, count in categories.items():
                    st.metric(category, f"{count:,} ativos")

if __name__ == "__main__":
    main()
