# 🚀 Zerodha Automated Trading Setup Guide

## Overview

This guide covers setting up **fully automated trading** with your NSE AlphaBot and Zerodha Kite account. The system will:

- ✅ Generate trading signals using 6-method analysis (including DRL)
- ✅ Automatically place BUY/SELL orders on Zerodha
- ✅ Monitor positions with stop-loss and take-profit
- ✅ Run trading cycles 4x per day during market hours

## Prerequisites

### 1. Zerodha Account
- ✅ Active Zerodha trading account
- ✅ Sufficient funds (₹50,000+ recommended)
- ✅ Kite mobile app installed

### 2. API Access
- ✅ Kite Connect API access enabled
- ✅ API Key and API Secret from Zerodha

### 3. System Requirements
- ✅ Python 3.8+
- ✅ Chrome browser (for authentication)
- ✅ Stable internet connection
- ✅ Linux/Mac/Windows

## Step 1: Get Zerodha API Credentials

### 1.1 Login to Kite Connect
1. Go to: https://developers.kite.trade/
2. Login with your Zerodha credentials
3. Click "Create App"

### 1.2 Create API App
```
App Name: NSE AlphaBot Auto Trading
Redirect URL: https://example.com (can be anything)
Postback URL: Leave empty
```

### 1.3 Get API Credentials
After creating the app, you'll get:
```
API Key: xxxxxxxxxxxxxxxx (16 characters)
API Secret: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx (32 characters)
```

### 1.4 Save Credentials
Create a `.env` file in your project root:

```bash
# Zerodha API Credentials
ZERODHA_API_KEY=your_api_key_here
ZERODHA_API_SECRET=your_api_secret_here
```

## Step 2: Install Dependencies

### 2.1 Install Required Packages
```bash
pip install kiteconnect selenium webdriver-manager python-dotenv schedule
```

Or install from requirements.txt:
```bash
pip install -r requirements.txt
```

### 2.2 Verify Installation
```bash
python3 -c "import kiteconnect; print('✅ kiteconnect installed')"
python3 -c "import selenium; print('✅ selenium installed')"
```

## Step 3: First-Time Authentication

### 3.1 Run Authentication
```bash
python3 -c "
from src.trading.zerodha_live_trader import ZerodhaLiveTrader
import os
trader = ZerodhaLiveTrader(os.getenv('ZERODHA_API_KEY'), os.getenv('ZERODHA_API_SECRET'))
trader.authenticate()
"
```

### 3.2 Complete Authentication
1. **Copy the login URL** from terminal
2. **Open URL in Chrome browser**
3. **Login with Zerodha credentials**
4. **Approve API access**
5. **Copy the `request_token`** from URL
6. **Paste it in terminal** when prompted

### 3.3 Verify Setup
```bash
python3 test_zerodha_connection.py
```

Expected output:
```
🧪 Testing Zerodha Kite API Connection
✅ API Key: xxxxxxxx...
✅ API Secret: xxxxxxxx...
✅ Loaded from saved configuration
📊 Testing portfolio access...
✅ Portfolio access successful
🔍 Testing instrument lookup...
✅ Found RELIANCE: 738561
💰 Testing live quotes...
✅ RELIANCE LTP: ₹2345.67
🤖 Testing DRL integration...
✅ DRL Decision: HOLD (confidence: 50.0%)

🎉 ALL TESTS PASSED!
✅ Zerodha API connection working
✅ Portfolio access working
✅ Live quotes working
✅ DRL integration working
```

## Step 4: Test Manual Trading

### 4.1 Run Manual Cycle
```bash
python3 zerodha_automated_trading.py --manual
```

This will:
- Generate signals from your bot
- Evaluate with DRL agent
- Show potential trades (but NOT execute them yet)

### 4.2 Review Output
Look for:
```
🤖 ZERODHA AUTOMATED TRADING - 2024-11-26 09:30
📊 STEP 3: GENERATING SIGNALS
Found 5 BUY signals, evaluating with DRL agent...

RELIANCE.NS:
  Bot Signal: BUY (confidence: 78.0%)
  DRL Decision: BUY (confidence: 65.0%)
  ✅ Both systems agree - WOULD EXECUTE TRADE
```

## Step 5: Start Automated Trading

### 5.1 Start the System
```bash
python3 zerodha_automated_trading.py
```

### 5.2 Automated Schedule
The system runs **4 trading cycles per day**:

| Time (IST) | Activity |
|------------|----------|
| 9:30 AM   | Market open - First signals |
| 11:00 AM  | Mid-morning check |
| 1:00 PM   | Afternoon momentum |
| 2:30 PM   | Pre-close opportunities |

### 5.3 What Happens Each Cycle
1. **Monitor Positions**: Check stop-loss/targets
2. **Generate Signals**: Bot analyzes market
3. **DRL Evaluation**: Risk assessment
4. **Execute Trades**: Place BUY/SELL orders
5. **Save State**: Update positions log

## Step 6: Monitor and Manage

### 6.1 Check Positions
```bash
python3 -c "
from src.trading.zerodha_live_trader import ZerodhaLiveTrader
trader = ZerodhaLiveTrader.load_from_config()
trader.get_portfolio_summary()
"
```

### 6.2 View Trading Logs
```bash
# System logs
tail -f autotrade_20241126.log

# Trading state
cat zerodha_trading_state.json
```

### 6.3 Emergency Stop
```bash
# Find the process
ps aux | grep zerodha_automated_trading.py

# Kill it
kill -9 <process_id>
```

## Risk Management Features

### Position Limits
- **Max Positions**: 8 simultaneous positions
- **Max Portfolio Risk**: 20% of capital per position
- **Risk per Trade**: 2% of capital

### Stop-Loss & Take-Profit
- **Stop Loss**: 5% below entry price
- **Take Profit**: Based on expected return %
- **DRL Override**: Can sell if confidence drops

### Daily Limits
- **Max Daily Loss**: ₹50,000
- **Trading Hours**: 9:15 AM - 3:30 PM IST
- **Market Days**: Monday - Friday only

## Trading Logic

### Signal Generation
```
Bot Analysis (6 methods) → BUY/HOLD/SELL signal
     ↓
DRL Agent Evaluation → Risk assessment
     ↓
Both Agree → Execute Trade
```

### Position Management
```
Entry: Bot + DRL agree on BUY
Exit: Stop-loss OR Take-profit OR DRL sell signal
Hold: Monitor daily, check conditions
```

## Configuration Options

### Adjust Risk Settings
Edit `src/trading/zerodha_live_trader.py`:

```python
# Risk parameters
self.max_positions = 8          # Max simultaneous positions
self.risk_per_trade = 0.02      # 2% per trade
self.max_portfolio_risk = 0.20  # 20% max per position
self.max_daily_loss = 50000     # ₹50k daily loss limit
```

### Change Trading Schedule
Edit `zerodha_automated_trading.py`:

```python
# Trading times (IST)
self.trading_times = ['09:30', '11:00', '13:00', '14:30']
```

## Troubleshooting

### Issue: Authentication Failed
```
❌ Authentication failed
```
**Solution:**
1. Check API key/secret in `.env`
2. Ensure app is approved on Kite Connect
3. Try re-authentication

### Issue: Orders Not Placing
```
❌ Buy order failed: Invalid order parameters
```
**Solution:**
1. Check account has sufficient funds
2. Verify instrument symbols
3. Check trading permissions

### Issue: DRL Model Not Loading
```
❌ DRL Agent not found!
```
**Solution:**
1. Ensure `models/sac_nse_nifty100.zip` exists
2. Check model file is not corrupted
3. Re-run DRL training if needed

### Issue: Market Data Errors
```
HTTP Error 404: Quote not found
```
**Solution:**
1. Check internet connection
2. Verify instrument tokens
3. Some stocks may be delisted

## Performance Monitoring

### Daily Reports
The system logs all activities:
- Orders placed/executed
- P&L calculations
- Risk metrics
- Error conditions

### Monthly Review
Check:
- Win rate vs loss rate
- Average profit/loss per trade
- Maximum drawdown
- Risk-adjusted returns

## Safety Features

### 1. Dual Confirmation
- Bot signal + DRL confirmation required
- No single system can place orders alone

### 2. Risk Limits
- Position size limits
- Daily loss limits
- Portfolio risk limits

### 3. Manual Override
- Can stop system anytime
- Emergency kill switches
- Manual position management

### 4. Error Handling
- Network failures handled gracefully
- Invalid orders logged and skipped
- System recovers from crashes

## Backup and Recovery

### State Persistence
- Positions saved every cycle
- Trade history maintained
- Can resume after restart

### Manual Recovery
If system crashes:
1. Check `zerodha_trading_state.json`
2. Manually verify positions on Kite
3. Restart system

## Advanced Features

### Custom Strategies
Modify `src/trading/zerodha_live_trader.py`:
- Add technical indicators
- Implement custom entry/exit rules
- Add sector rotation logic

### Multi-Timeframe Analysis
Already included:
- 5-minute, 15-minute, 1-hour, daily, weekly, monthly

### Sentiment Integration
- Finnhub news sentiment (5% weight)
- Can be enhanced with more sources

## Legal and Compliance

### Zerodha Terms
- ✅ Follow Zerodha API terms
- ✅ Respect rate limits
- ✅ Use only for personal trading

### Regulatory Compliance
- ✅ SEBI regulations followed
- ✅ Position limits respected
- ✅ Risk management mandatory

### Disclaimer
⚠️ **This is automated trading software**
- Past performance ≠ future results
- Always test with paper trading first
- Use at your own risk
- Author not responsible for losses

## Support and Updates

### Getting Help
1. Check logs: `tail -f autotrade_*.log`
2. Run tests: `python3 test_zerodha_connection.py`
3. Review documentation

### Updates
- Monitor for API changes
- Update dependencies regularly
- Backup configurations

---

## Quick Start Commands

```bash
# 1. Setup environment
echo "ZERODHA_API_KEY=your_key" > .env
echo "ZERODHA_API_SECRET=your_secret" >> .env

# 2. Install dependencies
pip install -r requirements.txt

# 3. Authenticate
python3 -c "from src.trading.zerodha_live_trader import ZerodhaLiveTrader; ZerodhaLiveTrader(os.getenv('ZERODHA_API_KEY'), os.getenv('ZERODHA_API_SECRET')).authenticate()"

# 4. Test connection
python3 test_zerodha_connection.py

# 5. Test manual cycle
python3 zerodha_automated_trading.py --manual

# 6. Start automated trading
python3 zerodha_automated_trading.py
```

**🎯 Your automated trading system is now ready!**

The system will:
- Monitor markets during trading hours
- Generate signals using your trained DRL model
- Automatically execute profitable trades
- Manage risk with stop-loss and take-profit
- Log all activities for review

**Happy Trading! 🚀**
