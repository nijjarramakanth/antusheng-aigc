# AIGC 教育智慧系统

## 📱 快速开始

### 前置要求
- Python 3.11+
- pip（Python包管理器）

### 安装步骤

1. **克隆仓库**
```bash
git clone https://github.com/nijjarramakanth/antusheng-aigc.git
cd antusheng-aigc
```

2. **创建虚拟环境**
```bash
python -m venv venv
source venv/bin/activate  # Mac/Linux
# 或
venv\\Scripts\\activate  # Windows
```

3. **安装依赖**
```bash
pip install -r requirements.txt
```

4. **配置环境**
```bash
cp .env.example .env
# 编辑 .env 文件，添加你的 Google API Key
```

5. **启动服务器**
```bash
python app.py
```

6. **打开浏览器**
访问：`http://localhost:5000/index.html`

---

## 🎯 核心功能

### 学员功能
- ✅ 用户注册和登录
- ✅ 查看教师发布的任务
- ✅ 提交作业
- ✅ 浏览100+提示词库
- ✅ 查看批改反馈

### 教师功能
- ✅ 发布和管理任务
- ✅ 查看学员提交
- ✅ 批改作业和评分
- ✅ 查看统计数据

---

## 📚 API 文档

### 认证
- `POST /api/auth/register` - 注册
- `POST /api/auth/login` - 登录
- `GET /api/auth/me` - 获取当前用户

### 任务
- `GET /api/assignments/` - 获取所有任务
- `POST /api/assignments/` - 创建任务（教师）

### 提交
- `GET /api/submissions/` - 获取提交
- `POST /api/submissions/` - 提交作业

### 反馈
- `POST /api/feedback/` - 创建反馈（教师）
- `GET /api/feedback/<id>` - 获取反馈

### 提示词库
- `GET /api/prompts/` - 获取所有提示词
- `GET /api/prompts/?category=<category>` - 按分类过滤
- `GET /api/prompts/?difficulty=<difficulty>` - 按难度过滤

---

## 📊 数据库

使用 SQLite（开发环境）或 PostgreSQL（生产环境）

主要表：
- users - 用户表
- assignments - 任务表
- submissions - 提交表
- feedbacks - 反馈表
- prompts - 提示词表

---

## 🔑 获取 Google API Key

1. 访问 https://ai.google.dev
2. 点击 "Get API Key"
3. 复制 API Key
4. 粘贴到 `.env` 文件

---

## 🐳 Docker 部署

```bash
docker-compose up -d
```

---

## 📝 许可证

MIT License
