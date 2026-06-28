from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from kline_shock.api.routes import router

app = FastAPI(title="股票分析系统", description="简易股票趋势分析工具")

# 解决跨域问题
app.add_middleware(
  CORSMiddleware,
  allow_origins=["*"],  # 开发环境允许所有，生产环境请替换为具体域名
  allow_methods=["*"],
  allow_headers=["*"],
  allow_credentials=True,
)

# Include an APIRouter
# Read more about it : https://fastapi.tiangolo.com/tutorial/bigger-applications
app.include_router(router)
