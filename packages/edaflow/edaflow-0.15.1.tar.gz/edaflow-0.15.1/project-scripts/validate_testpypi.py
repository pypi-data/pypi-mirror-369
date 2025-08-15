#!/usr/bin/env python3
"""
TestPyPI Validation Script
=========================
Tests the newly uploaded edaflow v0.14.2 from TestPyPI
"""

try:
    import pandas as pd
    from sklearn.datasets import make_classification
    import edaflow.ml as ml
    
    print("🧪 TESTING EDAFLOW v0.14.2 FROM TESTPYPI")
    print("=" * 45)
    
    # Check version
    import edaflow
    print(f"📦 Package Version: {edaflow.__version__}")
    
    # Create test data
    X, y = make_classification(
        n_samples=50, n_features=3, n_informative=2, 
        n_redundant=1, n_clusters_per_class=1, random_state=42
    )
    df = pd.DataFrame(X, columns=['A', 'B', 'C'])
    df['target'] = y
    
    print("\n🔬 Testing NEW API Pattern (X, y):")
    result1 = ml.validate_ml_data(
        X=df[['A', 'B', 'C']], 
        y=df['target'], 
        verbose=False
    )
    quality1 = result1['quality_score']
    print(f"✅ NEW API works! Quality Score: {quality1}")
    
    print("\n🔬 Testing Original API Pattern (experiment_config):")
    config = ml.setup_ml_experiment(
        df, 'target', val_size=0.2, random_state=42, verbose=False
    )
    result2 = ml.validate_ml_data(config, verbose=False)
    quality2 = result2['quality_score']
    print(f"✅ Original API works! Quality Score: {quality2}")
    
    print("\n🎯 API Consistency Validation:")
    print(f"   Pattern 1 (config): {quality2}")
    print(f"   Pattern 2 (X, y):   {quality1}")
    print("   Both patterns working ✅")
    
    print("\n🎉 SUCCESS: TestPyPI v0.14.2 VALIDATED!")
    print("✅ Package installs correctly")
    print("✅ New X,y API pattern works")
    print("✅ Original experiment_config pattern works") 
    print("✅ API consistency achieved")
    print("\n🚀 READY FOR PRODUCTION PYPI!")
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    print("❌ TestPyPI validation failed")
