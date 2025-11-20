# NSE AlphaBot System Architecture

## Overview
NSE AlphaBot is a streamlined trading system for NSE stocks, focusing on AI-driven predictions and decision-making. The core components include Time Series Transformer (or TrendMaster) for price forecasting and Deep Reinforcement Learning (DRL) agents using FinRL for trade execution. These are integrated with technical analysis modules for robust signal generation.

Key principles:
- No LSTM usage – all predictions use Transformer-based models.
- DRL handles dynamic trade decisions based on predictions and market state.
- Modular design for easy maintenance and extension.

## Core Components

### 1. Prediction Module (Time Series Transformer / TrendMaster)
- **Purpose**: Generates future price predictions using historical data.
- **Models**:
  - Time Series Transformer: Advanced sequence modeling for multi-step forecasts (e.g., 7-60 days ahead).
  - TrendMaster: Optimized Transformer variant for trend detection with NSE-specific tuning.
- **Training**: Handled in `src/training/train_transformer_*.py` and `src/training/train_trendmaster.py`.
- **Output**: Predicted price sequences used as input features for DRL and signal weighting.
- **Integration**: Loaded in bot scripts to provide forecast scores.

### 2. DRL Agents (FinRL)
- **Purpose**: Makes buy/sell/hold decisions using reinforcement learning.
- **Framework**: FinRL library with Stable Baselines3 for agents (e.g., PPO, A2C).
- **State Space**: Includes Transformer predictions, technical indicators, sentiment scores, and market data.
- **Training**: Managed in `src/training/train_drl.py`, incorporating predictions from Transformer/TrendMaster.
- **Inference**: Agent predicts actions in real-time trading scenarios.
- **Rewards**: Based on portfolio returns, risk-adjusted metrics (e.g., Sharpe ratio).

### 3. Analysis Modules
- **Multi-Timeframe Analyzer** (`src/utils/multi_timeframe_analyzer.py`): Aligns trends across timeframes (e.g., daily, weekly).
- **Smart Money Concepts (SMC) Analyzer** (`src/utils/smc_analyzer.py`): Detects order blocks, fair value gaps, liquidity.
- **Advanced Technical Analyzer** (`src/utils/advanced_technical.py`): Computes indicators like Volume Profile, Fibonacci, divergences.
- **Sentiment Analyzer** (`src/utils/sentiment_analyzer.py`): Hybrid news + technical sentiment scoring.

### 4. Main Bot (`src/bot/nse_alphabot_ultimate.py`)
- **Workflow**:
  1. Fetch stock data.
  2. Compute scores from analysis modules.
  3. Generate predictions using Transformer/TrendMaster.
  4. Feed into DRL agent for trade action.
  5. Combine weighted signals for final decision.
- **Signal Weighting** (example):
  - Transformer/TrendMaster Predictions: 20%
  - DRL Agent: 20%
  - MTF: 20%
  - SMC: 15%
  - Advanced Technical: 15%
  - Sentiment: 10%
- **Risk Management**: Position sizing, stop-loss based on ATR and confidence.

### 5. Evaluation and Training
- **Backtesting**: `src/evaluation/backtest.py` – Simulates trades using historical data.
- **Training Pipeline**: Scheduled in `docs/guides/MODEL_TRAINING_SCHEDULE.md` – Periodic retraining of Transformer and DRL models.
- **Models Directory**: Saved checkpoints in `models/`.

## Data Flow
```
Stock Data (yfinance) → Analysis Modules (MTF, SMC, Technical, Sentiment) → Prediction (Transformer/TrendMaster) → DRL Agent (FinRL) → Trade Signal → Execution
```

## Dependencies
- Python libraries: yfinance, pandas, numpy, torch, finrl, stable-baselines3.
- See `requirements.txt` for full list.

This architecture ensures high accuracy (target 78-88%) by leveraging AI for predictions and decisions, while keeping the system clean and focused.

Last updated: [Insert Date]
