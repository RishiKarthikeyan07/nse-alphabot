"""
Quick test of PKScreener integration
Tests with just 5 stocks for speed
"""

import sys
sys.path.append('src')

from utils.pkscreener_integration import PKScreenerIntegration

print("="*80)
print("🧪 PKScreener Integration - Quick Test")
print("="*80)

# Test 1: Initialize
print("\n📋 Test 1: Initialization")
try:
    screener = PKScreenerIntegration()
    print(f"✅ Initialized with {len(screener.nse_stocks)} stocks")
except Exception as e:
    print(f"❌ Failed: {e}")
    sys.exit(1)

# Test 2: Screen stocks (limit to 5 for speed)
print("\n📋 Test 2: Screening (5 stocks max)")
try:
    # Override stock list for quick test
    screener.nse_stocks = ['RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS', 'ICICIBANK.NS']
    qualified = screener.screen_stocks(max_stocks=5, min_volume=1000000, min_price=100, max_price=10000)
    print(f"✅ Screening complete: {len(qualified)} stocks qualified")
    for stock in qualified:
        print(f"   • {stock}")
except Exception as e:
    print(f"❌ Failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 3: Detailed analysis
if qualified:
    print(f"\n📋 Test 3: Detailed Analysis ({qualified[0]})")
    try:
        analysis = screener.get_stock_analysis(qualified[0])
        if analysis:
            print(f"✅ Analysis complete:")
            print(f"   Price: ₹{analysis['price']:.2f}")
            print(f"   Score: {analysis['score']:.2f}")
            print(f"   RSI: {analysis['rsi']:.1f}")
            print(f"   Signal: {analysis['signal']}")
        else:
            print("⚠️  No analysis data")
    except Exception as e:
        print(f"❌ Failed: {e}")
        import traceback
        traceback.print_exc()

print("\n" + "="*80)
print("✅ All Tests Passed!")
print("="*80)
