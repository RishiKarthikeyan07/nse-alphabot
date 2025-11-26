"""
Trading Signal Generator with Complete Price Levels
Generates actionable BUY/SELL/HOLD signals with:
- Entry Price
- Target Prices (T1, T2, T3)
- Stop Loss Price
- Risk-Reward Ratio
- Position Size
"""

import numpy as np
import pandas as pd
from datetime import datetime
import json

def calculate_trading_levels(df, signal_type, confidence, expected_return):
    """
    Calculate complete trading levels for a signal
    
    Args:
        df: DataFrame with OHLCV data and indicators
        signal_type: 'BUY', 'SELL', or 'HOLD'
        confidence: Signal confidence (0-1)
        expected_return: Expected return percentage
        
    Returns:
        Dict with entry, targets, stop-loss, and risk-reward
    """
    current_price = float(df['Close'].iloc[-1])
    atr = float(df['atr'].iloc[-1])
    
    # Get support and resistance levels
    recent_high = float(df['High'].iloc[-20:].max())
    recent_low = float(df['Low'].iloc[-20:].min())
    
    if signal_type == 'BUY':
        # Entry Price: Current market price
        entry_price = current_price
        
        # Stop Loss: 2 ATR below entry or recent low (whichever is closer)
        sl_atr = entry_price - (2 * atr)
        sl_support = recent_low * 0.98  # 2% below recent low
        stop_loss = max(sl_atr, sl_support)
        
        # Risk per share
        risk_per_share = entry_price - stop_loss
        
        # Target Prices based on risk-reward ratios
        target_1 = entry_price + (risk_per_share * 2)  # 2:1 R:R
        target_2 = entry_price + (risk_per_share * 3)  # 3:1 R:R
        target_3 = entry_price + (risk_per_share * 4)  # 4:1 R:R
        
        # Adjust targets based on expected return
        if expected_return > 5:
            target_1 = entry_price * (1 + expected_return / 200)  # 50% of expected
            target_2 = entry_price * (1 + expected_return / 133)  # 75% of expected
            target_3 = entry_price * (1 + expected_return / 100)  # 100% of expected
        
        # Ensure targets don't exceed recent high + 10%
        max_target = recent_high * 1.10
        target_1 = min(target_1, max_target * 0.95)
        target_2 = min(target_2, max_target * 0.98)
        target_3 = min(target_3, max_target)
        
        # Calculate risk-reward ratio
        avg_target = (target_1 + target_2 + target_3) / 3
        risk_reward = (avg_target - entry_price) / risk_per_share if risk_per_share > 0 else 0
        
        return {
            'signal': 'BUY',
            'entry_price': round(entry_price, 2),
            'stop_loss': round(stop_loss, 2),
            'target_1': round(target_1, 2),
            'target_2': round(target_2, 2),
            'target_3': round(target_3, 2),
            'risk_per_share': round(risk_per_share, 2),
            'risk_reward_ratio': round(risk_reward, 2),
            'stop_loss_pct': round((stop_loss - entry_price) / entry_price * 100, 2),
            'target_1_pct': round((target_1 - entry_price) / entry_price * 100, 2),
            'target_2_pct': round((target_2 - entry_price) / entry_price * 100, 2),
            'target_3_pct': round((target_3 - entry_price) / entry_price * 100, 2)
        }
    
    elif signal_type == 'SELL':
        # Entry Price: Current market price
        entry_price = current_price
        
        # Stop Loss: 2 ATR above entry or recent high (whichever is closer)
        sl_atr = entry_price + (2 * atr)
        sl_resistance = recent_high * 1.02  # 2% above recent high
        stop_loss = min(sl_atr, sl_resistance)
        
        # Risk per share
        risk_per_share = stop_loss - entry_price
        
        # Target Prices based on risk-reward ratios
        target_1 = entry_price - (risk_per_share * 2)  # 2:1 R:R
        target_2 = entry_price - (risk_per_share * 3)  # 3:1 R:R
        target_3 = entry_price - (risk_per_share * 4)  # 4:1 R:R
        
        # Adjust targets based on expected return (negative for SELL)
        if abs(expected_return) > 5:
            target_1 = entry_price * (1 - abs(expected_return) / 200)  # 50% of expected
            target_2 = entry_price * (1 - abs(expected_return) / 133)  # 75% of expected
            target_3 = entry_price * (1 - abs(expected_return) / 100)  # 100% of expected
        
        # Ensure targets don't go below recent low - 10%
        min_target = recent_low * 0.90
        target_1 = max(target_1, min_target * 1.05)
        target_2 = max(target_2, min_target * 1.02)
        target_3 = max(target_3, min_target)
        
        # Calculate risk-reward ratio
        avg_target = (target_1 + target_2 + target_3) / 3
        risk_reward = (entry_price - avg_target) / risk_per_share if risk_per_share > 0 else 0
        
        return {
            'signal': 'SELL',
            'entry_price': round(entry_price, 2),
            'stop_loss': round(stop_loss, 2),
            'target_1': round(target_1, 2),
            'target_2': round(target_2, 2),
            'target_3': round(target_3, 2),
            'risk_per_share': round(risk_per_share, 2),
            'risk_reward_ratio': round(risk_reward, 2),
            'stop_loss_pct': round((stop_loss - entry_price) / entry_price * 100, 2),
            'target_1_pct': round((target_1 - entry_price) / entry_price * 100, 2),
            'target_2_pct': round((target_2 - entry_price) / entry_price * 100, 2),
            'target_3_pct': round((target_3 - entry_price) / entry_price * 100, 2)
        }
    
    else:  # HOLD
        return {
            'signal': 'HOLD',
            'entry_price': round(current_price, 2),
            'stop_loss': None,
            'target_1': None,
            'target_2': None,
            'target_3': None,
            'risk_per_share': None,
            'risk_reward_ratio': None,
            'stop_loss_pct': None,
            'target_1_pct': None,
            'target_2_pct': None,
            'target_3_pct': None
        }


def calculate_position_size_with_risk(capital, risk_per_trade_pct, entry_price, stop_loss, confidence):
    """
    Calculate position size based on risk management
    
    Args:
        capital: Total trading capital
        risk_per_trade_pct: Risk percentage per trade (e.g., 0.02 for 2%)
        entry_price: Entry price per share
        stop_loss: Stop loss price per share
        confidence: Signal confidence (0-1)
        
    Returns:
        Dict with shares, position size, and risk amount
    """
    if stop_loss is None or entry_price == stop_loss:
        return {
            'shares': 0,
            'position_size': 0,
            'risk_amount': 0,
            'position_pct': 0
        }
    
    # Calculate risk per share
    risk_per_share = abs(entry_price - stop_loss)
    
    # Calculate maximum risk amount
    max_risk_amount = capital * risk_per_trade_pct
    
    # Adjust risk based on confidence
    confidence_multiplier = 0.5 + (confidence * 0.5)  # 0.5x to 1.0x
    adjusted_risk_amount = max_risk_amount * confidence_multiplier
    
    # Calculate number of shares
    shares = int(adjusted_risk_amount / risk_per_share)
    
    # Calculate actual position size
    position_size = shares * entry_price
    
    # Cap position size at 20% of capital
    max_position = capital * 0.20
    if position_size > max_position:
        shares = int(max_position / entry_price)
        position_size = shares * entry_price
    
    # Calculate actual risk amount
    actual_risk = shares * risk_per_share
    
    return {
        'shares': shares,
        'position_size': round(position_size, 2),
        'risk_amount': round(actual_risk, 2),
        'position_pct': round(position_size / capital * 100, 2)
    }


def generate_complete_signal(ticker, df, signal_type, confidence, expected_return, 
                            component_scores, capital=500000, risk_per_trade=0.02):
    """
    Generate complete trading signal with all details
    
    Args:
        ticker: Stock ticker
        df: DataFrame with OHLCV data
        signal_type: 'BUY', 'SELL', or 'HOLD'
        confidence: Signal confidence (0-1)
        expected_return: Expected return percentage
        component_scores: Dict with scores from all analysis methods
        capital: Trading capital
        risk_per_trade: Risk percentage per trade
        
    Returns:
        Complete trading signal dict
    """
    # Calculate trading levels
    levels = calculate_trading_levels(df, signal_type, confidence, expected_return)
    
    # Calculate position size
    position = calculate_position_size_with_risk(
        capital, risk_per_trade, levels['entry_price'], levels['stop_loss'], confidence
    )
    
    # Combine all information
    signal = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'ticker': ticker,
        'signal': levels['signal'],
        'confidence': round(confidence * 100, 1),
        'expected_return': round(expected_return, 2),
        
        # Price Levels
        'entry_price': levels['entry_price'],
        'stop_loss': levels['stop_loss'],
        'target_1': levels['target_1'],
        'target_2': levels['target_2'],
        'target_3': levels['target_3'],
        
        # Percentage Levels
        'stop_loss_pct': levels['stop_loss_pct'],
        'target_1_pct': levels['target_1_pct'],
        'target_2_pct': levels['target_2_pct'],
        'target_3_pct': levels['target_3_pct'],
        
        # Risk Management
        'risk_per_share': levels['risk_per_share'],
        'risk_reward_ratio': levels['risk_reward_ratio'],
        'shares': position['shares'],
        'position_size': position['position_size'],
        'risk_amount': position['risk_amount'],
        'position_pct': position['position_pct'],
        
        # Component Scores
        'mtf_score': round(component_scores.get('mtf_score', 0.5), 2),
        'smc_score': round(component_scores.get('smc_score', 0.5), 2),
        'tech_score': round(component_scores.get('tech_score', 0.5), 2),
        'sentiment_score': round(component_scores.get('sentiment_score', 0.5), 2),
        'kronos_score': round(component_scores.get('kronos_score', 0.5), 2),
        'drl_score': round(component_scores.get('drl_score', 0.5), 2),
        
        # Additional Info
        'rsi': round(float(df['rsi'].iloc[-1]), 1),
        'volume_ratio': round(float(df['volume_ratio'].iloc[-1]), 2)
    }
    
    return signal


def print_trading_signal(signal):
    """
    Print trading signal in a formatted way
    
    Args:
        signal: Complete trading signal dict
    """
    print(f"\n{'='*80}")
    print(f"📊 TRADING SIGNAL: {signal['ticker']}")
    print(f"{'='*80}")
    print(f"Timestamp: {signal['timestamp']}")
    print(f"Signal: {signal['signal']} | Confidence: {signal['confidence']}%")
    print(f"Expected Return: {signal['expected_return']:+.2f}%")
    print()
    
    if signal['signal'] in ['BUY', 'SELL']:
        print(f"{'─'*80}")
        print(f"PRICE LEVELS:")
        print(f"{'─'*80}")
        print(f"Entry Price:    ₹{signal['entry_price']:>10.2f}")
        print(f"Stop Loss:      ₹{signal['stop_loss']:>10.2f}  ({signal['stop_loss_pct']:+.2f}%)")
        print(f"Target 1:       ₹{signal['target_1']:>10.2f}  ({signal['target_1_pct']:+.2f}%)")
        print(f"Target 2:       ₹{signal['target_2']:>10.2f}  ({signal['target_2_pct']:+.2f}%)")
        print(f"Target 3:       ₹{signal['target_3']:>10.2f}  ({signal['target_3_pct']:+.2f}%)")
        print()
        
        print(f"{'─'*80}")
        print(f"POSITION SIZING:")
        print(f"{'─'*80}")
        print(f"Shares:         {signal['shares']:>10} shares")
        print(f"Position Size:  ₹{signal['position_size']:>10,.2f}  ({signal['position_pct']:.1f}% of capital)")
        print(f"Risk Amount:    ₹{signal['risk_amount']:>10,.2f}")
        print(f"Risk/Share:     ₹{signal['risk_per_share']:>10.2f}")
        print(f"Risk:Reward:    1:{signal['risk_reward_ratio']:.2f}")
        print()
        
        print(f"{'─'*80}")
        print(f"COMPONENT SCORES:")
        print(f"{'─'*80}")
        print(f"Kronos AI:      {signal['kronos_score']:.2f}  (25% weight)")
        print(f"Multi-TF:       {signal['mtf_score']:.2f}  (20% weight)")
        print(f"SMC:            {signal['smc_score']:.2f}  (20% weight)")
        print(f"Technical:      {signal['tech_score']:.2f}  (15% weight)")
        print(f"DRL Agent:      {signal['drl_score']:.2f}  (15% weight)")
        print(f"Sentiment:      {signal['sentiment_score']:.2f}  (5% weight)")
        print()
        
        print(f"{'─'*80}")
        print(f"TECHNICAL INDICATORS:")
        print(f"{'─'*80}")
        print(f"RSI:            {signal['rsi']:.1f}")
        print(f"Volume Ratio:   {signal['volume_ratio']:.2f}x")
        print()
        
        print(f"{'─'*80}")
        print(f"TRADING PLAN:")
        print(f"{'─'*80}")
        if signal['signal'] == 'BUY':
            print(f"1. BUY {signal['shares']} shares at ₹{signal['entry_price']:.2f}")
            print(f"2. Set Stop Loss at ₹{signal['stop_loss']:.2f}")
            print(f"3. Take Profit:")
            print(f"   - Sell 33% at ₹{signal['target_1']:.2f} (T1)")
            print(f"   - Sell 33% at ₹{signal['target_2']:.2f} (T2)")
            print(f"   - Sell 34% at ₹{signal['target_3']:.2f} (T3)")
            print(f"4. Trail stop loss after T1 is hit")
        else:  # SELL
            print(f"1. SELL {signal['shares']} shares at ₹{signal['entry_price']:.2f}")
            print(f"2. Set Stop Loss at ₹{signal['stop_loss']:.2f}")
            print(f"3. Take Profit:")
            print(f"   - Cover 33% at ₹{signal['target_1']:.2f} (T1)")
            print(f"   - Cover 33% at ₹{signal['target_2']:.2f} (T2)")
            print(f"   - Cover 34% at ₹{signal['target_3']:.2f} (T3)")
            print(f"4. Trail stop loss after T1 is hit")
    else:
        print(f"Current Price: ₹{signal['entry_price']:.2f}")
        print(f"No action recommended at this time.")
    
    print(f"{'='*80}\n")


def save_signal_to_json(signal, filename='trading_signals.json'):
    """
    Save trading signal to JSON file
    
    Args:
        signal: Complete trading signal dict
        filename: Output filename
    """
    try:
        # Load existing signals
        try:
            with open(filename, 'r') as f:
                signals = json.load(f)
        except FileNotFoundError:
            signals = []
        
        # Append new signal
        signals.append(signal)
        
        # Save back to file
        with open(filename, 'w') as f:
            json.dump(signals, f, indent=2)
        
        print(f"✅ Signal saved to {filename}")
    except Exception as e:
        print(f"❌ Error saving signal: {e}")


# Example usage
if __name__ == "__main__":
    import yfinance as yf
    
    # Test with sample data
    ticker = "RELIANCE.NS"
    df = yf.download(ticker, period='6mo', interval='1d', auto_adjust=True, progress=False)
    
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    
    # Calculate indicators
    delta = df['Close'].diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = (-delta.clip(upper=0)).rolling(14).mean()
    df['rsi'] = 100 - (100 / (1 + gain / loss))
    
    high_low = df['High'] - df['Low']
    high_close = (df['High'] - df['Close'].shift()).abs()
    low_close = (df['Low'] - df['Close'].shift()).abs()
    df['tr'] = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    df['atr'] = df['tr'].rolling(14).mean()
    
    df['volume_ratio'] = df['Volume'] / df['Volume'].rolling(20).mean()
    df = df.dropna()
    
    # Generate sample signal
    component_scores = {
        'mtf_score': 0.85,
        'smc_score': 0.75,
        'tech_score': 0.70,
        'sentiment_score': 0.60,
        'kronos_score': 0.80,
        'drl_score': 0.65
    }
    
    signal = generate_complete_signal(
        ticker=ticker,
        df=df,
        signal_type='BUY',
        confidence=0.82,
        expected_return=5.5,
        component_scores=component_scores,
        capital=500000,
        risk_per_trade=0.02
    )
    
    # Print signal
    print_trading_signal(signal)
    
    # Save to JSON
    save_signal_to_json(signal, 'test_signals.json')
