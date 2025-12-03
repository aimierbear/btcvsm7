"""可视化模块 - 使用Plotly创建交互式图表"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd


class ChartGenerator:
    """图表生成器"""

    # 配色方案
    COLORS = {
        'btc': '#F7931A',       # 比特币橙
        'm7': '#4285F4',        # Google蓝
        'positive': '#00C853',  # 上涨绿
        'negative': '#FF1744',  # 下跌红
        'neutral': '#9E9E9E',   # 中性灰
        'ratio_line': '#9C27B0' # 紫色
    }

    def __init__(self, data: pd.DataFrame):
        """
        初始化图表生成器

        Args:
            data: full_analysis()返回的DataFrame
        """
        self.data = data

    def price_comparison_chart(self) -> go.Figure:
        """标准化价格对比图"""
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=self.data.index,
            y=self.data['btc_normalized'],
            name='BTC',
            line=dict(color=self.COLORS['btc'], width=2),
            hovertemplate='BTC: %{y:.1f}<extra></extra>'
        ))

        fig.add_trace(go.Scatter(
            x=self.data.index,
            y=self.data['m7_normalized'],
            name='M7指数',
            line=dict(color=self.COLORS['m7'], width=2),
            hovertemplate='M7: %{y:.1f}<extra></extra>'
        ))

        fig.update_layout(
            title='BTC vs M7 标准化价格 (基期=100)',
            xaxis_title='日期',
            yaxis_title='标准化价格',
            hovermode='x unified',
            legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
            height=350
        )

        return fig

    def price_ratio_chart(self) -> go.Figure:
        """相对强弱指数图"""
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=self.data.index,
            y=self.data['price_ratio'],
            name='BTC/M7 比率',
            line=dict(color=self.COLORS['ratio_line'], width=2),
            fill='tozeroy',
            fillcolor='rgba(156, 39, 176, 0.1)',
            hovertemplate='比率: %{y:.1f}<extra></extra>'
        ))

        # 添加基准线100
        fig.add_hline(
            y=100,
            line_dash="dash",
            line_color="gray",
            annotation_text="均衡线",
            annotation_position="bottom right"
        )

        fig.update_layout(
            title='相对强弱指数 (>100 BTC强势)',
            xaxis_title='日期',
            yaxis_title='强弱比率',
            hovermode='x unified',
            height=300
        )

        return fig

    def momentum_chart(self, column: str = 'momentum_30d', title: str = '30期动量') -> go.Figure:
        """动量柱状图"""
        fig = go.Figure()

        momentum = self.data[column]
        colors = [self.COLORS['positive'] if v >= 0 else self.COLORS['negative'] for v in momentum]

        fig.add_trace(go.Bar(
            x=self.data.index,
            y=momentum,
            marker_color=colors,
            name='动量',
            hovertemplate='%{y:.2f}%<extra></extra>'
        ))

        # 添加零线
        fig.add_hline(y=0, line_color="gray", line_width=1)

        fig.update_layout(
            title=f'{title} (BTC收益率 - M7收益率)',
            xaxis_title='日期',
            yaxis_title='动量差 (%)',
            hovermode='x unified',
            height=250
        )

        return fig

    def weights_pie_chart(self, weights: pd.Series) -> go.Figure:
        """M7成分股权重饼图"""
        fig = go.Figure(data=[go.Pie(
            labels=weights.index,
            values=weights.values,
            hole=0.4,
            textinfo='label+percent',
            hovertemplate='%{label}: %{percent}<extra></extra>'
        )])

        fig.update_layout(
            title='M7 成分股权重 (按市值)',
            height=350
        )

        return fig

    def main_dashboard(self, weights: pd.Series = None) -> go.Figure:
        """
        创建主仪表盘 (4行布局)

        Args:
            weights: M7权重序列 (可选)

        Returns:
            完整仪表盘Figure
        """
        fig = make_subplots(
            rows=4, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.08,
            row_heights=[0.35, 0.25, 0.2, 0.2],
            subplot_titles=(
                'BTC vs M7 标准化价格 (基期=100)',
                '相对强弱指数 (>100 BTC强势)',
                '30期动量 (%)',
                '7期动量 (%)'
            )
        )

        # Row 1: 标准化价格对比
        fig.add_trace(go.Scatter(
            x=self.data.index,
            y=self.data['btc_normalized'],
            name='BTC',
            line=dict(color=self.COLORS['btc'], width=2)
        ), row=1, col=1)

        fig.add_trace(go.Scatter(
            x=self.data.index,
            y=self.data['m7_normalized'],
            name='M7指数',
            line=dict(color=self.COLORS['m7'], width=2)
        ), row=1, col=1)

        # Row 2: 价格比率
        fig.add_trace(go.Scatter(
            x=self.data.index,
            y=self.data['price_ratio'],
            name='BTC/M7比率',
            line=dict(color=self.COLORS['ratio_line'], width=2),
            showlegend=False
        ), row=2, col=1)
        fig.add_hline(y=100, line_dash="dash", line_color="gray", row=2, col=1)

        # Row 3: 30期动量
        self._add_momentum_trace(fig, 'momentum_30d', row=3)

        # Row 4: 7期动量
        self._add_momentum_trace(fig, 'momentum_7d', row=4)

        fig.update_layout(
            title='BTC vs Magnificent 7 相对强弱分析',
            height=900,
            showlegend=True,
            hovermode='x unified',
            legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
        )

        return fig

    def _add_momentum_trace(self, fig: go.Figure, column: str, row: int):
        """添加动量轨迹到子图"""
        momentum = self.data[column]

        # 正值区域
        positive = momentum.where(momentum >= 0, 0)
        fig.add_trace(go.Scatter(
            x=self.data.index,
            y=positive,
            fill='tozeroy',
            fillcolor='rgba(0, 200, 83, 0.3)',
            line=dict(color=self.COLORS['positive'], width=1),
            showlegend=False,
            hoverinfo='skip'
        ), row=row, col=1)

        # 负值区域
        negative = momentum.where(momentum < 0, 0)
        fig.add_trace(go.Scatter(
            x=self.data.index,
            y=negative,
            fill='tozeroy',
            fillcolor='rgba(255, 23, 68, 0.3)',
            line=dict(color=self.COLORS['negative'], width=1),
            showlegend=False,
            hoverinfo='skip'
        ), row=row, col=1)

        # 实际值线
        fig.add_trace(go.Scatter(
            x=self.data.index,
            y=momentum,
            line=dict(color='rgba(0,0,0,0.5)', width=1),
            showlegend=False,
            hovertemplate='%{y:.2f}%<extra></extra>'
        ), row=row, col=1)

        fig.add_hline(y=0, line_dash="dash", line_color="gray", row=row, col=1)

    def zscore_chart(self) -> go.Figure:
        """Z-Score强度图"""
        fig = go.Figure()

        zscore = self.data['zscore']
        colors = [
            self.COLORS['positive'] if v > 0 else self.COLORS['negative']
            for v in zscore
        ]

        fig.add_trace(go.Bar(
            x=self.data.index,
            y=zscore,
            marker_color=colors,
            name='Z-Score',
            hovertemplate='Z-Score: %{y:.2f}<extra></extra>'
        ))

        # 添加阈值线
        fig.add_hline(y=2, line_dash="dash", line_color="green",
                      annotation_text="异常强势", annotation_position="right")
        fig.add_hline(y=-2, line_dash="dash", line_color="red",
                      annotation_text="异常弱势", annotation_position="right")
        fig.add_hline(y=0, line_color="gray", line_width=1)

        fig.update_layout(
            title='Z-Score 相对强度 (识别极端情况)',
            xaxis_title='日期',
            yaxis_title='Z-Score',
            height=300
        )

        return fig
