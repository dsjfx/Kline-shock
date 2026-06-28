import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
from .factory import DataSourceFactory

# 创建全局数据源实例（使用默认配置）
_data_source = DataSourceFactory.get_source()

def fetch_stock_hist_data(code: str, days: int = 120) -> pd.DataFrame:
  """
  获取历史数据（对外统一接口）
  """
  return _data_source.fetch_hist_data(code, days)

def fetch_stock_name(code: str) -> str:
  """
  获取股票名称（对外统一接口）
  """
  return _data_source.fetch_stock_name(code)

def switch_data_source(source_name: str):
  """
  切换数据源（运行时动态切换）
  Args:
    source_name: 'dfcf' 或 'tx'
  """
  global _data_source
  _data_source = DataSourceFactory.get_source(source_name)
  print(f"✅ 已切换到数据源: {source_name}")


def get_current_source_name() -> str:
  """获取当前使用的数据源名称"""
  return _data_source.get_source_name()