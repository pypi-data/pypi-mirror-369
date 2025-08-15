#!/usr/bin/env python3
"""
TestPyPI Installation and Validation Script
==========================================

This script tests the installation of edaflow from TestPyPI and validates
the new API consistency features.
"""

import subprocess
import sys
import os

def test_testpypi_installation():
    """Test installation from TestPyPI"""
    print("🧪 TESTING EDAFLOW v0.14.2 FROM TESTPYPI")
    print("=" * 50)
    
    # Create a temporary virtual environment for testing
    print("\n📦 Step 1: Creating test environment...")
    test_env = "test_edaflow_env"
    
    try:
        # Create virtual environment
        subprocess.run([sys.executable, "-m", "venv", test_env], check=True)
        
        # Determine activation script path
        if os.name == 'nt':  # Windows
            activate_script = os.path.join(test_env, "Scripts", "activate.bat")
            pip_path = os.path.join(test_env, "Scripts", "pip.exe")
            python_path = os.path.join(test_env, "Scripts", "python.exe")
        else:  # Unix/Linux/Mac
            activate_script = os.path.join(test_env, "bin", "activate")
            pip_path = os.path.join(test_env, "bin", "pip")
            python_path = os.path.join(test_env, "bin", "python")
        
        print("✅ Test environment created")
        
        # Install from TestPyPI
        print("\n📥 Step 2: Installing from TestPyPI...")
        install_cmd = [
            pip_path, "install", "-i", "https://test.pypi.org/simple/",
            "--extra-index-url", "https://pypi.org/simple/",
            "edaflow==0.14.2"
        ]
        
        result = subprocess.run(install_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Installation failed: {result.stderr}")
            return False
        
        print("✅ Installation successful")
        
        # Test the API consistency features
        print("\n🧪 Step 3: Testing API consistency...")
        
        test_script = '''
import pandas as pd
import numpy as np
from sklearn.datasets import make_classification
import edaflow.ml as ml

print("Testing edaflow v0.14.2 API consistency...")

# Create test data
X, y = make_classification(n_samples=100, n_features=4, n_informative=3, 
                         n_redundant=1, n_clusters_per_class=1, random_state=42)
df = pd.DataFrame(X, columns=["A", "B", "C", "D"])
df["target"] = y

# Test Pattern 1: experiment_config
config = ml.setup_ml_experiment(df, "target", val_size=0.2, random_state=42, verbose=False)
result1 = ml.validate_ml_data(config, verbose=False)

# Test Pattern 2: X, y (NEW FEATURE)
result2 = ml.validate_ml_data(X=df[["A", "B", "C", "D"]], y=df["target"], 
                            check_missing=True, check_cardinality=True, 
                            check_distributions=True, verbose=False)

print(f"✅ Pattern 1 Quality: {result1['quality_score']}")
print(f"✅ Pattern 2 Quality: {result2['quality_score']}")
print("🎉 API consistency validated!")
print("✅ v0.14.2 working correctly")
'''
        
        # Run the test
        test_result = subprocess.run(
            [python_path, "-c", test_script],
            capture_output=True, text=True
        )
        
        if test_result.returncode == 0:
            print("✅ API consistency test passed!")
            print("Output:", test_result.stdout)
        else:
            print("❌ API consistency test failed!")
            print("Error:", test_result.stderr)
            return False
        
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ TestPyPI installation successful")
        print("✅ API consistency features working")
        print("✅ Ready for production PyPI!")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    
    finally:
        # Cleanup test environment
        print("\n🧹 Cleaning up test environment...")
        try:
            if os.path.exists(test_env):
                subprocess.run(["rmdir", "/s", "/q", test_env], shell=True)
                print("✅ Cleanup complete")
        except:
            print("⚠️ Manual cleanup may be needed for:", test_env)

if __name__ == "__main__":
    print("Run this script after uploading to TestPyPI to validate the package")
    print("Usage: python test_testpypi_install.py")
