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
