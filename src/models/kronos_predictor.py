"""
Kronos Price Prediction Module
Uses official NeoQuasar/Kronos-small model (24.7M params) for financial time-series prediction
"""

import torch
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
import warnings
warnings.filterwarnings("ignore")

class KronosPredictor:
    """
    Wrapper for official Kronos foundation model for NSE stock price prediction
    
    Uses NeoQuasar/Kronos-small (24.7M params) - the first open-source foundation model
    specifically trained for financial candlestick (K-line) prediction.
    
    Features:
    - Trained on 45+ global exchanges
    - Financial tokenization (Binary Spherical Quantization)
    - Multi-step ahead forecasting
    - Zero-shot prediction capability
    """
    
    def __init__(self, model_name: str = "NeoQuasar/Kronos-small", device: str = None):
        """
        Initialize Kronos predictor
        
        Args:
            model_name: Model to use (default: NeoQuasar/Kronos-small)
            device: Device to run on ('cuda', 'mps', 'cpu', or None for auto)
        """
        self.model_name = model_name
        
        # Auto-detect device
        if device is None:
            if torch.cuda.is_available():
                self.device = torch.device('cuda')
            elif torch.backends.mps.is_available():
                self.device = torch.device('mps')
            else:
                self.device = torch.device('cpu')
        else:
            self.device = torch.device(device)
        
        print(f"🔧 Initializing Kronos Predictor...")
        print(f"   Model: {model_name}")
        print(f"   Device: {self.device}")
        
        # Load Kronos model
        self.model = None
        self.tokenizer = None
        self._load_model()
        
    def _load_model(self):
        """Load official Kronos model (NO FALLBACK)"""
        try:
            # Use our custom official loader
            import sys
            sys.path.append('src')
            from models.kronos_official_loader import load_official_kronos
            
            print(f"📥 Loading official Kronos from {self.model_name}...")
            
            # Load using our official loader
            self.tokenizer, self.model, self.predictor_obj = load_official_kronos(
                model_name=self.model_name,
                device=str(self.device)
            )
            
            if self.model is None or self.tokenizer is None:
                raise Exception("Failed to load official Kronos model")
            
            print(f"✅ Official Kronos loaded successfully!")
            print(f"   Parameters: 24.7M")
            print(f"   Context: 512 tokens")
            print(f"   Using official NeoQuasar/Kronos-small")
            
        except Exception as e:
            print(f"❌ CRITICAL ERROR: Failed to load official Kronos model")
            print(f"   Error: {e}")
            print(f"   The bot cannot run without Kronos model.")
            raise Exception(f"Kronos model loading failed: {e}")
    
    def prepare_input(self, df: pd.DataFrame, sequence_length: int = 60) -> Dict:
        """
        Prepare input data for Kronos
        
        Args:
            df: DataFrame with OHLCV data
            sequence_length: Number of historical candles to use
            
        Returns:
            Dict with prepared input tensors
        """
        # Get last N candles
        if len(df) < sequence_length:
            sequence_length = len(df)
        
        recent_data = df.iloc[-sequence_length:].copy()
        
        # Prepare OHLCVA data
        input_data = {
            'open': recent_data['Open'].values,
            'high': recent_data['High'].values,
            'low': recent_data['Low'].values,
            'close': recent_data['Close'].values,
            'volume': recent_data['Volume'].values,
        }
        
        # Add amount if available (price * volume)
        if 'Amount' in recent_data.columns:
            input_data['amount'] = recent_data['Amount'].values
        else:
            input_data['amount'] = recent_data['Close'].values * recent_data['Volume'].values
        
        return input_data
    
    def predict(
        self, 
        df: pd.DataFrame, 
        horizon: int = 7,
        return_full_candles: bool = False
    ) -> Dict:
        """
        Predict future prices using official Kronos model
        
        Args:
            df: DataFrame with historical OHLCV data
            horizon: Number of days to predict ahead
            return_full_candles: If True, return full OHLCVA predictions
            
        Returns:
            Dict with predictions:
            - 'predicted_close': Predicted close prices
            - 'predicted_change': Predicted % change
            - 'confidence': Prediction confidence score
            - 'full_candles': Full OHLCVA predictions (if requested)
        """
        
        if self.model is None or self.tokenizer is None:
            raise Exception("Kronos model not loaded. Cannot make predictions.")
        
        try:
            # Prepare input data for official Kronos predictor
            input_df = df[['Open', 'High', 'Low', 'Close', 'Volume']].copy()
            input_df.columns = ['open', 'high', 'low', 'close', 'volume']
            
            # Use the official Kronos predictor
            with torch.no_grad():
                # Get timestamps
                x_timestamp = df.index
                last_date = x_timestamp[-1]
                y_timestamp = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=horizon, freq='D')
                
                # Make prediction using official predictor
                pred_df = self.predictor_obj.predict(
                    df=input_df,
                    x_timestamp=x_timestamp,
                    y_timestamp=y_timestamp,
                    pred_len=horizon,
                    T=1.0,
                    top_k=0,
                    top_p=0.9,
                    sample_count=1,
                    verbose=False
                )
                
                # Extract predictions
                predicted_closes = pred_df['close'].values
                current_close = df['Close'].iloc[-1]
                predicted_change = (predicted_closes[-1] - current_close) / current_close
                
                # Calculate confidence based on prediction consistency
                if len(predicted_closes) > 1:
                    pred_returns = np.diff(predicted_closes) / predicted_closes[:-1]
                    pred_volatility = np.std(pred_returns)
                    confidence = 1.0 / (1.0 + pred_volatility * 10)
                    confidence = np.clip(confidence, 0.7, 0.95)
                else:
                    confidence = 0.85
                
                result = {
                    'predicted_close': predicted_closes,
                    'predicted_change': predicted_change,
                    'confidence': float(confidence),
                    'horizon': horizon,
                    'official_kronos': True
                }
                
                if return_full_candles:
                    result['full_candles'] = pred_df
                
                return result
            
        except Exception as e:
            print(f"❌ Kronos prediction failed: {e}")
            raise Exception(f"Kronos prediction error: {e}")
    
    def _create_input_sequence(self, input_data: Dict) -> torch.Tensor:
        """Create input sequence for Kronos"""
        # Stack OHLCVA data
        sequence = np.stack([
            input_data['open'],
            input_data['high'],
            input_data['low'],
            input_data['close'],
            input_data['volume'],
            input_data['amount']
        ], axis=1)  # Shape: (seq_len, 6)
        
        # Normalize the data
        sequence_normalized = (sequence - sequence.mean(axis=0)) / (sequence.std(axis=0) + 1e-8)
        
        # Convert to tensor
        sequence_tensor = torch.FloatTensor(sequence_normalized).unsqueeze(0)  # (1, seq_len, 6)
        sequence_tensor = sequence_tensor.to(self.device)
        
        return sequence_tensor
    
    def _enhanced_momentum_prediction(self, df: pd.DataFrame, horizon: int, feature_confidence: float = 0.85) -> Dict:
        """
        Enhanced momentum prediction using multiple timeframes and trend analysis
        """
        current_close = df['Close'].iloc[-1]
        
        # Calculate multi-period momentum
        if len(df) >= 30:
            momentum_3d = (df['Close'].iloc[-1] - df['Close'].iloc[-4]) / df['Close'].iloc[-4]
            momentum_5d = (df['Close'].iloc[-1] - df['Close'].iloc[-6]) / df['Close'].iloc[-6]
            momentum_10d = (df['Close'].iloc[-1] - df['Close'].iloc[-11]) / df['Close'].iloc[-11]
            momentum_20d = (df['Close'].iloc[-1] - df['Close'].iloc[-21]) / df['Close'].iloc[-21]
            
            # Weighted momentum (recent periods weighted more)
            momentum = (momentum_3d * 0.4 + momentum_5d * 0.3 + 
                       momentum_10d * 0.2 + momentum_20d * 0.1)
        elif len(df) >= 20:
            momentum_5d = (df['Close'].iloc[-1] - df['Close'].iloc[-6]) / df['Close'].iloc[-6]
            momentum_10d = (df['Close'].iloc[-1] - df['Close'].iloc[-11]) / df['Close'].iloc[-11]
            momentum = (momentum_5d * 0.6 + momentum_10d * 0.4)
        else:
            momentum = 0.0
        
        # Calculate trend strength using EMAs
        if len(df) >= 50:
            ema_12 = df['Close'].ewm(span=12).mean().iloc[-1]
            ema_26 = df['Close'].ewm(span=26).mean().iloc[-1]
            ema_50 = df['Close'].ewm(span=50).mean().iloc[-1]
            
            # Trend alignment bonus
            if ema_12 > ema_26 > ema_50:
                trend_multiplier = 1.2  # Strong uptrend
            elif ema_12 < ema_26 < ema_50:
                trend_multiplier = 0.8  # Strong downtrend
            else:
                trend_multiplier = 1.0  # Mixed trend
        else:
            trend_multiplier = 1.0
        
        # Apply trend multiplier to momentum
        adjusted_momentum = momentum * trend_multiplier
        
        # Scale by horizon with decay
        horizon_factor = horizon / 7.0
        decay_factor = 0.9 ** (horizon - 1)
        predicted_change = adjusted_momentum * horizon_factor * decay_factor
        
        # Generate predicted close prices
        predicted_closes = []
        for i in range(1, horizon + 1):
            step_factor = i / horizon
            step_change = predicted_change * step_factor
            step_close = current_close * (1 + step_change)
            predicted_closes.append(step_close)
        
        predicted_closes = np.array(predicted_closes)
        
        # Calculate confidence
        if len(df) >= 20:
            returns = df['Close'].pct_change().dropna()
            volatility = returns.std()
            volatility_confidence = 1.0 / (1.0 + volatility * 10)
            
            recent_returns = returns.iloc[-10:]
            trend_consistency = 1.0 - abs(recent_returns.mean() / (recent_returns.std() + 1e-8)) * 0.1
            trend_consistency = np.clip(trend_consistency, 0.5, 1.0)
            
            if 'Volume' in df.columns:
                recent_volume = df['Volume'].iloc[-5:].mean()
                avg_volume = df['Volume'].mean()
                volume_factor = min(1.2, recent_volume / (avg_volume + 1))
                volume_confidence = 0.8 + (volume_factor - 1.0) * 0.2
            else:
                volume_confidence = 0.9
            
            base_confidence = (volatility_confidence * 0.4 + 
                             trend_consistency * 0.3 + 
                             volume_confidence * 0.2 +
                             feature_confidence * 0.1)
        else:
            base_confidence = 0.7
        
        if abs(predicted_change) > 0.15:
            base_confidence *= 0.8
        
        confidence = float(np.clip(base_confidence, 0.3, 0.95))
        
        return {
            'predicted_close': predicted_closes,
            'predicted_change': predicted_change,
            'confidence': confidence,
            'horizon': horizon,
            'enhanced': True,
            'momentum': momentum,
            'trend_multiplier': trend_multiplier
        }
    
    def get_prediction_score(self, df: pd.DataFrame) -> float:
        """
        Get a single prediction score (0-1) for signal generation
        
        Args:
            df: DataFrame with historical data
            
        Returns:
            Score between 0 (bearish) and 1 (bullish)
        """
        prediction = self.predict(df, horizon=7)
        
        predicted_change = prediction['predicted_change']
        confidence = prediction['confidence']
        
        # Scale predicted change to score (±10% change maps to 0-1 range)
        score = 0.5 + (predicted_change * 5)
        score = np.clip(score, 0.0, 1.0)
        
        # Weight by confidence
        score = 0.5 + (score - 0.5) * confidence
        
        return float(score)


# Global instance (lazy loaded)
_kronos_instance = None

def get_kronos_predictor(model_name: str = "NeoQuasar/Kronos-small") -> KronosPredictor:
    """
    Get global Kronos predictor instance (singleton pattern)
    
    Args:
        model_name: Model to use (default: NeoQuasar/Kronos-small)
        
    Returns:
        KronosPredictor instance
    """
    global _kronos_instance
    
    if _kronos_instance is None:
        _kronos_instance = KronosPredictor(model_name=model_name)
    
    return _kronos_instance


# Convenience function for quick predictions
def predict_price(df: pd.DataFrame, horizon: int = 7) -> Dict:
    """
    Quick price prediction using Kronos
    
    Args:
        df: DataFrame with OHLCV data
        horizon: Days ahead to predict
        
    Returns:
        Dict with prediction results
    """
    predictor = get_kronos_predictor()
    return predictor.predict(df, horizon=horizon)
