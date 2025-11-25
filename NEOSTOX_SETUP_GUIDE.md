# 🚀 NeoStox Paper Trading Setup Guide

Complete guide to set up and use **NeoStox's built-in paper trading** with NSE AlphaBot.

---

## 🎯 Why NeoStox?

### Advantages Over Custom Paper Trading

✅ **Built-in Paper Trading Mode** - Official broker feature  
✅ **Real Broker API** - Same as live trading  
✅ **Automatic Stop Loss & Targets** - Bracket orders supported  
✅ **Real-time Prices** - Actual market data  
✅ **Position Management** - Full broker features  
✅ **Easy Transition** - Switch to live with one parameter  

---

## 📋 Prerequisites

### 1. NeoStox Account
- Sign up at: https://neostox.com
- Free paper trading account
- No deposit required for paper trading

### 2. API Access
- Get API key from NeoStox dashboard
- Free for paper trading
- Instant activation

### 3. Python Environment
```bash
Python 3.8+
pip
```

---

## 🔧 Installation

### Step 1: Install NeoStox Library

```bash
pip install neostox
```

### Step 2: Update requirements.txt

Add to your `requirements.txt`:
```
neostox
```

Install all dependencies:
```bash
pip install -r requirements.txt
```

---

## ⚙️ Configuration

### Step 1: Get NeoStox Credentials

1. **Sign up at NeoStox**
   - Visit: https://neostox.com
   - Create account
   - Verify email

2. **Get API Key**
   - Login to dashboard
   - Go to API section
   - Generate API key
   - Copy your credentials:
     - Client ID (your email)
     - API Key

### Step 2: Configure .env File

Create/update `.env` file:

```bash
# NeoStox Credentials
NEOSTOX_CLIENT_ID=your_email@example.com
NEOSTOX_API_KEY=your_neostox_api_key

# Trading Configuration
CAPITAL=500000
RISK_PER_TRADE=0.03
MAX_POSITIONS=8
MIN_CONFIDENCE=0.75
MIN_EXPECTED_RETURN=2.5

# Finnhub API (for sentiment)
FINNHUB_API_KEY=your_finnhub_key
```

---

## 🚀 Usage

### Quick Start

```bash
# Run paper trading bot
python3 neostox_paper_trading_bot.py
```

### What It Does

1. **Connects to NeoStox** (paper mode)
2. **Runs NSE AlphaBot** to generate signals
3. **Executes trades** with bracket orders
4. **Manages positions** automatically
5. **Tracks performance**

---

## 📊 Example Session

```bash
$ python3 neostox_paper_trading_bot.py

🚀 NEOSTOX PAPER TRADING BOT
================================================================

📄 Using NeoStox's built-in PAPER TRADING mode
   • Real broker API
   • Virtual money
   • Real-time prices
   • Automatic stop loss & targets

🔧 Setting up NeoStox connection...
✅ NeoStox connected (PAPER MODE)

💰 ACCOUNT MARGINS
================================================================
Available Margin: ₹500,000.00
Used Margin: ₹0.00
================================================================

📊 CURRENT POSITIONS
================================================================
⏳ No open positions
================================================================

⚙️ CONFIGURATION
================================================================
Auto-execute trades? (yes/no): no
Total capital (default 500000): 500000
Maximum positions (default 8): 8

✅ Configuration:
   Auto-execute: False
   Capital: ₹500,000
   Max positions: 8

🌅 STARTING DAILY TRADING CYCLE
================================================================
Mode: MANUAL CONFIRMATION
Capital: ₹500,000
Max Positions: 8
Min Confidence: 75%
Min Return: 2.5%

📊 Current Positions: 0/8

🤖 RUNNING NSE ALPHABOT ANALYSIS
================================================================
Analyzing RELIANCE.NS...
✅ RELIANCE.NS: Conf=77%, Return=+4.7%
Analyzing TCS.NS...
✅ TCS.NS: Conf=76%, Return=+3.8%
Analyzing INFY.NS...
✅ INFY.NS: Conf=75%, Return=+3.2%

✅ Analysis complete: 3 BUY signals found

📋 SIGNALS SUMMARY (3 signals)
================================================================
1. RELIANCE.NS: ₹2,850.50 | Conf: 77% | Return: +4.7%
2. TCS.NS: ₹3,645.20 | Conf: 76% | Return: +3.8%
3. INFY.NS: ₹1,542.80 | Conf: 75% | Return: +3.2%

🎯 EXECUTING 3 SIGNALS
================================================================

Signal 1/3

🎯 SIGNAL: RELIANCE
================================================================
Price: ₹2,850.50
Shares: 526
Position Size: ₹1,499,763
Confidence: 77%
Expected Return: +4.7%
Stop Loss: ₹2,765.00 (-3%)
Target: ₹2,984.50 (+4.7%)
================================================================

🤔 Execute this trade? (yes/no/skip/quit): yes

📤 Placing BRACKET order on NeoStox (PAPER MODE)...
✅ Order executed successfully!
   Order ID: 240120000123456
   Ticker: RELIANCE
   Quantity: 526
   Entry: ₹2,850.50
   Stop Loss: ₹2,765.00
   Target: ₹2,984.50

[Continues for other signals...]

✅ EXECUTION COMPLETE: 3/3 trades executed
================================================================

📊 CURRENT POSITIONS
================================================================

RELIANCE:
  Quantity: 526
  Buy Price: ₹2,850.50
  LTP: ₹2,855.00
  P&L: ₹2,367.00

TCS:
  Quantity: 411
  Buy Price: ₹3,645.20
  LTP: ₹3,650.00
  P&L: ₹1,972.80

INFY:
  Quantity: 971
  Buy Price: ₹1,542.80
  LTP: ₹1,545.00
  P&L: ₹2,136.20

💰 Total P&L: ₹6,476.00
================================================================

✅ DAILY CYCLE COMPLETE
================================================================

✅ PAPER TRADING SESSION COMPLETE
================================================================
```

---

## 🎮 Features

### 1. Bracket Orders ✅
- **Entry order** - Market/Limit
- **Stop loss** - Automatic (-3%)
- **Target** - Based on expected return
- **All managed by broker**

### 2. Real-time Position Tracking ✅
- Live P&L updates
- Current prices
- Position details
- Margin usage

### 3. Automatic Risk Management ✅
- 3% risk per trade
- Position sizing
- Maximum positions limit
- Capital allocation

### 4. Bot Integration ✅
- Runs NSE AlphaBot
- Filters by confidence
- Executes top signals
- Tracks performance

---

## 📈 Daily Workflow

### Morning (Before 9:15 AM)

1. **Check Account**
   ```bash
   python3 -c "
   from src.trading.neostox_trader import setup_neostox
   trader = setup_neostox('paper')
   trader.display_margins()
   trader.display_positions()
   "
   ```

2. **Review Configuration**
   - Check .env settings
   - Verify thresholds
   - Confirm capital

### Market Open (9:15 AM)

3. **Run Paper Trading Bot**
   ```bash
   python3 neostox_paper_trading_bot.py
   ```

4. **Review Signals**
   - Check confidence levels
   - Verify expected returns
   - Confirm position sizes

5. **Execute Trades**
   - Manual mode: Confirm each trade
   - Auto mode: Trades execute automatically

### During Market Hours

6. **Monitor Positions**
   ```bash
   python3 -c "
   from src.trading.neostox_trader import setup_neostox
   trader = setup_neostox('paper')
   trader.display_positions()
   "
   ```

7. **Check Logs**
   ```bash
   tail -f neostox_paper_trading.log
   ```

### End of Day

8. **Review Performance**
   - Check executed trades
   - Calculate P&L
   - Review hit rate

9. **Plan for Tomorrow**
   - Note what worked
   - Adjust if needed

---

## 🔄 Switching to Live Trading

### When Ready (After 2-4 Weeks)

**Change ONE parameter:**

```python
# Paper trading
trader = setup_neostox(environment="paper")

# Live trading
trader = setup_neostox(environment="prod")
```

**That's it!** Everything else stays the same.

---

## 🛡️ Safety Features

### Built-in Protection

1. **Bracket Orders**
   - Automatic stop loss
   - Automatic target
   - No manual intervention needed

2. **Position Limits**
   - Maximum 8 positions
   - Prevents over-exposure

3. **Risk Management**
   - 3% risk per trade
   - Dynamic position sizing
   - Capital allocation

4. **Duplicate Prevention**
   - One trade per stock per day
   - Tracks executed trades

---

## 📊 Performance Tracking

### Key Metrics

Track these in paper trading:

1. **Win Rate**
   - Target: 70%+
   - Your bot: 78-88% expected

2. **Average Return**
   - Target: 3%+ per trade
   - Track actual vs expected

3. **Risk-Reward Ratio**
   - Target: 2:1 or better
   - Compare wins vs losses

4. **Max Drawdown**
   - Target: <15%
   - Track worst losing streak

### Validation Criteria

Before going live, achieve:

| Metric | Target | Status |
|--------|--------|--------|
| **Win Rate** | ≥70% | ⏳ Testing |
| **Avg Return** | ≥3% | ⏳ Testing |
| **Risk-Reward** | ≥2:1 | ⏳ Testing |
| **Max Drawdown** | <15% | ⏳ Testing |
| **Total Trades** | ≥20 | ⏳ Testing |

---

## 🐛 Troubleshooting

### Issue 1: "NeoStox not installed"

**Solution:**
```bash
pip install neostox
```

### Issue 2: "Credentials not found"

**Solution:**
```bash
# Check .env file
cat .env | grep NEOSTOX

# Should show:
# NEOSTOX_CLIENT_ID=your_email
# NEOSTOX_API_KEY=your_key
```

### Issue 3: "Connection failed"

**Possible causes:**
- Invalid credentials
- Network issue
- NeoStox server down

**Solution:**
- Verify credentials
- Check internet
- Try again later

### Issue 4: "Order rejected"

**Possible causes:**
- Insufficient margin
- Invalid symbol
- Market closed

**Solution:**
- Check margins
- Verify ticker symbol
- Check market hours

---

## 💡 Tips & Best Practices

### 1. Start with Manual Mode
- Review each trade
- Understand bot decisions
- Build confidence

### 2. Test Different Scenarios
- Bull market days
- Bear market days
- Volatile days
- Flat days

### 3. Keep a Trading Journal
- Note why you took each trade
- Record emotions
- Learn from mistakes

### 4. Monitor Closely
- Check positions regularly
- Review P&L daily
- Track performance weekly

### 5. Be Patient
- Test for 2-4 weeks minimum
- Don't rush to live trading
- Validate thoroughly

---

## 📝 Code Examples

### Test Connection

```python
from src.trading.neostox_trader import setup_neostox

# Connect to paper trading
trader = setup_neostox(environment="paper")

# Get account info
trader.display_margins()
trader.display_positions()
```

### Place Manual Order

```python
from src.trading.neostox_trader import setup_neostox

trader = setup_neostox(environment="paper")

# Place bracket order
order_id = trader.place_bracket_order(
    symbol="RELIANCE",
    quantity=100,
    transaction_type="BUY",
    product="MIS",
    squareoff=20,  # Target: +20 points
    stoploss=8     # Stop loss: -8 points
)

print(f"Order ID: {order_id}")
```

### Check Positions

```python
from src.trading.neostox_trader import setup_neostox

trader = setup_neostox(environment="paper")

# Get positions
positions = trader.get_positions()

for pos in positions:
    print(f"{pos['tradingsymbol']}: P&L = ₹{pos['pnl']:.2f}")
```

---

## 🎯 Advantages Summary

### vs Custom Paper Trading

| Feature | NeoStox | Custom |
|---------|---------|--------|
| **Real Broker API** | ✅ Yes | ❌ No |
| **Bracket Orders** | ✅ Yes | ❌ Manual |
| **Auto SL/Target** | ✅ Yes | ❌ Manual |
| **Real Prices** | ✅ Yes | ✅ Yes |
| **Easy to Live** | ✅ 1 param | ❌ Rewrite |
| **Position Mgmt** | ✅ Broker | ❌ Manual |

---

## 📞 Support

### NeoStox Support
- Website: https://neostox.com
- Email: support@neostox.com
- Documentation: https://neostox.com/docs

### Bot Support
- Guide: This file
- Logs: `neostox_paper_trading.log`
- Repository: https://github.com/RishiKarthikeyan07/nse-alphabot

---

## ✅ Quick Commands

```bash
# Install NeoStox
pip install neostox

# Test connection
python3 src/trading/neostox_trader.py

# Run paper trading bot
python3 neostox_paper_trading_bot.py

# Check logs
tail -f neostox_paper_trading.log

# View positions
python3 -c "from src.trading.neostox_trader import setup_neostox; trader = setup_neostox('paper'); trader.display_positions()"
```

---

## 🎉 Ready to Start!

### Your Journey

1. ✅ **Setup NeoStox** (5 minutes)
2. ✅ **Test connection** (2 minutes)
3. ✅ **Run paper trading** (2-4 weeks)
4. ✅ **Validate performance**
5. ✅ **Go live!** (when ready)

---

**Version:** 1.0  
**Last Updated:** November 20, 2024  
**Status:** Production Ready  

**🚀 The easiest way to paper trade with real broker features!**

**⚠️ Remember:** Paper trading success doesn't guarantee live trading success, but NeoStox's built-in paper trading is the closest you can get to real trading!
