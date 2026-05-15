"""
全国人才流动网络可视化模块
包含：桑基图、弦图、气泡地图、热力矩阵
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import folium
from streamlit_folium import st_folium

# 城市坐标
CITY_COORDS = {
    '北京': (39.90, 116.41), '上海': (31.23, 121.47), '深圳': (22.54, 114.06),
    '广州': (23.13, 113.26), '杭州': (30.27, 120.16), '南京': (32.06, 118.80),
    '苏州': (31.30, 120.59), '成都': (30.57, 104.07), '重庆': (29.43, 106.91),
    '武汉': (30.59, 114.31), '西安': (34.34, 108.94), '天津': (39.34, 117.36),
    '青岛': (36.07, 120.38), '长沙': (28.23, 112.94), '郑州': (34.75, 113.63),
    '宁波': (29.87, 121.54), '大连': (38.91, 121.61), '沈阳': (41.80, 123.43),
    '济南': (36.65, 117.12), '无锡': (31.49, 120.31), '东莞': (23.05, 113.75),
    '佛山': (23.02, 113.12), '昆明': (25.04, 102.71), '福州': (26.08, 119.30),
    '厦门': (24.49, 118.09), '合肥': (31.85, 117.27), '南昌': (28.68, 115.89),
    '贵阳': (26.65, 106.63), '石家庄': (38.04, 114.48), '太原': (37.87, 112.55),
    '长春': (43.88, 125.32), '兰州': (36.06, 103.83), '哈尔滨': (45.80, 126.53),
    '海口': (20.02, 110.35), '保定': (38.87, 115.48), '唐山': (39.63, 118.18),
    '温州': (28.00, 120.67), '金华': (29.08, 119.65),
    '嘉兴': (30.75, 120.76), '绍兴': (30.00, 120.58), '烟台': (37.54, 121.39),
    '常州': (31.81, 119.97),
}


def plot_talent_flow_sankey(flow_df, top_n=15):
    """
    绘制人才流动桑基图
    左边：来源城市（北京/苏州/深圳）
    右边：目标城市
    """
    if flow_df is None or flow_df.empty:
        return None

    # 筛选主要流动
    top_targets = flow_df.groupby('目标城市')['人数'].sum().nlargest(top_n).index.tolist()
    flow_filtered = flow_df[flow_df['目标城市'].isin(top_targets)]

    # 创建节点和链接
    sources = flow_filtered['来源城市'].unique().tolist()
    targets = top_targets
    all_nodes = sources + targets

    node_map = {name: i for i, name in enumerate(all_nodes)}

    # 计算节点位置
    source_idx = [node_map[s] for s in flow_filtered['来源城市']]
    target_idx = [node_map[t] for t in flow_filtered['目标城市']]

    # 节点标签和颜色
    labels = all_nodes
    colors = ['#1a56db'] * len(sources) + ['#3b82f6'] * len(targets)

    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=labels,
            color=colors
        ),
        link=dict(
            source=source_idx,
            target=target_idx,
            value=flow_filtered['人数'].tolist(),
            color='rgba(150, 150, 150, 0.4)'
        )
    )])

    fig.update_layout(
        title_text="人才流动网络 (企业所在地 → 招聘岗位所在地)",
        font_size=12,
        height=500
    )
    return fig


def plot_chord_diagram(flow_df):
    """
    绘制弦图（简化版：使用热力图展示双向流动）
    """
    if flow_df is None or flow_df.empty:
        return None

    # 创建流出矩阵
    flow_pivot = flow_df.pivot_table(
        index='来源城市', columns='目标城市', values='人数', fill_value=0
    )

    # 保留主要城市
    top_cities = flow_pivot.sum(axis=0).nlargest(15).index.tolist()
    flow_pivot = flow_pivot[top_cities].loc[[c for c in ['北京', '苏州', '深圳'] if c in flow_pivot.index], top_cities]

    fig = px.imshow(
        flow_pivot.values,
        x=flow_pivot.columns,
        y=flow_pivot.index,
        color_continuous_scale='YlOrRd',
        title="城市间人才流动热力矩阵",
        labels=dict(x="目标城市", y="来源城市", color="流动人数"),
        text_auto=True
    )
    fig.update_layout(height=500, width=700)
    return fig


def plot_talent_bubble_map(city_stats):
    """
    绘制全国人才分布气泡地图
    """
    if city_stats is None or city_stats.empty:
        return None

    # 筛选有坐标的城市
    map_data = city_stats[city_stats['纬度'].notna()].copy()
    map_data['气泡大小'] = (map_data['职位总数'] / map_data['职位总数'].max() * 50 + 10).round(1)
    map_data['颜色'] = map_data['人才吸引力指数']

    # 创建Folium地图
    m = folium.Map(location=[35, 105], zoom_start=4, tiles='CartoDB positron')

    for _, row in map_data.iterrows():
        if row['经度'] and row['纬度']:
            # 颜色映射：吸引力指数越高颜色越红
            score = row['人才吸引力指数']
            if score > 60:
                color = '#dc2626'  # 红色
            elif score > 40:
                color = '#f59e0b'  # 橙色
            elif score > 25:
                color = '#1a56db'  # 蓝色
            else:
                color = '#94a3b8'  # 灰色

            radius = max(row['气泡大小'], 5)

            folium.CircleMarker(
                location=[row['纬度'], row['经度']],
                radius=radius,
                popup=folium.Popup(
                    f"<b>{row['城市']}</b><br>"
                    f"招聘企业: {row['招聘企业数']:,}<br>"
                    f"职位总数: {row['职位总数']:,}<br>"
                    f"薪资中位数: {int(row['薪资中位数']) if pd.notna(row['薪资中位数']) else 'N/A'}元/月<br>"
                    f"吸引力指数: {row['人才吸引力指数']:.1f}" if pd.notna(row['人才吸引力指数']) else "",
                    max_width=200
                ),
                color=color,
                fill=True,
                fillColor=color,
                fillOpacity=0.7,
                weight=2
            ).add_to(m)

    return m


def plot_city_industry_heatmap(city_industry_df, top_n=20):
    """
    绘制城市-行业招聘热力图
    """
    if city_industry_df is None or city_industry_df.empty:
        return None

    # 选取主要城市
    top_cities = city_industry_df.groupby('城市')['职位数'].sum().nlargest(top_n).index.tolist()
    data = city_industry_df[city_industry_df['城市'].isin(top_cities)]

    # 创建透视表
    pivot = data.pivot_table(
        index='城市', columns='行业', values='职位数', fill_value=0
    )

    # 按总职位数排序
    pivot = pivot.loc[pivot.sum(axis=1).sort_values(ascending=False).index]

    fig = px.imshow(
        pivot.values,
        x=pivot.columns,
        y=pivot.index,
        color_continuous_scale='YlOrRd',
        title=f"城市-行业招聘热力图 (TOP {top_n}城市)",
        labels=dict(x="行业", y="城市", color="职位数"),
        text_auto=True
    )
    fig.update_layout(height=max(400, len(pivot) * 25), xaxis_tickangle=45)
    return fig


def plot_salary_ranking(city_stats, top_n=20):
    """
    绘制城市薪资排名图
    """
    if city_stats is None or city_stats.empty:
        return None

    data = city_stats.nlargest(top_n, '薪资中位数')
    data = data[data['薪资中位数'].notna()]
    data = data.copy()
    data['薪资中位数'] = data['薪资中位数'].astype(int)

    colors = ['#e94560' if c in ['北京', '苏州', '深圳'] else '#3498db' for c in data['城市']]

    fig = go.Figure(go.Bar(
        x=data['薪资中位数'],
        y=data['城市'],
        orientation='h',
        marker_color=colors,
        text=[f'{int(v):,}' for v in data['薪资中位数']],
        textposition='outside'
    ))

    fig.update_layout(
        title=f"城市薪资中位数排名 (TOP {top_n})",
        xaxis_title="薪资中位数 (元/月)",
        yaxis_title="城市",
        height=500,
        showlegend=False
    )
    return fig


def plot_attraction_index(city_stats, top_n=20):
    """
    绘制城市人才吸引力指数排名
    """
    if city_stats is None or city_stats.empty:
        return None

    data = city_stats.nlargest(top_n, '人才吸引力指数')

    colors = ['#e94560' if c in ['北京', '苏州', '深圳'] else '#3498db' for c in data['城市']]

    fig = go.Figure()

    # 添加水平条形图
    fig.add_trace(go.Bar(
        x=data['人才吸引力指数'],
        y=data['城市'],
        orientation='h',
        marker_color=colors,
        text=data['人才吸引力指数'].apply(lambda x: f'{x:.1f}'),
        textposition='outside'
    ))

    fig.update_layout(
        title=f"城市人才吸引力指数排名 (TOP {top_n})",
        xaxis_title="吸引力指数",
        yaxis_title="城市",
        height=500,
        showlegend=False
    )
    return fig


def plot_industry_diversity(city_stats, top_n=20):
    """
    绘制城市行业多样性对比图
    """
    if city_stats is None or city_stats.empty:
        return None

    data = city_stats.nlargest(top_n, '行业多样性指数')
    data = data[data['行业多样性指数'].notna()]

    colors = ['#e94560' if c in ['北京', '苏州', '深圳'] else '#3498db' for c in data['城市']]

    fig = go.Figure(go.Bar(
        x=data['行业多样性指数'],
        y=data['城市'],
        orientation='h',
        marker_color=colors,
        text=data['行业多样性指数'].apply(lambda x: f'{x:.2f}'),
        textposition='outside'
    ))

    fig.update_layout(
        title=f"城市行业多样性指数排名 (TOP {top_n})",
        xaxis_title="行业多样性指数 (信息熵)",
        yaxis_title="城市",
        height=500,
        showlegend=False
    )
    return fig


def load_nationwide_data(result_dir):
    """加载全国数据"""
    import os
    if not os.path.isabs(result_dir):
        base = os.path.dirname(os.path.abspath(__file__))
        result_dir = os.path.join(base, result_dir)
    city_stats = pd.read_csv(f"{result_dir}/全国城市统计表.csv", encoding="utf-8-sig")
    city_industry = pd.read_csv(f"{result_dir}/城市行业招聘_新.csv", encoding="utf-8-sig")
    flow_df = pd.read_csv(f"{result_dir}/人才流动_新.csv", encoding="utf-8-sig")

    flow_df = flow_df.rename(columns={'来源': '来源城市', '目标': '目标城市'})
    city_industry = city_industry.rename(columns={'工作城市': '城市'})
    city_industry = city_industry.melt(
        id_vars=['城市'], var_name='行业', value_name='职位数'
    ).dropna(subset=['职位数'])
    city_industry['职位数'] = city_industry['职位数'].astype(int)

    return city_stats, city_industry, flow_df
