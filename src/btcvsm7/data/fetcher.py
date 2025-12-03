"""数据获取模块 - 使用 Twelve Data API 获取 BTC 和 M7 数据"""

import os
import pandas as pd
from typing import Literal
from twelvedata import TDClient

# Magnificent 7 股票代码
M7_SYMBOLS = ("AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA")
M7_NAMES = {
    "AAPL": "Apple",
    "MSFT": "Microsoft",
    "GOOGL": "Google",
    "AMZN": "Amazon",
    "NVDA": "NVIDIA",
    "META": "Meta",
    "TSLA": "Tesla"
}

# 默认市值（2024年12月近似值，单位：万亿美元）
DEFAULT_MARKET_CAPS = {
    "AAPL": 3.7,
    "MSFT": 3.1,
    "GOOGL": 2.3,
    "AMZN": 2.3,
    "NVDA": 3.4,
    "META": 1.5,
    "TSLA": 1.3
}

TimeFrame = Literal["daily", "weekly", "monthly"]


class DataFetcher:
    """数据获取器 - 使用 Twelve Data API"""

    def __init__(self, api_key: str = None):
        """
        初始化数据获取器

        Args:
            api_key: Twelve Data API Key，也可通过环境变量 TWELVE_DATA_API_KEY 设置
        """
        self.api_key = api_key or os.environ.get("TWELVE_DATA_API_KEY")
        if not self.api_key:
            raise ValueError(
                "需要 Twelve Data API Key！\n"
                "1. 访问 https://twelvedata.com/pricing 注册免费账号\n"
                "2. 设置环境变量: export TWELVE_DATA_API_KEY=你的key\n"
                "   或在项目目录创建 .env 文件"
            )
        self.client = TDClient(apikey=self.api_key)
        self.m7_symbols = list(M7_SYMBOLS)

    def fetch_all(
        self,
        period: str = "1y",
        timeframe: TimeFrame = "daily"
    ) -> dict:
        """
        获取所有数据

        Args:
            period: 数据周期 (3mo, 6mo, 1y, 2y, 5y)
            timeframe: 时间粒度 (daily, weekly, monthly)

        Returns:
            dict: 包含 btc, m7_index, m7_stocks, market_caps, weights 的字典
        """
        # 转换 period 到 outputsize
        period_to_size = {
            "1mo": 22, "3mo": 66, "6mo": 130,
            "1y": 252, "2y": 504, "5y": 1260
        }
        outputsize = period_to_size.get(period, 252)

        # 转换 timeframe 到 interval
        interval_map = {
            "daily": "1day",
            "weekly": "1week",
            "monthly": "1month"
        }
        interval = interval_map[timeframe]

        # 获取 BTC 数据
        btc_ts = self.client.time_series(
            symbol="BTC/USD",
            interval=interval,
            outputsize=outputsize
        )
        btc_df = btc_ts.as_pandas()
        btc = btc_df['close'].sort_index()
        btc.name = 'BTC-USD'

        # 获取 M7 股票数据
        m7_data = {}
        for symbol in self.m7_symbols:
            ts = self.client.time_series(
                symbol=symbol,
                interval=interval,
                outputsize=outputsize
            )
            df = ts.as_pandas()
            m7_data[symbol] = df['close'].sort_index()

        m7_stocks = pd.DataFrame(m7_data)

        # 对齐日期索引（取交集）
        common_idx = btc.index.intersection(m7_stocks.index)
        btc = btc.loc[common_idx]
        m7_stocks = m7_stocks.loc[common_idx]

        # 获取市值和权重
        market_caps = self._get_market_caps()
        weights = market_caps / market_caps.sum()

        # 计算市值加权 M7 指数
        m7_returns = m7_stocks.pct_change()
        weighted_returns = (m7_returns * weights).sum(axis=1)
        m7_index = (1 + weighted_returns).cumprod() * 100
        m7_index.iloc[0] = 100

        return {
            'btc': btc,
            'm7_index': m7_index,
            'm7_stocks': m7_stocks,
            'market_caps': market_caps,
            'weights': weights
        }

    def _get_market_caps(self) -> pd.Series:
        """获取 M7 市值（使用默认值，避免额外 API 调用）"""
        # Twelve Data 免费版 API 调用有限，使用预设市值
        caps = {s: v * 1e12 for s, v in DEFAULT_MARKET_CAPS.items()}
        return pd.Series(caps)

    def get_quote(self, symbol: str) -> dict:
        """获取实时报价"""
        return self.client.quote(symbol=symbol).as_json()
