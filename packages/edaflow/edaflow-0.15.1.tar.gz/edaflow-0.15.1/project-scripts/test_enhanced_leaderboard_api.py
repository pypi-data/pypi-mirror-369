#!/usr/bin/env python3
"""
Test Enhanced compare_models and display_leaderboard API
=======================================================
Testing the enhanced API to support the user's requested usage pattern
"""

import pandas as pd
import numpy as np
from sklearn.datasets import make_classification
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import edaflow.ml as ml

# Test configuration
SEED = 42
SCORING = 'accuracy'
PRIMARY = 'accuracy'

# Create test data
X, y = make_classification(
    n_samples=500, n_features=10, n_informative=8, n_redundant=1, 
    n_clusters_per_class=1, random_state=SEED
)

# Split the data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=SEED, stratify=y
)

print("🧪 TESTING ENHANCED compare_models API")
print("=" * 45)
print(f"Training samples: {len(X_train)}")
print(f"Test samples: {len(X_test)}")

try:
    # Define models as requested
    models = {
        "LogReg": LogisticRegression(max_iter=1000, class_weight="balanced", random_state=SEED),
        "RandomForest": RandomForestClassifier(n_estimators=300, class_weight="balanced", random_state=SEED),
    }

    # Simulate XGBoost availability check
    HAS_XGB = False  # Set to True if you have XGBoost installed
    if HAS_XGB:
        from xgboost import XGBClassifier
        models["XGBoost"] = XGBClassifier(
            tree_method="hist", enable_categorical=False, random_state=SEED
        )
    
    print(f"\n📊 Models to test: {list(models.keys())}")
    
    # Fit models
    print("\n🏋️ Fitting models...")
    for name, model in models.items():
        print(f"  - Fitting {name}...")
        model.fit(X_train, y_train)
    
    # Test the enhanced compare_models function
    print("\n🏆 Running model comparison...")
    comparison_results = ml.compare_models(
        models=models,
        X_train=X_train, y_train=y_train,
        X_test=X_test,   y_test=y_test,
        cv_folds=5,
        scoring=SCORING,
        verbose=True
    )
    
    print("\n📋 Comparison Results:")
    print(comparison_results)
    
    # Test the enhanced display_leaderboard function
    print("\n🎯 Testing display_leaderboard...")
    result = ml.display_leaderboard(
        comparison_results=comparison_results,
        sort_by=PRIMARY, 
        ascending=False, 
        show_std=True, 
        highlight_best=True
    )
    
    print("\n✅ SUCCESS: Enhanced API working correctly!")
    print("✅ compare_models supports X_test, y_test parameters")
    print("✅ compare_models supports cv_folds and scoring parameters") 
    print("✅ display_leaderboard supports comparison_results parameter")
    print("✅ display_leaderboard supports sort_by, ascending, show_std parameters")
    print("🎉 User's requested API pattern is now supported!")
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
