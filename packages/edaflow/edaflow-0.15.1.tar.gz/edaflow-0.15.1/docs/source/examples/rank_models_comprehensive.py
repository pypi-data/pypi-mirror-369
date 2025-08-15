"""
Comprehensive rank_models Function Examples

This file demonstrates all the ways to use the enhanced rank_models function
in edaflow.ml with both DataFrame and List return formats.

Author: edaflow team
Updated: August 2025
"""

import pandas as pd
import numpy as np
from sklearn.datasets import make_classification, load_iris
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.naive_bayes import GaussianNB

# Import edaflow ML functions
from edaflow.ml.leaderboard import compare_models, rank_models, display_leaderboard

def comprehensive_rank_models_examples():
    """
    Comprehensive examples showing all rank_models capabilities
    """
    
    print("=" * 80)
    print("🎯 COMPREHENSIVE rank_models FUNCTION EXAMPLES")
    print("=" * 80)
    
    # === SETUP DATA AND MODELS ===
    print("\n📊 Setting up data and models...")
    
    # Use iris dataset for quick reproducible results
    iris = load_iris()
    X, y = iris.data, iris.target
    
    # Convert to binary classification for ROC AUC
    y_binary = (y != 0).astype(int)  # Make it binary
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_binary, test_size=0.3, random_state=42, stratify=y_binary
    )
    
    # Create diverse set of models
    models = {
        'RandomForest': RandomForestClassifier(n_estimators=50, random_state=42),
        'GradientBoosting': GradientBoostingClassifier(n_estimators=50, random_state=42),
        'LogisticRegression': LogisticRegression(random_state=42, max_iter=300),
        'SVM': SVC(probability=True, random_state=42, kernel='rbf'),
        'NaiveBayes': GaussianNB()
    }
    
    # Train all models
    print("🔧 Training models...")
    for name, model in models.items():
        model.fit(X_train, y_train)
        print(f"   ✅ {name}")
    
    # Compare models to get results for ranking
    print("\n📈 Comparing models...")
    comparison_results = compare_models(
        models=models,
        X_train=X_train,
        y_train=y_train,
        X_test=X_test,
        y_test=y_test,
        cv_folds=3,
        verbose=False
    )
    
    print("Model comparison completed!")
    print(f"Shape: {comparison_results.shape}")
    print(f"Columns: {list(comparison_results.columns)}")
    
    # === EXAMPLE 1: BASIC DATAFRAME FORMAT (Traditional) ===
    print("\n" + "=" * 80)
    print("📋 EXAMPLE 1: DataFrame Format (Traditional)")
    print("=" * 80)
    
    ranked_df = rank_models(
        comparison_df=comparison_results,
        primary_metric='accuracy'
    )
    
    print(f"Return type: {type(ranked_df)}")
    print(f"Shape: {ranked_df.shape}")
    print("\nRanked models (DataFrame format):")
    print(ranked_df[['model', 'accuracy', 'f1', 'precision', 'rank']].round(4))
    
    # Access best model (DataFrame way)
    best_model_df = ranked_df.iloc[0]['model']
    best_accuracy_df = ranked_df.iloc[0]['accuracy']
    print(f"\n🏆 Best model: {best_model_df} (accuracy: {best_accuracy_df:.4f})")
    
    # === EXAMPLE 2: LIST FORMAT (Easy Access) ===
    print("\n" + "=" * 80)
    print("📋 EXAMPLE 2: List Format (Easy Dictionary Access)")
    print("=" * 80)
    
    ranked_list = rank_models(
        comparison_df=comparison_results,
        primary_metric='accuracy',
        return_format='list'
    )
    
    print(f"Return type: {type(ranked_list)}")
    print(f"Length: {len(ranked_list)}")
    print(f"First item type: {type(ranked_list[0])}")
    print(f"First item keys: {list(ranked_list[0].keys())}")
    
    # Access best model (List/Dictionary way)
    best_model_list = ranked_list[0]['model_name']
    best_accuracy_list = ranked_list[0]['accuracy']
    print(f"\n🏆 Best model: {best_model_list} (accuracy: {best_accuracy_list:.4f})")
    
    print("\nTop 3 models (List format):")
    for i, model_info in enumerate(ranked_list[:3]):
        print(f"  {i+1}. {model_info['model_name']}: "
              f"acc={model_info['accuracy']:.4f}, "
              f"f1={model_info['f1']:.4f}")
    
    # === EXAMPLE 3: USER'S DESIRED ONE-LINER PATTERN ===
    print("\n" + "=" * 80)
    print("🎯 EXAMPLE 3: Your Desired One-liner Pattern")
    print("=" * 80)
    
    # This is the exact pattern you wanted to work
    best_model_name = rank_models(comparison_results, 'accuracy', return_format='list')[0]["model_name"]
    
    print("✅ SUCCESS! Your exact pattern works:")
    print("   Code: rank_models(comparison_results, 'accuracy', return_format='list')[0]['model_name']")
    print(f"   Result: {best_model_name}")
    
    # Alternative patterns that also work
    print("\n📝 Alternative one-liner patterns:")
    
    # Get best model with original 'model' key
    best_model_alt = rank_models(comparison_results, 'accuracy', return_format='list')[0]["model"]
    print(f"   rank_models(...)[0]['model'] = '{best_model_alt}'")
    
    # Get best accuracy score
    best_accuracy = rank_models(comparison_results, 'accuracy', return_format='list')[0]["accuracy"]
    print(f"   rank_models(...)[0]['accuracy'] = {best_accuracy:.4f}")
    
    # === EXAMPLE 4: DIFFERENT RANKING METRICS ===
    print("\n" + "=" * 80)
    print("📊 EXAMPLE 4: Ranking by Different Metrics")
    print("=" * 80)
    
    metrics_to_test = ['accuracy', 'f1', 'precision', 'recall']
    
    for metric in metrics_to_test:
        if metric in comparison_results.columns:
            best_by_metric = rank_models(
                comparison_results, 
                metric, 
                return_format='list'
            )[0]['model_name']
            
            score = rank_models(comparison_results, metric, return_format='list')[0][metric]
            print(f"🥇 Best by {metric}: {best_by_metric} ({score:.4f})")
    
    # === EXAMPLE 5: ASCENDING ORDER (For Error Metrics) ===
    print("\n" + "=" * 80)
    print("📈 EXAMPLE 5: Ascending Order (Lower is Better)")
    print("=" * 80)
    
    # For metrics where lower is better (like validation error)
    # Let's simulate validation error by using (1 - accuracy)
    comparison_with_error = comparison_results.copy()
    comparison_with_error['validation_error'] = 1 - comparison_with_error['accuracy']
    
    best_by_error = rank_models(
        comparison_with_error, 
        'validation_error', 
        ascending=True,  # Lower error is better
        return_format='list'
    )[0]['model_name']
    
    lowest_error = rank_models(
        comparison_with_error, 
        'validation_error', 
        ascending=True, 
        return_format='list'
    )[0]['validation_error']
    
    print(f"🎯 Best by lowest error: {best_by_error} (error: {lowest_error:.4f})")
    
    # === EXAMPLE 6: WEIGHTED MULTI-METRIC RANKING ===
    print("\n" + "=" * 80)
    print("⚖️ EXAMPLE 6: Weighted Multi-Metric Ranking")
    print("=" * 80)
    
    # Rank models using weighted combination of multiple metrics
    weighted_results = rank_models(
        comparison_df=comparison_results,
        primary_metric='accuracy',
        weights={
            'accuracy': 0.4,      # 40% weight
            'f1': 0.3,           # 30% weight
            'precision': 0.2,     # 20% weight
            'recall': 0.1         # 10% weight
        },
        return_format='list'
    )
    
    best_weighted = weighted_results[0]['model_name']
    weighted_score = weighted_results[0]['rank_score']
    
    print(f"🏅 Best by weighted score: {best_weighted} (score: {weighted_score:.4f})")
    print("\nTop 3 by weighted ranking:")
    for i, model in enumerate(weighted_results[:3]):
        print(f"  {i+1}. {model['model_name']}: score={model['rank_score']:.4f}")
    
    # === EXAMPLE 7: COMPARISON OF BOTH FORMATS ===
    print("\n" + "=" * 80)
    print("🔄 EXAMPLE 7: Format Comparison - Same Results")
    print("=" * 80)
    
    # Show both formats give the same ranking
    df_format = rank_models(comparison_results, 'f1_score')
    list_format = rank_models(comparison_results, 'f1_score', return_format='list')
    
    print("DataFrame format (top 3):")
    df_top3 = df_format.head(3)
    for idx, row in df_top3.iterrows():
        print(f"  {row['rank']}. {row['model']}: f1={row['f1']:.4f}")
    
    print("\nList format (top 3):")
    for i, model in enumerate(list_format[:3]):
        print(f"  {model['rank']}. {model['model_name']}: f1={model['f1']:.4f}")
    
    # Verify they're the same
    df_models = df_format['model'].tolist()
    list_models = [item['model'] for item in list_format]
    
    print(f"\n✅ Same ranking order: {'YES' if df_models == list_models else 'NO'}")
    
    # === USAGE RECOMMENDATIONS ===
    print("\n" + "=" * 80)
    print("💡 USAGE RECOMMENDATIONS")
    print("=" * 80)
    
    print("""
📋 DataFrame Format - Best for:
   • Data analysis and exploration
   • Display in notebooks
   • Integration with pandas workflows
   • Statistical analysis of results
   
   Example: ranked_df = rank_models(results, 'accuracy')
            best_model = ranked_df.iloc[0]['model']

📦 List Format - Best for:
   • Simple programmatic access
   • One-liner patterns
   • Iteration over results
   • Integration with production code
   
   Example: best_model = rank_models(results, 'accuracy', return_format='list')[0]['model_name']

🎯 Your Pattern:
   • Use return_format='list' for easy dictionary access
   • Access with [0]['model_name'] for best model
   • Both 'model_name' and 'model' keys work
   • All original metrics are preserved in the dictionaries
    """)
    
    print("\n🎉 All examples completed successfully!")
    print("Your rank_models function is ready for production use!")

if __name__ == "__main__":
    comprehensive_rank_models_examples()
