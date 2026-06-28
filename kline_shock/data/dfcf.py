import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
from .base import StockDataSource


class DfcfDataSource(StockDataSource):
  """东方财富数据源"""
  
  def get_source_name(self) -> str:
    return "东方财富"
  
  def fetch_hist_data(self, code: str, days: int = 120) -> pd.DataFrame:
    """
    从东方财富获取历史数据
    """
    print(f"🌐 正在从 {self.get_source_name()} 获取 {code} 数据...")
    
    start_date = (datetime.now() - timedelta(days=days)).strftime("%Y%m%d")
    end_date = datetime.now().strftime("%Y%m%d")
    
    try:
      df = ak.stock_zh_a_hist(
        symbol=code,
        period="daily",
        start_date=start_date,
        end_date=end_date,
        adjust="qfq"  # 前复权
      )
    except Exception as e:
      print(f"东方财富数据源获取失败: {e}")
      raise
    
    if df.empty:
      raise ValueError(f"东方财富：股票 {code} 未获取到数据")
    
    return self._standardize_columns(df)
  
  def fetch_stock_name(self, code: str) -> str:
    """
    获取股票名称（稳定版，和腾讯一致）
    """
    try:
      # 方法1：先尝试 A 股列表接口（最稳定）
      try:
        df_list = ak.stock_info_a_code_name()
        result = df_list[df_list['code'] == code]
        if not result.empty:
          return result['name'].values[0]
      except:
        pass
      
      # 方法2：使用个股信息接口
      info = ak.stock_individual_info_em(symbol=code)
      
      if info is None or info.empty:
        print(f"⚠️ 获取 {code} 名称失败：返回数据为空")
        return code
      
      if 'item' not in info.columns or 'value' not in info.columns:
        print(f"⚠️ 获取 {code} 名称失败：列名不匹配，实际列名: {info.columns.tolist()}")
        return code
      
      name_row = info[info['item'] == '股票简称']
      if not name_row.empty:
        return name_row['value'].values[0]
      else:
        return code
            
    except Exception as e:
      print(f"⚠️ 获取股票名称失败 ({code}): {e}")
      return code
  
  def _standardize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
      """标准化列名"""
      rename_map = {
          '日期': 'date', '开盘': 'open', '收盘': 'close',
          '最高': 'high', '最低': 'low', '成交量': 'volume',
          '成交额': 'amount', '涨跌幅': 'pct_change',
          '涨跌额': 'change', '换手率': 'turnover', '振幅': 'amplitude'
      }
      
      existing_rename = {k: v for k, v in rename_map.items() if k in df.columns}
      df.rename(columns=existing_rename, inplace=True)
      
      # 如果没有涨跌幅，用收盘价计算
      if 'pct_change' not in df.columns:
          df['pct_change'] = df['close'].pct_change() * 100
      
      df['date'] = pd.to_datetime(df['date'])
      return df