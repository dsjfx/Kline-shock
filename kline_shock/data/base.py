from abc import ABC, abstractmethod
import pandas as pd

class StockDataSource(ABC):
  """
  数据源基类（定义统一接口）
  """
  
  @abstractmethod
  def fetch_hist_data(self, code: str, days: int = 120) -> pd.DataFrame:
    """
    获取历史K线数据
    """
    pass
  
  @abstractmethod
  def fetch_stock_name(self, code: str) -> str:
    """
    获取股票名称
    """
    pass
  
  @abstractmethod
  def get_source_name(self) -> str:
    """
    获取数据源名称（用于日志）
    """
    pass