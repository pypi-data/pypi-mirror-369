# import unittest
# from unittest.mock import patch, MagicMock
# import pandas as pd
# from sanitipy.sanitipy import DataInfo
# from rich.panel import Panel
# from rich.console import Console

# class TestDataInfo(unittest.TestCase):
#   @patch('rich.console.Console')
#   def test_show_info(self, mock_console_class):
#     mock_console = MagicMock()
#     mock_console_class.return_value = mock_console

#     # Create a non-empty dataset
#     not_empty_dataset = pd.DataFrame({
#       'A': [1, 1, 2, 2],
#       'B': [3, 3, 4, 4],
#     })

#     # Call the method
#     data_info = DataInfo()
#     data_info.show_info(not_empty_dataset)

#     # Retrieve the actual panel content
#     printed_panel = mock_console.print.call_args[0][0]
    
#     self.assertIsInstance(printed_panel, Panel)

#     content = str(printed_panel.renderable)

#     self.assertIn('The dataset has 4 rows and 2 columns', content)
#     self.assertIn('The total number of observations is 8', content)
  
#   @patch('rich.console.Console')
#   def test_show_info_with_empty_dataset(self, mock_console_class):
#     mock_console = MagicMock()
#     mock_console_class.return_value = mock_console

#     # Create an empty dataset
#     empty_dataset = pd.DataFrame()

#     # Call the method
#     data_info = DataInfo()
#     data_info.show_info(empty_dataset)

#     # Retrieve the actual panel content
#     printed_panel = mock_console.print.call_args[0][0]
    
#     self.assertIsInstance(printed_panel, Panel)

#     content = str(printed_panel.renderable)

#     self.assertIn('Dataset is empty', content)
  
#   @patch('rich.console.Console')
#   def test_show_info_with_exception(self, mock_console_class):
#     mock_console = MagicMock()
#     mock_console_class.return_value = mock_console

#     # Create a dataset with will cause an exception
#     invalid_dataset = None

#     # Call the method
#     data_info = DataInfo()
#     data_info.show_info(invalid_dataset) # type: ignore

#     # Retrieve the actual panel content
#     printed_panel = mock_console.print.call_args[0][0]
    
#     self.assertIsInstance(printed_panel, Panel)

#     content = str(printed_panel.renderable)

#     self.assertIn('Input must be a pandas DataFrame.', content)
    
# if __name__ == '__main__':
#   unittest.main()
