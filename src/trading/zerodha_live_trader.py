#!/usr/bin/env python3
"""
Zerodha Kite Live Trading Integration for NSE AlphaBot
Automated trading system with DRL agent decision making
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import json
import logging
from datetime import datetime
import pandas as pd
import numpy as np

try:
    from kiteconnect import KiteConnect
except ImportError:
    print("⚠️  kiteconnect not installed. Install with: pip install kiteconnect")
    KiteConnect = None

from stable_baselines3 import SAC

# Setup logging
logging.basicConfig(
    filename=f'zerodha_trading_{datetime.now().strftime("%Y%m%d")}.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class ZerodhaLiveTrader:
    """
    Live trading system for Zerodha Kite with DRL agent integration
    """

    def __init__(self, api_key, api_secret, access_token=None):
        if KiteConnect is None:
            raise ImportError("kiteconnect library not installed")
            
        self.api_key = api_key
        self.api_secret = api_secret
        self.access_token = access_token

        # Initialize Kite
        self.kite = KiteConnect(api_key=self.api_key)

        # Trading state
        self.positions = {}
        self.max_positions = 8
        self.risk_per_trade = 0.02
        self.max_daily_loss = 50000

        # Load DRL agent
        self.load_drl_agent()

        # Set access token if provided
        if self.access_token:
            self.kite.set_access_token(self.access_token)

    def load_drl_agent(self):
        """Load the trained DRL agent"""
        print("🤖 Loading DRL Agent...")
        try:
            self.drl_agent = SAC.load("models/sac_nse_nifty100.zip")
            print("✅ Nifty 100 DRL Agent loaded")
        except:
            try:
                self.drl_agent = SAC.load("models/sac_nse_retrained.zip")
                print("✅ Retrained DRL Agent loaded")
            except:
                print("❌ DRL Agent not found!")
                self.drl_agent = None

    def authenticate(self):
        """Authenticate with Zerodha Kite"""
        print("🔐 Authenticating with Zerodha Kite...")
        
        # Generate login URL
        login_url = self.kite.login_url()
        print(f"\n🔗 Please visit this URL to login:\n{login_url}\n")
        print("After logging in, copy the 'request_token' from the URL")
        
        request_token = input("Enter request_token: ").strip()
        
        try:
            # Generate access token
            data = self.kite.generate_session(request_token, api_secret=self.api_secret)
            self.access_token = data["access_token"]
            self.kite.set_access_token(self.access_token)
            
            # Save tokens
            self.save_tokens()
            
            print("✅ Authentication successful!")
            return True
            
        except Exception as e:
            print(f"❌ Authentication failed: {e}")
            return False

    def save_tokens(self):
        """Save access token"""
        config = {
            'api_key': self.api_key,
            'api_secret': self.api_secret,
            'access_token': self.access_token,
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        with open('zerodha_config.json', 'w') as f:
            json.dump(config, f, indent=2)
        
        print("💾 Tokens saved to zerodha_config.json")

    @classmethod
    def load_from_config(cls):
        """Load trader from saved config"""
        if os.path.exists('zerodha_config.json'):
            with open('zerodha_config.json', 'r') as f:
                config = json.load(f)
            
            return cls(
                api_key=config['api_key'],
                api_secret=config['api_secret'],
                access_token=config['access_token']
            )
        else:
            raise FileNotFoundError("zerodha_config.json not found")

    def get_portfolio_summary(self):
        """Get current portfolio summary"""
        try:
            positions = self.kite.positions()
            holdings = positions.get('net', [])
            
            total_value = 0
            total_pnl = 0
            
            print(f"\n📊 PORTFOLIO SUMMARY ({len(holdings)} positions)")
            print("="*80)
            
            for position in holdings:
                if position['quantity'] > 0:
                    symbol = position['tradingsymbol']
                    qty = position['quantity']
                    avg_price = position['average_price']
                    ltp = position['last_price']
                    pnl = position['pnl']
                    
                    total_value += ltp * qty
                    total_pnl += pnl
                    
                    print(f"{symbol:<12} Qty:{qty:>4} Avg:{avg_price:>8.2f} LTP:{ltp:>8.2f} P&L:{pnl:>+10.2f}")
            
            print("="*80)
            print(f"Total Value: ₹{total_value:,.0f}")
            print(f"Total P&L: ₹{total_pnl:,.0f}")
            print("="*80)
            
            return holdings
            
        except Exception as e:
            print(f"❌ Error getting portfolio: {e}")
            return []

    def get_drl_decision(self, ticker, signal_data):
        """Get DRL agent's decision"""
        if self.drl_agent is None:
            return 'HOLD', 0.5
        
        try:
            price = signal_data['price']
            rsi = signal_data.get('rsi', 50)
            
            # Normalize inputs
            price_norm = np.clip(price / 10000.0, 0, 10)
            rsi_norm = np.clip(rsi / 100.0, 0, 1)
            macd_norm = 0.0
            capital_ratio = 0.8
            shares_held = 1.0 if ticker in self.positions else 0.0
            
            # Create observation
            obs = np.array([price_norm, rsi_norm, macd_norm, capital_ratio, shares_held], dtype=np.float32)
            obs = np.nan_to_num(obs, nan=0.0, posinf=1.0, neginf=0.0)
            
            # Get DRL action
            action, _ = self.drl_agent.predict(obs, deterministic=True)
            action_value = float(action[0])
            
            # Convert to decision
            if action_value > 0.3:
                decision = 'BUY'
                confidence = min(0.5 + action_value * 0.5, 1.0)
            elif action_value < -0.3:
                decision = 'SELL'
                confidence = min(0.5 + abs(action_value) * 0.5, 1.0)
            else:
                decision = 'HOLD'
                confidence = 0.5
            
            return decision, confidence
            
        except Exception as e:
            logging.error(f"DRL decision error for {ticker}: {e}")
            return 'HOLD', 0.5

    def place_buy_order(self, ticker, signal_data, drl_confidence):
        """Place a BUY order on Zerodha"""
        try:
            # Get instrument
            instruments = self.kite.instruments(exchange='NSE')
            instrument = next((i for i in instruments if i['tradingsymbol'] == ticker.replace('.NS', '')), None)
            
            if not instrument:
                print(f"❌ Instrument not found: {ticker}")
                return False
            
            # Calculate position size
            price = signal_data['price']
            shares = max(1, int((500000 * 0.02) / price))  # 2% of 5L capital
            
            # Calculate stop loss and target
            stop_loss = price * 0.95
            target = price * (1 + signal_data['expected_return'] / 100)
            
            print(f"\n🎯 PLACING BUY ORDER: {ticker}")
            print(f"   Price: ₹{price:.2f}")
            print(f"   Shares: {shares}")
            print(f"   Stop Loss: ₹{stop_loss:.2f}")
            print(f"   Target: ₹{target:.2f}")
            
            # Place order
            order_id = self.kite.place_order(
                variety='regular',
                exchange='NSE',
                tradingsymbol=instrument['tradingsymbol'],
                transaction_type='BUY',
                quantity=shares,
                price=None,
                order_type='MARKET',
                product='CNC'
            )
            
            # Track position
            self.positions[ticker] = {
                'order_id': order_id,
                'shares': shares,
                'entry_price': price,
                'stop_loss': stop_loss,
                'target': target,
                'confidence': signal_data['confidence'],
                'drl_confidence': drl_confidence
            }
            
            print(f"✅ BUY ORDER PLACED: {ticker} (Order ID: {order_id})")
            self.save_trading_state()
            
            return True
            
        except Exception as e:
            print(f"❌ Buy order failed for {ticker}: {e}")
            logging.error(f"Buy order failed for {ticker}: {e}")
            return False

    def place_sell_order(self, ticker, reason='DRL_SIGNAL'):
        """Place a SELL order on Zerodha"""
        if ticker not in self.positions:
            return False
        
        try:
            position = self.positions[ticker]
            shares = position['shares']
            
            # Get instrument
            instruments = self.kite.instruments(exchange='NSE')
            instrument = next((i for i in instruments if i['tradingsymbol'] == ticker.replace('.NS', '')), None)
            
            if not instrument:
                print(f"❌ Instrument not found: {ticker}")
                return False
            
            print(f"\n🎯 PLACING SELL ORDER: {ticker}")
            print(f"   Shares: {shares}")
            print(f"   Reason: {reason}")
            
            # Place sell order
            order_id = self.kite.place_order(
                variety='regular',
                exchange='NSE',
                tradingsymbol=instrument['tradingsymbol'],
                transaction_type='SELL',
                quantity=shares,
                price=None,
                order_type='MARKET',
                product='CNC'
            )
            
            print(f"✅ SELL ORDER PLACED: {ticker} (Order ID: {order_id})")
            
            # Remove from positions
            del self.positions[ticker]
            self.save_trading_state()
            
            return True
            
        except Exception as e:
            print(f"❌ Sell order failed for {ticker}: {e}")
            logging.error(f"Sell order failed for {ticker}: {e}")
            return False

    def monitor_positions(self):
        """Monitor open positions"""
        if not self.positions:
            return
        
        print(f"\n🔄 Monitoring {len(self.positions)} positions...")
        
        try:
            for ticker, position in list(self.positions.items()):
                # Get current price (simplified - would need real implementation)
                print(f"   {ticker}: Monitoring...")
                
        except Exception as e:
            print(f"❌ Error monitoring positions: {e}")
            logging.error(f"Position monitoring error: {e}")

    def save_trading_state(self):
        """Save current trading state"""
        state = {
            'positions': self.positions,
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        with open('zerodha_trading_state.json', 'w') as f:
            json.dump(state, f, indent=2)

    def load_trading_state(self):
        """Load trading state"""
        if os.path.exists('zerodha_trading_state.json'):
            with open('zerodha_trading_state.json', 'r') as f:
                state = json.load(f)
                self.positions = state.get('positions', {})
                print(f"📂 Loaded trading state: {len(self.positions)} positions")

    def run_automated_cycle(self):
        """Run complete automated trading cycle"""
        print("\n" + "="*100)
        print(f"🤖 ZERODHA AUTOMATED TRADING - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print("="*100)
        
        try:
            # Step 1: Get portfolio summary
            holdings = self.get_portfolio_summary()
            
            # Step 2: Monitor existing positions
            if self.positions:
                self.monitor_positions()
            
            # Step 3: Generate new signals (simplified)
            print(f"\n📊 STEP 3: GENERATING SIGNALS")
            print("="*100)
            print("Signal generation would happen here...")
            
            # Step 4: Save state
            self.save_trading_state()
            
            print(f"\n" + "="*100)
            print(f"✅ AUTOMATED CYCLE COMPLETE")
            print("="*100)
            
        except Exception as e:
            print(f"❌ Automated cycle failed: {e}")
            logging.error(f"Automated cycle error: {e}")


def main():
    """Main function for Zerodha automated trading"""
    
    # Configuration
    API_KEY = os.getenv('ZERODHA_API_KEY')
    API_SECRET = os.getenv('ZERODHA_API_SECRET')
    
    if not API_KEY or not API_SECRET:
        print("❌ Please set ZERODHA_API_KEY and ZERODHA_API_SECRET environment variables")
        return
    
    try:
        # Try to load from config first
        trader = ZerodhaLiveTrader.load_from_config()
        print("✅ Loaded from saved configuration")
        
    except FileNotFoundError:
        # First time setup
        print("🔐 First time setup required")
        trader = ZerodhaLiveTrader(API_KEY, API_SECRET)
        trader.authenticate()
    
    # Load trading state
    trader.load_trading_state()
    
    # Run automated cycle
    trader.run_automated_cycle()


if __name__ == "__main__":
    main()
