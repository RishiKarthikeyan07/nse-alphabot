# backtest_2y.py - 2-Year Backtest Validation for 90% Win Rate
import yfinance as yf
import pandas as pd
import numpy as np
import torch
from trendmaster import TransAm
from stable_baselines3 import SAC
from datetime import datetime, timedelta
import json
import os

print("="*100)
print("🔬 2-YEAR BACKTEST VALIDATION")
print("Target: Validate 90% Win Rate | FLEXIBLE SWING TRADING (3-14 days, extends to 2-4 weeks)")
print("="*100)

# Load trained models
print("\n📦 Loading Trained Models...")

# Load TrendMaster
TRENDMASTER_MODEL = TransAm(input_size=1, d_model=128, num_layers=4, nhead=8, dropout=0.1)
checkpoint = torch.load("models/trendmaster_nse.pth", map_location='cpu')
TRENDMASTER_MODEL.load_state_dict(checkpoint['model_state_dict'])
TRENDMASTER_MODEL.eval()
print("  ✅ Loaded TrendMaster model")

# Load DRL Agent
drl_agent = None
if os.path.exists("models/sac_nse_10y_final.zip"):
    drl_agent = SAC.load("models/sac_nse_10y_final.zip")
    print("  ✅ Loaded 10-year trained DRL agent")
elif os.path.exists("models/sac_nse_fixed.zip"):
    drl_agent = SAC.load("models/sac_nse_fixed.zip")
    print("  ⚠️  Loaded existing DRL agent (retrain with train_drl.py for better results)")
else:
    print("  ⚠️  No DRL agent found")

# Stocks to backtest
STOCKS = [
    'RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS', 'ICICIBANK.NS',
    'HINDUNILVR.NS', 'KOTAKBANK.NS', 'BHARTIARTL.NS', 'ITC.NS', 'ASIANPAINT.NS',
    'MARUTI.NS', 'AXISBANK.NS', 'LT.NS', 'SUNPHARMA.NS', 'TITAN.NS'
]

# Calculate indicators
def calculate_indicators(df):
    # RSI
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))
    
    # MACD
    exp1 = df['Close'].ewm(span=12, adjust=False).mean()
    exp2 = df['Close'].ewm(span=26, adjust=False).mean()
    df['macd'] = exp1 - exp2
    df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
    
    # EMA
    df['ema_9'] = df['Close'].ewm(span=9, adjust=False).mean()
    df['ema_21'] = df['Close'].ewm(span=21, adjust=False).mean()
    df['ema_50'] = df['Close'].ewm(span=50, adjust=False).mean()
    
    # ROC
    df['roc'] = ((df['Close'] - df['Close'].shift(12)) / df['Close'].shift(12)) * 100
    
    return df.dropna()

# Predict price
def predict_price(df):
    """Predict price 7 days ahead using TrendMaster"""
    sequence_length = 60
    if len(df) < sequence_length:
        return float(df['Close'].iloc[-1]) * 1.05
    
    input_seq = df['Close'].values[-sequence_length:].reshape(1, sequence_length, 1)
    input_tensor = torch.FloatTensor(input_seq)
    
    with torch.no_grad():
        pred = TRENDMASTER_MODEL(input_tensor)
        pred_7d = pred[0, 6].item()  # 7-day prediction
    return pred_7d

# Calculate confidence
def calculate_confidence(df):
    score = 0
    max_score = 0
    
    # RSI
    rsi = float(df['rsi'].iloc[-1])
    if 25 < rsi < 35:
        score += 20
    elif 35 < rsi < 45:
        score += 15
    elif rsi > 70:
        score -= 15
    max_score += 20
    
    # MACD
    macd = float(df['macd'].iloc[-1])
    macd_signal = float(df['macd_signal'].iloc[-1])
    if macd > macd_signal:
        score += 20
    max_score += 20
    
    # Trend
    ema_9 = float(df['ema_9'].iloc[-1])
    ema_21 = float(df['ema_21'].iloc[-1])
    ema_50 = float(df['ema_50'].iloc[-1])
    if ema_9 > ema_21 > ema_50:
        score += 30
    elif ema_9 > ema_21:
        score += 15
    max_score += 30
    
    # ROC
    roc = float(df['roc'].iloc[-1])
    if roc > 5:
        score += 10
    elif roc < -5:
        score -= 10
    max_score += 10
    
    confidence = max(0, min(1, score / max_score))
    return confidence

# Backtest function
def backtest_stock(ticker, start_date, end_date):
    print(f"\n📊 Backtesting {ticker}...")
    
    try:
        df = yf.download(ticker, start=start_date, end=end_date, progress=False)
        if len(df) < 200:
            print(f"  ⚠️  Insufficient data")
            return None
        
        df = calculate_indicators(df)
        
        capital = 100000
        shares = 0
        trades = []
        entry_price = 0
        entry_date = None
        
        for i in range(200, len(df)):
            current_df = df.iloc[:i+1]
            current_price = float(df['Close'].iloc[i])
            current_date = df.index[i]
            
            # Generate signal
            pred = predict_price(current_df)
            conf = calculate_confidence(current_df)
            expected_return = ((pred / current_price) - 1) * 100
            
            # BUY signal
            if shares == 0 and conf >= 0.85 and expected_return > 2:
                shares = int(capital * 0.95 / current_price)
                if shares > 0:
                    capital -= shares * current_price
                    entry_price = current_price
                    entry_date = current_date
                    trades.append({
                        'date': current_date,
                        'action': 'BUY',
                        'price': current_price,
                        'shares': shares,
                        'confidence': conf,
                        'expected_return': expected_return
                    })
            
            # SELL signal (flexible: 3-14 days swing, can extend to 2-4 weeks)
            elif shares > 0 and entry_date:
                holding_days = (current_date - entry_date).days
                actual_return = ((current_price / entry_price) - 1) * 100
                
                # Determine max holding based on performance (flexible)
                max_holding = 14  # Default: standard swing (14 days)
                if actual_return > 8 and conf > 0.90:  # Strong trend
                    max_holding = 28  # Extend to 2-4 weeks
                
                # Sell conditions (flexible)
                should_sell = False
                if holding_days >= 3:  # Minimum 3 days (swing)
                    if actual_return >= 5:  # Target hit
                        should_sell = True
                    elif actual_return <= -3:  # Stop loss
                        should_sell = True
                    elif holding_days >= max_holding:  # Max holding (flexible)
                        should_sell = True
                    elif holding_days >= 7 and conf < 0.70:  # Confidence dropped
                        should_sell = True
                
                if should_sell:
                    sell_value = shares * current_price
                    capital += sell_value
                    profit = sell_value - (shares * entry_price)
                    
                    trades.append({
                        'date': current_date,
                        'action': 'SELL',
                        'price': current_price,
                        'shares': shares,
                        'profit': profit,
                        'return': actual_return,
                        'holding_days': holding_days
                    })
                    shares = 0
                    entry_price = 0
                    entry_date = None
        
        # Calculate metrics
        buy_trades = [t for t in trades if t['action'] == 'BUY']
        sell_trades = [t for t in trades if t['action'] == 'SELL']
        
        if len(sell_trades) > 0:
            wins = len([t for t in sell_trades if t['return'] > 0])
            losses = len([t for t in sell_trades if t['return'] <= 0])
            win_rate = (wins / len(sell_trades)) * 100
            
            avg_return = np.mean([t['return'] for t in sell_trades])
            avg_holding = np.mean([t['holding_days'] for t in sell_trades])
            
            total_return = ((capital + (shares * float(df['Close'].iloc[-1]))) / 100000 - 1) * 100
            
            # Calculate max drawdown
            equity_curve = [100000]
            temp_capital = 100000
            temp_shares = 0
            for trade in trades:
                if trade['action'] == 'BUY':
                    temp_shares = trade['shares']
                    temp_capital -= temp_shares * trade['price']
                elif trade['action'] == 'SELL':
                    temp_capital += temp_shares * trade['price']
                    temp_shares = 0
                equity_curve.append(temp_capital + (temp_shares * trade['price']))
            
            peak = equity_curve[0]
            max_dd = 0
            for value in equity_curve:
                if value > peak:
                    peak = value
                dd = ((value - peak) / peak) * 100
                if dd < max_dd:
                    max_dd = dd
            
            print(f"  ✅ Completed")
            print(f"     Trades: {len(sell_trades)} | Win Rate: {win_rate:.1f}%")
            print(f"     Avg Return: {avg_return:+.2f}% | Avg Holding: {avg_holding:.1f} days")
            print(f"     Total Return: {total_return:+.2f}% | Max DD: {max_dd:.2f}%")
            
            return {
                'ticker': ticker,
                'total_trades': len(sell_trades),
                'wins': wins,
                'losses': losses,
                'win_rate': win_rate,
                'avg_return': avg_return,
                'avg_holding_days': avg_holding,
                'total_return': total_return,
                'max_drawdown': max_dd,
                'trades': trades
            }
        else:
            print(f"  ⚠️  No trades executed")
            return None
            
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return None

# Run backtest
print(f"\n🔄 Running 2-Year Backtest on {len(STOCKS)} stocks...")
print("="*100)

end_date = datetime.now()
start_date = end_date - timedelta(days=730)  # 2 years

results = []
for stock in STOCKS:
    result = backtest_stock(stock, start_date, end_date)
    if result:
        results.append(result)

# Aggregate results
print("\n" + "="*100)
print("📊 BACKTEST RESULTS SUMMARY")
print("="*100)

if results:
    total_trades = sum(r['total_trades'] for r in results)
    total_wins = sum(r['wins'] for r in results)
    total_losses = sum(r['losses'] for r in results)
    overall_win_rate = (total_wins / total_trades) * 100 if total_trades > 0 else 0
    
    avg_return = np.mean([r['avg_return'] for r in results])
    avg_holding = np.mean([r['avg_holding_days'] for r in results])
    avg_total_return = np.mean([r['total_return'] for r in results])
    avg_max_dd = np.mean([r['max_drawdown'] for r in results])
    
    # Calculate Sharpe Ratio (simplified)
    returns = [r['avg_return'] for r in results]
    sharpe = (np.mean(returns) / np.std(returns)) * np.sqrt(252/avg_holding) if np.std(returns) > 0 else 0
    
    # Calculate CAGR
    years = 2
    cagr = (((1 + avg_total_return/100) ** (1/years)) - 1) * 100
    
    # Rating calculation
    rating = 0
    if overall_win_rate >= 90: rating += 2
    elif overall_win_rate >= 80: rating += 1.5
    elif overall_win_rate >= 70: rating += 1
    
    if cagr >= 20: rating += 2
    elif cagr >= 15: rating += 1.5
    elif cagr >= 10: rating += 1
    
    if sharpe >= 2.0: rating += 2
    elif sharpe >= 1.5: rating += 1.5
    elif sharpe >= 1.0: rating += 1
    
    if avg_max_dd >= -8: rating += 2
    elif avg_max_dd >= -10: rating += 1.5
    elif avg_max_dd >= -12: rating += 1
    
    rating = min(8, rating)
    
    print(f"\n🎯 Overall Performance:")
    print(f"  Total Trades: {total_trades}")
    print(f"  Wins: {total_wins} | Losses: {total_losses}")
    print(f"  Win Rate: {overall_win_rate:.2f}% {'✅' if overall_win_rate >= 90 else '⚠️' if overall_win_rate >= 80 else '❌'}")
    print(f"  Average Return per Trade: {avg_return:+.2f}%")
    print(f"  Average Holding Period: {avg_holding:.1f} days")
    print(f"  Average Total Return: {avg_total_return:+.2f}%")
    print(f"  CAGR: {cagr:+.2f}% {'✅' if cagr >= 20 else '⚠️' if cagr >= 15 else '❌'}")
    print(f"  Average Max Drawdown: {avg_max_dd:.2f}% {'✅' if avg_max_dd >= -8 else '⚠️' if avg_max_dd >= -10 else '❌'}")
    print(f"  Sharpe Ratio: {sharpe:.2f} {'✅' if sharpe >= 2.0 else '⚠️' if sharpe >= 1.5 else '❌'}")
    print(f"  Rating: {rating:.1f}/8 {'⭐' * int(rating)}")
    
    # Save results
    os.makedirs("backtest_results", exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    report = {
        'timestamp': timestamp,
        'period': f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
        'summary': {
            'total_trades': total_trades,
            'wins': total_wins,
            'losses': total_losses,
            'win_rate': overall_win_rate,
            'avg_return': avg_return,
            'avg_holding_days': avg_holding,
            'avg_total_return': avg_total_return,
            'cagr': cagr,
            'avg_max_drawdown': avg_max_dd,
            'sharpe_ratio': sharpe,
            'rating': rating
        },
        'individual_results': results
    }
    
    filepath = f"backtest_results/backtest_2y_{timestamp}.json"
    with open(filepath, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    print(f"\n💾 Results saved to: {filepath}")
    
    # Recommendations
    print(f"\n💡 Recommendations:")
    if overall_win_rate >= 90:
        print(f"  ✅ Win rate target ACHIEVED! Ready for live trading.")
    elif overall_win_rate >= 85:
        print(f"  ⚠️  Win rate close to target. Fine-tune parameters.")
    else:
        print(f"  ❌ Win rate below target. Retrain models with more data.")
    
    if rating >= 8:
        print(f"  ✅ 8/8 rating ACHIEVED! System is EXCELLENT.")
    elif rating >= 7:
        print(f"  ⚠️  7/8 rating. Very good, minor improvements needed.")
    else:
        print(f"  ❌ Rating below target. Continue optimization.")

else:
    print("❌ No backtest results generated")

print("="*100)
