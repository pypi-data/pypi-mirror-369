Data Quality & Cleaning
========================

This guide covers edaflow's data quality assessment and cleaning capabilities.

Overview
--------

Data quality is the foundation of any successful data analysis or machine learning project. edaflow provides comprehensive tools for:

* **Missing Data Analysis**: Identify and visualize null values
* **Data Type Issues**: Detect and fix incorrect data types
* **Data Imputation**: Smart strategies for handling missing values  
* **Outlier Detection**: Identify and handle anomalous values

Missing Data Analysis
What Happens Under the Hood
~~~~~~~~~~~~~~~~~~~~~~~~~~
- `edaflow.check_null_columns` uses pandas to scan each column for null values and calculates the percentage of missing data.
- It generates a visual summary (e.g., heatmap or color-coded table) to highlight missingness patterns.
- The function applies user-defined thresholds to trigger warnings and provides actionable recommendations based on the severity of missing data.
---------------------

The first step in any EDA workflow should be understanding your missing data patterns.

**Basic Null Analysis**

.. code-block:: python

   import edaflow
   import pandas as pd
   
   df = pd.read_csv('your_data.csv')
   
   # Comprehensive null analysis
   edaflow.check_null_columns(df)

This function provides:

* **Visual null pattern display** with color coding
* **Percentage calculations** for each column
* **Threshold-based warnings** for high null percentages
* **Actionable recommendations** for handling missing data

**Customizing Null Analysis**

.. code-block:: python

   # Custom threshold for warnings
   edaflow.check_null_columns(df, threshold=15)  # Warn if >15% null

Data Type Conversion
What Happens Under the Hood
~~~~~~~~~~~~~~~~~~~~~~~~~~
- `edaflow.analyze_categorical_columns` inspects object columns to determine if they can be safely converted to numeric types, using heuristics and value checks.
- `edaflow.convert_to_numeric` attempts conversion for columns that meet the threshold, handling errors gracefully and reporting any columns that could not be converted.
- `edaflow.display_column_types` summarizes the current data types for all columns, making it easy to spot inconsistencies.
--------------------

Many datasets have columns that should be numeric but are stored as objects/strings.

**Smart Type Detection**

.. code-block:: python

   # Analyze which object columns could be numeric
   edaflow.analyze_categorical_columns(df)

**Automatic Conversion**

.. code-block:: python

   # Convert object columns to numeric when appropriate
   df_converted = edaflow.convert_to_numeric(df, threshold=25)

**Display Current Types**

.. code-block:: python

   # See all column data types in a clean format
   edaflow.display_column_types(df)

Data Imputation Strategies
What Happens Under the Hood
~~~~~~~~~~~~~~~~~~~~~~~~~~
- edaflow’s imputation utilities detect column types (numerical, categorical) and select the appropriate imputation strategy (mean, median, mode, or custom logic).
- The imputation process is applied column-wise, with missing values filled in-place or in a copy, depending on user preference.
- All imputation steps are logged or reported, ensuring transparency and reproducibility in the cleaning workflow.
---------------------------

edaflow provides intelligent imputation methods for different data types.

**Numerical Imputation**

.. code-block:: python

   # Use median for numerical columns (robust to outliers)
   df_imputed = edaflow.impute_numerical_median(df)

**Categorical Imputation**

.. code-block:: python

   # Use mode (most frequent value) for categorical columns
   df_imputed = edaflow.impute_categorical_mode(df)

**Combined Approach**

.. code-block:: python

   # Complete imputation workflow
   df_clean = edaflow.convert_to_numeric(df)
   df_clean = edaflow.impute_numerical_median(df_clean)
   df_clean = edaflow.impute_categorical_mode(df_clean)

Outlier Detection and Handling
What Happens Under the Hood
~~~~~~~~~~~~~~~~~~~~~~~~~~
- edaflow’s outlier detection tools use statistical methods (e.g., IQR, Z-score) to flag values that deviate significantly from the norm.
- Visualizations (such as boxplots) are generated to help users quickly spot and interpret outliers.
- The functions can optionally remove or cap outliers, with all actions logged for transparency.
-------------------------------

Outliers can significantly impact analysis and model performance.

**Automated Outlier Handling**

.. code-block:: python

   # Replace outliers with median values
   df_no_outliers = edaflow.handle_outliers_median(
       df, 
       method='z_score',  # or 'iqr'
       threshold=3
   )

**Method Options:**

* **Z-Score Method**: Identifies values >3 standard deviations from mean
* **IQR Method**: Uses interquartile range to identify outliers
* **Median Replacement**: Robust strategy that maintains data distribution

Best Practices Workflow
What Happens Under the Hood
~~~~~~~~~~~~~~~~~~~~~~~~~~
- The workflow combines all edaflow data quality utilities in a recommended sequence, ensuring each cleaning step builds on the previous one.
- Each function logs its actions and results, making the process auditable and reproducible.
- The workflow is modular, so users can customize or skip steps as needed for their specific data challenges.
------------------------

Here's a recommended data quality workflow:

.. code-block:: python

   import edaflow
   import pandas as pd
   
   # 1. Load and inspect data
   df = pd.read_csv('your_data.csv')
   print(f"Dataset shape: {df.shape}")
   
   # 2. Check for missing values
   edaflow.check_null_columns(df, threshold=10)
   
   # 3. Analyze data types
   edaflow.analyze_categorical_columns(df)
   edaflow.display_column_types(df)
   
   # 4. Convert types where appropriate
   df_converted = edaflow.convert_to_numeric(df, threshold=30)
   
   # 5. Handle missing values
   df_imputed = edaflow.impute_numerical_median(df_converted)
   df_imputed = edaflow.impute_categorical_mode(df_imputed)
   
   # 6. Handle outliers
   df_clean = edaflow.handle_outliers_median(
       df_imputed, 
       method='iqr'
   )
   
   # 7. Verify improvements
   print(f"Null values after cleaning: {df_clean.isnull().sum().sum()}")
   edaflow.display_column_types(df_clean)

Common Data Quality Issues
What Happens Under the Hood
~~~~~~~~~~~~~~~~~~~~~~~~~~
- edaflow scans for common data quality issues using a library of heuristics and pattern checks (e.g., constant columns, duplicate rows, mixed types).
- Detected issues are summarized in a report, with severity levels and suggested remediation steps.
- The system is extensible, allowing new issue types to be added as data challenges evolve.
---------------------------

**Mixed Data Types in Columns**

.. code-block:: python

   # Example: Price column with '$' symbols and 'Free' text
   # edaflow automatically handles these cases
   df_converted = edaflow.convert_to_numeric(df)

**Inconsistent Missing Value Representations**

.. code-block:: python

   # Handle various null representations before using edaflow
   df = df.replace(['N/A', 'n/a', 'NULL', ''], pd.NA)
   edaflow.check_null_columns(df)

**Date Columns as Objects**

.. code-block:: python

   # Convert dates after using edaflow's type analysis
   date_columns = ['created_date', 'modified_date']
   for col in date_columns:
       if col in df.columns:
           df[col] = pd.to_datetime(df[col], errors='coerce')

Integration with ML Workflow
What Happens Under the Hood
~~~~~~~~~~~~~~~~~~~~~~~~~~
- edaflow’s data quality outputs (cleaned data, reports, logs) are designed to integrate seamlessly with its ML experiment setup and modeling functions.
- Cleaned datasets and quality scores can be passed directly to ML workflows, ensuring consistency and traceability.
- Integration points are documented so users can automate the transition from EDA to modeling.
-----------------------------

Clean data is essential for machine learning:

.. code-block:: python

   # After cleaning with edaflow
   import edaflow.ml as ml
   
   # The ML functions expect clean data
   X = df_clean.drop('target', axis=1)
   y = df_clean['target']
   
   # Setup ML experiment with validated data
   config = ml.setup_ml_experiment(
      X=X, y=y,
      primary_metric="roc_auc"  # 👈 Set your main metric here! (e.g., 'f1', 'accuracy', 'r2', etc.)
   )
   
   # Additional ML-specific validation
   validation_report = ml.validate_ml_data(
       X=config['X_train'],
       y=config['y_train']
   )

Tips for Large Datasets
What Happens Under the Hood
~~~~~~~~~~~~~~~~~~~~~~~~~~
- edaflow uses efficient, vectorized operations (via pandas/numpy) to handle large datasets without excessive memory usage.
- For very large data, sampling and chunked processing options are available to maintain performance.
- All tips are based on practical experience with real-world, large-scale data cleaning tasks.
------------------------

**Memory Efficiency**

.. code-block:: python

   # For large datasets, process in chunks or use specific columns
   columns_to_analyze = ['col1', 'col2', 'col3']
   edaflow.check_null_columns(df[columns_to_analyze])

**Sampling Strategy**

.. code-block:: python

   # Analyze a representative sample first
   sample_df = df.sample(n=10000, random_state=42)
   edaflow.analyze_categorical_columns(sample_df)
   
   # Apply insights to full dataset
   df_converted = edaflow.convert_to_numeric(df)

Quality Assessment Checklist
What Happens Under the Hood
~~~~~~~~~~~~~~~~~~~~~~~~~~
- The checklist is generated from the results of all previous edaflow data quality checks and cleaning steps.
- It provides a structured summary of what has been validated, cleaned, or flagged for review.
- The checklist can be exported or included in reports for documentation and audit purposes.
-----------------------------

Use this checklist to ensure comprehensive data quality assessment:

- [ ] **Missing Data**: Check null patterns and percentages
- [ ] **Data Types**: Verify appropriate types for each column
- [ ] **Duplicates**: Check for and remove duplicate rows
- [ ] **Outliers**: Identify and decide on handling strategy
- [ ] **Consistency**: Check for consistent formatting within columns
- [ ] **Completeness**: Ensure all required fields are present
- [ ] **Validity**: Verify data values make sense in context
- [ ] **Uniqueness**: Check ID fields are truly unique
