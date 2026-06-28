import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
from .base import StockDataSource


class TxDataSource(StockDataSource):
  """
  腾讯数据源
  """
  
  def get_source_name(self) -> str:
    return "腾讯财经"
  
  def fetch_hist_data(self, code: str, days: int = 120) -> pd.DataFrame:
    """
    从腾讯财经获取历史数据
    """
    print(f"🌐 正在从 {self.get_source_name()} 获取 {code} 数据...")
    
    # 腾讯接口需要加前缀
    if code.startswith('6'):
      symbol = f"sh{code}"
    elif code.startswith('0') or code.startswith('3'):
      symbol = f"sz{code}"
    else:
      symbol = code
    
    start_date = (datetime.now() - timedelta(days=days)).strftime("%Y%m%d")
    end_date = datetime.now().strftime("%Y%m%d")
    
    try:
      df = ak.stock_zh_a_hist_tx(
        symbol=symbol,
        start_date=start_date,
        end_date=end_date
      )
    except Exception as e:
      print(f"腾讯数据源获取失败: {e}")
      raise
    
    if df.empty:
      raise ValueError(f"腾讯财经：股票 {code} 未获取到数据")
    
    return self._standardize_columns(df)
  
  def fetch_stock_name(self, code: str) -> str:
    """
    获取股票名称（稳定版）
    """
    try:
      # 方法1：尝试使用 A 股列表接口（更稳定）
      try:
        df_list = ak.stock_info_a_code_name()
        result = df_list[df_list['code'] == code]
        if not result.empty:
          return result['name'].values[0]
      except:
        pass
      
      # 方法2：如果上面的方法失败，尝试原来的接口
      info = ak.stock_individual_info_em(symbol=code)
      
      if info is None or info.empty:
        print(f"⚠️ 获取 {code} 名称失败：返回数据为空")
        return code
      
      if 'item' not in info.columns or 'value' not in info.columns:
        print(f"⚠️ 获取 {code} 名称失败：列名不匹配")
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
        '涨跌幅': 'pct_change'
      }
      
      existing_rename = {k: v for k, v in rename_map.items() if k in df.columns}
      df.rename(columns=existing_rename, inplace=True)
      
      if 'pct_change' not in df.columns:
        df['pct_change'] = df['close'].pct_change() * 100
      
      df['date'] = pd.to_datetime(df['date'])
      return df