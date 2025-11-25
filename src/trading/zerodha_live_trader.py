#!/usr/bin/env python3
"""
Zerodha Kite Live Trading Integration for NSE AlphaBot
Executes real trades based on bot signals
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from kiteconnect import KiteConnect
from kiteconnect import KiteTicker
import pandas as pd
import json
from datetime import datetime, time
import time as time_module
import logging
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('live_trading.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ZerodhaLiveTrader:
    """
    Live trading integration with Zerodha Kite
    """
    
    def __init__(self, api_key, api_secret, access_token=None):
        """
        Initialize Zerodha Kite connection
        
        Args:
            api_key: Kite API key
            api_secret: Kite API secret
            access_token: Access token (if already generated)
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.kite = KiteConnect(api_key=api_key)
        self.access_token = access_token
        
        if access_token:
            self.kite.set_access_token(access_token)
            logger.info("✅ Kite connection initialized with access token")
        else:
            logger.warning("⚠️ No access token provided. Need to generate one.")
        
        self.positions = {}
        self.orders = {}
        
    def generate_session(self, request_token):
        """
        Generate access token from request token
        
        Args:
            request_token: Request token from Kite login
            
        Returns:
            Access token
        """
        try:
            data = self.kite.generate_session(request_token, api_secret=self.api_secret)
            self.access_token = data["access_token"]
            self.kite.set_access_token(self.access_token)
            
            logger.info("✅ Access token generated successfully")
            logger.info(f"Access Token: {self.access_token}")
            logger.info("⚠️ SAVE THIS TOKEN - Valid until end of day")
            
            return self.access_token
            
        except Exception as e:
            logger.error(f"❌ Failed to generate session: {e}")
            raise
    
    def get_login_url(self):
        """Get Kite login URL"""
        login_url = self.kite.login_url()
        logger.info(f"🔗 Login URL: {login_url}")
        return login_url
    
    def get_profile(self):
        """Get user profile"""
        try:
            profile = self.kite.profile()
            logger.info(f"✅ Logged in as: {profile['user_name']} ({profile['email']})")
            return profile
        except Exception as e:
            logger.error(f"❌ Failed to get profile: {e}")
            return None
    
    def get_margins(self):
        """Get account margins"""
        try:
            margins = self.kite.margins()
            equity = margins['equity']
            
            logger.info(f"💰 Available Margin: ₹{equity['available']['live_balance']:,.2f}")
            logger.info(f"💰 Used Margin: ₹{equity['utilised']['debits']:,.2f}")
            
            return margins
        except Exception as e:
            logger.error(f"❌ Failed to get margins: {e}")
            return None
    
    def get_instrument_token(self, symbol):
        """
        Get instrument token for a symbol
        
        Args:
            symbol: Trading symbol (e.g., 'RELIANCE')
            
        Returns:
            Instrument token
        """
        try:
            # Remove .NS suffix if present
            symbol = symbol.replace('.NS', '')
            
            # Get instruments
            instruments = self.kite.instruments("NSE")
            
            # Find instrument
            for inst in instruments:
                if inst['tradingsymbol'] == symbol:
                    return inst['instrument_token']
            
            logger.warning(f"⚠️ Instrument not found: {symbol}")
            return None
            
        except Exception as e:
            logger.error(f"❌ Failed to get instrument token: {e}")
            return None
    
    def get_ltp(self, symbol):
        """
        Get Last Traded Price
        
        Args:
            symbol: Trading symbol
            
        Returns:
            LTP
        """
        try:
            symbol = symbol.replace('.NS', '')
            instrument_token = self.get_instrument_token(symbol)
            
            if not instrument_token:
                return None
            
            ltp_data = self.kite.ltp([f"NSE:{symbol}"])
            ltp = ltp_data[f"NSE:{symbol}"]['last_price']
            
            return ltp
            
        except Exception as e:
            logger.error(f"❌ Failed to get LTP for {symbol}: {e}")
            return None
    
    def place_order(self, symbol, quantity, order_type="MARKET", 
                    transaction_type="BUY", product="CNC", 
                    price=None, trigger_price=None, stoploss=None, target=None):
        """
        Place order on Zerodha
        
        Args:
            symbol: Trading symbol (e.g., 'RELIANCE')
            quantity: Number of shares
            order_type: MARKET, LIMIT, SL, SL-M
            transaction_type: BUY or SELL
            product: CNC (delivery), MIS (intraday), NRML (F&O)
            price: Limit price (for LIMIT orders)
            trigger_price: Trigger price (for SL orders)
            stoploss: Stop loss price (optional)
            target: Target price (optional)
            
        Returns:
            Order ID
        """
        try:
            symbol = symbol.replace('.NS', '')
            
            # Place main order
            order_params = {
                "exchange": "NSE",
                "tradingsymbol": symbol,
                "transaction_type": transaction_type,
                "quantity": quantity,
                "order_type": order_type,
                "product": product,
                "validity": "DAY"
            }
            
            if price:
                order_params["price"] = price
            if trigger_price:
                order_params["trigger_price"] = trigger_price
            
            order_id = self.kite.place_order(**order_params)
            
            logger.info(f"✅ Order placed: {transaction_type} {quantity} {symbol} @ {order_type}")
            logger.info(f"   Order ID: {order_id}")
            
            # Place stop loss order if specified
            if stoploss and transaction_type == "BUY":
                sl_order_id = self.place_stoploss_order(symbol, quantity, stoploss)
                logger.info(f"   Stop Loss Order ID: {sl_order_id}")
            
            # Place target order if specified
            if target and transaction_type == "BUY":
                target_order_id = self.place_target_order(symbol, quantity, target)
                logger.info(f"   Target Order ID: {target_order_id}")
            
            return order_id
            
        except Exception as e:
            logger.error(f"❌ Failed to place order: {e}")
            return None
    
    def place_stoploss_order(self, symbol, quantity, stoploss_price):
        """Place stop loss order"""
        try:
            symbol = symbol.replace('.NS', '')
            
            order_id = self.kite.place_order(
                exchange="NSE",
                tradingsymbol=symbol,
                transaction_type="SELL",
                quantity=quantity,
                order_type="SL",
                product="CNC",
                price=stoploss_price,
                trigger_price=stoploss_price,
                validity="DAY"
            )
            
            logger.info(f"✅ Stop Loss placed: SELL {quantity} {symbol} @ ₹{stoploss_price}")
            return order_id
            
        except Exception as e:
            logger.error(f"❌ Failed to place stop loss: {e}")
            return None
    
    def place_target_order(self, symbol, quantity, target_price):
        """Place target order"""
        try:
            symbol = symbol.replace('.NS', '')
            
            order_id = self.kite.place_order(
                exchange="NSE",
                tradingsymbol=symbol,
                transaction_type="SELL",
                quantity=quantity,
                order_type="LIMIT",
                product="CNC",
                price=target_price,
                validity="DAY"
            )
            
            logger.info(f"✅ Target placed: SELL {quantity} {symbol} @ ₹{target_price}")
            return order_id
            
        except Exception as e:
            logger.error(f"❌ Failed to place target: {e}")
            return None
    
    def modify_order(self, order_id, quantity=None, price=None, order_type=None):
        """Modify existing order"""
        try:
            params = {}
            if quantity:
                params["quantity"] = quantity
            if price:
                params["price"] = price
            if order_type:
                params["order_type"] = order_type
            
            self.kite.modify_order(order_id, **params)
            logger.info(f"✅ Order modified: {order_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to modify order: {e}")
            return False
    
    def cancel_order(self, order_id):
        """Cancel order"""
        try:
            self.kite.cancel_order(order_id)
            logger.info(f"✅ Order cancelled: {order_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to cancel order: {e}")
            return False
    
    def get_orders(self):
        """Get all orders"""
        try:
            orders = self.kite.orders()
            return orders
        except Exception as e:
            logger.error(f"❌ Failed to get orders: {e}")
            return []
    
    def get_positions(self):
        """Get current positions"""
        try:
            positions = self.kite.positions()
            return positions
        except Exception as e:
            logger.error(f"❌ Failed to get positions: {e}")
            return {}
    
    def get_holdings(self):
        """Get holdings"""
        try:
            holdings = self.kite.holdings()
            return holdings
        except Exception as e:
            logger.error(f"❌ Failed to get holdings: {e}")
            return []
    
    def execute_bot_signal(self, signal):
        """
        Execute trade based on bot signal
        
        Args:
            signal: Dict with ticker, price, shares, confidence, expected_return, etc.
            
        Returns:
            Order ID
        """
        try:
            ticker = signal['ticker'].replace('.NS', '')
            shares = signal['shares']
            price = signal['price']
            confidence = signal['confidence']
            expected_return = signal['expected_return']
            
            logger.info(f"\n{'='*80}")
            logger.info(f"🎯 EXECUTING BOT SIGNAL")
            logger.info(f"{'='*80}")
            logger.info(f"Ticker: {ticker}")
            logger.info(f"Price: ₹{price:.2f}")
            logger.info(f"Shares: {shares}")
            logger.info(f"Confidence: {confidence:.0%}")
            logger.info(f"Expected Return: +{expected_return:.1f}%")
            
            # Calculate stop loss and target
            stoploss = price * 0.97  # 3% stop loss
            target = price * (1 + expected_return/100)
            
            logger.info(f"Stop Loss: ₹{stoploss:.2f} (-3%)")
            logger.info(f"Target: ₹{target:.2f} (+{expected_return:.1f}%)")
            
            # Place order
            order_id = self.place_order(
                symbol=ticker,
                quantity=shares,
                order_type="MARKET",
                transaction_type="BUY",
                product="CNC",
                stoploss=stoploss,
                target=target
            )
            
            if order_id:
                logger.info(f"✅ Trade executed successfully!")
                logger.info(f"{'='*80}\n")
                return order_id
            else:
                logger.error(f"❌ Trade execution failed!")
                logger.info(f"{'='*80}\n")
                return None
                
        except Exception as e:
            logger.error(f"❌ Failed to execute bot signal: {e}")
            return None
    
    def is_market_open(self):
        """Check if market is open"""
        now = datetime.now()
        
        # Check if weekday (Monday=0, Sunday=6)
        if now.weekday() >= 5:  # Saturday or Sunday
            return False
        
        # Check market hours (9:15 AM to 3:30 PM)
        market_open = time(9, 15)
        market_close = time(15, 30)
        current_time = now.time()
        
        return market_open <= current_time <= market_close
    
    def get_daily_pnl(self):
        """Calculate daily P&L"""
        try:
            positions = self.get_positions()
            
            if not positions or 'day' not in positions:
                return 0
            
            total_pnl = sum([pos['pnl'] for pos in positions['day']])
            logger.info(f"📊 Daily P&L: ₹{total_pnl:,.2f}")
            
            return total_pnl
            
        except Exception as e:
            logger.error(f"❌ Failed to calculate P&L: {e}")
            return 0


def setup_zerodha():
    """
    Interactive setup for Zerodha Kite
    """
    print("="*80)
    print("🔧 ZERODHA KITE SETUP")
    print("="*80)
    
    # Check for existing credentials
    api_key = os.getenv('KITE_API_KEY')
    api_secret = os.getenv('KITE_API_SECRET')
    access_token = os.getenv('KITE_ACCESS_TOKEN')
    
    if not api_key or not api_secret:
        print("\n⚠️ Kite API credentials not found in .env file")
        print("\n📝 To get API credentials:")
        print("1. Go to https://kite.trade/")
        print("2. Login to your account")
        print("3. Go to https://developers.kite.trade/apps")
        print("4. Create a new app")
        print("5. Copy API Key and API Secret")
        print("\nAdd to .env file:")
        print("KITE_API_KEY=your_api_key")
        print("KITE_API_SECRET=your_api_secret")
        return None
    
    print(f"\n✅ API Key found: {api_key[:10]}...")
    
    # Initialize trader
    trader = ZerodhaLiveTrader(api_key, api_secret, access_token)
    
    # Check if access token is valid
    if access_token:
        try:
            profile = trader.get_profile()
            if profile:
                print(f"✅ Logged in as: {profile['user_name']}")
                return trader
        except:
            print("⚠️ Access token expired or invalid")
    
    # Generate new access token
    print("\n🔐 Generating new access token...")
    print("\nSteps:")
    print("1. Click the login URL below")
    print("2. Login to Kite")
    print("3. Copy the 'request_token' from the redirect URL")
    print("4. Paste it here")
    
    login_url = trader.get_login_url()
    print(f"\n🔗 Login URL:\n{login_url}\n")
    
    request_token = input("Enter request_token: ").strip()
    
    if request_token:
        access_token = trader.generate_session(request_token)
        print(f"\n✅ Access Token: {access_token}")
        print("\n⚠️ Add this to your .env file:")
        print(f"KITE_ACCESS_TOKEN={access_token}")
        print("\n⚠️ Token valid until end of day. Generate new token tomorrow.")
        
        return trader
    else:
        print("❌ No request token provided")
        return None


# === TESTING ===
if __name__ == "__main__":
    print("="*80)
    print("🧪 ZERODHA KITE LIVE TRADER TEST")
    print("="*80)
    
    # Setup
    trader = setup_zerodha()
    
    if not trader:
        print("\n❌ Setup failed. Please configure API credentials.")
        sys.exit(1)
    
    # Test connection
    print("\n" + "="*80)
    print("📊 ACCOUNT INFORMATION")
    print("="*80)
    
    profile = trader.get_profile()
    margins = trader.get_margins()
    
    # Test market status
    print("\n" + "="*80)
    print("🕐 MARKET STATUS")
    print("="*80)
    
    if trader.is_market_open():
        print("✅ Market is OPEN")
    else:
        print("⏸️ Market is CLOSED")
    
    # Test LTP
    print("\n" + "="*80)
    print("💹 LIVE PRICES")
    print("="*80)
    
    test_symbols = ['RELIANCE', 'TCS', 'INFY']
    for symbol in test_symbols:
        ltp = trader.get_ltp(symbol)
        if ltp:
            print(f"{symbol}: ₹{ltp:.2f}")
    
    # Test positions
    print("\n" + "="*80)
    print("📈 CURRENT POSITIONS")
    print("="*80)
    
    positions = trader.get_positions()
    if positions and 'net' in positions and positions['net']:
        for pos in positions['net']:
            print(f"{pos['tradingsymbol']}: {pos['quantity']} shares, P&L: ₹{pos['pnl']:,.2f}")
    else:
        print("No open positions")
    
    # Test holdings
    print("\n" + "="*80)
    print("💼 HOLDINGS")
    print("="*80)
    
    holdings = trader.get_holdings()
    if holdings:
        for holding in holdings:
            print(f"{holding['tradingsymbol']}: {holding['quantity']} shares, P&L: ₹{holding['pnl']:,.2f}")
    else:
        print("No holdings")
    
    print("\n" + "="*80)
    print("✅ All tests complete!")
    print("="*80)
    
    # Ask if user wants to place a test order
    print("\n⚠️ WARNING: Next step will place a REAL order!")
    response = input("Do you want to place a test order? (yes/no): ").strip().lower()
    
    if response == 'yes':
        print("\n📝 Test Order Details:")
        symbol = input("Enter symbol (e.g., RELIANCE): ").strip()
        quantity = int(input("Enter quantity: "))
        
        print(f"\n🎯 Placing MARKET order: BUY {quantity} {symbol}")
        confirm = input("Confirm? (yes/no): ").strip().lower()
        
        if confirm == 'yes':
            order_id = trader.place_order(
                symbol=symbol,
                quantity=quantity,
                order_type="MARKET",
                transaction_type="BUY",
                product="CNC"
            )
            
            if order_id:
                print(f"\n✅ Order placed successfully!")
                print(f"Order ID: {order_id}")
            else:
                print(f"\n❌ Order failed!")
        else:
            print("❌ Order cancelled")
    else:
        print("✅ Test complete without placing order")
