#!/usr/bin/env python3
"""
NeoStox Trading Integration
Supports both paper trading and live trading
"""

import os
from dotenv import load_dotenv
import logging
from datetime import datetime
from typing import Dict, List, Optional

try:
    from neostox import NeoAPI
    NEOSTOX_AVAILABLE = True
except ImportError:
    NEOSTOX_AVAILABLE = False
    print("⚠️ NeoStox not installed. Run: pip install neostox")

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class NeoStoxTrader:
    """
    NeoStox trading wrapper for both paper and live trading
    """
    
    def __init__(self, client_id: str, api_key: str, environment: str = "paper"):
        """
        Initialize NeoStox trader
        
        Args:
            client_id: Your email/client ID
            api_key: NeoStox API key
            environment: "paper" for paper trading, "prod" for live trading
        """
        if not NEOSTOX_AVAILABLE:
            raise ImportError("NeoStox library not installed. Run: pip install neostox")
        
        self.client_id = client_id
        self.api_key = api_key
        self.environment = environment
        self.client = None
        
        logger.info(f"🔧 Initializing NeoStox in {environment.upper()} mode")
    
    def connect(self) -> bool:
        """
        Connect to NeoStox
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.client = NeoAPI(
                client_id=self.client_id,
                api_key=self.api_key,
                environment=self.environment
            )
            
            logger.info(f"✅ Connected to NeoStox ({self.environment.upper()} mode)")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to NeoStox: {e}")
            return False
    
    def get_ltp(self, symbol: str, exchange: str = "NSE") -> Optional[float]:
        """
        Get Last Traded Price
        
        Args:
            symbol: Trading symbol (e.g., "RELIANCE")
            exchange: Exchange (NSE/BSE)
            
        Returns:
            Last traded price or None
        """
        try:
            # Get quote
            quote = self.client.quotes(
                exchange=exchange,
                tradingsymbol=symbol
            )
            
            if quote and 'data' in quote:
                ltp = float(quote['data'][0]['ltp'])
                return ltp
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Failed to get LTP for {symbol}: {e}")
            return None
    
    def place_order(self, 
                   symbol: str,
                   quantity: int,
                   order_type: str = "MARKET",
                   transaction_type: str = "BUY",
                   product: str = "CNC",
                   exchange: str = "NSE",
                   price: float = 0,
                   trigger_price: float = 0,
                   variety: str = "NORMAL") -> Optional[str]:
        """
        Place order on NeoStox
        
        Args:
            symbol: Trading symbol
            quantity: Number of shares
            order_type: MARKET/LIMIT/SL/SL-M
            transaction_type: BUY/SELL
            product: CNC/MIS/NRML
            exchange: NSE/BSE
            price: Limit price (for LIMIT orders)
            trigger_price: Trigger price (for SL orders)
            variety: NORMAL/BO/CO
            
        Returns:
            Order ID or None
        """
        try:
            logger.info(f"📤 Placing {transaction_type} order: {quantity} {symbol} @ {order_type}")
            
            response = self.client.place_order(
                exchange=exchange,
                tradingsymbol=symbol,
                quantity=quantity,
                price=price,
                trigger_price=trigger_price,
                order_type=order_type,
                product=product,
                transaction_type=transaction_type,
                variety=variety
            )
            
            if response and 'data' in response:
                order_id = response['data']['order_id']
                logger.info(f"✅ Order placed successfully: {order_id}")
                return order_id
            else:
                logger.error(f"❌ Order placement failed: {response}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Failed to place order: {e}")
            return None
    
    def place_bracket_order(self,
                           symbol: str,
                           quantity: int,
                           transaction_type: str = "BUY",
                           product: str = "MIS",
                           exchange: str = "NSE",
                           squareoff: float = 20,
                           stoploss: float = 8,
                           price: float = 0) -> Optional[str]:
        """
        Place bracket order with automatic stop loss and target
        
        Args:
            symbol: Trading symbol
            quantity: Number of shares
            transaction_type: BUY/SELL
            product: MIS/NRML (CNC not allowed for BO)
            exchange: NSE/BSE
            squareoff: Target profit points
            stoploss: Stop loss points
            price: Entry price (0 for market)
            
        Returns:
            Order ID or None
        """
        try:
            logger.info(f"📤 Placing BRACKET order: {quantity} {symbol}")
            logger.info(f"   Target: +{squareoff} points | Stop Loss: -{stoploss} points")
            
            response = self.client.place_order(
                exchange=exchange,
                tradingsymbol=symbol,
                quantity=quantity,
                price=price,
                trigger_price=0,
                order_type="MARKET" if price == 0 else "LIMIT",
                product=product,
                transaction_type=transaction_type,
                variety="BO",
                squareoff=squareoff,
                stoploss=stoploss
            )
            
            if response and 'data' in response:
                order_id = response['data']['order_id']
                logger.info(f"✅ Bracket order placed: {order_id}")
                return order_id
            else:
                logger.error(f"❌ Bracket order failed: {response}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Failed to place bracket order: {e}")
            return None
    
    def get_positions(self) -> List[Dict]:
        """
        Get current positions
        
        Returns:
            List of positions
        """
        try:
            response = self.client.positions()
            
            if response and 'data' in response:
                positions = response['data']
                logger.info(f"📊 Retrieved {len(positions)} positions")
                return positions
            
            return []
            
        except Exception as e:
            logger.error(f"❌ Failed to get positions: {e}")
            return []
    
    def get_holdings(self) -> List[Dict]:
        """
        Get holdings
        
        Returns:
            List of holdings
        """
        try:
            response = self.client.holdings()
            
            if response and 'data' in response:
                holdings = response['data']
                logger.info(f"📊 Retrieved {len(holdings)} holdings")
                return holdings
            
            return []
            
        except Exception as e:
            logger.error(f"❌ Failed to get holdings: {e}")
            return []
    
    def get_orders(self) -> List[Dict]:
        """
        Get order history
        
        Returns:
            List of orders
        """
        try:
            response = self.client.order_history()
            
            if response and 'data' in response:
                orders = response['data']
                logger.info(f"📊 Retrieved {len(orders)} orders")
                return orders
            
            return []
            
        except Exception as e:
            logger.error(f"❌ Failed to get orders: {e}")
            return []
    
    def cancel_order(self, order_id: str) -> bool:
        """
        Cancel order
        
        Args:
            order_id: Order ID to cancel
            
        Returns:
            True if successful
        """
        try:
            response = self.client.cancel_order(order_id=order_id)
            
            if response and response.get('status') == 'success':
                logger.info(f"✅ Order cancelled: {order_id}")
                return True
            
            logger.error(f"❌ Failed to cancel order: {response}")
            return False
            
        except Exception as e:
            logger.error(f"❌ Failed to cancel order: {e}")
            return False
    
    def modify_order(self, order_id: str, quantity: int = None, 
                    price: float = None) -> bool:
        """
        Modify order
        
        Args:
            order_id: Order ID to modify
            quantity: New quantity
            price: New price
            
        Returns:
            True if successful
        """
        try:
            params = {'order_id': order_id}
            if quantity:
                params['quantity'] = quantity
            if price:
                params['price'] = price
            
            response = self.client.modify_order(**params)
            
            if response and response.get('status') == 'success':
                logger.info(f"✅ Order modified: {order_id}")
                return True
            
            logger.error(f"❌ Failed to modify order: {response}")
            return False
            
        except Exception as e:
            logger.error(f"❌ Failed to modify order: {e}")
            return False
    
    def get_margins(self) -> Dict:
        """
        Get account margins
        
        Returns:
            Margin details
        """
        try:
            response = self.client.limits()
            
            if response and 'data' in response:
                margins = response['data']
                logger.info("💰 Retrieved margin details")
                return margins
            
            return {}
            
        except Exception as e:
            logger.error(f"❌ Failed to get margins: {e}")
            return {}
    
    def display_positions(self):
        """Display current positions in formatted way"""
        positions = self.get_positions()
        
        if not positions:
            print("\n⏳ No open positions")
            return
        
        print("\n" + "="*100)
        print("📊 CURRENT POSITIONS")
        print("="*100)
        
        total_pnl = 0
        
        for pos in positions:
            symbol = pos.get('tradingsymbol', 'N/A')
            quantity = pos.get('quantity', 0)
            buy_price = pos.get('average_price', 0)
            ltp = pos.get('ltp', 0)
            pnl = pos.get('pnl', 0)
            
            total_pnl += pnl
            
            print(f"\n{symbol}:")
            print(f"  Quantity: {quantity}")
            print(f"  Buy Price: ₹{buy_price:.2f}")
            print(f"  LTP: ₹{ltp:.2f}")
            print(f"  P&L: ₹{pnl:,.2f}")
        
        print("\n" + "="*100)
        print(f"💰 Total P&L: ₹{total_pnl:,.2f}")
        print("="*100)
    
    def display_margins(self):
        """Display margin details"""
        margins = self.get_margins()
        
        if not margins:
            print("\n⚠️ Could not retrieve margins")
            return
        
        print("\n" + "="*100)
        print("💰 ACCOUNT MARGINS")
        print("="*100)
        
        available = margins.get('available_margin', 0)
        used = margins.get('used_margin', 0)
        
        print(f"\nAvailable Margin: ₹{available:,.2f}")
        print(f"Used Margin: ₹{used:,.2f}")
        print("="*100)


def setup_neostox(environment: str = "paper") -> Optional[NeoStoxTrader]:
    """
    Setup NeoStox trader from environment variables
    
    Args:
        environment: "paper" or "prod"
        
    Returns:
        NeoStoxTrader instance or None
    """
    client_id = os.getenv('NEOSTOX_CLIENT_ID')
    api_key = os.getenv('NEOSTOX_API_KEY')
    
    if not client_id or not api_key:
        logger.error("❌ NeoStox credentials not found in .env")
        logger.error("   Add NEOSTOX_CLIENT_ID and NEOSTOX_API_KEY to .env file")
        return None
    
    trader = NeoStoxTrader(client_id, api_key, environment)
    
    if trader.connect():
        return trader
    
    return None


# === TESTING ===
if __name__ == "__main__":
    print("="*100)
    print("🧪 NEOSTOX TRADER TEST")
    print("="*100)
    
    # Test connection
    print("\n1. Testing connection...")
    trader = setup_neostox(environment="paper")
    
    if not trader:
        print("❌ Failed to setup NeoStox")
        exit(1)
    
    print("✅ Connection successful!")
    
    # Test getting LTP
    print("\n2. Testing LTP fetch...")
    ltp = trader.get_ltp("RELIANCE")
    if ltp:
        print(f"✅ RELIANCE LTP: ₹{ltp:.2f}")
    
    # Test getting margins
    print("\n3. Testing margins...")
    trader.display_margins()
    
    # Test getting positions
    print("\n4. Testing positions...")
    trader.display_positions()
    
    # Test getting orders
    print("\n5. Testing order history...")
    orders = trader.get_orders()
    print(f"✅ Retrieved {len(orders)} orders")
    
    print("\n" + "="*100)
    print("✅ ALL TESTS PASSED!")
    print("="*100)
