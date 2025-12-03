---
title: BTC vs M7 强弱指数
emoji: 📊
colorFrom: orange
colorTo: blue
sdk: streamlit
sdk_version: 1.29.0
app_file: app.py
pinned: false
---

# BTC vs Magnificent 7 相对强弱指数

追踪 BTC 相对于美股七朵金花（AAPL, MSFT, GOOGL, AMZN, NVDA, META, TSLA）的相对强弱，判断资金流向偏好。

## 核心指标

| 指标 | 说明 |
|------|------|
| 价格比率 | >100 BTC强，<100 M7强 |
| 7/30期动量 | BTC收益率 - M7收益率 |
| Z-Score | 识别极端强弱 |

## 数据来源

[Twelve Data](https://twelvedata.com/) - 免费 API，支持美股+加密货币
