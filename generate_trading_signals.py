#!/usr/bin/env python3
"""
NSE AlphaBot - Complete Trading Signal Generator
Generates actionable BUY/SELL/HOLD signals with:
- Entry Price
- Stop Loss Price
- Target Prices (T1, T2, T3)
- Position Size
- Risk-Reward Ratio
"""

import sys
sys.path.append('src')

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
import json
import warnings
warnings.filterwarnings("ignore")

from stable_baselines3 import SAC

# Import analyzers
from utils.multi_timeframe_analyzer import MultiTimeframeAnalyzer
from utils.smc_analyzer import SMCAnalyzer
from utils.advanced_technical import AdvancedTechnicalAnalyzer
from utils.sentiment_analyzer import get_hybrid_sentiment
from models.kronos_predictor import get_kronos_predictor
from utils.pkscreener_integration import screen_nse_stocks
from bot.trading_signal_generator import (
    generate_complete_signal, 
    print_trading_signal,
    save_signal_to_json
)

# Configuration
CAPITAL = 500000
RISK_PER_TRADE = 0.02
MIN_CONFIDENCE = 0.75
MIN_EXPECTED_RETURN = 2.5

# Weights
WEIGHT_KRONOS = 0.25
WEIGHT_MTF = 0.20
WEIGHT_SMC = 0.20
WEIGHT_TECHNICAL = 0.15
WEIGHT_DRL = 0.15
WEIGHT_SENTIMENT = 0.05

# Load models
print("🚀 Loading AI/ML Models...")
KRONOS_PREDICTOR = get_kronos_predictor(model_name="NeoQuasar/Kronos-small")

try:
    DRL_AGENT = SAC.load("models/sac_nse_nifty100.zip")
    print("✅ Loaded Nifty 100 DRL agent")
except:
    DRL_AGENT = None
    print("⚠️  DRL agent not found")

def get_stock_data(ticker, period="6mo"):
    """Fetch stock data"""
    try:
        df = yf.download(ticker, period=period, interval="1d",
                        auto_adjust=True, progress=False)
        
        if df.empty:
            return None
        
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        
        return df
    except:
        return None

def calculate_indicators(df):
    """Calculate technical indicators"""
    # EMAs
    df['ema_12'] = df['Close'].ewm(span=12).mean()
    df['ema_26'] = df['Close'].ewm(span=26).mean()
    df['ema_50'] = df['Close'].ewm(span=50).mean()
    
    # MACD
    df['macd'] = df['ema_12'] - df['ema_26']
    df['macd_signal'] = df['macd'].ewm(span=9).mean()
    
    # RSI
    delta = df['Close'].diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = (-delta.clip(upper=0)).rolling(14).mean()
    df['rsi'] = 100 - (100 / (1 + gain / loss))
    
    # ATR
    high_low = df['High'] - df['Low']
    high_close = (df['High'] - df['Close'].shift()).abs()
    low_close = (df['Low'] - df['Close'].shift()).abs()
    df['tr'] = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    df['atr'] = df['tr'].rolling(14).mean()
    
    # Volume
    df['volume_ratio'] = df['Volume'] / df['Volume'].rolling(20).mean()
    
    return df.dropna()

def analyze_stock(ticker):
    """
    Analyze stock and generate signal
    
    Returns:
        Complete trading signal dict or None
    """
    # Get data
    df = get_stock_data(ticker)
    if df is None or len(df) < 50:
        return None
    
    df = calculate_indicators(df)
    
    # Get current values
    current_price = df['Close'].iloc[-1]
    rsi = df['rsi'].iloc[-1]
    macd = df['macd'].iloc[-1]
    macd_signal_val = df['macd_signal'].iloc[-1]
    
    # === 1. Multi-Timeframe Analysis ===
    mtf_score = 0.5
    mtf_signal = "HOLD"
    mtf_alignment = 0.5
    
    try:
        mtf_analyzer = MultiTimeframeAnalyzer(ticker)
        if mtf_analyzer.fetch_all_timeframes():
            mtf_result = mtf_analyzer.generate_signal()
            mtf_signal = mtf_result['signal']
            mtf_score = mtf_result['confidence']
            mtf_alignment = mtf_result['alignment_score']
    except:
        pass
    
    # === 2. Smart Money Concepts ===
    smc_score = 0.5
    smc_signal = "NEUTRAL"
    
    try:
        smc_analyzer = SMCAnalyzer(df)
        smc_result = smc_analyzer.analyze_smc()
        smc_signal = smc_result['signal']
        smc_score = smc_result['score']
    except:
        pass
    
    # === 3. Advanced Technical ===
    tech_score = 0.5
    tech_signal = "NEUTRAL"
    
    try:
        tech_analyzer = AdvancedTechnicalAnalyzer(df)
        tech_result = tech_analyzer.analyze()
        tech_signal = tech_result['signal']
        tech_score = tech_result['score']
    except:
        pass
    
    # === 4. Sentiment ===
    sentiment_score = 0.5
    
    try:
        sentiment_score = get_hybrid_sentiment(ticker, df)
    except:
        pass
    
    # === 5. Kronos AI ===
    kronos_score = 0.5
    pred_change = 0.0
    
    try:
        kronos_prediction = KRONOS_PREDICTOR.predict(df, horizon=7)
        pred_change = kronos_prediction['predicted_change']
        kronos_confidence = kronos_prediction['confidence']
        
        kronos_score = 0.5 + (pred_change * 5)
        kronos_score = np.clip(kronos_score, 0, 1)
        kronos_score = 0.5 + (kronos_score - 0.5) * kronos_confidence
    except:
        pass
    
    # === 6. DRL Agent ===
    drl_score = 0.5
    
    try:
        if DRL_AGENT is not None:
            price_norm = np.clip(current_price / 10000.0, 0, 10)
            rsi_norm = np.clip(rsi / 100.0, 0, 1)
            macd_norm = np.clip(macd / 100.0, -1, 1)
            
            obs = np.array([price_norm, rsi_norm, macd_norm, 1.0, 0.0], dtype=np.float32)
            obs = np.nan_to_num(obs, nan=0.0, posinf=1.0, neginf=0.0)
            
            drl_action, _ = DRL_AGENT.predict(obs, deterministic=True)
            drl_score = 0.5 + (drl_action[0] * 0.5)
            drl_score = np.clip(drl_score, 0, 1)
    except:
        pass
    
    # === Combine Signals ===
    final_confidence = (
        kronos_score * WEIGHT_KRONOS +
        mtf_score * WEIGHT_MTF +
        smc_score * WEIGHT_SMC +
        tech_score * WEIGHT_TECHNICAL +
        drl_score * WEIGHT_DRL +
        sentiment_score * WEIGHT_SENTIMENT
    )
    
    # Calculate expected return
    price_5d_ago = df['Close'].iloc[-6] if len(df) >= 6 else current_price
    momentum_5d = ((current_price - price_5d_ago) / price_5d_ago) * 100
    expected_return = momentum_5d * 1.5 + (pred_change * 100) * 0.5
    
    # Determine signal type
    bullish_signals = sum([
        1 if mtf_signal == "BUY" else 0,
        1 if smc_signal in ["BUY", "STRONG_BUY"] else 0,
        1 if tech_signal in ["BUY", "STRONG_BUY"] else 0,
        1 if kronos_score > 0.6 else 0
    ])
    
    # Determine BUY/SELL/HOLD
    if (bullish_signals >= 3 and
        final_confidence >= MIN_CONFIDENCE and
        expected_return >= MIN_EXPECTED_RETURN and
        rsi < 75 and
        mtf_alignment >= 0.6):
        signal_type = "BUY"
    elif (bullish_signals <= 1 and
          final_confidence < 0.4 and
          expected_return < -MIN_EXPECTED_RETURN and
          rsi > 25):
        signal_type = "SELL"
    else:
        signal_type = "HOLD"
    
    # Component scores
    component_scores = {
        'mtf_score': mtf_score,
        'smc_score': smc_score,
        'tech_score': tech_score,
        'sentiment_score': sentiment_score,
        'kronos_score': kronos_score,
        'drl_score': drl_score
    }
    
    # Generate complete signal
    signal = generate_complete_signal(
        ticker=ticker,
        df=df,
        signal_type=signal_type,
        confidence=final_confidence,
        expected_return=expected_return,
        component_scores=component_scores,
        capital=CAPITAL,
        risk_per_trade=RISK_PER_TRADE
    )
    
    return signal

def main():
    """Main function"""
    print("="*100)
    print(f"🚀 NSE AlphaBot - Trading Signal Generator - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("="*100)
    print(f"Capital: ₹{CAPITAL:,} | Risk per Trade: {RISK_PER_TRADE:.1%}")
    print(f"Min Confidence: {MIN_CONFIDENCE:.0%} | Min Return: {MIN_EXPECTED_RETURN:.1f}%")
    print("="*100)
    print()
    
    # Screen stocks
    print("📊 STEP 1: Screening NSE Stocks...")
    print("="*100)
    
    qualified_stocks = screen_nse_stocks(max_stocks=20, min_volume=1000000)
    
    if not qualified_stocks:
        print("⚠️  No stocks qualified")
        return
    
    print(f"✅ Found {len(qualified_stocks)} qualified stocks")
    print()
    
    # Analyze stocks
    print("📊 STEP 2: Analyzing Stocks...")
    print("="*100)
    print()
    
    all_signals = []
    buy_signals = []
    sell_signals = []
    
    for i, ticker in enumerate(qualified_stocks, 1):
        print(f"[{i:2}/{len(qualified_stocks)}] Analyzing {ticker:15}...", end=" ")
        
        try:
            signal = analyze_stock(ticker)
            
            if signal is None:
                print("❌ No data")
                continue
            
            all_signals.append(signal)
            
            if signal['signal'] == 'BUY':
                buy_signals.append(signal)
                print(f"🎯 BUY  | Conf: {signal['confidence']:.1f}% | Return: {signal['expected_return']:+.1f}%")
            elif signal['signal'] == 'SELL':
                sell_signals.append(signal)
                print(f"📉 SELL | Conf: {signal['confidence']:.1f}% | Return: {signal['expected_return']:+.1f}%")
            else:
                print(f"⏸️  HOLD | Conf: {signal['confidence']:.1f}%")
                
        except Exception as e:
            print(f"❌ Error: {str(e)[:40]}")
    
    print()
    print("="*100)
    print(f"📊 RESULTS SUMMARY")
    print("="*100)
    print(f"Total Analyzed: {len(all_signals)}")
    print(f"BUY Signals: {len(buy_signals)}")
    print(f"SELL Signals: {len(sell_signals)}")
    print(f"HOLD Signals: {len(all_signals) - len(buy_signals) - len(sell_signals)}")
    print("="*100)
    print()
    
    # Print BUY signals
    if buy_signals:
        print("="*100)
        print(f"🎯 BUY SIGNALS ({len(buy_signals)})")
        print("="*100)
        
        # Sort by confidence * expected_return
        buy_signals.sort(key=lambda x: x['confidence'] * x['expected_return'], reverse=True)
        
        for signal in buy_signals:
            print_trading_signal(signal)
        
        # Save to JSON
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'buy_signals_{timestamp}.json'
        
        with open(filename, 'w') as f:
            json.dump(buy_signals, f, indent=2)
        
        print(f"✅ BUY signals saved to: {filename}")
        print()
    
    # Print SELL signals
    if sell_signals:
        print("="*100)
        print(f"📉 SELL SIGNALS ({len(sell_signals)})")
        print("="*100)
        
        # Sort by confidence * abs(expected_return)
        sell_signals.sort(key=lambda x: x['confidence'] * abs(x['expected_return']), reverse=True)
        
        for signal in sell_signals:
            print_trading_signal(signal)
        
        # Save to JSON
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'sell_signals_{timestamp}.json'
        
        with open(filename, 'w') as f:
            json.dump(sell_signals, f, indent=2)
        
        print(f"✅ SELL signals saved to: {filename}")
        print()
    
    if not buy_signals and not sell_signals:
        print("="*100)
        print("⏸️  NO ACTIONABLE SIGNALS TODAY")
        print("="*100)
        print("All stocks are in HOLD status.")
        print("Market conditions may not be favorable for trading.")
        print("="*100)
    
    print()
    print(f"✅ Analysis complete at {datetime.now().strftime('%H:%M:%S')}")
    print("="*100)

if __name__ == "__main__":
    main()
