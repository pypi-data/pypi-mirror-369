"""
Sanity test for dynamic best model selection in edaflow ML workflow.
This script runs the workflow for different metrics and asserts correctness.
"""
import edaflow.ml as ml
import pandas as pd
from sklearn.datasets import load_breast_cancer
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
import numpy as np

def test_best_model_selection(primary_metric):
    data = load_breast_cancer()
    df = pd.DataFrame(data.data, columns=data.feature_names)
    df['target'] = data.target
    X = df.drop('target', axis=1)
    y = df['target']

    config = ml.setup_ml_experiment(
        X=X,
        y=y,
        test_size=0.2,
        val_size=0.15,
        experiment_name=f"test_{primary_metric}",
        random_state=42
    )

    models = {
        'random_forest': RandomForestClassifier(n_estimators=100, random_state=42),
        'gradient_boosting': GradientBoostingClassifier(n_estimators=100, random_state=42),
        'logistic_regression': LogisticRegression(random_state=42),
        'svm': SVC(probability=True, random_state=42)
    }
    for name, model in models.items():
        model.fit(config['X_train'], config['y_train'])

    comparison_results = ml.compare_models(
        models=models,
        X_train=config['X_train'],
        y_train=config['y_train'],
        X_test=config['X_test'],
        y_test=config['y_test'],
        cv_folds=5,
        scoring=['accuracy', 'precision', 'recall', 'f1', 'roc_auc']
    )

    ranked_df = ml.rank_models(comparison_results, primary_metric)
    best_model_traditional = ranked_df.iloc[0]['model']
    best_model = ml.rank_models(
        comparison_results,
        primary_metric,
        return_format='list'
    )[0]['model_name']

    assert best_model == best_model_traditional, f"Mismatch: {best_model} vs {best_model_traditional}"
    best_score = ranked_df.iloc[0][primary_metric]
    assert np.isclose(best_score, ranked_df[primary_metric].max()), f"Best score is not max for {primary_metric}"
    print(f"[PASS] Best model for {primary_metric}: {best_model} (score: {best_score:.4f})")

if __name__ == "__main__":
    test_metrics = ['accuracy', 'f1', 'roc_auc']
    for metric in test_metrics:
        test_best_model_selection(metric)
