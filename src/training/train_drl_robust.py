#!/usr/bin/env python3
"""
Robust DRL Agent Training for NSE AlphaBot
Handles network issues with retries and uses longer period for more data
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
import time
from stable_baselines3 import SAC
from stable_baselines3.common.vec_env import DummyVecEnv
import gymnasium as gym
from gymnasium import spaces

print("="*100)
print("🚀 NSE ALPHABOT - ROBUST DRL AGENT TRAINING")
print("="*100)

# Configuration
TRAINING_STOCKS = [
    'RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS', 'ICICIBANK.NS',
    'HINDUNILVR.NS', 'KOTAKBANK.NS', 'BHARTIARTL.NS', 'ITC.NS', 'ASIANPAINT.NS',
    'SBIN.NS', 'AXISBANK.NS', 'LT.NS', 'TATAMOTORS.NS', 'TATASTEEL.NS',
    'JSWSTEEL.NS', 'HINDALCO.NS', 'VEDL.NS', 'ADANIPORTS.NS', 'MARUTI.NS'
]

MODEL_DIR = "models"
os.makedirs(MODEL_DIR, exist_ok=True)

def calculate_indicators(df):
    """Calculate technical indicators"""
    # RSI
    delta = df['Close'].diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = (-delta.clip(upper=0)).rolling(14).mean()
    df['rsi'] = 100 - (100 / (1 + gain / loss))
    
    # MACD
    ema_12 = df['Close'].ewm(span=12).mean()
    ema_26 = df['Close'].ewm(span=26).mean()
    df['macd'] = ema_12 - ema_26
    df['macd_signal'] = df['macd'].ewm(span=9).mean()
    
    # Volume
    df['volume_ma'] = df['Volume'].rolling(20).mean()
    df['volume_ratio'] = df['Volume'] / df['volume_ma']
    
    return df.dropna()

def download_with_retry(ticker, max_retries=3, delay=2):
    """Download stock data with retry logic"""
    for attempt in range(max_retries):
        try:
            print(f"  Loading {ticker}... (attempt {attempt + 1}/{max_retries})", end=" ")
            
            # Try different periods to get more data
            for period in ['5y', '3y', '2y', '1y']:
                df = yf.download(ticker, period=period, interval="1d", 
                               auto_adjust=True, progress=False, timeout=15)
                
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.get_level_values(0)
                
                if len(df) >= 200:  # Lower threshold
                    df = calculate_indicators(df)
                    print(f"✅ {len(df)} points (period: {period})")
                    return df
            
            print(f"⚠️  Insufficient data (< 200 points)")
            return None
            
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"❌ Error, retrying in {delay}s...")
                time.sleep(delay)
            else:
                print(f"❌ Failed after {max_retries} attempts")
                return None
    
    return None

class TradingEnv(gym.Env):
    """Custom Trading Environment for DRL"""
    
    def __init__(self, df, initial_capital=100000):
        super().__init__()
        
        self.df = df.reset_index(drop=True)
        self.initial_capital = initial_capital
        self.current_step = 0
        self.max_steps = len(df) - 1
        
        # State: [price_norm, rsi_norm, macd_norm, capital_ratio, shares_held_norm]
        self.observation_space = spaces.Box(
            low=np.array([0, 0, -1, 0, 0], dtype=np.float32),
            high=np.array([10, 1, 1, 2, 1], dtype=np.float32),
            dtype=np.float32
        )
        
        # Action: continuous [-1, 1] (sell to buy)
        self.action_space = spaces.Box(
            low=np.array([-1], dtype=np.float32),
            high=np.array([1], dtype=np.float32),
            dtype=np.float32
        )
        
        self.reset()
    
    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.current_step = 0
        self.capital = self.initial_capital
        self.shares_held = 0
        self.total_value = self.initial_capital
        
        return self._get_observation(), {}
    
    def _get_observation(self):
        """Get current state observation"""
        row = self.df.iloc[self.current_step]
        
        price_norm = np.clip(row['Close'] / 10000.0, 0, 10)
        rsi_norm = np.clip(row['rsi'] / 100.0, 0, 1)
        macd_norm = np.clip(row['macd'] / 100.0, -1, 1)
        capital_ratio = np.clip(self.capital / self.initial_capital, 0, 2)
        shares_held_norm = np.clip(self.shares_held / 100.0, 0, 1)
        
        obs = np.array([price_norm, rsi_norm, macd_norm, capital_ratio, shares_held_norm], dtype=np.float32)
        obs = np.nan_to_num(obs, nan=0.0, posinf=1.0, neginf=0.0)
        
        return obs
    
    def step(self, action):
        """Execute trading action"""
        current_price = self.df.iloc[self.current_step]['Close']
        action_value = action[0]
        
        # Execute trade based on action
        if action_value > 0.3:  # BUY
            shares_to_buy = int((self.capital * 0.95) / current_price)
            if shares_to_buy > 0:
                cost = shares_to_buy * current_price
                self.capital -= cost
                self.shares_held += shares_to_buy
        
        elif action_value < -0.3:  # SELL
            if self.shares_held > 0:
                revenue = self.shares_held * current_price
                self.capital += revenue
                self.shares_held = 0
        
        # Move to next step
        self.current_step += 1
        done = self.current_step >= self.max_steps
        
        # Calculate reward (portfolio value change)
        new_total_value = self.capital + (self.shares_held * current_price)
        reward = (new_total_value - self.total_value) / self.initial_capital
        self.total_value = new_total_value
        
        # Penalty for holding too long without profit
        if self.shares_held > 0 and reward < 0:
            reward -= 0.01
        
        obs = self._get_observation()
        
        return obs, reward, done, False, {}

def train_drl():
    """Train DRL agent with robust data loading"""
    print("\n" + "="*100)
    print("📊 TRAINING DRL AGENT (SAC) - ROBUST VERSION")
    print("="*100)
    
    print(f"\n📥 Loading data from {len(TRAINING_STOCKS)} stocks...")
    print("   Using retry logic and flexible data requirements...")
    
    all_dfs = []
    successful = 0
    failed = 0
    
    for ticker in TRAINING_STOCKS:
        df = download_with_retry(ticker, max_retries=3, delay=2)
        
        if df is not None and len(df) >= 200:
            all_dfs.append(df)
            successful += 1
        else:
            failed += 1
    
    print(f"\n📊 Data Loading Summary:")
    print(f"   ✅ Successful: {successful}/{len(TRAINING_STOCKS)}")
    print(f"   ❌ Failed: {failed}/{len(TRAINING_STOCKS)}")
    
    if len(all_dfs) == 0:
        print("\n❌ No data loaded! Cannot train DRL agent.")
        print("   Please check your internet connection and try again.")
        return None
    
    # Combine data
    combined_df = pd.concat(all_dfs, ignore_index=True)
    print(f"\n✅ Total training data: {len(combined_df):,} points from {len(all_dfs)} stocks")
    
    # Create environment
    def make_env():
        return TradingEnv(combined_df)
    
    env = DummyVecEnv([make_env])
    
    print(f"\n🔧 DRL Configuration:")
    print(f"   Algorithm: SAC (Soft Actor-Critic)")
    print(f"   Training timesteps: 100,000")
    print(f"   Environment: Custom TradingEnv")
    print(f"   Component weights: MTF 25%, SMC 25%, Tech 10%, Sentiment 10%, AI/ML 30%")
    print(f"   AI/ML breakdown: Kronos 70% (21% total), DRL 30% (9% total)")
    
    # Train SAC model
    print(f"\n🔄 Training DRL Agent...")
    print(f"   This will take 5-10 minutes...")
    print(f"   Progress will be shown every 10 updates...")
    
    model = SAC(
        'MlpPolicy',
        env,
        learning_rate=3e-4,
        buffer_size=100000,
        learning_starts=1000,
        batch_size=256,
        tau=0.005,
        gamma=0.99,
        verbose=1,
        device='cpu'
    )
    
    try:
        model.learn(total_timesteps=100000, log_interval=10)
        
        # Save model
        model_path = f"{MODEL_DIR}/sac_nse_retrained.zip"
        model.save(model_path)
        
        print(f"\n💾 Model saved: {model_path}")
        
        # Get file size
        size_mb = os.path.getsize(model_path) / (1024 * 1024)
        print(f"   Model size: {size_mb:.1f} MB")
        print(f"   Training data: {len(combined_df):,} points from {len(all_dfs)} stocks")
        
        return model
        
    except Exception as e:
        print(f"\n❌ Training error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    try:
        start_time = datetime.now()
        
        print(f"\n⏰ Training started at: {start_time.strftime('%H:%M:%S')}")
        
        # Train DRL Agent
        drl_agent = train_drl()
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds() / 60
        
        if drl_agent is not None:
            print("\n" + "="*100)
            print("✅ DRL TRAINING COMPLETE!")
            print("="*100)
            print(f"⏱️  Total time: {duration:.1f} minutes")
            print(f"⏰ Completed at: {end_time.strftime('%H:%M:%S')}")
            print(f"\n📦 Model saved:")
            print(f"  {MODEL_DIR}/sac_nse_retrained.zip")
            print(f"\n🎯 Next steps:")
            print(f"  1. Test the updated bot with new weights")
            print(f"  2. Run: python3 src/bot/nse_alphabot_ultimate.py")
            print(f"  3. Compare performance with old weights")
            print("="*100)
        else:
            print("\n" + "="*100)
            print("❌ DRL TRAINING FAILED")
            print("="*100)
            print("Please check the errors above and try again.")
            print("="*100)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Training interrupted by user")
    except Exception as e:
        print(f"\n❌ Training failed: {e}")
        import traceback
        traceback.print_exc()
