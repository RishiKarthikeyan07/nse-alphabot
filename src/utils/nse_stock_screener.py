"""
NSE Stock Screener - High Volume & Momentum Filter
Filters ALL NSE stocks based on professional trading criteria
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings("ignore")

# === SCREENING CRITERIA ===
MIN_VOLUME = 1000000  # 10 lakh shares/day
MIN_MARKET_CAP = 5000  # ₹5000 Crore
MIN_PRICE = 100  # ₹100
MIN_BETA = 1.2  # High volatility
RSI_RANGE = (55, 70)  # Bullish momentum
MIN_VOLUME_SURGE = 1.5  # 1.5x average volume

# Import dynamic NSE stock fetcher
from fetch_all_nse_stocks import get_all_nse_stocks

# NSE Stock Universe - Will be populated dynamically
NSE_STOCKS = []

def load_nse_stocks():
    """Load all NSE stocks dynamically"""
    global NSE_STOCKS
    if not NSE_STOCKS:
        NSE_STOCKS = get_all_nse_stocks()
    return NSE_STOCKS

def calculate_technical_indicators(df):
    """Calculate technical indicators for screening"""
    try:
        # Moving Averages
        df['ma_50'] = df['Close'].rolling(50).mean()
        df['ma_200'] = df['Close'].rolling(200).mean()
        
        # RSI
        delta = df['Close'].diff()
        gain = delta.clip(lower=0).rolling(14).mean()
        loss = (-delta.clip(upper=0)).rolling(14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # MACD
        exp1 = df['Close'].ewm(span=12).mean()
        exp2 = df['Close'].ewm(span=26).mean()
        df['macd'] = exp1 - exp2
        df['macd_signal'] = df['macd'].ewm(span=9).mean()
        
        # Volume
        df['volume_ma_20'] = df['Volume'].rolling(20).mean()
        df['volume_ratio'] = df['Volume'] / df['volume_ma_20']
        
        # Beta (vs Nifty 50)
        # Simplified: Use 60-day volatility ratio
        df['returns'] = df['Close'].pct_change()
        df['volatility'] = df['returns'].rolling(60).std()
        
        return df
    except:
        return None

def screen_stock(ticker):
    """Screen individual stock against criteria"""
    try:
        # Download 1 year data
        df = yf.download(ticker, period="1y", interval="1d", 
                        auto_adjust=True, progress=False)
        
        if df.empty or len(df) < 200:
            return None
        
        # Get stock info
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # Calculate indicators
        df = calculate_technical_indicators(df)
        if df is None:
            return None
        
        df = df.dropna()
        if len(df) < 50:
            return None
        
        # Get latest values
        current_price = float(df['Close'].iloc[-1])
        avg_volume = float(df['Volume'].rolling(20).mean().iloc[-1])
        current_volume = float(df['Volume'].iloc[-1])
        rsi = float(df['rsi'].iloc[-1])
        ma_50 = float(df['ma_50'].iloc[-1])
        ma_200 = float(df['ma_200'].iloc[-1])
        macd = float(df['macd'].iloc[-1])
        macd_signal = float(df['macd_signal'].iloc[-1])
        volume_ratio = float(df['volume_ratio'].iloc[-1])
        volatility = float(df['volatility'].iloc[-1])
        
        # Market cap (in Crores)
        market_cap = info.get('marketCap', 0) / 10000000  # Convert to Crores
        
        # Beta approximation (volatility-based)
        nifty_volatility = 0.015  # Approximate Nifty daily volatility
        beta = volatility / nifty_volatility if nifty_volatility > 0 else 1.0
        
        # === APPLY FILTERS ===
        
        # 1. Volume Filter
        if avg_volume < MIN_VOLUME:
            return None
        
        # 2. Market Cap Filter
        if market_cap < MIN_MARKET_CAP:
            return None
        
        # 3. Price Filter
        if current_price < MIN_PRICE:
            return None
        
        # 4. Beta Filter (high volatility)
        if beta < MIN_BETA:
            return None
        
        # 5. Technical Filters
        # Price above MAs
        if current_price < ma_50 or current_price < ma_200:
            return None
        
        # RSI in bullish range
        if not (RSI_RANGE[0] <= rsi <= RSI_RANGE[1]):
            return None
        
        # MACD bullish
        if macd <= macd_signal:
            return None
        
        # Volume surge
        if volume_ratio < MIN_VOLUME_SURGE:
            return None
        
        # === CALCULATE MOMENTUM SCORE ===
        # Higher score = better momentum
        
        # Price momentum (vs 50-day MA)
        price_momentum = ((current_price - ma_50) / ma_50) * 100
        
        # Volume momentum
        volume_momentum = (volume_ratio - 1.0) * 100
        
        # RSI strength (normalized)
        rsi_strength = (rsi - 50) / 50 * 100
        
        # MACD strength
        macd_strength = ((macd - macd_signal) / abs(macd_signal)) * 100 if macd_signal != 0 else 0
        
        # Combined momentum score
        momentum_score = (
            price_momentum * 0.35 +
            volume_momentum * 0.25 +
            rsi_strength * 0.20 +
            macd_strength * 0.20
        )
        
        return {
            'ticker': ticker,
            'price': current_price,
            'market_cap': market_cap,
            'avg_volume': avg_volume,
            'current_volume': current_volume,
            'volume_ratio': volume_ratio,
            'beta': beta,
            'rsi': rsi,
            'macd': macd,
            'macd_signal': macd_signal,
            'ma_50': ma_50,
            'ma_200': ma_200,
            'momentum_score': momentum_score,
            'price_momentum': price_momentum,
            'volume_momentum': volume_momentum
        }
        
    except Exception as e:
        return None

def screen_nse_stocks(max_stocks=100, verbose=True):
    """
    Screen ALL NSE stocks and return top candidates
    
    Returns: List of qualified stocks sorted by momentum score
    """
    # Load all NSE stocks dynamically
    all_stocks = load_nse_stocks()
    
    if verbose:
        print("="*100)
        print(f"🔍 NSE STOCK SCREENER - High Volume & Momentum Filter")
        print("="*100)
        print(f"Universe: {len(all_stocks)} NSE stocks")
        print(f"Filters:")
        print(f"  • Volume: >{MIN_VOLUME:,} shares/day")
        print(f"  • Market Cap: >₹{MIN_MARKET_CAP:,} Cr")
        print(f"  • Price: >₹{MIN_PRICE}")
        print(f"  • Beta: >{MIN_BETA}")
        print(f"  • RSI: {RSI_RANGE[0]}-{RSI_RANGE[1]} (bullish)")
        print(f"  • Price: Above 50-day & 200-day MA")
        print(f"  • MACD: Bullish crossover")
        print(f"  • Volume: {MIN_VOLUME_SURGE}x surge")
        print("="*100)
        print()
    
    qualified_stocks = []
    
    for i, ticker in enumerate(all_stocks, 1):
        if verbose:
            print(f"[{i:4}/{len(all_stocks)}] {ticker:20}", end=" ")
        
        result = screen_stock(ticker)
        
        if result:
            qualified_stocks.append(result)
            if verbose:
                print(f"✅ PASS | Score: {result['momentum_score']:>6.1f} | "
                      f"Vol: {result['volume_ratio']:.1f}x | RSI: {result['rsi']:.0f}")
        else:
            if verbose:
                print("❌ FAIL")
    
    # Sort by momentum score
    qualified_stocks = sorted(qualified_stocks, 
                            key=lambda x: x['momentum_score'], 
                            reverse=True)
    
    # Limit to max_stocks
    qualified_stocks = qualified_stocks[:max_stocks]
    
    if verbose:
        print()
        print("="*100)
        print(f"✅ SCREENING COMPLETE")
        print("="*100)
        print(f"Qualified Stocks: {len(qualified_stocks)}/{len(all_stocks)}")
        print(f"Pass Rate: {len(qualified_stocks)/len(all_stocks)*100:.1f}%")
        print("="*100)
        
        if qualified_stocks:
            print()
            print("🎯 TOP 20 HIGH MOMENTUM STOCKS:")
            print("-"*100)
            print(f"{'Rank':<5} {'Ticker':<15} {'Price':>10} {'MCap':>10} {'Volume':>12} {'Beta':>6} {'RSI':>5} {'Score':>7}")
            print("-"*100)
            
            for i, stock in enumerate(qualified_stocks[:20], 1):
                print(f"{i:<5} {stock['ticker']:<15} ₹{stock['price']:>9.2f} "
                      f"₹{stock['market_cap']:>8.0f}Cr {stock['avg_volume']:>11,.0f} "
                      f"{stock['beta']:>5.2f} {stock['rsi']:>5.0f} {stock['momentum_score']:>6.1f}")
            
            print("-"*100)
    
    return qualified_stocks

def get_screened_tickers(max_stocks=100):
    """
    Convenience function to get just the ticker list
    """
    stocks = screen_nse_stocks(max_stocks=max_stocks, verbose=False)
    return [s['ticker'] for s in stocks]

if __name__ == "__main__":
    # Test the screener
    print(f"\n🧪 Testing NSE Stock Screener")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    qualified = screen_nse_stocks(max_stocks=50)
    
    print(f"\n✅ Screener test complete!")
    print(f"Found {len(qualified)} qualified stocks for swing/positional trading")
