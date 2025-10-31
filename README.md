# Wuxi Art Web

一个结合前后端的数字媒体课堂项目，展现無錫城市景观的虚实交织。前端使用 Tailwind CSS 打造沉浸式体验，后端由 Flask 提供景点数据接口和简易录入页面，数据存储在 JSON 文件中，便于快速演示与扩展。

## 功能亮点
- 动态首页：`frontend/index.html` 通过 `fetch` 拉取景点列表，生成非对称卡片布局。
- 详情页：`frontend/spot-minimal-detail.html` 根据 URL 参数加载指定景点，保持图文交错的段落呈现。
- 管理后台：提供景点基础信息与段落录入表单，适合课堂或小规模内容维护。
- 轻量存储：`backend/data/spots.json` 保存所有景点数据，支持直接编辑或通过 API 更新。
- 一键脚本：`start.ps1` 和 `run.ps1` 帮助快速创建虚拟环境、安装依赖并启动服务。

## 目录结构
```
Wuxi_Art_Web/
├─ README.md            # 当前说明文档
├─ .gitignore
├─ backend/             # Flask 后端
│  ├─ app.py            # 主应用，提供 API 和后台页面
│  ├─ storage.py        # JSON 文件读写工具
│  ├─ data/spots.json   # 景点数据源
│  ├─ templates/admin/  # 管理后台模板
│  ├─ start.ps1         # 初始化虚拟环境并安装依赖
│  └─ run.ps1           # 启动开发服务器
└─ frontend/            # 静态前端页面
   ├─ index.html        # 首页，展示景点列表
   └─ spot-minimal-detail.html # 景点详情页
```

## 环境要求
- Python 3.10 及以上版本（建议启用虚拟环境）
- PowerShell 5.1 或更高版本（用于运行脚本）
- 现代浏览器（Chrome、Edge 等）

## 快速开始
1. 打开 PowerShell，切换至项目目录：
   ```powershell
   Set-Location Wuxi_Art_Web\backend
   ```
2. 初始化虚拟环境并安装依赖：
   ```powershell
   ./start.ps1
   ```
3. 启动开发服务器：
   ```powershell
   ./run.ps1
   ```
   默认监听 `http://127.0.0.1:5000`。
4. 在浏览器中直接打开 `frontend/index.html` 或使用 VS Code Live Server 等本地服务查看页面。前端会自动访问本地后端接口。

## API 速览
- `GET /api/health` 健康检查
- `GET /api/spots` 获取景点列表（含总数）
- `GET /api/spots/<spot_id>` 获取指定景点详情
- `POST /api/spots` 新建或覆盖景点（JSON 请求体需包含 `id`、`name` 等字段）
- `PUT /api/spots/<spot_id>` 更新现有景点
- `DELETE /api/spots/<spot_id>` 删除景点

所有接口返回 JSON，并自动附带基础 CORS 头，方便静态页面调用。详情页还支持通过 `spot-minimal-detail.html?id=<spot_id>&apiBase=<可选接口根路径>` 指定数据源。

## 数据维护
- 推荐使用后台页面：
  - `/admin/spots/new` 录入景点基础信息
  - `/admin/spots/<spot_id>/details/new` 补充图文段落
- 若需手动编辑数据，可直接修改 `backend/data/spots.json`。结构示例：
  ```json
  {
    "id": "yuantouzhu",
    "name": "鼋头渚",
    "summary": "樱花与太湖交织的湖光山色，四季皆景。",
    "heroImage": "https://...",
    "tags": ["自然奇观", "太湖风景"],
    "detailSections": [
      {
        "title": "樱花漫过湖面时",
        "emphasis": "时间会慢下来",
        "paragraphs": ["..."],
        "image": "https://...",
        "imageAlt": "樱花"
      }
    ]
  }
  ```
- 为避免多人协作冲突，编辑 JSON 后建议运行 `git diff` 检查格式，并通过接口验证内容是否能正常加载。

## 常见问题
- **前端加载失败**：确认后端已启动，且浏览器未被跨域或 Mixed Content 限制；必要时在 URL 中添加 `?apiBase=http://127.0.0.1:5000`。
- **图片占位符**：当前使用示例图片，可替换为实际资源 URL 或部署静态资产服务器。
- **依赖更新**：新增依赖后请在 `backend/requirements.txt` 中补充，并重新运行 `pip install -r requirements.txt`。

若有新的景点或改动，可先通过后台表单录入，再检查前端展示效果，确保交互与布局符合预期。
