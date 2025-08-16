import pandas as pd
from .validator import Validator
from .preprocessor import Preprocessor
from .visualizations import Visualizations

class DataCleaner:
  def __init__(self, data_frame: pd.DataFrame):
    # Create an instance of the Validator
    self.validator = Validator(data_frame)

    # Create an instance of the Preprocessor
    self.preprocessor = Preprocessor()

    # Create an instance of the Visualizer
    self.visualizer = Visualizations(data_frame)

    # Store the data_frame variable
    self.data_frame = data_frame

  def clean_data(self, visualization = False) -> pd.DataFrame:
    missing_values: int = self.validator.check_missing_values(self.data_frame)
    validate_data_types: bool = self.validator.validate_data_types()
    self.data_frame = self.preprocessor.remove_duplicates(self.data_frame)

    if missing_values > 0:
      self.data_frame = self.preprocessor.remove_na(self.data_frame)
      remaining_missing_values: int = self.validator.check_missing_values(self.data_frame)

      if remaining_missing_values != 0:
        raise ValueError(f'Data still contains {remaining_missing_values} missing values. Check the Data Set manually')

    if not validate_data_types:
      self.data_frame = self.preprocessor.infer_data_types(self.data_frame)
    
    if visualization != False:
      self.visualizer.show_missing_values()

    self.data_frame = self.data_frame.reset_index(drop=True)

    return self.data_frame
