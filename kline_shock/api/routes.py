from fastapi import APIRouter, Query, HTTPException
import pandas as pd
from ..models.schemas import StockAnalysisResponse
from ..data.stock_data_source import fetch_stock_hist_data, fetch_stock_name
from ..service.analysis_service import compute_all_indicators, analyze_trend, get_current_indicators
from ..service.suggest_service import generate_suggestion

router = APIRouter()

# 分析结论（趋势、指标、建议）
@router.get("/api/stock/analysis", response_model=StockAnalysisResponse)
def stock_analysis(
  code: str = Query(..., description="股票代码"),
  days: int = Query(120, description="分析天数")
):
    # 1. 拿数据
    df = fetch_stock_hist_data(code, days)
    
    # 2. 算指标
    df = compute_all_indicators(df)
    
    # 3. 业务分析
    basic = {
        'code': code,
        'name': fetch_stock_name(code),
        'price': round(df.iloc[-1]['close'], 2),
        'change_pct': round(df.iloc[-1]['pct_change'], 2)
    }
    trend = analyze_trend(df)
    indicators = get_current_indicators(df)
    suggest = generate_suggestion(trend, indicators)
    
    return {'basic': basic, 'trend': trend, 'indicators': indicators, 'suggest': suggest}

# K 线原始数据（含均线）
@router.get("/api/stock/kline")
def get_kline(
    code: str = Query(..., description="股票代码"),
    days: int = Query(120, description="获取天数")
):
  """
  获取K线数据（供前端ECharts渲染）
  """
  try:
    df = fetch_stock_hist_data(code, days)
      
    if df.empty:
      raise HTTPException(status_code=404, detail=f"未获取到股票 {code} 的数据")
      
    df = compute_all_indicators(df)
    
    # 转为前端需要的格式
    result = []
    for _, row in df.iterrows():
      result.append({
        'date': row['date'].strftime('%Y-%m-%d'),
        'open': round(row['open'], 2),
        'high': round(row['high'], 2),
        'low': round(row['low'], 2),
        'close': round(row['close'], 2),
        'volume': int(row['volume']),
        'ma5': round(row['ma5'], 2) if pd.notna(row['ma5']) else None,
        'ma20': round(row['ma20'], 2) if pd.notna(row['ma20']) else None,
        'ma60': round(row['ma60'], 2) if pd.notna(row['ma60']) else None
      })
    
    return {"data": result}
      
  except Exception as e:
    print(f"获取K线数据失败: {e}")
    raise HTTPException(status_code=500, detail=str(e))