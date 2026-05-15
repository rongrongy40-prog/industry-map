# 中国产业地图 - 商业决策支持系统

基于 Python Streamlit 的交互式数据可视化平台，分析全国城市人才流动、薪资分布和产业集聚情况。

**在线访问**: https://your-username.streamlit.app (部署后替换)

---

## 本地运行

```bash
pip install -r requirements.txt
streamlit run visualization.py
```

然后打开浏览器访问 http://localhost:8501

---

## 部署到 Streamlit Cloud (免费)

### 准备工作

1. **GitHub 账号**: https://github.com
2. **Streamlit Cloud 账号**: https://streamlit.io/cloud (用 GitHub 账号登录)

### 步骤

#### 1. 创建 GitHub 仓库

1. 打开 https://github.com/new
2. 仓库名称填写 `industry-map-dashboard` (或你喜欢的名字)
3. 选择 **Public** (公开仓库，Streamlit Cloud 才能访问)
4. 不要勾选 "Add a README file" (稍后上传)
5. 点击 **Create repository**

#### 2. 上传代码到 GitHub

**方法 A - 使用 GitHub 网页 (最简单)**

1. 在刚创建的空仓库页面，点击 **"uploading an existing file"**
2. 把 `第四问可视化系统` 文件夹里的**所有内容**拖入上传区域
3. 确保包含以下文件：
   - `visualization.py`
   - `talent_flow_viz.py`
   - `nationwide_data_analysis.py`
   - `requirements.txt`
   - `.streamlit/config.toml`
   - `.gitignore`
   - `data/` 文件夹
   - `result/` 文件夹
4. 拉到页面底部，点击 **Commit changes**

**方法 B - 使用 Git 命令行**

```bash
cd 第四问可视化系统
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/你的用户名/industry-map-dashboard.git
git push -u origin main
```

#### 3. 部署到 Streamlit Cloud

1. 打开 https://streamlit.io/cloud
2. 点击 **New app**
3. 配置部署：
   - **Repository**: 选择你刚创建的仓库 (例如 `your-username/industry-map-dashboard`)
   - **Branch**: `main`
   - **Main file path**: `visualization.py`
4. 点击 **Deploy!**

#### 4. 等待部署完成

- 首次部署需要 2-5 分钟安装依赖
- 部署成功后，你会获得一个链接：`https://your-app-name.streamlit.app`
- 点击链接即可在浏览器中访问

#### 5. 分享链接

部署成功后，把 `https://your-app-name.streamlit.app` 这个链接分享给别人，他们就可以直接看到可视化页面了。

---

## 目录结构

```
第四问可视化系统/
├── visualization.py              # 主应用入口
├── talent_flow_viz.py            # 全国人才流动可视化模块
├── nationwide_data_analysis.py   # 数据处理模块
├── requirements.txt               # Python 依赖
├── .streamlit/
│   └── config.toml               # Streamlit 配置
├── .gitignore
├── data/                         # 原始数据
│   ├── 1. 企业基础信息.csv
│   └── 2. 企业招聘行为表.csv
└── result/                       # 分析结果
    ├── 全国城市统计表.csv
    ├── 城市行业招聘_新.csv
    ├── 人才流动_新.csv
    └── ...
```

---

## 注意事项

- Streamlit Cloud 每次部署会重新安装 `requirements.txt` 中的所有依赖
- 免费版 Streamlit Cloud 同一时间只能运行一个应用
- 如果代码有更新，只需 `git push` 到 GitHub，Streamlit Cloud 会自动重新部署
- 确保 `data/` 和 `result/` 文件夹中的 CSV 文件都已包含在仓库中
