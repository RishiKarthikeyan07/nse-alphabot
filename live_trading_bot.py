#!/usr/bin/env python3
"""
NSE AlphaBot - Live Trading with Zerodha Kite
Automated trading system that:
1. Runs bot to generate signals
2. Executes trades on Zerodha automatically
3. Manages positions with stop loss and targets
"""

import sys
import os
sys.path.append('src')

from trading.zerodha_live_trader import ZerodhaLiveTrader, setup_zerodha
from bot.nse_alphabot_ultimate import run_ultimate_bot
import json
from datetime import datetime
import time
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('live_trading_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class LiveTradingBot:
    """
    Automated live trading bot
    """
    
    def __init__(self, trader, auto_execute=False, max_positions=8, capital=500000):
        """
        Initialize live trading bot
        
        Args:
            trader: ZerodhaLiveTrader instance
            auto_execute: If True, automatically execute trades
            max_positions: Maximum number of positions
            capital: Total capital
        """
        self.trader = trader
        self.auto_execute = auto_execute
        self.max_positions = max_positions
        self.capital = capital
        self.executed_today = []
        
    def run_bot_and_get_signals(self):
        """
        Run NSE AlphaBot and get signals
        
        Returns:
            List of signals
        """
        logger.info("\n" + "="*100)
        logger.info("🤖 RUNNING NSE ALPHABOT")
        logger.info("="*100)
        
        try:
            # Import and run bot
            from bot.nse_alphabot_ultimate import ELITE_STOCKS, get_stock_data, analyze_stock
            
            signals = []
            
            for ticker in ELITE_STOCKS:
                try:
                    result = analyze_stock(ticker)
                    if result and result.get('signal') == 'BUY':
                        signals.append(result)
                except Exception as e:
                    logger.error(f"Error analyzing {ticker}: {e}")
                    continue
            
            # Sort by confidence
            signals.sort(key=lambda x: x['confidence'], reverse=True)
            
            logger.info(f"\n✅ Bot analysis complete: {len(signals)} BUY signals found")
            
            return signals
            
        except Exception as e:
            logger.error(f"❌ Failed to run bot: {e}")
            return []
    
    def check_position_limits(self):
        """Check if we can take more positions"""
        try:
            positions = self.trader.get_positions()
            
            if not positions or 'net' not in positions:
                current_positions = 0
            else:
                current_positions = len([p for p in positions['net'] if p['quantity'] != 0])
            
            logger.info(f"📊 Current Positions: {current_positions}/{self.max_positions}")
            
            return current_positions < self.max_positions
            
        except Exception as e:
            logger.error(f"❌ Failed to check positions: {e}")
            return False
    
    def execute_signals(self, signals):
        """
        Execute trading signals
        
        Args:
            signals: List of signals from bot
        """
        if not signals:
            logger.info("⏳ No signals to execute")
            return
        
        logger.info("\n" + "="*100)
        logger.info(f"🎯 EXECUTING {len(signals)} SIGNALS")
        logger.info("="*100)
        
        executed_count = 0
        
        for i, signal in enumerate(signals, 1):
            # Check position limits
            if not self.check_position_limits():
                logger.warning("⚠️ Maximum positions reached. Skipping remaining signals.")
                break
            
            ticker = signal['ticker']
            
            # Check if already executed today
            if ticker in self.executed_today:
                logger.info(f"⏭️ Skipping {ticker} - Already executed today")
                continue
            
            logger.info(f"\n{'='*100}")
            logger.info(f"Signal {i}/{len(signals)}: {ticker}")
            logger.info(f"{'='*100}")
            logger.info(f"Price: ₹{signal['price']:.2f}")
            logger.info(f"Shares: {signal['shares']}")
            logger.info(f"Confidence: {signal['confidence']:.0%}")
            logger.info(f"Expected Return: +{signal['expected_return']:.1f}%")
            logger.info(f"Capital Required: ₹{signal['price'] * signal['shares']:,.0f}")
            
            if self.auto_execute:
                # Auto execute
                logger.info("🤖 AUTO-EXECUTING...")
                order_id = self.trader.execute_bot_signal(signal)
                
                if order_id:
                    executed_count += 1
                    self.executed_today.append(ticker)
                    logger.info(f"✅ Trade executed: {ticker}")
                else:
                    logger.error(f"❌ Trade failed: {ticker}")
            else:
                # Manual confirmation
                response = input(f"\n🤔 Execute this trade? (yes/no/skip/quit): ").strip().lower()
                
                if response == 'yes':
                    order_id = self.trader.execute_bot_signal(signal)
                    if order_id:
                        executed_count += 1
                        self.executed_today.append(ticker)
                        logger.info(f"✅ Trade executed: {ticker}")
                    else:
                        logger.error(f"❌ Trade failed: {ticker}")
                        
                elif response == 'skip':
                    logger.info(f"⏭️ Skipped: {ticker}")
                    continue
                    
                elif response == 'quit':
                    logger.info("🛑 Stopping execution")
                    break
                    
                else:
                    logger.info(f"❌ Cancelled: {ticker}")
        
        logger.info("\n" + "="*100)
        logger.info(f"✅ EXECUTION COMPLETE: {executed_count}/{len(signals)} trades executed")
        logger.info("="*100)
    
    def monitor_positions(self):
        """Monitor and display current positions"""
        logger.info("\n" + "="*100)
        logger.info("📊 CURRENT POSITIONS")
        logger.info("="*100)
        
        try:
            positions = self.trader.get_positions()
            
            if not positions or 'net' not in positions or not positions['net']:
                logger.info("No open positions")
                return
            
            total_pnl = 0
            
            for pos in positions['net']:
                if pos['quantity'] == 0:
                    continue
                
                pnl = pos['pnl']
                total_pnl += pnl
                
                pnl_pct = (pnl / (pos['buy_price'] * pos['quantity'])) * 100 if pos['buy_price'] > 0 else 0
                
                logger.info(f"\n{pos['tradingsymbol']}:")
                logger.info(f"  Quantity: {pos['quantity']}")
                logger.info(f"  Buy Price: ₹{pos['buy_price']:.2f}")
                logger.info(f"  LTP: ₹{pos['last_price']:.2f}")
                logger.info(f"  P&L: ₹{pnl:,.2f} ({pnl_pct:+.2f}%)")
            
            logger.info(f"\n{'='*100}")
            logger.info(f"💰 Total P&L: ₹{total_pnl:,.2f}")
            logger.info("="*100)
            
        except Exception as e:
            logger.error(f"❌ Failed to get positions: {e}")
    
    def run_daily_cycle(self):
        """Run complete daily trading cycle"""
        logger.info("\n" + "="*100)
        logger.info("🌅 STARTING DAILY TRADING CYCLE")
        logger.info(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("="*100)
        
        # Check market status
        if not self.trader.is_market_open():
            logger.warning("⏸️ Market is CLOSED. Exiting.")
            return
        
        logger.info("✅ Market is OPEN")
        
        # Get account info
        logger.info("\n📊 Account Information:")
        profile = self.trader.get_profile()
        margins = self.trader.get_margins()
        
        # Run bot and get signals
        signals = self.run_bot_and_get_signals()
        
        if not signals:
            logger.info("\n⏳ No trading signals today")
            return
        
        # Display signals
        logger.info("\n" + "="*100)
        logger.info(f"📋 SIGNALS SUMMARY ({len(signals)} signals)")
        logger.info("="*100)
        
        for i, signal in enumerate(signals, 1):
            logger.info(f"{i}. {signal['ticker']}: ₹{signal['price']:.2f} | "
                       f"Conf: {signal['confidence']:.0%} | "
                       f"Return: +{signal['expected_return']:.1f}%")
        
        # Execute signals
        self.execute_signals(signals)
        
        # Monitor positions
        self.monitor_positions()
        
        logger.info("\n" + "="*100)
        logger.info("✅ DAILY CYCLE COMPLETE")
        logger.info("="*100)


def main():
    """Main function"""
    print("="*100)
    print("🚀 NSE ALPHABOT - LIVE TRADING WITH ZERODHA KITE")
    print("="*100)
    
    # Setup Zerodha
    print("\n🔧 Setting up Zerodha Kite connection...")
    trader = setup_zerodha()
    
    if not trader:
        print("\n❌ Failed to setup Zerodha. Please check your credentials.")
        return
    
    print("\n✅ Zerodha connection established!")
    
    # Configuration
    print("\n" + "="*100)
    print("⚙️ CONFIGURATION")
    print("="*100)
    
    auto_execute = input("Auto-execute trades? (yes/no): ").strip().lower() == 'yes'
    
    if auto_execute:
        print("⚠️ WARNING: Trades will be executed AUTOMATICALLY!")
        confirm = input("Are you sure? (yes/no): ").strip().lower()
        if confirm != 'yes':
            auto_execute = False
            print("✅ Switched to manual mode")
    
    max_positions = int(input("Maximum positions (default 8): ").strip() or "8")
    capital = float(input("Total capital (default 500000): ").strip() or "500000")
    
    print(f"\n✅ Configuration:")
    print(f"   Auto-execute: {auto_execute}")
    print(f"   Max positions: {max_positions}")
    print(f"   Capital: ₹{capital:,.0f}")
    
    # Initialize bot
    bot = LiveTradingBot(
        trader=trader,
        auto_execute=auto_execute,
        max_positions=max_positions,
        capital=capital
    )
    
    # Run daily cycle
    bot.run_daily_cycle()
    
    print("\n" + "="*100)
    print("✅ LIVE TRADING SESSION COMPLETE")
    print("="*100)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n🛑 Interrupted by user")
    except Exception as e:
        logger.error(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
