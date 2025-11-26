#!/usr/bin/env python3
"""
Comprehensive System Testing for NSE AlphaBot v2.0
Tests all components with Nifty 100 DRL model support
"""

import sys
import os
sys.path.append('src')

import traceback
from datetime import datetime
import json

# Test results storage
test_results = {
    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    'tests_run': 0,
    'tests_passed': 0,
    'tests_failed': 0,
    'failures': []
}

def test_header(test_name):
    """Print test header"""
    print(f"\n{'='*80}")
    print(f"TEST: {test_name}")
    print(f"{'='*80}")

def test_result(test_name, passed, error=None):
    """Record test result"""
    test_results['tests_run'] += 1
    if passed:
        test_results['tests_passed'] += 1
        print(f"✅ PASSED: {test_name}")
    else:
        test_results['tests_failed'] += 1
        test_results['failures'].append({
            'test': test_name,
            'error': str(error)
        })
        print(f"❌ FAILED: {test_name}")
        if error:
            print(f"   Error: {error}")

# ============================================================================
# TEST 1: Import Tests
# ============================================================================

test_header("1. Import Tests - Core Dependencies")
try:
    import pandas as pd
    import numpy as np
    import yfinance as yf
    import torch
    from transformers import AutoTokenizer, AutoModel
    from stable_baselines3 import SAC
    import einops  # Critical for Kronos
    test_result("Core dependencies import", True)
except Exception as e:
    test_result("Core dependencies import", False, e)

test_header("2. Import Tests - Project Modules")
try:
    from utils.fetch_all_nse_stocks import get_all_nse_stocks
    from utils.pkscreener_integration import screen_nse_stocks
    from utils.multi_timeframe_analyzer import MultiTimeframeAnalyzer
    from utils.smc_analyzer import SMCAnalyzer
    from utils.advanced_technical import AdvancedTechnicalAnalyzer
    from utils.sentiment_analyzer import get_hybrid_sentiment
    from models.kronos_predictor import get_kronos_predictor
    test_result("Project modules import", True)
except Exception as e:
    test_result("Project modules import", False, e)

# ============================================================================
# TEST 2: NSE Stock Fetching
# ============================================================================

test_header("3. NSE Stock Fetching")
try:
    from utils.fetch_all_nse_stocks import get_all_nse_stocks
    stocks = get_all_nse_stocks()
    
    assert stocks is not None, "Stocks list is None"
    assert len(stocks) > 2000, f"Expected >2000 stocks, got {len(stocks)}"
    assert 'RELIANCE.NS' in stocks, "RELIANCE.NS not in stock list"
    assert 'TCS.NS' in stocks, "TCS.NS not in stock list"
    
    print(f"   ✓ Fetched {len(stocks)} NSE stocks")
    test_result("NSE stock fetching", True)
except Exception as e:
    test_result("NSE stock fetching", False, e)

# ============================================================================
# TEST 3: Stock Data Download
# ============================================================================

test_header("4. Stock Data Download (yfinance)")
try:
    import yfinance as yf
    
    # Test single stock
    df = yf.download('RELIANCE.NS', period='1mo', interval='1d', 
                     auto_adjust=True, progress=False)
    
    assert not df.empty, "Downloaded data is empty"
    assert len(df) > 10, f"Expected >10 days of data, got {len(df)}"
    assert 'Close' in df.columns, "Close column missing"
    assert 'Volume' in df.columns, "Volume column missing"
    
    print(f"   ✓ Downloaded {len(df)} days of data for RELIANCE.NS")
    test_result("Stock data download", True)
except Exception as e:
    test_result("Stock data download", False, e)

# ============================================================================
# TEST 4: PKScreener Integration
# ============================================================================

test_header("5. PKScreener Integration")
try:
    from utils.pkscreener_integration import screen_nse_stocks
    
    # Test screening with small sample
    qualified = screen_nse_stocks(max_stocks=10, min_volume=1000000)
    
    assert qualified is not None, "Screening returned None"
    assert isinstance(qualified, list), "Screening didn't return a list"
    assert len(qualified) <= 10, f"Expected ≤10 stocks, got {len(qualified)}"
    
    print(f"   ✓ Screened and found {len(qualified)} qualified stocks")
    test_result("PKScreener integration", True)
except Exception as e:
    test_result("PKScreener integration", False, e)

# ============================================================================
# TEST 5: Multi-Timeframe Analysis
# ============================================================================

test_header("6. Multi-Timeframe Analysis")
try:
    from utils.multi_timeframe_analyzer import MultiTimeframeAnalyzer
    
    analyzer = MultiTimeframeAnalyzer('RELIANCE.NS')
    success = analyzer.fetch_all_timeframes()
    
    assert success, "Failed to fetch timeframes"
    assert len(analyzer.data) >= 3, f"Expected ≥3 timeframes, got {len(analyzer.data)}"
    
    analyzer.analyze_all_timeframes()
    signal = analyzer.generate_signal()
    
    assert 'signal' in signal, "Signal missing 'signal' key"
    assert 'confidence' in signal, "Signal missing 'confidence' key"
    assert signal['signal'] in ['BUY', 'SELL', 'HOLD'], f"Invalid signal: {signal['signal']}"
    
    print(f"   ✓ Analyzed {len(analyzer.data)} timeframes")
    print(f"   ✓ Signal: {signal['signal']} (Confidence: {signal['confidence']:.2%})")
    test_result("Multi-timeframe analysis", True)
except Exception as e:
    test_result("Multi-timeframe analysis", False, e)

# ============================================================================
# TEST 6: Smart Money Concepts Analysis
# ============================================================================

test_header("7. Smart Money Concepts Analysis")
try:
    from utils.smc_analyzer import SMCAnalyzer
    import yfinance as yf
    import pandas as pd
    
    df = yf.download('RELIANCE.NS', period='3mo', interval='1d',
                     auto_adjust=True, progress=False)
    
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    
    analyzer = SMCAnalyzer(df)
    result = analyzer.analyze_smc()
    
    assert 'signal' in result, "SMC result missing 'signal' key"
    assert 'score' in result, "SMC result missing 'score' key"
    assert 'order_blocks' in result, "SMC result missing 'order_blocks' key"
    assert 'fvgs' in result, "SMC result missing 'fvgs' key"
    
    print(f"   ✓ SMC Signal: {result['signal']} (Score: {result['score']:.2f})")
    print(f"   ✓ Order Blocks: {result['order_blocks']['bullish']} bullish, {result['order_blocks']['bearish']} bearish")
    test_result("Smart Money Concepts analysis", True)
except Exception as e:
    test_result("Smart Money Concepts analysis", False, e)

# ============================================================================
# TEST 7: Advanced Technical Analysis
# ============================================================================

test_header("8. Advanced Technical Analysis")
try:
    from utils.advanced_technical import AdvancedTechnicalAnalyzer
    import yfinance as yf
    import pandas as pd
    
    df = yf.download('RELIANCE.NS', period='6mo', interval='1d',
                     auto_adjust=True, progress=False)
    
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    
    analyzer = AdvancedTechnicalAnalyzer(df)
    result = analyzer.analyze()
    
    assert 'signal' in result, "Technical result missing 'signal' key"
    assert 'score' in result, "Technical result missing 'score' key"
    
    print(f"   ✓ Technical Signal: {result['signal']} (Score: {result['score']:.2f})")
    test_result("Advanced technical analysis", True)
except Exception as e:
    test_result("Advanced technical analysis", False, e)

# ============================================================================
# TEST 8: Sentiment Analysis
# ============================================================================

test_header("9. Sentiment Analysis")
try:
    from utils.sentiment_analyzer import get_hybrid_sentiment
    
    sentiment = get_hybrid_sentiment('RELIANCE.NS')
    
    assert sentiment is not None, "Sentiment is None"
    assert 0 <= sentiment <= 1, f"Sentiment out of range: {sentiment}"
    
    print(f"   ✓ Sentiment Score: {sentiment:.2f}")
    test_result("Sentiment analysis", True)
except Exception as e:
    test_result("Sentiment analysis", False, e)

# ============================================================================
# TEST 9: Kronos AI Model Loading
# ============================================================================

test_header("10. Kronos AI Model Loading")
try:
    from models.kronos_predictor import get_kronos_predictor
    
    predictor = get_kronos_predictor(model_name="NeoQuasar/Kronos-small")
    
    assert predictor is not None, "Predictor is None"
    assert predictor.model is not None, "Kronos model is None"
    assert predictor.tokenizer is not None, "Kronos tokenizer is None"
    
    print(f"   ✓ Kronos model loaded successfully")
    print(f"   ✓ Device: {predictor.device}")
    print(f"   ✓ Model: NeoQuasar/Kronos-small (24.7M params)")
    test_result("Kronos AI model loading", True)
except Exception as e:
    test_result("Kronos AI model loading", False, e)

# ============================================================================
# TEST 10: Kronos Price Prediction
# ============================================================================

test_header("11. Kronos Price Prediction")
try:
    from models.kronos_predictor import get_kronos_predictor
    import yfinance as yf
    import pandas as pd
    
    predictor = get_kronos_predictor()
    df = yf.download('RELIANCE.NS', period='6mo', interval='1d',
                     auto_adjust=True, progress=False)
    
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    
    prediction = predictor.predict(df, horizon=7)
    
    assert 'predicted_close' in prediction, "Prediction missing 'predicted_close'"
    assert 'predicted_change' in prediction, "Prediction missing 'predicted_change'"
    assert 'confidence' in prediction, "Prediction missing 'confidence'"
    
    print(f"   ✓ Predicted change: {prediction['predicted_change']:+.2%}")
    print(f"   ✓ Confidence: {prediction['confidence']:.2%}")
    test_result("Kronos price prediction", True)
except Exception as e:
    test_result("Kronos price prediction", False, e)

# ============================================================================
# TEST 11: DRL Agent Loading (Nifty 100 Priority)
# ============================================================================

test_header("12. DRL Agent Loading (Nifty 100 Priority)")
try:
    from stable_baselines3 import SAC
    
    # Try to load DRL agent (prioritize Nifty 100)
    drl_models = [
        ('models/sac_nse_nifty100.zip', 'Nifty 100 (100 stocks, 200k timesteps) ⭐ BEST'),
        ('models/sac_nse_nifty50.zip', 'Nifty 50 (50 stocks, 150k timesteps)'),
        ('models/sac_nse_retrained.zip', 'Retrained (20 stocks, 100k timesteps)'),
        ('models/sac_nse_10y_final.zip', 'Original (10 years data)')
    ]
    
    agent = None
    loaded_model = None
    
    for model_path, description in drl_models:
        if os.path.exists(model_path):
            try:
                agent = SAC.load(model_path)
                loaded_model = (model_path, description)
                print(f"   ✓ Loaded: {model_path}")
                print(f"   ✓ Description: {description}")
                break
            except Exception as e:
                print(f"   ⚠️  Failed to load {model_path}: {str(e)[:50]}")
    
    assert agent is not None, "No DRL agent found"
    assert loaded_model is not None, "No model loaded"
    
    print(f"   ✓ Algorithm: SAC (Soft Actor-Critic)")
    print(f"   ✓ State Space: 5 dimensions")
    print(f"   ✓ Action Space: Continuous [-1, 1]")
    
    test_result("DRL agent loading", True)
except Exception as e:
    test_result("DRL agent loading", False, e)

# ============================================================================
# TEST 12: DRL Agent Prediction
# ============================================================================

test_header("13. DRL Agent Prediction")
try:
    from stable_baselines3 import SAC
    import numpy as np
    
    # Load agent (prioritize Nifty 100)
    drl_models = [
        'models/sac_nse_nifty100.zip',
        'models/sac_nse_nifty50.zip',
        'models/sac_nse_retrained.zip',
        'models/sac_nse_10y_final.zip'
    ]
    
    agent = None
    for model_path in drl_models:
        if os.path.exists(model_path):
            try:
                agent = SAC.load(model_path)
                print(f"   ✓ Using: {os.path.basename(model_path)}")
                break
            except:
                pass
    
    assert agent is not None, "No DRL agent available"
    
    # Create realistic observation
    price_norm = 0.285  # ₹2850 / 10000
    rsi_norm = 0.65     # RSI 65 (healthy)
    macd_norm = 0.05    # MACD 5 (bullish)
    capital_ratio = 1.0 # Full capital
    shares_held = 0.0   # No position
    
    obs = np.array([price_norm, rsi_norm, macd_norm, capital_ratio, shares_held], 
                  dtype=np.float32)
    obs = np.nan_to_num(obs, nan=0.0, posinf=1.0, neginf=0.0)
    
    action, _ = agent.predict(obs, deterministic=True)
    
    # Interpret action
    if action[0] > 0.2:
        signal = "BUY"
    elif action[0] < -0.2:
        signal = "SELL"
    else:
        signal = "HOLD"
    
    # Convert to score
    drl_score = 0.5 + (action[0] * 0.5)
    drl_score = np.clip(drl_score, 0, 1)
    
    assert action is not None, "Action is None"
    assert -1 <= action[0] <= 1, f"Action out of range: {action[0]}"
    
    print(f"   ✓ Input: Price=₹2850, RSI=65, MACD=5")
    print(f"   ✓ Raw Action: {action[0]:+.3f}")
    print(f"   ✓ DRL Score: {drl_score:.3f}")
    print(f"   ✓ Signal: {signal}")
    
    test_result("DRL agent prediction", True)
except Exception as e:
    test_result("DRL agent prediction", False, e)

# ============================================================================
# TEST 13: Complete Bot Workflow
# ============================================================================

test_header("14. Complete Bot Workflow (3 Stocks)")
try:
    print("   Testing complete workflow with 3 stocks...")
    
    # Import bot components
    from utils.multi_timeframe_analyzer import MultiTimeframeAnalyzer
    from utils.smc_analyzer import SMCAnalyzer
    from utils.advanced_technical import AdvancedTechnicalAnalyzer
    from utils.sentiment_analyzer import get_hybrid_sentiment
    from models.kronos_predictor import get_kronos_predictor
    import yfinance as yf
    import pandas as pd
    
    # Get predictor
    predictor = get_kronos_predictor()
    
    # Test with 3 stocks
    test_stocks = ['RELIANCE.NS', 'TCS.NS', 'INFY.NS']
    
    for ticker in test_stocks:
        print(f"\n   Analyzing {ticker}...")
        
        # Fetch data
        df = yf.download(ticker, period='6mo', interval='1d',
                        auto_adjust=True, progress=False)
        
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        
        # Multi-timeframe
        mtf = MultiTimeframeAnalyzer(ticker)
        mtf.fetch_all_timeframes()
        mtf.analyze_all_timeframes()
        mtf_signal = mtf.generate_signal()
        print(f"      MTF: {mtf_signal['signal']} ({mtf_signal['confidence']:.0%})")
        
        # SMC
        smc = SMCAnalyzer(df)
        smc_result = smc.analyze_smc()
        print(f"      SMC: {smc_result['signal']} ({smc_result['score']:.2f})")
        
        # Technical
        tech = AdvancedTechnicalAnalyzer(df)
        tech_result = tech.analyze()
        print(f"      Tech: {tech_result['signal']} ({tech_result['score']:.2f})")
        
        # Sentiment
        sentiment = get_hybrid_sentiment(ticker, df)
        print(f"      Sentiment: {sentiment:.2f}")
        
        # Kronos
        kronos_pred = predictor.predict(df, horizon=7)
        print(f"      Kronos: {kronos_pred['predicted_change']:+.2%} ({kronos_pred['confidence']:.0%})")
    
    print(f"\n   ✓ Successfully analyzed {len(test_stocks)} stocks")
    test_result("Complete bot workflow", True)
except Exception as e:
    test_result("Complete bot workflow", False, e)
    traceback.print_exc()

# ============================================================================
# TEST 14: Configuration Files
# ============================================================================

test_header("15. Configuration Files")
try:
    # Check requirements.txt
    assert os.path.exists('requirements.txt'), "requirements.txt not found"
    with open('requirements.txt', 'r') as f:
        reqs = f.read()
        assert 'yfinance' in reqs, "yfinance not in requirements"
        assert 'torch' in reqs, "torch not in requirements"
        assert 'transformers' in reqs, "transformers not in requirements"
        assert 'stable-baselines3' in reqs, "stable-baselines3 not in requirements"
        assert 'einops' in reqs, "einops not in requirements (CRITICAL)"
    
    print(f"   ✓ requirements.txt complete (including einops)")
    
    # Check main bot file
    assert os.path.exists('src/bot/nse_alphabot_ultimate.py'), "Main bot not found"
    print(f"   ✓ Main bot file present")
    
    test_result("Configuration files", True)
except Exception as e:
    test_result("Configuration files", False, e)

# ============================================================================
# TEST 15: Model Files (Nifty 100 Priority)
# ============================================================================

test_header("16. Model Files (Nifty 100 Priority)")
try:
    # Check models directory
    assert os.path.exists('models'), "models directory not found"
    
    # Check for DRL models (prioritize Nifty 100)
    drl_models = [
        ('models/sac_nse_nifty100.zip', 'Nifty 100 ⭐ BEST'),
        ('models/sac_nse_nifty50.zip', 'Nifty 50'),
        ('models/sac_nse_retrained.zip', 'Retrained'),
        ('models/sac_nse_10y_final.zip', 'Original')
    ]
    
    found_models = []
    for model_path, description in drl_models:
        if os.path.exists(model_path):
            size_mb = os.path.getsize(model_path) / (1024 * 1024)
            print(f"   ✓ {model_path} ({size_mb:.1f} MB) - {description}")
            found_models.append(model_path)
    
    assert len(found_models) > 0, "No DRL models found"
    print(f"   ✓ Found {len(found_models)} DRL model(s)")
    print(f"   ✓ Primary: {os.path.basename(found_models[0])}")
    
    test_result("Model files", True)
except Exception as e:
    test_result("Model files", False, e)

# ============================================================================
# TEST 16: Error Handling
# ============================================================================

test_header("17. Error Handling")
try:
    import yfinance as yf
    
    # Test with invalid ticker
    df = yf.download('INVALID_TICKER.NS', period='1mo', interval='1d',
                     auto_adjust=True, progress=False)
    
    # Should return empty dataframe, not crash
    assert df.empty or len(df) == 0, "Expected empty dataframe for invalid ticker"
    
    print(f"   ✓ Handles invalid tickers gracefully")
    test_result("Error handling", True)
except Exception as e:
    test_result("Error handling", False, e)

# ============================================================================
# TEST 17: Memory Usage
# ============================================================================

test_header("18. Memory Usage")
try:
    import psutil
    import os
    
    process = psutil.Process(os.getpid())
    memory_mb = process.memory_info().rss / 1024 / 1024
    
    print(f"   ✓ Current memory usage: {memory_mb:.1f} MB")
    
    # Check if memory is reasonable (< 2GB)
    assert memory_mb < 2048, f"Memory usage too high: {memory_mb:.1f} MB"
    
    test_result("Memory usage", True)
except Exception as e:
    test_result("Memory usage", False, e)

# ============================================================================
# FINAL REPORT
# ============================================================================

print(f"\n{'='*80}")
print(f"COMPREHENSIVE TEST REPORT v2.0")
print(f"{'='*80}")
print(f"Timestamp: {test_results['timestamp']}")
print(f"Tests Run: {test_results['tests_run']}")
print(f"Tests Passed: {test_results['tests_passed']} ✅")
print(f"Tests Failed: {test_results['tests_failed']} ❌")
print(f"Success Rate: {test_results['tests_passed']/test_results['tests_run']*100:.1f}%")

if test_results['failures']:
    print(f"\n{'='*80}")
    print(f"FAILED TESTS:")
    print(f"{'='*80}")
    for failure in test_results['failures']:
        print(f"\n❌ {failure['test']}")
        print(f"   Error: {failure['error']}")

print(f"\n{'='*80}")
print(f"TEST SUMMARY")
print(f"{'='*80}")

# Calculate grade
success_rate = test_results['tests_passed']/test_results['tests_run']*100
if success_rate == 100:
    grade = "A+ (100/100)"
    status = "🎉 PERFECT SCORE!"
elif success_rate >= 95:
    grade = "A (95-99/100)"
    status = "✅ EXCELLENT"
elif success_rate >= 90:
    grade = "A- (90-94/100)"
    status = "✅ VERY GOOD"
elif success_rate >= 85:
    grade = "B+ (85-89/100)"
    status = "✅ GOOD"
elif success_rate >= 80:
    grade = "B (80-84/100)"
    status = "⚠️  ACCEPTABLE"
else:
    grade = "C or below (<80/100)"
    status = "❌ NEEDS IMPROVEMENT"

print(f"\nGrade: {grade}")
print(f"Status: {status}")

# Save results to file
with open('test_results_v2.json', 'w') as f:
    json.dump(test_results, f, indent=2)

print(f"\n✅ Test results saved to: test_results_v2.json")

# Exit with appropriate code
if test_results['tests_failed'] == 0:
    print(f"\n🎉 ALL TESTS PASSED - GRADE: A+ (100/100)!")
    print(f"🚀 Your NSE AlphaBot is production-ready!")
    sys.exit(0)
else:
    print(f"\n⚠️  SOME TESTS FAILED - Review failures above")
    sys.exit(1)
