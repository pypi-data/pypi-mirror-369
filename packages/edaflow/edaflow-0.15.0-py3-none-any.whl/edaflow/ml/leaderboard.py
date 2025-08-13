"""
edaflow.ml.leaderboard - Model comparison and ranking functionality

This module provides utilities for comparing multiple models, ranking them
based on performance metrics, and displaying comprehensive leaderboards.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any, Union
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, roc_auc_score,
    mean_squared_error, mean_absolute_error, r2_score
)
from sklearn.model_selection import cross_val_score
from sklearn.base import BaseEstimator
import matplotlib.pyplot as plt
import seaborn as sns
import time
import warnings


def compare_models(
    models: Dict[str, BaseEstimator],
    X_train: Optional[pd.DataFrame] = None,
    X_val: Optional[pd.DataFrame] = None,
    X_test: Optional[pd.DataFrame] = None,
    y_train: Optional[pd.Series] = None,
    y_val: Optional[pd.Series] = None,
    y_test: Optional[pd.Series] = None,
    experiment_config: Optional[Dict[str, Any]] = None,
    problem_type: str = 'auto',
    metrics: Optional[List[str]] = None,
    cv_folds: int = 5,
    scoring: Optional[Union[str, List[str]]] = None,
    verbose: bool = True
) -> pd.DataFrame:
    """
    Compare multiple models across various performance metrics.
    
    Parameters:
    -----------
    models : Dict[str, BaseEstimator]
        Dictionary of model name -> fitted model pairs
    X_train : pd.DataFrame, optional
        Training features (can be provided via experiment_config)
    X_val : pd.DataFrame, optional
        Validation features (can be provided via experiment_config)
    X_test : pd.DataFrame, optional
        Test features for final evaluation
    y_train : pd.Series, optional
        Training target (can be provided via experiment_config)
    y_val : pd.Series, optional
        Validation target (can be provided via experiment_config)
    y_test : pd.Series, optional
        Test target for final evaluation
    experiment_config : Dict[str, Any], optional
        Complete experiment configuration from setup_ml_experiment()
        If provided, will extract X_train, X_val, y_train, y_val from it
    problem_type : str, default='auto'
        'classification', 'regression', or 'auto' to detect
    metrics : List[str], optional
        Specific metrics to calculate. If None, uses default metrics
    cv_folds : int, default=5
        Number of cross-validation folds (if applicable)
    scoring : str or List[str], optional
        Scoring metric(s) to use for evaluation
    verbose : bool, default=True
        Whether to print comparison progress
        
    Returns:
    --------
    pd.DataFrame
        Comparison results with models as rows and metrics as columns
    """
    
    # Extract data from experiment_config if provided
    if experiment_config is not None:
        X_train = experiment_config['X_train']
        X_val = experiment_config['X_val']
        y_train = experiment_config['y_train']
        y_val = experiment_config['y_val']
        
        # Extract test data if available in experiment config
        X_test = experiment_config.get('X_test', X_test)
        y_test = experiment_config.get('y_test', y_test)
        
        # Use problem type from experiment if available
        if problem_type == 'auto' and 'experiment_config' in experiment_config:
            problem_type = experiment_config['experiment_config'].get('problem_type', 'auto')
        
        if verbose:
            exp_name = experiment_config.get('experiment_config', {}).get('experiment_name', 'Unknown')
            print(f"📋 Using experiment: {exp_name}")
    
    # Prioritize test data for evaluation if available, otherwise use validation data
    eval_X = X_test if X_test is not None else X_val
    eval_y = y_test if y_test is not None else y_val
    eval_label = "test" if X_test is not None else "validation"
    
    # Validate required data is available
    if X_train is None or eval_X is None or y_train is None or eval_y is None:
        raise ValueError("Must provide either (X_train, y_train, X_val/X_test, y_val/y_test) OR experiment_config")
    
    if verbose:
        print("🏆 Comparing Models...")
        print(f"📊 Models to compare: {len(models)}")
        print(f"📈 Training samples: {len(X_train)}")
        print(f"🔍 Evaluation samples ({eval_label}): {len(eval_X)}")
        if scoring is not None:
            print(f"📏 Custom scoring: {scoring}")
        if cv_folds > 1:
            print(f"🔄 Cross-validation folds: {cv_folds}")
    
    # Auto-detect problem type
    if problem_type == 'auto':
        problem_type = _detect_problem_type(y_train)
    
    # Set default metrics based on problem type and scoring parameter
    if metrics is None:
        if scoring is not None:
            # Use scoring parameter if provided
            if isinstance(scoring, str):
                metrics = [scoring]
            else:
                metrics = list(scoring)
        else:
            # Use default metrics
            if problem_type == 'classification':
                metrics = ['accuracy', 'precision', 'recall', 'f1', 'roc_auc']
            else:
                metrics = ['mse', 'mae', 'r2']
    
    results = []
    
    for model_name, model in models.items():
        if verbose:
            print(f"⚡ Evaluating {model_name}...")
        
        start_time = time.time()
        
        # Make predictions
        try:
            y_pred = model.predict(eval_X)
            if problem_type == 'classification' and hasattr(model, 'predict_proba'):
                y_proba = model.predict_proba(eval_X)
        except Exception as e:
            if verbose:
                print(f"❌ Error with {model_name}: {str(e)}")
            continue
        
        # Calculate metrics
        model_results = {'model': model_name}
        
        for metric in metrics:
            try:
                if problem_type == 'classification':
                    score = _calculate_classification_metric(metric, eval_y, y_pred, y_proba if 'y_proba' in locals() else None)
                else:
                    score = _calculate_regression_metric(metric, eval_y, y_pred)
                
                model_results[metric] = score
            except Exception as e:
                if verbose:
                    print(f"⚠️ Could not calculate {metric} for {model_name}: {str(e)}")
                model_results[metric] = np.nan
        
        # Calculate training time (if available)
        end_time = time.time()
        model_results['eval_time_ms'] = (end_time - start_time) * 1000
        
        # Add model complexity info if available
        if hasattr(model, 'get_params'):
            n_params = len(str(model.get_params()))
            model_results['complexity'] = n_params
        
        results.append(model_results)
    
    # Convert to DataFrame
    comparison_df = pd.DataFrame(results)
    
    if verbose:
        print(f"✅ Comparison complete! {len(comparison_df)} models evaluated.")
    
    return comparison_df


def rank_models(
    comparison_df: pd.DataFrame,
    primary_metric: str,
    ascending: bool = False,
    secondary_metrics: Optional[List[str]] = None,
    weights: Optional[Dict[str, float]] = None,
    return_format: str = 'dataframe'
) -> Union[pd.DataFrame, List[Dict]]:
    """
    Rank models based on performance metrics.
    
    Parameters:
    -----------
    comparison_df : pd.DataFrame
        Results from compare_models()
    primary_metric : str
        Main metric to rank by
    ascending : bool, default=False
        Whether to sort in ascending order (True for error metrics)
    secondary_metrics : List[str], optional
        Additional metrics to consider for tie-breaking
    weights : Dict[str, float], optional
        Weights for weighted ranking across multiple metrics
    return_format : str, default='dataframe'
        Format to return: 'dataframe' or 'list'
        
    Returns:
    --------
    Union[pd.DataFrame, List[Dict]]
        If 'dataframe': Ranked models DataFrame
        If 'list': List of dicts for easy access with pattern [0]["model_name"]
        
    Examples:
    ---------
    # DataFrame format (default)
    ranked_df = rank_models(results, 'accuracy')
    best_model = ranked_df.iloc[0]['model']
    
    # List format for easier access
    ranked_list = rank_models(results, 'accuracy', return_format='list')
    best_model = ranked_list[0]["model_name"]
    """
    
    ranked_df = comparison_df.copy()
    
    # Validate primary metric exists
    if primary_metric not in ranked_df.columns:
        raise ValueError(f"Primary metric '{primary_metric}' not found in comparison results")
    
    # Simple ranking by primary metric
    if weights is None:
        ranked_df = ranked_df.sort_values(
            by=[primary_metric] + (secondary_metrics or []),
            ascending=ascending
        ).reset_index(drop=True)
        
        ranked_df['rank'] = range(1, len(ranked_df) + 1)
        ranked_df['rank_score'] = ranked_df[primary_metric]
    
    # Weighted ranking across multiple metrics
    else:
        # Normalize metrics to 0-1 scale
        metric_columns = [col for col in weights.keys() if col in ranked_df.columns]
        normalized_df = ranked_df[metric_columns].copy()
        
        for metric in metric_columns:
            col_values = ranked_df[metric].dropna()
            if len(col_values) > 0:
                min_val, max_val = col_values.min(), col_values.max()
                if max_val > min_val:
                    # Normalize to 0-1, flip if lower is better (like error metrics)
                    if metric.lower() in ['mse', 'mae', 'rmse', 'error']:
                        normalized_df[metric] = 1 - (ranked_df[metric] - min_val) / (max_val - min_val)
                    else:
                        normalized_df[metric] = (ranked_df[metric] - min_val) / (max_val - min_val)
        
        # Calculate weighted score
        weighted_scores = []
        for idx, row in normalized_df.iterrows():
            score = sum(row[metric] * weights[metric] for metric in metric_columns if not pd.isna(row[metric]))
            weighted_scores.append(score)
        
        ranked_df['rank_score'] = weighted_scores
        ranked_df = ranked_df.sort_values('rank_score', ascending=False).reset_index(drop=True)
        ranked_df['rank'] = range(1, len(ranked_df) + 1)
    
    # Return in requested format
    if return_format == 'list':
        # Convert to list of dictionaries for easy access
        result_list = []
        for _, row in ranked_df.iterrows():
            model_dict = row.to_dict()
            # Add model_name key for consistency with user's pattern
            if 'model' in model_dict:
                model_dict['model_name'] = model_dict['model']
            result_list.append(model_dict)
        return result_list
    
    return ranked_df


def display_leaderboard(
    comparison_results: pd.DataFrame = None,
    ranked_df: pd.DataFrame = None,
    sort_by: str = None,
    ascending: bool = False,
    show_std: bool = False,
    top_n: int = 10,
    show_metrics: Optional[List[str]] = None,
    highlight_best: bool = True,
    figsize: Tuple[int, int] = (12, 8)
) -> None:
    """
    Display a visual leaderboard of model performance.
    
    Parameters:
    -----------
    comparison_results : pd.DataFrame, optional
        Raw comparison results from compare_models()
    ranked_df : pd.DataFrame, optional
        Pre-ranked results (alternative to comparison_results)
    sort_by : str, optional
        Metric to sort by. If None, uses first numeric column
    ascending : bool, default=False
        Whether to sort in ascending order
    show_std : bool, default=False
        Whether to show standard deviation columns
    top_n : int, default=10
        Number of top models to display
    show_metrics : List[str], optional
        Specific metrics to show. If None, shows all numeric metrics
    highlight_best : bool, default=True
        Whether to highlight the best performing model
    figsize : Tuple[int, int], default=(12, 8)
        Figure size for the visualization
    """
    
    # Handle input data
    if comparison_results is not None:
        display_df = comparison_results.copy()
        
        # Sort by specified metric
        if sort_by is not None and sort_by in display_df.columns:
            display_df = display_df.sort_values(sort_by, ascending=ascending)
        elif len(display_df.select_dtypes(include=[np.number]).columns) > 0:
            # Sort by first numeric column if sort_by not specified
            numeric_cols = display_df.select_dtypes(include=[np.number]).columns
            display_df = display_df.sort_values(numeric_cols[0], ascending=ascending)
    
    elif ranked_df is not None:
        display_df = ranked_df.copy()
    
    else:
        raise ValueError("Must provide either comparison_results or ranked_df")
    
    # Filter out std columns if not requested
    if not show_std:
        std_cols = [col for col in display_df.columns if '_std' in col.lower() or 'std_' in col.lower()]
        display_df = display_df.drop(columns=std_cols, errors='ignore')
    
    # Filter to specific metrics if requested
    if show_metrics is not None:
        keep_cols = ['model'] + [col for col in display_df.columns if any(metric in col.lower() for metric in show_metrics)]
        display_df = display_df[keep_cols]
    
    print("🏆 MODEL LEADERBOARD 🏆")
    print("=" * 50)
    
    # Take top_n results
    display_df = display_df.head(top_n).copy()
    
    # Highlight best model if requested
    if highlight_best and len(display_df) > 0:
        best_model = display_df.iloc[0]['model']
        print(f"🥇 Best Model: {best_model}")
        print()
    
    # Display the results
    print(display_df.to_string(index=False))
    print()
    
    # Create simple visualization if matplotlib is available
    try:
        import matplotlib.pyplot as plt
        
        # Get numeric columns for plotting
        numeric_cols = display_df.select_dtypes(include=[np.number]).columns.tolist()
        if len(numeric_cols) > 0:
            # Create a simple bar plot for the first metric
            plt.figure(figsize=figsize)
            
            first_metric = numeric_cols[0]
            models = display_df['model'].tolist()
            scores = display_df[first_metric].tolist()
            
            bars = plt.barh(range(len(models)), scores)
            plt.yticks(range(len(models)), models)
            plt.xlabel(first_metric.title())
            plt.title(f'Model Comparison - {first_metric.title()}')
            
            # Highlight best model
            if highlight_best and len(bars) > 0:
                bars[0].set_color('gold')
            
            plt.tight_layout()
            plt.show()
    
    except ImportError:
        print("📊 Matplotlib not available for visualization")
    
    return display_df


def _detect_problem_type(y):
    """Detect if problem is classification or regression"""
    if hasattr(y, 'dtype'):
        if y.dtype.name in ['object', 'category', 'bool']:
            return 'classification'
        elif len(np.unique(y)) <= 10:  # Likely categorical
            return 'classification'
        else:
            return 'regression'
    else:
        unique_values = len(set(y))
        if unique_values <= 10:
            return 'classification'
        else:
            return 'regression'


def export_model_comparison(
    comparison_df: pd.DataFrame,
    filepath: str,
    include_config: bool = True,
    format: str = 'csv'
) -> None:
    """
    Export model comparison results to file.
    
    Parameters:
    -----------
    comparison_df : pd.DataFrame
        Comparison results to export
    filepath : str
        Path where to save the file
    include_config : bool, default=True
        Whether to include experiment configuration
    format : str, default='csv'
        Export format ('csv', 'excel', 'json')
    """
    
    print(f"💾 Exporting comparison results to {filepath}...")
    
    if format.lower() == 'csv':
        comparison_df.to_csv(filepath, index=False)
    elif format.lower() == 'excel':
        comparison_df.to_excel(filepath, index=False)
    elif format.lower() == 'json':
        comparison_df.to_json(filepath, indent=2)
    else:
        raise ValueError(f"Unsupported format: {format}")
    
    print("✅ Export completed!")


def _calculate_classification_metric(metric: str, y_true: pd.Series, y_pred: np.ndarray, y_proba: Optional[np.ndarray] = None) -> float:
    """Calculate classification metric."""
    metric = metric.lower()
    
    if metric == 'accuracy':
        return accuracy_score(y_true, y_pred)
    elif metric == 'precision':
        return precision_score(y_true, y_pred, average='weighted', zero_division=0)
    elif metric == 'recall':
        return recall_score(y_true, y_pred, average='weighted', zero_division=0)
    elif metric == 'f1':
        return f1_score(y_true, y_pred, average='weighted', zero_division=0)
    elif metric == 'roc_auc':
        if y_proba is not None and len(np.unique(y_true)) == 2:
            return roc_auc_score(y_true, y_proba[:, 1])
        else:
            return np.nan
    else:
        raise ValueError(f"Unknown classification metric: {metric}")


def _calculate_regression_metric(metric: str, y_true: pd.Series, y_pred: np.ndarray) -> float:
    """Calculate regression metric."""
    metric = metric.lower()
    
    if metric == 'mse':
        return mean_squared_error(y_true, y_pred)
    elif metric == 'mae':
        return mean_absolute_error(y_true, y_pred)
    elif metric == 'rmse':
        return np.sqrt(mean_squared_error(y_true, y_pred))
    elif metric == 'r2':
        return r2_score(y_true, y_pred)
    else:
        raise ValueError(f"Unknown regression metric: {metric}")
