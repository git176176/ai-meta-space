# AI Meta Space - 后端 API

## 技术栈

- Python 3.8+
- FastAPI
- SQLAlchemy + MySQL
- JWT 认证
- WebSocket（待实现）

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

创建 `.env` 文件：

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=ai_meta_space

SECRET_KEY=your-secret-key-change-in-production

MINIMAX_API_KEY=your_minimax_api_key
```

### 3. 创建数据库

```sql
CREATE DATABASE ai_meta_space CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 4. 运行服务

```bash
# 开发模式
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 生产模式（使用 PM2）
pm2 start "uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4" --name ai-meta-space
```

## API 文档

启动服务后访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 目录结构

```
app/
├── __init__.py
├── main.py              # FastAPI 入口
├── core/
│   ├── config.py         # 配置
│   ├── database.py       # 数据库连接
│   └── security.py       # JWT 认证
├── models/
│   └── models.py         # 数据库模型
├── schemas/
│   └── schemas.py        # Pydantic 模型
└── api/
    ├── auth.py           # 认证接口
    ├── chat.py           # 对话接口
    ├── brain.py           # 智囊接口
    ├── feedback.py        # 反馈接口
    └── admin.py           # 管理后台接口
```

## 主要接口

### 认证
- `POST /api/v1/auth/register` - 用户注册
- `POST /api/v1/auth/login` - 用户登录
- `POST /api/v1/auth/refresh` - 刷新 Token
- `GET /api/v1/auth/me` - 获取当前用户

### 对话
- `POST /api/v1/chat/sessions` - 创建会话
- `GET /api/v1/chat/sessions` - 会话列表
- `POST /api/v1/chat/session/{id}/message` - 发送消息
- `DELETE /api/v1/chat/session/{id}` - 删除会话

### 智囊
- `POST /api/v1/brain/tasks` - 创建任务
- `GET /api/v1/brain/tasks` - 任务列表
- `POST /api/v1/brain/task/{id}/execute` - 执行任务

### 反馈
- `POST /api/v1/feedback` - 提交反馈
- `GET /api/v1/feedback/my` - 我的反馈

### 管理后台
- `GET /api/v1/admin/stats` - 运营统计
- `GET /api/v1/admin/users` - 用户列表
