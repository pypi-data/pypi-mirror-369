import pandas as pd
import matplotlib.pyplot as plt
import missingno as msno
from .validator import Validator

class Visualizations(Validator):
  def __init__(self, data: pd.DataFrame) -> None:
    super().__init__(data)

  def show_missing_values(self) -> None:
    data_frame = self.data
    
    plt.title('Missing Values in Dataset')
    plt.xlabel('Column Names')
    plt.ylabel('Total Observations')
    msno.bar(data_frame)
    plt.show()
