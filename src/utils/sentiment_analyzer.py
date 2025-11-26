"""
Hybrid Sentiment Analyzer
Combines Finnhub news sentiment with technical momentum analysis
"""
import requests
import time
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

FINNHUB_API_KEY = os.getenv('FINNHUB_API_KEY', 'd4bifi9r01qoua2vuuagd4bifi9r01qoua2vuub0')
FINNHUB_BASE_URL = "https://finnhub.io/api/v1"

# Cache to avoid hitting API limits
_sentiment_cache = {}
_cache_expiry = {}
CACHE_DURATION = 3600  # 1 hour


def get_finnhub_news_sentiment(ticker):
    """
    Get news sentiment from Finnhub API
    Returns: sentiment score 0.0 to 1.0
    """
    try:
        # Remove .NS suffix for Finnhub (use base ticker)
        base_ticker = ticker.replace('.NS', '')
        
        # Check cache
        cache_key = f"{base_ticker}_{datetime.now().strftime('%Y%m%d%H')}"
        if cache_key in _sentiment_cache:
            if time.time() < _cache_expiry.get(cache_key, 0):
                return _sentiment_cache[cache_key]
        
        # Get news from last 7 days
        to_date = datetime.now().strftime('%Y-%m-%d')
        from_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        
        url = f"{FINNHUB_BASE_URL}/company-news"
        params = {
            'symbol': base_ticker,
            'from': from_date,
            'to': to_date,
            'token': FINNHUB_API_KEY
        }
        
        response = requests.get(url, params=params, timeout=5)
        
        if response.status_code == 200:
            news_items = response.json()
            
            if not news_items or len(news_items) == 0:
                # No news, return neutral
                return 0.5
            
            # Analyze sentiment from headlines
            positive_count = 0
            negative_count = 0
            neutral_count = 0
            
            # Keywords for sentiment analysis
            positive_keywords = [
                'surge', 'gain', 'profit', 'growth', 'up', 'rise', 'high',
                'beat', 'strong', 'bullish', 'positive', 'upgrade', 'buy',
                'outperform', 'record', 'success', 'boost', 'rally'
            ]
            
            negative_keywords = [
                'fall', 'drop', 'loss', 'decline', 'down', 'low', 'weak',
                'miss', 'bearish', 'negative', 'downgrade', 'sell', 'cut',
                'underperform', 'concern', 'risk', 'warning', 'crash'
            ]
            
            for item in news_items[:20]:  # Analyze last 20 news items
                headline = item.get('headline', '').lower()
                summary = item.get('summary', '').lower()
                text = headline + ' ' + summary
                
                pos_score = sum(1 for word in positive_keywords if word in text)
                neg_score = sum(1 for word in negative_keywords if word in text)
                
                if pos_score > neg_score:
                    positive_count += 1
                elif neg_score > pos_score:
                    negative_count += 1
                else:
                    neutral_count += 1
            
            # Calculate sentiment score
            total = positive_count + negative_count + neutral_count
            if total == 0:
                sentiment = 0.5
            else:
                # Weight: positive=1.0, neutral=0.5, negative=0.0
                sentiment = (positive_count * 1.0 + neutral_count * 0.5) / total
            
            # Cache the result
            _sentiment_cache[cache_key] = sentiment
            _cache_expiry[cache_key] = time.time() + CACHE_DURATION
            
            return round(sentiment, 2)
        
        else:
            # API error, return neutral
            return 0.5
            
    except Exception as e:
        # On error, return neutral sentiment
        return 0.5


def get_technical_sentiment(df):
    """
    Get sentiment based on technical indicators
    Returns: sentiment score 0.0 to 1.0
    """
    try:
        current_price = float(df['Close'].iloc[-1])
        
        # 5-day momentum
        if len(df) >= 6:
            price_5d = float(df['Close'].iloc[-6])
            momentum_5d = (current_price - price_5d) / price_5d
        else:
            momentum_5d = 0
        
        # 10-day momentum  
        if len(df) >= 11:
            price_10d = float(df['Close'].iloc[-11])
            momentum_10d = (current_price - price_10d) / price_10d
        else:
            momentum_10d = 0
        
        # Volume trend
        volume_ratio = float(df['volume_ratio'].iloc[-1])
        volume_score = min(1.0, volume_ratio / 1.5)
        
        # RSI score
        rsi = float(df['rsi'].iloc[-1])
        if 30 <= rsi <= 70:
            rsi_score = 0.7
        elif rsi < 30:
            rsi_score = 0.9  # Oversold = bullish
        else:
            rsi_score = 0.3  # Overbought = bearish
        
        # MACD trend
        macd = float(df['macd'].iloc[-1])
        macd_signal = float(df['macd_signal'].iloc[-1])
        macd_score = 0.7 if macd > macd_signal else 0.3
        
        # Weighted combination
        sentiment_score = (
            momentum_5d * 0.25 +
            momentum_10d * 0.20 +
            volume_score * 0.20 +
            rsi_score * 0.20 +
            macd_score * 0.15
        )
        
        # Normalize to 0-1
        sentiment_score = max(0, min(1, sentiment_score + 0.5))
        return round(sentiment_score, 2)
        
    except Exception as e:
        return 0.5


def get_hybrid_sentiment(ticker, df=None):
    """
    Hybrid sentiment combining Finnhub news + technical indicators
    
    Args:
        ticker: Stock ticker (e.g., 'RELIANCE.NS')
        df: Optional DataFrame with OHLCV data. If None, will fetch internally.
    
    Weights:
    - 50% News sentiment (Finnhub)
    - 50% Technical sentiment (momentum, RSI, MACD, volume)
    
    Returns: sentiment score 0.0 to 1.0
    """
    try:
        # Get news sentiment from Finnhub
        news_sentiment = get_finnhub_news_sentiment(ticker)
        
        # If df not provided, fetch it
        if df is None:
            import yfinance as yf
            df = yf.download(ticker, period='1mo', interval='1d',
                           auto_adjust=True, progress=False)
            
            if df.empty:
                # No data, return news sentiment only
                return news_sentiment
            
            # Handle MultiIndex columns
            if hasattr(df.columns, 'levels'):
                df.columns = df.columns.get_level_values(0)
            
            # Calculate required indicators
            import pandas as pd
            
            # RSI
            delta = df['Close'].diff()
            gain = delta.clip(lower=0).rolling(14).mean()
            loss = (-delta.clip(upper=0)).rolling(14).mean()
            rs = gain / loss
            df['rsi'] = 100 - (100 / (1 + rs))
            
            # MACD
            ema_12 = df['Close'].ewm(span=12).mean()
            ema_26 = df['Close'].ewm(span=26).mean()
            df['macd'] = ema_12 - ema_26
            df['macd_signal'] = df['macd'].ewm(span=9).mean()
            
            # Volume ratio
            df['volume_ma'] = df['Volume'].rolling(20).mean()
            df['volume_ratio'] = df['Volume'] / df['volume_ma']
            
            df = df.dropna()
            
            if len(df) < 5:
                # Not enough data, return news sentiment only
                return news_sentiment
        
        # Get technical sentiment
        technical_sentiment = get_technical_sentiment(df)
        
        # Combine with 50-50 weight
        hybrid_sentiment = (news_sentiment * 0.5) + (technical_sentiment * 0.5)
        
        return round(hybrid_sentiment, 2)
        
    except Exception as e:
        # Fallback to news sentiment only
        try:
            return get_finnhub_news_sentiment(ticker)
        except:
            return 0.5


# For backward compatibility
def get_sentiment_score(ticker, df):
    """
    Main sentiment function - uses hybrid approach
    """
    return get_hybrid_sentiment(ticker, df)


if __name__ == "__main__":
    # Test the sentiment analyzer
    import pandas as pd
    import numpy as np
    
    print("🧪 Testing Hybrid Sentiment Analyzer\n")
    
    # Test 1: Finnhub API
    print("1. Testing Finnhub News Sentiment...")
    test_ticker = "RELIANCE.NS"
    news_sent = get_finnhub_news_sentiment(test_ticker)
    print(f"   {test_ticker} News Sentiment: {news_sent}")
    
    # Test 2: Technical Sentiment
    print("\n2. Testing Technical Sentiment...")
    data = {
        'Close': [100, 102, 105, 103, 107, 110, 108, 112, 115, 118, 120],
        'volume_ratio': [1.2] * 11,
        'rsi': [45] * 11,
        'macd': [0.5] * 11,
        'macd_signal': [0.3] * 11
    }
    df = pd.DataFrame(data)
    tech_sent = get_technical_sentiment(df)
    print(f"   Technical Sentiment: {tech_sent}")
    
    # Test 3: Hybrid
    print("\n3. Testing Hybrid Sentiment...")
    hybrid_sent = get_hybrid_sentiment(test_ticker, df)
    print(f"   Hybrid Sentiment: {hybrid_sent}")
    print(f"   (50% News: {news_sent} + 50% Technical: {tech_sent})")
    
    print("\n✅ All tests complete!")
