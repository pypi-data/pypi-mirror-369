#!/usr/bin/env python3
"""
Production PyPI Validation Script
=================================
After upload completes, run this to validate production PyPI installation.
"""

print("🎯 PRODUCTION PYPI VALIDATION")
print("=" * 35)

print("\n📋 Step 1: Check upload completion")
print("   Look for 'Upload complete' message above")

print("\n📋 Step 2: Install from production PyPI (in fresh environment):")
print("   pip install edaflow==0.14.2")

print("\n📋 Step 3: Test the enhanced API:")

validation_code = '''
import pandas as pd  
from sklearn.datasets import make_classification
import edaflow.ml as ml

# Create test data
X, y = make_classification(n_samples=50, n_features=3, n_informative=2, 
                         n_redundant=1, n_clusters_per_class=1, random_state=42)
df = pd.DataFrame(X, columns=['A', 'B', 'C'])
df['target'] = y

print(f"📦 EDAflow Version: {edaflow.__version__}")

# Test NEW API pattern (X, y) - The feature you requested!
result1 = ml.validate_ml_data(X=df[['A', 'B', 'C']], y=df['target'], 
                            check_missing=True, check_cardinality=True, 
                            check_distributions=True, verbose=False)
print(f"✅ NEW API (X,y): Quality = {result1['quality_score']}")

# Test original pattern (backward compatibility)
config = ml.setup_ml_experiment(df, 'target', val_size=0.2, random_state=42, verbose=False)
result2 = ml.validate_ml_data(config, verbose=False)
print(f"✅ Original API: Quality = {result2['quality_score']}")

print("🎉 API CONSISTENCY ACHIEVED!")
print("✅ Both calling patterns work perfectly")
print("✅ Your requested feature is live!")
'''

print(validation_code)

print("\n📋 Step 4: Success indicators:")
print("   ✅ Package installs from PyPI")
print("   ✅ Version shows 0.14.2") 
print("   ✅ Both API patterns work")
print("   ✅ Quality scores generated correctly")

print("\n🎊 If all tests pass:")
print("   🎉 DEPLOYMENT SUCCESSFUL!")
print("   🚀 edaflow v0.14.2 is LIVE on PyPI")
print("   ✅ API consistency feature deployed")
print("   📖 Ready to update documentation/announce")
