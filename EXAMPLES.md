# 📊 Exemplos de Uso - Multi-Strategy Scanner

## 🎯 Exemplo 1: Analisando PETR4 com Cacas Channel

### Configuração
- **Estratégia**: Cacas Channel
- **Ativo**: PETR4.SA
- **Parâmetros**: Upper=20, Under=30, EMA=9

### Resultado Obtido
```
✅ Convergência: SIM
   📊 Sinal Diário: ✅ (Linha Branca > Linha Laranja)
   📊 Sinal Semanal: ✅ (Linha Branca > Linha Laranja)

🎯 Gestão de Risco:
   💰 Preço Atual: R$ 34.50
   ⛔ Stop Loss: R$ 32.80 (-4.9%)
   🎯 Alvo: R$ 37.90 (+9.8%)
   📊 R/R Ratio: 2.00

📈 Backtest (252 dias):
   Total Trades: 12
   Win Rate: 66.7%
   Profit Factor: 3.14
   Retorno Total: +24.43%
   Sharpe Ratio: 1.85
```

### Interpretação
- ✅ **Convergência positiva**: Ambos timeframes confirmam tendência de alta
- ✅ **R/R favorável**: Risco de 4.9% para potencial de 9.8%
- ✅ **Backtest positivo**: Win rate acima de 60%, profit factor > 3
- ✅ **Ação sugerida**: Considerar entrada com stop e alvo definidos

---

## 🎯 Exemplo 2: Analisando AAPL com Moving Average Cross

### Configuração
- **Estratégia**: Moving Average Cross
- **Ativo**: AAPL (Apple)
- **Parâmetros**: EMA Rápida=9, EMA Lenta=21

### Resultado Obtido
```
✅ Convergência: SIM
   📊 Sinal Diário: ✅ (EMA 9 > EMA 21)
   📊 Sinal Semanal: ✅ (EMA 9 > EMA 21)
   📏 Distância Diária: +2.3%
   📏 Distância Semanal: +4.1%

🎯 Gestão de Risco:
   💰 Preço Atual: $178.50
   ⛔ Stop Loss: $173.20 (-3.0%)
   🎯 Alvo: $189.10 (+5.9%)
   📊 R/R Ratio: 2.00

📈 Backtest (252 dias):
   Total Trades: 15
   Win Rate: 60.0%
   Profit Factor: 2.45
   Retorno Total: +18.30%
   Sharpe Ratio: 1.62
```

### Interpretação
- ✅ **Convergência forte**: Distância entre médias indica momentum
- ✅ **Tendência estabelecida**: Semanal confirma movimento
- ✅ **Performance consistente**: 60% win rate com profit factor > 2
- ✅ **Ação sugerida**: Setup válido para entrada

---

## 🎯 Exemplo 3: Analisando BTC-USD com ambas estratégias

### A) Cacas Channel
```
❌ Convergência: NÃO
   📊 Sinal Diário: ✅ (Linha Branca > Linha Laranja)
   📊 Sinal Semanal: ❌ (Linha Branca < Linha Laranja)

📈 Backtest (252 dias):
   Total Trades: 8
   Win Rate: 37.5%
   Profit Factor: 0.85
   Retorno Total: -12.40%
```

**Interpretação**: Sem convergência. Aguardar sinal semanal.

### B) Moving Average Cross
```
✅ Convergência: SIM
   📊 Sinal Diário: ✅ (EMA 9 > EMA 21)
   📊 Sinal Semanal: ✅ (EMA 9 > EMA 21)

📈 Backtest (252 dias):
   Total Trades: 11
   Win Rate: 72.7%
   Profit Factor: 3.87
   Retorno Total: +35.20%
```

**Interpretação**: Moving Average tem melhor performance no BTC.

### Conclusão
Este exemplo mostra como **diferentes estratégias performam diferentemente** em cada ativo:
- Cacas Channel pode ser melhor para ações
- Moving Average pode ser melhor para crypto
- **Sempre compare múltiplas estratégias!**

---

## 🎯 Exemplo 4: Scanner de Múltiplos Ativos

### Objetivo
Encontrar ativos com convergência em qualquer estratégia.

### Processo Manual (via interface)
1. Selecione "Brasil" → "Ações"
2. Para cada ação da lista:
   - Analise com Cacas Channel
   - Analise com Moving Average Cross
   - Anote quais têm convergência

### Exemplo de Resultados
```
Estratégia: Cacas Channel
├─ ✅ PETR4.SA (Convergência)
├─ ✅ VALE3.SA (Convergência)
├─ ❌ ITUB4.SA (Sem convergência)
├─ ✅ BBDC4.SA (Convergência)
└─ ❌ ABEV3.SA (Sem convergência)

Estratégia: Moving Average Cross
├─ ❌ PETR4.SA (Sem convergência)
├─ ✅ VALE3.SA (Convergência)
├─ ✅ ITUB4.SA (Convergência)
├─ ❌ BBDC4.SA (Sem convergência)
└─ ✅ ABEV3.SA (Convergência)

📊 Ativos com dupla confirmação:
   VALE3.SA - ✅ Cacas + ✅ MA Cross
```

### Insight
**VALE3.SA** tem convergência em **ambas** estratégias = sinal mais forte!

---

## 🎯 Exemplo 5: Comparando Parâmetros

### Cenário
Testar diferentes configurações da estratégia Moving Average Cross em ITUB4.SA

### Teste A: EMA Rápida=9, Lenta=21 (padrão)
```
Convergência: ❌ NÃO
Backtest: Win Rate 45.0%, Retorno -5.2%
```

### Teste B: EMA Rápida=5, Lenta=15 (mais sensível)
```
Convergência: ✅ SIM
Backtest: Win Rate 38.5%, Retorno -8.7%
Total Trades: 23 (muitos trades, win rate baixo)
```

### Teste C: EMA Rápida=20, Lenta=50 (menos sensível)
```
Convergência: ❌ NÃO
Backtest: Win Rate 66.7%, Retorno +12.3%
Total Trades: 6 (poucos trades, mas lucrativos)
```

### Conclusão
- Parâmetros **mais sensíveis** = mais trades, mas pior qualidade
- Parâmetros **menos sensíveis** = menos trades, mas melhor qualidade
- **Encontre o equilíbrio** ideal para cada ativo

---

## 🎯 Exemplo 6: Interpretando Métricas de Backtest

### Cenário Real
```
📊 Backtest - WEGE3.SA (Cacas Channel)
   Total Trades: 10
   Win Rate: 70.0%
   Win Rate Ajustado: 85.7%
   Retorno Total: +28.50%
   Retorno Médio: +2.85%
   Profit Factor: 4.32
   Sharpe Ratio: 2.15
   Max Drawdown: -8.30%
   Expectância: +2.12%
   
   Distribuição:
   ✅ Alvos: 6 (60%)
   ❌ Stops: 1 (10%)
   🔄 Outras Saídas: 3 (30%)
```

### Análise Detalhada

**✅ Pontos Positivos:**
- **Win Rate 70%**: 7 de 10 trades foram lucrativos
- **Win Rate Ajustado 85.7%**: De 7 saídas definidas (stop/alvo), 6 bateram alvo
- **Profit Factor 4.32**: Para cada R$1 perdido, ganhou R$4.32
- **Sharpe Ratio 2.15**: Excelente retorno ajustado ao risco (>2 é ótimo)
- **Expectância +2.12%**: Média esperada de ganho por trade

**⚠️ Pontos de Atenção:**
- **Max Drawdown -8.30%**: Maior sequência de perdas acumuladas
- **30% Outras Saídas**: Alguns trades saíram por perda de sinal, não por stop/alvo

**🎯 Decisão:**
Esta é uma **excelente estratégia** para WEGE3.SA:
- Profit Factor > 3
- Sharpe > 2
- Win Rate > 60%
- Drawdown controlado

---

## 🎯 Exemplo 7: Red Flags - Quando NÃO Operar

### Caso A: Win Rate baixo
```
Backtest: MGLU3.SA (Moving Average Cross)
   Total Trades: 15
   Win Rate: 26.7%
   Profit Factor: 0.45
   Retorno Total: -22.50%
```
**🚫 NÃO OPERAR**: Win rate < 30%, profit factor < 1

### Caso B: Poucos trades
```
Backtest: RENT3.SA (Cacas Channel)
   Total Trades: 2
   Win Rate: 100.0%
   Profit Factor: ∞
   Retorno Total: +8.50%
```
**🚫 NÃO CONFIAR**: Apenas 2 trades não é estatisticamente significativo

### Caso C: Alto drawdown
```
Backtest: BTCUSD (Cacas Channel)
   Total Trades: 12
   Win Rate: 58.3%
   Profit Factor: 1.85
   Max Drawdown: -35.40%
```
**⚠️ CUIDADO**: Drawdown muito alto, risco excessivo

### Caso D: Win Rate Ajustado vs Win Rate muito diferente
```
Backtest: ELET3.SA (Moving Average Cross)
   Total Trades: 20
   Win Rate: 60.0%
   Win Rate Ajustado: 25.0%
   (12 wins, mas apenas 2 alvos vs 6 stops)
```
**⚠️ PROBLEMA**: Muitos gains por saída de sinal (não atingiu alvo), poucos alvos reais

---

## 💡 Melhores Práticas

### 1. Múltiplas Confirmações
```
✅ PETR4.SA:
   ├─ Cacas Channel: ✅ Convergência
   ├─ Moving Average: ✅ Convergência
   └─ Backtest ambos: > 60% win rate
   
🔥 FORTE CANDIDATO!
```

### 2. Período de Análise
```
❌ Apenas 3 meses de dados
✅ Mínimo 1 ano (252 dias)
✅ Ideal: 2+ anos
```

### 3. Validação de Setups
```
Antes de operar:
├─ ✅ Convergência multi-timeframe
├─ ✅ Backtest positivo (>60% win, PF>2)
├─ ✅ R/R ratio adequado (>2.0)
├─ ✅ Drawdown aceitável (<15%)
└─ ✅ Volume médio suficiente
```

### 4. Gestão de Risco
```
Para cada trade:
├─ Risco: 1-2% do capital
├─ Stop Loss: Sempre configurado
├─ Alvo: Pelo menos 2x o stop
└─ Revisão: Se bater stop, aguardar novo setup
```

---

## 🎓 Exercícios Práticos

### Exercício 1: Compare Estratégias
1. Escolha um ativo (ex: BBDC4.SA)
2. Analise com Cacas Channel
3. Analise com Moving Average Cross
4. Compare as métricas de backtest
5. Qual performou melhor? Por quê?

### Exercício 2: Otimize Parâmetros
1. Escolha VALE3.SA
2. Teste Moving Average com diferentes períodos:
   - 5/15, 9/21, 12/26, 20/50
3. Anote Win Rate e Profit Factor de cada
4. Qual configuração é ideal?

### Exercício 3: Encontre Setups
1. Escolha 10 ações brasileiras
2. Para cada uma, teste ambas estratégias
3. Liste aquelas com convergência
4. Ordene por Profit Factor do backtest
5. Top 3 = suas melhores oportunidades

---

**🎯 Lembre-se**: Estes são exemplos educacionais. Sempre faça sua própria análise!
