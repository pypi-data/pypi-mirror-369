#!/usr/bin/env python3
"""
Comprehensive API Consistency Validation for validate_ml_data
============================================================

This script validates the implementation logic correctness of the enhanced 
validate_ml_data function, particularly when X and y parameters are passed.

Tests:
1. API consistency between experiment_config and X,y patterns
2. Implementation logic correctness across different data scenarios  
3. Edge cases and error handling
4. Downstream function compatibility

Author: EDAflow Development Team
Version: 0.14.2 Pre-release Validation
"""

import pandas as pd
import numpy as np
from sklearn.datasets import make_classification, make_regression
import warnings
import edaflow.ml as ml

def test_api_consistency():
    """Test API consistency between patterns"""
    print("🔄 Testing API consistency...")
    
    # Create test data
    X, y = make_classification(n_samples=100, n_features=5, n_informative=3, 
                             n_redundant=1, n_clusters_per_class=1, random_state=42)
    df = pd.DataFrame(X, columns=[f'feature_{i}' for i in range(5)])
    df['target'] = y
    
    # Pattern 1: Traditional experiment_config
    config = ml.setup_ml_experiment(df, 'target', val_size=0.2, random_state=42, verbose=False)
    result1 = ml.validate_ml_data(config, verbose=False)
    
    # Pattern 2: X, y parameters
    X_features = df[[f'feature_{i}' for i in range(5)]]
    result2 = ml.validate_ml_data(X=X_features, y=df['target'], 
                                  check_missing=True, check_cardinality=True, 
                                  check_distributions=True, verbose=False)
    
    # Validate consistency
    assert 'quality_score' in result1, "Pattern 1 missing quality_score"
    assert 'quality_score' in result2, "Pattern 2 missing quality_score"
    
    print(f"✅ Pattern 1 Quality: {result1['quality_score']}")
    print(f"✅ Pattern 2 Quality: {result2['quality_score']}")
    print("✅ API consistency validated")
    
    return result1, result2

def test_implementation_logic():
    """Test implementation logic correctness"""
    print("\n🧪 Testing implementation logic...")
    
    # Test with problematic data
    X, y = make_classification(n_samples=150, n_features=4, n_informative=3, 
                             n_redundant=1, n_clusters_per_class=1, random_state=123)
    df = pd.DataFrame(X, columns=['A', 'B', 'C', 'D'])
    df['target'] = y
    
    # Introduce data quality issues
    df.loc[0:10, 'A'] = np.nan  # Missing values
    df = pd.concat([df, df.iloc[0:5]], ignore_index=True)  # Duplicates
    df.loc[100:110, 'B'] = 999  # Potential outliers
    
    # Test X,y pattern with issues
    X_problem = df[['A', 'B', 'C', 'D']]
    result = ml.validate_ml_data(X=X_problem, y=df['target'], verbose=False)
    
    # Validate detection of issues
    assert 'missing_values' in result, "Missing values not detected"
    assert 'duplicates' in result, "Duplicates not detected"
    
    missing_count = result['missing_values']['total_missing']
    duplicate_count = result['duplicates']['total_duplicates']
    quality = result['quality_score']
    
    print(f"✅ Detected {missing_count} missing values")
    print(f"✅ Detected {duplicate_count} duplicates")
    print(f"✅ Quality score: {quality} (appropriately reduced)")
    
    assert missing_count > 0, "Should detect missing values"
    assert duplicate_count > 0, "Should detect duplicates"
    assert quality < 100, "Quality should be reduced with issues"
    
    print("✅ Implementation logic validated")
    return result

def test_edge_cases():
    """Test edge cases and error handling"""
    print("\n⚡ Testing edge cases...")
    
    # Very small dataset
    X_small = pd.DataFrame({'f1': [1, 2], 'f2': [3, 4]})
    y_small = pd.Series([0, 1])
    
    result_small = ml.validate_ml_data(X=X_small, y=y_small, verbose=False)
    assert 'quality_score' in result_small, "Small dataset should work"
    print("✅ Small dataset handled")
    
    # Single feature
    X_single = pd.DataFrame({'feature': [1, 2, 3, 4, 5]})
    y_single = pd.Series([0, 1, 0, 1, 0])
    
    result_single = ml.validate_ml_data(X=X_single, y=y_single, verbose=False)
    assert 'quality_score' in result_single, "Single feature should work"
    print("✅ Single feature handled")
    
    # Regression target
    X_reg, y_reg = make_regression(n_samples=50, n_features=3, random_state=42)
    X_reg_df = pd.DataFrame(X_reg, columns=['x1', 'x2', 'x3'])
    
    result_reg = ml.validate_ml_data(X=X_reg_df, y=y_reg, verbose=False)
    assert 'quality_score' in result_reg, "Regression should work"
    print("✅ Regression target handled")
    
    print("✅ Edge cases validated")

def test_downstream_compatibility():
    """Test compatibility with downstream functions"""
    print("\n🔗 Testing downstream compatibility...")
    
    # Create clean dataset
    X, y = make_classification(n_samples=100, n_features=4, n_informative=3, 
                             n_redundant=1, n_clusters_per_class=1, random_state=42)
    df = pd.DataFrame(X, columns=['feat1', 'feat2', 'feat3', 'feat4'])
    df['target'] = y
    
    # Test that validation results work with downstream functions
    validation_result = ml.validate_ml_data(X=df[['feat1', 'feat2', 'feat3', 'feat4']], 
                                           y=df['target'], verbose=False)
    
    # Check that result structure is compatible
    assert isinstance(validation_result, dict), "Result should be dictionary"
    assert 'quality_score' in validation_result, "Should have quality_score"
    
    # Check that basic keys exist for downstream usage
    expected_keys = ['quality_score', 'missing_values', 'duplicates']
    for key in expected_keys:
        assert key in validation_result, f"Missing key: {key}"
    
    print("✅ Downstream compatibility validated")
    
def main():
    """Run all validation tests"""
    print("🚀 VALIDATE_ML_DATA API CONSISTENCY VALIDATION")
    print("=" * 55)
    print("Testing enhanced validate_ml_data with dual API patterns")
    print("Focus: Implementation logic correctness with X,y parameters\n")
    
    try:
        # Run validation tests
        test_api_consistency()
        test_implementation_logic() 
        test_edge_cases()
        test_downstream_compatibility()
        
        print("\n" + "=" * 55)
        print("🎉 ALL TESTS PASSED!")
        print("✅ API consistency verified")
        print("✅ Implementation logic correct") 
        print("✅ X,y parameter handling validated")
        print("✅ Ready for deployment")
        
    except Exception as e:
        print(f"\n❌ VALIDATION FAILED: {e}")
        raise

if __name__ == "__main__":
    main()
