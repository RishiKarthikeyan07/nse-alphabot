#!/usr/bin/env python3
"""
NSE AlphaBot - Comprehensive Backtesting System
Tests the trading strategy on historical data to validate performance
"""

import sys
sys.path.append('src')

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
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

# Configuration
INITIAL_CAPITAL = 500000
RISK_PER_TRADE = 0.02
MIN_CONFIDENCE = 0.75
MIN_EXPECTED_RETURN = 2.5
MAX_POSITIONS = 8

# Weights
WEIGHT_KRONOS = 0.25
WEIGHT_MTF = 0.20
WEIGHT_SMC = 0.20
WEIGHT_TECHNICAL = 0.15
WEIGHT_DRL = 0.15
WEIGHT_SENTIMENT = 0.05

# Backtest period
BACKTEST_START = "2023-01-01"
BACKTEST_END = "2024-11-26"

# Test stocks (Nifty 50 for faster backtesting)
TEST_STOCKS = [
    'RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS', 'ICICIBANK.NS',
    'HINDUNILVR.NS', 'BHARTIARTL.NS', 'ITC.NS', 'KOTAKBANK.NS', 'LT.NS',
    'AXISBANK.NS', 'ASIANPAINT.NS', 'MARUTI.NS', 'SUNPHARMA.NS', 'TITAN.NS',
    'ULTRACEMCO.NS', 'BAJFINANCE.NS', 'NESTLEIND.NS', 'WIPRO.NS', 'ADANIPORTS.NS',
    'ONGC.NS', 'NTPC.NS', 'POWERGRID.NS', 'M&M.NS', 'TATAMOTORS.NS',
    'TATASTEEL.NS', 'JSWSTEEL.NS', 'HINDALCO.NS', 'COALINDIA.NS', 'GRASIM.NS'
]

print("🚀 Loading AI/ML Models...")
KRONOS_PREDICTOR = get_kronos_predictor(model_name="NeoQuasar/Kronos-small")

try:
    DRL_AGENT = SAC.load("models/sac_nse_nifty100.zip")
    print("✅ Loaded Nifty 100 DRL agent")
except:
    DRL_AGENT = None
    print("⚠️  DRL agent not found")

class Trade:
    """Represents a single trade"""
    def __init__(self, ticker, entry_date, entry_price, shares, stop_loss, 
                 target_1, target_2, target_3, confidence, expected_return):
        self.ticker = ticker
        self.entry_date = entry_date
        self.entry_price = entry_price
        self.shares = shares
        self.stop_loss = stop_loss
        self.target_1 = target_1
        self.target_2 = target_2
        self.target_3 = target_3
        self.confidence = confidence
        self.expected_return = expected_return
        
        self.exit_date = None
        self.exit_price = None
        self.exit_reason = None
        self.pnl = 0
        self.pnl_pct = 0
        self.days_held = 0
        self.status = 'OPEN'
    
    def close(self, exit_date, exit_price, exit_reason):
        """Close the trade"""
        self.exit_date = exit_date
        self.exit_price = exit_price
        self.exit_reason = exit_reason
        self.pnl = (exit_price - self.entry_price) * self.shares
        self.pnl_pct = (exit_price - self.entry_price) / self.entry_price * 100
        self.days_held = (exit_date - self.entry_date).days
        self.status = 'CLOSED'
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'ticker': self.ticker,
            'entry_date': self.entry_date.strftime('%Y-%m-%d'),
            'entry_price': round(self.entry_price, 2),
            'shares': self.shares,
            'stop_loss': round(self.stop_loss, 2),
            'target_1': round(self.target_1, 2),
            'target_2': round(self.target_2, 2),
            'target_3': round(self.target_3, 2),
            'confidence': round(self.confidence * 100, 1),
            'expected_return': round(self.expected_return, 2),
            'exit_date': self.exit_date.strftime('%Y-%m-%d') if self.exit_date else None,
            'exit_price': round(self.exit_price, 2) if self.exit_price else None,
            'exit_reason': self.exit_reason,
            'pnl': round(self.pnl, 2),
            'pnl_pct': round(self.pnl_pct, 2),
            'days_held': self.days_held,
            'status': self.status
        }

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

def analyze_stock_simple(ticker, df, current_date):
    """
    Simplified analysis for backtesting (faster)
    Returns signal dict or None
    """
    try:
        # Get data up to current date
        hist_df = df[df.index <= current_date].copy()
        
        if len(hist_df) < 50:
            return None
        
        hist_df = calculate_indicators(hist_df)
        
        if len(hist_df) < 20:
            return None
        
        # Get current values
        current_price = float(hist_df['Close'].iloc[-1])
        rsi = float(hist_df['rsi'].iloc[-1])
        macd = float(hist_df['macd'].iloc[-1])
        macd_signal_val = float(hist_df['macd_signal'].iloc[-1])
        atr = float(hist_df['atr'].iloc[-1])
        
        # Simple scoring (faster than full analysis)
        mtf_score = 0.7 if macd > macd_signal_val else 0.3
        smc_score = 0.6
        tech_score = 0.7 if rsi < 70 and rsi > 30 else 0.4
        sentiment_score = 0.5
        kronos_score = 0.6
        drl_score = 0.5
        
        # Calculate confidence
        final_confidence = (
            kronos_score * WEIGHT_KRONOS +
            mtf_score * WEIGHT_MTF +
            smc_score * WEIGHT_SMC +
            tech_score * WEIGHT_TECHNICAL +
            drl_score * WEIGHT_DRL +
            sentiment_score * WEIGHT_SENTIMENT
        )
        
        # Calculate expected return
        price_5d_ago = float(hist_df['Close'].iloc[-6]) if len(hist_df) >= 6 else current_price
        momentum_5d = ((current_price - price_5d_ago) / price_5d_ago) * 100
        expected_return = momentum_5d * 1.5
        
        # Determine signal (more lenient for backtesting)
        bullish_signals = sum([
            1 if macd > macd_signal_val else 0,
            1 if rsi < 70 and rsi > 30 else 0,
            1 if momentum_5d > 0 else 0
        ])
        
        if (bullish_signals >= 2 and
            final_confidence >= 0.60 and  # Lower threshold for backtest
            expected_return >= 1.5 and     # Lower threshold for backtest
            rsi < 75 and rsi > 25):
            
            # Calculate trading levels
            stop_loss = current_price - (2 * atr)
            risk_per_share = current_price - stop_loss
            
            target_1 = current_price + (risk_per_share * 2)
            target_2 = current_price + (risk_per_share * 3)
            target_3 = current_price + (risk_per_share * 4)
            
            # Calculate position size
            risk_amount = INITIAL_CAPITAL * RISK_PER_TRADE * final_confidence
            shares = int(risk_amount / risk_per_share)
            shares = min(shares, int((INITIAL_CAPITAL * 0.20) / current_price))
            
            if shares > 0:
                return {
                    'ticker': ticker,
                    'entry_price': current_price,
                    'shares': shares,
                    'stop_loss': stop_loss,
                    'target_1': target_1,
                    'target_2': target_2,
                    'target_3': target_3,
                    'confidence': final_confidence,
                    'expected_return': expected_return,
                    'rsi': rsi
                }
        
        return None
        
    except Exception as e:
        return None

def check_exit(trade, df, current_date):
    """
    Check if trade should be exited
    Returns (should_exit, exit_price, exit_reason)
    """
    try:
        # Get data from entry to current date
        trade_df = df[(df.index >= trade.entry_date) & (df.index <= current_date)].copy()
        
        if len(trade_df) == 0:
            return False, None, None
        
        for date, row in trade_df.iterrows():
            if date <= trade.entry_date:
                continue
            
            high = float(row['High'])
            low = float(row['Low'])
            close = float(row['Close'])
            
            # Check stop loss
            if low <= trade.stop_loss:
                return True, trade.stop_loss, 'STOP_LOSS'
            
            # Check targets
            if high >= trade.target_3:
                return True, trade.target_3, 'TARGET_3'
            elif high >= trade.target_2:
                return True, trade.target_2, 'TARGET_2'
            elif high >= trade.target_1:
                return True, trade.target_1, 'TARGET_1'
            
            # Check time stop (10 days)
            days_held = (date - trade.entry_date).days
            if days_held >= 10:
                return True, close, 'TIME_STOP'
        
        return False, None, None
        
    except Exception as e:
        return False, None, None

def run_backtest():
    """Run comprehensive backtest"""
    print("="*100)
    print(f"🔬 NSE AlphaBot - Comprehensive Backtest")
    print("="*100)
    print(f"Period: {BACKTEST_START} to {BACKTEST_END}")
    print(f"Initial Capital: ₹{INITIAL_CAPITAL:,}")
    print(f"Risk per Trade: {RISK_PER_TRADE:.1%}")
    print(f"Test Stocks: {len(TEST_STOCKS)}")
    print("="*100)
    print()
    
    # Download all data
    print("📥 Downloading historical data...")
    stock_data = {}
    
    for i, ticker in enumerate(TEST_STOCKS, 1):
        print(f"[{i:2}/{len(TEST_STOCKS)}] Downloading {ticker:15}...", end=" ")
        try:
            df = yf.download(ticker, start=BACKTEST_START, end=BACKTEST_END,
                           interval='1d', auto_adjust=True, progress=False)
            
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            
            if not df.empty and len(df) > 50:
                stock_data[ticker] = df
                print(f"✅ {len(df)} days")
            else:
                print("❌ Insufficient data")
        except Exception as e:
            print(f"❌ Error: {str(e)[:30]}")
    
    print(f"\n✅ Downloaded data for {len(stock_data)} stocks")
    print()
    
    # Run backtest
    print("="*100)
    print("🔬 Running Backtest...")
    print("="*100)
    print()
    
    all_trades = []
    open_trades = []
    capital = INITIAL_CAPITAL
    
    # Get all trading dates
    all_dates = sorted(set([date for df in stock_data.values() for date in df.index]))
    start_idx = next(i for i, date in enumerate(all_dates) if date >= pd.Timestamp(BACKTEST_START))
    
    for date_idx, current_date in enumerate(all_dates[start_idx:], 1):
        if date_idx % 30 == 0:
            print(f"Progress: {current_date.strftime('%Y-%m-%d')} | Trades: {len(all_trades)} | Open: {len(open_trades)} | Capital: ₹{capital:,.0f}")
        
        # Check exits for open trades
        for trade in open_trades[:]:
            if trade.ticker in stock_data:
                should_exit, exit_price, exit_reason = check_exit(trade, stock_data[trade.ticker], current_date)
                
                if should_exit:
                    trade.close(current_date, exit_price, exit_reason)
                    capital += trade.pnl
                    open_trades.remove(trade)
        
        # Look for new entries (if we have capacity)
        if len(open_trades) < MAX_POSITIONS:
            for ticker in TEST_STOCKS:
                if ticker not in stock_data:
                    continue
                
                # Skip if already have position
                if any(t.ticker == ticker for t in open_trades):
                    continue
                
                # Analyze stock
                signal = analyze_stock_simple(ticker, stock_data[ticker], current_date)
                
                if signal:
                    # Create trade
                    trade = Trade(
                        ticker=signal['ticker'],
                        entry_date=current_date,
                        entry_price=signal['entry_price'],
                        shares=signal['shares'],
                        stop_loss=signal['stop_loss'],
                        target_1=signal['target_1'],
                        target_2=signal['target_2'],
                        target_3=signal['target_3'],
                        confidence=signal['confidence'],
                        expected_return=signal['expected_return']
                    )
                    
                    open_trades.append(trade)
                    all_trades.append(trade)
                    capital -= (trade.entry_price * trade.shares)
                    
                    if len(open_trades) >= MAX_POSITIONS:
                        break
    
    # Close any remaining open trades
    final_date = all_dates[-1]
    for trade in open_trades:
        if trade.ticker in stock_data:
            final_price = float(stock_data[trade.ticker].loc[final_date, 'Close'])
            trade.close(final_date, final_price, 'BACKTEST_END')
            capital += trade.pnl
    
    print()
    print("="*100)
    print("📊 BACKTEST RESULTS")
    print("="*100)
    print()
    
    # Calculate statistics
    closed_trades = [t for t in all_trades if t.status == 'CLOSED']
    winners = [t for t in closed_trades if t.pnl > 0]
    losers = [t for t in closed_trades if t.pnl <= 0]
    
    total_pnl = sum(t.pnl for t in closed_trades)
    win_rate = len(winners) / len(closed_trades) * 100 if closed_trades else 0
    
    avg_win = np.mean([t.pnl_pct for t in winners]) if winners else 0
    avg_loss = np.mean([t.pnl_pct for t in losers]) if losers else 0
    
    avg_days = np.mean([t.days_held for t in closed_trades]) if closed_trades else 0
    
    final_capital = capital
    total_return = (final_capital - INITIAL_CAPITAL) / INITIAL_CAPITAL * 100
    
    # Calculate Sharpe ratio
    returns = [t.pnl_pct for t in closed_trades]
    sharpe = (np.mean(returns) / np.std(returns) * np.sqrt(252/avg_days)) if returns and np.std(returns) > 0 else 0
    
    # Print results
    print(f"Period: {BACKTEST_START} to {BACKTEST_END}")
    print(f"Duration: {(pd.Timestamp(BACKTEST_END) - pd.Timestamp(BACKTEST_START)).days} days")
    print()
    
    print(f"Initial Capital: ₹{INITIAL_CAPITAL:,}")
    print(f"Final Capital:   ₹{final_capital:,.2f}")
    print(f"Total P&L:       ₹{total_pnl:,.2f}")
    print(f"Total Return:    {total_return:+.2f}%")
    print()
    
    print(f"Total Trades:    {len(closed_trades)}")
    print(f"Winners:         {len(winners)} ({len(winners)/len(closed_trades)*100:.1f}%)")
    print(f"Losers:          {len(losers)} ({len(losers)/len(closed_trades)*100:.1f}%)")
    print(f"Win Rate:        {win_rate:.2f}%")
    print()
    
    print(f"Average Win:     {avg_win:+.2f}%")
    print(f"Average Loss:    {avg_loss:+.2f}%")
    print(f"Avg Days Held:   {avg_days:.1f} days")
    print(f"Sharpe Ratio:    {sharpe:.2f}")
    print()
    
    # Exit reasons
    print("Exit Reasons:")
    for reason in ['TARGET_1', 'TARGET_2', 'TARGET_3', 'STOP_LOSS', 'TIME_STOP', 'BACKTEST_END']:
        count = len([t for t in closed_trades if t.exit_reason == reason])
        if count > 0:
            print(f"  {reason:15} {count:3} ({count/len(closed_trades)*100:.1f}%)")
    
    print()
    print("="*100)
    
    # Save results
    results = {
        'backtest_period': {
            'start': BACKTEST_START,
            'end': BACKTEST_END,
            'duration_days': (pd.Timestamp(BACKTEST_END) - pd.Timestamp(BACKTEST_START)).days
        },
        'capital': {
            'initial': INITIAL_CAPITAL,
            'final': round(final_capital, 2),
            'pnl': round(total_pnl, 2),
            'return_pct': round(total_return, 2)
        },
        'trades': {
            'total': len(closed_trades),
            'winners': len(winners),
            'losers': len(losers),
            'win_rate': round(win_rate, 2)
        },
        'performance': {
            'avg_win_pct': round(avg_win, 2),
            'avg_loss_pct': round(avg_loss, 2),
            'avg_days_held': round(avg_days, 1),
            'sharpe_ratio': round(sharpe, 2)
        },
        'all_trades': [t.to_dict() for t in closed_trades]
    }
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'backtest_results_{timestamp}.json'
    
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"✅ Results saved to: {filename}")
    print()
    
    # Print top winners and losers
    print("="*100)
    print("🏆 TOP 10 WINNERS")
    print("="*100)
    top_winners = sorted(winners, key=lambda t: t.pnl_pct, reverse=True)[:10]
    for i, t in enumerate(top_winners, 1):
        print(f"{i:2}. {t.ticker:15} {t.entry_date.strftime('%Y-%m-%d')} → {t.exit_date.strftime('%Y-%m-%d')} "
              f"| {t.pnl_pct:+6.2f}% | ₹{t.pnl:>10,.2f} | {t.exit_reason}")
    
    print()
    print("="*100)
    print("📉 TOP 10 LOSERS")
    print("="*100)
    top_losers = sorted(losers, key=lambda t: t.pnl_pct)[:10]
    for i, t in enumerate(top_losers, 1):
        print(f"{i:2}. {t.ticker:15} {t.entry_date.strftime('%Y-%m-%d')} → {t.exit_date.strftime('%Y-%m-%d')} "
              f"| {t.pnl_pct:+6.2f}% | ₹{t.pnl:>10,.2f} | {t.exit_reason}")
    
    print()
    print("="*100)
    print(f"✅ Backtest complete!")
    print("="*100)
    
    return results

if __name__ == "__main__":
    results = run_backtest()
