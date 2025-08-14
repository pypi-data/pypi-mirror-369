# Decision Tree Visualization and Classification Analysis Toolkit and basic graphs

![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

A comprehensive Python package for creating interactive decision tree visualizations and performing advanced classification model analysis.

## Features

- **Interactive HTML Decision Trees**: Visualize decision paths with D3.js
- **Automated Model Comparison**: Evaluate multiple classifiers with one function
- **Feature Importance Analysis**: Multiple methods including SHAP, permutation, and native importance
- **Probability Analysis**: Visualize prediction distributions
- **Data Preprocessing**: Automatic handling of categorical and numerical variables
- **Basic Graphs**: Plotting and saving plotly graphs with explenation 


# Milieudefensie Decision Tree Tools

Python package for creating interactive decision tree visualizations for environmental analysis.

## Quick Start Example
## Beslisboom

```python
from milieudefensie.beslisboom import CreateHTML
from milieudefensie.model_non_linear_y import generate_example_dataset
import time
import numpy as np

# Generate example data
df = generate_example_dataset(n_samples=10000)
df['Interesse'] = np.where(df['y_binary'] == "yes", 1, 0)

# Configure tree parameters
variables_ = ['major_donor_2024', 'age', 'member']  # Variables to include
y = 'Interesse'  # Target variable for splits
split_method = 'gini'  # 'gini' or 'mean' for splitting criteria
min_records = 500  # Minimum records required for a split
max_integer = 5  # Max splits for integer variables
max_nr_splits = 2  # Max splits except for categoricals
min_split_values = 1000  # Minimum records per split
nr_splits = {'age': 4}  # Custom number of splits per variable
splits = {'age': [20,25,40,60]}  # Custom split points
color_reverse = True  # Color scheme (True: red=low, blue=high)
name_all = 'Selectie interesse nalaten'  # Root node name

# Create and visualize the tree
create_html = CreateHTML(
    df=df,
    vars=variables_,
    y=y,
    split_method=split_method,
    min_records=min_records,
    max_integer=max_integer,
    max_nr_splits=max_nr_splits,
    min_split_values=min_split_values,
    nr_splits=nr_splits,
    splits=splits,
    color_reverse=color_reverse,
    name_all=name_all,
    reorder=False  # Keep original variable order
)

# Generate HTML output
create_html.build_HTML(
    output_file='beslisboom_voorbeeld.html',
    title='Interesse Analysis',
    explanation='This tree shows how different donor characteristics affect legacy interest',
    made_by='Milieudefensie Data Team'
)
```

# Milieudefensie Machine Learning Toolkit

## Comprehensive Usage Example

```python
from milieudefensie import generate_example_dataset, ClassificationAnalyzer

### 1. Data Preparation
# Generate example dataset (1000 samples)
df = generate_example_dataset(n_samples=1000)

# Select target variable (binary or multiclass)
y = df['y_binary']  # Binary target
# y = df['y_multiclass']  # Multiclass target

# Prepare features
X = df.drop(columns=['y_binary', 'y_multiclass'])

# Generate larger dataset for predictions (10000 samples)
df_all = generate_example_dataset(n_samples=10000)
df_all['relation_id'] = range(1, len(df_all) + 1)
X_all = df_all.drop(columns=['y_binary', 'y_multiclass', 'relation_id'])

### 2. Model Analysis
# Initialize analyzer
analyzer = ClassificationAnalyzer(y=y, X=X)

# Compare multiple models
results = analyzer.compare_models(test_size=0.2)
print("Model Comparison Results:")
print(results['results'])

# Analyze feature importance
feature_importance = analyzer.analyze_feature_importance(method='auto')
print("\nTop Features:")
print(feature_importance.head(10))

### 3. Prediction Generation
# Generate predictions on training data
train_predictions = analyzer.generate_predictions(
    relation_ids=df['age'],  # Using age as ID
    save_as_csv=False
)

# Generate predictions on new data
new_predictions = analyzer.generate_predictions(
    relation_ids=df_all['age'],
    X_new=X_all,
    save_as_csv=True,
    csv_name='new_predictions.csv'
)

### 4. Probability Analysis
# Basic probability analysis
prob_analysis = analyzer.analyze_probabilities()

# Advanced analysis with new data
prob_analysis_new = analyzer.analyze_probabilities(
    X_data=X_all,
    n_cases=1000,
    analysis_type='highest',  # 'highest', 'lowest', or 'both'
    hover_columns=['age', 'gender_male', 'major_donor_2024'],
    plot_filename='interest_probabilities.html'
)

# Multiclass-specific analysis
if len(analyzer.class_names) > 2:
    prob_analysis_custom = analyzer.analyze_probabilities(
        target_class='Interested',  # Specify class to analyze
        n_cases=100,
        analysis_type='highest',
        hover_columns=['age', 'gender_male', 'major_donor_2024'],
        plot_filename='class_probabilities.html'
    )
```

## Basic graphs
```python

from grafieken import create_uitstroom_linegraph, create_double_axis_barchart
import numpy as np
import pandas as pd

# Example data
np.random.seed(42)
maanden = ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Dec']
data = {'Maanden': maanden}
for i in range(1, 21):
    basis = np.linspace(0.1, 0.5, 12)
    variatie = np.random.normal(0, 0.03, 12)
    data[f'Kanaal {i}'] = np.clip(basis + variatie, 0, 0.6)
df_test = pd.DataFrame(data)

# Grafiek uitstroom maken en opslaan
fig = create_uitstroom_linegraph(
    df=df_test,
    title="Uitstroom per kanaal",
    x_var="Maanden",
    x_title="Maanden",
    explanation_text="Hier zien we de uitstroompercentages per instroomkanaal. De data komt uit ons DWH en gaat terug tot 1990.",
    save_file=True,
    file_name="uitstroom_rapport",
    file_location="rapporten"
)
fig.show()


# Example data
ages = np.arange(18, 91)
clv = np.round(np.linspace(100, 2000, len(ages)) * np.random.uniform(0.9, 1.1, len(ages)))
donations = np.round(np.linspace(10, 500, len(ages)) * np.random.uniform(0.8, 1.2, len(ages)))

# Create DataFrame
df = pd.DataFrame({
    "Age": ages,
    "CLV": clv,
    "Donations": donations
})

# Grafiek leeftijden maken en opslaan
fig = create_double_axis_barchart(
    df=df,
    title="Customer Value & Donations by Age",
    x_var="Age",
    x_title="Age",
    primary_vars=["CLV"],
    primary_title="Customer Lifetime Value (€)",
    secondary_vars=["Donations"],
    secondary_title="Donations (€)",
    explanation_text="CLV and donations generally increase with age.",
    save_file=True,
    file_name="clv_donations_by_age.html"
)
fig.show()

```

## Installation

```bash
pip install milieudefensie