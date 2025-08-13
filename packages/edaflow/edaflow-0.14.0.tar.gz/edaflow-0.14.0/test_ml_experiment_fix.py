#!/usr/bin/env python3
"""
Test script to verify that setup_ml_experiment works with both calling patterns.
This addresses the TypeError: setup_ml_experiment() got an unexpected keyword argument 'X'
"""

import pandas as pd
import numpy as np
import sys
import os

# Add the parent directory to the path to import edaflow
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import edaflow.ml as ml

def test_both_calling_patterns():
    """Test both DataFrame+target_column and X+y calling patterns."""
    
    print("🧪 Testing setup_ml_experiment calling patterns...")
    
    # Create sample data
    np.random.seed(42)
    data = {
        'feature1': np.random.randn(100),
        'feature2': np.random.randn(100),
        'feature3': np.random.randint(0, 5, 100),
        'target': np.random.choice([0, 1], 100, p=[0.3, 0.7])
    }
    df = pd.DataFrame(data)
    
    print(f"📊 Created test dataset: {df.shape}")
    print(f"🎯 Target distribution:\n{df['target'].value_counts()}")
    
    print("\n" + "="*60)
    print("🔍 METHOD 1: DataFrame + target_column (recommended)")
    print("="*60)
    
    try:
        # Method 1: Standard edaflow pattern
        experiment1 = ml.setup_ml_experiment(
            df, 
            target_column='target',
            test_size=0.20,
            val_size=0.15,
            stratify=True,
            verbose=True
        )
        
        print("✅ Method 1 SUCCESS!")
        print(f"📈 Problem type: {experiment1['experiment_config']['problem_type']}")
        print(f"📋 Features: {len(experiment1['feature_names'])}")
        print(f"🎯 Target: {experiment1['target_name']}")
        
    except Exception as e:
        print(f"❌ Method 1 FAILED: {e}")
        return False
    
    print("\n" + "="*60)
    print("🔍 METHOD 2: Sklearn-style X + y (also supported)")
    print("="*60)
    
    try:
        # Method 2: Sklearn-style pattern  
        X = df.drop('target', axis=1)
        y = df['target']
        
        experiment2 = ml.setup_ml_experiment(
            X=X,
            y=y,
            test_size=0.20,
            validation_size=0.15,
            stratify=True,
            verbose=True
        )
        
        print("✅ Method 2 SUCCESS!")
        print(f"📈 Problem type: {experiment2['experiment_config']['problem_type']}")
        print(f"📋 Features: {len(experiment2['feature_names'])}")
        print(f"🎯 Target: {experiment2['target_name']}")
        
    except Exception as e:
        print(f"❌ Method 2 FAILED: {e}")
        return False
    
    print("\n" + "="*60)
    print("🔍 COMPARING RESULTS")
    print("="*60)
    
    # Compare key results
    print(f"Method 1 train samples: {len(experiment1['X_train'])}")
    print(f"Method 2 train samples: {len(experiment2['X_train'])}")
    
    print(f"Method 1 features: {experiment1['feature_names']}")
    print(f"Method 2 features: {experiment2['feature_names']}")
    
    # Verify both methods produce consistent results
    if (len(experiment1['X_train']) == len(experiment2['X_train']) and
        experiment1['feature_names'] == experiment2['feature_names'] and
        experiment1['experiment_config']['problem_type'] == experiment2['experiment_config']['problem_type']):
        print("✅ Both methods produce consistent results!")
        return True
    else:
        print("❌ Methods produce inconsistent results!")
        return False

def test_error_cases():
    """Test error handling for invalid inputs."""
    
    print("\n" + "="*60)
    print("🔍 TESTING ERROR CASES")
    print("="*60)
    
    # Test missing parameters
    try:
        ml.setup_ml_experiment()
        print("❌ Should have failed with missing parameters")
        return False
    except ValueError as e:
        print(f"✅ Correctly caught error for missing parameters: {e}")
    
    # Test invalid target column
    df = pd.DataFrame({'a': [1, 2, 3], 'b': [4, 5, 6]})
    try:
        ml.setup_ml_experiment(df, target_column='nonexistent')
        print("❌ Should have failed with invalid target column")
        return False
    except ValueError as e:
        print(f"✅ Correctly caught error for invalid target column: {e}")
    
    print("✅ All error cases handled correctly!")
    return True

if __name__ == "__main__":
    print("🎯 TESTING SETUP_ML_EXPERIMENT FIX")
    print("="*80)
    print("This test addresses the TypeError: got an unexpected keyword argument 'X'")
    print("="*80)
    
    success1 = test_both_calling_patterns()
    success2 = test_error_cases()
    
    if success1 and success2:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ setup_ml_experiment now supports both calling patterns:")
        print("   1. ml.setup_ml_experiment(df, target_column='target')")
        print("   2. ml.setup_ml_experiment(X=X, y=y)")
        print("\n📝 Users can now use either pattern without errors!")
    else:
        print("\n💥 SOME TESTS FAILED!")
        sys.exit(1)
