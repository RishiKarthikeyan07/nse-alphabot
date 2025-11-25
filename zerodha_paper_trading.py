#!/usr/bin/env python3
"""
Zerodha Paper Trading System
Uses real Zerodha prices but executes virtual trades (no real money)
Perfect for testing before going live!
"""

import sys
import os
sys.path.append('src')

from trading.zerodha_live_trader import ZerodhaLiveTrader, setup_zerodha
from bot.nse_alphabot_ultimate import ELITE_STOCKS, get_stock_data, analyze_stock
import json
from datetime import datetime
import time
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('zerodha_paper_trading.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ZerodhaPaperTrader:
    """
    Paper trading with real Zerodha prices
    """
    
    def __init__(self, trader, capital=500000, max_positions=8):
        """
        Initialize paper trader
        
        Args:
            trader: ZerodhaLiveTrader instance (for real prices)
            capital: Virtual capital
            max_positions: Maximum positions
        """
        self.trader = trader
        self.initial_capital = capital
        self.available_capital = capital
        self.max_positions = max_positions
        
        # Virtual portfolio
        self.positions = {}  # {ticker: {quantity, buy_price, buy_date, stop_loss, target}}
        self.closed_trades = []  # List of completed trades
        self.orders = []  # List of all orders
        
        # Performance tracking
        self.total_trades = 0
        self.winning_trades = 0
        self.losing_trades = 0
        self.total_pnl = 0
        
        # Load existing data if available
        self.load_portfolio()
    
    def save_portfolio(self):
        """Save portfolio to file"""
        data = {
            'initial_capital': self.initial_capital,
            'available_capital': self.available_capital,
            'positions': self.positions,
            'closed_trades': self.closed_trades,
            'orders': self.orders,
            'total_trades': self.total_trades,
            'winning_trades': self.winning_trades,
            'losing_trades': self.losing_trades,
            'total_pnl': self.total_pnl,
            'last_updated': datetime.now().isoformat()
        }
        
        with open('zerodha_paper_portfolio.json', 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info("💾 Portfolio saved")
    
    def load_portfolio(self):
        """Load portfolio from file"""
        try:
            if Path('zerodha_paper_portfolio.json').exists():
                with open('zerodha_paper_portfolio.json', 'r') as f:
                    data = json.load(f)
                
                self.initial_capital = data.get('initial_capital', self.initial_capital)
                self.available_capital = data.get('available_capital', self.available_capital)
                self.positions = data.get('positions', {})
                self.closed_trades = data.get('closed_trades', [])
                self.orders = data.get('orders', [])
                self.total_trades = data.get('total_trades', 0)
                self.winning_trades = data.get('winning_trades', 0)
                self.losing_trades = data.get('losing_trades', 0)
                self.total_pnl = data.get('total_pnl', 0)
                
                logger.info("📂 Portfolio loaded from file")
        except Exception as e:
            logger.warning(f"⚠️ Could not load portfolio: {e}")
    
    def get_real_price(self, symbol):
        """Get real price from Zerodha"""
        try:
            ltp = self.trader.get_ltp(symbol)
            return ltp
        except Exception as e:
            logger.error(f"❌ Failed to get price for {symbol}: {e}")
            return None
    
    def place_paper_order(self, symbol, quantity, order_type="BUY", 
                          price=None, stop_loss=None, target=None):
        """
        Place virtual order
        
        Args:
            symbol: Trading symbol
            quantity: Number of shares
            order_type: BUY or SELL
            price: Entry price (if None, uses current LTP)
            stop_loss: Stop loss price
            target: Target price
            
        Returns:
            Order ID (virtual)
        """
        try:
            symbol = symbol.replace('.NS', '')
            
            # Get real price from Zerodha
            if price is None:
                price = self.get_real_price(symbol)
                if price is None:
                    logger.error(f"❌ Could not get price for {symbol}")
                    return None
            
            order_value = price * quantity
            
            if order_type == "BUY":
                # Check available capital
                if order_value > self.available_capital:
                    logger.error(f"❌ Insufficient capital: Need ₹{order_value:,.0f}, Have ₹{self.available_capital:,.0f}")
                    return None
                
                # Check position limits
                if len(self.positions) >= self.max_positions:
                    logger.error(f"❌ Maximum positions reached: {self.max_positions}")
                    return None
                
                # Execute virtual buy
                order_id = f"PAPER_{datetime.now().strftime('%Y%m%d%H%M%S')}_{symbol}"
                
                self.positions[symbol] = {
                    'quantity': quantity,
                    'buy_price': price,
                    'buy_date': datetime.now().isoformat(),
                    'stop_loss': stop_loss or price * 0.97,
                    'target': target or price * 1.05,
                    'order_id': order_id
                }
                
                self.available_capital -= order_value
                
                self.orders.append({
                    'order_id': order_id,
                    'symbol': symbol,
                    'type': 'BUY',
                    'quantity': quantity,
                    'price': price,
                    'value': order_value,
                    'timestamp': datetime.now().isoformat(),
                    'status': 'EXECUTED'
                })
                
                logger.info(f"✅ PAPER BUY: {quantity} {symbol} @ ₹{price:.2f}")
                logger.info(f"   Order Value: ₹{order_value:,.0f}")
                logger.info(f"   Stop Loss: ₹{self.positions[symbol]['stop_loss']:.2f}")
                logger.info(f"   Target: ₹{self.positions[symbol]['target']:.2f}")
                logger.info(f"   Available Capital: ₹{self.available_capital:,.0f}")
                
                self.save_portfolio()
                return order_id
                
            elif order_type == "SELL":
                # Check if position exists
                if symbol not in self.positions:
                    logger.error(f"❌ No position found for {symbol}")
                    return None
                
                position = self.positions[symbol]
                
                # Execute virtual sell
                order_id = f"PAPER_{datetime.now().strftime('%Y%m%d%H%M%S')}_{symbol}_SELL"
                
                sell_value = price * quantity
                buy_value = position['buy_price'] * position['quantity']
                pnl = sell_value - buy_value
                pnl_pct = (pnl / buy_value) * 100
                
                # Update capital
                self.available_capital += sell_value
                self.total_pnl += pnl
                
                # Record closed trade
                self.closed_trades.append({
                    'symbol': symbol,
                    'quantity': quantity,
                    'buy_price': position['buy_price'],
                    'sell_price': price,
                    'buy_date': position['buy_date'],
                    'sell_date': datetime.now().isoformat(),
                    'pnl': pnl,
                    'pnl_pct': pnl_pct,
                    'order_id': order_id
                })
                
                self.orders.append({
                    'order_id': order_id,
                    'symbol': symbol,
                    'type': 'SELL',
                    'quantity': quantity,
                    'price': price,
                    'value': sell_value,
                    'pnl': pnl,
                    'pnl_pct': pnl_pct,
                    'timestamp': datetime.now().isoformat(),
                    'status': 'EXECUTED'
                })
                
                # Update stats
                self.total_trades += 1
                if pnl > 0:
                    self.winning_trades += 1
                else:
                    self.losing_trades += 1
                
                # Remove position
                del self.positions[symbol]
                
                logger.info(f"✅ PAPER SELL: {quantity} {symbol} @ ₹{price:.2f}")
                logger.info(f"   P&L: ₹{pnl:,.2f} ({pnl_pct:+.2f}%)")
                logger.info(f"   Available Capital: ₹{self.available_capital:,.0f}")
                
                self.save_portfolio()
                return order_id
                
        except Exception as e:
            logger.error(f"❌ Failed to place paper order: {e}")
            return None
    
    def update_positions(self):
        """Update all positions with current prices and check stop loss/targets"""
        if not self.positions:
            return
        
        logger.info("\n" + "="*100)
        logger.info("📊 UPDATING POSITIONS WITH REAL ZERODHA PRICES")
        logger.info("="*100)
        
        positions_to_close = []
        
        for symbol, position in self.positions.items():
            try:
                # Get real current price from Zerodha
                current_price = self.get_real_price(symbol)
                
                if current_price is None:
                    logger.warning(f"⚠️ Could not get price for {symbol}")
                    continue
                
                quantity = position['quantity']
                buy_price = position['buy_price']
                stop_loss = position['stop_loss']
                target = position['target']
                
                current_value = current_price * quantity
                buy_value = buy_price * quantity
                pnl = current_value - buy_value
                pnl_pct = (pnl / buy_value) * 100
                
                logger.info(f"\n{symbol}:")
                logger.info(f"  Quantity: {quantity}")
                logger.info(f"  Buy Price: ₹{buy_price:.2f}")
                logger.info(f"  Current Price: ₹{current_price:.2f} (Real Zerodha)")
                logger.info(f"  P&L: ₹{pnl:,.2f} ({pnl_pct:+.2f}%)")
                logger.info(f"  Stop Loss: ₹{stop_loss:.2f}")
                logger.info(f"  Target: ₹{target:.2f}")
                
                # Check stop loss
                if current_price <= stop_loss:
                    logger.warning(f"🛑 STOP LOSS HIT for {symbol}!")
                    positions_to_close.append((symbol, current_price, "STOP_LOSS"))
                
                # Check target
                elif current_price >= target:
                    logger.info(f"🎯 TARGET HIT for {symbol}!")
                    positions_to_close.append((symbol, current_price, "TARGET"))
                    
            except Exception as e:
                logger.error(f"❌ Error updating {symbol}: {e}")
        
        # Close positions that hit stop loss or target
        for symbol, price, reason in positions_to_close:
            logger.info(f"\n🔄 Auto-closing {symbol} ({reason})")
            self.place_paper_order(symbol, self.positions[symbol]['quantity'], 
                                  order_type="SELL", price=price)
    
    def get_portfolio_value(self):
        """Calculate total portfolio value"""
        total_value = self.available_capital
        
        for symbol, position in self.positions.items():
            current_price = self.get_real_price(symbol)
            if current_price:
                total_value += current_price * position['quantity']
        
        return total_value
    
    def get_performance_report(self):
        """Generate performance report"""
        portfolio_value = self.get_portfolio_value()
        total_return = portfolio_value - self.initial_capital
        total_return_pct = (total_return / self.initial_capital) * 100
        
        win_rate = (self.winning_trades / self.total_trades * 100) if self.total_trades > 0 else 0
        
        logger.info("\n" + "="*100)
        logger.info("📊 PAPER TRADING PERFORMANCE REPORT")
        logger.info("="*100)
        logger.info(f"\n💰 Capital:")
        logger.info(f"  Initial: ₹{self.initial_capital:,.0f}")
        logger.info(f"  Available: ₹{self.available_capital:,.0f}")
        logger.info(f"  Portfolio Value: ₹{portfolio_value:,.0f}")
        logger.info(f"  Total Return: ₹{total_return:,.0f} ({total_return_pct:+.2f}%)")
        
        logger.info(f"\n📈 Trading Stats:")
        logger.info(f"  Total Trades: {self.total_trades}")
        logger.info(f"  Winning Trades: {self.winning_trades}")
        logger.info(f"  Losing Trades: {self.losing_trades}")
        logger.info(f"  Win Rate: {win_rate:.1f}%")
        logger.info(f"  Open Positions: {len(self.positions)}")
        
        logger.info(f"\n💵 P&L:")
        logger.info(f"  Realized P&L: ₹{self.total_pnl:,.2f}")
        
        if self.closed_trades:
            avg_win = sum([t['pnl'] for t in self.closed_trades if t['pnl'] > 0]) / self.winning_trades if self.winning_trades > 0 else 0
            avg_loss = sum([t['pnl'] for t in self.closed_trades if t['pnl'] < 0]) / self.losing_trades if self.losing_trades > 0 else 0
            
            logger.info(f"  Average Win: ₹{avg_win:,.2f}")
            logger.info(f"  Average Loss: ₹{avg_loss:,.2f}")
            
            if avg_loss != 0:
                risk_reward = abs(avg_win / avg_loss)
                logger.info(f"  Risk-Reward Ratio: {risk_reward:.2f}:1")
        
        logger.info("="*100)
        
        return {
            'portfolio_value': portfolio_value,
            'total_return': total_return,
            'total_return_pct': total_return_pct,
            'win_rate': win_rate,
            'total_trades': self.total_trades
        }


def main():
    """Main function"""
    print("="*100)
    print("📄 ZERODHA PAPER TRADING (Virtual Money, Real Prices)")
    print("="*100)
    
    # Setup Zerodha (for real prices)
    print("\n🔧 Setting up Zerodha connection (for real prices)...")
    trader = setup_zerodha()
    
    if not trader:
        print("\n❌ Failed to setup Zerodha. Please check your credentials.")
        print("⚠️ You need Zerodha API access to get real prices for paper trading.")
        return
    
    print("\n✅ Zerodha connection established! (Using real prices)")
    
    # Initialize paper trader
    capital = float(input("\nVirtual capital (default 500000): ").strip() or "500000")
    max_positions = int(input("Maximum positions (default 8): ").strip() or "8")
    
    paper_trader = ZerodhaPaperTrader(trader, capital=capital, max_positions=max_positions)
    
    print(f"\n✅ Paper Trading Initialized:")
    print(f"   Virtual Capital: ₹{capital:,.0f}")
    print(f"   Max Positions: {max_positions}")
    print(f"   Prices: Real-time from Zerodha")
    print(f"   Trades: Virtual (no real money)")
    
    # Main menu
    while True:
        print("\n" + "="*100)
        print("📋 MENU")
        print("="*100)
        print("1. Run Bot & Get Signals")
        print("2. Execute Signal (Manual)")
        print("3. Update Positions (Check Stop Loss/Targets)")
        print("4. View Positions")
        print("5. View Performance Report")
        print("6. Close Position")
        print("7. Exit")
        
        choice = input("\nChoose option: ").strip()
        
        if choice == '1':
            # Run bot
            print("\n🤖 Running NSE AlphaBot...")
            signals = []
            
            for ticker in ELITE_STOCKS[:20]:  # Test with 20 stocks
                try:
                    result = analyze_stock(ticker)
                    if result and result.get('signal') == 'BUY':
                        signals.append(result)
                except:
                    continue
            
            signals.sort(key=lambda x: x['confidence'], reverse=True)
            
            print(f"\n✅ Found {len(signals)} BUY signals")
            
            if signals:
                print("\n📋 SIGNALS:")
                for i, sig in enumerate(signals, 1):
                    print(f"{i}. {sig['ticker']}: ₹{sig['price']:.2f} | "
                          f"Conf: {sig['confidence']:.0%} | Return: +{sig['expected_return']:.1f}%")
        
        elif choice == '2':
            # Execute signal
            ticker = input("\nEnter ticker (e.g., RELIANCE): ").strip().upper()
            
            # Get real price from Zerodha
            price = paper_trader.get_real_price(ticker)
            if not price:
                print(f"❌ Could not get price for {ticker}")
                continue
            
            print(f"Current Price (Real Zerodha): ₹{price:.2f}")
            
            quantity = int(input("Enter quantity: "))
            
            stop_loss = price * 0.97
            target = price * 1.05
            
            print(f"\nOrder Summary:")
            print(f"  Ticker: {ticker}")
            print(f"  Quantity: {quantity}")
            print(f"  Price: ₹{price:.2f} (Real Zerodha)")
            print(f"  Value: ₹{price * quantity:,.0f}")
            print(f"  Stop Loss: ₹{stop_loss:.2f} (-3%)")
            print(f"  Target: ₹{target:.2f} (+5%)")
            
            confirm = input("\nExecute paper trade? (yes/no): ").strip().lower()
            
            if confirm == 'yes':
                paper_trader.place_paper_order(
                    ticker, quantity, "BUY", price, stop_loss, target
                )
        
        elif choice == '3':
            # Update positions
            paper_trader.update_positions()
        
        elif choice == '4':
            # View positions
            if not paper_trader.positions:
                print("\n⏳ No open positions")
            else:
                print("\n📊 OPEN POSITIONS:")
                for symbol, pos in paper_trader.positions.items():
                    current_price = paper_trader.get_real_price(symbol)
                    if current_price:
                        pnl = (current_price - pos['buy_price']) * pos['quantity']
                        pnl_pct = ((current_price - pos['buy_price']) / pos['buy_price']) * 100
                        print(f"\n{symbol}:")
                        print(f"  Quantity: {pos['quantity']}")
                        print(f"  Buy Price: ₹{pos['buy_price']:.2f}")
                        print(f"  Current Price: ₹{current_price:.2f} (Real Zerodha)")
                        print(f"  P&L: ₹{pnl:,.2f} ({pnl_pct:+.2f}%)")
        
        elif choice == '5':
            # Performance report
            paper_trader.get_performance_report()
        
        elif choice == '6':
            # Close position
            if not paper_trader.positions:
                print("\n⏳ No open positions")
                continue
            
            print("\nOpen Positions:")
            for i, symbol in enumerate(paper_trader.positions.keys(), 1):
                print(f"{i}. {symbol}")
            
            symbol = input("\nEnter ticker to close: ").strip().upper()
            
            if symbol in paper_trader.positions:
                current_price = paper_trader.get_real_price(symbol)
                if current_price:
                    quantity = paper_trader.positions[symbol]['quantity']
                    paper_trader.place_paper_order(symbol, quantity, "SELL", current_price)
            else:
                print(f"❌ No position found for {symbol}")
        
        elif choice == '7':
            print("\n👋 Exiting paper trading...")
            break


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n🛑 Interrupted by user")
    except Exception as e:
        logger.error(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
