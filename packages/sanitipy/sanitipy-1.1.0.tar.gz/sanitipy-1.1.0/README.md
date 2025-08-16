# SanitiPy - Automatic Data Cleaner
<!-- Badges go here -->
![PyPI - Version](https://img.shields.io/pypi/v/sanitipy?style=for-the-badge)
![PyPI status](https://img.shields.io/pypi/status/sanitipy?style=for-the-badge)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/sanitipy?style=for-the-badge)
![PyPI - License](https://img.shields.io/pypi/l/sanitipy?style=for-the-badge)

**SanitiPy automates the data cleaning process for your data science projects using Python.**

## Overview
SanitiPy is a user-friendly Python library designed to streamline the data cleaning and preprocessing workflow. It provides essential utilities to prepare datasets for analysis or modeling by handling common data quality issues such as duplicate entries, missing values, and inconsistent data types.

## Features
- **Remove Duplicates:** Easily eliminate duplicate rows from your DataFrame to ensure data integrity.

- **Handle Missing Values:** Automatically identify and remove rows containing `NaN` (Not a Number) values.

- **Infer Data Types:** Intelligently detect and convert column data types, including:
  - Converting potential datetime columns based on a configurable ratio of valid dates.
  
  - Converting numeric-like values to proper numeric types.
  
  - Falling back to string type when type inference is unsuccessful.

- **Automated Cleaning Process:** The `DataCleaner` class orchestrates the cleaning steps, ensuring your data is ready for further analysis.

## Installation
You can install SanitiPy using pip:

```zsh
pip install sanitipy
```

## Useage
Quick example on using the package with a Pandas DataFrame:

```python
import pandas as pd
from sanitipy import DataCleaner

# Create a sample DataFrame with some common data issues
data = {
  'ID': [1, 2, 3, 1, 4, 5],
  'Name': ['Alice', 'Bob', 'Charlie', 'Alice', 'David', 'Eve'],
  'Value': [100, 200, None, 100, 400, 500],
  'Date': ['2023/01/01', '2023/01/02', '2023/01/03', '2023/01/01', 'invalid-date', '2023/01/05'],
  'Category': ['A', 'B', 'C', 'A', 'D', 'E']
}
df = pd.DataFrame(data)

# Initialize the DataCleaner
cleaner = DataCleaner(df)

# Clean the data
cleaned_df = cleaner.clean_data()
```

## API Reference
### `DataCleaner` Class
The main class for orchestrating the data cleaning process.

- `__init__(self, data_frame: pd.DataFrame)`:
  - Initializes the `DataCleaner` with a pandas DataFrame

- `clean_data(self) -> pd.DataFrame`:
  - Performs a sequence of cleaning operations:
    - Removes duplicate rows.
    
    - Removes rows with missing values (if any are detected). Raises a `ValueError` if missing values persist after removal.

    - Infers and converts data types for columns with inconsistent types.

    - Resets the DataFrame index.
  - Returns the cleaned pandas DataFrame.

### `Preprocessor` Class
Provides individual data transformation and cleaning utilities.

- `remove_duplicates(self, data: pd.DataFrame) -> pd.DataFrame`:
  - Removes duplicate rows from the input DataFrame.

- `remove_na(self, data: pd.DataFrame) -> pd.DataFrame`:
  - Removes rows containing any `NaN` values from the input DataFrame.

- `infer_data_types(self, data_frame: pd.DataFrame, date_time_ratio: float = 0.5) -> pd.DataFrame`:
  - Infers and converts data types for columns.
  - `date_time_ratio`: The threshold (0-1) for treating an object column as datetime. Default is 0.5 (50% valid date values required).

### `Validator` Class
Used internally by `DataCleaner` to check data quality.

- `check_missing_values(self, data: pd.DataFrame) -> int`:
  -  Retuns the total count of missing values in the DataFrame.

- `validate_data_types(self) -> bool`:
  - Checks if all columns in the DataFrame have consistent data types. Returns `True` if all columns have the same data type or if the DataFrame is empty, `False` otherwise.

## Contributing
Constributions are welcome! If you have suggestions for improvements or new features, please open an issue or submit a pull request.

## License
This project is licensed under the GNU License - see the [LICENSE](./LICENSE) file for details.
