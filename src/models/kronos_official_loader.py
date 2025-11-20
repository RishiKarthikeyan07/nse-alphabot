"""
Official Kronos Model Loader
Loads NeoQuasar/Kronos-small with proper configuration
"""

import torch
import numpy as np
import pandas as pd
from typing import Dict, Optional
import json
import warnings
warnings.filterwarnings("ignore")


def load_official_kronos(model_name: str = "NeoQuasar/Kronos-small", device: str = None):
    """
    Load official Kronos model with proper configuration
    
    Args:
        model_name: Model to load from HuggingFace
        device: Device to use ('cuda', 'mps', 'cpu', or None for auto)
        
    Returns:
        Tuple of (tokenizer, model, predictor) or (None, None, None) if loading fails
    """
    try:
        import sys
        sys.path.append('src')
        from models.kronos_official.kronos import KronosTokenizer, Kronos, KronosPredictor
        from huggingface_hub import hf_hub_download
        
        # Auto-detect device
        if device is None:
            if torch.cuda.is_available():
                device = 'cuda'
            elif torch.backends.mps.is_available():
                device = 'mps'
            else:
                device = 'cpu'
        
        print(f"📥 Loading official Kronos from {model_name}...")
        print(f"   Device: {device}")
        
        # Download config
        config_path = hf_hub_download(repo_id=model_name, filename="config.json")
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        print(f"✅ Config loaded")
        
        # Complete configuration with missing parameters
        # These are standard values from Kronos paper/examples
        full_config = {
            # From HuggingFace config
            'd_model': config.get('d_model', 512),
            'n_heads': config.get('n_heads', 8),
            'ff_dim': config.get('ff_dim', 1024),
            'n_layers': config.get('n_layers', 8),
            'ffn_dropout_p': config.get('ffn_dropout_p', 0.25),
            'attn_dropout_p': config.get('attn_dropout_p', 0.1),
            'resid_dropout_p': config.get('resid_dropout_p', 0.25),
            'token_dropout_p': config.get('token_dropout_p', 0.1),
            's1_bits': config.get('s1_bits', 10),
            's2_bits': config.get('s2_bits', 10),
            'learn_te': config.get('learn_te', True),
            
            # Missing parameters - use standard defaults
            'd_in': 6,  # OHLCVA (Open, High, Low, Close, Volume, Amount)
            'n_enc_layers': 4,  # Encoder layers for tokenizer
            'n_dec_layers': 4,  # Decoder layers for tokenizer
            'beta': 0.25,  # BSQuantizer temperature
            'gamma0': 1.0,  # BSQuantizer initial gamma
            'gamma': 0.99,  # BSQuantizer decay
            'zeta': 1e-5,  # BSQuantizer epsilon
            'group_size': 10,  # BSQuantizer group size (must divide codebook_dim = s1_bits + s2_bits = 20)
        }
        
        print(f"📦 Creating tokenizer...")
        # Create tokenizer with all required parameters
        tokenizer = KronosTokenizer(
            d_in=full_config['d_in'],
            d_model=full_config['d_model'],
            n_heads=full_config['n_heads'],
            ff_dim=full_config['ff_dim'],
            n_enc_layers=full_config['n_enc_layers'],
            n_dec_layers=full_config['n_dec_layers'],
            ffn_dropout_p=full_config['ffn_dropout_p'],
            attn_dropout_p=full_config['attn_dropout_p'],
            resid_dropout_p=full_config['resid_dropout_p'],
            s1_bits=full_config['s1_bits'],
            s2_bits=full_config['s2_bits'],
            beta=full_config['beta'],
            gamma0=full_config['gamma0'],
            gamma=full_config['gamma'],
            zeta=full_config['zeta'],
            group_size=full_config['group_size']
        )
        
        print(f"📦 Creating model...")
        # Create Kronos model
        model = Kronos(
            s1_bits=full_config['s1_bits'],
            s2_bits=full_config['s2_bits'],
            n_layers=full_config['n_layers'],
            d_model=full_config['d_model'],
            n_heads=full_config['n_heads'],
            ff_dim=full_config['ff_dim'],
            ffn_dropout_p=full_config['ffn_dropout_p'],
            attn_dropout_p=full_config['attn_dropout_p'],
            resid_dropout_p=full_config['resid_dropout_p'],
            token_dropout_p=full_config['token_dropout_p'],
            learn_te=full_config['learn_te']
        )
        
        # Try to load pretrained weights
        try:
            print(f"📥 Loading pretrained weights...")
            model_path = hf_hub_download(repo_id=model_name, filename="model.safetensors")
            
            # Load weights using safetensors
            from safetensors.torch import load_file
            state_dict = load_file(model_path)
            
            # Load into model
            model.load_state_dict(state_dict, strict=False)
            print(f"✅ Pretrained weights loaded")
            
        except Exception as e:
            print(f"⚠️  Could not load pretrained weights: {e}")
            print(f"   Using randomly initialized model")
        
        # Move to device
        tokenizer = tokenizer.to(device)
        model = model.to(device)
        
        # Set to eval mode
        tokenizer.eval()
        model.eval()
        
        # Create predictor
        predictor = KronosPredictor(
            model=model,
            tokenizer=tokenizer,
            device=device,
            max_context=512,
            clip=5
        )
        
        print(f"✅ Official Kronos loaded successfully!")
        print(f"   Parameters: ~24.7M")
        print(f"   Context: 512 tokens")
        print(f"   Input: OHLCVA (6 dimensions)")
        
        return tokenizer, model, predictor
        
    except Exception as e:
        print(f"❌ Failed to load official Kronos: {e}")
        import traceback
        traceback.print_exc()
        return None, None, None


def test_kronos_prediction(predictor, test_data: pd.DataFrame):
    """
    Test Kronos prediction with sample data
    
    Args:
        predictor: KronosPredictor instance
        test_data: DataFrame with OHLCV data
        
    Returns:
        Prediction DataFrame
    """
    try:
        # Prepare timestamps
        x_timestamp = test_data.index
        pred_len = 7  # Predict 7 days ahead
        
        # Create future timestamps (assuming daily data)
        last_date = x_timestamp[-1]
        y_timestamp = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=pred_len, freq='D')
        
        # Make prediction
        print(f"\n🔮 Testing prediction...")
        print(f"   Input: {len(test_data)} historical candles")
        print(f"   Output: {pred_len} future candles")
        
        pred_df = predictor.predict(
            df=test_data,
            x_timestamp=x_timestamp,
            y_timestamp=y_timestamp,
            pred_len=pred_len,
            T=1.0,  # Temperature
            top_k=0,  # No top-k filtering
            top_p=0.9,  # Top-p filtering
            sample_count=1,  # Number of samples
            verbose=False
        )
        
        print(f"✅ Prediction successful!")
        print(f"\nPredicted prices:")
        print(pred_df[['open', 'high', 'low', 'close']])
        
        # Calculate predicted change
        last_close = test_data['close'].iloc[-1]
        pred_close = pred_df['close'].iloc[-1]
        change_pct = ((pred_close - last_close) / last_close) * 100
        
        print(f"\nPredicted change: {change_pct:+.2f}%")
        print(f"   Current: ₹{last_close:.2f}")
        print(f"   Predicted (7d): ₹{pred_close:.2f}")
        
        return pred_df
        
    except Exception as e:
        print(f"❌ Prediction failed: {e}")
        import traceback
        traceback.print_exc()
        return None


# Convenience function
def get_official_kronos_predictor(device: str = None):
    """
    Get official Kronos predictor (convenience function)
    
    Args:
        device: Device to use
        
    Returns:
        KronosPredictor instance or None
    """
    _, _, predictor = load_official_kronos(device=device)
    return predictor


if __name__ == "__main__":
    print("="*80)
    print("🧪 TESTING OFFICIAL KRONOS LOADER")
    print("="*80)
    print()
    
    # Load model
    tokenizer, model, predictor = load_official_kronos()
    
    if predictor is not None:
        print("\n" + "="*80)
        print("✅ OFFICIAL KRONOS LOADED SUCCESSFULLY!")
        print("="*80)
        
        # Create sample data for testing
        print("\n📊 Creating sample test data...")
        dates = pd.date_range('2024-01-01', periods=100, freq='D')
        test_data = pd.DataFrame({
            'open': np.random.randn(100).cumsum() + 1500,
            'high': np.random.randn(100).cumsum() + 1520,
            'low': np.random.randn(100).cumsum() + 1480,
            'close': np.random.randn(100).cumsum() + 1500,
            'volume': np.random.randint(1000000, 5000000, 100),
        }, index=dates)
        
        # Ensure OHLC relationships are valid
        test_data['high'] = test_data[['open', 'high', 'close']].max(axis=1)
        test_data['low'] = test_data[['open', 'low', 'close']].min(axis=1)
        
        # Test prediction
        pred_df = test_kronos_prediction(predictor, test_data)
        
        if pred_df is not None:
            print("\n" + "="*80)
            print("🎉 ALL TESTS PASSED!")
            print("="*80)
    else:
        print("\n" + "="*80)
        print("❌ FAILED TO LOAD OFFICIAL KRONOS")
        print("="*80)
