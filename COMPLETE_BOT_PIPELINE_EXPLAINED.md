# 🤖 NSE AlphaBot - Complete Pipeline Explained

**A Step-by-Step Walkthrough of How Everything Works Together**

**Date:** 2024-11-20  
**Version:** 4.0 Ultimate with 30% AI/ML Weight  

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Complete Pipeline Flow](#complete-pipeline-flow)
3. [Step 1: Stock Screening](#step-1-stock-screening)
4. [Step 2: Multi-Timeframe Analysis](#step-2-multi-timeframe-analysis)
5. [Step 3: Smart Money Concepts](#step-3-smart-money-concepts)
6. [Step 4: AI/ML Predictions](#step-4-aiml-predictions)
7. [Step 5: Advanced Technical](#step-5-advanced-technical)
8. [Step 6: Sentiment Analysis](#step-6-sentiment-analysis)
9. [Step 7: Signal Generation](#step-7-signal-generation)
10. [Step 8: Trade Execution](#step-8-trade-execution)
11. [Real Example Walkthrough](#real-example-walkthrough)

---

## 🎯 Overview

### What Does the Bot Do?

NSE AlphaBot is an AI-powered trading system that:
1. **Screens 2000+ NSE stocks** to find high-momentum candidates
2. **Analyzes top 50 stocks** using 6 advanced methods
3. **Generates 0-5 BUY signals** with 75%+ confidence
4. **Calculates position sizes** with 3% risk management
5. **Executes trades** (paper or live) with automatic stop loss/targets

### Key Innovation

**Multi-Analysis Approach:**
- Not just one method (like RSI or MACD)
- Combines 6 different analysis methods
- Weighted scoring (AI/ML gets 30%!)
- Only signals when 3/4 major systems agree

---

## 🔄 Complete Pipeline Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    9:15 AM - Market Opens                    │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 1: FETCH ALL NSE STOCKS (2000+)                       │
│  • Fetch from NSE India website                             │
│  • Get complete equity list                                 │
│  • Add .NS suffix for yfinance                              │
│  Output: ['RELIANCE.NS', 'TCS.NS', ...]                     │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 2: SCREEN WITH 8 FILTERS                              │
│  ✓ Volume > 10 lakh shares/day                              │
│  ✓ Market Cap > ₹5000 Cr                                    │
│  ✓ Price > ₹100                                             │
│  ✓ Beta > 1.2 (high volatility)                             │
│  ✓ RSI: 55-70 (bullish momentum)                            │
│  ✓ Price above 50-day & 200-day MA                          │
│  ✓ MACD bullish crossover                                   │
│  ✓ Volume surge 1.5x average                                │
│  Output: Top 50 high-momentum stocks                        │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 3: DEEP ANALYSIS (6 Methods)                          │
│                                                              │
│  For each of top 50 stocks:                                 │
│                                                              │
│  ┌──────────────────────────────────────────────┐          │
│  │ 3A. Multi-Timeframe Analysis (25%)           │          │
│  │ • Analyze 5 timeframes                       │          │
│  │ • Calculate alignment                        │          │
│  │ • Generate MTF score                         │          │
│  └──────────────────────────────────────────────┘          │
│                    │                                         │
│  ┌──────────────────────────────────────────────┐          │
│  │ 3B. Smart Money Concepts (25%)               │          │
│  │ • Find order blocks                          │          │
│  │ • Detect fair value gaps                    │          │
│  │ • Identify liquidity sweeps                 │          │
│  │ • Check break of structure                  │          │
│  └──────────────────────────────────────────────┘          │
│                    │                                         │
│  ┌──────────────────────────────────────────────┐          │
│  │ 3C. AI/ML Predictions (30%)                  │          │
│  │ • Kronos: 7-day price forecast (21%)        │          │
│  │ • DRL: Optimal action (9%)                  │          │
│  └──────────────────────────────────────────────┘          │
│                    │                                         │
│  ┌──────────────────────────────────────────────┐          │
│  │ 3D. Advanced Technical (10%)                 │          │
│  │ • Volume profile                             │          │
│  │ • Fibonacci levels                           │          │
│  │ • MACD/RSI divergences                       │          │
│  └──────────────────────────────────────────────┘          │
│                    │                                         │
│  ┌──────────────────────────────────────────────┐          │
│  │ 3E. Sentiment Analysis (10%)                 │          │
│  │ • News sentiment (Finnhub)                   │          │
│  │ • Technical momentum                         │          │
│  └──────────────────────────────────────────────┘          │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 4: CALCULATE WEIGHTED SCORE                           │
│                                                              │
│  Final Score = (MTF × 0.25) + (SMC × 0.25) +               │
│                (AI/ML × 0.30) + (Tech × 0.10) +             │
│                (Sentiment × 0.10)                            │
│                                                              │
│  Example:                                                    │
│  • MTF: 0.90 × 0.25 = 0.225                                │
│  • SMC: 0.80 × 0.25 = 0.200                                │
│  • AI/ML: 0.75 × 0.30 = 0.225                              │
│  • Tech: 0.60 × 0.10 = 0.060                               │
│  • Sentiment: 0.65 × 0.10 = 0.065                          │
│  • Total: 0.775 = 77.5% confidence                         │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 5: FILTER SIGNALS                                     │
│                                                              │
│  ALL must be true:                                           │
│  ✓ Confidence ≥ 75%                                         │
│  ✓ Expected return ≥ 2.5%                                   │
│  ✓ 3/4 major systems bullish                                │
│  ✓ Timeframe alignment ≥ 60%                                │
│  ✓ RSI < 75 (not overbought)                                │
│                                                              │
│  If YES → Generate BUY signal                               │
│  If NO → HOLD (skip this stock)                             │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 6: CALCULATE POSITION SIZE                            │
│                                                              │
│  Risk Management:                                            │
│  • Risk per trade: 3% of capital                            │
│  • Stop loss: -3% from entry                                │
│  • Target: Expected return                                  │
│  • Max position: 20% of capital                             │
│                                                              │
│  Formula:                                                    │
│  Shares = (Capital × 0.03) / (Price × 0.03)                │
│  Position Size = Shares × Price                             │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 7: SHOW SIGNALS TO USER                               │
│                                                              │
│  Display:                                                    │
│  • Ticker, Price, Confidence                                │
│  • Expected return                                           │
│  • Component scores (MTF, SMC, AI, etc.)                    │
│  • Shares to buy                                             │
│  • Stop loss & target prices                                │
│                                                              │
│  User decides: Execute or Skip                              │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 8: EXECUTE TRADE                                      │
│                                                              │
│  Paper Trading:                                              │
│  • Log trade to file                                         │
│  • Track position                                            │
│  • Calculate P&L                                             │
│                                                              │
│  Live Trading:                                               │
│  • Place bracket order on Zerodha                           │
│  • Entry: Market order                                       │
│  • Stop Loss: -3% (automatic)                               │
│  • Target: +Expected return (automatic)                     │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 9: MONITOR & TRACK                                    │
│                                                              │
│  • Broker manages stop loss/target                          │
│  • Update P&L in real-time                                  │
│  • Log everything                                            │
│  • Generate reports                                          │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 Step 1: Stock Screening

### Purpose
Filter 2000+ NSE stocks down to top 50 high-momentum candidates

### How It Works

**1. Fetch All NSE Stocks**
```python
# File: src/utils/fetch_all_nse_stocks.py

def get_all_nse_stocks():
    """
    Fetch complete NSE equity list from NSE India website
    
    Process:
    1. Download CSV from NSE India
    2. Parse equity symbols
    3. Add .NS suffix for yfinance
    4. Return list of 2000+ tickers
    """
    url = "https://www.nseindia.com/api/equity-stockIndices?index=SECURITIES%20IN%20F%26O"
    # Fetch and parse...
    return ['RELIANCE.NS', 'TCS.NS', 'INFY.NS', ...]  # 2000+ stocks
```

**2. Apply 8 Filters**
```python
# File: src/utils/nse_stock_screener.py

def screen_stock(ticker):
    """
    Screen individual stock against 8 criteria
    
    Filters:
    1. Volume > 10 lakh shares/day (liquidity)
    2. Market Cap > ₹5000 Cr (large/mid cap)
    3. Price > ₹100 (avoid penny stocks)
    4. Beta > 1.2 (high volatility for swing trading)
    5. RSI: 55-70 (bullish momentum, not overbought)
    6. Price above 50-day & 200-day MA (uptrend)
    7. MACD bullish crossover (momentum confirmation)
    8. Volume surge 1.5x average (unusual activity)
    
    Returns:
        Stock data if passes all filters, None otherwise
    """
```

**3. Calculate Momentum Score**
```python
def calculate_momentum_score(stock_data):
    """
    Calculate momentum score for ranking
    
    Components:
    • Price momentum (vs 50-day MA): 35%
    • Volume momentum (vs 20-day avg): 25%
    • RSI strength (normalized): 20%
    • MACD strength: 20%
    
    Higher score = better momentum
    """
    price_momentum = ((price - ma_50) / ma_50) * 100
    volume_momentum = (volume_ratio - 1.0) * 100
    rsi_strength = (rsi - 50) / 50 * 100
    macd_strength = ((macd - macd_signal) / abs(macd_signal)) * 100
    
    momentum_score = (
        price_momentum * 0.35 +
        volume_momentum * 0.25 +
        rsi_strength * 0.20 +
        macd_strength * 0.20
    )
    
    return momentum_score
```

**4. Select Top 50**
```python
def screen_nse_stocks(max_stocks=50):
    """
    Screen all NSE stocks and return top 50
    
    Process:
    1. Load 2000+ NSE stocks
    2. Screen each stock (8 filters)
    3. Calculate momentum score
    4. Sort by momentum score
    5. Return top 50
    
    Output:
    [
        {'ticker': 'RELIANCE.NS', 'momentum_score': 85.3, ...},
        {'ticker': 'TCS.NS', 'momentum_score': 82.1, ...},
        ...
    ]
    """
```

### Example Output

```
🔍 NSE STOCK SCREENER
================================================================
Universe: 2,143 NSE stocks
Filters: 8 criteria

[   1/2143] RELIANCE.NS          ✅ PASS | Score:  85.3 | Vol: 2.1x | RSI: 62
[   2/2143] TCS.NS               ✅ PASS | Score:  82.1 | Vol: 1.8x | RSI: 65
[   3/2143] INFY.NS              ❌ FAIL
[   4/2143] HDFCBANK.NS          ✅ PASS | Score:  78.5 | Vol: 1.6x | RSI: 58
...
[2143/2143] ZOMATO.NS            ❌ FAIL

✅ SCREENING COMPLETE
================================================================
Qualified Stocks: 50/2,143
Pass Rate: 2.3%

🎯 TOP 20 HIGH MOMENTUM STOCKS:
Rank  Ticker          Price      MCap     Volume      Beta   RSI  Score
1     RELIANCE.NS   ₹2,850.50  ₹19,28,000Cr  15,234,567  1.45   62   85.3
2     TCS.NS        ₹3,645.20  ₹13,45,000Cr  12,456,789  1.32   65   82.1
...
```

---

## 📈 Step 2: Multi-Timeframe Analysis (25% Weight)

### Purpose
Analyze trends across 5 timeframes to identify high-probability setups

### How It Works

**1. Fetch Data for 5 Timeframes**
```python
# File: src/utils/multi_timeframe_analyzer.py

class MultiTimeframeAnalyzer:
    def fetch_all_timeframes(self):
        """
        Fetch data for 5 timeframes
        
        Timeframes:
        1. Monthly (5 years, 60 bars)
        2. Weekly (2 years, 104 bars)
        3. Daily (1 year, 252 bars)
        4. 4-Hour (60 days, 360 bars)
        5. 1-Hour (60 days, 1440 bars)
        
        Why these timeframes?
        • Monthly/Weekly: Major trend
        • Daily: Short-term trend
        • 4H/1H: Entry timing
        """
```

**2. Analyze Each Timeframe**
```python
def analyze_timeframe(df):
    """
    Analyze one timeframe
    
    Calculates:
    • Trend direction (bullish/bearish/neutral)
    • Trend strength (0-5 score)
    • RSI (14-period)
    • MACD (12, 26, 9)
    • Moving averages (20, 50, 200 EMA)
    
    Trend Determination:
    Bullish if:
    - Price > EMA20 > EMA50 > EMA200
    - MACD > MACD Signal
    - RSI > 50
    - Higher highs and higher lows
    
    Score (0-5):
    +1 if price > EMA20
    +1 if EMA20 > EMA50
    +1 if EMA50 > EMA200
    +1 if MACD > Signal
    +1 if RSI > 50
    """
```

**3. Calculate Alignment**
```python
def calculate_alignment():
    """
    Calculate timeframe alignment
    
    Alignment = Bullish timeframes / Total timeframes
    
    Example:
    • Monthly: Bullish
    • Weekly: Bullish
    • Daily: Bullish
    • 4H: Neutral
    • 1H: Bullish
    
    Alignment = 4/5 = 80%
    
    Why important?
    • Higher alignment = higher probability
    • All timeframes bullish = very strong signal
    • Mixed timeframes = wait for clarity
    """
```

**4. Generate MTF Score**
```python
def calculate_mtf_score():
    """
    Calculate final MTF score
    
    Formula:
    MTF Score = (Average Strength / 5) × Alignment
    
    Example:
    • Monthly: 5/5 (strong bullish)
    • Weekly: 4/5 (bullish)
    • Daily: 4/5 (bullish)
    • 4H: 3/5 (neutral-bullish)
    • 1H: 4/5 (bullish)
    
    Average Strength = (5+4+4+3+4)/5 = 4.0/5
    Alignment = 4/5 = 0.80 (80%)
    
    MTF Score = (4.0/5) × 0.80 = 0.64
    
    Contribution to final score:
    0.64 × 0.25 (weight) = 0.16 (16%)
    """
```

### Example Output

```
MULTI-TIMEFRAME ANALYSIS: RELIANCE.NS
================================================================

SIGNAL: BUY | Confidence: 90%
Reason: Strong bullish alignment across all timeframes

TIMEFRAME ALIGNMENT:
├─ Bullish Timeframes: 5/5
├─ Alignment Score: 100%
└─ Average Strength: 4.2/5

TIMEFRAME BREAKDOWN:

MONTHLY:
├─ Trend: BULLISH (Score: 5/5)
├─ Price: ₹2,850.50
├─ RSI: 62.5
├─ MACD: 45.2 (Signal: 38.1)
└─ Reasons: Price > all EMAs, MACD bullish, RSI strong

WEEKLY:
├─ Trend: BULLISH (Score: 4/5)
├─ Price: ₹2,850.50
├─ RSI: 58.3
├─ MACD: 32.1 (Signal: 28.5)
└─ Reasons: Price > EMAs, MACD bullish

DAILY:
├─ Trend: BULLISH (Score: 4/5)
├─ Price: ₹2,850.50
├─ RSI: 55.2
├─ MACD: 12.5 (Signal: 10.3)
└─ Reasons: Uptrend confirmed

4-HOUR:
├─ Trend: BULLISH (Score: 3/5)
├─ Price: ₹2,850.50
├─ RSI: 52.1
├─ MACD: 5.2 (Signal: 4.8)
└─ Reasons: Neutral-bullish

1-HOUR:
├─ Trend: BULLISH (Score: 4/5)
├─ Price: ₹2,850.50
├─ RSI: 56.8
├─ MACD: 3.1 (Signal: 2.5)
└─ Reasons: Short-term bullish

================================================================
MTF Score: 0.90 (90%)
Contribution: 0.90 × 0.25 = 0.225 (22.5%)
```

---

## 💰 Step 3: Smart Money Concepts (25% Weight)

### Purpose
Detect institutional trading patterns (where big money is moving)

### How It Works

**1. Find Order Blocks**
```python
# File: src/utils/smc_analyzer.py

def find_order_blocks():
    """
    Order Block = Last opposite candle before strong move
    
    Bullish Order Block:
    • Last bearish candle before bullish rally
    • Institutional buying zone
    • High probability support
    
    Detection:
    1. Find strong moves (>3% in 1-3 candles)
    2. Identify last opposite candle before move
    3. Mark as order block
    4. Track if price returns to test it
    
    Example:
    Day 1: Bearish candle (red)
    Day 2: Bearish candle (red) ← ORDER BLOCK
    Day 3: Bullish candle +2%
    Day 4: Bullish candle +3%
    Day 5: Bullish candle +2%
    
    The Day 2 candle is a bullish order block
    If price returns to Day 2 level = buy opportunity
    """
```

**2. Detect Fair Value Gaps**
```python
def find_fair_value_gaps():
    """
    FVG = Price imbalance (gap in price action)
    
    Bullish FVG:
    • Current candle low > Previous candle high
    • Gap up = strong buying pressure
    • Target for price to fill
    
    Detection:
    Day 1: High = 2800
    Day 2: Low = 2850 ← GAP!
    
    FVG = 2800 to 2850 (50 points)
    
    Trading Logic:
    • If price gaps up, it may return to fill gap
    • Use gap as support level
    • Or wait for gap fill before buying
    """
```

**3. Identify Liquidity Sweeps**
```python
def detect_liquidity_sweeps():
    """
    Liquidity Sweep = Stop hunt before reversal
    
    Bullish Sweep:
    • Price breaks below recent low
    • Triggers stop losses (liquidity grab)
    • Then reverses up strongly
    • Institutions accumulating
    
    Detection:
    Day 1-5: Low = 2800 (support level)
    Day 6: Price drops to 2790 ← SWEEP!
    Day 7: Price rallies to 2850 ← REVERSAL!
    
    This is a bullish liquidity sweep
    Institutions grabbed liquidity below 2800
    Then pushed price up
    """
```

**4. Check Break of Structure**
```python
def detect_break_of_structure():
    """
    BOS = Trend confirmation
    
    Bullish BOS:
    • Price breaks above previous high
    • Higher high confirmed
    • Uptrend continuation
    
    Detection:
    Previous High: 2850
    Current Price: 2870 ← BREAK!
    
    This confirms uptrend
    Expect continuation higher
    """
```

**5. Calculate SMC Score**
```python
def calculate_smc_score():
    """
    Calculate SMC score (0-1)
    
    Components:
    • Order Blocks: 30%
    • Fair Value Gaps: 30%
    • Liquidity Sweeps: 20%
    • Break of Structure: 20%
    
    Example:
    • Bullish OB > Bearish OB: +0.3
    • Bullish FVG > Bearish FVG: +0.3
    • Bullish Liquidity Sweep: +0.2
    • Bullish BOS: +0.2
    • Total: 1.0
    
    Contribution:
    1.0 × 0.25 (weight) = 0.25 (25%)
    """
```

### Example Output

```
SMART MONEY CONCEPTS ANALYSIS: RELIANCE.NS
================================================================

SIGNAL: STRONG_BUY | Score: 0.85

ORDER BLOCKS:
  Bullish: 3
  Bearish: 1
  Recent: ₹2,765-₹2,785 (tested and held)

FAIR VALUE GAPS:
  Bullish: 2
  Bearish: 0
  Recent: ₹2,800-₹2,820 (filled)

LIQUIDITY SWEEP:
  Type: BULLISH
  Strength: Strong
  Size: 1.2%
  Details: Swept ₹2,790 low, reversed to ₹2,850

BREAK OF STRUCTURE:
  Type: BULLISH
  Strength: Strong
  Size: 2.3%
  Details: Broke ₹2,850 high, now at ₹2,870

KEY SIGNALS:
  • Bullish order block holding as support
  • Fair value gaps filled (bullish)
  • Liquidity sweep completed (accumulation)
  • Break of structure confirmed (continuation)

================================================================
SMC Score: 0.85 (85%)
Contribution: 0.85 × 0.25 = 0.2125 (21.25%)
```

---

## 🤖 Step 4: AI/ML Predictions (30% Weight)

### Purpose
Use AI models to predict price movements and optimal actions

### Component A: Kronos Price Prediction (21% of total)

**1. Load Kronos Model**
```python
# File: src/models/kronos_predictor.py

def get_kronos_predictor(model_name="NeoQuasar/Kronos-small"):
    """
    Load official Kronos transformer model
    
    Model Details:
    • Name: NeoQuasar/Kronos-small
    • Parameters: 24.7M
    • Architecture: Transformer
    • Training: 45+ global exchanges
    • Quantization: Binary Spherical (BSQ)
    
    Why Kronos?
    • State-of-the-art time series model
    • Better than LSTM for long sequences
    • Attention mechanism captures patterns
    • Pre-trained on financial data
    """
```

**2. Prepare Data**
```python
def prepare_data_for_kronos(df):
    """
    Prepare stock data for Kronos
    
    Process:
    1. Get last 60 days of prices
    2. Normalize to 0-1 range
    3. Create sequence tensor
    4. Add batch dimension
    
    Input shape: (1, 60, 1)
    • 1 = batch size
    • 60 = sequence length
    • 1 = features (price)
    """
```

**3. Generate Prediction**
```python
def predict(df, horizon=7):
    """
    Generate 7-day price forecast
    
    Process:
    1. Prepare last 60 days
    2. Run through Kronos model
    3. Get 7-day forecast
    4. Denormalize predictions
    5. Calculate predicted change
    6. Calculate confidence
    
    Output:
    {
        'predicted_prices': [2855, 2862, 2870, 2878, 2885, 2892, 2900],
        'predicted_change': +1.7%,  # 7-day change
        'confidence': 0.85,  # Model confidence
        'direction': 'bullish'
    }
    """
```

**4. Convert to Score**
```python
def calculate_kronos_score(prediction):
    """
    Convert Kronos prediction to score (0-1)
    
    Formula:
    Base Score = 0.5 + (predicted_change × 5)
    Weighted Score = 0.5 + (Base Score - 0.5) × confidence
    
    Example:
    • Predicted change: +1.7%
    • Confidence: 0.85
    
    Base Score = 0.5 + (0.017 × 5) = 0.585
    Weighted Score = 0.5 + (0.585 - 0.5) × 0.85 = 0.572
    
    Kronos Score: 0.572
    """
```

### Component B: DRL Action Selection (9% of total)

**1. Load DRL Agent**
```python
# File: src/bot/nse_alphabot_ultimate.py

# Load SAC agent
DRL_AGENT = SAC.load("models/sac_nse_retrained.zip")

"""
DRL Agent Details:
• Algorithm: SAC (Soft Actor-Critic)
• Training: 24,359 data points
• Episodes: 50,000 timesteps
• State Space: [price, rsi, macd, capital, shares]
• Action Space: Buy/Sell/Hold (-1 to +1)
• Reward: Portfolio returns + Sharpe ratio
"""
```

**2. Prepare State**
```python
def prepare_drl_state(stock_data):
    """
    Prepare state vector for DRL agent
    
    State Components:
    1. Price (normalized)
    2. RSI (normalized)
    3. MACD (normalized)
    4. Capital ratio
    5. Shares held
    
    Example:
    price_norm = 2850 / 10000 = 0.285
    rsi_norm = 55 / 100 = 0.55
    macd_norm = 12.5 / 100 = 0.125
    capital_ratio = 1.0 (100% available)
    shares_held = 0.0 (no position)
    
    State = [0.285, 0.55, 0.125, 1.0, 0.0]
    """
```

**3. Get Action**
```python
def get_drl_action(state):
    """
    Get trading action from DRL agent
    
    Process:
    1. Prepare state vector
    2. Run through DRL agent
    3. Get action (-1 to +1)
    4. Convert to score (0-1)
    
    Action Interpretation:
    • -1.0 to -0.3: Strong
