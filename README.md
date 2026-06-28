# Kline-shock
A software for analyzing the K-line trend of stocks

Kline-shock/                  # 项目根目录
│
├── app/                      # 核心代码目录
│   ├── __init__.py
│   ├── main.py               # 程序入口（只负责启动服务）
│   │
│   ├── api/                  # 控制器层（接收HTTP请求）
│   │   ├── __init__.py
│   │   └── routes.py         # 路由定义（/api/stock/analysis 等）
│   │
│   ├── service/              # 业务逻辑层（核心分析逻辑）
│   │   ├── __init__.py
│   │   ├── analysis_service.py   # 趋势分析、指标计算
│   │   └── suggest_service.py    # 买卖建议生成
│   │
│   ├── data/                 # 数据访问层（获取原始数据）
│   │   ├── __init__.py
│   │   ├── stock_data_source.py  # 从AkShare获取数据
│   │   └── cache.py              # 缓存管理（避免重复拉取）
│   │
│   ├── models/               # 数据模型层（定义数据结构）
│   │   ├── __init__.py
│   │   └── schemas.py        # Pydantic模型（请求/响应格式）
│   │
│   └── utils/                # 工具函数层
│       ├── __init__.py
│       └── indicators.py     # 技术指标计算公式（MACD、RSI等）
│
├── config/                   # 配置文件
│   ├── __init__.py
│   └── settings.py           # 数据库连接、API密钥等配置
│
├── tests/                    # 单元测试
│   ├── __init__.py
│   └── test_analysis.py
│
├── requirements.txt          # 依赖清单
└── README.md                 # 项目说明
