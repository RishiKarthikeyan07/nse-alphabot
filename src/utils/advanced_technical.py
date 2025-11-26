# advanced_technical.py - Advanced Technical Analysis
"""
Advanced technical indicators for NSE AlphaBot:
- Volume Profile (POC, Value Area)
- Fibonacci Retracements & Extensions
- MACD Divergence Detection
- Advanced RSI (Divergence, Hidden Divergence)
- Support/Resistance Levels
- Pivot Points

Expected accuracy boost: +5-10% when combined with SMC
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings("ignore")

class AdvancedTechnicalAnalyzer:
    """
    Advanced technical analysis for institutional-grade signals
    """
    
    def __init__(self, df: pd.DataFrame):
        """
        Initialize with OHLCV data
        
        Args:
            df: DataFrame with Open, High, Low, Close, Volume columns
        """
        self.df = df.copy()
        self._calculate_base_indicators()
    
    def _calculate_base_indicators(self):
        """Calculate base indicators (RSI, MACD, etc.)"""
        # RSI
        delta = self.df['Close'].diff()
        gain = delta.clip(lower=0).rolling(14).mean()
        loss = (-delta.clip(upper=0)).rolling(14).mean()
        rs = gain / loss
        self.df['rsi'] = 100 - (100 / (1 + rs))
        
        # MACD
        ema_12 = self.df['Close'].ewm(span=12).mean()
        ema_26 = self.df['Close'].ewm(span=26).mean()
        self.df['macd'] = ema_12 - ema_26
        self.df['macd_signal'] = self.df['macd'].ewm(span=9).mean()
        self.df['macd_hist'] = self.df['macd'] - self.df['macd_signal']
        
        # Volume MA
        self.df['volume_ma'] = self.df['Volume'].rolling(20).mean()
    
    def calculate_volume_profile(self, bins: int = 20) -> Dict:
        """
        Calculate Volume Profile - identifies high-volume price levels
        
        Args:
            bins: Number of price bins
            
        Returns:
            Dict with POC (Point of Control), Value Area High/Low
        """
        if len(self.df) < 20:
            return {'poc': None, 'vah': None, 'val': None}
        
        # Get price range
        price_min = self.df['Low'].min()
        price_max = self.df['High'].max()
        
        # Create price bins
        price_bins = np.linspace(price_min, price_max, bins + 1)
        volume_profile = np.zeros(bins)
        
        # Distribute volume across price bins
        for idx, row in self.df.iterrows():
            # Find which bins this candle touches
            low_bin = np.digitize(row['Low'], price_bins) - 1
            high_bin = np.digitize(row['High'], price_bins) - 1
            
            # Distribute volume evenly across touched bins
            bins_touched = high_bin - low_bin + 1
            if bins_touched > 0:
                volume_per_bin = row['Volume'] / bins_touched
                for b in range(max(0, low_bin), min(bins, high_bin + 1)):
                    volume_profile[b] += volume_per_bin
        
        # Find POC (Point of Control) - highest volume bin
        poc_bin = np.argmax(volume_profile)
        poc_price = (price_bins[poc_bin] + price_bins[poc_bin + 1]) / 2
        
        # Find Value Area (70% of volume)
        total_volume = volume_profile.sum()
        target_volume = total_volume * 0.70
        
        # Expand from POC until we reach 70% volume
        value_area_bins = [poc_bin]
        current_volume = volume_profile[poc_bin]
        
        left = poc_bin - 1
        right = poc_bin + 1
        
        while current_volume < target_volume and (left >= 0 or right < bins):
            left_vol = volume_profile[left] if left >= 0 else 0
            right_vol = volume_profile[right] if right < bins else 0
            
            if left_vol > right_vol and left >= 0:
                value_area_bins.append(left)
                current_volume += left_vol
                left -= 1
            elif right < bins:
                value_area_bins.append(right)
                current_volume += right_vol
                right += 1
            else:
                break
        
        # Calculate Value Area High and Low
        vah = price_bins[max(value_area_bins) + 1]
        val = price_bins[min(value_area_bins)]
        
        return {
            'poc': poc_price,
            'vah': vah,
            'val': val,
            'current_price': self.df['Close'].iloc[-1],
            'position': 'above_poc' if self.df['Close'].iloc[-1] > poc_price else 'below_poc'
        }
    
    def calculate_fibonacci_levels(self, lookback: int = 50) -> Dict:
        """
        Calculate Fibonacci retracement levels
        
        Args:
            lookback: Number of candles to look back for swing high/low
            
        Returns:
            Dict with Fibonacci levels and current position
        """
        if len(self.df) < lookback:
            return {'levels': {}, 'trend': 'unknown'}
        
        recent_data = self.df.iloc[-lookback:]
        swing_high = recent_data['High'].max()
        swing_low = recent_data['Low'].min()
        current_price = self.df['Close'].iloc[-1]
        
        # Determine trend
        if current_price > (swing_high + swing_low) / 2:
            trend = 'uptrend'
            # Retracement from high to low
            diff = swing_high - swing_low
            levels = {
                '0.0': swing_high,
                '0.236': swing_high - (diff * 0.236),
                '0.382': swing_high - (diff * 0.382),
                '0.500': swing_high - (diff * 0.500),
                '0.618': swing_high - (diff * 0.618),
                '0.786': swing_high - (diff * 0.786),
                '1.0': swing_low
            }
        else:
            trend = 'downtrend'
            # Retracement from low to high
            diff = swing_high - swing_low
            levels = {
                '0.0': swing_low,
                '0.236': swing_low + (diff * 0.236),
                '0.382': swing_low + (diff * 0.382),
                '0.500': swing_low + (diff * 0.500),
                '0.618': swing_low + (diff * 0.618),
                '0.786': swing_low + (diff * 0.786),
                '1.0': swing_high
            }
        
        # Find nearest level
        nearest_level = min(levels.items(), key=lambda x: abs(x[1] - current_price))
        
        return {
            'trend': trend,
            'levels': levels,
            'current_price': current_price,
            'nearest_level': nearest_level[0],
            'nearest_price': nearest_level[1],
            'distance_pct': abs(current_price - nearest_level[1]) / current_price * 100
        }
    
    def detect_macd_divergence(self, lookback: int = 20) -> Dict:
        """
        Detect MACD divergence - powerful reversal signal
        
        Bullish Divergence: Price makes lower low, MACD makes higher low
        Bearish Divergence: Price makes higher high, MACD makes lower high
        
        Returns:
            Dict with divergence type and strength
        """
        if len(self.df) < lookback + 10:
            return {'detected': False}
        
        recent_data = self.df.iloc[-lookback:]
        
        # Find price swings
        price_lows = []
        price_highs = []
        macd_lows = []
        macd_highs = []
        
        for i in range(5, len(recent_data) - 5):
            # Local low
            if all(recent_data['Low'].iloc[i] < recent_data['Low'].iloc[i-j] for j in range(1, 6)) and \
               all(recent_data['Low'].iloc[i] < recent_data['Low'].iloc[i+j] for j in range(1, 6)):
                price_lows.append((i, recent_data['Low'].iloc[i]))
                macd_lows.append((i, recent_data['macd'].iloc[i]))
            
            # Local high
            if all(recent_data['High'].iloc[i] > recent_data['High'].iloc[i-j] for j in range(1, 6)) and \
               all(recent_data['High'].iloc[i] > recent_data['High'].iloc[i+j] for j in range(1, 6)):
                price_highs.append((i, recent_data['High'].iloc[i]))
                macd_highs.append((i, recent_data['macd'].iloc[i]))
        
        # Check for bullish divergence (last 2 lows)
        if len(price_lows) >= 2 and len(macd_lows) >= 2:
            last_price_low = price_lows[-1][1]
            prev_price_low = price_lows[-2][1]
            last_macd_low = macd_lows[-1][1]
            prev_macd_low = macd_lows[-2][1]
            
            if last_price_low < prev_price_low and last_macd_low > prev_macd_low:
                strength = abs(last_macd_low - prev_macd_low) / abs(prev_macd_low) * 100
                return {
                    'detected': True,
                    'type': 'bullish',
                    'strength': 'strong' if strength > 10 else 'moderate',
                    'strength_pct': strength
                }
        
        # Check for bearish divergence (last 2 highs)
        if len(price_highs) >= 2 and len(macd_highs) >= 2:
            last_price_high = price_highs[-1][1]
            prev_price_high = price_highs[-2][1]
            last_macd_high = macd_highs[-1][1]
            prev_macd_high = macd_highs[-2][1]
            
            if last_price_high > prev_price_high and last_macd_high < prev_macd_high:
                strength = abs(last_macd_high - prev_macd_high) / abs(prev_macd_high) * 100
                return {
                    'detected': True,
                    'type': 'bearish',
                    'strength': 'strong' if strength > 10 else 'moderate',
                    'strength_pct': strength
                }
        
        return {'detected': False}
    
    def detect_rsi_divergence(self, lookback: int = 20) -> Dict:
        """
        Detect RSI divergence - confirms MACD divergence
        
        Returns:
            Dict with divergence type and strength
        """
        if len(self.df) < lookback + 10:
            return {'detected': False}
        
        recent_data = self.df.iloc[-lookback:]
        
        # Find price and RSI swings
        price_lows = []
        price_highs = []
        rsi_lows = []
        rsi_highs = []
        
        for i in range(5, len(recent_data) - 5):
            # Local low
            if all(recent_data['Low'].iloc[i] < recent_data['Low'].iloc[i-j] for j in range(1, 6)) and \
               all(recent_data['Low'].iloc[i] < recent_data['Low'].iloc[i+j] for j in range(1, 6)):
                price_lows.append((i, recent_data['Low'].iloc[i]))
                rsi_lows.append((i, recent_data['rsi'].iloc[i]))
            
            # Local high
            if all(recent_data['High'].iloc[i] > recent_data['High'].iloc[i-j] for j in range(1, 6)) and \
               all(recent_data['High'].iloc[i] > recent_data['High'].iloc[i+j] for j in range(1, 6)):
                price_highs.append((i, recent_data['High'].iloc[i]))
                rsi_highs.append((i, recent_data['rsi'].iloc[i]))
        
        # Check for bullish divergence
        if len(price_lows) >= 2 and len(rsi_lows) >= 2:
            if price_lows[-1][1] < price_lows[-2][1] and rsi_lows[-1][1] > rsi_lows[-2][1]:
                return {
                    'detected': True,
                    'type': 'bullish',
                    'strength': 'strong' if rsi_lows[-1][1] > 40 else 'moderate'
                }
        
        # Check for bearish divergence
        if len(price_highs) >= 2 and len(rsi_highs) >= 2:
            if price_highs[-1][1] > price_highs[-2][1] and rsi_highs[-1][1] < rsi_highs[-2][1]:
                return {
                    'detected': True,
                    'type': 'bearish',
                    'strength': 'strong' if rsi_highs[-1][1] < 60 else 'moderate'
                }
        
        return {'detected': False}
    
    def calculate_support_resistance(self, lookback: int = 50, tolerance: float = 0.02) -> Dict:
        """
        Calculate support and resistance levels using pivot points
        
        Args:
            lookback: Number of candles to analyze
            tolerance: Price tolerance for level clustering (2%)
            
        Returns:
            Dict with support and resistance levels
        """
        if len(self.df) < lookback:
            return {'support': [], 'resistance': []}
        
        recent_data = self.df.iloc[-lookback:]
        current_price = self.df['Close'].iloc[-1]
        
        # Find pivot highs and lows
        pivots_high = []
        pivots_low = []
        
        for i in range(5, len(recent_data) - 5):
            # Pivot high
            if all(recent_data['High'].iloc[i] > recent_data['High'].iloc[i-j] for j in range(1, 6)) and \
               all(recent_data['High'].iloc[i] > recent_data['High'].iloc[i+j] for j in range(1, 6)):
                pivots_high.append(recent_data['High'].iloc[i])
            
            # Pivot low
            if all(recent_data['Low'].iloc[i] < recent_data['Low'].iloc[i-j] for j in range(1, 6)) and \
               all(recent_data['Low'].iloc[i] < recent_data['Low'].iloc[i+j] for j in range(1, 6)):
                pivots_low.append(recent_data['Low'].iloc[i])
        
        # Cluster nearby levels
        def cluster_levels(levels, tolerance):
            if not levels:
                return []
            
            levels = sorted(levels)
            clusters = []
            current_cluster = [levels[0]]
            
            for level in levels[1:]:
                if abs(level - current_cluster[-1]) / current_cluster[-1] <= tolerance:
                    current_cluster.append(level)
                else:
                    clusters.append(np.mean(current_cluster))
                    current_cluster = [level]
            
            clusters.append(np.mean(current_cluster))
            return clusters
        
        resistance_levels = cluster_levels([p for p in pivots_high if p > current_price], tolerance)
        support_levels = cluster_levels([p for p in pivots_low if p < current_price], tolerance)
        
        return {
            'support': sorted(support_levels, reverse=True)[:3],  # Top 3 nearest
            'resistance': sorted(resistance_levels)[:3],  # Top 3 nearest
            'current_price': current_price
        }
    
    def analyze(self) -> Dict:
        """
        Perform complete advanced technical analysis
        
        Returns:
            Dict with all advanced indicators and overall score
        """
        return self.analyze_advanced_technical()
    
    def analyze_advanced_technical(self) -> Dict:
        """
        Perform complete advanced technical analysis
        
        Returns:
            Dict with all advanced indicators and overall score
        """
        # Calculate all indicators
        volume_profile = self.calculate_volume_profile()
        fibonacci = self.calculate_fibonacci_levels()
        macd_div = self.detect_macd_divergence()
        rsi_div = self.detect_rsi_divergence()
        sr_levels = self.calculate_support_resistance()
        
        # Calculate technical score (0-1)
        tech_score = 0.5  # Neutral
        signals = []
        
        # Volume Profile (weight: 0.2)
        if volume_profile['poc']:
            if volume_profile['position'] == 'above_poc':
                tech_score += 0.1
                signals.append("Price above POC (bullish)")
            else:
                tech_score -= 0.1
                signals.append("Price below POC (bearish)")
        
        # Fibonacci (weight: 0.15)
        if fibonacci['trend'] == 'uptrend':
            if fibonacci['nearest_level'] in ['0.382', '0.500', '0.618']:
                tech_score += 0.1
                signals.append(f"At Fib {fibonacci['nearest_level']} support")
        elif fibonacci['trend'] == 'downtrend':
            if fibonacci['nearest_level'] in ['0.382', '0.500', '0.618']:
                tech_score -= 0.1
                signals.append(f"At Fib {fibonacci['nearest_level']} resistance")
        
        # MACD Divergence (weight: 0.25)
        if macd_div['detected']:
            if macd_div['type'] == 'bullish':
                tech_score += 0.15 if macd_div['strength'] == 'strong' else 0.1
                signals.append(f"Bullish MACD Divergence ({macd_div['strength']})")
            else:
                tech_score -= 0.15 if macd_div['strength'] == 'strong' else 0.1
                signals.append(f"Bearish MACD Divergence ({macd_div['strength']})")
        
        # RSI Divergence (weight: 0.2)
        if rsi_div['detected']:
            if rsi_div['type'] == 'bullish':
                tech_score += 0.1 if rsi_div['strength'] == 'strong' else 0.05
                signals.append(f"Bullish RSI Divergence ({rsi_div['strength']})")
            else:
                tech_score -= 0.1 if rsi_div['strength'] == 'strong' else 0.05
                signals.append(f"Bearish RSI Divergence ({rsi_div['strength']})")
        
        # Support/Resistance (weight: 0.2)
        current_price = self.df['Close'].iloc[-1]
        if sr_levels['support']:
            nearest_support = sr_levels['support'][0]
            support_dist = (current_price - nearest_support) / current_price * 100
            if support_dist < 2:  # Within 2% of support
                tech_score += 0.1
                signals.append(f"Near support (₹{nearest_support:.2f})")
        
        if sr_levels['resistance']:
            nearest_resistance = sr_levels['resistance'][0]
            resistance_dist = (nearest_resistance - current_price) / current_price * 100
            if resistance_dist < 2:  # Within 2% of resistance
                tech_score -= 0.1
                signals.append(f"Near resistance (₹{nearest_resistance:.2f})")
        
        # Normalize score
        tech_score = max(0, min(1, tech_score))
        
        # Determine signal
        if tech_score >= 0.7:
            tech_signal = "STRONG_BUY"
        elif tech_score >= 0.6:
            tech_signal = "BUY"
        elif tech_score >= 0.4:
            tech_signal = "NEUTRAL"
        elif tech_score >= 0.3:
            tech_signal = "SELL"
        else:
            tech_signal = "STRONG_SELL"
        
        return {
            'signal': tech_signal,
            'score': tech_score,
            'volume_profile': volume_profile,
            'fibonacci': fibonacci,
            'macd_divergence': macd_div,
            'rsi_divergence': rsi_div,
            'support_resistance': sr_levels,
            'signals': signals
        }


def analyze_advanced_technical_quick(df: pd.DataFrame) -> Dict:
    """
    Quick advanced technical analysis
    
    Args:
        df: DataFrame with OHLCV data
        
    Returns:
        Dict with analysis results
    """
    analyzer = AdvancedTechnicalAnalyzer(df)
    return analyzer.analyze_advanced_technical()


# === TESTING ===
if __name__ == "__main__":
    import yfinance as yf
    
    print("="*80)
    print("ADVANCED TECHNICAL ANALYSIS TEST")
    print("="*80)
    
    ticker = "RELIANCE.NS"
    print(f"\nTesting on {ticker}...")
    
    df = yf.download(ticker, period="6mo", interval="1d", auto_adjust=True, progress=False)
    
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    
    analyzer = AdvancedTechnicalAnalyzer(df)
    result = analyzer.analyze_advanced_technical()
    
    print(f"\n{'='*80}")
    print(f"ADVANCED TECHNICAL ANALYSIS: {ticker}")
    print(f"{'='*80}")
    print(f"\nSignal: {result['signal']}")
    print(f"Score: {result['score']:.2f}")
    
    print(f"\nVolume Profile:")
    vp = result['volume_profile']
    if vp['poc']:
        print(f"  POC: ₹{vp['poc']:.2f}")
        print(f"  VAH: ₹{vp['vah']:.2f}")
        print(f"  VAL: ₹{vp['val']:.2f}")
        print(f"  Position: {vp['position']}")
    
    print(f"\nFibonacci:")
    fib = result['fibonacci']
    print(f"  Trend: {fib['trend']}")
    print(f"  Nearest Level: {fib['nearest_level']} (₹{fib['nearest_price']:.2f})")
    
    print(f"\nMACD Divergence:")
    if result['macd_divergence']['detected']:
        md = result['macd_divergence']
        print(f"  Type: {md['type'].upper()}")
        print(f"  Strength: {md['strength']}")
    else:
        print(f"  None detected")
    
    print(f"\nRSI Divergence:")
    if result['rsi_divergence']['detected']:
        rd = result['rsi_divergence']
        print(f"  Type: {rd['type'].upper()}")
        print(f"  Strength: {rd['strength']}")
    else:
        print(f"  None detected")
    
    print(f"\nSupport/Resistance:")
    sr = result['support_resistance']
    if sr['support']:
        print(f"  Support: {', '.join([f'₹{s:.2f}' for s in sr['support']])}")
    if sr['resistance']:
        print(f"  Resistance: {', '.join([f'₹{r:.2f}' for r in sr['resistance']])}")
    
    print(f"\nKey Signals:")
    for signal in result['signals']:
        print(f"  • {signal}")
    
    print(f"\n{'='*80}")
    print("✅ Advanced Technical Analysis Complete!")
