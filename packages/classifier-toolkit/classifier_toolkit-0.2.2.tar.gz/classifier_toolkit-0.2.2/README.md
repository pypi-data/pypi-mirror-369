[PyPI: classifier-toolkit](https://pypi.org/project/classifier-toolkit/)

```bash
pip install classifier-toolkit
```

# Classifier Toolkit

[![Poetry](https://img.shields.io/endpoint?url=https://python-poetry.org/badge/v0.json)](https://python-poetry.org/)
[![Linting - Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Code style - Black](https://img.shields.io/badge/Code%20Style-Black-000000.svg)](https://github.com/psf/black)

This is a new project.

-----

## Table of Content

<!-- [[_TOC_]] -->

1. [Installation](#installation)
2. [Usage](#usage)
3. [Modules Overview](#modules-overview)
4. [Future Work](#future-work)

### Installation

This library is published in the PyPI directory. To install, users can run pip install 'classifier_toolkit' command.

### Usage

This library automates binary classification tasks in the finance domain, specifically for default and fraud labeling. It includes several packages designed to address the main steps in any machine learning/data science task:

1. EDA: which is accessible by EDA_Toolkit. This package provides the EDA and feature engineering functionality alongside with all the necessary visualizations.
2. Feature Selection: To be implemented.
3. Model fitting and hyperparameter tuning: To be implemented.
4. Evaluation and reporting: To be implemented.

In the future, the package architectures will be included here. However, for now please consult the docstrings in the specific methods in the relevant modules.

**Note**: that this library does not contain data wrangling steps (although it contains feature engineering), it's an intermediate step between EDA and feature engineering where users should fix any data quality related issues. Therefore, conducting the EDA is crucial to mitigate any issues before moving onto the feature engineering and the subsequent steps.

### Modules Overview

- **EDA Toolkit**: This module includes classes and methods for performing comprehensive exploratory data analysis. It provides automated warnings for data quality issues, univariate and bivariate analysis, and various data visualizations to help understand the dataset.

- **Univariate Analysis**: This class focuses on the analysis of individual variables. It includes methods for calculating statistical measures, visualizing distributions, and assessing relationships between variables and a target through techniques like Cramer's V and Information Value. This helps in understanding the significance and distribution of each feature independently.

- **Bivariate Analysis**: This class deals with the analysis of two variables to understand their relationship. It includes functionalities for generating correlation heatmaps, performing ANOVA tests between numerical and categorical variables, and computing pairwise Cramer's V for categorical features. This aids in identifying patterns and correlations between pairs of variables, which is crucial for feature selection and engineering.

- **Feature Engineering**: This module assists in transforming features, handling missing values, encoding categorical variables, and more. It aims to enhance the dataset's quality for better model performance.

- **Visualizations**: This module offers a wide range of plotting capabilities to visually analyze data distributions, relationships, and other crucial aspects of the dataset.

- **Automated Warnings**: A utility to automatically check the dataset for common issues such as missing or duplicate values, outliers, and more, providing warnings to guide data cleaning efforts.

- **Feature Selection**: This module provides various feature selection techniques:
  - **Embedded Methods**: Includes ElasticNet for regularization-based feature selection.
  - **Wrapper Methods**: 
    - Recursive Feature Elimination (RFE) with support for various ensemble methods (Random Forest, XGBoost, LightGBM, CatBoost).
    - Sequential Feature Selection (forward, backward, floating, and bidirectional).
  - **Meta Selector**: Combines multiple feature selection methods to provide a robust selection.
  - **Utility Functions**: Includes scoring functions and plotting utilities for feature importance visualization.

### Future Work
The next planned improvements and additions to the library include:
* Adding model fitting and hyperparameter tuning functionalities.
* Developing comprehensive evaluation and reporting tools to assist with model assessment.
* Expanding documentation to include architecture diagrams and detailed usage examples.