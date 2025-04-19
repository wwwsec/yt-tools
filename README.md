# YouTube API Service

一个基于 Flask 的 YouTube API 服务，提供获取 YouTube 频道视频和字幕的功能。

## 功能特性

- 获取 YouTube 频道的所有视频 ID（包括播放列表中的视频）
- 获取 YouTube 视频的字幕（支持手动字幕和自动字幕）
- 支持多种语言的字幕获取
- 支持纯文本格式的字幕输出
- RESTful API 接口
- 统一的错误处理机制

## 项目结构

```
app/
├── __init__.py
├── config.py          # 配置管理
├── errors.py          # 错误处理
├── services/          # 服务层
│   ├── __init__.py
│   ├── channel_service.py    # 频道相关服务
│   └── subtitle_service.py   # 字幕相关服务
├── routes/            # 路由层
│   ├── __init__.py
│   └── api.py         # API 路由定义
└── main.py            # 应用入口
```

## 安装步骤

1. 克隆项目：
```bash
git clone <repository-url>
cd <project-directory>
```

2. 创建虚拟环境（推荐）：
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

3. 安装依赖：
```bash
pip install -r requirements.txt
```

## 运行服务

```bash
python -m app.main
```

服务将在 `http://localhost:5000` 启动。

## API 文档

### 获取频道视频

获取指定 YouTube 频道的所有视频 ID。

**请求：**
```
GET /api/channel/videos?channel_id=<channel_id>
```

**参数：**
- `channel_id` (必需): YouTube 频道 ID

**响应：**
```json
{
    "status": "success",
    "count": 100,
    "videos": ["video_id1", "video_id2", ...]
}
```

### 获取视频字幕

获取指定 YouTube 视频的字幕。

**请求：**
```
GET /api/subtitles?video_id=<video_id>&lang=<lang>&pure_text=<pure_text>
```

**参数：**
- `video_id` (必需): YouTube 视频 ID
- `lang` (可选): 字幕语言代码，默认为 "en"
- `pure_text` (可选): 是否只返回纯文本，默认为 false

**响应：**
```json
{
    "status": "success",
    "data": {
        "video_id": "video_id",
        "subtitles": {
            "en": "subtitle text..."
        }
    }
}
```

## 错误处理

所有 API 接口都使用统一的错误处理机制：

- 400: 参数错误
- 500: 服务错误

错误响应格式：
```json
{
    "status": "error",
    "error": "错误信息"
}
```

## 依赖项

- Flask: Web 框架
- yt-dlp: YouTube 视频和字幕下载
- Python 3.6+

## 注意事项

1. 需要安装 Firefox 浏览器以支持字幕下载功能
2. 某些视频可能没有字幕或自动字幕
3. 频道视频获取可能会受到 YouTube API 限制

## 贡献

欢迎提交 Issue 和 Pull Request。

## 许可证

MIT License 