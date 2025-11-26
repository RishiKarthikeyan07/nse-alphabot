#!/usr/bin/env python3
"""
Test Zerodha Kite API Connection
"""

import os
import sys
sys.path.append('src')

def test_zerodha_connection():
    """Test Zerodha API connection and basic functionality"""

    print("🧪 Testing Zerodha Kite API Connection")
    print("="*50)

    # Check environment variables
    api_key = os.getenv('ZERODHA_API_KEY')
    api_secret = os.getenv('ZERODHA_API_SECRET')

    if not api_key or not api_secret:
        print("❌ Missing environment variables")
        print("   Set ZERODHA_API_KEY and ZERODHA_API_SECRET in .env file")
        return False

    print(f"✅ API Key: {api_key[:8]}...")
    print(f"✅ API Secret: {api_secret[:8]}...")

    try:
        from src.trading.zerodha_live_trader import ZerodhaLiveTrader

        # Try to load from config first
        try:
            trader = ZerodhaLiveTrader.load_from_config()
            print("✅ Loaded from saved configuration")

        except FileNotFoundError:
            print("⚠️  No saved config found - first time setup required")
            print("   Run authentication first:")
            print("   python3 -c \"from src.trading.zerodha_live_trader import ZerodhaLiveTrader; ZerodhaLiveTrader(os.getenv('ZERODHA_API_KEY'), os.getenv('ZERODHA_API_SECRET')).authenticate()\"")
            return False

        # Test portfolio access
        print("\n📊 Testing portfolio access...")
        holdings = trader.get_portfolio_summary()

        if holdings is not None:
            print("✅ Portfolio access successful")
        else:
            print("❌ Portfolio access failed")
            return False

        # Test instrument lookup
        print("\n🔍 Testing instrument lookup...")
        instruments = trader.kite.instruments(exchange='NSE')
        reliance = next((i for i in instruments if i['tradingsymbol'] == 'RELIANCE'), None)

        if reliance:
            print(f"✅ Found RELIANCE: {reliance['instrument_token']}")
        else:
            print("❌ RELIANCE instrument not found")
            return False

        # Test quote fetching
        print("\n💰 Testing live quotes...")
        try:
            quote = trader.kite.quote(reliance['instrument_token'])
            if reliance['instrument_token'] in quote:
                ltp = quote[reliance['instrument_token']]['last_price']
                print(f"✅ RELIANCE LTP: ₹{ltp:.2f}")
            else:
                print("❌ Quote fetch failed")
                return False
        except Exception as e:
            print(f"❌ Quote fetch error: {e}")
            return False

        # Test DRL integration
        print("\n🤖 Testing DRL integration...")
        signal_data = {
            'price': ltp,
            'rsi': 50,
            'confidence': 0.8,
            'expected_return': 3.0
        }

        drl_decision, drl_conf = trader.get_drl_decision('RELIANCE.NS', signal_data)
        print(f"✅ DRL Decision: {drl_decision} (confidence: {drl_conf:.1%})")

        print("\n" + "="*50)
        print("🎉 ALL TESTS PASSED!")
        print("✅ Zerodha API connection working")
        print("✅ Portfolio access working")
        print("✅ Live quotes working")
        print("✅ DRL integration working")
        print("="*50)
        print("\n🚀 Ready for automated trading!")
        print("   Run: python3 src/trading/zerodha_live_trader.py")

        return True

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Install required packages:")
        print("   pip install kiteconnect selenium webdriver-manager")
        return False

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_zerodha_connection()
    sys.exit(0 if success else 1)
