"""
Direct test of the issue from the user screenshot.
Test the exact error case: setup_ml_experiment() got an unexpected keyword argument 'X'
"""

import sys
import os
sys.path.insert(0, '.')

# Test the exact pattern that was failing
def test_user_error():
    print("Testing the exact issue from user screenshot...")
    
    try:
        from edaflow.ml.config import setup_ml_experiment
        print("✅ Function imported")
        
        # Simulate the user's failing call pattern
        import pandas as pd
        import numpy as np
        
        # Create sample data like user would have
        np.random.seed(42)
        n_samples = 100
        X = pd.DataFrame({
            'feature1': np.random.randn(n_samples),
            'feature2': np.random.randn(n_samples)
        })
        y = pd.Series(np.random.choice([0, 1], n_samples))
        
        print("✅ Sample data created")
        print(f"X shape: {X.shape}")
        print(f"y shape: {y.shape}")
        
        # This was the failing pattern from the screenshot
        print("🧪 Testing sklearn-style call that was failing...")
        result = setup_ml_experiment(X=X, y=y)
        
        print("✅ SUCCESS! The TypeError has been fixed!")
        print(f"Result keys: {list(result.keys())}")
        print(f"Features: {result['feature_names']}")
        print(f"Target: {result['target_name']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Still failing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🎯 TESTING USER'S EXACT ERROR CASE")
    print("="*50)
    success = test_user_error()
    if success:
        print("\n🎉 PROBLEM FIXED!")
        print("Users can now call setup_ml_experiment(X=X, y=y) without errors!")
    else:
        print("\n💥 Problem still exists")
