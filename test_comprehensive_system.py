#!/usr/bin/env python3
"""
Comprehensive System Testing for NSE AlphaBot
Tests all components, integrations, and workflows
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
    
    df = yf.download('RELIANCE.NS', period='6mo', interval='1d',
                     auto_adjust=True, progress=False)
    
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    
    analyzer = AdvancedTechnicalAnalyzer(df)
    result = analyzer.analyze()
    
    assert 'signal' in result, "Technical result missing 'signal' key"
    assert 'score' in result, "Technical result missing 'score' key"
    assert 'divergence' in result, "Technical result missing 'divergence' key"
    
    print(f"   ✓ Technical Signal: {result['signal']} (Score: {result['score']:.2f})")
    print(f"   ✓ Divergence: {result['divergence']['type']}")
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
# TEST 11: DRL Agent Loading
# ============================================================================

test_header("12. DRL Agent Loading")
try:
    from stable_baselines3 import SAC
    
    # Try to load retrained agent
    try:
        agent = SAC.load("models/sac_nse_retrained.zip")
        print(f"   ✓ Loaded retrained DRL agent")
    except:
        try:
            agent = SAC.load("models/sac_nse_10y_final.zip")
            print(f"   ✓ Loaded original DRL agent")
        except:
            raise Exception("No DRL agent found")
    
    assert agent is not None, "DRL agent is None"
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
    
    # Load agent
    try:
        agent = SAC.load("models/sac_nse_retrained.zip")
    except:
        agent = SAC.load("models/sac_nse_10y_final.zip")
    
    # Create dummy observation
    obs = np.array([0.5, 0.6, 0.5, 1.0, 0.0])
    
    action, _ = agent.predict(obs, deterministic=True)
    
    assert action is not None, "Action is None"
    assert -1 <= action[0] <= 1, f"Action out of range: {action[0]}"
    
    print(f"   ✓ DRL Action: {action[0]:.3f}")
    test_result("DRL agent prediction", True)
except Exception as e:
    test_result("DRL agent prediction", False, e)

# ============================================================================
# TEST 13: Complete Bot Workflow (Small Sample)
# ============================================================================

test_header("14. Complete Bot Workflow (Small Sample)")
try:
    print("   Testing complete workflow with 3 stocks...")
    
    # Import bot components
    from utils.pkscreener_integration import screen_nse_stocks
    from utils.multi_timeframe_analyzer import MultiTimeframeAnalyzer
    from utils.smc_analyzer import SMCAnalyzer
    from utils.advanced_technical import AdvancedTechnicalAnalyzer
    from utils.sentiment_analyzer import get_hybrid_sentiment
    from models.kronos_predictor import get_kronos_predictor
    import yfinance as yf
    
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
        sentiment = get_hybrid_sentiment(ticker)
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
        assert 'einops' in reqs, "einops not in requirements"
    
    # Check Railway files
    assert os.path.exists('railway.json'), "railway.json not found"
    assert os.path.exists('Procfile'), "Procfile not found"
    
    # Check main bot file
    assert os.path.exists('automated_paper_trading.py'), "automated_paper_trading.py not found"
    
    print(f"   ✓ All configuration files present")
    test_result("Configuration files", True)
except Exception as e:
    test_result("Configuration files", False, e)

# ============================================================================
# TEST 15: Model Files
# ============================================================================

test_header("16. Model Files")
try:
    # Check models directory
    assert os.path.exists('models'), "models directory not found"
    
    # Check for DRL agent
    drl_found = False
    if os.path.exists('models/sac_nse_retrained.zip'):
        drl_found = True
        print(f"   ✓ Found retrained DRL agent")
    elif os.path.exists('models/sac_nse_10y_final.zip'):
        drl_found = True
        print(f"   ✓ Found original DRL agent")
    
    assert drl_found, "No DRL agent found"
    
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
print(f"COMPREHENSIVE TEST REPORT")
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

# Save results to file
with open('test_results.json', 'w') as f:
    json.dump(test_results, f, indent=2)

print(f"\n✅ Test results saved to: test_results.json")

# Exit with appropriate code
if test_results['tests_failed'] == 0:
    print(f"\n🎉 ALL TESTS PASSED!")
    sys.exit(0)
else:
    print(f"\n⚠️  SOME TESTS FAILED - Review failures above")
    sys.exit(1)
