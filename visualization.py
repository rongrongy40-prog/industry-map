"""
中国产业地图 - 商业决策支持系统 (Professional Dashboard)
基于所有城市真实数据，具备商业决策价值的智能分析平台
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import folium
from streamlit_folium import st_folium
import re
import os

# 导入可视化模块
from talent_flow_viz import (
    load_nationwide_data,
    plot_talent_flow_sankey,
    plot_chord_diagram,
    plot_talent_bubble_map,
    plot_city_industry_heatmap,
    plot_salary_ranking,
    plot_attraction_index,
    plot_industry_diversity
)

st.set_page_config(
    page_title="产业地图 | 商业决策支持系统",
    layout="wide",
    page_icon="🏭",
    initial_sidebar_state="expanded"
)

# ============================================================
#  0. 自定义 CSS — 专业商业分析主题
# ============================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500;600;700;800&display=swap');

    :root {
        --brand: #1a56db;
        --brand-light: #3b83f6;
        --brand-dark: #1e40af;
        --accent: #f59e0b;
        --accent-red: #dc2626;
        --success: #059669;
        --bg: #f8fafc;
        --card-bg: #ffffff;
        --border: #e5e7eb;
        --text-primary: #111827;
        --text-secondary: #6b7280;
        --text-muted: #9ca3af;
        --sidebar-bg: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
        --card-shadow: 0 1px 3px rgba(0,0,0,0.06), 0 4px 12px rgba(0,0,0,0.04);
        --card-shadow-hover: 0 4px 20px rgba(0,0,0,0.10);
    }

    * { font-family: 'Noto Sans SC', -apple-system, 'PingFang SC', 'Microsoft YaHei', sans-serif !important; }

    .stApp { background: var(--bg); }

    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        max-width: 1400px;
    }

    /* ---- 侧边栏 ---- */
    [data-testid="stSidebar"] {
        background: var(--sidebar-bg) !important;
        border-right: 1px solid rgba(255,255,255,0.06);
    }
    [data-testid="stSidebar"] * { color: #cbd5e1 !important; }

    .sidebar-brand {
        padding: 20px 16px 16px;
        text-align: center;
        border-bottom: 1px solid rgba(255,255,255,0.08);
        margin-bottom: 8px;
    }
    .sidebar-brand .brand-icon {
        font-size: 2.2rem;
        display: block;
        margin-bottom: 6px;
    }
    .sidebar-brand .brand-title {
        color: #f1f5f9 !important;
        font-size: 0.95rem !important;
        font-weight: 700 !important;
        letter-spacing: 0.05em;
        line-height: 1.4;
    }
    .sidebar-brand .brand-sub {
        color: #64748b !important;
        font-size: 0.7rem !important;
        margin-top: 4px;
    }

    .sidebar-section {
        padding: 4px 12px;
    }
    .sidebar-section-title {
        color: #475569 !important;
        font-size: 0.62rem !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        padding: 8px 4px 4px;
    }

    [data-testid="stSidebar"] .stRadio label {
        border-radius: 10px;
        padding: 9px 14px;
        transition: all 0.2s;
        font-weight: 500;
        font-size: 0.88rem;
        margin: 2px 0;
    }
    [data-testid="stSidebar"] .stRadio label:hover {
        background: rgba(26,86,219,0.15) !important;
    }
    [data-testid="stSidebar"] .stRadio [data-selected="true"] label {
        background: linear-gradient(135deg, rgba(26,86,219,0.3), rgba(26,86,219,0.15)) !important;
        color: #f1f5f9 !important;
        font-weight: 700;
        border-left: 3px solid #3b83f6;
    }

    [data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.08) !important; margin: 10px 0; }
    [data-testid="stSidebar"] [data-testid="stMetricLabel"] { color: #64748b !important; font-size: 0.68rem !important; }
    [data-testid="stSidebar"] [data-testid="stMetricValue"] { color: #f1f5f9 !important; font-size: 1.3rem !important; font-weight: 800 !important; }

    .sidebar-data-card {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.07);
        border-radius: 12px;
        padding: 14px;
        margin: 6px 0;
    }
    .sidebar-data-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 4px 0;
        border-bottom: 1px solid rgba(255,255,255,0.05);
        font-size: 0.78rem;
    }
    .sidebar-data-row:last-child { border-bottom: none; }
    .sidebar-data-label { color: #64748b; }
    .sidebar-data-value { color: #f1f5f9; font-weight: 600; }

    /* ---- 标题体系 ---- */
    h1 {
        color: var(--text-primary) !important;
        font-weight: 800 !important;
        font-size: 1.65rem !important;
        letter-spacing: -0.02em;
        border-bottom: none !important;
        padding-bottom: 0 !important;
    }
    h2 {
        color: var(--text-primary) !important;
        font-weight: 700 !important;
        font-size: 1.2rem !important;
        letter-spacing: -0.01em;
    }
    h3 {
        color: #374151 !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
    }
    h4 {
        color: var(--text-secondary) !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
    }

    /* ---- KPI 卡片 ---- */
    .kpi-grid {
        display: flex;
        flex-direction: column;
        gap: 10px;
        margin-bottom: 4px;
    }
    .kpi-card {
        background: var(--card-bg);
        border-radius: 14px;
        padding: 16px 24px;
        box-shadow: var(--card-shadow);
        border: 1px solid var(--border);
        transition: all 0.25s;
        position: relative;
        overflow: hidden;
        display: flex;
        align-items: center;
        gap: 16px;
    }
    .kpi-card:hover {
        box-shadow: var(--card-shadow-hover);
        transform: translateY(-2px);
    }
    .kpi-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 3px;
        background: var(--brand);
        border-radius: 14px 14px 0 0;
    }
    .kpi-card.green::before { background: var(--success); }
    .kpi-card.amber::before { background: var(--accent); }
    .kpi-card.red::before { background: var(--accent-red); }
    .kpi-label {
        color: var(--text-muted);
        font-size: 0.68rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        white-space: nowrap;
    }
    .kpi-value {
        color: var(--text-primary);
        font-size: 1.3rem;
        font-weight: 800;
        line-height: 1.2;
    }
    .kpi-sub {
        color: var(--text-muted);
        font-size: 0.72rem;
        margin-top: 4px;
    }

    /* ---- 内容卡片 ---- */
    .content-card {
        background: var(--card-bg);
        border-radius: 16px;
        padding: 24px;
        box-shadow: var(--card-shadow);
        border: 1px solid var(--border);
        margin: 10px 0;
    }
    .content-card-header {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 18px;
        padding-bottom: 14px;
        border-bottom: 1px solid var(--border);
    }
    .content-card-icon {
        width: 36px;
        height: 36px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.1rem;
        flex-shrink: 0;
    }
    .content-card-title {
        font-size: 0.95rem;
        font-weight: 700;
        color: var(--text-primary);
    }
    .content-card-sub {
        font-size: 0.72rem;
        color: var(--text-muted);
    }

    /* ---- 洞察卡片 ---- */
    .insight-box {
        border-radius: 12px;
        padding: 16px 18px;
        margin: 8px 0;
        font-size: 0.85rem;
        line-height: 1.7;
    }
    .insight-success { background: linear-gradient(135deg, #f0fdf4, #dcfce7); border-left: 4px solid #22c55e; color: #14532d; }
    .insight-info    { background: linear-gradient(135deg, #eff6ff, #dbeafe); border-left: 4px solid #3b82f6; color: #1e3a8a; }
    .insight-warn    { background: linear-gradient(135deg, #fffbeb, #fef3c7); border-left: 4px solid #f59e0b; color: #92400e; }
    .insight-danger  { background: linear-gradient(135deg, #fef2f2, #fee2e2); border-left: 4px solid #ef4444; color: #7f1d1d; }

    /* ---- 核心发现 ---- */
    .finding-card {
        background: linear-gradient(135deg, var(--brand), var(--brand-dark));
        border-radius: 12px;
        padding: 14px 18px;
        margin: 8px 0;
        color: #fff;
        font-size: 0.88rem;
        line-height: 1.65;
        box-shadow: 0 4px 14px rgba(26,86,219,0.25);
        border-left: 4px solid rgba(255,255,255,0.3);
    }

    /* ---- 标签页 ---- */
    .stTabs [data-baseweb="tab-list"] {
        background: #f1f5f9;
        border-radius: 12px;
        padding: 4px;
        gap: 2px;
        border: 1px solid #e5e7eb;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 9px;
        color: var(--text-secondary);
        font-weight: 600;
        font-size: 0.82rem;
        padding: 7px 18px;
        transition: all 0.2s;
    }
    .stTabs [data-baseweb="tab"]:hover { color: var(--text-primary); }
    .stTabs [aria-selected="true"] {
        background: var(--card-bg) !important;
        color: var(--brand) !important;
        box-shadow: 0 1px 4px rgba(0,0,0,0.08);
        font-weight: 700;
    }

    /* ---- 表格 ---- */
    .dataframe { border-radius: 12px; overflow: hidden; }
    .dataframe tbody tr { background: #ffffff !important; }
    .dataframe tbody tr:nth-child(even) { background: #f9fafb !important; }
    .dataframe thead tr th {
        background: linear-gradient(180deg, #f8fafc, #f3f4f6) !important;
        color: #374151 !important;
        font-weight: 700;
        font-size: 0.75rem;
        padding: 10px 12px !important;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        border-bottom: 2px solid #e5e7eb !important;
    }
    .dataframe tbody tr:hover { background: #eff6ff !important; }
    .dataframe td { font-size: 0.82rem !important; color: #374151 !important; }

    /* ---- 按钮 ---- */
    .stButton > button {
        border-radius: 10px !important;
        font-weight: 600 !important;
        padding: 8px 20px !important;
        transition: all 0.2s;
        border: none !important;
    }

    /* ---- 分隔线 ---- */
    hr { border-color: var(--border); opacity: 0.6; }

    /* ---- 滚动条 ---- */
    ::-webkit-scrollbar { width: 5px; height: 5px; }
    ::-webkit-scrollbar-track { background: #f1f5f9; }
    ::-webkit-scrollbar-thumb { background: #d1d5db; border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: #9ca3af; }

    /* ---- 图表统一 ---- */
    .js-plotly-plot .plotly { border-radius: 14px; overflow: hidden; }
    .js-plotly-plot .modebar { opacity: 0; transition: opacity 0.2s; }
    .js-plotly-plot:hover .modebar { opacity: 1; }

    /* ---- 工具提示 ---- */
    .tooltip {
        position: relative;
        display: inline-block;
        cursor: help;
        border-bottom: 1px dashed var(--text-muted);
    }
    .tooltip .tooltiptext {
        visibility: hidden;
        background: #1f2937;
        color: #fff;
        font-size: 0.72rem;
        padding: 8px 12px;
        border-radius: 8px;
        position: absolute;
        z-index: 100;
        bottom: 140%;
        left: 50%;
        transform: translateX(-50%);
        white-space: nowrap;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        line-height: 1.5;
        width: max-content;
        max-width: 280px;
    }
    .tooltip:hover .tooltiptext { visibility: visible; }

    /* ---- 底部 ---- */
    .site-footer {
        background: #0f172a;
        border-radius: 16px;
        padding: 32px;
        margin-top: 32px;
        color: #94a3b8;
        font-size: 0.8rem;
    }
    .site-footer .footer-title {
        color: #f1f5f9;
        font-size: 1rem;
        font-weight: 700;
        margin-bottom: 12px;
    }
    .site-footer .footer-row {
        display: flex;
        gap: 32px;
        flex-wrap: wrap;
        margin-top: 16px;
    }
    .site-footer .footer-item {
        color: #94a3b8;
        font-size: 0.78rem;
        line-height: 1.8;
    }
    .site-footer .footer-item strong { color: #cbd5e1; }

    /* ---- 高亮 ---- */
    .highlight { color: var(--brand); font-weight: 700; }
    .text-red { color: var(--accent-red); }
    .text-green { color: var(--success); }
    .text-amber { color: var(--accent); }

    /* ---- 分隔 ---- */
    .section-divider { margin: 6px 0; }

    /* ---- Badge ---- */
    .badge {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 20px;
        font-size: 0.72rem;
        font-weight: 700;
    }
    .badge-blue { background: #dbeafe; color: #1d4ed8; }
    .badge-green { background: #dcfce7; color: #15803d; }
    .badge-red { background: #fee2e2; color: #b91c1c; }
    .badge-amber { background: #fef3c7; color: #b45309; }

    /* ---- 投资推荐卡 ---- */
    .invest-card {
        background: linear-gradient(135deg, #ffffff, #f8fafc);
        border-radius: 16px;
        padding: 24px;
        border: 1px solid var(--border);
        box-shadow: var(--card-shadow);
        text-align: center;
    }
    .invest-card-rank {
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: var(--text-muted);
        margin-bottom: 6px;
    }
    .invest-card-city {
        font-size: 1.3rem;
        font-weight: 800;
        color: var(--text-primary);
        margin: 4px 0;
    }
    .invest-card-score {
        font-size: 2.2rem;
        font-weight: 900;
        background: linear-gradient(135deg, var(--brand), #6366f1);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 8px 0;
    }
    .invest-card-meta {
        font-size: 0.75rem;
        color: var(--text-muted);
    }

    /* ---- Alert ---- */
    .stAlert { border-radius: 12px !important; }

    /* ---- 进度条 ---- */
    .progress-bar-container {
        background: #e5e7eb;
        border-radius: 4px;
        height: 6px;
        overflow: hidden;
        margin: 4px 0;
    }
    .progress-bar-fill {
        height: 100%;
        border-radius: 4px;
        transition: width 0.5s;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
#  1. 数据加载
# ============================================================
import os
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
RESULT_DIR = os.path.join(PROJECT_ROOT, "result")
IMG_DIR = os.path.join(RESULT_DIR, "images")

code_to_name = {
    'A': '农林业', 'B': '采矿业', 'C': '制造业', 'D': '电力热力',
    'E': '建筑业', 'F': '批发零售', 'G': '住宿餐饮', 'H': '交通运输',
    'I': '信息技术', 'J': '金融业', 'K': '房地产业', 'L': '租赁商务服务',
    'M': '科学技术服务', 'N': '水利环境', 'O': '居民服务', 'P': '教育',
    'Q': '卫生社会', 'R': '文体娱乐', 'S': '其他', 'T': '综合'
}

industry_map = {
    '全部行业': None,
    '信息技术(I)': 'I', '金融业(J)': 'J', '制造业(C)': 'C',
    '批发零售(F)': 'F', '科学技术(M)': 'M', '建筑业(E)': 'E',
    '房地产业(K)': 'K', '交通运输(H)': 'H', '文化娱乐(R)': 'R'
}

def extract_salary(s):
    """解析薪水字符串，返回元/月薪资（与 nationwide_data_processor.py 完全一致）"""
    if pd.isna(s):
        return None
    s = str(s).strip().replace(',', '').replace(' ', '')

    # 1. 确定单位
    if any(u in s for u in ['万/月', '万元/月']):
        unit = 10000; s = s.replace('万', '').replace('元', '')
    elif any(u in s for u in ['万/年', '万元/年']):
        unit = 10000 / 12; s = s.replace('万', '').replace('元', '').replace('年', '')
    elif any(u in s for u in ['千/月', '千元/月']):
        unit = 1000; s = s.replace('千', '').replace('元', '').replace('月', '')
    elif 'k/' in s.lower() or 'K/' in s:
        unit = 1000; s = re.sub(r'[kK]', '', s)
    elif any(u in s for u in ['元/天', '/天', '元/日']):
        unit = 22; s = re.sub(r'元|天|日', '', s)
    elif '元/月' in s or '元 ' in s:
        unit = 1; s = s.replace('元', '').replace('月', '')
    else:
        unit = 1

    # 2. 提取数字
    nums = re.findall(r'\d+(?:\.\d+)?', s)
    if not nums:
        return None
    nums = [float(n) for n in nums]

    # 3. Range 格式取均值
    if len(nums) >= 2:
        nums = [sum(nums) / len(nums)]

    val = nums[0] * unit

    # 4. 合理性过滤
    if val < 1000 or val > 1000000:
        return None
    return val


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
    '潍坊': (36.71, 119.16), '常州': (31.81, 119.97), '呼和浩特': (40.84, 111.73),
}

DISTRICT_MAP = {
    '海淀区': '北京', '朝阳区': '北京', '丰台区': '北京', '西城区': '北京', '东城区': '北京',
    '通州区': '北京', '昌平区': '北京', '大兴区': '北京', '顺义区': '北京', '房山区': '北京',
    '石景山': '北京', '怀柔区': '北京', '门头沟': '北京', '平谷区': '北京', '密云区': '北京',
    '浦东新区': '上海', '闵行区': '上海', '徐汇区': '上海', '黄浦区': '上海', '静安区': '上海',
    '长宁区': '上海', '普陀区': '上海', '虹口区': '上海', '杨浦区': '上海', '宝山区': '上海',
    '嘉定区': '上海', '金山区': '上海', '松江区': '上海', '青浦区': '上海', '奉贤区': '上海',
    '崇明区': '上海',
    '南山区': '深圳', '福田区': '深圳', '龙华区': '深圳', '宝安区': '深圳', '光明区': '深圳',
    '龙岗区': '深圳', '罗湖区': '深圳', '盐田区': '深圳', '坪山区': '深圳', '大鹏新区': '深圳',
    '天河区': '广州', '白云区': '广州', '黄埔区': '广州', '番禺区': '广州', '海珠区': '广州',
    '越秀区': '广州', '荔湾区': '广州', '南沙区': '广州', '增城区': '广州', '从化区': '广州',
    '工业园区': '苏州', '姑苏区': '苏州', '吴中区': '苏州', '相城区': '苏州', '虎丘区': '苏州',
    '昆山': '苏州',
    '江宁区': '南京', '浦口区': '南京', '六合区': '南京', '溧水区': '南京', '高淳区': '南京',
    '西湖区': '杭州', '余杭区': '杭州', '萧山区': '杭州', '滨江区': '杭州', '拱墅区': '杭州',
    '江干区': '杭州', '上城区': '杭州', '钱塘区': '杭州',
    '锦江区': '成都', '青羊区': '成都', '武侯区': '成都', '成华区': '成都', '金牛区': '成都',
    '龙泉驿': '成都', '双流区': '成都', '郫都区': '成都', '温江区': '成都', '新都区': '成都',
    '渝北区': '重庆', '江北区': '重庆', '南岸区': '重庆', '九龙坡': '重庆', '沙坪坝': '重庆',
    '大渡口': '重庆', '巴南区': '重庆', '北碚区': '重庆', '璧山区': '重庆', '涪陵区': '重庆',
    '万州区': '重庆', '江津区': '重庆',
    '洪山区': '武汉', '武昌区': '武汉', '江汉区': '武汉', '硚口区': '武汉', '汉阳区': '武汉',
    '青山区': '武汉', '江岸区': '武汉', '东西湖': '武汉', '黄陂区': '武汉', '新洲区': '武汉',
    '雁塔区': '西安', '碑林区': '西安', '莲湖区': '西安', '新城区': '西安', '灞桥区': '西安',
    '未央区': '西安', '长安区': '西安', '临潼区': '西安',
}


def extract_city(loc):
    """从工作地点提取城市名（与 nationwide_data_processor.py 完全一致）"""
    if pd.isna(loc):
        return None
    loc = str(loc)
    for city in CITY_COORDS.keys():
        if city in loc:
            return city
    for district, city in DISTRICT_MAP.items():
        if district in loc:
            return city
    return None


@st.cache_data
def load_all_data():
    recruit_path = f"{DATA_DIR}/2. 企业招聘行为表.csv"
    if not os.path.exists(recruit_path):
        zip_path = f"{DATA_DIR}/2. 企业招聘行为表.zip"
        if os.path.exists(zip_path):
            import zipfile
            with zipfile.ZipFile(zip_path, 'r') as z:
                z.extractall(DATA_DIR)

    df_base     = pd.read_csv(f"{DATA_DIR}/1. 企业基础信息.csv", encoding="utf-8-sig", low_memory=False)
    df_recruit  = pd.read_csv(f"{DATA_DIR}/2. 企业招聘行为表.csv", encoding="utf-8-sig", low_memory=False)
    center_df   = pd.read_csv(f"{RESULT_DIR}/就业中心识别结果_簇质心.csv", encoding="utf-8-sig")
    industry_df = pd.read_csv(f"{RESULT_DIR}/行业集聚综合分析.csv", encoding="utf-8-sig")
    center_detail = pd.read_csv(f"{RESULT_DIR}/就业中心详细信息.csv", encoding="utf-8-sig")
    evolution_df = pd.read_csv(f"{RESULT_DIR}/年度演化摘要_完整版.csv", encoding="utf-8-sig")

    city_map = {110000: '北京', 320500: '苏州', 440300: '深圳'}
    df_base['城市'] = df_base['城市代码'].map(city_map)

    df_recruit['薪资'] = df_recruit['薪水范围'].apply(extract_salary)
    df_recruit['工作城市'] = df_recruit['工作地点'].apply(extract_city)

    df_merged = df_recruit.merge(
        df_base[['企业名称', '城市', '行业门类']], on='企业名称', how='left'
    )

    return df_base, df_recruit, center_df, industry_df, center_detail, evolution_df, df_merged

df_base, df_recruit, center_df, industry_df, center_detail, evolution_df, df_merged = load_all_data()


@st.cache_data
def compute_city_salary_stats():
    """从已加载的 df_merged 计算城市薪资统计（共用同一套 extract_salary / extract_city 结果）"""
    valid = df_merged[df_merged['工作城市'].notna() & df_merged['薪资'].notna()].copy()
    valid['行业'] = valid['行业门类'].map(code_to_name)

    # 城市薪资统计
    city_sal = valid.groupby('工作城市')['薪资'].agg(
        薪资中位数='median', 平均薪资='mean', 薪资标准差='std',
        最高薪资='max', 样本数='count'
    ).reset_index().rename(columns={'工作城市': '城市'})
    city_sal = city_sal[city_sal['样本数'] >= 5]
    for col in ['薪资中位数', '平均薪资', '薪资标准差', '最高薪资']:
        city_sal[col] = city_sal[col].astype(int)
    city_sal['纬度'] = city_sal['城市'].map(lambda x: CITY_COORDS.get(x, (None, None))[0])
    city_sal['经度'] = city_sal['城市'].map(lambda x: CITY_COORDS.get(x, (None, None))[1])

    # 行业薪资排名（从 valid 算，保持一致）
    ind_sal = valid.groupby('行业')['薪资'].agg(样本数='count', 薪资中位数='median').reset_index()
    ind_sal = ind_sal[ind_sal['样本数'] >= 20].sort_values('薪资中位数', ascending=False)
    ind_sal['薪资中位数'] = ind_sal['薪资中位数'].astype(int)

    # 城市-行业薪资矩阵（pivot_table 确保纯数值列）
    city_ind_sal = valid.pivot_table(
        index='工作城市', columns='行业', values='薪资', aggfunc='median'
    )
    city_ind_sal.index.name = '城市'
    city_ind_sal = city_ind_sal.fillna(0).astype(int)

    return city_sal, ind_sal, city_ind_sal

# ============================================================
#  2. 辅助计算函数
# ============================================================
def city_kpis(city):
    c_data = df_base[df_base['城市'] == city]
    c_recruit = df_merged[df_merged['城市'] == city]
    cap = c_data['注册资本(万元)'].dropna()
    cap = cap[(cap > 0) & (cap < 50000)]
    crow = center_df[center_df['城市'] == city].iloc[0]
    return c_data, c_recruit, cap, crow


def get_invest_score(city):
    c_data, c_recruit, cap, crow = city_kpis(city)
    large_ratio = len(cap[cap > 1000]) / len(cap) if len(cap) > 0 else 0
    avg_sal = c_recruit['薪资'].median() or 0
    score = (1 - crow['NNI']) * 40 + large_ratio * 35 + (avg_sal / 10000) * 15
    risk = 0
    if crow['NNI'] < 0.35: risk += 1
    if crow['有效簇数'] == 1: risk += 2
    if crow['Moran_P'] > 0.05: risk += 1
    risk_level = '低风险' if risk <= 1 else ('中风险' if risk <= 3 else '高风险')
    return score, risk, risk_level


def color_map(city):
    return {'北京': '#e94560', '苏州': '#10b981', '深圳': '#3b82f6'}.get(city, '#94a3b8')


# 预计算各城市对比数据 (模块级别，供各页面使用)
comp_data = []
for city in center_df['城市'].tolist():
    try:
        c_data, c_recruit, cap, crow = city_kpis(city)
    except Exception:
        continue
    avg_sal = c_recruit['薪资'].median()
    score, risk, rlevel = get_invest_score(city)
    comp_data.append({
        "城市": city,
        "企业数": len(c_data),
        "就业中心": int(crow['有效簇数']),
        "NNI": round(float(crow['NNI']), 3),
        "Moran_I": round(float(crow['Moran_I']), 4),
        "Moran_P": float(crow['Moran_P']),
        "薪资中位数(元)": round(avg_sal) if avg_sal else 0,
        "平均注册资本(万)": round(cap.median()) if len(cap) > 0 else 0,
        "投资评分": round(score, 1),
        "风险等级": rlevel,
        "空间格局": crow['最终空间格局'],
    })
comp_df = pd.DataFrame(comp_data)

# ============================================================
#  3. 页面布局 — 顶部 Header
# ============================================================
st.markdown(f"""
<div style="background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 50%, #1e40af 100%);
            border-radius: 18px; padding: 28px 32px; margin-bottom: 18px;
            position: relative; overflow: hidden;">
    <div style="position: absolute; top: -30px; right: -30px; width: 200px; height: 200px;
                background: radial-gradient(circle, rgba(59,130,246,0.15) 0%, transparent 70%);
                border-radius: 50%; pointer-events: none;"></div>
    <div style="position: absolute; bottom: -40px; left: 20%; width: 150px; height: 150px;
                background: radial-gradient(circle, rgba(245,158,11,0.10) 0%, transparent 70%);
                border-radius: 50%; pointer-events: none;"></div>
    <div style="display: flex; justify-content: space-between; align-items: center; position: relative; z-index: 1;">
        <div>
            <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 6px;">
                <span style="font-size: 1.6rem;">🏭</span>
                <div style="font-size: 1.5rem; font-weight: 800; color: #ffffff; letter-spacing: 0.02em; line-height: 1.2;">
                    中国产业地图 · 商业决策支持系统
                </div>
            </div>
            <div style="color: rgba(255,255,255,0.6); font-size: 0.8rem; letter-spacing: 0.03em;">
                基于空间计量经济学分析 · 产业集聚洞察 · 投资决策支持
            </div>
        </div>
        <div style="text-align: right; display: flex; gap: 20px;">
            <div style="background: rgba(255,255,255,0.08); border-radius: 12px; padding: 10px 16px; text-align: center; min-width: 80px;">
                <div style="color: #3b82f6; font-size: 1.1rem; font-weight: 800;">{len(df_base):,}</div>
                <div style="color: rgba(255,255,255,0.5); font-size: 0.62rem; text-transform: uppercase; letter-spacing: 0.06em;">企业数</div>
            </div>
            <div style="background: rgba(255,255,255,0.08); border-radius: 12px; padding: 10px 16px; text-align: center; min-width: 80px;">
                <div style="color: #22c55e; font-size: 1.1rem; font-weight: 800;">{len(df_recruit):,}</div>
                <div style="color: rgba(255,255,255,0.5); font-size: 0.62rem; text-transform: uppercase; letter-spacing: 0.06em;">招聘数</div>
            </div>
            <div style="background: rgba(255,255,255,0.08); border-radius: 12px; padding: 10px 16px; text-align: center; min-width: 80px;">
                <div style="color: #f59e0b; font-size: 1.1rem; font-weight: 800;">{df_recruit['工作城市'].nunique()}</div>
                <div style="color: rgba(255,255,255,0.5); font-size: 0.62rem; text-transform: uppercase; letter-spacing: 0.06em;">城市数</div>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================================
#  4. 侧边栏
# ============================================================
with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand">
        <span class="brand-icon">🏭</span>
        <div class="brand-title">产业地图<br>商业决策系统</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sidebar-section-title">分析模块</div>', unsafe_allow_html=True)

    all_pages = [
        "📊 执行摘要",
        "🏙️ 北深苏分析",
        "🌐 全国分析",
    ]
    page = st.radio("导航", all_pages, index=0)

    sub_map_north = {
        "📈 行业深度洞察": "🏙️ 北深苏·行业深度洞察",
        "💼 投资决策": "🏙️ 北深苏·投资决策",
        "🏙️ 年度演化": "🏙️ 北深苏·年度演化",
        "⚖️ 三城综合对比": "🏙️ 北深苏·三城综合对比",
        "🔍 企业查询": "🏙️ 北深苏·企业查询",
    }
    sub_map_nation = {
        "🕸️ 人才流动网络": "🌐 全国人才流动网络",
        "🗺️ 产业地图": "🗼 全国产业地图",
        "💰 薪酬与竞争": "💰 薪酬与竞争",
        "📈 增长潜力": "📈 增长潜力",
    }
    if page == "🏙️ 北深苏分析":
        sub = st.selectbox("子模块", list(sub_map_north.keys()), key="nav_north")
        page = sub_map_north[sub]
    elif page == "🌐 全国分析":
        sub = st.selectbox("子模块", list(sub_map_nation.keys()), key="nav_nation")
        page = sub_map_nation[sub]

    st.markdown("---")

    st.markdown('<div class="sidebar-section-title">数据概览</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="sidebar-data-card">
        <div class="sidebar-data-row">
            <span class="sidebar-data-label">企业总数</span>
            <span class="sidebar-data-value" style="color:#3b82f6;">{len(df_base):,}</span>
        </div>
        <div class="sidebar-data-row">
            <span class="sidebar-data-label">招聘记录</span>
            <span class="sidebar-data-value" style="color:#22c55e;">{len(df_recruit):,}</span>
        </div>
        <div class="sidebar-data-row">
            <span class="sidebar-data-label">覆盖城市</span>
            <span class="sidebar-data-value" style="color:#f59e0b;">{df_recruit['工作城市'].nunique()}个</span>
        </div>
        <div class="sidebar-data-row">
            <span class="sidebar-data-label">行业门类</span>
            <span class="sidebar-data-value">{df_base['行业门类'].nunique()}类</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<div class="sidebar-section-title">指标说明</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size:0.68rem; color:#64748b; line-height:1.7; padding:0 4px;">
        <div style="margin-bottom:6px;"><b style="color:#94a3b8;">NNI</b> — 最近邻指数，衡量产业集聚程度</div>
        <div style="margin-bottom:6px;"><b style="color:#94a3b8;">Moran I</b> — 空间自相关指数</div>
        <div style="margin-bottom:6px;"><b style="color:#94a3b8;">就业中心</b> — 产业集聚核心区数量</div>
        <div><b style="color:#94a3b8;">CR5</b> — 前5城市集中度</div>
    </div>
    """, unsafe_allow_html=True)

# ============================================================
#  5. 执行摘要
# ============================================================
if page == "📊 执行摘要":
    st.title("📊 执行摘要")
    city_sal_stats, _, _ = compute_city_salary_stats()

    # ---- KPI 卡片组 ----
    top_sal = int(city_sal_stats['薪资中位数'].max()) if not city_sal_stats.empty else 0
    top_city_sal = city_sal_stats.loc[city_sal_stats['薪资中位数'].idxmax(), '城市'] if not city_sal_stats.empty else 'N/A'

    st.markdown(f"""
    <div class="kpi-grid">
        <div class="kpi-card">
            <div class="kpi-value" style="color:#1a56db;">{len(df_base):,}</div>
            <div>
                <div class="kpi-label">企业总数</div>
                <div class="kpi-sub">注册企业数量</div>
            </div>
        </div>
        <div class="kpi-card green">
            <div class="kpi-value" style="color:#059669;">{len(df_recruit):,}</div>
            <div>
                <div class="kpi-label">招聘职位</div>
                <div class="kpi-sub">在招岗位</div>
            </div>
        </div>
        <div class="kpi-card amber">
            <div class="kpi-value" style="color:#d97706;">{df_recruit['工作城市'].nunique()}</div>
            <div>
                <div class="kpi-label">覆盖城市</div>
                <div class="kpi-sub">全国城市</div>
            </div>
        </div>
        <div class="kpi-card">
            <div class="kpi-value" style="color:#7c3aed;">{df_base['行业门类'].nunique()}</div>
            <div>
                <div class="kpi-label">行业门类</div>
                <div class="kpi-sub">国民经济分类</div>
            </div>
        </div>
        <div class="kpi-card red">
            <div class="kpi-value" style="color:#dc2626;">{top_sal:,}</div>
            <div>
                <div class="kpi-label">最高薪资中位数</div>
                <div class="kpi-sub">{top_city_sal} · 元/月</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    findings_html = ""
    if not comp_df.empty:
        best = comp_df.sort_values('投资评分', ascending=False).iloc[0]
        findings_html += f'<div class="finding-card"><b>🏆 {best["城市"]}</b><br>投资评分 <b>{best["投资评分"]:.1f} 分</b>，{best["空间格局"]}格局，就业中心 {int(best["就业中心"])} 个</div>'
    active = df_recruit['工作城市'].value_counts()
    if not active.empty:
        findings_html += f'<div class="finding-card"><b>💼 {active.index[0]}</b><br>职位发布量 <b>{active.iloc[0]:,}</b> 个，劳动力需求最旺盛</div>'
    if not industry_df.empty:
        mc = industry_df.loc[industry_df['NNI'].idxmin()]
        findings_html += f'<div class="finding-card"><b>📊 {mc["行业名称"]}</b><br>产业集聚最强 (NNI={mc["NNI"]:.3f})，空间聚集效应显著</div>'

    insights_html = ""
    top3 = comp_df.sort_values('投资评分', ascending=False).head(3)
    cls = ['insight-danger', 'insight-success', 'insight-info']
    for i, (_, row) in enumerate(top3.iterrows()):
        badge = "🔴 高风险" if row['风险等级'] == '高风险' else ("🟢 低风险" if row['风险等级'] == '低风险' else "🟡 中风险")
        insights_html += f'<div class="{cls[i%3]}"><b>{badge} · {row["城市"]}</b><br>NNI={row["NNI"]:.3f} | {row["空间格局"]} | 企业{int(row["企业数"]):,}家 | 薪资{int(row["薪资中位数(元)"]):,}元/月</div>'

    table_html = ""
    if not comp_df.empty:
        display_df = comp_df.sort_values('投资评分', ascending=False)
        table_html += f"""
        <div class="content-card">
            <div class="content-card-header">
                <div class="content-card-icon" style="background:#eff6ff;">📋</div>
                <div>
                    <div class="content-card-title">城市投资评分排行</div>
                    <div class="content-card-sub">综合 NNI · 薪资 · 企业规模 · 空间格局</div>
                </div>
            </div>
        """
        # DataFrame needs to render separately
        table_df = display_df
    else:
        table_df = None

    st.markdown(f"""
    <div class="content-card">
        <div class="content-card-header">
            <div class="content-card-icon" style="background:#eff6ff;">🎯</div>
            <div>
                <div class="content-card-title">核心发现</div>
                <div class="content-card-sub">基于空间计量经济学模型分析</div>
            </div>
        </div>
        {findings_html}
    </div>
    <div class="content-card" style="margin-top:12px;">
        <div class="content-card-header">
            <div class="content-card-icon" style="background:#f0fdf4;">💡</div>
            <div>
                <div class="content-card-title">战略洞察</div>
                <div class="content-card-sub">商业决策建议</div>
            </div>
        </div>
        {insights_html}
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="content-card">
        <div class="content-card-header">
            <div class="content-card-icon" style="background:#eff6ff;">📋</div>
            <div>
                <div class="content-card-title">城市投资评分排行</div>
                <div class="content-card-sub">综合 NNI · 薪资 · 企业规模 · 空间格局</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    if table_df is not None and not table_df.empty:
        # 城市投资评分排行 — 动态高度
        _inv_df = display_df
        _inv_h = max(100, min(len(_inv_df) * 35 + 80, 400))
        st.dataframe(
            _inv_df
            .style.background_gradient(subset=['投资评分'], cmap='Greens')
            .background_gradient(subset=['薪资中位数(元)'], cmap='Blues')
            .format({'薪资中位数(元)': '{:.0f}', '平均注册资本(万)': '{:.0f}', 'NNI': '{:.3f}', 'Moran_I': '{:.4f}'}),
            width='stretch', hide_index=True, height=_inv_h
        )
    st.markdown("</div>", unsafe_allow_html=True)

    ind_dist = df_base['行业门类'].value_counts()
    ind_dist.index = ind_dist.index.map(lambda x: code_to_name.get(x, x))
    fig_tm = px.treemap(
        names=ind_dist.index, parents=[''] * len(ind_dist),
        values=ind_dist.values, color=ind_dist.values,
        color_continuous_scale='Blues'
    )
    fig_tm.update_layout(template='plotly_white', height=280, margin=dict(l=0, r=0, t=0, b=0))
    st.markdown(f"""
    <div class="content-card" style="margin-top:12px;">
        <div class="content-card-header">
            <div class="content-card-icon" style="background:#f0fdf4;">🏭</div>
            <div>
                <div class="content-card-title">行业分布总览</div>
                <div class="content-card-sub">面积 = 企业数量 | 颜色 = 数量梯度</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    st.plotly_chart(fig_tm, width='stretch')
    st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
#  6. 北深苏•行业深度洞察
# ============================================================
elif page == "🏙️ 北深苏·行业深度洞察":
    st.title("📈 行业深度洞察")

    tab_ind, tab_rank, tab_compare = st.tabs(["🏙️ 城市行业分布", "📊 行业集聚排名", "🔬 集聚指标详情"])

    with tab_ind:
        all_cities = sorted(df_base['城市'].dropna().unique().tolist())
        if not all_cities:
            st.warning("暂无城市数据")
        else:
            sel_city = st.selectbox("选择城市", all_cities, key="ind_city")
            c_data = df_base[df_base['城市'] == sel_city]
            ic = c_data['行业门类'].value_counts()
            ic.index = ic.index.map(lambda x: code_to_name.get(x, x))
            ic = ic[ic.index.isin(set(code_to_name.values()))]

            if ic.empty:
                st.warning(f"暂无 {sel_city} 的行业数据")

            col1, col2 = st.columns(2)
        with col1:
            fig = make_subplots(rows=1, cols=2,
                               specs=[[{"type": "bar"}, {"type": "pie"}]],
                               subplot_titles=[f"{sel_city} 行业企业数", f"{sel_city} 行业占比"])
            fig.add_trace(go.Bar(x=ic.head(8).values[::-1], y=ic.head(8).index[::-1],
                                 orientation='h', marker_color='#e94560'), 1, 1)
            fig.add_trace(go.Pie(labels=ic.head(6).index, values=ic.head(6).values,
                                 hole=0.4, marker_colors=['#e94560','#3b82f6','#10b981','#43e97b','#f59e0b','#8b5cf6']), 1, 2)
            fig.update_layout(template='plotly_white', height=400, showlegend=False)
            st.plotly_chart(fig, width='stretch')

        with col2:
            c_recruit = df_merged[df_merged['城市'] == sel_city]
            ind_sal = c_recruit.groupby('行业门类')['薪资'].median().dropna().sort_values(ascending=False)
            ind_sal.index = ind_sal.index.map(lambda x: code_to_name.get(x, x))
            fig2 = go.Figure(go.Bar(
                x=ind_sal.head(8).values / 1000,
                y=ind_sal.head(8).index,
                orientation='h',
                marker_color=ind_sal.head(8).values,
                marker_coloraxis='coloraxis'
            ))
            fig2.update_layout(
                template='plotly_white', showlegend=False, height=400,
                coloraxis_colorbar=dict(title='薪资(k/月)'),
                title=dict(text=f"{sel_city} 行业薪资中位数 (k/月)", x=0.5)
            )
            st.plotly_chart(fig2, width='stretch')

    with tab_rank:
        st.markdown("#### 行业集聚程度综合排名 (NNI — 最近邻指数)")
        ind_rank = industry_df[['城市', '行业编码', '行业名称', '企业数量', 'NNI',
                                '50%集聚半径_km', '主簇集中度', '集聚判定']].copy()
        ind_rank = ind_rank.sort_values('NNI')
        _r = max(120, min(len(ind_rank) * 35 + 80, 400))
        st.dataframe(
            ind_rank.style.background_gradient(subset=['NNI'], cmap='OrRd')
            .background_gradient(subset=['企业数量'], cmap='Blues')
            .format({'NNI': '{:.4f}', '50%集聚半径_km': '{:.1f}', '主簇集中度': '{:.4f}'}),
            width='stretch', hide_index=True, height=_r
        )

        colors = ['#e94560', '#3b82f6', '#10b981', '#f59e0b', '#8b5cf6']
        all_city_colors = {city: colors[i % len(colors)] for i, city in enumerate(industry_df['城市'].unique())}
        fig = px.scatter(
            industry_df, x='企业数量', y='NNI',
            size='50%集聚半径_km', color='城市',
            hover_name='行业名称',
            title="行业集聚: 企业数量 vs NNI (气泡大小=50%集聚半径)",
            color_discrete_map=all_city_colors
        )
        fig.update_layout(template='plotly_white', height=450)
        st.plotly_chart(fig, width='stretch')

    with tab_compare:
        st.markdown("#### 行业详细指标对比")
        sel_ind = st.selectbox("选择行业", list(industry_map.keys())[1:])
        sel_code = industry_map[sel_ind]
        ind_detail = industry_df[industry_df['行业编码'] == sel_code][
            ['城市', 'NNI', '25%集聚半径_km', '50%集聚半径_km', '90%集聚半径_km',
             'Ripley_L峰距_km', '主簇集中度', 'Gi热点数_99%', 'Gi冷点数_99%', '集聚判定']
        ].copy()

        if not ind_detail.empty:
            ind_detail.columns = ['城市', 'NNI', '25%半径', '50%半径', '90%半径',
                                  'Ripley L', '主簇集中度', '热点数', '冷点数', '集聚判定']
            # 用三个紧凑卡片代替大表格
            card_cols = st.columns(3)
            for i, (_, row) in enumerate(ind_detail.iterrows()):
                with card_cols[i]:
                    risk_color = '#dc2626' if row['NNI'] < 0.4 else ('#d97706' if row['NNI'] < 0.6 else '#059669')
                    st.markdown(f"""
                    <div style="background:#f8fafc; border-radius:12px; padding:16px; border:1px solid #e2e8f0;">
                        <div style="font-size:1.1rem; font-weight:800; color:#0f172a; margin-bottom:8px;">{row['城市']}</div>
                        <div style="display:grid; grid-template-columns:1fr 1fr; gap:6px; font-size:0.75rem;">
                            <div><span style="color:#64748b;">NNI</span> <b style="color:{risk_color};">{row['NNI']:.4f}</b></div>
                            <div><span style="color:#64748b;">热点数</span> <b style="color:#dc2626;">{int(row['热点数'])}</b></div>
                            <div><span style="color:#64748b;">50%半径</span> <b style="color:#3b82f6;">{row['50%半径']:.1f}km</b></div>
                            <div><span style="color:#64748b;">冷点数</span> <b style="color:#3b82f6;">{int(row['冷点数'])}</b></div>
                            <div><span style="color:#64748b;">Ripley L</span> <b style="color:#7c3aed;">{row['Ripley L']:.1f}km</b></div>
                            <div><span style="color:#64748b;">集中度</span> <b>{row['主簇集中度']:.3f}</b></div>
                        </div>
                        <div style="margin-top:8px; text-align:center; font-size:0.72rem; color:#059669;
                                    background:#f0fdf4; border-radius:6px; padding:4px;">
                            {row['集聚判定']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

            fig = px.bar_polar(
                ind_detail, r='50%半径', theta='城市',
                title=f"{sel_ind} 50%集聚半径对比",
                color='NNI', color_continuous_scale='RdYlGn',
                template="plotly_dark"
            )
            st.plotly_chart(fig, width='stretch')
        else:
            st.info("暂无该行业的详细数据")

# ============================================================
#  7. 北深苏•投资决策
# ============================================================
elif page == "🏙️ 北深苏·投资决策":
    st.title("💼 投资决策引擎")

    tab_score, tab_risk, tab_tool = st.tabs(["🎯 投资评分", "⚠️ 风险评估", "🛠️ 选址工具"])

    with tab_score:
        all_cities = center_df['城市'].tolist()
        invest_data = []
        for city in all_cities:
            try:
                c_data, c_recruit, cap, crow = city_kpis(city)
            except Exception:
                continue
            large_ratio = len(cap[cap > 1000]) / len(cap) if len(cap) > 0 else 0
            avg_sal = c_recruit['薪资'].median() or 0
            score, risk, rlevel = get_invest_score(city)
            invest_data.append({
                "城市": city,
                "企业总数": len(c_data),
                "大企业占比(%)": round(large_ratio * 100, 1),
                "薪资中位数(元)": round(avg_sal),
                "NNI": round(crow['NNI'], 3),
                "空间格局": crow['最终空间格局'],
                "就业中心数": int(crow['有效簇数']),
                "投资评分": round(score, 1),
                "风险等级": rlevel,
            })

        if invest_data:
            inv_df = pd.DataFrame(invest_data).sort_values('投资评分', ascending=False)

            # 投资矩阵 + 评分表 上下布局
            st.markdown("#### 投资价值矩阵")
            fig = px.scatter(
                inv_df, x='企业总数', y='投资评分',
                size='大企业占比(%)', color='城市',
                hover_name='城市', text='城市',
                size_max=50
            )
            fig.update_traces(textposition='top center', marker=dict(opacity=0.85))
            fig.update_layout(template='plotly_white', height=420, margin=dict(l=0, r=0, t=10, b=0))
            st.plotly_chart(fig, width='stretch')

            st.markdown("#### 综合投资评分排名")
            _sc_h = max(120, min(len(inv_df) * 35 + 80, 400))
            st.dataframe(
                inv_df[['城市', '企业总数', '大企业占比(%)', '薪资中位数(元)', 'NNI',
                        '就业中心数', '投资评分', '风险等级']]
                .style.background_gradient(subset=['投资评分'], cmap='Greens')
                .background_gradient(subset=['大企业占比(%)'], cmap='Blues')
                .format({'薪资中位数(元)': '{:.0f}', 'NNI': '{:.3f}'}),
                width='stretch', hide_index=True, height=_sc_h
            )

            # 推荐卡片
            top3 = inv_df.head(3)
            st.markdown("---")
            st.markdown("#### 🏆 投资推荐 TOP3")
            rec_cols = st.columns(3)
            for i, (_, row) in enumerate(top3.iterrows()):
                with rec_cols[i]:
                    st.markdown(f"""
                    <div style="background:#ffffff; border-radius:16px; padding:20px;
                                border:1px solid #f1f5f9; box-shadow:0 2px 12px rgba(0,0,0,0.06);">
                        <div style="font-size:0.8rem; color:#64748b; text-transform:uppercase; letter-spacing:0.05em;">
                            {'🥇' if i==0 else ('🥈' if i==1 else '🥉')} 第{i+1}名
                        </div>
                        <div style="font-size:1.4rem; font-weight:800; color:#0f172a; margin:6px 0;">
                            {row['城市']}
                        </div>
                        <div style="font-size:2rem; font-weight:900; color:#e94560;">
                            {row['投资评分']}
                        </div>
                        <div style="font-size:0.8rem; color:#64748b;">
                            评分 · {row['空间格局']} · {row['风险等级']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

    with tab_risk:
        all_cities = center_df['城市'].tolist()
        risk_data = []
        for city in all_cities:
            try:
                c_data, c_recruit, cap, crow = city_kpis(city)
            except Exception:
                continue
            score, risk, rlevel = get_invest_score(city)
            factors = []
            if crow['NNI'] < 0.35: factors.append(f"⚠️ NNI={crow['NNI']:.3f}")
            if crow['有效簇数'] == 1: factors.append(f"⚠️ 单核结构")
            if crow['Moran_P'] > 0.05: factors.append(f"⚠️ 空间不显著")
            if crow['Moran_P'] < 0.01: factors.append(f"✅ 强空间聚集")
            if crow['有效簇数'] > 3: factors.append(f"✅ 多核格局")

            risk_data.append({
                "城市": city,
                "有效簇数": int(crow['有效簇数']),
                "NNI": round(crow['NNI'], 3),
                "Moran_I": round(crow['Moran_I'], 4),
                "Moran_P": f"{crow['Moran_P']:.6f}",
                "风险等级": rlevel,
                "主要风险": " | ".join(factors) if factors else "无明显风险"
            })

        if risk_data:
            risk_df = pd.DataFrame(risk_data)
            st.markdown("#### 风险因素分析")
            _rs_h = max(100, min(len(risk_df) * 35 + 80, 400))
            st.dataframe(risk_df, width='stretch', hide_index=True, height=_rs_h)
            st.markdown("#### 风险雷达图")
            categories = ['NNI(倒)', '大企业比', '薪资水平', '多中心性']
            fig = go.Figure()
            colors = ['#e94560', '#3b82f6', '#10b981']
            for i, city in enumerate(all_cities):
                try:
                    c_data, c_recruit, cap, crow = city_kpis(city)
                except Exception:
                    continue
                large_ratio = len(cap[cap > 1000]) / len(cap) if len(cap) > 0 else 0
                avg_sal = c_recruit['薪资'].median() or 0
                values = [
                    (1 - crow['NNI']) * 100,
                    large_ratio * 100,
                    min(avg_sal / 150, 100),
                    min(crow['有效簇数'] * 20, 100)
                ]
                fig.add_trace(go.Scatterpolar(
                    r=values, theta=categories, fill='toself',
                    name=city, line_color=colors[i % len(colors)],
                    fillcolor=colors[i % len(colors)], opacity=0.25
                ))
            fig.update_layout(template='plotly_white', height=380, margin=dict(l=20, r=20, t=30, b=20),
                              polar=dict(angularaxis=dict(color='#8b95a5'),
                                        radialaxis=dict(color='#8b95a5', range=[0, 100])))
            st.plotly_chart(fig, width='stretch')

    with tab_tool:
        st.markdown("#### 🏢 企业选址推荐工具")

        sel_industry = st.selectbox("选择目标行业", list(industry_map.keys())[1:])
        ind_code = industry_map[sel_industry]

        all_cities = center_df['城市'].tolist()
        rec_data = []
        for city in all_cities:
            try:
                c_data, c_recruit, cap, crow = city_kpis(city)
            except Exception:
                continue
            ind_data = c_data[c_data['行业门类'] == ind_code] if ind_code else c_data
            ind_recruit = c_recruit[c_recruit['行业门类'] == ind_code] if ind_code else c_recruit
            large_ratio = len(cap[cap > 1000]) / len(cap) if len(cap) > 0 else 0
            avg_sal = c_recruit['薪资'].median() or 0
            score, risk, rlevel = get_invest_score(city)
            ind_score = len(ind_data) / max(df_base[df_base['行业门类'] == ind_code].groupby('城市').size().max(), 1) * 30
            total = score + ind_score
            rec_data.append({
                "城市": city,
                "该行业企业数": len(ind_data),
                "招聘职位数": len(ind_recruit),
                "薪资中位数": round(avg_sal),
                "空间格局": crow['最终空间格局'],
                "NNI": round(crow['NNI'], 3),
                "投资评分": round(score, 1),
                "综合推荐分": round(total, 1),
                "推荐等级": "⭐⭐⭐" if total > 70 else ("⭐⭐" if total > 50 else "⭐"),
            })

        if rec_data:
            rec_df = pd.DataFrame(rec_data).sort_values('综合推荐分', ascending=False)
            _rc_h = max(120, min(len(rec_df) * 35 + 80, 400))
            st.dataframe(
                rec_df.style.background_gradient(subset=['综合推荐分'], cmap='Greens')
                .background_gradient(subset=['该行业企业数'], cmap='Blues')
                .format({'薪资中位数': '{:.0f}', 'NNI': '{:.3f}'}),
                width='stretch', hide_index=True, height=_rc_h
            )

            best_city = rec_df.iloc[0]['城市']
            best_score = rec_df.iloc[0]['综合推荐分']
            st.success(
                f"🏆 **推荐城市: {best_city}** | 综合推荐分 {best_score} | "
                f"最适合 **{sel_industry}** 企业选址"
            )

# ============================================================
#  10. 北深苏•年度演化
# ============================================================
elif page == "🏙️ 北深苏·年度演化":
    st.title("🏙️ 年度演化")

    if not evolution_df.empty:
        evolution_df['年份'] = pd.to_numeric(evolution_df['年份'], errors='coerce')
        available_years = sorted(evolution_df['年份'].dropna().unique().astype(int).tolist())
        years = [f'{y}年' for y in available_years]
        all_cities = sorted(evolution_df['城市'].dropna().unique().tolist())
        colors = ['#e94560', '#3b82f6', '#10b981', '#f59e0b', '#8b5cf6', '#43e97b']

        for i, city in enumerate(all_cities):
            city_data = evolution_df[evolution_df['城市'] == city].copy()
            if city_data.empty: continue

            city_data = city_data.sort_values('年份')
            ent_vals = city_data['活跃企业数'].tolist()
            den_vals = city_data['中心数量'].tolist()

            while len(ent_vals) < len(years):
                ent_vals.append(0)
                den_vals.append(0)

            color = colors[i % len(colors)]
            st.markdown(f"#### {city} — 年度企业数量变化")
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=years, y=ent_vals,
                mode='lines+markers+text',
                marker=dict(size=12, color=color),
                line=dict(width=3, color=color),
                text=ent_vals, textposition='top center',
                name='企业数量'
            ))
            fig.add_trace(go.Bar(
                x=years, y=den_vals,
                marker_color='rgba(102,126,234,0.2)',
                name='密度级(右轴)'
            ))
            fig.update_layout(
                template='plotly_white', height=350,
                yaxis=dict(title='企业数量'),
                yaxis2=dict(title='密度级', overlaying='y', side='right', showgrid=False)
            )
            st.plotly_chart(fig, width='stretch')

            st.markdown("**年度密度级**")
            den_cols = st.columns(3)
            for j, (y, d) in enumerate(zip(years, den_vals)):
                stars = "⭐" * int(d) if d > 0 else "-"
                with den_cols[j % 3]:
                    st.write(f"{y}: {stars} ({d}级)")

            if len(ent_vals) >= 2 and ent_vals[0] > 0:
                change = (ent_vals[-1] - ent_vals[0]) / ent_vals[0] * 100
                trend = "📈 增长" if change > 0 else "📉 下降"
                st.markdown(f"{trend} **{abs(change):.1f}%** ({available_years[0]}→{available_years[-1]})")
            elif len(ent_vals) == 1:
                st.markdown(f"仅有 **{available_years[0]}年** 数据")
            st.markdown("---")

        st.markdown("#### 各城市企业数量趋势对比")
        fig = go.Figure()
        for i, city in enumerate(all_cities):
            city_data = evolution_df[evolution_df['城市'] == city].copy()
            if city_data.empty: continue
            city_data = city_data.sort_values('年份')
            ent_vals = city_data['活跃企业数'].tolist()
            city_years = [f'{int(y)}年' for y in city_data['年份'].tolist()]
            fig.add_trace(go.Scatter(x=city_years, y=ent_vals, mode='lines+markers',
                                     name=city, line=dict(width=3, color=colors[i % len(colors)]),
                                     marker=dict(size=10)))
        fig.update_layout(template='plotly_white', height=400)
        st.plotly_chart(fig, width='stretch')

        # ---- 演化趋势判断 ----
        evolution_trend_path = f"{RESULT_DIR}/城市演化趋势判断.csv"
        if os.path.exists(evolution_trend_path):
            evolution_trend = pd.read_csv(evolution_trend_path, encoding="utf-8-sig")
            st.markdown("---")
            st.markdown("#### 🔬 城市演化趋势判断")

            trend_data = []
            for _, row in evolution_trend.iterrows():
                trend_data.append({
                    "城市": row['城市'],
                    "周期": f"{row['起始年']}-{row['终止年']}",
                    "中心数变化": row['中心数变化'],
                    "主中心占比变化": row['主中心占比变化'],
                    "迁移距离(km)": f"{row['主中心迁移距离km']:.1f}",
                    "稳定性指数": f"{row['稳定性指数']:.3f}",
                    "趋势判断": row['演化趋势判断'],
                })

            if trend_data:
                trend_df = pd.DataFrame(trend_data)
                _tr_h = max(100, min(len(trend_df) * 35 + 80, 400))
                st.dataframe(trend_df, width='stretch', hide_index=True, height=_tr_h)

                for _, row in evolution_trend.iterrows():
                    trend = row['演化趋势判断']
                    stability = row['稳定性指数']
                    icon = "🔴" if stability < 0.5 else ("🟡" if stability < 0.7 else "🟢")
                    st.markdown(
                        f"**{row['城市']}**: {icon} {trend} "
                        f"(稳定性{stability:.3f}, 主中心迁移{row['主中心迁移距离km']:.1f}km)"
                    )
    else:
        st.info("暂无年度演化数据")

# ============================================================
#  11. 北深苏•企业查询
# ============================================================
elif page == "🏙️ 北深苏·企业查询":
    st.title("🔍 企业查询")

    search_name = st.text_input("输入企业名称关键词", placeholder="例如: 科技、金融...")

    if search_name:
        results = df_base[df_base['企业名称'].str.contains(search_name, na=False)].head(50).copy()
        results['行业中文'] = results['行业门类'].map(code_to_name)
        cap = results['注册资本(万元)'].dropna()
        results['注册资本(万)'] = results['注册资本(万元)'].apply(
            lambda x: f"{x:.0f}" if pd.notna(x) else "N/A"
        )

        st.markdown(f"找到 **{len(results)}** 家相关企业")
        _eq_h = max(120, min(len(results) * 35 + 80, 400))
        st.dataframe(
            results[['企业名称', '城市', '行业中文', '注册资本(万)', '企业状态']],
            width='stretch', hide_index=True, height=_eq_h
        )

        if not results.empty:
            city_dist = results['城市'].value_counts()
            colors = ['#e94560', '#3b82f6', '#10b981', '#f59e0b', '#8b5cf6', '#43e97b']
            pie_colors = {city: colors[i % len(colors)] for i, city in enumerate(city_dist.index)}
            fig = px.pie(city_dist, values=city_dist.values, names=city_dist.index,
                         title=f"'{search_name}' 搜索结果 — 城市分布",
                         hole=0.4,
                         color=city_dist.index,
                         color_discrete_map=pie_colors)
            fig.update_layout(template='plotly_white')
            st.plotly_chart(fig, width='stretch')
    else:
        st.info("👆 请在上方输入企业名称关键词进行查询")

    st.markdown("---")
    st.markdown("#### 行业分布总览")
    ind_dist = df_base['行业门类'].value_counts()
    ind_dist.index = ind_dist.index.map(lambda x: code_to_name.get(x, x))
    fig = px.treemap(
        names=ind_dist.index, parents=[''] * len(ind_dist),
        values=ind_dist.values,
        title="企业行业分布 (面积=企业数量)",
        color=ind_dist.values, color_continuous_scale='Viridis'
    )
    fig.update_layout(template='plotly_white', height=450)
    st.plotly_chart(fig, width='stretch')

# ============================================================
#  12. 北深苏•三城综合对比 (NEW)
# ============================================================
elif page == "🏙️ 北深苏·三城综合对比":
    st.title("⚖️ 北深苏三城综合对比")

    target_cities = ['北京', '苏州', '深圳']
    radar_data = {}

    for city in target_cities:
        c_data = df_base[df_base['城市'] == city]
        c_recruit = df_merged[df_merged['城市'] == city]
        cap = c_data['注册资本(万元)'].dropna()
        cap = cap[(cap > 0) & (cap < 50000)]

        ent_count = len(c_data)
        rec_count = len(c_recruit)
        large_ratio = len(cap[cap > 1000]) / len(cap) if len(cap) > 0 else 0
        avg_sal = c_recruit['薪资'].median() or 0
        ind_diversity = c_data['行业门类'].nunique()
        avg_cap = cap.median() if len(cap) > 0 else 0

        radar_data[city] = {
            '企业密度': min(ent_count / 50, 100),
            '大企业占比': large_ratio * 100,
            '薪资水平': min(avg_sal / 200, 100),
            '行业多样性': ind_diversity * 5,
            '招聘活跃度': min(rec_count / 100, 100),
            '资本实力': min(avg_cap / 200, 100),
        }

    if radar_data:
        st.markdown("#### 三城综合实力对比雷达图")
        categories = list(next(iter(radar_data.values())).keys())
        fig = go.Figure()
        colors = ['#e94560', '#3b82f6', '#10b981']
        for i, (city, vals) in enumerate(radar_data.items()):
            fig.add_trace(go.Scatterpolar(
                r=list(vals.values()),
                theta=categories,
                fill='toself',
                name=city,
                line_color=colors[i],
                fillcolor=colors[i],
                opacity=0.3
            ))
        fig.update_layout(
            template='plotly_white', height=450,
            polar=dict(
                angularaxis=dict(color='#8b95a5'),
                radialaxis=dict(color='#8b95a5', range=[0, 100])
            )
        )
        st.plotly_chart(fig, width='stretch')

        st.markdown("#### 📊 关键指标对比")
        compare_data = []
        for city in target_cities:
                c_data = df_base[df_base['城市'] == city]
                c_recruit = df_merged[df_merged['城市'] == city]
                cap = c_data['注册资本(万元)'].dropna()
                cap = cap[(cap > 0) & (cap < 50000)]

                crow_data = center_df[center_df['城市'] == city]
                nni_val = crow_data['NNI'].values[0] if not crow_data.empty else 0
                clusters = int(crow_data['有效簇数'].values[0]) if not crow_data.empty else 0
                pattern = crow_data['最终空间格局'].values[0] if not crow_data.empty else 'N/A'

                compare_data.append({
                    "城市": city,
                    "企业数": len(c_data),
                    "职位数": len(c_recruit),
                    "行业种类": c_data['行业门类'].nunique(),
                    "薪资中位数(元)": int(c_recruit['薪资'].median() or 0),
                    "大企业占比(%)": round(len(cap[cap > 1000]) / len(cap) * 100, 1) if len(cap) > 0 else 0,
                    "NNI": round(nni_val, 3),
                    "就业中心": clusters,
                    "空间格局": pattern,
                })

        if compare_data:
            cmp_df = pd.DataFrame(compare_data)
            # 三城用指标卡片代替表格
            card_cols = st.columns(3)
            for i, (_, row) in enumerate(cmp_df.iterrows()):
                with card_cols[i]:
                    risk_col = '#dc2626' if row['NNI'] < 0.4 else ('#d97706' if row['NNI'] < 0.6 else '#059669')
                    st.markdown(f"""
                    <div style="background:#f8fafc; border-radius:12px; padding:16px; border:1px solid #e2e8f0; text-align:center;">
                        <div style="font-size:1.2rem; font-weight:800; color:#0f172a; margin-bottom:10px;">{row['城市']}</div>
                        <div style="font-size:2rem; font-weight:900; color:#e94560; margin-bottom:4px;">{row['企业数']:,}</div>
                        <div style="color:#64748b; font-size:0.72rem; margin-bottom:10px;">家企业</div>
                        <div style="display:grid; grid-template-columns:1fr 1fr; gap:8px; font-size:0.75rem; text-align:left;">
                            <div><span style="color:#94a3b8;">NNI</span><br><b style="color:{risk_col};">{row['NNI']}</b></div>
                            <div><span style="color:#94a3b8;">薪资中位数</span><br><b style="color:#059669;">{row['薪资中位数(元)']:,}</b></div>
                            <div><span style="color:#94a3b8;">就业中心</span><br><b>{row['就业中心']}个</b></div>
                            <div><span style="color:#94a3b8;">大企业占比</span><br><b>{row['大企业占比(%)']}%</b></div>
                        </div>
                        <div style="margin-top:8px; font-size:0.72rem; color:#7c3aed;
                                    background:#f5f3ff; border-radius:6px; padding:4px;">
                            {row['空间格局']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("#### 🏆 各城市优势行业 TOP3")
        cols = st.columns(3)
        for i, city in enumerate(target_cities):
            with cols[i]:
                c_recruit = df_merged[df_merged['城市'] == city]
                ind_counts = c_recruit['行业门类'].value_counts().head(3)
                ind_counts.index = ind_counts.index.map(lambda x: code_to_name.get(x, x))
                st.markdown(f"**{city}**")
                for idx, (ind, cnt) in enumerate(ind_counts.items()):
                    medal = ['🥇', '🥈', '🥉'][idx]
                    st.markdown(f"{medal} {ind}: {cnt} 职位")
    else:
        st.info("暂无三城对比数据")

# ============================================================
#  12. 薪酬分析
# ============================================================
elif page == "💰 薪酬与竞争":
    st.title("💰 薪酬与竞争格局")

    tab_sal, tab_comp, tab_require = st.tabs(["💵 薪资对比", "📊 行业竞争指数", "🎓 招聘要求"])

    sal_by_city = df_recruit.groupby('工作城市')['薪资'].agg(['median', 'count', 'max', 'std']).dropna()
    sal_by_city = sal_by_city[sal_by_city['count'] > 5].sort_values('median', ascending=False)

    with tab_sal:
        sal_df = sal_by_city.head(15).reset_index()
        sal_df['median'] = sal_df['median'].astype(int)
        sal_df['max'] = sal_df['max'].astype(int)
        sal_df['std'] = sal_df['std'].astype(int)
        fig = px.bar(
            sal_df,
            x='工作城市', y='median',
            title="各城市薪资中位数 TOP15 (元/月)",
            color='median', color_continuous_scale='RdYlGn',
            error_y=sal_by_city.head(15)['std'].values / 3
        )
        fig.update_layout(template='plotly_white', yaxis=dict(tickformat=',d'))
        st.plotly_chart(fig, width='stretch')

        st.markdown("#### 薪资统计表")
        st.dataframe(
            sal_by_city.head(15).rename(columns={
                'median': '薪资中位数', 'count': '样本数', 'max': '最高薪资', 'std': '标准差'
            }),
            width='stretch', hide_index=True
        )

    with tab_comp:
        st.markdown("#### 行业竞争指数分析")
        st.markdown("**竞争指数 = 行业企业数 / 招聘职位数，越高表示竞争越激烈**")

        city_sal_stats, ind_sal_stats, _ = compute_city_salary_stats()
        comp_data = []
        for ind_code, ind_name in code_to_name.items():
            ind_ent = df_base[df_base['行业门类'] == ind_code]
            ind_rec = df_merged[df_merged['行业门类'] == ind_code]
            ent_count = len(ind_ent)
            rec_count = len(ind_rec)
            if rec_count < 10:
                continue
            comp_index = round(ent_count / max(rec_count, 1), 2)
            # CR5: top 5 cities' share
            city_counts = ind_ent['城市'].value_counts()
            cr5 = round(city_counts.head(5).sum() / city_counts.sum() * 100, 1) if not city_counts.empty else 0
            med_sal = ind_rec['薪资'].median() or 0
            comp_data.append({
                "行业": ind_name,
                "企业数": ent_count,
                "职位数": rec_count,
                "竞争指数": comp_index,
                "CR5集中度(%)": cr5,
                "薪资中位数(元)": int(med_sal),
            })

        if comp_data:
            comp_df_viz = pd.DataFrame(comp_data).sort_values('竞争指数', ascending=False)
            fig_comp = px.scatter(
                comp_df_viz, x='CR5集中度(%)', y='竞争指数',
                size='薪资中位数(元)', color='行业',
                hover_name='行业', title="行业竞争格局 (X=集中度, Y=竞争指数, 气泡=薪资)",
                size_max=50
            )
            fig_comp.update_layout(template='plotly_white', height=450)
            st.plotly_chart(fig_comp, width='stretch')

            st.markdown("**竞争指数排名**")
            st.dataframe(
                comp_df_viz.style.background_gradient(subset=['竞争指数'], cmap='Reds')
                .background_gradient(subset=['CR5集中度(%)'], cmap='Blues'),
                width='stretch', hide_index=True
            )
        else:
            st.info("暂无足够的竞争分析数据")

    with tab_require:
        edu = df_recruit['学历'].value_counts()
        exp = df_recruit['工作年限'].value_counts()

        col1, col2 = st.columns(2)
        with col1:
            fig = px.pie(edu, values=edu.values, names=edu.index,
                         title="学历要求分布", hole=0.5,
                         color=edu.index,
                         color_discrete_map={'大专': '#e94560', '本科': '#3b82f6',
                                            '硕士': '#10b981', '博士': '#f59e0b', '不限': '#94a3b8'})
            fig.update_layout(template='plotly_white')
            st.plotly_chart(fig, width='stretch')
        with col2:
            fig = px.bar(exp, x=exp.index, y=exp.values,
                         title="工作经验要求分布",
                         color=exp.values, color_continuous_scale='Viridis')
            fig.update_layout(template='plotly_white')
            st.plotly_chart(fig, width='stretch')

        st.markdown("#### 高薪职位 TOP15")
        top15 = df_merged.nlargest(15, '薪资')[
            ['城市', '薪水范围', '行业门类', '学历', '工作年限']
        ].copy()
        top15['行业'] = top15['行业门类'].map(code_to_name)
        st.dataframe(top15[['城市', '薪水范围', '行业', '学历', '工作年限']],
                     width='stretch', hide_index=True)

# ============================================================
#  13. 全国人才流动网络
# ============================================================
elif page == "🌐 全国人才流动网络":
    st.title("🌐 全国人才流动网络分析")

    # 从预生成 CSV 拿基础指标（招聘企业数/职位总数等），薪资从统一函数覆盖
    raw_city_stats, city_industry, flow_df = load_nationwide_data(RESULT_DIR)
    unified_city_sal, _, _ = compute_city_salary_stats()
    # 用统一薪资替换 CSV 中的薪资（保持列名兼容）
    city_stats = raw_city_stats.drop(columns=['薪资中位数', '平均薪资', '薪资标准差'], errors='ignore')
    city_stats = city_stats.merge(
        unified_city_sal[['城市', '薪资中位数', '平均薪资', '薪资标准差', '样本数']],
        on='城市', how='left'
    )

    tab1, tab2, tab3 = st.tabs(["🕸️ 人才流动网络", "🗺️ 城市分布地图", "📊 吸引力指数"])

    with tab1:
        st.markdown("#### 人才流动网络")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**桑基图：人才从企业所在地流向岗位所在地**")
            fig_sankey = plot_talent_flow_sankey(flow_df, top_n=20)
            if fig_sankey:
                st.plotly_chart(fig_sankey, width="stretch")
            else:
                st.info("暂无桑基图数据")

        with col2:
            st.markdown("**热力矩阵：城市间双向人才流动**")
            fig_chord = plot_chord_diagram(flow_df)
            if fig_chord:
                st.plotly_chart(fig_chord, width="stretch")
            else:
                st.info("暂无弦图数据")

    with tab2:
        st.markdown("#### 全国城市人才分布地图")

        # KPI展示
        kpi_col1, kpi_col2, kpi_col3 = st.columns(3)
        with kpi_col1:
            st.metric("覆盖城市", len(city_stats))
        with kpi_col2:
            top_city = city_stats.iloc[0]['城市'] if not city_stats.empty else "N/A"
            st.metric("职位最多城市", top_city)
        with kpi_col3:
            avg_sal = city_stats['薪资中位数'].mean() if '薪资中位数' in city_stats.columns else 0
            st.metric("平均薪资中位数", f"{avg_sal:,.0f} 元/月" if avg_sal else "N/A")

        st.markdown("---")
        st.markdown("**气泡地图：气泡大小=职位数，颜色=吸引力指数（红>60，橙40-60，蓝<40）**")

        # 绘制气泡地图
        m = plot_talent_bubble_map(city_stats)
        if m:
            st_folium(m, width='100%', height=550)
        else:
            st.info("暂无地图数据")

    with tab3:
        st.markdown("#### 城市人才吸引力指数")

        st.markdown("""
        **人才吸引力指数** = 岗位密度(50%) + 薪资水平(30%) + 行业多样性(20%)
        """)

        fig_attraction = plot_attraction_index(city_stats, top_n=20)
        if fig_attraction:
            st.plotly_chart(fig_attraction, width='stretch')
        else:
            st.info("暂无吸引力指数数据")

        st.markdown("---")
        st.markdown("#### 行业多样性排名")

        fig_diversity = plot_industry_diversity(city_stats, top_n=20)
        if fig_diversity:
            st.plotly_chart(fig_diversity, width='stretch')
        else:
            st.info("暂无多样性数据")

        st.markdown("""
        <div class="insight-success">
        <b>💡 商业洞察</b>：<br>
        • <b>北京</b>凭借信息技术和科学技术服务的高薪资，位居吸引力榜首<br>
        • <b>深圳</b>在金融业和信息技术领域具有竞争优势<br>
        • <b>苏州</b>以制造业和批发零售为主，岗位丰富度较高
        </div>
        """, unsafe_allow_html=True)

# ============================================================
#  13. 全国产业地图
# ============================================================
elif page == "🗼 全国产业地图":
    st.title("🗼 全国产业地图")

    # 薪资数据从统一函数获取，行业矩阵从原函数获取（共用同一套 extract_salary / extract_city）
    city_sal, ind_sal, city_ind_salary = compute_city_salary_stats()
    _, city_industry, _ = load_nationwide_data(RESULT_DIR)

    tab_ind1, tab_ind2, tab_ind3 = st.tabs(["🏙️ 城市-行业热力图", "💼 行业薪资排名", "📈 城市行业分布"])

    with tab_ind1:
        st.markdown("#### 城市-行业招聘热力图")

        st.markdown("**热力图说明**：颜色越深表示该城市该行业的招聘职位越多")

        fig_heatmap = plot_city_industry_heatmap(city_industry, top_n=20)
        if fig_heatmap:
            st.plotly_chart(fig_heatmap, width='stretch')
        else:
            st.info("暂无热力图数据")

        st.markdown("---")

        # 按行业筛选查看
        st.markdown("#### 按行业查看城市分布")
        sel_industry = st.selectbox("选择行业", city_industry['行业'].unique().tolist())

        ind_data = city_industry[city_industry['行业'] == sel_industry].copy()
        ind_data = ind_data.sort_values('职位数', ascending=False).head(15)

        if not ind_data.empty:
            fig = px.bar(
                ind_data, x='城市', y='职位数',
                title=f"{sel_industry} 行业 - 城市招聘职位数 TOP15",
                color='职位数', color_continuous_scale='YlOrRd'
            )
            fig.update_layout(template='plotly_white', xaxis_tickangle=-45)
            st.plotly_chart(fig, width='stretch')

    with tab_ind2:
        st.markdown("#### 行业薪资排名")

        st.markdown("**行业薪资排名（按中位数）**")

        if not ind_sal.empty:
            ind_sal_int = ind_sal.head(15).copy()
            ind_sal_int['薪资中位数'] = ind_sal_int['薪资中位数'].astype(int)
            fig = px.bar(
                ind_sal_int, x='行业', y='薪资中位数',
                title="行业薪资中位数 TOP15 (元/月)",
                color='薪资中位数', color_continuous_scale='RdYlGn',
                text='薪资中位数'
            )
            fig.update_layout(template='plotly_white', xaxis_tickangle=-45, yaxis=dict(tickformat=',d'))
            st.plotly_chart(fig, width='stretch')

        st.markdown("---")
        st.markdown("#### 城市-行业薪资矩阵")

        _mat = city_ind_salary
        if not _mat.empty:
            _display = _mat.loc[
                _mat.sum(axis=1).sort_values(ascending=False).head(15).index
            ]
            fig = px.imshow(
                _display.values,
                x=_display.columns,
                y=_display.index,
                color_continuous_scale='RdYlGn',
                title="城市-行业薪资中位数矩阵 (元/月)",
                labels=dict(x="行业", y="城市", color="薪资"),
                text_auto=True
            )
            fig.update_layout(height=500, xaxis_tickangle=45)
            st.plotly_chart(fig, width='stretch')

    with tab_ind3:
        st.markdown("#### 重点城市行业分布")

        sel_city = st.selectbox("选择城市查看行业分布", ['北京', '上海', '深圳', '广州', '杭州', '苏州', '成都', '重庆'])

        city_ind = city_industry[city_industry['城市'] == sel_city].copy()
        city_ind = city_ind.sort_values('职位数', ascending=False).head(10)

        if not city_ind.empty:
            col1, col2 = st.columns(2)

            with col1:
                fig = px.pie(
                    city_ind, values='职位数', names='行业',
                    title=f"{sel_city} 行业分布",
                    hole=0.4
                )
                fig.update_layout(template='plotly_white')
                st.plotly_chart(fig, width="stretch")

            with col2:
                fig = px.bar(
                    city_ind, x='行业', y='职位数',
                    title=f"{sel_city} 行业职位数",
                    color='职位数', color_continuous_scale='YlOrRd'
                )
                fig.update_layout(template='plotly_white', xaxis_tickangle=-45)
                st.plotly_chart(fig, width="stretch")

        st.markdown("""
        <div class="insight-success">
        <b>💡 城市产业特征</b>：<br>
        • <b>北京</b>：信息技术、科学技术服务、租赁商务服务占主导<br>
        • <b>上海</b>：金融业、信息技术、批发零售均衡发展<br>
        • <b>深圳</b>：批发零售、信息技术、制造业并重<br>
        • <b>苏州</b>：制造业、科学技术服务、批发零售为核心
        </div>
        """, unsafe_allow_html=True)

# ============================================================
#  15. 增长潜力榜 (NEW)
# ============================================================
elif page == "📈 增长潜力":
    st.title("📈 城市增长潜力评估")

    city_sal_stats, _, _ = compute_city_salary_stats()

    growth_data = []
    all_cities = sorted(df_merged['工作城市'].dropna().unique().tolist())
    for city in all_cities:
        c_data = df_merged[df_merged['工作城市'] == city]
        ent_count = c_data['企业名称'].nunique()
        rec_count = len(c_data)
        if rec_count < 20 or ent_count == 0:
            continue

        avg_sal = c_data['薪资'].median() or 0
        ind_diversity = c_data['行业门类'].dropna().nunique()

        ent_rec_ratio = min(ent_count / max(rec_count, 1), 2)
        sal_score = min(avg_sal / 30000 * 100, 100)
        div_score = min(ind_diversity / 20 * 100, 100)
        ratio_score = (1 / ent_rec_ratio if ent_rec_ratio > 0 else 0) * 100
        growth_score = div_score * 0.4 + sal_score * 0.35 + ratio_score * 0.25

        lat, lon = CITY_COORDS.get(city, (None, None))
        growth_data.append({
            "城市": city,
            "招聘企业数": ent_count,
            "职位数": rec_count,
            "行业种类": ind_diversity,
            "薪资中位数(元)": int(avg_sal),
            "增长潜力指数": round(growth_score, 1),
            "潜力等级": "🟢 高" if growth_score > 65 else ("🟡 中" if growth_score > 40 else "🔴 待观察"),
            "纬度": lat,
            "经度": lon,
        })

    if growth_data:
        growth_df = pd.DataFrame(growth_data).sort_values('增长潜力指数', ascending=False)

        # KPI cards
        k1, k2, k3, k4 = st.columns(4)
        with k1:
            st.metric("评估城市数", len(growth_df))
        with k2:
            st.metric("平均潜力指数", f"{growth_df['增长潜力指数'].mean():.1f}")
        with k3:
            top_city = growth_df.iloc[0]
            st.metric("🏆 潜力榜首", top_city['城市'], f"{top_city['增长潜力指数']:.0f}")
        with k4:
            high_count = (growth_df['增长潜力指数'] > 65).sum()
            st.metric("高潜力城市", f"{high_count}个")

        st.markdown("---")

        # 地图 + 榜单 两栏布局
        col_map, col_rank = st.columns([3, 2])

        with col_map:
            st.markdown("#### 🗺️ 全国城市增长潜力分布图")
            st.markdown("*气泡越大 = 增长潜力越高 · 颜色越亮 = 薪资越高*")

            geo_df = growth_df.dropna(subset=['纬度', '经度']).copy()
            if not geo_df.empty:
                m = folium.Map(
                    location=[35.86, 104.19],
                    zoom_start=3,
                    tiles='CartoDB positron',
                    prefer_canvas=True
                )
                for _, row in geo_df.iterrows():
                    score = row['增长潜力指数']
                    radius = max(score * 200, 10000)
                    color = '#e94560' if score > 65 else ('#f59e0b' if score > 40 else '#3b82f6')
                    folium.CircleMarker(
                        location=[row['纬度'], row['经度']],
                        radius=min(score / 5, 18),
                        popup=f"<b>{row['城市']}</b><br>潜力指数: {score}<br>薪资: {row['薪资中位数(元)']:,}元<br>企业: {row['招聘企业数']}家",
                        color=color,
                        fill=True,
                        fillColor=color,
                        fillOpacity=0.7,
                        weight=2
                    ).add_to(m)
                st_folium(m, width='100%', height=500)
            else:
                st.info("暂无地图坐标数据")

        with col_rank:
            st.markdown("#### 📊 增长潜力 TOP15")
            fig = px.bar(
                growth_df.head(15).sort_values('增长潜力指数'),
                x='增长潜力指数', y='城市',
                orientation='h',
                title="城市增长潜力排名",
                color='增长潜力指数', color_continuous_scale='RdYlGn',
                text='增长潜力指数'
            )
            fig.update_traces(textposition='outside', textfont_size=11)
            fig.update_layout(template='plotly_white', height=500, showlegend=False,
                              margin=dict(l=0, r=20, t=40, b=0))
            st.plotly_chart(fig, width='stretch')

        st.markdown("---")

        # 详情表格 + 矩阵
        col_tbl, col_mat = st.columns([3, 2])
        with col_tbl:
            st.markdown("#### 📋 增长潜力详情")
            st.dataframe(
                growth_df[['城市', '招聘企业数', '职位数', '行业种类',
                           '薪资中位数(元)', '增长潜力指数', '潜力等级']]
                .head(20)
                .style.background_gradient(subset=['增长潜力指数'], cmap='Greens')
                .background_gradient(subset=['薪资中位数(元)'], cmap='Blues'),
                width='stretch', hide_index=True
            )

        with col_mat:
            st.markdown("#### 🎯 行业多样性·薪资矩阵")
            fig2 = px.scatter(
                growth_df.head(30), x='行业种类', y='薪资中位数(元)',
                size='招聘企业数', color='增长潜力指数',
                hover_name='城市',
                title="增长潜力矩阵",
                color_continuous_scale='RdYlGn', size_max=40
            )
            fig2.update_layout(template='plotly_white', height=380, margin=dict(l=0, r=0, t=40, b=0))
            st.plotly_chart(fig2, width='stretch')

        st.markdown("---")

        # 洞察卡片
        insight_cols = st.columns(3)
        with insight_cols[0]:
            st.markdown("""
            <div style="background:#f0fdf4; border-left:4px solid #10b981; border-radius:8px;
                        padding:16px; height:100%;">
            <b style="color:#059669;">🏙️ 多元化城市</b><br>
            <span style="color:#065f46; font-size:0.85rem;">
            行业多样性高的城市抗风险能力强，<br>适合长期战略性投资布局
            </span>
            </div>
            """, unsafe_allow_html=True)

        with insight_cols[1]:
            st.markdown("""
            <div style="background:#eff6ff; border-left:4px solid #3b82f6; border-radius:8px;
                        padding:16px; height:100%;">
            <b style="color:#1d4ed8;">💰 薪酬引力</b><br>
            <span style="color:#1e3a5f; font-size:0.85rem;">
            高薪资城市吸引高端人才，<br>适合技术密集型产业落地
            </span>
            </div>
            """, unsafe_allow_html=True)

        with insight_cols[2]:
            st.markdown("""
            <div style="background:#fef3c7; border-left:4px solid #f59e0b; border-radius:8px;
                        padding:16px; height:100%;">
            <b style="color:#b45309;">⚡ 供需红利</b><br>
            <span style="color:#78350f; font-size:0.85rem;">
            企业/职位比低的城市竞争较小，<br>人才获取成本更低
            </span>
            </div>
            """, unsafe_allow_html=True)

    else:
        st.info("暂无足够的增长数据")

# ============================================================
# Footer
# ============================================================
st.markdown(f"""
<div class="site-footer">
    <div class="footer-title">🏭 中国产业地图 · 商业决策支持系统</div>
    <div style="color:#64748b; font-size:0.78rem; line-height:1.8;">
        本系统基于企业招聘数据与空间计量经济学方法，为商业选址与投资决策提供数据支撑
    </div>
    <div class="footer-row">
        <div class="footer-item">
            <strong>分析方法</strong><br>
            最近邻指数 (NNI) · Moran I · Ripley's K · 聚类分析
        </div>
        <div class="footer-item">
            <strong>数据来源</strong><br>
            企业基础信息 · 招聘行为数据 · 国民经济行业分类
        </div>
        <div class="footer-item">
            <strong>分析维度</strong><br>
            产业集聚 · 人才流动 · 薪酬格局 · 年度演化
        </div>
    </div>
    <div style="margin-top:20px; padding-top:16px; border-top:1px solid rgba(255,255,255,0.06);
                color:#475569; font-size:0.72rem;">
        应用统计案例大赛 · {__import__('datetime').date.today().year}
    </div>
</div>
""", unsafe_allow_html=True)
