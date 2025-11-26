# Railway Performance Guide & Alternatives

## 🐌 Why Railway Runs Slowly (Free/Hobby Tier)

### Railway Hobby Plan Limitations:
- **CPU:** Shared CPU (0.5 vCPU)
- **RAM:** 512 MB (limited)
- **Cold Starts:** 30-60 seconds to wake up
- **Build Time:** 3-5 minutes (installing PyTorch, transformers, etc.)
- **Execution:** Slower due to limited resources

### Your Bot's Requirements:
- **Kronos AI:** 24.7M parameters (needs ~500MB RAM just for model)
- **PyTorch:** Heavy ML framework
- **2,204 stocks:** Data fetching and processing
- **6 analysis methods:** CPU-intensive calculations

**Result:** Railway Hobby tier struggles with ML workloads

---

## ⚡ Solutions to Speed Up

### Option 1: Upgrade Railway Plan (Recommended for Railway)

**Railway Pro Plan ($20/month):**
- **CPU:** 2 vCPU (4x faster)
- **RAM:** 2 GB (4x more)
- **No cold starts:** Always running
- **Faster builds:** Parallel processing
- **Expected time:** 5-8 minutes per run (vs 15-20 min)

**How to Upgrade:**
1. Go to Railway dashboard
2. Click "Upgrade to Pro"
3. Add payment method
4. Instant upgrade

---

### Option 2: Use AWS EC2 (Best Performance/Cost)

**AWS EC2 t3.medium ($30/month, but more powerful):**
- **CPU:** 2 vCPU (dedicated)
- **RAM:** 4 GB
- **Storage:** 20 GB SSD
- **Network:** Fast
- **Expected time:** 3-5 minutes per run

**Setup Steps:**

1. **Launch EC2 Instance:**
```bash
# On AWS Console:
- AMI: Ubuntu 22.04 LTS
- Instance Type: t3.medium
- Storage: 20 GB gp3
- Security Group: Allow SSH (port 22)
```

2. **Connect and Setup:**
```bash
# SSH into instance
ssh -i your-key.pem ubuntu@your-ec2-ip

# Install Python and dependencies
sudo apt update
sudo apt install python3.10 python3-pip git -y

# Clone your repo
git clone https://github.com/RishiKarthikeyan07/nse-alphabot.git
cd nse-alphabot

# Install dependencies
pip3 install -r requirements.txt
```

3. **Setup Cron Job:**
```bash
# Edit crontab
crontab -e

# Add this line (9:15 AM IST = 3:45 AM UTC)
45 3 * * 1-5 cd /home/ubuntu/nse-alphabot && python3 automated_paper_trading.py >> /home/ubuntu/trading.log 2>&1
```

4. **Keep Instance Running:**
```bash
# Instance runs 24/7, cron triggers bot daily
# Cost: ~$30/month for t3.medium
```

---

### Option 3: Use Google Cloud Run (Pay-per-use)

**Google Cloud Run (Serverless):**
- **Cost:** ~$5-10/month (pay only when running)
- **CPU:** 2 vCPU
- **RAM:** 2 GB
- **Cold starts:** 10-20 seconds
- **Expected time:** 5-8 minutes per run

**Setup:**
1. Create Dockerfile
2. Push to Google Container Registry
3. Deploy to Cloud Run
4. Setup Cloud Scheduler for cron

---

### Option 4: Optimize Your Bot (Free, but limited improvement)

**Reduce Analysis Scope:**

Edit `automated_paper_trading.py`:

```python
# Option A: Analyze fewer stocks
qualified_stocks = screen_nse_stocks(
    max_stocks=25,  # Reduced from 50
    min_volume=2000000  # Higher threshold
)

# Option B: Skip some analysis methods
# Comment out slower methods in bot code
# (But this reduces accuracy)

# Option C: Use lighter AI model
# Replace Kronos with simpler model
# (But this is your main advantage!)
```

**Pros:** Free, immediate
**Cons:** Reduced accuracy, fewer signals

---

## 📊 Performance Comparison

| Platform | Cost/Month | CPU | RAM | Time/Run | Setup | Best For |
|----------|------------|-----|-----|----------|-------|----------|
| **Railway Hobby** | $5 | 0.5 | 512MB | 15-20 min | Easy | Testing |
| **Railway Pro** | $20 | 2 | 2GB | 5-8 min | Easy | Production |
| **AWS EC2 t3.medium** | $30 | 2 | 4GB | 3-5 min | Medium | Best performance |
| **Google Cloud Run** | $5-10 | 2 | 2GB | 5-8 min | Medium | Pay-per-use |
| **Local Computer** | $0 | Varies | Varies | 3-10 min | Easy | Development |

---

## 💡 My Recommendation

### For Testing (1-2 weeks):
**Use Railway Hobby ($5/month)**
- Accept slower performance
- Validate bot works correctly
- Track win rate and signals
- **Then decide:**

### For Production (After validation):

**If budget allows ($30/month):**
→ **AWS EC2 t3.medium**
- Best performance (3-5 min/run)
- Dedicated resources
- Full control
- Most reliable

**If budget-conscious ($20/month):**
→ **Railway Pro**
- Good performance (5-8 min/run)
- Easy to use
- No server management
- Quick upgrade from Hobby

**If minimal usage ($5-10/month):**
→ **Google Cloud Run**
- Pay only when running
- Good performance
- Serverless (no maintenance)
- Scales automatically

---

## 🚀 Quick Win: Optimize Railway Hobby (Free)

While on Railway Hobby, you can make it slightly faster:

### 1. Reduce Stock Universe

Edit `src/utils/pkscreener_integration.py`:

```python
def screen_stocks(self, max_stocks=25, min_volume=2000000):  # Reduced from 50
    # This will analyze fewer stocks, finishing faster
```

### 2. Cache Model Loading

The Kronos model takes time to load. Consider caching it:

```python
# In automated_paper_trading.py
# Model loads once, reuses for all stocks
# (Already implemented, but verify it's working)
```

### 3. Parallel Processing

Add multiprocessing for stock analysis:

```python
from multiprocessing import Pool

def analyze_stock_parallel(stocks):
    with Pool(processes=2) as pool:  # Railway Hobby has 0.5 vCPU, so 2 processes max
        results = pool.map(analyze_single_stock, stocks)
    return results
```

**Expected improvement:** 10-20% faster (still slow, but better)

---

## 🎯 Action Plan

### Week 1-2: Test on Railway Hobby
- ✅ Accept 15-20 min runtime
- ✅ Validate bot generates good signals
- ✅ Track win rate
- ✅ Monitor performance

### Week 3: Decide Based on Results

**If bot is profitable:**
→ Upgrade to AWS EC2 or Railway Pro

**If bot needs tuning:**
→ Stay on Railway Hobby while optimizing

**If bot isn't working:**
→ Fix issues before spending more

---

## 💰 Cost-Benefit Analysis

### Railway Hobby ($5/month):
- **Time cost:** 15-20 min/day = 5.5 hours/month
- **Your time value:** If you value your time at $20/hour
- **Opportunity cost:** 5.5 hours × $20 = $110/month in waiting time
- **Conclusion:** Upgrade makes sense if bot is profitable

### AWS EC2 ($30/month):
- **Time saved:** 12-15 min/day = 4.4 hours/month
- **Performance:** Consistent, reliable
- **Total cost:** $30/month
- **Break-even:** If bot makes >$30/month profit, it pays for itself

---

## 🔧 How to Upgrade Railway (If You Choose)

1. **Go to Railway Dashboard:**
   https://railway.app/dashboard

2. **Click "Upgrade to Pro"**
   - Top right corner
   - Or in project settings

3. **Add Payment Method:**
   - Credit/debit card
   - $20/month

4. **Instant Upgrade:**
   - No redeployment needed
   - Immediately faster
   - More resources

---

## 📞 Summary

**Current Situation:**
- Railway Hobby is slow (15-20 min/run)
- This is normal for free tier with ML workloads
- Your bot is resource-intensive (Kronos AI + 2,204 stocks)

**Options:**
1. **Accept slowness** - Test for 1-2 weeks ($5/month)
2. **Upgrade Railway Pro** - 3x faster ($20/month)
3. **Move to AWS EC2** - 5x faster ($30/month)
4. **Optimize bot** - Slightly faster (free, but reduced accuracy)

**My Recommendation:**
- **Now:** Use Railway Hobby for testing
- **After 2 weeks:** If profitable, upgrade to AWS EC2 or Railway Pro
- **Long-term:** AWS EC2 for best performance/reliability

---

**Remember:** Even at 15-20 minutes, your bot still runs automatically every day. The slowness is annoying but doesn't affect the trading results - signals are still generated correctly!

**The key question:** Is the bot profitable? If yes, upgrade. If no, optimize strategy first.
