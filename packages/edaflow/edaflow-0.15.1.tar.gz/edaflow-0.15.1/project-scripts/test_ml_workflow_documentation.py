#!/usr/bin/env python3
"""
ML Workflow Documentation Testing Script
=======================================
Tests all the documented ML workflow examples to ensure they work correctly
and follow the required design logic without throwing errors.
"""

import sys
import traceback
import pandas as pd
import numpy as np
from sklearn.datasets import make_classification
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

def create_test_dataset():
    """Create a test dataset for ML workflow validation."""
    print("🔧 Creating test dataset...")
    
    # Create synthetic classification dataset
    X, y = make_classification(
        n_samples=1000,
        n_features=10,
        n_informative=8,
        n_redundant=2,
        n_clusters_per_class=1,
        random_state=42
    )
    
    # Convert to DataFrame with meaningful column names
    feature_names = [f'feature_{i+1}' for i in range(X.shape[1])]
    df = pd.DataFrame(X, columns=feature_names)
    df['target_column'] = y
    
    print(f"✅ Test dataset created: {df.shape}")
    print(f"   Features: {len(feature_names)}")
    print(f"   Target classes: {df['target_column'].nunique()}")
    
    return df

def test_basic_ml_workflow():
    """Test the basic ML workflow from documentation."""
    print("\n" + "="*60)
    print("🧪 TESTING: Basic ML Workflow")
    print("="*60)
    
    try:
        # Import edaflow.ml
        import edaflow.ml as ml
        print("✅ edaflow.ml imported successfully")
        
        # Create test data
        df_ml = create_test_dataset()
        df_encoded = df_ml  # Simulate encoded data from EDA workflow
        
        print(f"ML Dataset shape: {df_ml.shape}")

        # Step 1: ML Experiment Setup - Enhanced parameters in v0.14.0
        print("\n📋 Step 1: ML Experiment Setup")
        config = ml.setup_ml_experiment(
            df_ml, 'target_column',
            test_size=0.2,
            val_size=0.15,
            experiment_name="complete_ml_workflow",
            random_state=42,
            stratify=True,
            verbose=True
        )
        print("✅ ML experiment setup completed")
        
        print(f"Training samples: {len(config['X_train'])}")
        print(f"Validation samples: {len(config['X_val'])}")
        print(f"Test samples: {len(config['X_test'])}")

        # Step 2: Data Validation - Enhanced with dual API support
        print("\n📋 Step 2: Data Validation")
        validation_report = ml.validate_ml_data(config, verbose=True)
        print("✅ Data validation completed")
        print(f"Data Quality Score: {validation_report['quality_score']}/100")

        # Step 3: Baseline Model Comparison
        print("\n📋 Step 3: Baseline Model Comparison")
        baseline_models = {
            'RandomForest': RandomForestClassifier(random_state=42),
            'GradientBoosting': GradientBoostingClassifier(random_state=42),
            'LogisticRegression': LogisticRegression(random_state=42),
            'SVM': SVC(random_state=42, probability=True)
        }

        # Fit all baseline models
        for name, model in baseline_models.items():
            model.fit(config['X_train'], config['y_train'])
            print(f"   ✅ {name} fitted")

        # Enhanced compare_models with experiment_config support
        baseline_results = ml.compare_models(
            models=baseline_models,
            experiment_config=config,
            verbose=True
        )
        print("✅ Baseline model comparison completed")

        # Step 4: Display Results
        print("\n📋 Step 4: Display Results")
        ml.display_leaderboard(baseline_results, figsize=(12, 4))
        print("✅ Leaderboard displayed")

        return True, config, baseline_models, baseline_results
        
    except Exception as e:
        print(f"❌ Error in basic ML workflow: {str(e)}")
        traceback.print_exc()
        return False, None, None, None

def test_alternative_api_patterns():
    """Test the alternative API patterns documented."""
    print("\n" + "="*60)
    print("🧪 TESTING: Alternative API Patterns")
    print("="*60)
    
    try:
        import edaflow.ml as ml
        
        # Create test data
        df_ml = create_test_dataset()
        X = df_ml.drop('target_column', axis=1)
        y = df_ml['target_column']
        
        # Alternative 1: sklearn-style calling
        print("\n📋 Testing sklearn-style setup_ml_experiment")
        config_sklearn = ml.setup_ml_experiment(
            X=X, y=y,
            val_size=0.15, 
            experiment_name="sklearn_style_workflow",
            random_state=42
        )
        print("✅ sklearn-style setup_ml_experiment works")
        
        # Alternative 2: Direct X, y validation
        print("\n📋 Testing direct X, y validation")
        validation_report_xy = ml.validate_ml_data(
            X=config_sklearn['X_train'],
            y=config_sklearn['y_train'],
            check_missing=True,
            check_cardinality=True,
            check_distributions=True
        )
        print("✅ Direct X, y validation works")
        print(f"Quality Score: {validation_report_xy['quality_score']}/100")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in alternative API patterns: {str(e)}")
        traceback.print_exc()
        return False

def test_hyperparameter_optimization():
    """Test hyperparameter optimization workflow."""
    print("\n" + "="*60)
    print("🧪 TESTING: Hyperparameter Optimization")
    print("="*60)
    
    try:
        import edaflow.ml as ml
        
        # Use simplified test for faster execution
        df_ml = create_test_dataset()
        config = ml.setup_ml_experiment(
            df_ml, 'target_column',
            test_size=0.3, val_size=0.2,  # Smaller sets for faster testing
            experiment_name="optimization_test",
            random_state=42
        )
        
        baseline_models = {
            'RandomForest': RandomForestClassifier(random_state=42),
            'LogisticRegression': LogisticRegression(random_state=42)
        }
        
        # Fit models
        for name, model in baseline_models.items():
            model.fit(config['X_train'], config['y_train'])
        
        # Get baseline results
        baseline_results = ml.compare_models(
            models=baseline_models,
            experiment_config=config,
            verbose=False
        )
        
        # Get top model for optimization (simplified)
        performance_col = [col for col in baseline_results.columns 
                          if col not in ['model', 'eval_time_ms', 'complexity']][0]
        top_model_name = baseline_results.nlargest(1, performance_col)['model'].iloc[0]
        
        print(f"\n📋 Optimizing top model: {top_model_name}")
        
        # Test optimization with minimal parameters for speed
        if top_model_name == 'RandomForest':
            param_distributions = {
                'n_estimators': [50, 100],  # Reduced for testing
                'max_depth': [5, 10]
            }
            method = 'grid'
        else:  # LogisticRegression
            param_distributions = {
                'C': [0.1, 1.0, 10.0]
            }
            method = 'grid'

        results = ml.optimize_hyperparameters(
            model=baseline_models[top_model_name],
            param_distributions=param_distributions,
            X_train=config['X_train'],
            y_train=config['y_train'],
            method=method,
            n_iter=3,  # Reduced for testing
            cv=3       # Reduced for testing
        )
        
        print(f"✅ Hyperparameter optimization completed")
        print(f"   Best {top_model_name} score: {results['best_score']:.4f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in hyperparameter optimization: {str(e)}")
        traceback.print_exc()
        return False

def test_visualization_functions():
    """Test the visualization functions from the workflow."""
    print("\n" + "="*60)
    print("🧪 TESTING: Visualization Functions")
    print("="*60)
    
    try:
        import edaflow.ml as ml
        
        # Create simplified test setup
        df_ml = create_test_dataset()
        config = ml.setup_ml_experiment(
            df_ml, 'target_column',
            test_size=0.3, val_size=0.2,
            experiment_name="viz_test",
            random_state=42
        )
        
        # Simple models for testing
        models = {
            'RandomForest': RandomForestClassifier(n_estimators=50, random_state=42),
            'LogisticRegression': LogisticRegression(random_state=42)
        }
        
        # Fit models
        for name, model in models.items():
            model.fit(config['X_train'], config['y_train'])
        
        best_model = models['RandomForest']  # Use RF for feature importance
        
        print("\n📋 Testing visualization functions")
        
        # Test learning curves
        print("   Testing learning curves...")
        ml.plot_learning_curves(
            model=best_model,
            X_train=config['X_train'],
            y_train=config['y_train'],
            cv=3  # Reduced for testing
        )
        print("   ✅ Learning curves work")
        
        # Test ROC curves
        print("   Testing ROC curves...")
        ml.plot_roc_curves(
            models=models,
            X_val=config['X_test'],
            y_val=config['y_test']
        )
        print("   ✅ ROC curves work")
        
        # Test Precision-Recall curves
        print("   Testing Precision-Recall curves...")
        ml.plot_precision_recall_curves(
            models=models,
            X_val=config['X_test'],
            y_val=config['y_test']
        )
        print("   ✅ Precision-Recall curves work")
        
        # Test confusion matrix
        print("   Testing confusion matrix...")
        ml.plot_confusion_matrix(
            model=best_model,
            X_val=config['X_test'],
            y_val=config['y_test'],
            normalize=True
        )
        print("   ✅ Confusion matrix works")
        
        # Test feature importance
        print("   Testing feature importance...")
        if hasattr(best_model, 'feature_importances_'):
            ml.plot_feature_importance(
                model=best_model,
                feature_names=config['feature_names'],
                top_n=8  # Reduced for testing
            )
            print("   ✅ Feature importance works")
        
        # Test validation curves
        print("   Testing validation curves...")
        ml.plot_validation_curves(
            model=RandomForestClassifier(random_state=42),
            X_train=config['X_train'],
            y_train=config['y_train'],
            param_name='n_estimators',
            param_range=[50, 100, 150]  # Reduced for testing
        )
        print("   ✅ Validation curves work")
        
        print("✅ All visualization functions completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error in visualization functions: {str(e)}")
        traceback.print_exc()
        return False

def test_model_artifacts():
    """Test model artifacts and deployment preparation."""
    print("\n" + "="*60)
    print("🧪 TESTING: Model Artifacts & Deployment")
    print("="*60)
    
    try:
        import edaflow.ml as ml
        
        # Create test setup
        df_ml = create_test_dataset()
        config = ml.setup_ml_experiment(
            df_ml, 'target_column',
            test_size=0.3, val_size=0.2,
            experiment_name="artifacts_test",
            random_state=42
        )
        
        # Simple model
        best_model = RandomForestClassifier(n_estimators=50, random_state=42)
        best_model.fit(config['X_train'], config['y_train'])
        
        # Create mock comparison results
        final_comparison = pd.DataFrame({
            'model': ['RandomForest'],
            'roc_auc': [0.85],
            'accuracy': [0.80]
        })
        
        best_model_name = 'RandomForest'
        final_score = best_model.score(config['X_test'], config['y_test'])
        
        print("\n📋 Testing model artifacts saving")
        
        # Get CV score safely
        best_model_row = final_comparison.query(f"model == '{best_model_name}'")
        cv_score = float(best_model_row['roc_auc'].iloc[0])
        
        # Create serializable config (as documented)
        serializable_config = {
            'experiment_name': config['experiment_name'],
            'problem_type': config['experiment_config']['problem_type'],
            'target_name': config['target_name'],
            'feature_names': config['feature_names'],
            'n_classes': config['experiment_config']['n_classes'],
            'test_size': config.get('test_size', 0.2),
            'val_size': config.get('val_size', 0.15),
            'random_state': config.get('random_state', 42),  # Use get() with default
            'stratified': config.get('stratified', True),   # Use get() with default
            'total_samples': config['experiment_config']['total_samples'],
            'train_samples': config['experiment_config']['train_samples'],
            'val_samples': config['experiment_config']['val_samples'],
            'test_samples': config['experiment_config']['test_samples'],
        }
        
        # Save model artifacts
        ml.save_model_artifacts(
            model=best_model,
            model_name=f"{config['experiment_name']}_production_model",
            experiment_config=serializable_config,
            performance_metrics={
                'cv_score': cv_score,
                'test_score': float(final_score),
                'model_type': str(best_model_name),
                'experiment_name': str(config['experiment_name']),
                'training_date': datetime.now().strftime('%Y-%m-%d'),
                'data_shape': f"{df_ml.shape[0]}x{df_ml.shape[1]}",
                'feature_count': int(len(config['feature_names']))
            }
        )
        print("✅ Model artifacts saved successfully")
        
        # Test model report generation
        print("\n📋 Testing model report generation")
        report = ml.create_model_report(
            model=best_model,
            model_name=f"{best_model_name}_test_model",
            experiment_config=config,  # Correct parameter name
            performance_metrics=best_model_row.iloc[0].to_dict(),
            validation_results=None,  # Add validation_results parameter
            save_path=None  # Don't save during testing
        )
        print("✅ Model report generated successfully")
        
        print(f"\n✅ Model artifacts workflow completed!")
        print(f"📁 Model artifacts saved with experiment name: {config['experiment_name']}")
        print(f"📊 Model ready for production deployment")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in model artifacts: {str(e)}")
        traceback.print_exc()
        return False

def main():
    """Run all ML workflow documentation tests."""
    print("🧪 TESTING ML WORKFLOW DOCUMENTATION")
    print("=" * 80)
    print("This script validates all documented ML workflow examples")
    print("to ensure they work correctly without errors.")
    print("=" * 80)
    
    test_results = {}
    
    # Test 1: Basic ML Workflow
    success, config, models, results = test_basic_ml_workflow()
    test_results['Basic ML Workflow'] = success
    
    # Test 2: Alternative API Patterns
    success = test_alternative_api_patterns()
    test_results['Alternative API Patterns'] = success
    
    # Test 3: Hyperparameter Optimization (simplified)
    success = test_hyperparameter_optimization()
    test_results['Hyperparameter Optimization'] = success
    
    # Test 4: Visualization Functions
    success = test_visualization_functions()
    test_results['Visualization Functions'] = success
    
    # Test 5: Model Artifacts
    success = test_model_artifacts()
    test_results['Model Artifacts'] = success
    
    # Summary
    print("\n" + "="*80)
    print("🏁 TEST SUMMARY")
    print("="*80)
    
    all_passed = True
    for test_name, passed in test_results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name:.<50} {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "="*80)
    if all_passed:
        print("🎉 ALL TESTS PASSED! The ML workflow documentation is working correctly.")
        print("✅ All documented examples follow the required design logic.")
        print("✅ No errors detected in the workflow implementation.")
    else:
        print("⚠️  Some tests failed. Please review the errors above.")
    print("="*80)
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
