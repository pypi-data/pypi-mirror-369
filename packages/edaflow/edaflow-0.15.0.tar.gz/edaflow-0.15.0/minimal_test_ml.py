import sys
import os
sys.path.insert(0, '.')

try:
    from edaflow.ml.config import setup_ml_experiment
    print("✅ Function imported successfully")
    
    # Test minimal call
    import pandas as pd
    df = pd.DataFrame({'a': [1, 2, 3], 'target': [0, 1, 0]})
    
    result = setup_ml_experiment(df, target_column='target', verbose=False)
    print("✅ Function executed successfully")
    print(f"Keys in result: {list(result.keys())}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
