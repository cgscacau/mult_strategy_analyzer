# 📊 Multi-Strategy Scanner

Scanner de ativos com análise multi-timeframe e suporte a múltiplas estratégias de trading.

## 🚀 Funcionalidades

### Estratégias Disponíveis
1. **Cacas Channel** - Canal de tendência com 4 linhas (Superior, Inferior, Média, EMA)
2. **Moving Average Cross** - Cruzamento de médias móveis exponenciais

### Recursos
- ✅ Análise multi-timeframe (Diário + Semanal)
- ✅ Detecção de convergência entre timeframes
- ✅ Gestão de risco com ATR (Stop Loss e Alvos)
- ✅ Backtest completo com métricas avançadas
- ✅ Suporte multi-mercado:
  - 🇧🇷 Brasil: Ações, FIIs, ETFs, BDRs
  - 🇺🇸 EUA: Stocks, ETFs, REITs
  - 💰 Criptomoedas

### Métricas de Backtest
- Win Rate e Win Rate Ajustado
- Retorno Total e Médio
- Profit Factor
- Maximum Drawdown
- Sharpe Ratio
- Expectância matemática
- Distribuição de trades (Alvos vs Stops)

## 🛠️ Instalação

```bash
# Clone o repositório
git clone <repo-url>
cd cacas-scanner

# Instale as dependências
pip install -r requirements.txt

# Execute a aplicação
streamlit run app.py
```

## 📁 Estrutura do Projeto

```
cacas-scanner/
│
├── app.py                          # Aplicação Streamlit principal
├── requirements.txt                # Dependências
│
├── data/                           # Arquivos CSV com ativos
│   ├── b3_acoes.csv
│   ├── b3_fiis.csv
│   ├── b3_etfs.csv
│   ├── b3_bdrs.csv
│   ├── us_stocks.csv
│   ├── us_etfs.csv
│   ├── us_reits.csv
│   └── crypto.csv
│
└── src/
    ├── strategies/                 # Módulo de estratégias
    │   ├── __init__.py            # Factory de estratégias
    │   ├── base_strategy.py       # Classe base abstrata
    │   ├── cacas_channel_strategy.py
    │   └── moving_average_strategy.py
    │
    ├── backtest/                   # Módulo de backtest
    │   ├── __init__.py
    │   └── strategy_backtester.py # Backtester genérico
    │
    ├── data/                       # Módulo de dados
    │   ├── asset_loader.py        # Carregador de ativos
    │   └── market_data.py         # Download via yfinance
    │
    └── ui/                         # Módulo de interface
        └── charts.py              # Gráficos Plotly
```

## 🎯 Como Usar

1. **Selecione a Estratégia**: Escolha entre Cacas Channel ou Moving Average Cross
2. **Configure Parâmetros**: Ajuste os parâmetros da estratégia na sidebar
3. **Escolha o Ativo**: Selecione mercado, categoria e ativo
4. **Analise**: Clique em "Analisar Ativo" para ver:
   - Status de convergência
   - Gestão de risco (Stop Loss e Alvo)
   - Gráficos interativos
   - Backtest com métricas completas

## 🔧 Adicionando Novas Estratégias

Para adicionar uma nova estratégia:

1. Crie um arquivo em `src/strategies/` herdando de `BaseStrategy`
2. Implemente os métodos obrigatórios:
   - `calculate_indicators()` - Calcula indicadores
   - `generate_signals()` - Gera sinais de compra
   - `check_convergence()` - Verifica convergência
3. Registre em `src/strategies/__init__.py`

Exemplo:

```python
from .base_strategy import BaseStrategy

class MyStrategy(BaseStrategy):
    def calculate_indicators(self, df):
        # Seu código aqui
        return df
    
    def generate_signals(self, df):
        # Seu código aqui
        return df
    
    def check_convergence(self, daily_df, weekly_df):
        # Seu código aqui
        return has_convergence, info
```

## 📊 Base de Dados

A aplicação suporta listas personalizadas de ativos via arquivos CSV em `data/`:
- Formato: Uma coluna "ticker" com símbolos dos ativos
- Naming: `{mercado}_{categoria}.csv` (ex: `b3_acoes.csv`, `us_stocks.csv`)

## 🤝 Contribuindo

Contribuições são bem-vindas! Sinta-se à vontade para:
- Adicionar novas estratégias
- Melhorar métricas de backtest
- Expandir listas de ativos
- Reportar bugs ou sugerir features

## 📝 Licença

MIT License

## ✨ Autor

Desenvolvido com ❤️ por [Seu Nome]
