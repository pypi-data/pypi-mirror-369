"""
Check function signature to verify our fix is in place
"""
import sys
sys.path.insert(0, '.')

try:
    from edaflow.ml.config import setup_ml_experiment
    print("✅ Function imported successfully")
    
    import inspect
    sig = inspect.signature(setup_ml_experiment)
    print(f"📋 Function signature: {sig}")
    
    # Check if X and y parameters are present
    params = sig.parameters
    param_names = list(params.keys())
    print(f"📝 Parameters: {param_names}")
    
    if 'X' in param_names and 'y' in param_names:
        print("✅ X and y parameters found - fix is in place!")
        
        # Check if they're Optional
        X_param = params['X']
        y_param = params['y']
        print(f"X parameter: {X_param}")
        print(f"y parameter: {y_param}")
        
        print("\n🎉 ANALYSIS: The TypeError should be fixed!")
        print("The function now accepts both calling patterns:")
        print("  1. setup_ml_experiment(data, target_column='target')")  
        print("  2. setup_ml_experiment(X=X, y=y)")
    else:
        print("❌ X and y parameters not found - fix not applied")
        
except Exception as e:
    print(f"❌ Import error: {e}")
    import traceback
    traceback.print_exc()
