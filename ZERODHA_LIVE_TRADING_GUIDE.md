# 🚀 Zerodha Kite Live Trading Guide

Complete guide to set up and use live trading with Zerodha Kite for NSE AlphaBot.

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Zerodha Kite Setup](#zerodha-kite-setup)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Usage](#usage)
6. [Safety Features](#safety-features)
7. [Troubleshooting](#troubleshooting)

---

## 🎯 Prerequisites

### 1. Zerodha Account
- Active Zerodha trading account
- Kite login credentials
- Sufficient margin for trading

### 2. Kite Connect API Access
- Developer account on Kite Connect
- API subscription (₹2000/month)
- API Key and API Secret

### 3. Python Environment
```bash
Python 3.8+
pip
All project dependencies
```

---

## 🔧 Zerodha Kite Setup

### Step 1: Create Kite Connect App

1. **Go to Kite Connect Developer Portal**
   - Visit: https://developers.kite.trade/
   - Login with your Zerodha credentials

2. **Create New App**
   - Click "Create new app"
   - Fill in details:
     - **App name:** NSE AlphaBot
     - **Redirect URL:** http://127.0.0.1:5000 (or your preferred URL)
     - **Description:** AI-powered trading bot
   - Submit for approval

3. **Get API Credentials**
   - Once approved, you'll receive:
     - **API Key:** Your unique API key
     - **API Secret:** Your secret key
   - **IMPORTANT:** Keep these secure!

### Step 2: Subscribe to API
- Go to your app dashboard
- Subscribe to Kite Connect API
- Cost: ₹2000/month
- Payment required before using API

---

## 📦 Installation

### 1. Install Kite Connect Library

```bash
pip install kiteconnect
```

### 2. Update requirements.txt

Add to your `requirements.txt`:
```
kiteconnect
```

### 3. Install All Dependencies

```bash
cd /Users/rishi/Downloads/NSE\ AlphaBot
pip install -r requirements.txt
```

---

## ⚙️ Configuration

### 1. Create/Update .env File

Create `.env` file in project root:

```bash
# Zerodha Kite API Credentials
KITE_API_KEY=your_api_key_here
KITE_API_SECRET=your_api_secret_here
KITE_ACCESS_TOKEN=  # Leave empty initially

# Trading Configuration
CAPITAL=500000
RISK_PER_TRADE=0.03
MAX_POSITIONS=8
MIN_CONFIDENCE=0.75
MIN_EXPECTED_RETURN=2.5

# Finnhub API (for sentiment)
FINNHUB_API_KEY=your_finnhub_key
```

### 2. Get Access Token (Daily)

Access tokens expire daily. Generate new token each day:

```bash
# Run setup script
python3 src/trading/zerodha_live_trader.py
```

**Steps:**
1. Script will show login URL
2. Click URL and login to Kite
3. Copy `request_token` from redirect URL
4. Paste in terminal
5. Script generates `access_token`
6. **SAVE TOKEN** to .env file

**Example Redirect URL:**
```
http://127.0.0.1:5000/?request_token=ABC123XYZ&action=login&status=success
```

Copy `ABC123XYZ` (the request_token part)

### 3. Update .env with Access Token

```bash
KITE_ACCESS_TOKEN=your_generated_access_token
```

**⚠️ IMPORTANT:** Generate new access token every day before market opens!

---

## 🚀 Usage

### Method 1: Automated Live Trading

Run the complete automated system:

```bash
python3 live_trading_bot.py
```

**What it does:**
1. Connects to Zerodha Kite
2. Runs NSE AlphaBot to generate signals
3. Executes trades automatically (if configured)
4. Manages stop loss and targets
5. Monitors positions

**Configuration Options:**
- **Auto-execute:** Trades execute automatically
- **Manual mode:** Confirm each trade
- **Max positions:** Limit concurrent positions
- **Capital:** Total trading capital

### Method 2: Manual Trading

#### Step 1: Run Bot to Get Signals

```bash
python3 src/bot/nse_alphabot_ultimate.py
```

This generates signals and saves to JSON file.

#### Step 2: Review Signals

Check the signals output for:
- Ticker
- Price
- Confidence
- Expected return
- Shares to buy

#### Step 3: Execute Trades Manually

```python
from src.trading.zerodha_live_trader import ZerodhaLiveTrader

# Initialize
trader = ZerodhaLiveTrader(api_key, api_secret, access_token)

# Place order
order_id = trader.place_order(
    symbol='RELIANCE',
    quantity=100,
    order_type='MARKET',
    transaction_type='BUY',
    product='CNC'
)

# Place stop loss
sl_order_id = trader.place_stoploss_order('RELIANCE', 100, 2800)

# Place target
target_order_id = trader.place_target_order('RELIANCE', 100, 2950)
```

### Method 3: Test Mode

Test the system without real trades:

```bash
# Test Zerodha connection
python3 src/trading/zerodha_live_trader.py

# This will:
# - Connect to Kite
# - Show account info
# - Display margins
# - Show current positions
# - Get live prices
# - NO TRADES EXECUTED
```

---

## 🛡️ Safety Features

### 1. Position Limits
- Maximum 8 concurrent positions (configurable)
- Prevents over-exposure

### 2. Capital Management
- 3% risk per trade
- Dynamic position sizing
- Margin checks before orders

### 3. Stop Loss & Targets
- Automatic stop loss at -3%
- Target based on expected return
- Orders placed immediately after entry

### 4. Market Hours Check
- Only trades during market hours (9:15 AM - 3:30 PM)
- Skips weekends and holidays

### 5. Duplicate Prevention
- Tracks executed trades
- Prevents duplicate orders same day

### 6. Manual Confirmation Mode
- Review each trade before execution
- Skip or cancel anytime
- Full control

### 7. Logging
- All trades logged to `live_trading_bot.log`
- Audit trail for review
- Error tracking

---

## 📊 Daily Workflow

### Morning (Before 9:15 AM)

1. **Generate Access Token**
   ```bash
   python3 src/trading/zerodha_live_trader.py
   ```
   - Get new access token
   - Update .env file

2. **Check Account**
   - Verify margins
   - Check existing positions
   - Review yesterday's P&L

3. **Review Bot Configuration**
   - Check signal thresholds
   - Verify position limits
   - Confirm capital allocation

### Market Open (9:15 AM)

4. **Run Live Trading Bot**
   ```bash
   python3 live_trading_bot.py
   ```
   - Bot generates signals
   - Reviews each signal
   - Executes trades (auto or manual)

5. **Monitor Positions**
   - Check order status
   - Verify stop loss placement
   - Monitor P&L

### During Market Hours

6. **Position Management**
   - Monitor stop losses
   - Track targets
   - Adjust if needed

7. **Check Bot Logs**
   ```bash
   tail -f live_trading_bot.log
   ```

### Market Close (3:30 PM)

8. **Review Performance**
   - Check executed trades
   - Calculate P&L
   - Review hit rate

9. **Plan for Tomorrow**
   - Note any issues
   - Adjust parameters if needed
   - Prepare for next day

---

## 🔍 Monitoring & Management

### Check Current Positions

```python
from src.trading.zerodha_live_trader import ZerodhaLiveTrader

trader = ZerodhaLiveTrader(api_key, api_secret, access_token)

# Get positions
positions = trader.get_positions()

# Get holdings
holdings = trader.get_holdings()

# Get orders
orders = trader.get_orders()

# Get daily P&L
pnl = trader.get_daily_pnl()
```

### Modify Orders

```python
# Modify order
trader.modify_order(order_id, quantity=150, price=2850)

# Cancel order
trader.cancel_order(order_id)
```

### Manual Exit

```python
# Sell position
order_id = trader.place_order(
    symbol='RELIANCE',
    quantity=100,
    order_type='MARKET',
    transaction_type='SELL',
    product='CNC'
)
```

---

## ⚠️ Important Notes

### 1. Access Token Validity
- **Valid for:** One trading day only
- **Expires:** End of day (midnight)
- **Action:** Generate new token daily before market opens

### 2. API Rate Limits
- Kite has rate limits on API calls
- Bot is optimized to stay within limits
- Avoid running multiple instances

### 3. Order Types
- **CNC:** Delivery (hold overnight)
- **MIS:** Intraday (square off same day)
- **NRML:** F&O normal

### 4. Charges
- **API Subscription:** ₹2000/month
- **Brokerage:** As per your plan
- **STT, taxes:** Standard charges apply

### 5. Risk Management
- **Start small:** Test with 10-20% capital
- **Monitor closely:** First few weeks
- **Stop loss:** Always use stop loss
- **Review daily:** Check performance

---

## 🐛 Troubleshooting

### Issue 1: "Access token expired"

**Solution:**
```bash
# Generate new access token
python3 src/trading/zerodha_live_trader.py

# Update .env file with new token
```

### Issue 2: "Insufficient funds"

**Solution:**
- Check available margin
- Reduce position size
- Add funds to account

### Issue 3: "Order rejected"

**Possible causes:**
- Insufficient margin
- Stock in ban list
- Circuit limit hit
- Market closed

**Solution:**
- Check order rejection reason
- Verify stock status
- Check market hours

### Issue 4: "Connection error"

**Solution:**
```bash
# Check internet connection
ping google.com

# Verify API credentials
# Check Kite Connect status
```

### Issue 5: "Import error: kiteconnect"

**Solution:**
```bash
pip install kiteconnect
```

---

## 📈 Performance Tracking

### Daily Metrics to Track

1. **Trades Executed**
   - Number of trades
   - Success rate
   - Rejection rate

2. **P&L**
   - Daily P&L
   - Per trade P&L
   - Cumulative P&L

3. **Hit Rate**
   - Winning trades %
   - Losing trades %
   - Average win/loss

4. **Risk Metrics**
   - Max drawdown
   - Sharpe ratio
   - Risk-reward ratio

### Weekly Review

- Compare with paper trading results
- Adjust parameters if needed
- Review bot performance
- Check for improvements

---

## 🔒 Security Best Practices

### 1. Protect API Credentials
- Never commit .env to Git
- Don't share API keys
- Use environment variables

### 2. Secure Access Tokens
- Generate fresh daily
- Don't store in code
- Use .env file only

### 3. Monitor Account
- Check for unauthorized access
- Review all trades
- Enable 2FA on Zerodha

### 4. Backup Data
- Save trade logs
- Backup .env file (securely)
- Keep performance records

---

## 📞 Support

### Zerodha Support
- **Kite Connect:** https://kite.trade/docs/connect/v3/
- **Support:** https://support.zerodha.com/
- **Forum:** https://tradingqna.com/

### Bot Issues
- Check logs: `live_trading_bot.log`
- Review documentation
- Test in paper trading first

---

## ✅ Pre-Live Checklist

Before going live with real money:

- [ ] Zerodha account active and funded
- [ ] Kite Connect API subscribed (₹2000/month)
- [ ] API credentials configured in .env
- [ ] Access token generated and tested
- [ ] Bot tested in paper trading (2-4 weeks)
- [ ] Performance validated (70%+ win rate)
- [ ] Risk management understood
- [ ] Stop loss strategy confirmed
- [ ] Position limits set
- [ ] Capital allocation decided
- [ ] Monitoring system ready
- [ ] Backup plan prepared

---

## 🎯 Quick Start Commands

```bash
# 1. Generate access token (daily)
python3 src/trading/zerodha_live_trader.py

# 2. Test connection
python3 src/trading/zerodha_live_trader.py

# 3. Run live trading (manual mode)
python3 live_trading_bot.py
# Choose: no (for manual confirmation)

# 4. Run live trading (auto mode)
python3 live_trading_bot.py
# Choose: yes (for auto-execution)

# 5. Monitor logs
tail -f live_trading_bot.log
```

---

## 📊 Example Session

```bash
$ python3 live_trading_bot.py

🚀 NSE ALPHABOT - LIVE TRADING WITH ZERODHA KITE
================================================================

🔧 Setting up Zerodha Kite connection...
✅ API Key found: abc123xyz...
✅ Logged in as: Rishi Karthikeyan

⚙️ CONFIGURATION
================================================================
Auto-execute trades? (yes/no): no
Maximum positions (default 8): 8
Total capital (default 500000): 500000

✅ Configuration:
   Auto-execute: False
   Max positions: 8
   Capital: ₹500,000

🌅 STARTING DAILY TRADING CYCLE
================================================================
✅ Market is OPEN

📊 Account Information:
💰 Available Margin: ₹485,250.00
💰 Used Margin: ₹14,750.00

🤖 RUNNING NSE ALPHABOT
================================================================
[Bot runs and generates signals...]

✅ Bot analysis complete: 3 BUY signals found

📋 SIGNALS SUMMARY (3 signals)
================================================================
1. RELIANCE.NS: ₹2,850.50 | Conf: 77% | Return: +4.7%
2. TCS.NS: ₹3,645.20 | Conf: 76% | Return: +3.8%
3. INFY.NS: ₹1,542.80 | Conf: 75% | Return: +3.2%

🎯 EXECUTING 3 SIGNALS
================================================================

Signal 1/3: RELIANCE.NS
================================================================
Price: ₹2,850.50
Shares: 526
Confidence: 77%
Expected Return: +4.7%
Capital Required: ₹1,499,763

🤔 Execute this trade? (yes/no/skip/quit): yes

🎯 EXECUTING BOT SIGNAL
================================================================
Ticker: RELIANCE
Price: ₹2,850.50
Shares: 526
Confidence: 77%
Expected Return: +4.7%
Stop Loss: ₹2,765.00 (-3%)
Target: ₹2,984.50 (+4.7%)

✅ Order placed: BUY 526 RELIANCE @ MARKET
   Order ID: 240120000123456
   Stop Loss Order ID: 240120000123457
   Target Order ID: 240120000123458

✅ Trade executed: RELIANCE.NS

[Continues for other signals...]

✅ EXECUTION COMPLETE: 3/3 trades executed
================================================================

📊 CURRENT POSITIONS
================================================================

RELIANCE:
  Quantity: 526
  Buy Price: ₹2,850.50
  LTP: ₹2,855.00
  P&L: ₹2,367.00 (+0.16%)

TCS:
  Quantity: 411
  Buy Price: ₹3,645.20
  LTP: ₹3,650.00
  P&L: ₹1,972.80 (+0.13%)

INFY:
  Quantity: 971
  Buy Price: ₹1,542.80
  LTP: ₹1,545.00
  P&L: ₹2,136.20 (+0.14%)

================================================================
💰 Total P&L: ₹6,476.00
================================================================

✅ DAILY CYCLE COMPLETE
================================================================

✅ LIVE TRADING SESSION COMPLETE
================================================================
```

---

**Version:** 1.0  
**Last Updated:** November 20, 2024  
**Status:** Production Ready  

**⚠️ DISCLAIMER:** Trading involves risk. Use at your own risk. Start with paper trading and small capital. Always use stop losses.
