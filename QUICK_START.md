# 🚀 Guia Rápido - Multi-Strategy Scanner

## ⚡ Início Rápido (3 passos)

```bash
# 1. Instale as dependências
pip install -r requirements.txt

# 2. Execute a aplicação
streamlit run app.py

# 3. Acesse no navegador
# Abre automaticamente em: http://localhost:8501
```

## 📖 Como Usar

### 1️⃣ Escolha a Estratégia
Na barra lateral, selecione entre:
- **Cacas Channel**: Estratégia original com 4 linhas (Superior, Inferior, Média, EMA)
- **Moving Average Cross**: Cruzamento de médias móveis exponenciais

### 2️⃣ Configure os Parâmetros

**Para Cacas Channel:**
- `Upper`: Período da linha superior (resistência) - Padrão: 20
- `Under`: Período da linha inferior (suporte) - Padrão: 30
- `EMA`: Período da EMA (sinal) - Padrão: 9

**Para Moving Average Cross:**
- `EMA Rápida`: Período da média rápida - Padrão: 9
- `EMA Lenta`: Período da média lenta - Padrão: 21

**Gestão de Risco (comum a todas):**
- `Stop Loss`: Multiplicador do ATR - Padrão: 1.5
- `Alvo`: Multiplicador do Stop - Padrão: 2.0

### 3️⃣ Selecione o Ativo
1. Escolha o **Mercado** (Brasil, EUA, Crypto)
2. Escolha a **Categoria** (Ações, FIIs, ETFs, etc.)
3. Selecione o **Ativo** específico

### 4️⃣ Analise
Clique em **"🔍 Analisar Ativo"** para ver:

- ✅ **Status de Convergência**: Se há sinal em ambos timeframes
- 📊 **Sinais Individual**: Diário e Semanal separados
- 💰 **Preço Atual**: Cotação mais recente
- 🎯 **Gestão de Risco**: Stop Loss, Alvo e R/R Ratio
- 📈 **Gráficos Interativos**: Visualização com indicadores
- 📊 **Backtest Completo**: Performance histórica da estratégia

## 🎯 Interpretando os Resultados

### ✅ Convergência = SIM
Significa que **ambos** os timeframes (diário E semanal) estão com sinal de compra.
Isso indica maior probabilidade de sucesso segundo a estratégia.

### ❌ Convergência = NÃO
Pelo menos um dos timeframes não está com sinal de compra.
A estratégia recomenda aguardar convergência.

### 📊 Métricas do Backtest

- **Win Rate**: % de trades lucrativos
- **Win Rate Ajustado**: % considerando apenas stops vs alvos (ignora saídas por sinal)
- **Profit Factor**: Lucro bruto / Perda bruta (>1 é positivo)
- **Sharpe Ratio**: Retorno ajustado ao risco (>1 é bom, >2 é excelente)
- **Max Drawdown**: Maior queda acumulada
- **Expectância**: Retorno médio esperado por trade

## 🔧 Adicionando Seus Próprios Ativos

Edite os arquivos CSV em `data/`:

```csv
ticker
PETR4.SA
VALE3.SA
ITUB4.SA
```

**Formato dos Tickers:**
- 🇧🇷 Brasil: `TICKER.SA` (ex: PETR4.SA)
- 🇺🇸 EUA: `TICKER` (ex: AAPL)
- 💰 Crypto: `TICKER-USD` (ex: BTC-USD)

## 🆕 Criando Sua Própria Estratégia

### Passo 1: Crie o arquivo da estratégia
```python
# src/strategies/minha_estrategia.py

from .base_strategy import BaseStrategy
import pandas as pd

class MinhaEstrategia(BaseStrategy):
    def __init__(self, periodo: int = 14):
        self.periodo = periodo
    
    def get_strategy_name(self) -> str:
        return "Minha Estratégia"
    
    def get_strategy_description(self) -> str:
        return f"Minha estratégia com período {self.periodo}"
    
    def get_indicator_names(self) -> list:
        return ['meu_indicador']
    
    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        # Calcule seus indicadores aqui
        df['meu_indicador'] = df['Close'].rolling(self.periodo).mean()
        return df
    
    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        # Gere sinais de compra/venda
        df['signal'] = (df['Close'] > df['meu_indicador']).astype(int)
        
        # ATR para stop e alvo
        high_low = df['High'] - df['Low']
        atr = high_low.rolling(14).mean()
        df['stop_loss'] = df['Close'] - atr * 1.5
        df['target'] = df['Close'] + atr * 3.0
        
        return df
    
    def check_convergence(self, daily_df, weekly_df):
        daily_signal = daily_df['signal'].iloc[-1]
        weekly_signal = weekly_df['signal'].iloc[-1]
        
        has_convergence = (daily_signal == 1 and weekly_signal == 1)
        
        info = {
            'daily_signal': bool(daily_signal),
            'weekly_signal': bool(weekly_signal),
            'convergence': has_convergence,
            'stop_loss': float(daily_df['stop_loss'].iloc[-1]),
            'target': float(daily_df['target'].iloc[-1]),
        }
        
        return has_convergence, info
```

### Passo 2: Registre a estratégia
```python
# src/strategies/__init__.py

from .minha_estrategia import MinhaEstrategia

AVAILABLE_STRATEGIES = {
    'Cacas Channel': CacasChannelStrategy,
    'Moving Average Cross': MovingAverageCrossStrategy,
    'Minha Estratégia': MinhaEstrategia,  # ← Adicione aqui
}
```

### Passo 3: (Opcional) Adicione UI personalizada
```python
# app.py - Na seção de parâmetros

elif selected_strategy_name == "Minha Estratégia":
    periodo = st.sidebar.slider("Período", 5, 50, 14)
    strategy_params = {'periodo': periodo}
```

### Passo 4: (Opcional) Adicione gráficos personalizados
```python
# src/ui/charts.py

def _plot_minha_estrategia_indicators(fig, df):
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df['meu_indicador'],
            name='Meu Indicador',
            line=dict(color='purple', width=2)
        ),
        row=1, col=1
    )
```

## 💡 Dicas

1. **Performance**: Use período máximo de 1 ano para dados diários (mais rápido)
2. **Backtest**: 252 dias = ~1 ano de trading (dias úteis)
3. **Convergência**: Quanto mais timeframes concordam, mais forte o sinal
4. **R/R Ratio**: Busque > 2.0 (risco 1, retorno 2+)
5. **Testes**: Sempre faça backtest antes de operar com dinheiro real

## ⚠️ Avisos Importantes

- ⚠️ Este é um **sistema educacional** para estudo de estratégias
- ⚠️ **NÃO** é recomendação de investimento
- ⚠️ Sempre faça sua própria análise e gerenciamento de risco
- ⚠️ Performance passada não garante resultados futuros
- ⚠️ Opere apenas com capital que pode perder

## 🐛 Problemas Comuns

### Erro ao baixar dados
- Verifique sua conexão com internet
- Confirme que o ticker está correto
- Tente novamente (pode ser timeout temporário)

### Estratégia não aparece
- Verifique se adicionou em `AVAILABLE_STRATEGIES`
- Confirme que o arquivo está em `src/strategies/`
- Reinicie a aplicação Streamlit

### Backtest sem trades
- Normal para estratégias muito seletivas
- Tente aumentar o período de análise
- Ajuste os parâmetros da estratégia

## 📞 Suporte

Encontrou um bug ou tem uma sugestão?
- Abra uma issue no repositório
- Envie um pull request com melhorias

---

✨ **Bons trades!** 📈
