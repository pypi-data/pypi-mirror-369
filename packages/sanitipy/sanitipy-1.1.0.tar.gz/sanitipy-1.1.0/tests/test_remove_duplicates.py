import unittest
import pandas as pd
from sanitipy.preprocessor import Preprocessor

class TestRemoveDuplicates(unittest.TestCase):
  def setUp(self) -> None:
    self.data = pd.DataFrame({
      'A': [1, 1, 2, 2],
      'B': [3, 3, 4, 4]
    })
    self.preprocessor = Preprocessor()

  def test_remove_duplicates_removes_duplicate_rows(self):
    # Call the remove_duplicates() method from the Preprocessor class
    cleaned_data = self.preprocessor.remove_duplicates(self.data)

    # Check the length of the cleaned DataFrame
    self.assertEqual(len(cleaned_data), 2)

    # Check the contents of the cleaned DataFrame
    expected_data = pd.DataFrame({
      'A': [1, 2],
      'B': [3, 4]
    })

    pd.testing.assert_frame_equal(cleaned_data.reset_index(drop=True), expected_data)

if __name__ == '__main__':
  unittest.main()
