#!/usr/bin/env python3
"""
Test script to verify check_null_columns display alignment fixes for Google Colab.
This simulates the rendering environment to ensure proper box alignment.
"""

import pandas as pd
import numpy as np

# Create test dataset with various null patterns
def create_test_data():
    """Create a test dataset with different null percentages."""
    np.random.seed(42)
    data = {
        'clean_column': range(1000),  # 0% nulls
        'minor_nulls': [None if i % 20 == 0 else i for i in range(1000)],  # 5% nulls
        'warning_level': [None if i % 10 == 0 else i for i in range(1000)],  # 10% nulls  
        'critical_nulls': [None if i % 3 == 0 else i for i in range(1000)],  # 33% nulls
        'mostly_null': [i if i % 10 == 0 else None for i in range(1000)]  # 90% nulls
    }
    return pd.DataFrame(data)

def test_null_display():
    """Test the check_null_columns function with various thresholds."""
    print("🧪 Testing check_null_columns display alignment...")
    
    # Create test data
    df = create_test_data()
    
    print(f"📊 Dataset shape: {df.shape}")
    print(f"💾 Memory usage: {df.memory_usage(deep=True).sum() / 1024:.2f} KB")
    
    # Import the function
    try:
        from edaflow.analysis.core import check_null_columns
        
        print("\n" + "="*80)
        print("🔍 TESTING WITH THRESHOLD 15%")
        print("="*80)
        
        # Test with threshold 15%
        result = check_null_columns(df, threshold=15)
        
        print("\n" + "="*80)
        print("🔍 TESTING WITH THRESHOLD 5%") 
        print("="*80)
        
        # Test with lower threshold
        result2 = check_null_columns(df, threshold=5)
        
        print("\n✅ Display alignment test completed!")
        print("📋 Results should show properly aligned boxes without jagged edges.")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing display: {e}")
        return False

if __name__ == "__main__":
    success = test_null_display()
    if success:
        print("\n🎯 Test completed successfully!")
        print("📝 Check that the Rich Panel boxes display cleanly without jagged borders.")
    else:
        print("\n💥 Test failed!")
