# Wuxi Art Web – Backend

小巧的 Flask 服务，为前端页面提供景点与详情数据。数据默认保存在 `data/spots.json` 中，方便课堂演示或小规模内容管理。

## 快速开始

```powershell
# 初始化虚拟环境并安装依赖
./start.ps1

# 启动开发服务器
./run.ps1
```

服务器默认监听 `http://127.0.0.1:5000`，前端可以通过以下接口获取数据：

- `GET /api/health`：健康检查
- `GET /api/spots`：获取景点列表（含总数）
- `GET /api/spots/<spot_id>`：获取指定景点详情
- `POST /api/spots`：创建或覆盖景点，需要 JSON 请求体，至少包含 `id`、`name`
- `PUT /api/spots/<spot_id>`：更新景点（同样接受整个 JSON 结构）
- `DELETE /api/spots/<spot_id>`：删除景点

接口返回 JSON，已内置简易 CORS 头部，方便前端静态页面直接通过 `fetch` 访问。

## 后台录入页面

- `GET /admin/spots/new`：录入景点基础信息，包含 ID、名称、摘要、头图、标签等。提交成功后自动跳转到详情段落录入页。
- `GET /admin/spots/<spot_id>/details/new`：为指定景点添加图文段落，支持逐段保存并实时查看已添加的内容。

页面使用原生 HTML 表单提交，无需额外前端框架，适合课堂演示或快速填充数据。

## 数据结构

`data/spots.json` 中的示例：

```json
{
  "spots": [
    {
      "id": "yuantouzhu",
      "name": "鼋头渚",
      "location": "无锡 · 太湖",
      "summary": "樱花与太湖交织的湖光山色，四季皆景。",
      "heroImage": "https://...",
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
  ]
}
```

你可以直接编辑该文件，或通过 `POST`/`PUT` 接口动态维护内容。应用会在读取/写入时自动创建文件夹并保持线程安全。
