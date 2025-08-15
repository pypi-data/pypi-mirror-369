# rank_models Quick Reference Guide

The `rank_models` function in edaflow.ml provides flexible model ranking with two return formats to suit different use cases.

## Basic Usage

```python
from edaflow.ml.leaderboard import compare_models, rank_models

# After getting comparison_results from compare_models()
comparison_results = compare_models(models, X_train, y_train, X_test, y_test)
```

## Two Return Formats

### 1. DataFrame Format (Default - Traditional)

```python
# Returns pandas DataFrame
ranked_df = rank_models(comparison_results, 'accuracy')

# Access best model
best_model = ranked_df.iloc[0]['model']
best_accuracy = ranked_df.iloc[0]['accuracy']

print(f"Best model: {best_model} (accuracy: {best_accuracy:.4f})")
```

**Best for:** Data analysis, visualization, pandas workflows

### 2. List Format (New - Easy Access)

```python
# Returns list of dictionaries
ranked_list = rank_models(comparison_results, 'accuracy', return_format='list')

# Access best model (multiple ways)
best_model_name = ranked_list[0]["model_name"]  # Preferred key
best_model = ranked_list[0]["model"]            # Original key
best_accuracy = ranked_list[0]["accuracy"]

print(f"Best model: {best_model_name} (accuracy: {best_accuracy:.4f})")
```

**Best for:** Simple programmatic access, one-liners, production code

## Common Patterns

### One-liner Pattern (Your Requested Pattern)
```python
# Get best model name in one line
best_model = rank_models(comparison_results, 'accuracy', return_format='list')[0]["model_name"]
```

### Iterate Through All Models
```python
ranked_models = rank_models(comparison_results, 'accuracy', return_format='list')

for i, model_info in enumerate(ranked_models):
    print(f"{i+1}. {model_info['model_name']}: {model_info['accuracy']:.4f}")
```

### Different Ranking Metrics
```python
# Rank by different metrics
best_by_f1 = rank_models(comparison_results, 'f1_score', return_format='list')[0]["model_name"]
best_by_precision = rank_models(comparison_results, 'precision', return_format='list')[0]["model_name"]

# For error metrics (lower is better)
best_by_error = rank_models(comparison_results, 'validation_error', ascending=True, return_format='list')[0]["model_name"]
```

### Weighted Multi-Metric Ranking
```python
# Combine multiple metrics with weights
weighted_ranking = rank_models(
    comparison_results, 
    'accuracy',
    weights={
        'accuracy': 0.4,
        'f1_score': 0.3,
        'precision': 0.2,
        'recall': 0.1
    },
    return_format='list'
)

best_overall = weighted_ranking[0]["model_name"]
```

## Function Signature

```python
def rank_models(
    comparison_df: pd.DataFrame,
    primary_metric: str,
    ascending: bool = False,
    secondary_metrics: Optional[List[str]] = None,
    weights: Optional[Dict[str, float]] = None,
    return_format: str = 'dataframe'  # 'dataframe' or 'list'
) -> Union[pd.DataFrame, List[Dict]]
```

## Key Points

- **Backward Compatible:** Default behavior unchanged (`return_format='dataframe'`)
- **Both Keys Available:** List format includes both `'model'` and `'model_name'` keys
- **Same Ranking:** Both formats produce identical ranking order
- **All Metrics Preserved:** Both formats include all original metrics
- **Flexible Access:** Choose the format that fits your workflow

## When to Use Which Format

| Use Case | Format | Example |
|----------|--------|---------|
| Quick best model access | `list` | `rank_models(results, 'accuracy', return_format='list')[0]['model_name']` |
| Data analysis | `dataframe` | `ranked_df.head(3)[['model', 'accuracy', 'rank']]` |
| Iteration | `list` | `for model in ranked_models: print(model['model_name'])` |
| Pandas integration | `dataframe` | `ranked_df.query('accuracy > 0.8')` |
| Production code | `list` | Simple dictionary access |
| Visualization | `dataframe` | Easy plotting with pandas |

## Complete Example

```python
import edaflow.ml as ml
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression

# Setup and train models
models = {
    'RandomForest': RandomForestClassifier(random_state=42),
    'LogisticRegression': LogisticRegression(random_state=42)
}

for name, model in models.items():
    model.fit(X_train, y_train)

# Compare models
comparison_results = ml.compare_models(models, X_train, y_train, X_test, y_test)

# Your pattern works perfectly!
best_model_name = ml.rank_models(comparison_results, 'accuracy', return_format='list')[0]["model_name"]
print(f"🏆 Best model: {best_model_name}")
```

This enhancement makes `rank_models` more flexible while maintaining full backward compatibility!
