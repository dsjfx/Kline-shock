import uvicorn

if __name__ == "__main__":
  # 从 app.main 模块中导入 app 对象，然后启动服务器
  uvicorn.run("kline_shock.main:app", host="0.0.0.0", port=8000, reload=True)