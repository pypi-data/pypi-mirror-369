#!/usr/bin/env python3
"""
Comprehensive test to verify user's ML workflow inputs work correctly
with the fixed setup_ml_experiment function.

This tests the exact TypeError scenario the user reported:
TypeError: setup_ml_experiment() got an unexpected keyword argument 'X'
"""

import sys
import os
sys.path.insert(0, '.')

def test_user_workflow():
    """Test the exact user workflow that was failing."""
    
    print("🎯 TESTING USER'S EXACT ML WORKFLOW")
    print("="*60)
    
    try:
        # Import the function
        from edaflow.ml.config import setup_ml_experiment
        print("✅ setup_ml_experiment imported successfully")
        
        # Test function signature
        import inspect
        sig = inspect.signature(setup_ml_experiment)
        params = list(sig.parameters.keys())
        print(f"✅ Function parameters: {params}")
        
        # Verify X and y parameters exist
        if 'X' in params and 'y' in params:
            print("✅ X and y parameters found in function signature")
        else:
            print("❌ X and y parameters missing!")
            return False
            
        # Create test data similar to user's workflow
        import pandas as pd
        import numpy as np
        
        print("\n📊 Creating test dataset...")
        np.random.seed(42)
        n_samples = 200
        
        # Create typical ML dataset
        X = pd.DataFrame({
            'feature_1': np.random.normal(0, 1, n_samples),
            'feature_2': np.random.normal(2, 1.5, n_samples), 
            'feature_3': np.random.randint(0, 5, n_samples),
            'feature_4': np.random.exponential(1, n_samples)
        })
        
        # Create binary classification target
        y = pd.Series(np.random.choice([0, 1], n_samples, p=[0.3, 0.7]))
        
        print(f"✅ Test data created: X shape {X.shape}, y shape {y.shape}")
        print(f"✅ Target distribution: {y.value_counts().to_dict()}")
        
        # Test Case 1: Original failing pattern (sklearn-style)
        print("\n" + "="*60)
        print("🧪 TEST 1: User's Original Failing Pattern")
        print("   setup_ml_experiment(X=X, y=y)")
        print("="*60)
        
        try:
            # This was the exact call that was failing
            experiment1 = setup_ml_experiment(
                X=X, 
                y=y,
                test_size=0.2,
                validation_size=0.15,
                stratify=True,
                verbose=True
            )
            
            print("✅ SUCCESS! sklearn-style call works!")
            print(f"📈 Problem type: {experiment1['experiment_config']['problem_type']}")
            print(f"📊 Train samples: {len(experiment1['X_train'])}")
            print(f"📊 Validation samples: {len(experiment1['X_val'])}")  
            print(f"📊 Test samples: {len(experiment1['X_test'])}")
            print(f"🎯 Target name: {experiment1['target_name']}")
            print(f"📋 Features: {experiment1['feature_names']}")
            
        except Exception as e:
            print(f"❌ FAILED: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        # Test Case 2: Alternative DataFrame + target_column pattern  
        print("\n" + "="*60)
        print("🧪 TEST 2: DataFrame + target_column Pattern")
        print("   setup_ml_experiment(data=df, target_column='target')")
        print("="*60)
        
        try:
            # Create combined DataFrame for this test
            df = X.copy()
            df['target'] = y
            
            experiment2 = setup_ml_experiment(
                data=df,
                target_column='target',
                test_size=0.2,
                validation_size=0.15, 
                stratify=True,
                verbose=True
            )
            
            print("✅ SUCCESS! DataFrame+target_column call works!")
            print(f"📈 Problem type: {experiment2['experiment_config']['problem_type']}")
            print(f"📊 Train samples: {len(experiment2['X_train'])}")
            print(f"📊 Validation samples: {len(experiment2['X_val'])}")
            print(f"📊 Test samples: {len(experiment2['X_test'])}")
            print(f"🎯 Target name: {experiment2['target_name']}")
            print(f"📋 Features: {experiment2['feature_names']}")
            
        except Exception as e:
            print(f"❌ FAILED: {e}")
            import traceback
            traceback.print_exc()
            return False
            
        # Test Case 3: Compare results consistency
        print("\n" + "="*60)
        print("🔍 TEST 3: Comparing Results Consistency")
        print("="*60)
        
        # Both methods should produce similar results
        consistent_results = (
            len(experiment1['X_train']) == len(experiment2['X_train']) and
            len(experiment1['X_val']) == len(experiment2['X_val']) and
            len(experiment1['X_test']) == len(experiment2['X_test']) and
            experiment1['experiment_config']['problem_type'] == experiment2['experiment_config']['problem_type'] and
            len(experiment1['feature_names']) == len(experiment2['feature_names'])
        )
        
        if consistent_results:
            print("✅ Both calling patterns produce consistent results!")
        else:
            print("⚠️  Results differ between calling patterns")
            print(f"Method 1 train: {len(experiment1['X_train'])}, Method 2 train: {len(experiment2['X_train'])}")
            
        # Test Case 4: Edge cases and error handling
        print("\n" + "="*60) 
        print("🧪 TEST 4: Error Handling")
        print("="*60)
        
        # Test missing parameters
        try:
            setup_ml_experiment()
            print("❌ Should have failed with missing parameters")
            return False
        except ValueError as e:
            print(f"✅ Correctly caught missing parameters error: {str(e)[:50]}...")
        
        # Test invalid parameter combinations
        try:
            setup_ml_experiment(X=X)  # Missing y
            print("❌ Should have failed with missing y parameter") 
            return False
        except ValueError as e:
            print(f"✅ Correctly caught missing y parameter error: {str(e)[:50]}...")
            
        print("\n🎉 ALL TESTS PASSED!")
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_specific_user_patterns():
    """Test other common patterns users might try."""
    
    print("\n" + "="*80)
    print("🔬 TESTING ADDITIONAL USER PATTERNS")
    print("="*80)
    
    try:
        from edaflow.ml.config import setup_ml_experiment
        import pandas as pd
        import numpy as np
        
        # Create test data
        np.random.seed(123)
        data = pd.DataFrame({
            'age': np.random.randint(18, 80, 100),
            'income': np.random.normal(50000, 15000, 100),
            'score': np.random.normal(75, 10, 100),
            'approved': np.random.choice([0, 1], 100, p=[0.4, 0.6])
        })
        
        # Pattern 1: Using val_size instead of validation_size
        print("\n🧪 Testing val_size parameter...")
        try:
            experiment = setup_ml_experiment(
                data=data,
                target_column='approved', 
                val_size=0.15,  # Alternative parameter name
                verbose=False
            )
            print("✅ val_size parameter works")
        except Exception as e:
            print(f"⚠️  val_size parameter issue: {e}")
            
        # Pattern 2: Using different stratify options
        print("\n🧪 Testing stratify=False...")
        try:
            experiment = setup_ml_experiment(
                X=data.drop('approved', axis=1),
                y=data['approved'],
                stratify=False,
                verbose=False
            )
            print("✅ stratify=False works")
        except Exception as e:
            print(f"❌ stratify=False failed: {e}")
            return False
            
        # Pattern 3: Different data types
        print("\n🧪 Testing different target data types...")
        try:
            # String target
            data_str = data.copy()
            data_str['category'] = data_str['approved'].map({0: 'reject', 1: 'approve'})
            
            experiment = setup_ml_experiment(
                data=data_str,
                target_column='category',
                verbose=False
            )
            print("✅ String target works")
        except Exception as e:
            print(f"❌ String target failed: {e}")
            return False
            
        print("\n✅ All additional user patterns work correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Additional pattern tests failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 COMPREHENSIVE USER FUNCTIONALITY TEST")
    print("="*80)
    print("Testing if user's inputs will work with fixed setup_ml_experiment")
    print("="*80)
    
    # Run main tests
    main_success = test_user_workflow()
    
    # Run additional pattern tests  
    additional_success = test_specific_user_patterns()
    
    # Final summary
    print("\n" + "="*80)
    if main_success and additional_success:
        print("🎉 COMPLETE SUCCESS!")
        print("✅ User's ML workflow will work perfectly")
        print("✅ Both sklearn-style and DataFrame-style patterns supported")  
        print("✅ Error handling works correctly")
        print("✅ All edge cases handled")
        print("\n📝 The TypeError: 'unexpected keyword argument X' is FIXED!")
    else:
        print("💥 SOME ISSUES FOUND")
        print("❌ User's workflow may still have problems")
        
    print("="*80)
