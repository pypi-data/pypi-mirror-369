import pandas as pd
# from sklearn.preprocessing import StandardScaler

class Preprocessor:
  """
  Preprocessor Class for Data Transformation and Cleaning
  
  This module defines the `Preprocessor` class, which provides essential preprocessing ultilities for datasets
  stored as pandas DataFrames. It focuses on preparing data for analysis or modeling by removing duplicates,
  handling missing values, and inferring apprpriate data types.

  Key Features:
  -------------
  - Remove Duplicates (`remove_duplicates`):
    Eliminates duplicate rows to ensure data integrity.
  
  - Remove Missing Values (`remove_na`):
    Drops any rows containing NaN values.
  
  - Infer Data Types (`infer_data_types`):
    Attempts to automatically detect and convert column data types
      - Converts potential datetime columns if a sufficient ratio of valid dates is detected (controlled by `date_time_ratio`).
      - Converts numeric-like values to proper numeric types.
      - Falls back to string type when type inference fails.
  
  Notes:
  ------
  - The `date_time_ratio` parameter in `infer_data_types` controls the threshold for treating an object column as a datetime column.
  Default is 0.5 (50% valid date values required).
  
  - Future enhancements may include normaltization, categorical encoding, and column exclusion options.

  Dependencies:
  -------------
  - pandas (pd)
  """
  def remove_duplicates(self, data: pd.DataFrame) -> pd.DataFrame:
    """
    Remove duplicate rows from the DataFrame.

    Parameters:
    -----------
    data: pd.DataFrame
    - The DataFrame to process

    Returns:
    --------
    pd.DataFrame
    - A DataFrame with duplicate rows removed.
    """
    return data.drop_duplicates()
  
  def remove_na(self, data: pd.DataFrame) -> pd.DataFrame:
    """
    Remove rows containing any NaN values.

    Parameters:
    -----------
    data: pd.DataFrame
    - The DataFrame to process

    Returns:
    --------
    pd.DataFrame
    - A DataFrame with rows containing NaN values removed.
    """
    return data.dropna()
  
  def infer_data_types(self, data_frame: pd.DataFrame, date_time_ratio: float = 0.5) -> pd.DataFrame:
    """
    Infer and convert data types of the DataFrame columns.
    
    This method attempts to automatically assign the most approopriate data type to each column:
      - Converts object columns to dattime if the proportion of valid dates meets or exceeds `date_time_ratio`.
      - Converts numeric-like values to numeric types.
      - Defaults to string type when type inference is unsuccessful.
    
    Parameters:
    -----------
    data_frame: pd.DataFrame
    - The DataFrame to process.

    date_time_ratio: float, optional, default = 0.5
    - The threshold (0-1) for treating an object column as datetime.
    For example, 0.5 means at least 50% of values must be valid
    dates to convert.

    Returns:
    --------
    pd.DataFrame
    - A DataFrame with inferred and converted data types.
    """
    for col in data_frame.columns:
      # Check for datetime columns
      if data_frame[col].dtype == 'object':
        date_time_column = pd.to_datetime(data_frame[col], format="%Y/%m/%d", errors='coerce')

        # If at least 80% of the values are valid dates, keep datetime
        valid_ratio = date_time_column.notna().mean()

        if valid_ratio >= date_time_ratio:
          data_frame[col] = date_time_column
        else:
          data_frame[col] = data_frame[col].astype('string')
      
      # Convert to appropriate types
      if data_frame[col].dtype == 'object':
        data_frame[col] = data_frame[col].astype('string')
      elif data_frame[col].dtype in ['float64', 'int64']:
        data_frame[col] = pd.to_numeric(data_frame[col], errors='coerce')
    
    return data_frame
  
  # def normalize_data(self):
  #   """Normalize numeric columns in the DataFrame using StandardScaler"""
  #   # Select only numeric columns for normalization
  #   numeric_data = self.data.select_dtypes(include=['float64', 'int64'])
  #   scaler = StandardScaler()
  #   normalized_data = pd.DataFrame(scaler.fit_transform(numeric_data), columns=numeric_data.columns)

  #   # Repalce the numeric columns in the originial DataFrame with the normalized one
  #   self.data[numeric_data.columns] = normalized_data
  #   self.data = pd.concat([self.data.drop(columns=numeric_data.columns), normalized_data], axis=1)

  #   return self.data
