from .dfcf import DfcfDataSource
from .tx import TxDataSource
from .base import StockDataSource

class DataSourceFactory:
    """
    数据源工厂：管理数据源的创建和切换
    """
    
    # 支持的数据源列表
    SOURCES = {
      'dfcf': DfcfDataSource,
      'tx': TxDataSource,
    }
    
    # 默认数据源（可以通过环境变量或配置文件修改）
    DEFAULT_SOURCE = 'dfcf'  # 默认使用腾讯，更稳定
    
    @classmethod
    def get_source(cls, name: str = None) -> StockDataSource:
      """
      获取数据源实例
      
      Args:
        name: 数据源名称，可选 'dfcf' 或 'tx'
              如果不传，使用默认数据源
      """
      source_name = name or cls.DEFAULT_SOURCE
      
      if source_name not in cls.SOURCES:
        raise ValueError(f"不支持的数据源: {source_name}，可选: {list(cls.SOURCES.keys())}")
      
      return cls.SOURCES[source_name]()
    
    @classmethod
    def set_default_source(cls, name: str):
      """
      切换默认数据源
      """
      if name not in cls.SOURCES:
        raise ValueError(f"不支持的数据源: {name}，可选: {list(cls.SOURCES.keys())}")
      cls.DEFAULT_SOURCE = name
      print(f"✅ 已切换到数据源: {name}")