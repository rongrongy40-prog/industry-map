"""
重设计的全国城市数据处理模块
优化薪资计算，专注商业分析
"""

import pandas as pd
import numpy as np
import re

DATA_DIR = r"d:\project\应用统计案例大赛\原始数据\行业码表+三类企业数据集"
RESULT_DIR = r"d:\project\应用统计案例大赛\分析结果"

CITY_COORDS = {
    '北京': (39.90, 116.41), '上海': (31.23, 121.47), '深圳': (22.54, 114.06),
    '广州': (23.13, 113.26), '杭州': (30.27, 120.16), '南京': (32.06, 118.80),
    '苏州': (31.30, 120.59), '成都': (30.57, 104.07), '重庆': (29.43, 106.91),
    '武汉': (30.59, 114.31), '西安': (34.34, 108.94), '天津': (39.34, 117.36),
    '青岛': (36.07, 120.38), '长沙': (28.23, 112.94), '郑州': (34.75, 113.63),
    '宁波': (29.87, 121.54), '大连': (38.91, 121.61), '无锡': (31.49, 120.31),
    '东莞': (23.05, 113.75), '佛山': (23.02, 113.12), '昆山': (31.39, 120.75),
}

DISTRICT_MAP = {
    '海淀区': '北京', '朝阳区': '北京', '丰台区': '北京', '西城区': '北京', '东城区': '北京',
    '通州区': '北京', '昌平区': '北京', '大兴区': '北京', '顺义区': '北京', '房山区': '北京',
    '浦东新区': '上海', '闵行区': '上海', '徐汇区': '上海', '黄浦区': '上海', '静安区': '上海',
    '南山区': '深圳', '福田区': '深圳', '龙华区': '深圳', '宝安区': '深圳', '光明区': '深圳',
    '龙岗区': '深圳', '罗湖区': '深圳', '天河区': '广州', '白云区': '广州',
    '工业园区': '苏州', '姑苏区': '苏州', '吴中区': '苏州', '相城区': '苏州', '虎丘区': '苏州',
}

INDUSTRY_MAP = {
    'C': '制造业', 'E': '建筑业', 'F': '批发零售', 'G': '住宿餐饮', 'H': '交通运输',
    'I': '信息技术', 'J': '金融业', 'K': '房地产业', 'L': '租赁商务服务',
    'M': '科学技术服务', 'N': '水利环境', 'O': '居民服务', 'P': '教育',
    'Q': '卫生社会', 'R': '文体娱乐',
}


def extract_salary_v2(s):
    """改进的薪资解析函数，处理各种格式"""
    if pd.isna(s):
        return None
    s = str(s).strip().replace(',', '').replace(' ', '').replace('元', '').replace('月', '')

    # 去除后缀
    s = re.sub(r'·\d+薪$', '', s)
    s = re.sub(r'·\d+个月$', '', s)

    unit = 1

    # 判断单位
    if '万/' in s:
        unit = 10000
        s = re.sub(r'万', '', s)
    elif '千/' in s:
        unit = 1000
        s = re.sub(r'千', '', s)
    elif 'k/' in s.lower() or 'K' in s:
        unit = 1000
        s = re.sub(r'[kK]', '', s)

    # 提取数字
    nums = re.findall(r'\d+(?:\.\d+)?', s)
    if not nums:
        return None
    nums = [float(n) for n in nums]

    # 如果有范围，取中值
    if len(nums) >= 2:
        val = (nums[0] + nums[1]) / 2 * unit
    else:
        val = nums[0] * unit

    # 合理性过滤：月薪应该在3000-80000之间
    if val < 3000 or val > 80000:
        return None
    return val


def extract_city(loc):
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


def process_data():
    print("加载招聘数据...")
    df_recruit = pd.read_csv(f"{DATA_DIR}/2. 企业招聘行为表.csv", encoding="utf-8-sig", low_memory=False)
    df_base = pd.read_csv(f"{DATA_DIR}/1. 企业基础信息.csv", encoding="utf-8-sig", low_memory=False)

    print(f"招聘数据: {len(df_recruit)} 条")

    # 提取城市和薪资
    df_recruit['工作城市'] = df_recruit['工作地点'].apply(extract_city)
    df_recruit['薪资'] = df_recruit['薪水范围'].apply(extract_salary_v2)

    # 合并行业信息
    df_merged = df_recruit.merge(
        df_base[['企业名称', '行业门类']].drop_duplicates('企业名称'),
        on='企业名称', how='left'
    )
    df_merged['行业'] = df_merged['行业门类'].map(INDUSTRY_MAP)

    df_valid = df_merged[df_merged['工作城市'].notna() & df_merged['薪资'].notna()].copy()

    print(f"有效数据(有城市+有薪资): {len(df_valid)} 条")
    print(f"涉及城市数: {df_valid['工作城市'].nunique()}")

    # ========== 1. 城市统计 ==========
    print("\n生成城市统计...")
    city_stats = df_valid.groupby('工作城市').agg({
        '企业名称': 'nunique',
        '职位名称': 'count',
        '薪资': ['mean', 'median', 'std', lambda x: np.percentile(x, 25), lambda x: np.percentile(x, 75)]
    })
    city_stats.columns = ['招聘企业数', '职位总数', '平均薪资', '薪资中位数', '薪资标准差', '25分位', '75分位']
    city_stats = city_stats.reset_index()
    city_stats.columns = ['城市', '招聘企业数', '职位总数', '平均薪资', '薪资中位数', '薪资标准差', '25分位', '75分位']

    city_stats['纬度'] = city_stats['城市'].map(lambda x: CITY_COORDS.get(x, (None, None))[0])
    city_stats['经度'] = city_stats['城市'].map(lambda x: CITY_COORDS.get(x, (None, None))[1])

    # 行业多样性（信息熵）
    def calc_entropy(group):
        counts = group['行业门类'].value_counts(normalize=True)
        entropy = -(counts * np.log(counts + 1e-10)).sum()
        return entropy
    entropy_df = df_valid.groupby('工作城市').apply(calc_entropy, include_groups=False).reset_index()
    entropy_df.columns = ['城市', '行业多样性指数']
    city_stats = city_stats.merge(entropy_df, on='城市', how='left')

    # 人才吸引力指数（归一化）
    max_jobs = city_stats['职位总数'].max()
    max_sal = city_stats['薪资中位数'].max()
    max_ent = city_stats['行业多样性指数'].max()

    city_stats['岗位得分'] = (city_stats['职位总数'] / max_jobs * 40).round(1)
    city_stats['薪资得分'] = (city_stats['薪资中位数'] / max_sal * 40).round(1)
    city_stats['多样性得分'] = (city_stats['行业多样性指数'] / max_ent * 20).round(1)
    city_stats['人才吸引力指数'] = (city_stats['岗位得分'] + city_stats['薪资得分'] + city_stats['多样性得分']).round(1)

    city_stats = city_stats.sort_values('人才吸引力指数', ascending=False)
    city_stats.to_csv(f"{RESULT_DIR}/城市统计_新.csv", index=False, encoding="utf-8-sig")
    print(f"已保存: 城市统计_新.csv ({len(city_stats)} 个城市)")

    # ========== 2. 城市-行业薪资矩阵 ==========
    print("\n生成城市-行业薪资矩阵...")
    city_ind = df_valid.groupby(['工作城市', '行业'])['薪资'].agg(['count', 'median', 'mean']).reset_index()
    city_ind.columns = ['城市', '行业', '样本数', '薪资中位数', '平均薪资']
    city_ind = city_ind[city_ind['样本数'] >= 5]  # 至少5个样本
    city_ind.to_csv(f"{RESULT_DIR}/城市行业薪资_新.csv", index=False, encoding="utf-8-sig")

    # ========== 3. 行业薪资排名 ==========
    print("\n生成行业薪资排名...")
    ind_sal = df_valid.groupby('行业').agg({
        '薪资': ['count', 'mean', 'median'],
        '职位名称': 'count'
    }).reset_index()
    ind_sal.columns = ['行业', '样本数', '平均薪资', '薪资中位数', '职位数']
    ind_sal = ind_sal[ind_sal['样本数'] >= 20]
    ind_sal = ind_sal.sort_values('薪资中位数', ascending=False)
    ind_sal.to_csv(f"{RESULT_DIR}/行业薪资排名_新.csv", index=False, encoding="utf-8-sig")

    # ========== 4. 城市间人才流动 ==========
    print("\n生成人才流动矩阵...")
    df_base['城市'] = df_base['城市代码'].map({110000: '北京', 320500: '苏州', 440300: '深圳'})
    df_flow = df_valid.merge(df_base[['企业名称', '城市']].drop_duplicates(), on='企业名称', how='left')
    df_flow['企业城市'] = df_flow['城市']

    flow = df_flow[df_flow['企业城市'].notna()].groupby(['企业城市', '工作城市']).size().reset_index(name='人数')
    flow.columns = ['来源', '目标', '人数']
    flow = flow[flow['人数'] >= 5]
    flow.to_csv(f"{RESULT_DIR}/人才流动_新.csv", index=False, encoding="utf-8-sig")

    # ========== 5. 城市-行业招聘矩阵 ==========
    city_job = df_valid.pivot_table(index='工作城市', columns='行业', values='职位名称', aggfunc='count', fill_value=0)
    city_job.to_csv(f"{RESULT_DIR}/城市行业招聘_新.csv", encoding="utf-8-sig")

    print("\n" + "=" * 50)
    print("数据处理完成!")
    print("=" * 50)

    # 输出薪资统计验证
    print("\n薪资统计验证:")
    for city in ['北京', '上海', '深圳', '苏州', '广州', '杭州']:
        data = df_valid[df_valid['工作城市'] == city]['薪资']
        if len(data) > 0:
            print(f"  {city}: 中位数={data.median():.0f}, 均值={data.mean():.0f}, 样本={len(data)}")

    return city_stats, city_ind, ind_sal, flow


if __name__ == "__main__":
    city_stats, city_ind, ind_sal, flow = process_data()

    print("\n城市吸引力 TOP 10:")
    print(city_stats[['城市', '职位总数', '薪资中位数', '人才吸引力指数']].head(10).to_string(index=False))

    print("\n行业薪资 TOP 10:")
    print(ind_sal[['行业', '薪资中位数', '样本数']].head(10).to_string(index=False))
