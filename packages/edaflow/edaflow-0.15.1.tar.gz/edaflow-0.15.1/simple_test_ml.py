#!/usr/bin/env python3
"""Simple test to check import and basic functionality."""

import sys
import traceback

try:
    print("Testing imports...")
    import edaflow.ml as ml
    print("✅ ML module imported successfully")
    
    print("Available functions in ml module:")
    for attr in dir(ml):
        if not attr.startswith('_'):
            print(f"  - {attr}")
    
    # Check if setup_ml_experiment exists
    if hasattr(ml, 'setup_ml_experiment'):
        print("✅ setup_ml_experiment found")
        
        # Get function signature
        import inspect
        sig = inspect.signature(ml.setup_ml_experiment)
        print(f"Function signature: {sig}")
    else:
        print("❌ setup_ml_experiment NOT found")
        
except Exception as e:
    print(f"❌ Error: {e}")
    traceback.print_exc()
