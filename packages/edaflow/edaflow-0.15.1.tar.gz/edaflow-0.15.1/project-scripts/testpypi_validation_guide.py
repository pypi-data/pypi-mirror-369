#!/usr/bin/env python3
"""
Simple TestPyPI Validation
==========================
Run this after uploading to TestPyPI to verify installation works.
"""

print("🧪 TESTPYPI VALIDATION GUIDE")
print("=" * 30)

print("\n📋 Step 1: Upload completed? Check output above for success message")
print("📋 Step 2: Install from TestPyPI in a new environment:")
print("   pip install -i https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ edaflow==0.14.2")

print("\n📋 Step 3: Test the new API features:")
test_code = '''
import pandas as pd
from sklearn.datasets import make_classification
import edaflow.ml as ml

# Create test data
X, y = make_classification(n_samples=50, n_features=3, n_informative=2, 
                         n_redundant=1, n_clusters_per_class=1, random_state=42)
df = pd.DataFrame(X, columns=['A', 'B', 'C'])
df['target'] = y

# Test NEW API pattern (X, y)
result = ml.validate_ml_data(X=df[['A', 'B', 'C']], y=df['target'], verbose=False)
print(f"✅ New API works! Quality: {result['quality_score']}")

# Test original pattern still works
config = ml.setup_ml_experiment(df, 'target', val_size=0.2, random_state=42, verbose=False)
result2 = ml.validate_ml_data(config, verbose=False)
print(f"✅ Original API works! Quality: {result2['quality_score']}")
print("🎉 v0.14.2 API consistency validated!")
'''

print(f"\n{test_code}")

print("\n📋 Step 4: If tests pass, ready for production PyPI:")
print("   python -m twine upload dist/edaflow-0.14.2*")

print("\n🎯 What we're validating:")
print("   ✅ Package installs from TestPyPI")
print("   ✅ New X,y API pattern works")
print("   ✅ Original experiment_config pattern still works") 
print("   ✅ API consistency achieved")
print("   ✅ Ready for production release")
