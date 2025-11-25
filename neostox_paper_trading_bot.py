#!/usr/bin/env python3
"""
NeoStox Paper Trading Bot
Automated paper trading with NeoStox's built-in paper trading mode
"""

import sys
import os
sys.path.append('src')

from trading.neostox_trader import NeoStoxTrader, setup_neostox
from bot.nse_alphabot_ultimate import ELITE_STOCKS, analyze_stock
import json
from datetime import datetime
import time
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('neostox_paper_trading.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class NeoStoxPaperTradingBot:
    """
    Automated paper trading bot using NeoStox
    """
    
    def __init__(self, trader: NeoStoxTrader, capital: float = 500000, 
                 max_positions: int = 8, min_confidence: float = 0.75,
                 min_expected_return: float = 2.5):
        """
        Initialize paper trading bot
        
        Args:
            trader: NeoStoxTrader instance
            capital: Total capital
            max_positions: Maximum concurrent positions
            min_confidence: Minimum confidence threshold
            min_expected_return: Minimum expected return %
        """
        self.trader = trader
        self.capital = capital
        self.max_positions = max_positions
        self.min_confidence = min_confidence
        self.min_expected_return = min_expected_return
        
        # Track executed trades today
        self.executed_today = set()
        
        logger.info(f"🤖 Bot initialized with ₹{capital:,.0f} capital")
    
    def calculate_position_size(self, price: float, confidence: float, 
                               expected_return: float) -> tuple:
        """
        Calculate position size based on risk management
        
        Args:
            price: Stock price
            confidence: Signal confidence
            expected_return: Expected return %
            
        Returns:
            (shares, position_size)
        """
        # Risk 3% of capital per trade
        risk_amount = self.capital * 0.03
        
        # Adjust by confidence
        adjusted_risk = risk_amount * confidence
        
        # Calculate shares (assuming 3% stop loss)
        shares = int(adjusted_risk / (price * 0.03))
        
        # Ensure minimum 1 share
        shares = max(1, shares)
        
        # Calculate actual position size
        position_size = shares * price
        
        # Don't exceed 20% of capital per position
        max_position = self.capital * 0.20
        if position_size > max_position:
            shares = int(max_position / price)
            position_size = shares * price
        
        return shares, position_size
    
    def run_bot_analysis(self) -> list:
        """
        Run bot to generate signals
        
        Returns:
            List of signals
        """
        logger.info("\n" + "="*100)
        logger.info("🤖 RUNNING NSE ALPHABOT ANALYSIS")
        logger.info("="*100)
        
        signals = []
        
        for ticker in ELITE_STOCKS:
            try:
                logger.info(f"Analyzing {ticker}...")
                result = analyze_stock(ticker)
                
                if result and result.get('signal') == 'BUY':
                    confidence = result.get('confidence', 0)
                    expected_return = result.get('expected_return', 0)
                    
                    # Filter by thresholds
                    if confidence >= self.min_confidence and expected_return >= self.min_expected_return:
                        signals.append(result)
                        logger.info(f"✅ {ticker}: Conf={confidence:.0%}, Return=+{expected_return:.1f}%")
                
            except Exception as e:
                logger.error(f"❌ Error analyzing {ticker}: {e}")
                continue
        
        # Sort by confidence
        signals.sort(key=lambda x: x['confidence'], reverse=True)
        
        logger.info(f"\n✅ Analysis complete: {len(signals)} BUY signals found")
        return signals
    
    def execute_signal(self, signal: dict, auto_execute: bool = False) -> bool:
        """
        Execute a trading signal
        
        Args:
            signal: Signal dictionary
            auto_execute: If True, execute without confirmation
            
        Returns:
            True if executed successfully
        """
        ticker = signal['ticker'].replace('.NS', '')
        price = signal['price']
        confidence = signal['confidence']
        expected_return = signal['expected_return']
        
        # Check if already executed today
        if ticker in self.executed_today:
            logger.warning(f"⚠️ {ticker} already traded today. Skipping.")
            return False
        
        # Calculate position size
        shares, position_size = self.calculate_position_size(
            price, confidence, expected_return
        )
        
        # Calculate stop loss and target
        stop_loss_price = price * 0.97  # -3%
        target_price = price * (1 + expected_return / 100)
        
        # Calculate points for bracket order
        stop_loss_points = (price - stop_loss_price)
        target_points = (target_price - price)
        
        logger.info("\n" + "="*100)
        logger.info(f"🎯 SIGNAL: {ticker}")
        logger.info("="*100)
        logger.info(f"Price: ₹{price:.2f}")
        logger.info(f"Shares: {shares}")
        logger.info(f"Position Size: ₹{position_size:,.0f}")
        logger.info(f"Confidence: {confidence:.0%}")
        logger.info(f"Expected Return: +{expected_return:.1f}%")
        logger.info(f"Stop Loss: ₹{stop_loss_price:.2f} (-3%)")
        logger.info(f"Target: ₹{target_price:.2f} (+{expected_return:.1f}%)")
        logger.info("="*100)
        
        # Confirm execution
        if not auto_execute:
            confirm = input("\n🤔 Execute this trade? (yes/no/skip/quit): ").strip().lower()
            
            if confirm == 'quit':
                return False
            elif confirm != 'yes':
                logger.info("⏭️ Skipped")
                return False
        
        # Execute bracket order on NeoStox
        try:
            logger.info(f"\n📤 Placing BRACKET order on NeoStox (PAPER MODE)...")
            
            order_id = self.trader.place_bracket_order(
                symbol=ticker,
                quantity=shares,
                transaction_type="BUY",
                product="MIS",  # Intraday for bracket orders
                exchange="NSE",
                squareoff=target_points,
                stoploss=stop_loss_points,
                price=0  # Market order
            )
            
            if order_id:
                logger.info(f"✅ Order executed successfully!")
                logger.info(f"   Order ID: {order_id}")
                logger.info(f"   Ticker: {ticker}")
                logger.info(f"   Quantity: {shares}")
                logger.info(f"   Entry: ₹{price:.2f}")
                logger.info(f"   Stop Loss: ₹{stop_loss_price:.2f}")
                logger.info(f"   Target: ₹{target_price:.2f}")
                
                # Mark as executed
                self.executed_today.add(ticker)
                
                return True
            else:
                logger.error(f"❌ Order execution failed")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to execute order: {e}")
            return False
    
    def run_daily_cycle(self, auto_execute: bool = False):
        """
        Run complete daily trading cycle
        
        Args:
            auto_execute: If True, execute trades automatically
        """
        logger.info("\n" + "="*100)
        logger.info("🌅 STARTING DAILY TRADING CYCLE")
        logger.info("="*100)
        logger.info(f"Mode: {'AUTO-EXECUTE' if auto_execute else 'MANUAL CONFIRMATION'}")
        logger.info(f"Capital: ₹{self.capital:,.0f}")
        logger.info(f"Max Positions: {self.max_positions}")
        logger.info(f"Min Confidence: {self.min_confidence:.0%}")
        logger.info(f"Min Return: {self.min_expected_return:.1f}%")
        
        # Get current positions
        positions = self.trader.get_positions()
        current_positions = len(positions)
        
        logger.info(f"\n📊 Current Positions: {current_positions}/{self.max_positions}")
        
        if current_positions >= self.max_positions:
            logger.warning(f"⚠️ Maximum positions reached. No new trades today.")
            return
        
        # Run bot analysis
        signals = self.run_bot_analysis()
        
        if not signals:
            logger.info("\n⏳ No signals found today")
            return
        
        # Display signals
        logger.info("\n" + "="*100)
        logger.info(f"📋 SIGNALS SUMMARY ({len(signals)} signals)")
        logger.info("="*100)
        
        for i, sig in enumerate(signals, 1):
            logger.info(f"{i}. {sig['ticker']}: ₹{sig['price']:.2f} | "
                       f"Conf: {sig['confidence']:.0%} | "
                       f"Return: +{sig['expected_return']:.1f}%")
        
        # Execute signals
        available_slots = self.max_positions - current_positions
        signals_to_execute = signals[:available_slots]
        
        logger.info(f"\n🎯 EXECUTING {len(signals_to_execute)} SIGNALS")
        logger.info("="*100)
        
        executed_count = 0
        
        for i, signal in enumerate(signals_to_execute, 1):
            logger.info(f"\nSignal {i}/{len(signals_to_execute)}")
            
            if self.execute_signal(signal, auto_execute):
                executed_count += 1
            
            # Small delay between orders
            if i < len(signals_to_execute):
                time.sleep(2)
        
        # Summary
        logger.info("\n" + "="*100)
        logger.info(f"✅ EXECUTION COMPLETE: {executed_count}/{len(signals_to_execute)} trades executed")
        logger.info("="*100)
        
        # Display current positions
        self.trader.display_positions()
        
        logger.info("\n✅ DAILY CYCLE COMPLETE")
        logger.info("="*100)


def main():
    """Main function"""
    print("="*100)
    print("🚀 NEOSTOX PAPER TRADING BOT")
    print("="*100)
    print("\n📄 Using NeoStox's built-in PAPER TRADING mode")
    print("   • Real broker API")
    print("   • Virtual money")
    print("   • Real-time prices")
    print("   • Automatic stop loss & targets")
    
    # Setup NeoStox in paper mode
    print("\n🔧 Setting up NeoStox connection...")
    trader = setup_neostox(environment="paper")
    
    if not trader:
        print("\n❌ Failed to setup NeoStox")
        print("\n📝 Setup Instructions:")
        print("1. Sign up at https://neostox.com")
        print("2. Get API key from dashboard")
        print("3. Add to .env file:")
        print("   NEOSTOX_CLIENT_ID=your_email")
        print("   NEOSTOX_API_KEY=your_api_key")
        print("4. Run: pip install neostox")
        return
    
    print("✅ NeoStox connected (PAPER MODE)")
    
    # Display account info
    trader.display_margins()
    trader.display_positions()
    
    # Configuration
    print("\n" + "="*100)
    print("⚙️ CONFIGURATION")
    print("="*100)
    
    auto_execute = input("Auto-execute trades? (yes/no): ").strip().lower() == 'yes'
    
    capital = float(input("Total capital (default 500000): ").strip() or "500000")
    max_positions = int(input("Maximum positions (default 8): ").strip() or "8")
    
    print(f"\n✅ Configuration:")
    print(f"   Auto-execute: {auto_execute}")
    print(f"   Capital: ₹{capital:,.0f}")
    print(f"   Max positions: {max_positions}")
    
    # Initialize bot
    bot = NeoStoxPaperTradingBot(
        trader=trader,
        capital=capital,
        max_positions=max_positions
    )
    
    # Run daily cycle
    bot.run_daily_cycle(auto_execute=auto_execute)
    
    print("\n✅ PAPER TRADING SESSION COMPLETE")
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
