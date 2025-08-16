import pandas as pd

class Validator:
  def __init__(self, data: pd.DataFrame) -> None:
    self.data = data
    self.empty = self.check_missing_values(data) > 0

  def validate_data_types(self) -> bool:
    # Check for consistent data types
    if self.empty:
      return True
    
    data_types = self.data.dtypes

    if data_types.nunique() == 1:
      return True
    else:
      return False
    
  def check_missing_values(self, data: pd.DataFrame) -> int:
    if data is None:
      return 0

    # Identify missing values in the dataset
    return data.isnull().sum().sum()
