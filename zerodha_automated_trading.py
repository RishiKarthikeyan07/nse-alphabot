#!/usr/bin/env python3
"""
Zerodha Automated Trading System
Runs trading cycles automatically during market hours
"""

import sys
import os
sys.path.append('src')

import time
import schedule
import logging
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    filename=f'autotrade_{datetime.now().strftime("%Y%m%d")}.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class AutomatedTradingSystem:
    """
    Automated trading system scheduler for Zerodha
    """
    
    def __init__(self):
        self.trader = None
        self.trading_times = ['09:30', '11:00', '13:00', '14:30']  # IST
        self.market_open = '09:15'
        self.market_close = '15:30'
        
    def is_trading_day(self):
        """Check if today is a trading day (Monday-Friday)"""
        return datetime.now().weekday() < 5  # 0-4 is Mon-Fri
    
    def is_market_hours(self):
        """Check if current time is within market hours"""
        now = datetime.now()
        current_time = now.strftime('%H:%M')
        
        # Convert to minutes for comparison
        def time_to_minutes(time_str):
            h, m = map(int, time_str.split(':'))
            return h * 60 + m
        
        current_minutes = time_to_minutes(current_time)
        open_minutes = time_to_minutes(self.market_open)
        close_minutes = time_to_minutes(self.market_close)
        
        return open_minutes <= current_minutes <= close_minutes
    
    def initialize_trader(self):
        """Initialize the Zerodha trader"""
        try:
            from src.trading.zerodha_live_trader import ZerodhaLiveTrader
            
            # Try to load from config
            try:
                self.trader = ZerodhaLiveTrader.load_from_config()
                print("✅ Trader loaded from configuration")
                logging.info("Trader loaded from configuration")
                return True
                
            except FileNotFoundError:
                print("❌ No saved configuration found")
                print("Please run authentication first:")
                print("python3 src/trading/zerodha_live_trader.py")
                return False
                
        except Exception as e:
            print(f"❌ Failed to initialize trader: {e}")
            logging.error(f"Trader initialization failed: {e}")
            return False
    
    def run_trading_cycle(self):
        """Run a single trading cycle"""
        if not self.is_trading_day():
            print("⏭️  Not a trading day (weekend)")
            return
        
        if not self.is_market_hours():
            print("⏭️  Outside market hours")
            return
        
        print(f"\n{'='*100}")
        print(f"🔄 RUNNING TRADING CYCLE - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*100}")
        
        try:
            if self.trader is None:
                if not self.initialize_trader():
                    return
            
            # Load trading state
            self.trader.load_trading_state()
            
            # Run automated cycle
            self.trader.run_automated_cycle()
            
            print(f"✅ Trading cycle completed successfully")
            logging.info("Trading cycle completed successfully")
            
        except Exception as e:
            print(f"❌ Trading cycle failed: {e}")
            logging.error(f"Trading cycle failed: {e}")
    
    def schedule_trading(self):
        """Schedule trading cycles"""
        print("\n" + "="*100)
        print("🤖 ZERODHA AUTOMATED TRADING SYSTEM")
        print("="*100)
        print(f"Trading Times (IST): {', '.join(self.trading_times)}")
        print(f"Market Hours: {self.market_open} - {self.market_close}")
        print(f"Trading Days: Monday - Friday")
        print("="*100)
        
        # Schedule trading cycles
        for trading_time in self.trading_times:
            schedule.every().day.at(trading_time).do(self.run_trading_cycle)
            print(f"✅ Scheduled trading cycle at {trading_time} IST")
        
        print("\n🚀 Automated trading system started!")
        print("Press Ctrl+C to stop\n")
        
        # Run scheduler
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
                
        except KeyboardInterrupt:
            print("\n\n⚠️  Automated trading stopped by user")
            logging.info("Automated trading stopped by user")


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Zerodha Automated Trading System')
    parser.add_argument('--manual', action='store_true', help='Run single manual cycle')
    parser.add_argument('--test', action='store_true', help='Test mode (no actual orders)')
    
    args = parser.parse_args()
    
    system = AutomatedTradingSystem()
    
    if args.manual:
        # Run single manual cycle
        print("🔧 Running manual trading cycle...")
        system.run_trading_cycle()
    else:
        # Start automated scheduler
        system.schedule_trading()


if __name__ == "__main__":
    main()
