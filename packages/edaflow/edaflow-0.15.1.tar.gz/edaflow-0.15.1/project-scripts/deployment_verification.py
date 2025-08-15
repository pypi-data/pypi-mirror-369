#!/usr/bin/env python3
"""
Deployment Verification Script for edaflow v0.14.0
==================================================

This script verifies that our package is ready for deployment and tests
the key ML workflow enhancements that were implemented.
"""

import sys
import os
import subprocess
import importlib.util

def test_package_installation():
    """Test that edaflow can be imported with the new version."""
    try:
        import edaflow
        print(f"✅ edaflow imported successfully")
        print(f"   Version: {edaflow.__version__}")
        return True
    except Exception as e:
        print(f"❌ Failed to import edaflow: {e}")
        return False

def test_ml_module():
    """Test that the ML module components can be imported."""
    try:
        from edaflow.ml import setup_ml_experiment, compare_models, optimize_hyperparameters
        print("✅ ML module components imported successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to import ML components: {e}")
        return False

def test_new_parameters():
    """Test the new parameter support in ML functions."""
    try:
        import pandas as pd
        import numpy as np
        from sklearn.datasets import make_classification
        from edaflow.ml import setup_ml_experiment
        
        # Create sample data
        X, y = make_classification(n_samples=100, n_features=5, n_classes=2, random_state=42)
        df = pd.DataFrame(X, columns=[f'feature_{i}' for i in range(X.shape[1])])
        df['target'] = y
        
        # Test 1: Original parameter style (backward compatibility)
        print("  Testing backward compatibility...")
        result1 = setup_ml_experiment(df, 'target', test_size=0.3, random_state=42)
        
        # Test 2: New parameters (val_size, experiment_name)
        print("  Testing new parameters...")
        result2 = setup_ml_experiment(
            df, 'target', 
            test_size=0.2, 
            val_size=0.15,
            experiment_name="deployment_test",
            random_state=42
        )
        
        # Verify results
        if len(result1) == 4 and len(result2) == 6:  # X_train, X_test, y_train, y_test vs X_train, X_val, X_test, y_train, y_val, y_test
            print("✅ Parameter functionality working correctly")
            print(f"   Original call returns: {len(result1)} objects")
            print(f"   Enhanced call returns: {len(result2)} objects")
            print(f"   Validation set size: {len(result2[1])} samples")
            return True
        else:
            print(f"❌ Unexpected return structure: {len(result1)}, {len(result2)}")
            return False
            
    except Exception as e:
        print(f"❌ Parameter test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_build_files():
    """Check that the distribution files were created correctly."""
    dist_dir = "dist"
    v014_files = [f for f in os.listdir(dist_dir) if "0.14.0" in f]
    
    if len(v014_files) >= 2:  # Should have wheel and tar.gz
        print("✅ Build files present for v0.14.0:")
        for f in v014_files:
            print(f"   {f}")
        return True
    else:
        print(f"❌ Missing build files. Found: {v014_files}")
        return False

def check_version_consistency():
    """Check that version is consistent across files."""
    try:
        # Check pyproject.toml
        with open("pyproject.toml", 'r') as f:
            pyproject_content = f.read()
            if 'version = "0.14.0"' in pyproject_content:
                print("✅ pyproject.toml version: 0.14.0")
            else:
                print("❌ pyproject.toml version mismatch")
                return False
        
        # Check __init__.py
        import edaflow
        if edaflow.__version__ == "0.14.0":
            print("✅ __init__.py version: 0.14.0")
        else:
            print(f"❌ __init__.py version mismatch: {edaflow.__version__}")
            return False
            
        return True
    except Exception as e:
        print(f"❌ Version check failed: {e}")
        return False

def main():
    """Run all deployment verification tests."""
    print("🚀 edaflow v0.14.0 Deployment Verification")
    print("=" * 50)
    
    tests = [
        ("Package Installation", test_package_installation),
        ("ML Module Import", test_ml_module),
        ("New Parameters", test_new_parameters),
        ("Build Files", check_build_files),
        ("Version Consistency", check_version_consistency)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 {test_name}:")
        try:
            if test_func():
                passed += 1
            else:
                print(f"   ⚠️  Test failed")
        except Exception as e:
            print(f"   ❌ Test error: {e}")
    
    print(f"\n📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Package ready for deployment.")
        return True
    else:
        print("❌ Some tests failed. Please review before deployment.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
