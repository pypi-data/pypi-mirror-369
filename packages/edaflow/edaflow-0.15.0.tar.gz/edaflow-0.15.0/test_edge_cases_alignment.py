#!/usr/bin/env python3
"""
Edge case test for check_null_columns alignment fixes.
"""

import pandas as pd
import numpy as np

def test_edge_cases():
    """Test edge cases that might cause display issues."""
    
    print("🧪 Testing edge cases for display alignment...")
    
    from edaflow.analysis.core import check_null_columns
    
    # Test 1: All clean data
    print("\n" + "="*60)
    print("📋 TEST 1: All Clean Data")
    print("="*60)
    
    clean_df = pd.DataFrame({
        'col1': range(100),
        'col2': ['test'] * 100,
        'col3': [1.5] * 100
    })
    
    result1 = check_null_columns(clean_df, threshold=5)
    
    # Test 2: All null data
    print("\n" + "="*60)
    print("📋 TEST 2: All Null Data")
    print("="*60)
    
    null_df = pd.DataFrame({
        'all_null1': [None] * 50,
        'all_null2': [None] * 50
    })
    
    result2 = check_null_columns(null_df, threshold=10)
    
    # Test 3: Single column
    print("\n" + "="*60)
    print("📋 TEST 3: Single Column")
    print("="*60)
    
    single_df = pd.DataFrame({
        'single_col': [1, 2, None, 4, None]
    })
    
    result3 = check_null_columns(single_df, threshold=30)
    
    print("\n✅ All edge case tests completed!")
    return True

if __name__ == "__main__":
    test_edge_cases()
    print("\n🎯 Edge case testing successful!")
    print("📝 All display boxes should be properly aligned.")
