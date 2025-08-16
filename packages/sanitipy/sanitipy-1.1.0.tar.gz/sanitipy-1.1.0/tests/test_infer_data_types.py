import unittest
import pandas as pd
from sanitipy.preprocessor import Preprocessor

class TestInferDataTypes(unittest.TestCase):
  def setUp(self) -> None:
    self.preprocessor = Preprocessor()
  
  def test_infer_dates_and_convert_objects(self) -> None:
    data = pd.DataFrame({
      'date_col': ['2021/01/01', '2022/12/31', 'not a date'],
      'numeric_col': [10, 20, 30],
      'string_col': ['apple', 'banana', 'cherry'],
    })
    result = self.preprocessor.infer_data_types(data)

    # Check that 'date_col' was converted to datetime with NaT where applicable
    self.assertTrue(pd.api.types.is_datetime64_any_dtype(result['date_col']))
    self.assertTrue(pd.isna(result['date_col'].iloc[2]))

    # Check that 'numeric_col' was converted to numeric
    self.assertTrue(pd.api.types.is_numeric_dtype(result['numeric_col']))
    self.assertEqual(result['numeric_col'].tolist(), [10, 20, 30])

    # Check that 'string_col' was converted to string dtype
    self.assertEqual(str(result['string_col'].dtype), 'string')
  
  def test_handles_mixed_types_gracefully(self) -> None:
    data = pd.DataFrame({
      'mixed_col': ['1', '2023/05/20', 'text', None]
    })
    result = self.preprocessor.infer_data_types(data)

    # NOTE: Column should be string, because datetime and numeric conversion failed for all values
    self.assertEqual(str(result['mixed_col'].dtype), 'string')
  
  def test_numeric_columns_remain_numeric(self) -> None:
    data = pd.DataFrame({
      'float_col': [1.5, 2.5, 3.0],
      'int_col': [1, 2, 3]
    })
    result = self.preprocessor.infer_data_types(data)

    self.assertTrue(pd.api.types.is_float_dtype(result['float_col']))
    self.assertTrue(pd.api.types.is_integer_dtype(result['int_col']) or pd.api.types.is_numeric_dtype(result['int_col']))

if __name__ == '__main__':
  unittest.main()
