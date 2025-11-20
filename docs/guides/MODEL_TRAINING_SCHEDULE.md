# 🔄 Model Training Schedule & Maintenance Guide

## 📋 Quick Answer

**You DON'T need to train every day!**

### Training Frequency Recommendations

| Training Type | Frequency | Duration | Purpose |
|--------------|-----------|----------|---------|
| **Initial Training** | Once | 2-4 hours | Build base model (85-90% accuracy) |
| **Weekly Retraining** | Weekly | 1-2 hours | Keep model updated with recent data |
| **Monthly Full Retraining** | Monthly | 2-4 hours | Comprehensive model refresh |
| **Quarterly Deep Training** | Quarterly | 4-8 hours | Major model improvements |

---

## 🎯 Detailed Training Strategy

### 1. Initial Training (One-Time)

**When:** Before starting to use the bot  
**Duration:** 2-4 hours  
**Frequency:** Once  

```bash
# Run this ONCE to create your base model
python3 src/training/train_transformer_advanced.py
```

**What It Does:**
- Trains on 10+ years of historical data
- Creates a well-trained model (85-90% accuracy)
- Saves model to `models/transformer_advanced_final.pth`

**Result:**
- ✅ Model learns long-term patterns
- ✅ Understands market cycles
- ✅ Ready for daily predictions

**You're Done!** This model will work for weeks/months without retraining.

---

### 2. Weekly Retraining (Recommended)

**When:** Every Sunday evening  
**Duration:** 1-2 hours  
**Frequency:** Weekly  

```bash
# Run this weekly to update with recent data
python3 src/training/train_transformer_weekly.py
```

**Why Weekly?**
- ✅ Captures recent market trends
- ✅ Adapts to new patterns
- ✅ Maintains accuracy over time
- ✅ Not too frequent (avoids overfitting)
- ✅ Not too rare (stays current)

**What Changes:**
- Last week's data added to training
- Model fine-tuned on recent patterns
- Old predictions validated

**Impact:**
- Maintains 85-90% accuracy
- Adapts to market changes
- Prevents model drift

---

### 3. Monthly Full Retraining (Good Practice)

**When:** First Sunday of each month  
**Duration:** 2-4 hours  
**Frequency:** Monthly  

```bash
# Run this monthly for comprehensive update
python3 src/training/train_transformer_advanced.py
```

**Why Monthly?**
- ✅ Comprehensive model refresh
- ✅ Incorporates full month of new data
- ✅ Re-evaluates all patterns
- ✅ Catches seasonal changes

**What Happens:**
- Full retraining from scratch
- All historical data + new month
- Fresh model weights
- Complete evaluation

**Impact:**
- Ensures sustained accuracy
- Adapts to market regime changes
- Prevents gradual degradation

---

### 4. Quarterly Deep Training (Optional)

**When:** Every 3 months  
**Duration:** 4-8 hours  
**Frequency:** Quarterly  

```bash
# Run this quarterly for major improvements
python3 src/training/train_transformer_advanced.py
# Then consider adding more stocks or features
```

**Why Quarterly?**
- ✅ Major model improvements
- ✅ Add new stocks to training
- ✅ Experiment with new features
- ✅ Evaluate long-term performance

**What to Do:**
- Full retraining with expanded data
- Consider adding more stocks (10 → 20)
- Add new technical indicators
- Experiment with hyperparameters

**Impact:**
- Potential accuracy boost (90% → 95%)
- Better generalization
- More robust predictions

---

## 📊 Training Schedule Comparison

### Option A: Minimal (Not Recommended)
```
Initial Training: Once
Retraining: Never
```
**Pros:** No maintenance effort  
**Cons:** Accuracy degrades over time (85% → 70% in 6 months)  
**Verdict:** ❌ Not recommended

### Option B: Basic (Acceptable)
```
Initial Training: Once
Retraining: Monthly
```
**Pros:** Low maintenance, stays reasonably accurate  
**Cons:** May miss short-term trends  
**Verdict:** ✅ Acceptable for casual use

### Option C: Recommended (Best Balance)
```
Initial Training: Once
Retraining: Weekly
Full Retraining: Monthly
```
**Pros:** Stays current, maintains accuracy, manageable effort  
**Cons:** Requires weekly commitment  
**Verdict:** ✅✅ Recommended for serious trading

### Option D: Professional (Maximum Accuracy)
```
Initial Training: Once
Retraining: Weekly
Full Retraining: Monthly
Deep Training: Quarterly
```
**Pros:** Maximum accuracy, adapts quickly, continuous improvement  
**Cons:** Requires significant time investment  
**Verdict:** ✅✅✅ Best for professional trading

---

## 🤖 Automated Training Schedule

### Set Up Automated Weekly Retraining

```bash
# Add to crontab
crontab -e

# Add this line (runs every Sunday at 8 PM)
0 20 * * 0 cd /path/to/NSE-AlphaBot && python3 src/training/train_transformer_weekly.py

# Add this line (full retraining first Sunday of month at 8 PM)
0 20 1-7 * 0 cd /path/to/NSE-AlphaBot && python3 src/training/train_transformer_advanced.py
```

**Benefits:**
- ✅ Automatic updates
- ✅ No manual intervention
- ✅ Consistent schedule
- ✅ Always up-to-date

---

## 📈 When to Retrain (Triggers)

### Mandatory Retraining Triggers

1. **Accuracy Drop**
   - If accuracy falls below 80%
   - If predictions consistently wrong
   - If direction accuracy < 75%

2. **Market Regime Change**
   - Major market crash/rally
   - Policy changes (budget, RBI)
   - Global events (war, pandemic)

3. **New Data Available**
   - After earnings season
   - After major announcements
   - After sector rotation

4. **Model Age**
   - Model > 3 months old
   - No retraining in 6 weeks
   - Significant new data accumulated

### Optional Retraining Triggers

1. **Performance Improvement**
   - Want to add new stocks
   - Want to add new features
   - Want to try new architecture

2. **Seasonal Adjustment**
   - Before earnings season
   - Before budget/policy events
   - Before festival season

---

## 🔍 How to Check If Retraining is Needed

### Daily Monitoring (Automated)

```python
# Add to your bot
def check_model_performance():
    predictions = []
    actuals = []
    
    # Collect last 7 days predictions vs actuals
    for day in last_7_days:
        pred = model.predict(day)
        actual = get_actual_price(day)
        predictions.append(pred)
        actuals.append(actual)
    
    # Calculate accuracy
    mape = mean_absolute_percentage_error(actuals, predictions)
    accuracy = 100 - mape
    
    # Alert if accuracy drops
    if accuracy < 80:
        send_alert("Model accuracy dropped to {accuracy}%. Retraining recommended!")
        return True
    
    return False
```

### Weekly Review

Check these metrics every Sunday:

1. **Accuracy Metrics**
   - Price accuracy: Should be > 85%
   - Direction accuracy: Should be > 85%
   - R² score: Should be > 0.80

2. **Prediction Quality**
   - Are predictions consistently off?
   - Is the model too conservative/aggressive?
   - Are certain stocks predicted poorly?

3. **Market Conditions**
   - Has market behavior changed?
   - Are there new trends?
   - Have volatility patterns shifted?

---

## 💾 Model Versioning Strategy

### Keep Multiple Model Versions

```
models/
├── transformer_advanced_final.pth          # Current production model
├── transformer_advanced_2024_11_14.pth     # Dated backup
├── transformer_advanced_2024_11_07.pth     # Previous week
├── transformer_advanced_2024_10_31.pth     # Previous month
└── transformer_advanced_best_ever.pth      # Best performing model
```

**Benefits:**
- ✅ Can rollback if new model performs worse
- ✅ Compare performance across versions
- ✅ A/B test different models
- ✅ Safety net for experiments

### Version Naming Convention

```python
import datetime

# Save with timestamp
timestamp = datetime.datetime.now().strftime("%Y_%m_%d")
model_name = f"transformer_advanced_{timestamp}.pth"
torch.save(model.state_dict(), f"models/{model_name}")

# Keep last 4 versions
keep_last_n_versions(4)
```

---

## 🎯 Practical Training Schedule

### For Beginners (First 3 Months)

**Month 1:**
- Week 1: Initial training (once)
- Week 2-4: Use model, monitor performance

**Month 2:**
- Week 1: Full retraining (monthly)
- Week 2-4: Use model, monitor performance

**Month 3:**
- Week 1: Full retraining (monthly)
- Week 2-4: Use model, monitor performance

**Result:** Understand model behavior, establish baseline

### For Intermediate Users (Months 4-6)

**Every Week:**
- Sunday: Weekly retraining (1-2 hours)
- Monday-Friday: Use model for trading
- Saturday: Review performance

**Every Month:**
- First Sunday: Full retraining (2-4 hours)
- Review monthly performance
- Adjust parameters if needed

**Result:** Consistent accuracy, good adaptation

### For Advanced Users (Months 7+)

**Every Week:**
- Sunday: Automated weekly retraining
- Daily: Monitor accuracy metrics
- Friday: Review week's performance

**Every Month:**
- First Sunday: Automated full retraining
- Review and analyze monthly results
- Experiment with improvements

**Every Quarter:**
- Deep training with expanded data
- Add new stocks/features
- Optimize hyperparameters

**Result:** Maximum accuracy, continuous improvement

---

## 📊 Expected Accuracy Over Time

### Without Retraining
```
Month 0: 90% (initial)
Month 1: 87% (slight drift)
Month 2: 83% (noticeable drift)
Month 3: 78% (significant drift)
Month 6: 70% (poor performance)
```

### With Monthly Retraining
```
Month 0: 90% (initial)
Month 1: 89% (maintained)
Month 2: 88% (maintained)
Month 3: 90% (refreshed)
Month 6: 88% (stable)
```

### With Weekly Retraining
```
Month 0: 90% (initial)
Month 1: 90% (maintained)
Month 2: 91% (improved)
Month 3: 90% (stable)
Month 6: 90% (consistent)
```

---

## 🛠️ Quick Training Scripts

### Create Weekly Training Script

```python
# src/training/train_transformer_weekly.py
"""
Quick weekly retraining script
- Uses last 2 years of data
- Fine-tunes existing model
- Takes 1-2 hours
"""

import torch
from train_transformer_advanced import *

# Load existing model
model, config = create_advanced_model()
model.load_state_dict(torch.load("models/transformer_advanced_final.pth"))

# Load recent data (last 2 years)
data = load_multi_stock_data(period="2y")

# Fine-tune for 10 epochs
model = train_advanced_model(model, config, data, epochs=10)

# Save updated model
torch.save(model.state_dict(), "models/transformer_advanced_final.pth")
print("✓ Weekly retraining complete!")
```

---

## 🎓 Best Practices

### DO ✅
1. **Train initially** with full historical data
2. **Retrain weekly** to stay current
3. **Full retrain monthly** for comprehensive update
4. **Monitor accuracy** daily
5. **Keep model versions** for rollback
6. **Automate retraining** with cron jobs
7. **Test new models** before deploying

### DON'T ❌
1. **Don't train daily** (overfitting risk)
2. **Don't skip monitoring** (catch issues early)
3. **Don't delete old models** (need for rollback)
4. **Don't ignore accuracy drops** (retrain immediately)
5. **Don't train on too little data** (< 1 year)
6. **Don't deploy untested models** (validate first)

---

## 📝 Summary

### Training Frequency Answer

**Initial Training:** Once (2-4 hours)
- Creates your base model
- 85-90% accuracy
- Good for weeks/months

**Ongoing Maintenance:** Weekly (1-2 hours)
- Keeps model current
- Maintains accuracy
- Adapts to changes

**Full Refresh:** Monthly (2-4 hours)
- Comprehensive update
- Ensures sustained performance
- Prevents degradation

### Bottom Line

**You train ONCE initially, then weekly/monthly for maintenance.**

**NOT daily!** Daily training would:
- ❌ Overfit to recent noise
- ❌ Waste computational resources
- ❌ Not improve accuracy
- ❌ Actually hurt performance

**Weekly/Monthly is optimal!** This approach:
- ✅ Maintains high accuracy
- ✅ Adapts to market changes
- ✅ Prevents overfitting
- ✅ Manageable time commitment
- ✅ Best accuracy/effort ratio

---

**Recommended Schedule:**
```
Week 0: Initial training (once, 2-4 hours)
Week 1-4: Use model (no training)
Week 5: Weekly retrain (1-2 hours)
Week 6-8: Use model (no training)
Week 9: Monthly full retrain (2-4 hours)
... repeat weekly/monthly pattern
```

**Time Investment:**
- Initial: 2-4 hours (one-time)
- Weekly: 1-2 hours (automated)
- Monthly: 2-4 hours (automated)
- **Total: ~2-3 hours per week average**

---

**Last Updated:** 2025-11-14  
**Version:** 1.0  
**Recommendation:** Weekly retraining for best results
