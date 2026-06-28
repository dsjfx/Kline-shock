import pandas as pd
from ..utils.indicators import calculate_ma, calculate_macd, calculate_rsi, calculate_bollinger_bands

def compute_all_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """批量计算所有指标"""
    df = calculate_ma(df)
    df = calculate_macd(df)
    df = calculate_rsi(df)
    df = calculate_bollinger_bands(df)
    return df

def analyze_trend(df: pd.DataFrame) -> dict:
    """趋势分析"""
    latest = df.iloc[-1]
    if latest['ma5'] > latest['ma20'] > latest['ma60']:
        direction = "上升趋势"
    elif latest['ma5'] < latest['ma20'] < latest['ma60']:
        direction = "下降趋势"
    else:
        direction = "震荡整理"
    
    return {
        'direction': direction,
        'ma5': round(latest['ma5'], 2),
        'ma20': round(latest['ma20'], 2),
        'ma60': round(latest['ma60'], 2)
    }

def get_current_indicators(df: pd.DataFrame) -> dict:
    """获取当前指标"""
    latest = df.iloc[-1]
    
    if latest['close'] >= latest['boll_upper']:
        boll_pos = "上轨附近（超买区域）"
    elif latest['close'] <= latest['boll_lower']:
        boll_pos = "下轨附近（超卖区域）"
    else:
        boll_pos = "中轨附近（合理区间）"
    
    return {
        'macd': round(latest['macd'], 4),
        'rsi': round(latest['rsi'], 2),
        'boll_position': boll_pos
    }