"""指数计算模块 - 计算BTC vs M7相对强弱指数"""

import pandas as pd
import numpy as np
from typing import Literal


SignalType = Literal[
    "强烈看多BTC", "温和看多BTC", "中性观望", "温和看多M7", "强烈看多M7"
]


class RelativeStrengthCalculator:
    """相对强弱指数计算器"""

    def __init__(self, btc: pd.Series, m7_index: pd.Series):
        """
        初始化计算器

        Args:
            btc: BTC价格序列
            m7_index: M7市值加权指数序列
        """
        self.btc = btc
        self.m7 = m7_index

        # 标准化到基期100
        self.btc_norm = self.btc / self.btc.iloc[0] * 100
        self.m7_norm = self.m7 / self.m7.iloc[0] * 100

    def price_ratio_index(self) -> pd.Series:
        """
        价格比率指数: (BTC标准化 / M7标准化) * 100

        解读:
        - > 100: BTC表现优于M7
        - < 100: BTC表现弱于M7
        - = 100: 两者表现相当
        """
        return (self.btc_norm / self.m7_norm) * 100

    def rolling_momentum(self, window: int) -> pd.Series:
        """
        N期滚动动量差 (百分点)

        计算: BTC N期收益率 - M7 N期收益率

        Args:
            window: 滚动窗口大小

        Returns:
            动量差序列 (百分点)
        """
        btc_ret = self.btc.pct_change(window)
        m7_ret = self.m7.pct_change(window)
        return (btc_ret - m7_ret) * 100

    def zscore_strength(self, window: int = 60) -> pd.Series:
        """
        Z-Score相对强度

        用于识别异常强弱情况:
        - > 2: BTC异常强势
        - < -2: BTC异常弱势
        - -1 ~ 1: 正常范围

        Args:
            window: 计算均值和标准差的滚动窗口

        Returns:
            相对Z-Score序列
        """
        btc_ret = self.btc.pct_change()
        m7_ret = self.m7.pct_change()

        btc_z = (btc_ret - btc_ret.rolling(window).mean()) / btc_ret.rolling(window).std()
        m7_z = (m7_ret - m7_ret.rolling(window).mean()) / m7_ret.rolling(window).std()

        return btc_z - m7_z

    def generate_signal(
        self,
        short_window: int = 7,
        medium_window: int = 30
    ) -> SignalType:
        """
        生成综合交易信号

        规则:
        - 短期+中期动量 > 5%: 强烈看多BTC
        - 短期或中期动量 > 2%: 温和看多BTC
        - 短期+中期动量 < -5%: 强烈看多M7
        - 短期或中期动量 < -2%: 温和看多M7
        - 其他: 中性观望

        Args:
            short_window: 短期动量窗口
            medium_window: 中期动量窗口

        Returns:
            信号字符串
        """
        short_momentum = self.rolling_momentum(short_window).iloc[-1]
        medium_momentum = self.rolling_momentum(medium_window).iloc[-1]

        if np.isnan(short_momentum) or np.isnan(medium_momentum):
            return "中性观望"

        if short_momentum > 5 and medium_momentum > 5:
            return "强烈看多BTC"
        elif short_momentum > 2 or medium_momentum > 2:
            return "温和看多BTC"
        elif short_momentum < -5 and medium_momentum < -5:
            return "强烈看多M7"
        elif short_momentum < -2 or medium_momentum < -2:
            return "温和看多M7"
        else:
            return "中性观望"

    def full_analysis(self) -> pd.DataFrame:
        """
        完整分析结果

        Returns:
            包含所有指标的DataFrame
        """
        return pd.DataFrame({
            'btc_price': self.btc,
            'm7_index': self.m7,
            'btc_normalized': self.btc_norm,
            'm7_normalized': self.m7_norm,
            'price_ratio': self.price_ratio_index(),
            'momentum_7d': self.rolling_momentum(7),
            'momentum_14d': self.rolling_momentum(14),
            'momentum_30d': self.rolling_momentum(30),
            'momentum_90d': self.rolling_momentum(90),
            'zscore': self.zscore_strength(60)
        })

    def get_latest_metrics(self) -> dict:
        """
        获取最新指标

        Returns:
            包含最新指标值的字典
        """
        analysis = self.full_analysis()
        latest = analysis.iloc[-1]

        return {
            'btc_price': latest['btc_price'],
            'm7_index': latest['m7_index'],
            'price_ratio': latest['price_ratio'],
            'momentum_7d': latest['momentum_7d'],
            'momentum_14d': latest['momentum_14d'],
            'momentum_30d': latest['momentum_30d'],
            'momentum_90d': latest['momentum_90d'],
            'zscore': latest['zscore'],
            'signal': self.generate_signal(),
            'btc_change': (self.btc_norm.iloc[-1] / 100 - 1) * 100,
            'm7_change': (self.m7_norm.iloc[-1] / 100 - 1) * 100
        }
