How edaflow Splits Your Dataset: Training, Validation, and Test
----------------------------------------------------------------

edaflow automates robust, reproducible splitting of your dataset into training, validation, and test sets, following best practices for machine learning workflows.

**Key Function: `setup_ml_experiment`**

- This is the main function responsible for splitting your data.
- Example usage:

  .. code-block:: python

      config = ml.setup_ml_experiment(
            X=X,
            y=y,
            test_size=0.2,
            val_size=0.15,
            random_state=42
      )

- **Parameters:**
  - `X`, `y`: Your features and target.
  - `test_size`: Fraction of data reserved for the test set (e.g., 0.2 = 20%).
  - `val_size`: Fraction of the *remaining* data (after test split) for validation.
  - `random_state`: Ensures reproducibility.

**What Happens Under the Hood**

1. **Test Split:**
    - The function first splits off the test set using `sklearn.model_selection.train_test_split`.
    - Example: With `test_size=0.2`, 20% of the data is set aside for final testing.

2. **Validation Split:**
    - From the remaining 80%, it splits off the validation set using another `train_test_split`.
    - Example: With `val_size=0.15`, 15% of the *original* data (or 18.75% of the remaining 80%) is used for validation.

3. **Output:**
    - Returns a config dictionary containing:
      - `X_train`, `X_val`, `X_test`
      - `y_train`, `y_val`, `y_test`
      - Indices for each split (useful for reproducibility)
      - Other experiment settings

**Why This Matters**

- **Training Set:** Used to fit models.
- **Validation Set:** Used for hyperparameter tuning and model selection (prevents overfitting to the test set).
- **Test Set:** Used only for final evaluation, simulating unseen data.

**Other Functions Involved**

- `validate_ml_data`: Can be used on any split to check for data quality issues.
- `configure_model_pipeline`: Uses the split data to set up preprocessing pipelines.
- All downstream modeling functions (e.g., `compare_models`, `optimize_hyperparameters`) expect the split data from `setup_ml_experiment`.

**Summary Table:**

=================  ===============================  =====================================
Split              Purpose                          How edaflow Creates It
=================  ===============================  =====================================
Training           Model fitting                    From `setup_ml_experiment`
Validation         Tuning, model selection          From `setup_ml_experiment`
Test               Final evaluation (unseen)        From `setup_ml_experiment`
=================  ===============================  =====================================

**In short:**
edaflow’s `setup_ml_experiment` automates robust, reproducible splitting of your data, following best practices for ML workflows. All other ML functions in edaflow are designed to work seamlessly with these splits.
Sanity Test: Dynamic Best Model Selection
----------------------------------------

To ensure the robustness of the dynamic best model selection logic in the workflow, a sanity test script is provided. This script runs the workflow for different metrics (e.g., accuracy, f1, roc_auc) and asserts that the best model is correctly selected for each case.

**Script location:**

    sanity_test_dynamic_best_model.py

**How it works:**

1. Loads a sample dataset (breast cancer from scikit-learn).
2. Runs the ML workflow for each metric in a list.
3. Asserts that the best model selected matches the highest score for the chosen metric.
4. Prints a pass message for each metric.

**Usage:**

Activate your virtual environment, then run:

    python sanity_test_dynamic_best_model.py

If all tests pass, you will see output like:

    [PASS] Best model for accuracy: random_forest (score: 0.9474)
    [PASS] Best model for f1: random_forest (score: 0.9474)
    [PASS] Best model for roc_auc: logistic_regression (score: 0.9947)

This ensures the sample code in the documentation is safe for copy-paste and works for any metric.
Troubleshooting & Common Pitfalls
---------------------------------

Even with a robust workflow, users may encounter common issues. Here are some troubleshooting tips and pitfalls to avoid:

**Data Issues**
- Unexpected errors during model fitting often stem from missing values, inconsistent data types, or unseen categories. Always validate and clean your data first.
- If you see shape mismatch errors, check that your features and target arrays are aligned and have no missing values.

**Model Training**
- If a model fails to converge, try scaling your features or adjusting hyperparameters (e.g., increase max_iter).
- For imbalanced classification, consider using stratified splits and appropriate metrics (e.g., ROC AUC, F1-score).

**Leaderboard & Comparison**
- If the leaderboard shows similar scores for all models, check for data leakage or target leakage.
- If a model dominates, ensure your baseline is reasonable and your metrics are appropriate for the problem type.

**Artifact Saving/Loading**
- Always use the same library versions for saving and loading models to avoid compatibility issues.
- If you cannot load a saved model, check for missing dependencies or version mismatches.

**General Tips**
- Read error messages carefully—they often point directly to the problem.
- Use version control to track changes in your workflow and experiments.

Further Resources & FAQ
----------------------

**Further Resources**
- [scikit-learn User Guide](https://scikit-learn.org/stable/user_guide.html)
- [XGBoost Documentation](https://xgboost.readthedocs.io/en/stable/)
- [LightGBM Documentation](https://lightgbm.readthedocs.io/en/latest/)
- [CatBoost Documentation](https://catboost.ai/docs/)
- [Model Deployment with FastAPI](https://fastapi.tiangolo.com/tutorial/)
- [Model Monitoring Concepts](https://mlops.community/model-monitoring/)

**FAQ**

**Q: Why does my model perform poorly on new data?**
A: This may be due to overfitting, data drift, or differences between training and production data. Use cross-validation and monitor performance after deployment.

**Q: How do I handle missing values in my dataset?**
A: Use edaflow's imputation utilities or scikit-learn's SimpleImputer to fill missing values before training.

**Q: Can I use custom models with edaflow?**
A: Yes, as long as your model follows the scikit-learn API (fit/predict methods), it can be integrated into the workflow.

**Q: How do I deploy my trained model?**
A: See the "What's Next After Training the Model?" section for deployment options and best practices.

**Q: What if I have a question not covered here?**
A: Check the official documentation above or reach out to the project maintainers/community for support.
edaflow Machine Learning Workflow: Overview & Best Practices
===========================================================

This guide walks you through the recommended end-to-end workflow for building, evaluating, and deploying machine learning models with edaflow. Each step is explained in detail below, but here’s a high-level summary to help you see the big picture:

**Recommended ML Workflow**

1. **Data Validation**
    - Check for missing values, outliers, and data quality issues.
2. **Experiment Setup**
    - Split data into train/validation/test sets and configure experiment settings.
3. **Preprocessing**
    - Apply scaling, encoding, and imputation as needed.

    What Happens Under the Hood
    ~~~~~~~~~~~~~~~~~~~~~~~~~~
    - The `configure_model_pipeline` function builds a scikit-learn `Pipeline` or `ColumnTransformer` based on your data types and preprocessing choices.
    - It automatically detects numerical and categorical columns, applying the specified strategies (e.g., standard scaling, one-hot encoding, imputation).
    - Handles missing values according to your chosen method, ensuring compatibility with downstream models.
    - The resulting pipeline is stored in the config and used for all model training and evaluation steps.
4. **Model Fitting**
    - Train multiple candidate models (including baselines).

    What Happens Under the Hood
    ~~~~~~~~~~~~~~~~~~~~~~~~~~
    - edaflow expects you to provide a dictionary of models (scikit-learn compatible) for training.
    - Each model is fit on the training data (from the config) using its `.fit()` method.
    - Training progress and any errors are reported if `verbose=True`.
    - All models are trained independently to avoid cross-contamination of results.
5. **Model Comparison & Evaluation**
    - Compare models using cross-validation and leaderboard visualizations.

    What Happens Under the Hood
    ~~~~~~~~~~~~~~~~~~~~~~~~~~
    - The `compare_models` function runs cross-validation for each model using the specified number of folds and metrics.
    - It collects out-of-fold predictions and aggregates scores for each metric, storing means and standard deviations.
    - Results are returned as a DataFrame or list, ready for leaderboard display and ranking.
    - The function supports both classification and regression, auto-detecting the problem type if needed.
6. **Hyperparameter Optimization**
    - Tune the best models for optimal performance.

    What Happens Under the Hood
    ~~~~~~~~~~~~~~~~~~~~~~~~~~
    - edaflow provides `optimize_hyperparameters`, `grid_search_models`, and `bayesian_optimization` utilities.
    - These functions define a search space and strategy, then evaluate model performance for each combination using cross-validation.
    - The best hyperparameters are selected based on your chosen metric, and the tuned model is returned for further use.
    - All search results and best parameters are stored for reproducibility and reporting.
7. **Select Best Model**
    - Choose the top-performing model based on your primary metric.

    What Happens Under the Hood
    ~~~~~~~~~~~~~~~~~~~~~~~~~~
    - The `rank_models` function sorts models by your primary metric, supporting both DataFrame and list return formats.
    - It can apply custom weights for multi-metric ranking and supports both ascending and descending order (for error vs. score metrics).
    - The top-ranked model is selected for further tuning or deployment.
    - All ranking logic is transparent and reproducible.
8. **Save Model Artifacts**
    - Persist the model, configuration, and metrics for reproducibility and deployment.

    What Happens Under the Hood
    ~~~~~~~~~~~~~~~~~~~~~~~~~~
    - The `save_model_artifacts` function serializes your trained model, config, and metrics using joblib or pickle.
    - It saves all relevant files to a specified directory, using clear naming conventions for traceability.
    - The function can also include a sample of your training data for future reference or debugging.
    - Loading is handled by `load_model_artifacts`, which restores all components for immediate use.
9. **Generate Model Reports**
    - Create reports and visualizations for stakeholders and documentation.
10. **Track Experiments**
     - Log experiment details for future reference and reproducibility.

**Workflow Diagram:**

::

    [Data Validation]
             ↓
    [Experiment Setup]
             ↓
    [Preprocessing]
             ↓
    [Model Fitting] → [Baseline Model]
             ↓
    [Model Comparison/Evaluation]
             ↓
    [Hyperparameter Optimization]
             ↓
    [Select Best Model]
             ↓
    [Save Artifacts & Generate Reports]
             ↓
    [Track Experiments]

Each section of this guide provides actionable examples, best practices, and explanations for every step above. Use this workflow as your roadmap for robust, reproducible, and effective machine learning with edaflow.

Choosing the Right Performance Visualization
-------------------------------------------

Selecting the appropriate visualization helps you interpret model results and diagnose issues more effectively. Use the table below to match your problem type and primary metric to the recommended plot:

+---------------------------+---------------------+-------------------------------+
| Problem Type / Scenario   | Primary Metrics     | Recommended Visualizations     |
+===========================+=====================+===============================+
| Binary Classification     | accuracy, f1,       | ROC curve, learning curve,    |
| (e.g., disease prediction)| recall, roc_auc     | confusion matrix              |
+---------------------------+---------------------+-------------------------------+
| Multiclass Classification | accuracy, f1        | Learning curve, confusion     |
| (e.g., digit recognition) |                     | matrix                        |
+---------------------------+---------------------+-------------------------------+
| Imbalanced Classification | f1, recall,         | ROC curve, precision-recall   |
| (e.g., fraud detection)   | precision, roc_auc  | curve, learning curve         |
+---------------------------+---------------------+-------------------------------+
| Regression                | mae, rmse, r2, mse  | Learning curve, residual plot |
| (e.g., house prices)      |                     | predicted vs. actual plot     |
+---------------------------+---------------------+-------------------------------+

**Tips:**
- Use learning curves to diagnose underfitting/overfitting and data sufficiency for any problem type.
- Use ROC curves for binary/imbalanced classification to assess discrimination ability.
- Use residual plots and predicted vs. actual plots for regression to check model fit and error patterns.
- Confusion matrices are helpful for understanding misclassifications in classification tasks.

edaflow provides functions for learning curves, ROC curves, and feature importance plots. Choose the visualization that best matches your metric and problem type for the most actionable insights.
Best Practices and Strategies for Hyperparameter Optimization
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

1. **Start Simple:**
    - Begin with default hyperparameters or a small grid. Only tune a few key hyperparameters at first (e.g., `n_estimators`, `max_depth`).

2. **Use Cross-Validation:**
    - Always evaluate hyperparameter combinations using cross-validation to avoid overfitting to a single train/test split.

3. **Limit Search Space:**
    - Define reasonable ranges for each hyperparameter. Avoid very large grids unless you have significant compute resources.

4. **Random Search for Large Spaces:**
    - For high-dimensional or continuous spaces, random search or Bayesian optimization is often more efficient than exhaustive grid search.

5. **Tune Important Hyperparameters First:**
    - Focus on hyperparameters that have the most impact (e.g., learning rate, tree depth, regularization). Fix less important ones to sensible defaults.

6. **Monitor for Overfitting:**
    - Watch for large gaps between training and validation scores. Use regularization and early stopping if available.

7. **Automate and Parallelize:**
    - Use tools that support parallel search or distributed computing to speed up tuning.

8. **Document Results:**
    - Keep track of tested combinations and their performance. This helps avoid redundant work and supports reproducibility.

9. **Balance Performance and Simplicity:**
    - The most complex model is not always the best. Prefer simpler models if performance is similar.

10. **Re-tune When Data Changes:**
     - If your data distribution changes significantly, re-run hyperparameter optimization.

**Strategy Examples:**

- **Grid Search:** Best for small, discrete search spaces and when you want to exhaustively test all combinations.
- **Random Search:** Good for large or continuous spaces; often finds good solutions faster than grid search.
- **Bayesian Optimization:** Efficient for expensive models or large search spaces; uses past results to guide the search.

edaflow supports both grid search and Bayesian optimization, so you can choose the strategy that best fits your problem and resources.

Baseline Models: A Starting Point
What Happens Under the Hood
~~~~~~~~~~~~~~~~~~~~~~~~~~
- Baseline models in edaflow are typically implemented using scikit-learn’s `DummyClassifier` or `DummyRegressor`.
- These models use simple strategies (e.g., most frequent, mean, median) to generate predictions.
- Including them in your model dictionary allows direct comparison with more advanced models in the same workflow.
- The results help you verify that your pipeline and metrics are working as expected before investing in complex modeling.
Machine Learning User Guide
===========================

This guide provides comprehensive examples and workflows for using edaflow's ML functions effectively.

Overview
--------

The edaflow.ml subpackage provides 26 functions organized into 5 categories:

* **Configuration & Setup** (3 functions): Experiment setup and data validation
* **Model Comparison** (4 functions): Multi-model evaluation and ranking  
* **Hyperparameter Tuning** (4 functions): Optimization strategies
* **Performance Visualization** (6 functions): ML-specific plots and curves
* **Model Artifacts** (4 functions): Model persistence and experiment tracking

Best Practice Scoring Metrics

Data Validation: A Critical First Step
--------------------------------------
Before comparing models, always validate your data. Data issues like missing values, high cardinality, or inconsistent distributions can lead to misleading results or model errors. edaflow provides the `validate_ml_data` function to help you:

- Detect missing values and outliers
- Check feature cardinality and distributions
- Ensure your data is suitable for modeling

**Best practice:** Run `validate_ml_data` on your training data before any model comparison. This ensures your results are reliable and helps prevent common pitfalls in ML workflows.

Example:

.. code-block:: python

   report = ml.validate_ml_data(
       X=X_train, y=y_train,
       check_missing=True,
       check_cardinality=True,
       check_distributions=True
   )

Review the validation report and address any issues before proceeding to model comparison.


**Data Quality Score:**
The `validate_ml_data` function provides a data quality score—a summary metric (typically from 0 to 1) that reflects the overall health of your dataset. A higher score means your data is cleaner, more complete, and better suited for modeling. Use this score to quickly assess readiness:

- **Tip:** The data quality score can also be used to compare the quality of different datasets. When you have multiple data sources or versions, use the score to objectively evaluate and select the dataset that is best suited for modeling. This helps ensure you are building models on the highest quality data available.

- **0.9–1.0:** Excellent quality, ready for modeling
- **0.7–0.9:** Good, but review warnings and minor issues
- **Below 0.7:** Significant issues—address missing values, outliers, or feature problems before proceeding

**Best practice:** Aim for a high data quality score to ensure robust, reliable model results.
---------------------------


Choosing the right scoring metric is critical for evaluating and comparing machine learning models. Here are the best practice metrics supported by edaflow, with practical guidance:

.. note::
    **Set Your Primary Metric in `setup_ml_experiment`!**

    Always specify the ``primary_metric`` parameter in your call to ``setup_ml_experiment``. This ensures that all downstream functions (like model ranking and best model selection) use the metric that matches your problem and business goals.

    **Example:**

    .. code-block:: python

        config = ml.setup_ml_experiment(
             X=X, y=y,
             test_size=0.2,
             val_size=0.15,
             experiment_name="my_experiment",
             primary_metric="roc_auc"  # Change this to 'f1', 'accuracy', 'r2', etc. as needed
        primary_metric="roc_auc"  # 👈 Set your main metric here! (e.g., 'f1', 'accuracy', 'r2', etc.)
        )

    **Tip:**
    - For classification, use ``primary_metric='roc_auc'``, ``'f1'``, or ``'accuracy'`` as appropriate.
    - For regression, use ``primary_metric='r2'``, ``'mae'``, or ``'rmse'``.
    - Choose the metric that best reflects your real-world success criteria!

**When to Choose Accuracy or F1 as Your Primary Metric**

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Selecting a primary metric depends on your dataset and business goals:

- **Accuracy** is best when your classes are balanced and all types of errors are equally important. It measures the overall proportion of correct predictions. Use accuracy as your primary metric when:
    - The dataset has roughly equal numbers of samples in each class.
    - False positives and false negatives have similar costs.
    - Example: Handwritten digit recognition, animal type classification with balanced classes.

- **F1 Score** is best when your classes are imbalanced or when you care about both precision and recall. It is especially useful when the positive class is rare or when missing positive cases is costly. Use F1 as your primary metric when:
    - The dataset is imbalanced (one class is much less frequent).
    - Both false positives and false negatives are important to minimize.
    - Example: Disease detection, fraud detection, spam filtering.

**Summary:**
- Use **accuracy** for balanced datasets and equal error costs.
- Use **F1** for imbalanced datasets or when both precision and recall matter.

Tracking both metrics can provide a more complete picture, but always select a primary metric that aligns with your real-world goals.

**Classification Metrics:**

- **accuracy**: Overall correctness. Use for balanced datasets.
- **precision**: Correctness of positive predictions. Important for imbalanced data (e.g., fraud detection).
- **recall**: Ability to find all positive samples. Use when missing positives is costly (e.g., medical diagnosis).
- **f1**: Harmonic mean of precision and recall. Best for imbalanced data when both precision and recall matter.
- **roc_auc**: Area under the ROC curve. Measures ranking quality, best for binary classification.

**Regression Metrics:**

- **mse**: Mean squared error. Penalizes large errors, sensitive to outliers.
- **mae**: Mean absolute error. Robust to outliers, interpretable.
- **rmse**: Root mean squared error. Like MSE, but in original units.
- **r2**: R-squared. Proportion of variance explained by the model.

**How to Use in edaflow**


You can specify any of these metrics in the `scoring` argument of `ml.compare_models`.

**About cv_folds**
~~~~~~~~~~~~~~~~~
The `cv_folds` parameter controls the number of cross-validation folds used to evaluate each model. Cross-validation splits your training data into several parts (folds), trains the model on some folds, and validates it on the remaining fold, repeating this process for each fold. The results are averaged to give a more reliable estimate of model performance.

- Typical values: 5 or 10 (5 is common and a good default)
- More folds = more reliable estimates, but longer runtime
- Use higher values for small datasets, and lower values for very large datasets

Example: `cv_folds=5` means 5-fold cross-validation (the data is split into 5 parts, each used once as validation).

**Other Key Parameters for Model Comparison**
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- **experiment_config**: Pass the output of `setup_ml_experiment()` to automatically use consistent train/validation/test splits and experiment settings. Best practice: Always use this for reproducibility and to avoid data leakage.

- **problem_type**: Set to `'classification'`, `'regression'`, or `'auto'` (default). `'auto'` will detect the problem type from your data. Best practice: Let edaflow auto-detect unless you have a special case.

- **metrics**: List of metrics to calculate for each model. If not set, edaflow uses the metrics in `scoring` or defaults based on problem type. Best practice: Specify only if you want extra metrics beyond those in `scoring`.

- **verbose**: If True (default), prints progress and helpful messages during comparison. Set to False for silent operation (e.g., in scripts or pipelines). Best practice: Keep verbose on for interactive work, off for automation.

These parameters help you follow best practices for reproducibility, clarity, and robust model evaluation in edaflow.

.. code-block:: python

   # Example: Compare models using all best practice metrics
   results = ml.compare_models(
       models=models,
       X_train=config['X_train'],
       y_train=config['y_train'],
       X_test=config['X_test'],
       y_test=config['y_test'],
       cv_folds=5,
       scoring=['accuracy', 'precision', 'recall', 'f1', 'roc_auc']
   )

   # For regression:
   results = ml.compare_models(
       models=models,
       X_train=X_train,
       y_train=y_train,
       X_test=X_test,
       y_test=y_test,
       cv_folds=5,
       scoring=['mse', 'mae', 'rmse', 'r2']
   )

**Tip:**
- For imbalanced classification, prefer `f1`, `precision`, and `recall` over `accuracy`.
- For regression, use both `mae` and `rmse` to understand error characteristics.

These metrics are recommended for most practical ML workflows and are fully supported in edaflow.

Choosing Metrics by Problem Type
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The best metric depends on your prediction target:

**Binary Classification (2 classes):**
- Use: `accuracy`, `precision`, `recall`, `f1`, `roc_auc`
- `roc_auc` is only available for binary targets (e.g., 0/1, True/False).
- Example: Disease prediction (yes/no), fraud detection (fraud/not fraud)

**Multiclass Classification (3+ classes):**
- Use: `accuracy`, `precision`, `recall`, `f1`
- `roc_auc` is not available in edaflow for multiclass (will show NaN)
- Example: Animal type (cat/dog/horse), digit recognition (0-9)

**Regression (continuous target):**
- Use: `mse`, `mae`, `rmse`, `r2`
- Example: House price prediction, temperature forecasting

**Tip:**
- If you see NaN for `roc_auc`, check if your target is multiclass or if your model lacks probability outputs.
- For multiclass ROC AUC, use scikit-learn directly or request an edaflow extension.

This guidance ensures you always choose the right metric for your ML problem type.

Practical Examples: Metric Selection
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

+---------------------------+---------------------+-------------------------------+
| Scenario                  | Recommended Metrics | Why/When to Use               |
+===========================+=====================+===============================+
| Disease prediction        | f1, recall, roc_auc | Imbalanced, missing positives |
| (binary classification)   |                     | is costly                     |
+---------------------------+---------------------+-------------------------------+
| Spam detection            | precision, f1       | Imbalanced, false positives   |
| (binary classification)   |                     | are costly                    |
+---------------------------+---------------------+-------------------------------+
| Animal type classification| accuracy, f1        | Multiclass, balanced classes  |
| (multiclass classification)|                    |                               |
+---------------------------+---------------------+-------------------------------+
| Digit recognition         | accuracy, f1        | Multiclass, balanced          |
| (multiclass classification)|                    |                               |
+---------------------------+---------------------+-------------------------------+
| House price prediction    | mae, rmse, r2       | Regression, interpretability  |
| (regression)              |                     | and error size matter         |
+---------------------------+---------------------+-------------------------------+
| Energy demand forecasting | mae, mse, r2        | Regression, outlier-robust    |
| (regression)              |                     | and variance explained        |
+---------------------------+---------------------+-------------------------------+

**Tip:**
- For imbalanced binary classification, use `f1`, `recall`, and `roc_auc`.
- For multiclass, use `accuracy` and `f1`.
- For regression, use both `mae` and `rmse` for a full error picture.

Complete ML Workflow Example
-----------------------------

Here's a comprehensive example showing the full ML workflow:

.. code-block:: python

   import edaflow.ml as ml
   import pandas as pd
   from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
   from sklearn.linear_model import LogisticRegression
   from sklearn.svm import SVC

   # Load your data
   df = pd.read_csv('your_data.csv')
   X = df.drop('target', axis=1)
   y = df['target']

   # Step 1: Setup ML Experiment
   config = ml.setup_ml_experiment(
       X=X, 
       y=y,
       test_size=0.2,
       val_size=0.15,
       experiment_name="comprehensive_model_comparison",
       random_state=42
   )

   # Step 2: Validate Data Quality
   validation_report = ml.validate_ml_data(
       X=config['X_train'],
       y=config['y_train'],
       check_missing=True,
       check_cardinality=True,
       check_distributions=True
   )

   # Step 3: Configure Preprocessing Pipeline
   pipeline_config = ml.configure_model_pipeline(
       data_config=config,
       numerical_strategy='standard',
       categorical_strategy='onehot',
       handle_missing='impute',
       verbose=True
   )

   # Step 4: Compare Multiple Models
   models = {
       'random_forest': RandomForestClassifier(n_estimators=100, random_state=42),
       'gradient_boosting': GradientBoostingClassifier(n_estimators=100, random_state=42),
       'logistic_regression': LogisticRegression(random_state=42),
       'svm': SVC(probability=True, random_state=42)
   }

   # 🚨 CRITICAL: Train all models first!
   print("🔧 Training models...")
   for name, model in models.items():
       model.fit(config['X_train'], config['y_train'])
       print(f"✅ {name} trained")

   comparison_results = ml.compare_models(
       models=models,
       X_train=config['X_train'],
       y_train=config['y_train'],
       X_test=config['X_test'],
       y_test=config['y_test'],
       cv_folds=5,
       scoring=['accuracy', 'precision', 'recall', 'f1', 'roc_auc']
   )

   # Step 5: Display Model Leaderboard
   ml.display_leaderboard(
       comparison_results=comparison_results,
       sort_by='roc_auc',
       ascending=False,
       show_std=True,
       figsize=(12, 4)
   )

   # Step 6: Rank Models and Select Best Performer

   # Dynamically select the best model based on the primary metric
   primary_metric = config.get('primary_metric', 'roc_auc')  # fallback to 'roc_auc' if not set

   # Method 1: DataFrame format (traditional)
   ranked_df = ml.rank_models(comparison_results, primary_metric)
   best_model_traditional = ranked_df.iloc[0]['model']

   # Method 2: List format (easy dictionary access)
   best_model = ml.rank_models(
       comparison_results,
       primary_metric,
       return_format='list'
   )[0]['model_name']

   print(f"Best performing model (by {primary_metric}): {best_model}")
   
   # Step 7: Hyperparameter Optimization for Best Model
   if best_model == 'random_forest':
       param_distributions = {
           'n_estimators': [50, 100, 200],
           'max_depth': [3, 5, 7, None],
           'min_samples_split': [2, 5, 10],
           'min_samples_leaf': [1, 2, 4]
       }
   
   tuning_results = ml.optimize_hyperparameters(
       model=RandomForestClassifier(random_state=42),
       X_train=config['X_train'],
       y_train=config['y_train'],
       param_distributions=param_distributions,
       method='random',
       n_iter=50,
       cv=5,
       scoring='roc_auc'
   )

   # Step 8: Performance Visualizations
   best_tuned_model = tuning_results['best_model']
   
   # Learning curves
   ml.plot_learning_curves(
       model=best_tuned_model,
       X_train=config['X_train'],
       y_train=config['y_train'],
       cv=5,
       scoring='roc_auc'
   )
   
   # ROC curves
   ml.plot_roc_curves(
       models={'tuned_model': best_tuned_model},
       X_val=config['X_test'],
       y_val=config['y_test']
   )
   
   # Feature importance
   ml.plot_feature_importance(
       model=best_tuned_model,
       feature_names=config['X_train'].columns,
       top_n=15
   )

   # Step 9: Save Model Artifacts
   artifact_paths = ml.save_model_artifacts(
       model=best_tuned_model,
       model_name="best_tuned_rf_model",
       experiment_config=config,
       performance_metrics=tuning_results['best_score_dict'],
       save_dir="production_models",
       include_data_sample=True,
       X_sample=config['X_train'].head(100)
   )

   # Step 10: Track Experiment
   ml.track_experiment(
       experiment_name=config['experiment_name'],
       model_results=comparison_results,
       tuning_results=tuning_results,
       final_model_path=artifact_paths['model_path'],
       notes="Comprehensive model comparison with hyperparameter tuning"
   )

   # Step 11: Generate Model Report
   ml.create_model_report(
       model=best_tuned_model,
       experiment_config=config,
       performance_metrics=tuning_results['best_score_dict'],
       model_comparison=comparison_results,
       save_path="model_reports/comprehensive_analysis.pdf"
   )

Individual Function Examples
----------------------------

Configuration Functions
~~~~~~~~~~~~~~~~~~~~~~~~

**Setup ML Experiment**

.. code-block:: python

   # Basic setup
   config = ml.setup_ml_experiment(X=X, y=y)
   
   # Advanced setup with custom splits
   config = ml.setup_ml_experiment(
       X=X, y=y,
       test_size=0.2,
       val_size=0.15,
       stratify=True,
       experiment_name="advanced_experiment",
       random_state=42,
       create_directories=True
   )

**Validate ML Data**

.. code-block:: python

   # Comprehensive data validation
   report = ml.validate_ml_data(
       X=X_train, y=y_train,
       check_missing=True,
       check_cardinality=True,
       check_distributions=True,
       missing_threshold=0.1,
       high_cardinality_threshold=50
   )

Model Comparison Functions
How Model Comparison and Leaderboards Work in edaflow
-----------------------------------------------------

edaflow makes it easy to compare multiple models and visualize their performance side by side. Here’s how the workflow operates and what you can expect:

**How `ml.compare_models` Works:**
- Takes a dictionary of models and your train/test data.
- Runs cross-validation (using `cv_folds`) for each model, fitting and evaluating them on the specified metrics.
- Returns a results object (usually a DataFrame) with each model’s average scores for all metrics, plus standard deviations if applicable.
- Supports both classification and regression models.

**How `ml.display_leaderboard` Works:**
- Takes the results from `ml.compare_models` and displays them in a clear, sortable table (the leaderboard).
- You can choose which metric to sort by (e.g., accuracy, f1, roc_auc, mae, etc.).
- The leaderboard highlights the best-performing models for each metric and can show standard deviations to help you assess model stability.
- Options like `highlight_best`, `show_std`, and `figsize` let you customize the display.

**What You’ll See:**
- A table or plot with model names as rows and metrics as columns.
- The best model(s) for each metric are highlighted.
- You can quickly spot which models perform best overall or on specific metrics.
- Standard deviations (if shown) help you judge the consistency of each model’s performance.

**How to Use the Output:**
- Use the leaderboard to select the best model for your needs (e.g., highest f1 for imbalanced classification, lowest rmse for regression).
- Compare models not just on average scores, but also on their stability (std) and performance across multiple metrics.
- Export or save the leaderboard for reporting or further analysis.

**Example Workflow:**

.. code-block:: python

   results = ml.compare_models(
       models=models,
       X_train=X_train, y_train=y_train,
       X_test=X_test, y_test=y_test,
       cv_folds=5,
       scoring=['accuracy', 'f1', 'roc_auc']
   )

   ml.display_leaderboard(
       comparison_results=results,
       sort_by='f1',
       show_std=True,
       highlight_best=True,
       figsize=(10, 4)
   )

This workflow helps you make informed, data-driven choices about which model to use in production or further tuning.
~~~~~~~~~~~~~~~~~~~~~~~~~~

**Compare Models**

.. code-block:: python

   # Quick model comparison
   models = {
       'rf': RandomForestClassifier(),
       'lr': LogisticRegression(),
       'svm': SVC(probability=True)
   }
   
   results = ml.compare_models(
       models=models,
       X_train=X_train, y_train=y_train,
       X_test=X_test, y_test=y_test,
       cv_folds=5
   )

**Display Leaderboard**

.. code-block:: python

   # Show model rankings
   ml.display_leaderboard(
       comparison_results=results,
       sort_by='f1_score',
       show_std=True,
       highlight_best=True,
       figsize=(12, 4)
   )

**Rank Models**

The ``rank_models`` function provides flexible model ranking with two return formats:

.. code-block:: python

   # DataFrame format (traditional, backward compatible)
   ranked_df = ml.rank_models(
       comparison_df=results,
       primary_metric='accuracy'
   )
   
   # Access best model
   best_model = ranked_df.iloc[0]['model']
   best_accuracy = ranked_df.iloc[0]['accuracy']
   
   print(f"Best model: {best_model} (accuracy: {best_accuracy:.4f})")

   # List format (dictionary access)
   ranked_list = ml.rank_models(
       comparison_df=results,
       primary_metric='accuracy',
       return_format='list'
   )
   
   # Easy dictionary access patterns
   best_model_name = ranked_list[0]["model_name"]
   best_accuracy = ranked_list[0]["accuracy"]
   best_f1 = ranked_list[0]["f1"]
   
   # One-liner pattern for best model
   best_model = ml.rank_models(results, 'accuracy', return_format='list')[0]["model_name"]
   
   # Access all ranked models
   print("All models ranked by accuracy:")
   for i, model_info in enumerate(ranked_list):
       print(f"{i+1}. {model_info['model_name']}: {model_info['accuracy']:.4f}")

**Advanced Ranking Options**

.. code-block:: python

   # Rank by different metrics
   ranked_by_f1 = ml.rank_models(results, 'f1_score', return_format='list')
   ranked_by_precision = ml.rank_models(results, 'precision', return_format='list')
   
   # Ascending order (useful for error metrics)
   ranked_by_error = ml.rank_models(
       results, 
       'validation_error', 
       ascending=True,  # Lower error is better
       return_format='list'
   )
   
   # Weighted multi-metric ranking
   ranked_weighted = ml.rank_models(
       comparison_df=results,
       primary_metric='accuracy',
       weights={
           'accuracy': 0.4,
           'f1_score': 0.3,
           'precision': 0.2,
           'recall': 0.1
       },
       return_format='list'
   )
   
   best_overall = ranked_weighted[0]["model_name"]
   print(f"Best model by weighted score: {best_overall}")

**Return Format Comparison**

.. code-block:: python

   # Both formats provide the same ranking
   df_format = ml.rank_models(results, 'accuracy')
   list_format = ml.rank_models(results, 'accuracy', return_format='list')
   
   # DataFrame format - good for analysis and display
   print("Top 3 models (DataFrame):")
   print(df_format.head(3)[['model', 'accuracy', 'f1', 'rank']])
   
   # List format - easy programmatic access
   print("Top 3 models (List):")
   for i, model in enumerate(list_format[:3]):
       print(f"{i+1}. {model['model_name']}: {model['accuracy']:.4f}")
   
   # Choose format based on your needs:
   # - DataFrame: Analysis, filtering, display
   # - List: Simple access, iteration, one-liners

Hyperparameter Tuning Functions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

What is Hyperparameter Optimization?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Hyperparameter optimization (also called hyperparameter tuning) is the process of systematically searching for the best combination of settings (hyperparameters) that control how a machine learning model learns from data. Unlike model parameters (which are learned during training, such as weights in a neural network), hyperparameters are set before training and can significantly affect model performance.

Common hyperparameters include:
- Number of trees in a random forest (`n_estimators`)
- Maximum tree depth (`max_depth`)
- Learning rate for boosting algorithms
- Regularization strength
- Kernel type for SVMs

Why is it important?
--------------------
The right hyperparameters can dramatically improve a model’s accuracy, generalization, and robustness. Poorly chosen hyperparameters can lead to underfitting, overfitting, or unnecessarily slow training.

How does it work?
-----------------
Hyperparameter optimization involves:
1. Defining a search space (the possible values for each hyperparameter).
2. Selecting a search strategy (e.g., grid search, random search, Bayesian optimization).
3. Evaluating model performance for each combination using cross-validation or a holdout set.
4. Selecting the combination that yields the best results according to a chosen metric (e.g., accuracy, F1 score).

edaflow provides utilities for both grid search and Bayesian optimization, making it easy to tune models for optimal performance.

**Grid Search**

.. code-block:: python

   param_grid = {
       'n_estimators': [100, 200],
       'max_depth': [3, 5, None]
   }
   
   grid_results = ml.grid_search_models(
       models={'RandomForest': RandomForestClassifier()},
       param_grids={'RandomForest': param_grid},
       X_train=X_train, y_train=y_train,
       cv=5,
       scoring='accuracy'
   )

**Bayesian Optimization**

.. code-block:: python

   param_space = {
       'n_estimators': (50, 200),
       'max_depth': (3, 10),
       'min_samples_split': (2, 20)
   }
   
   bayes_results = ml.bayesian_optimization(
       model=RandomForestClassifier(),
       param_space=param_space,
       X_train=X_train, y_train=y_train,
       n_calls=50,
       cv=5
   )

Performance Visualization Functions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Learning Curves**

.. code-block:: python

   ml.plot_learning_curves(
       model=model,
       X_train=X_train, y_train=y_train,
       cv=5,
       train_sizes=np.linspace(0.1, 1.0, 10),
       scoring='f1_weighted'
   )

**ROC Curves**

.. code-block:: python

   ml.plot_roc_curves(
       models={'Model 1': model1, 'Model 2': model2},
       X_val=X_test, y_val=y_test,
       title="Model Comparison ROC Curves"
   )

Model Artifacts Functions
~~~~~~~~~~~~~~~~~~~~~~~~~

Saving and Managing Model Artifacts
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Saving model artifacts is essential for reproducibility, deployment, and collaboration. Here are best practices and tips for managing your models and experiment outputs:

1. **Save Everything Needed for Reproducibility:**
    - Always save the trained model, the configuration (hyperparameters, preprocessing steps), and the performance metrics.
    - Use `ml.save_model_artifacts()` to bundle these together in a single directory or file.

2. **Use Clear Naming Conventions:**
    - Name your model files with version numbers, dates, or experiment IDs (e.g., `production_model_v1.joblib`, `rf_exp2025-08-14.joblib`).
    - This makes it easy to track which model was used for which experiment or deployment.

3. **Track Experiment Metadata:**
    - Save experiment configuration, random seeds, and data splits alongside your model. This ensures you can reproduce results exactly.
    - Consider using experiment tracking tools or a simple spreadsheet/log to record key details.

4. **Test Loading Before Deployment:**
    - After saving, always test loading the model and running a prediction to ensure the artifact is valid and compatible with your environment.

5. **Store Artifacts Securely:**
    - Keep production models in a version-controlled or access-controlled location (e.g., cloud storage, artifact repository).
    - Avoid storing sensitive data in model artifacts unless necessary, and document any data included.

6. **Document Model Lineage:**
    - Record which data, code version, and hyperparameters produced each model artifact. This is critical for audits and troubleshooting.

7. **Automate Artifact Management:**
    - Integrate artifact saving and loading into your ML pipeline to reduce manual errors and ensure consistency.

By following these practices, you ensure your models are reproducible, auditable, and ready for deployment or further analysis.

**Save Model Artifacts**

.. code-block:: python

   paths = ml.save_model_artifacts(
       model=trained_model,
       model_name="production_model_v1",
       experiment_config=config,
       performance_metrics=metrics,
       save_dir="models/production",
       format='joblib'
   )

**Load Model Artifacts**

.. code-block:: python

   loaded_artifacts = ml.load_model_artifacts(
       model_path="models/production/production_model_v1.joblib"
   )
   
   model = loaded_artifacts['model']
   config = loaded_artifacts['config']
   metrics = loaded_artifacts['metrics']

Best Practices
--------------

1. **Always start with setup_ml_experiment()** to ensure consistent data splits
2. **Validate your data** with validate_ml_data() before training
3. **Use compare_models()** to evaluate multiple algorithms quickly  
4. **Apply hyperparameter tuning** only to your best-performing models
5. **Save model artifacts** with comprehensive metadata for reproducibility
6. **Track experiments** to maintain a history of your ML work
7. **Generate model reports** for stakeholder communication

Integration with EDA
Baseline Models: A Starting Point
---------------------------------

Before building complex machine learning models, it's important to establish a baseline. A baseline model is a simple model that provides a minimum benchmark for performance. Comparing your advanced models to a baseline helps you understand if your modeling efforts are truly adding value.

**What is a Baseline Model?**

- A baseline model is a simple, easy-to-implement model that makes predictions using basic rules or heuristics.
- It sets a reference point for model performance—your goal is to outperform the baseline.
- If your advanced model does not beat the baseline, it may indicate issues with your data, features, or modeling approach.

**Why Use Baseline Models?**

- They help you detect data leakage or target leakage.
- They provide context for interpreting model results.
- They are quick to implement and require no tuning.

**Common Baseline Models**

*For Classification:*

- **DummyClassifier** (from scikit-learn):
    - "most_frequent": Always predicts the most common class in the training data.
    - "stratified": Predicts according to the class distribution.
    - "uniform": Predicts classes uniformly at random.

*For Regression:*

- **DummyRegressor** (from scikit-learn):
    - "mean": Always predicts the mean of the training targets.
    - "median": Always predicts the median of the training targets.

**How to Use Baseline Models in edaflow**

You can include baseline models in your model dictionary when using `ml.compare_models`. Here is an example:

.. code-block:: python

   from sklearn.dummy import DummyClassifier, DummyRegressor

   # For classification
   models = {
       'dummy_most_frequent': DummyClassifier(strategy='most_frequent'),
       'dummy_stratified': DummyClassifier(strategy='stratified'),
       # Add your real models here
   }

   results = ml.compare_models(
       models=models,
       X_train=X_train, y_train=y_train,
       X_test=X_test, y_test=y_test,
       cv_folds=5
   )

   # For regression
   models = {
       'dummy_mean': DummyRegressor(strategy='mean'),
       'dummy_median': DummyRegressor(strategy='median'),
       # Add your real models here
   }

   results = ml.compare_models(
       models=models,
       X_train=X_train, y_train=y_train,
       X_test=X_test, y_test=y_test,
       cv_folds=5
   )

**Best Practice:**
- Always include at least one baseline model in your comparisons.
- If your best model does not outperform the baseline, revisit your data, features, or modeling approach.

This approach ensures you have a solid reference point and helps you build more robust, trustworthy machine learning solutions.
---------------------

Widely Used Model Types in Machine Learning
-------------------------------------------

edaflow supports a wide range of models from scikit-learn and compatible libraries. Here are the most common types you can use for classification and regression:

**Classification Models:**

- **Logistic Regression**
    - Good baseline for linear problems.
    - `from sklearn.linear_model import LogisticRegression`
- **Decision Tree Classifier**
    - Interpretable, handles non-linear data.
    - `from sklearn.tree import DecisionTreeClassifier`
- **Random Forest Classifier**
    - Robust ensemble of decision trees.
    - `from sklearn.ensemble import RandomForestClassifier`
- **Gradient Boosting Classifier**
    - Powerful for tabular data.
    - `from sklearn.ensemble import GradientBoostingClassifier`
- **K-Nearest Neighbors (KNN) Classifier**
    - Simple, non-parametric.
    - `from sklearn.neighbors import KNeighborsClassifier`
- **Naive Bayes**
    - Fast, good for text and categorical data.
    - `from sklearn.naive_bayes import GaussianNB`
- **Support Vector Machine (SVM)**
    - Effective for high-dimensional data.
    - `from sklearn.svm import SVC`
- **Neural Network (MLPClassifier)**
    - Flexible, can model complex patterns.
    - `from sklearn.neural_network import MLPClassifier`
- **Ensemble Methods**
    - Bagging, Stacking, Voting, AdaBoost, ExtraTrees.
    - `from sklearn.ensemble import BaggingClassifier, StackingClassifier, VotingClassifier, AdaBoostClassifier, ExtraTreesClassifier`
- **Advanced Boosting Libraries**
    - XGBoost, LightGBM, CatBoost (install separately).
    - `from xgboost import XGBClassifier`, `from lightgbm import LGBMClassifier`, `from catboost import CatBoostClassifier`

**Regression Models:**

- **Linear Regression**
    - Standard for continuous targets.
    - `from sklearn.linear_model import LinearRegression`
- **Ridge, Lasso, ElasticNet**
    - Regularized linear models.
    - `from sklearn.linear_model import Ridge, Lasso, ElasticNet`
- **Decision Tree Regressor**
    - Non-linear, interpretable.
    - `from sklearn.tree import DecisionTreeRegressor`
- **Random Forest Regressor**
    - Ensemble, robust to overfitting.
    - `from sklearn.ensemble import RandomForestRegressor`
- **Gradient Boosting Regressor**
    - Powerful for many regression tasks.
    - `from sklearn.ensemble import GradientBoostingRegressor`
- **K-Nearest Neighbors (KNN) Regressor**
    - Simple, non-parametric.
    - `from sklearn.neighbors import KNeighborsRegressor`
- **Support Vector Regressor (SVR)**
    - Effective for high-dimensional regression.
    - `from sklearn.svm import SVR`
- **Neural Network (MLPRegressor)**
    - Flexible, can model complex patterns.
    - `from sklearn.neural_network import MLPRegressor`
- **Ensemble Methods**
    - Bagging, Stacking, Voting, AdaBoost, ExtraTrees.
    - `from sklearn.ensemble import BaggingRegressor, StackingRegressor, VotingRegressor, AdaBoostRegressor, ExtraTreesRegressor`
- **Advanced Boosting Libraries**
    - XGBoost, LightGBM, CatBoost (install separately).
    - `from xgboost import XGBRegressor`, `from lightgbm import LGBMRegressor`, `from catboost import CatBoostRegressor`

**Example: Adding Multiple Model Types to edaflow**

.. code-block:: python

     from sklearn.linear_model import LogisticRegression, LinearRegression
     from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, RandomForestRegressor, GradientBoostingRegressor
     from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
     from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor
     from sklearn.naive_bayes import GaussianNB
     from sklearn.svm import SVC, SVR
     from sklearn.neural_network import MLPClassifier, MLPRegressor

     # For classification
     models = {
             'logistic_regression': LogisticRegression(),
             'decision_tree': DecisionTreeClassifier(),
             'random_forest': RandomForestClassifier(),
             'gradient_boosting': GradientBoostingClassifier(),
             'knn': KNeighborsClassifier(),
             'naive_bayes': GaussianNB(),
             'svm': SVC(probability=True),
             'mlp': MLPClassifier()
     }

     # For regression
     models = {
             'linear_regression': LinearRegression(),
             'decision_tree': DecisionTreeRegressor(),
             'random_forest': RandomForestRegressor(),
             'gradient_boosting': GradientBoostingRegressor(),
             'knn': KNeighborsRegressor(),
             'svr': SVR(),
             'mlp': MLPRegressor()
     }

**Note:** For XGBoost, LightGBM, and CatBoost, you must install the libraries separately (e.g., `pip install xgboost lightgbm catboost`).

Refer to scikit-learn and the respective library documentation for more details and advanced options.
---------------------

The ML functions integrate seamlessly with edaflow's EDA capabilities:

.. code-block:: python

   # Start with EDA
   edaflow.check_null_columns(df)
   edaflow.analyze_categorical_columns(df) 
   edaflow.visualize_heatmap(df)
   
   # Clean and prepare data
   df_clean = edaflow.convert_to_numeric(df)
   df_imputed = edaflow.impute_numerical_median(df_clean)
   
   # Transition to ML workflow  
   X = df_imputed.drop('target', axis=1)
   y = df_imputed['target']
   
   config = ml.setup_ml_experiment(X=X, y=y)
   # ... continue with ML workflow


This creates a complete data science pipeline from exploration to model deployment.

What's Next After Training the Model?
------------------------------------

Completing the ML workflow is a major milestone, but impactful data science continues beyond model training. Here are the recommended next steps to ensure your work delivers value in real-world settings:

1. **Model Deployment**
    - Deploy your trained model to production environments (web apps, APIs, batch jobs, etc.).
    - Consider using tools like Flask, FastAPI, Streamlit, or cloud services (Azure ML, AWS SageMaker, GCP AI Platform).
    - Ensure reproducibility by saving model artifacts and environment details.

2. **Model Monitoring & Maintenance**
    - Track model performance over time to detect data drift or performance degradation.
    - Set up alerts for significant drops in accuracy or changes in data distribution.
    - Plan for periodic retraining as new data becomes available.

3. **Interpretability & Reporting**
    - Use model explainability tools (e.g., SHAP, LIME) to interpret predictions and build trust with stakeholders.
    - Generate clear reports and visualizations for both technical and non-technical audiences.

4. **Collaboration & Documentation**
    - Document your workflow, decisions, and results for future reference and team collaboration.
    - Share code, artifacts, and experiment logs using version control and collaborative platforms.

5. **Iterative Improvement**
    - Gather feedback from users and stakeholders to identify areas for improvement.
    - Iterate on feature engineering, model selection, and hyperparameter tuning as needed.

**Checklist: Post-ML Workflow Actions**

- [ ] Deploy the selected model to a test or production environment
- [ ] Set up monitoring for model performance and data drift
- [ ] Document the workflow, results, and key decisions
- [ ] Share reports and artifacts with stakeholders
- [ ] Plan for regular model review and retraining

By following these steps, you ensure your machine learning solutions remain robust, interpretable, and valuable over time.
