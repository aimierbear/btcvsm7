"""
BTC vs Magnificent 7 相对强弱指数 Dashboard

启动方式: streamlit run app.py
"""

import streamlit as st
import pandas as pd
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

# 添加src目录到路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from btcvsm7.data import DataFetcher, M7_SYMBOLS
from btcvsm7.data.fetcher import M7_NAMES
from btcvsm7.index import RelativeStrengthCalculator
from btcvsm7.visualization import ChartGenerator

# 页面配置
st.set_page_config(
    page_title="BTC vs M7 强弱指数",
    page_icon="📊",
    layout="wide"
)

# 信号颜色映射
SIGNAL_COLORS = {
    "强烈看多BTC": "🟢🟢",
    "温和看多BTC": "🟢",
    "中性观望": "⚪",
    "温和看多M7": "🔴",
    "强烈看多M7": "🔴🔴"
}


@st.cache_data(ttl=3600)  # 缓存1小时
def load_data(period: str, timeframe: str):
    """加载并缓存数据"""
    fetcher = DataFetcher()
    return fetcher.fetch_all(period=period, timeframe=timeframe)


def main():
    # 标题
    st.title("📊 BTC vs Magnificent 7 相对强弱指数")
    st.markdown("追踪 BTC 相对于美股七朵金花的相对强弱，判断资金流向偏好")

    # 侧边栏设置
    with st.sidebar:
        st.header("⚙️ 设置")

        # 时间粒度选择
        timeframe = st.radio(
            "时间粒度",
            options=["daily", "weekly", "monthly"],
            format_func=lambda x: {"daily": "日线", "weekly": "周线", "monthly": "月线"}[x],
            index=0
        )

        # 数据范围选择
        period = st.selectbox(
            "数据范围",
            options=["3mo", "6mo", "1y", "2y", "5y"],
            format_func=lambda x: {
                "3mo": "3个月", "6mo": "6个月", "1y": "1年", "2y": "2年", "5y": "5年"
            }[x],
            index=2
        )

        # 刷新按钮
        if st.button("🔄 刷新数据"):
            st.cache_data.clear()
            st.rerun()

        st.markdown("---")

    # 检查 API Key
    if not os.environ.get("TWELVE_DATA_API_KEY"):
        st.error("❌ 未设置 Twelve Data API Key")
        st.markdown("""
        **设置步骤：**
        1. 访问 [Twelve Data](https://twelvedata.com/pricing) 注册免费账号
        2. 在项目目录创建 `.env` 文件，内容：
        ```
        TWELVE_DATA_API_KEY=你的API密钥
        ```
        3. 重启 Dashboard
        """)
        return

    # 加载数据
    with st.spinner("正在加载数据..."):
        try:
            data = load_data(period, timeframe)
        except Exception as e:
            st.error(f"数据加载失败: {e}")
            st.info("请检查 API Key 是否正确，或稍后重试")
            return

    # 计算指标
    calculator = RelativeStrengthCalculator(data['btc'], data['m7_index'])
    analysis = calculator.full_analysis()
    metrics = calculator.get_latest_metrics()

    # 侧边栏指标卡片
    with st.sidebar:
        st.header("📈 当前指标")

        # 价格比率
        ratio = metrics['price_ratio']
        ratio_delta = ratio - 100
        st.metric(
            "价格比率",
            f"{ratio:.1f}",
            delta=f"{ratio_delta:+.1f}",
            delta_color="normal" if ratio_delta >= 0 else "inverse"
        )

        # 动量指标
        col1, col2 = st.columns(2)
        with col1:
            m7d = metrics['momentum_7d']
            st.metric("7期动量", f"{m7d:+.1f}%")
        with col2:
            m30d = metrics['momentum_30d']
            st.metric("30期动量", f"{m30d:+.1f}%")

        st.markdown("---")

        # 综合信号
        signal = metrics['signal']
        signal_icon = SIGNAL_COLORS.get(signal, "⚪")
        st.markdown(f"### {signal_icon} {signal}")

        st.markdown("---")

        # 区间涨跌幅
        st.header("📊 区间涨跌")
        col1, col2 = st.columns(2)
        with col1:
            btc_change = metrics['btc_change']
            st.metric("BTC", f"{btc_change:+.1f}%")
        with col2:
            m7_change = metrics['m7_change']
            st.metric("M7指数", f"{m7_change:+.1f}%")

    # 主面板
    charts = ChartGenerator(analysis)

    # 图表区域
    tab1, tab2, tab3 = st.tabs(["📊 综合分析", "📈 详细指标", "🏢 M7成分股"])

    with tab1:
        # 标准化价格对比
        st.plotly_chart(charts.price_comparison_chart(), use_container_width=True)

        # 两列布局
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(charts.price_ratio_chart(), use_container_width=True, key="ratio_chart")
        with col2:
            st.plotly_chart(charts.weights_pie_chart(data['weights']), use_container_width=True, key="weights_pie_1")

    with tab2:
        # 动量图
        st.subheader("动量分析")
        momentum_options = {
            "momentum_7d": "7期动量",
            "momentum_14d": "14期动量",
            "momentum_30d": "30期动量",
            "momentum_90d": "90期动量"
        }
        selected_momentum = st.selectbox(
            "选择动量周期",
            options=list(momentum_options.keys()),
            format_func=lambda x: momentum_options[x],
            index=2
        )
        st.plotly_chart(
            charts.momentum_chart(selected_momentum, momentum_options[selected_momentum]),
            use_container_width=True
        )

        # Z-Score图
        st.subheader("Z-Score 极端识别")
        st.plotly_chart(charts.zscore_chart(), use_container_width=True)

    with tab3:
        st.subheader("M7 成分股详情")

        # 成分股表格
        weights = data['weights']
        market_caps = data['market_caps']
        m7_stocks = data['m7_stocks']

        # 计算各股票涨跌幅
        stock_changes = (m7_stocks.iloc[-1] / m7_stocks.iloc[0] - 1) * 100

        # 构建表格数据
        table_data = []
        for symbol in M7_SYMBOLS:
            table_data.append({
                "股票": f"{M7_NAMES[symbol]} ({symbol})",
                "市值 (万亿$)": f"{market_caps[symbol] / 1e12:.2f}",
                "权重": f"{weights[symbol] * 100:.1f}%",
                "区间涨跌": f"{stock_changes[symbol]:+.1f}%"
            })

        df_table = pd.DataFrame(table_data)
        st.dataframe(df_table, use_container_width=True, hide_index=True)

        # 权重饼图
        st.plotly_chart(charts.weights_pie_chart(weights), use_container_width=True, key="weights_pie_2")

    # 底部信息
    st.markdown("---")
    st.markdown("""
    **信号解读说明:**
    - 🟢🟢 强烈看多BTC: 短期和中期动量都 > 5%
    - 🟢 温和看多BTC: 短期或中期动量 > 2%
    - ⚪ 中性观望: 动量在 -2% ~ 2% 之间
    - 🔴 温和看多M7: 短期或中期动量 < -2%
    - 🔴🔴 强烈看多M7: 短期和中期动量都 < -5%

    **数据来源:** [Twelve Data](https://twelvedata.com/)
    """)


if __name__ == "__main__":
    main()
