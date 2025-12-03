# BTC vs Magnificent 7 相对强弱指数

追踪 BTC 相对于美股七朵金花（AAPL, MSFT, GOOGL, AMZN, NVDA, META, TSLA）的相对强弱，判断资金流向偏好。

## 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 2. 配置 API Key
```bash
cp .env.example .env
# 编辑 .env，填入你的 Twelve Data API Key
# 获取地址: https://twelvedata.com/pricing (免费)
```

### 3. 启动
```bash
streamlit run app.py
```

## 服务器部署

```bash
# 后台运行，监听所有 IP
nohup streamlit run app.py --server.port 8501 --server.address 0.0.0.0 > app.log 2>&1 &
```

## 核心指标

| 指标 | 说明 |
|------|------|
| 价格比率 | >100 BTC强，<100 M7强 |
| 7/30期动量 | BTC收益率 - M7收益率 |
| Z-Score | 识别极端强弱 |

## 数据来源

[Twelve Data](https://twelvedata.com/) - 免费 API，支持美股+加密货币
