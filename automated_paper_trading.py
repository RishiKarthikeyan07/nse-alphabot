#!/usr/bin/env python3
"""
Automated Paper Trading System for NSE AlphaBot
Integrates bot signals with DRL agent for automatic trade execution
"""

import sys
sys.path.append('src')

import json
import os
from datetime import datetime
import pandas as pd
import yfinance as yf
import numpy as np
from stable_baselines3 import SAC

# Import bot components
from bot.nse_alphabot_ultimate import run_ultimate_bot, generate_ultimate_signal, CAPITAL, RISK_PER_TRADE, MAX_POSITIONS
from models.kronos_predictor import get_kronos_predictor

# Configuration
PAPER_TRADING_LOG = "paper_trading_log.json"
SIGNALS_DIR = "signals"
os.makedirs(SIGNALS_DIR, exist_ok=True)

class AutomatedPaperTrader:
    """
    Automated paper trading system with DRL agent decision making
    """
    
    def __init__(self, initial_capital=500000):
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.positions = {}  # {ticker: {shares, entry_price, entry_date, stop_loss}}
        self.trade_history = []
        self.load_state()
        
        # Load DRL agent
        print("🤖 Loading DRL Agent for automated trading...")
        try:
            self.drl_agent = SAC.load("models/sac_nse_retrained.zip")
            print("✅ DRL Agent loaded successfully")
        except:
            try:
                self.drl_agent = SAC.load("models/sac_nse_10y_final.zip")
                print("✅ DRL Agent loaded (original)")
            except:
                print("❌ DRL Agent not found!")
                self.drl_agent = None
    
    def load_state(self):
        """Load existing paper trading state"""
        if os.path.exists(PAPER_TRADING_LOG):
            with open(PAPER_TRADING_LOG, 'r') as f:
                data = json.load(f)
                self.current_capital = data.get('current_capital', self.initial_capital)
                self.positions = data.get('positions', {})
                self.trade_history = data.get('trade_history', [])
                print(f"📂 Loaded existing state: ₹{self.current_capital:,.0f} capital, {len(self.positions)} open positions")
        else:
            print(f"🆕 Starting fresh with ₹{self.initial_capital:,.0f} capital")
    
    def save_state(self):
        """Save paper trading state"""
        data = {
            'start_date': datetime.now().strftime('%Y-%m-%d'),
            'initial_capital': self.initial_capital,
            'current_capital': self.current_capital,
            'positions': self.positions,
            'trade_history': self.trade_history,
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        with open(PAPER_TRADING_LOG, 'w') as f:
            json.dump(data, f, indent=2)
    
    def get_drl_decision(self, ticker, signal_data):
        """
        Get DRL agent's decision on whether to execute trade
        
        Returns: (action, confidence)
            action: 'BUY', 'HOLD', 'SELL'
            confidence: 0-1
        """
        if self.drl_agent is None:
            return 'HOLD', 0.5
        
        try:
            # Prepare state for DRL agent
            price = signal_data['price']
            rsi = signal_data['rsi']
            
            # Get MACD from recent data
            df = yf.download(ticker, period='1mo', interval='1d', progress=False, auto_adjust=True)
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            
            ema_12 = df['Close'].ewm(span=12).mean().iloc[-1]
            ema_26 = df['Close'].ewm(span=26).mean().iloc[-1]
            macd = ema_12 - ema_26
            
            # Normalize inputs
            price_norm = np.clip(price / 10000.0, 0, 10)
            rsi_norm = np.clip(rsi / 100.0, 0, 1)
            macd_norm = np.clip(macd / 100.0, -1, 1)
            capital_ratio = np.clip(self.current_capital / self.initial_capital, 0, 2)
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
            print(f"⚠️  DRL decision error: {str(e)[:50]}")
            return 'HOLD', 0.5
    
    def calculate_position_size(self, price, confidence, expected_return):
        """Calculate position size based on risk management"""
        # Base size: 2% of capital
        base_size = self.current_capital * RISK_PER_TRADE
        
        # Confidence multiplier (1.0x to 2.0x)
        confidence_mult = 1.0 + (confidence - 0.75) * 2.0
        confidence_mult = max(1.0, min(2.0, confidence_mult))
        
        # Return multiplier (up to 2.5x)
        return_mult = min(2.5, 1.0 + (expected_return / 10))
        
        # Calculate final size
        position_size = base_size * confidence_mult * return_mult
        
        # Cap at 20% of capital
        max_position = self.current_capital * 0.20
        position_size = min(position_size, max_position)
        
        # Calculate shares
        shares = int(position_size / price)
        
        return shares, position_size
    
    def execute_buy(self, ticker, signal_data, drl_confidence):
        """Execute a BUY trade"""
        # Check if we already have this position
        if ticker in self.positions:
            print(f"⏭️  Already holding {ticker}, skipping")
            return False
        
        # Check if we have reached max positions
        if len(self.positions) >= MAX_POSITIONS:
            print(f"⏭️  Max positions ({MAX_POSITIONS}) reached, skipping")
            return False
        
        # Calculate position size
        price = signal_data['price']
        confidence = signal_data['confidence']
        expected_return = signal_data['expected_return']
        
        shares, position_size = self.calculate_position_size(price, confidence, expected_return)
        
        # Check if we have enough capital
        if position_size > self.current_capital:
            print(f"⏭️  Insufficient capital (need ₹{position_size:,.0f}, have ₹{self.current_capital:,.0f})")
            return False
        
        # Calculate stop loss (5% below entry)
        stop_loss = price * 0.95
        
        # Execute trade
        self.positions[ticker] = {
            'shares': shares,
            'entry_price': price,
            'entry_date': datetime.now().strftime('%Y-%m-%d'),
            'entry_time': datetime.now().strftime('%H:%M:%S'),
            'stop_loss': stop_loss,
            'target': price * (1 + expected_return / 100),
            'confidence': confidence,
            'drl_confidence': drl_confidence,
            'expected_return': expected_return
        }
        
        self.current_capital -= position_size
        
        # Log trade
        trade = {
            'trade_id': len(self.trade_history) + 1,
            'type': 'BUY',
            'ticker': ticker,
            'date': datetime.now().strftime('%Y-%m-%d'),
            'time': datetime.now().strftime('%H:%M:%S'),
            'price': price,
            'shares': shares,
            'amount': position_size,
            'confidence': confidence,
            'drl_confidence': drl_confidence,
            'expected_return': expected_return
        }
        
        self.trade_history.append(trade)
        self.save_state()
        
        print(f"\n✅ BUY EXECUTED: {ticker}")
        print(f"   Price: ₹{price:.2f}")
        print(f"   Shares: {shares}")
        print(f"   Amount: ₹{position_size:,.0f}")
        print(f"   Stop Loss: ₹{stop_loss:.2f}")
        print(f"   Target: ₹{price * (1 + expected_return / 100):.2f}")
        print(f"   Bot Confidence: {confidence:.1%}")
        print(f"   DRL Confidence: {drl_confidence:.1%}")
        
        return True
    
    def execute_sell(self, ticker, reason='DRL_SIGNAL'):
        """Execute a SELL trade"""
        if ticker not in self.positions:
            return False
        
        position = self.positions[ticker]
        
        # Get current price
        try:
            stock = yf.Ticker(ticker)
            current_price = stock.history(period='1d')['Close'].iloc[-1]
        except:
            print(f"⚠️  Could not fetch price for {ticker}")
            return False
        
        # Calculate P&L
        shares = position['shares']
        entry_price = position['entry_price']
        exit_value = current_price * shares
        entry_value = entry_price * shares
        pnl = exit_value - entry_value
        pnl_pct = (pnl / entry_value) * 100
        
        # Update capital
        self.current_capital += exit_value
        
        # Log trade
        trade = {
            'trade_id': len(self.trade_history) + 1,
            'type': 'SELL',
            'ticker': ticker,
            'date': datetime.now().strftime('%Y-%m-%d'),
            'time': datetime.now().strftime('%H:%M:%S'),
            'entry_price': entry_price,
            'exit_price': current_price,
            'shares': shares,
            'pnl': pnl,
            'pnl_pct': pnl_pct,
            'reason': reason
        }
        
        self.trade_history.append(trade)
        
        # Remove position
        del self.positions[ticker]
        self.save_state()
        
        print(f"\n✅ SELL EXECUTED: {ticker}")
        print(f"   Entry: ₹{entry_price:.2f} → Exit: ₹{current_price:.2f}")
        print(f"   P&L: ₹{pnl:,.0f} ({pnl_pct:+.2f}%)")
        print(f"   Reason: {reason}")
        
        return True
    
    def update_positions(self):
        """Update all open positions and check stop loss/targets"""
        print(f"\n🔄 Updating {len(self.positions)} open positions...")
        
        for ticker in list(self.positions.keys()):
            position = self.positions[ticker]
            
            try:
                # Get current price
                stock = yf.Ticker(ticker)
                current_price = stock.history(period='1d')['Close'].iloc[-1]
                
                # Calculate current P&L
                entry_price = position['entry_price']
                shares = position['shares']
                pnl = (current_price - entry_price) * shares
                pnl_pct = (pnl / (entry_price * shares)) * 100
                
                print(f"\n   {ticker}:")
                print(f"   Entry: ₹{entry_price:.2f} → Current: ₹{current_price:.2f}")
                print(f"   P&L: ₹{pnl:,.0f} ({pnl_pct:+.2f}%)")
                
                # Check stop loss
                if current_price <= position['stop_loss']:
                    print(f"   ⚠️  STOP LOSS HIT!")
                    self.execute_sell(ticker, reason='STOP_LOSS')
                    continue
                
                # Check target
                if current_price >= position['target']:
                    print(f"   🎯 TARGET REACHED!")
                    self.execute_sell(ticker, reason='TARGET')
                    continue
                
                # Get DRL decision for holding
                signal_data = {
                    'price': current_price,
                    'rsi': 50,  # Placeholder
                    'confidence': position['confidence'],
                    'expected_return': position['expected_return']
                }
                
                drl_decision, drl_conf = self.get_drl_decision(ticker, signal_data)
                
                if drl_decision == 'SELL' and drl_conf > 0.7:
                    print(f"   🤖 DRL recommends SELL (confidence: {drl_conf:.1%})")
                    self.execute_sell(ticker, reason='DRL_SIGNAL')
                
            except Exception as e:
                print(f"   ❌ Error updating {ticker}: {str(e)[:50]}")
        
        self.save_state()
    
    def run_daily_cycle(self):
        """Run complete daily trading cycle"""
        print("\n" + "="*100)
        print(f"🤖 AUTOMATED PAPER TRADING - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print("="*100)
        print(f"💰 Capital: ₹{self.current_capital:,.0f} | Positions: {len(self.positions)}/{MAX_POSITIONS}")
        print("="*100)
        
        # Step 1: Update existing positions
        if self.positions:
            self.update_positions()
        
        # Step 2: Generate new signals from bot
        print(f"\n📊 STEP 1: GENERATING SIGNALS")
        print("="*100)
        
        # Import and run bot (this will screen 2000+ stocks)
        from utils.pkscreener_integration import screen_nse_stocks
        
        print("🔍 Screening NSE stocks...")
        qualified_stocks = screen_nse_stocks(max_stocks=50, min_volume=1000000, min_price=100, max_price=10000)
        
        if not qualified_stocks:
            print("⏳ No qualified stocks today")
            return
        
        print(f"\n📊 STEP 2: ANALYZING TOP {len(qualified_stocks)} STOCKS")
        print("="*100)
        
        signals = []
        for i, ticker in enumerate(qualified_stocks, 1):
            print(f"🔍 [{i:3}/{len(qualified_stocks)}] {ticker:20}", end=" ")
            
            try:
                signal = generate_ultimate_signal(ticker)
                
                if signal and signal['signal'] == 'BUY':
                    signals.append(signal)
                    print(f"🎯 BUY  | Conf: {signal['confidence']:.2f}")
                else:
                    print(f"⏭️  HOLD")
            except Exception as e:
                print(f"❌ Error")
        
        # Step 3: DRL agent evaluates signals and executes trades
        if signals:
            print(f"\n📊 STEP 3: DRL AGENT EVALUATION")
            print("="*100)
            print(f"Found {len(signals)} BUY signals, evaluating with DRL agent...")
            
            for signal in signals:
                ticker = signal['ticker']
                
                # Get DRL decision
                drl_decision, drl_confidence = self.get_drl_decision(ticker, signal)
                
                print(f"\n{ticker}:")
                print(f"  Bot Signal: BUY (confidence: {signal['confidence']:.1%})")
                print(f"  DRL Decision: {drl_decision} (confidence: {drl_confidence:.1%})")
                
                # Execute if both bot and DRL agree
                if drl_decision == 'BUY' and drl_confidence >= 0.6:
                    print(f"  ✅ Both systems agree - EXECUTING TRADE")
                    self.execute_buy(ticker, signal, drl_confidence)
                else:
                    print(f"  ⏭️  DRL disagrees - SKIPPING")
        else:
            print(f"\n⏳ NO SIGNALS TODAY")
        
        # Step 4: Summary
        print(f"\n" + "="*100)
        print(f"📊 DAILY SUMMARY")
        print("="*100)
        print(f"💰 Current Capital: ₹{self.current_capital:,.0f}")
        print(f"📈 Open Positions: {len(self.positions)}")
        print(f"📊 Total Trades: {len(self.trade_history)}")
        
        if self.trade_history:
            closed_trades = [t for t in self.trade_history if t['type'] == 'SELL']
            if closed_trades:
                total_pnl = sum(t.get('pnl', 0) for t in closed_trades)
                print(f"💵 Total P&L: ₹{total_pnl:,.0f}")
        
        print("="*100)
        
        self.save_state()


def main():
    """Main function"""
    trader = AutomatedPaperTrader(initial_capital=500000)
    trader.run_daily_cycle()


if __name__ == "__main__":
    main()
