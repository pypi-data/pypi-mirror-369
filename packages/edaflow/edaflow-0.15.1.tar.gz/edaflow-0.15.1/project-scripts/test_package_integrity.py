"""
Quick test to verify edaflow v0.15.0 package integrity before publishing
"""

import sys
import importlib.util

def test_package_import():
    """Test that all main modules can be imported"""
    try:
        import edaflow
        print(f"✅ edaflow imported successfully")
        print(f"📦 Version: {edaflow.__version__}")
        
        # Test main functions
        result = edaflow.hello()
        print(f"✅ hello() works: {result}")
        
        # Test ML subpackage
        import edaflow.ml as ml
        print(f"✅ edaflow.ml imported successfully")
        
        # Test some key ML functions exist
        assert hasattr(ml, 'setup_ml_experiment'), "setup_ml_experiment missing"
        assert hasattr(ml, 'compare_models'), "compare_models missing"
        assert hasattr(ml, 'rank_models'), "rank_models missing"
        print(f"✅ Key ML functions exist")
        
        # Test main analysis functions exist
        assert hasattr(edaflow, 'check_null_columns'), "check_null_columns missing"
        assert hasattr(edaflow, 'convert_to_numeric'), "convert_to_numeric missing"
        print(f"✅ Key EDA functions exist")
        
        print(f"\n🎉 Package integrity test: PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Package test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_package_import()
    if success:
        print("\n📦 Ready for PyPI publishing!")
    else:
        print("\n⚠️  Fix issues before publishing")
        sys.exit(1)
