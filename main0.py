from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import akshare as ak
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

app = FastAPI(title="股票分析API", description="简易股票趋势分析工具")

# 解决跨域问题（让你的Vue前端能调用）
app.add_middleware(
  CORSMiddleware,
  allow_origins=["*"],  # 开发环境允许所有，生产环境请替换为具体域名
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

# ==================== 定义返回数据结构 ====================

class StockBasic(BaseModel):
    code: str
    name: str
    price: float
    change_pct: float

class TrendAnalysis(BaseModel):
    direction: str  # 上升趋势 / 下降趋势 / 震荡整理
    ma5: float
    ma20: float
    ma60: float

class Indicators(BaseModel):
    macd: float
    rsi: float
    boll_position: str  # 上轨附近 / 中轨附近 / 下轨附近

class Suggest(BaseModel):
    action: str  # 买入 / 持有 / 观望 / 卖出
    reason: str

class StockAnalysisResponse(BaseModel):
    basic: StockBasic
    trend: TrendAnalysis
    indicators: Indicators
    suggest: Suggest

# ==================== 核心业务函数 ====================

def get_stock_data(code: str, days: int = 120) -> pd.DataFrame:
    """
    获取股票历史数据
    """
    try:
        # 使用 akshare 获取 A 股历史行情
        df = ak.stock_zh_a_hist(
            symbol=code,
            period="daily",
            start_date=(datetime.now() - timedelta(days=days)).strftime("%Y%m%d"),
            end_date=datetime.now().strftime("%Y%m%d"),
            adjust="qfq"  # 前复权
        )
        # 重命名列名，便于处理
        df.rename(columns={
            '日期': 'date',
            '开盘': 'open',
            '收盘': 'close',
            '最高': 'high',
            '最低': 'low',
            '成交量': 'volume',
            '成交额': 'amount',
            '振幅': 'amplitude',
            '涨跌幅': 'pct_change',
            '涨跌额': 'change',
            '换手率': 'turnover'
        }, inplace=True)
        return df
    except Exception as e:
        raise ValueError(f"获取股票数据失败，请检查代码是否正确：{e}")

def calculate_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    计算技术指标：MA5, MA20, MA60, MACD, RSI, 布林带
    """
    # 均线
    df['ma5'] = df['close'].rolling(window=5).mean()
    df['ma20'] = df['close'].rolling(window=20).mean()
    df['ma60'] = df['close'].rolling(window=60).mean()
    
    # MACD
    exp1 = df['close'].ewm(span=12, adjust=False).mean()
    exp2 = df['close'].ewm(span=26, adjust=False).mean()
    df['macd'] = exp1 - exp2
    df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
    df['macd_hist'] = df['macd'] - df['macd_signal']
    
    # RSI (14日)
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))
    
    # 布林带 (20日均线 ± 2倍标准差)
    df['boll_mid'] = df['close'].rolling(window=20).mean()
    df['boll_std'] = df['close'].rolling(window=20).std()
    df['boll_upper'] = df['boll_mid'] + 2 * df['boll_std']
    df['boll_lower'] = df['boll_mid'] - 2 * df['boll_std']
    
    return df

def get_trend_analysis(df: pd.DataFrame) -> dict:
    """
    判断趋势方向
    """
    latest = df.iloc[-1]
    # 判断趋势：MA5 > MA20 > MA60 为上升，反之为下降，交错为震荡
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

def get_indicators(df: pd.DataFrame) -> dict:
    """
    获取当前指标值
    """
    latest = df.iloc[-1]
    
    # 判断布林带位置
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

def generate_suggestion(trend: dict, indicators: dict) -> dict:
    """
    生成买卖建议
    """
    action = "观望"
    reasons = []
    
    # 趋势判断
    if trend['direction'] == "上升趋势":
        reasons.append("均线呈现多头排列，中期趋势向好")
        action = "持有"
    elif trend['direction'] == "下降趋势":
        reasons.append("均线呈空头排列，中期趋势偏弱")
        action = "观望"
    else:
        reasons.append("均线交错，处于震荡格局")
        action = "观望"
    
    # RSI 超买超卖修正
    if indicators['rsi'] > 70:
        reasons.append(f"RSI={indicators['rsi']}，处于超买区间，短期有回调风险")
        if action == "持有":
            action = "逢高减仓"
    elif indicators['rsi'] < 30:
        reasons.append(f"RSI={indicators['rsi']}，处于超卖区间，短期或有反弹")
        if action == "观望":
            action = "关注"
    
    # 布林带位置修正
    if "下轨" in indicators['boll_position']:
        reasons.append("股价触及布林带下轨，存在技术性反弹可能")
        if action == "观望":
            action = "关注"
    elif "上轨" in indicators['boll_position']:
        reasons.append("股价触及布林带上轨，追高风险较大")
        if action == "持有":
            action = "持有观望"
    
    # MACD 动能
    if indicators['macd'] > 0:
        reasons.append("MACD位于零轴上方，多头动能占优")
    else:
        reasons.append("MACD位于零轴下方，空头动能占优")
    
    # 如果没有任何理由，给一个默认
    if not reasons:
        reasons.append("当前指标信号不明确，建议继续观察")
    
    return {
        'action': action,
        'reason': "；".join(reasons)
    }

# ==================== API 接口 ====================

@app.get("/")
def root():
    return {"message": "股票分析API已启动", "docs": "/docs"}

@app.get("/api/stock/analysis", response_model=StockAnalysisResponse)
def stock_analysis(
    code: str = Query(..., description="股票代码，如 000001"),
    days: int = Query(120, description="分析数据天数，默认120天")
):
    """
    获取股票完整分析数据
    """
    # 1. 获取原始数据
    df = get_stock_data(code, days)
    if df.empty:
        return {"error": "未获取到数据"}
    
    # 2. 计算指标
    df = calculate_indicators(df)
    
    # 3. 获取最新行情
    latest = df.iloc[-1]
    
    # 4. 获取股票名称
    try:
        stock_info = ak.stock_individual_info_em(symbol=code)
        name = stock_info[stock_info['item'] == '股票简称']['value'].values[0]
    except:
        name = code  # 如果获取名称失败，直接用代码
    
    # 5. 组装返回数据
    basic = {
        'code': code,
        'name': name,
        'price': round(latest['close'], 2),
        'change_pct': round(latest['pct_change'], 2)
    }
    
    trend = get_trend_analysis(df)
    indicators = get_indicators(df)
    suggest = generate_suggestion(trend, indicators)
    
    return {
        'basic': basic,
        'trend': trend,
        'indicators': indicators,
        'suggest': suggest
    }

@app.get("/api/stock/kline")
def get_kline(
    code: str = Query(..., description="股票代码"),
    days: int = Query(120, description="获取天数")
):
    """
    获取K线数据（供前端ECharts渲染）
    """
    df = get_stock_data(code, days)
    if df.empty:
        return {"error": "未获取到数据"}
    
    df = calculate_indicators(df)
    
    # 只取最后 days 天
    df = df.tail(days)
    
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

# ==================== 启动服务 ====================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)