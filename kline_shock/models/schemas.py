from pydantic import BaseModel

class StockBasic(BaseModel):
  code: str
  name: str
  price: float
  change_pct: float

# 股票基础数据结构
class TrendAnalysis(BaseModel):
  direction: str      # 上升趋势 / 下降趋势 / 震荡整理
  ma5: float
  ma20: float
  ma60: float

class Indicators(BaseModel):
  macd: float
  rsi: float
  boll_position: str  # 上轨附近 / 中轨附近 / 下轨附近

class Suggest(BaseModel):
  action: str         # 买入 / 持有 / 观望 / 卖出
  reason: str

# 股票分析响应数据
class StockAnalysisResponse(BaseModel):
  basic: StockBasic
  trend: TrendAnalysis
  indicators: Indicators
  suggest: Suggest