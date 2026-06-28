import pandas as pd
import numpy as np

# 计算均线
def calculate_ma(df: pd.DataFrame, windows=[5, 20, 60]):
    """计算均线"""
    for w in windows:
        df[f'ma{w}'] = df['close'].rolling(window=w).mean()
    return df

# 计算MACD
def calculate_macd(df: pd.DataFrame, fast=12, slow=26, signal=9):
    """计算MACD"""
    exp1 = df['close'].ewm(span=fast, adjust=False).mean()
    exp2 = df['close'].ewm(span=slow, adjust=False).mean()
    df['macd'] = exp1 - exp2
    df['macd_signal'] = df['macd'].ewm(span=signal, adjust=False).mean()
    df['macd_hist'] = df['macd'] - df['macd_signal']
    return df

def calculate_rsi(df: pd.DataFrame, period=14):
    """计算RSI"""
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))
    return df

def calculate_bollinger_bands(df: pd.DataFrame, window=20, std=2):
    """计算布林带"""
    df['boll_mid'] = df['close'].rolling(window=window).mean()
    df['boll_std'] = df['close'].rolling(window=window).std()
    df['boll_upper'] = df['boll_mid'] + std * df['boll_std']
    df['boll_lower'] = df['boll_mid'] - std * df['boll_std']
    return df