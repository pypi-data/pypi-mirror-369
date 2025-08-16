import unittest
import pandas as pd
from sanitipy.preprocessor import Preprocessor

class TestRemoveNa(unittest.TestCase):
  def setUp(self) -> None:
    self.data = pd.DataFrame({
      'A': [1, 2, None, 4],
      'B': [5, None, 7, 8]
    })
    self.preprocessor = Preprocessor()
  
  def test_remove_na_removes_rows_with_nan(self):
    """
    Test that remove_na() removes any row that contains at least one NaN value.

    The original DataFrame contains the following rows:

        A     B
    0  1.0   5.0     <- valid row (no NaN)
    1  2.0   NaN     <- invalid row (NaN in column B)
    2  NaN   7.0     <- invalid row (NaN in column A)
    3  4.0   8.0

    The remove_na() method drops any row with at least one NaN value.
    Therefore, only rows 0 and 3 remain.
    
        A     B
    0  1.0   5.0
    1  4.0   8.0
    """
    cleaned_data = self.preprocessor.remove_na(self.data)
    expected_data = pd.DataFrame({
      'A': [1.0, 4.0],
      'B': [5.0, 8.0]
    })

    pd.testing.assert_frame_equal(cleaned_data.reset_index(drop=True), expected_data)

if __name__ == '__main__':
  unittest.main()
