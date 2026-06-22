# 鲜知 fridge · AI 冰箱管家 — 全面设计规范与开发流程

> 版本：v1.0  
> 日期：2026-06-17  
> 状态：待确认

---

## 目录

1. [项目架构设计](#1-项目架构设计)
2. [技术栈选型](#2-技术栈选型)
3. [文件目录结构](#3-文件目录结构)
4. [代码规范](#4-代码规范)
5. [接口设计标准](#5-接口设计标准)
6. [数据库设计](#6-数据库设计)
7. [开发环境配置](#7-开发环境配置)
8. [版本控制策略](#8-版本控制策略)
9. [测试策略](#9-测试策略)
10. [部署流程](#10-部署流程)

---

## 1. 项目架构设计

### 1.1 整体架构

采用 **前后端分离 + AI 服务层** 的三层架构：

```
┌─────────────────────────────────────────────────┐
│                   前端 (React)                    │
│   路由 / 状态管理 / UI组件 / API调用 / 本地缓存     │
└────────────────────┬────────────────────────────┘
                     │ REST API (JSON)
┌────────────────────▼────────────────────────────┐
│                后端 (FastAPI)                     │
│   路由层 → 服务层 → 数据访问层                     │
│   认证中间件 / 限流 / 日志 / 异常处理               │
└────────┬───────────────────┬────────────────────┘
         │                   │
┌────────▼────────┐  ┌───────▼────────┐
│   数据库(SQLite) │  │   AI 服务层     │
│   SQLAlchemy ORM │  │ 多模态识别+LLM  │
└─────────────────┘  └────────────────┘
```

### 1.2 后端分层

```
Router（路由层）  →  接收请求、参数校验、返回响应
  ↓
Service（服务层）  →  业务逻辑编排
  ↓
Repository（数据层）→  数据库 CRUD
  ↓
Model（模型层）    →  ORM 定义
```

### 1.3 AI 服务层

- **图像识别**：调用多模态大模型（如 OpenAI GPT-4o / 智谱 GLM-4V）识别冰箱照片中的食材
- **菜谱生成**：调用 LLM 根据库存食材生成菜谱、步骤、营养分析
- **降级策略**：AI 不可用时回退到本地规则引擎（基于食材关键词匹配预设菜谱库）

---

## 2. 技术栈选型

### 2.1 前端

| 类别 | 技术 | 版本 | 说明 |
|------|------|------|------|
| 框架 | React | 18.x | 与参考项目一致，组件生态成熟 |
| 构建工具 | Vite | 5.x | 极速 HMR，与参考项目一致 |
| UI 组件库 | Ant Design | 5.x | 与参考项目一致 |
| 路由 | React Router | 6.x | 标准路由方案 |
| HTTP 客户端 | Axios | 1.x | 与参考项目一致 |
| 状态管理 | React Context + useReducer | - | 轻量级，Demo 阶段足够 |
| 图表 | ECharts | 5.x | 营养洞察可视化 |
| 测试 | Vitest + Testing Library | - | 单元测试 |
| E2E 测试 | Playwright | - | 端到端测试 |
| Lint | ESLint | 8.x | 代码规范 |

### 2.2 后端

| 类别 | 技术 | 版本 | 说明 |
|------|------|------|------|
| Web 框架 | FastAPI | 0.104+ | 异步高性能，自动生成 OpenAPI 文档 |
| ASGI 服务器 | Uvicorn | 0.24+ | 标准 ASGI 服务器 |
| ORM | SQLAlchemy | 2.0+ | 异步 ORM |
| 数据库 | SQLite (开发) / PostgreSQL (生产) | - | 开发零配置，生产可切换 |
| 迁移工具 | Alembic | 1.13+ | 数据库版本管理 |
| 数据验证 | Pydantic | 2.x | 请求/响应模型校验 |
| 认证 | python-jose + passlib | - | JWT 双 Token 认证 |
| AI SDK | openai | 1.x | 调用多模态大模型 |
| Lint | Ruff | 0.4+ | 替代 flake8/isort/black |
| 安全扫描 | Bandit | 1.7+ | Python SAST |
| 测试 | pytest + pytest-asyncio | - | 异步测试 |

### 2.3 基础设施

| 类别 | 技术 | 说明 |
|------|------|------|
| 容器化 | Docker + docker-compose | 一键启动全栈 |
| CI/CD | GitHub Actions | 自动测试、构建、部署 |
| 代码质量 | pre-commit | 提交前自动检查 |
| 静态部署 | GitHub Pages | 前端 Demo 可独立部署 |

---

## 3. 文件目录结构

```
fridge-manager-demo/
├── backend/                          # 后端代码
│   ├── alembic/                      # 数据库迁移
│   │   ├── versions/                 # 迁移脚本
│   │   └── env.py
│   ├── routers/                      # 路由层（按功能模块拆分）
│   │   ├── __init__.py
│   │   ├── auth.py                   # 认证路由
│   │   ├── ingredients.py            # 食材管理路由
│   │   ├── recipes.py                # 菜谱推荐路由
│   │   ├── recognition.py            # 图像识别路由
│   │   └── nutrition.py              # 营养分析路由
│   ├── services/                     # 服务层（业务逻辑）
│   │   ├── __init__.py
│   │   ├── ingredient_service.py     # 食材管理逻辑
│   │   ├── recipe_service.py         # 菜谱推荐逻辑
│   │   ├── recognition_service.py    # AI 图像识别逻辑
│   │   └── nutrition_service.py      # 营养分析逻辑
│   ├── models/                       # 数据模型层
│   │   ├── __init__.py
│   │   ├── database.py               # 数据库连接与 Base
│   │   ├── user.py                   # 用户模型
│   │   ├── ingredient.py             # 食材模型
│   │   └── recipe.py                 # 菜谱模型
│   ├── schemas/                      # Pydantic 请求/响应模型
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── ingredient.py
│   │   ├── recipe.py
│   │   └── common.py                 # 通用响应模型
│   ├── core/                         # 核心配置
│   │   ├── __init__.py
│   │   ├── config.py                 # 环境配置
│   │   ├── security.py               # JWT/密码哈希
│   │   └── exceptions.py             # 自定义异常
│   ├── tests/                        # 后端测试
│   │   ├── conftest.py               # pytest fixtures
│   │   ├── test_auth.py
│   │   ├── test_ingredients.py
│   │   ├── test_recipes.py
│   │   └── test_recognition.py
│   ├── alembic.ini
│   ├── main.py                       # 应用入口
│   ├── pyproject.toml                # Ruff/Bandit 配置
│   ├── requirements.txt
│   └── requirements-test.txt
│
├── frontend/                         # 前端代码
│   ├── public/
│   │   └── favicon.ico
│   ├── src/
│   │   ├── api/                      # API 调用层
│   │   │   ├── client.js             # Axios 实例
│   │   │   ├── auth.js               # 认证 API
│   │   │   ├── ingredients.js        # 食材 API
│   │   │   └── recipes.js            # 菜谱 API
│   │   ├── components/               # 通用组件
│   │   │   ├── Layout.jsx            # 页面布局
│   │   │   ├── IngredientCard.jsx    # 食材卡片
│   │   │   ├── RecipeCard.jsx        # 菜谱卡片
│   │   │   ├── UploadPanel.jsx       # 拍照上传
│   │   │   ├── NutritionChart.jsx    # 营养图表
│   │   │   └── ShoppingList.jsx      # 购物清单
│   │   ├── pages/                    # 页面组件
│   │   │   ├── HomePage.jsx          # 主页（冰箱看板）
│   │   │   ├── RecipesPage.jsx       # 菜谱推荐页
│   │   │   └── NutritionPage.jsx     # 营养洞察页
│   │   ├── contexts/                 # Context 状态管理
│   │   │   └── AppContext.jsx        # 全局状态
│   │   ├── hooks/                    # 自定义 Hooks
│   │   │   └── useIngredients.js
│   │   ├── styles/                   # 全局样式
│   │   │   └── theme.js              # Ant Design 主题
│   │   ├── utils/                    # 工具函数
│   │   │   └── helpers.js
│   │   ├── App.jsx                   # 根组件
│   │   ├── main.jsx                  # 入口
│   │   └── config.js                 # 前端配置
│   ├── tests/                        # 前端测试
│   │   ├── setup.js
│   │   ├── HomePage.test.jsx
│   │   └── RecipeCard.test.jsx
│   ├── e2e/                          # E2E 测试
│   │   └── smoke.spec.js
│   ├── index.html
│   ├── vite.config.js
│   ├── vitest.config.js
│   ├── playwright.config.js
│   ├── .eslintrc.cjs
│   └── package.json
│
├── .github/
│   └── workflows/
│       ├── ci.yml                    # CI 流水线
│       └── deploy.yml                # GitHub Pages 部署
│
├── docs/                             # 文档
│   ├── DESIGN_SPEC.md                # 本文档
│   └── API.md                        # API 文档
│
├── .gitignore
├── .pre-commit-config.yaml
├── Dockerfile
├── docker-compose.yml
├── README.md
└── legacy-demo.html                  # 原静态 Demo（已归档，不再作为首页）
```

---

## 4. 代码规范

### 4.1 Python 后端规范

**工具：Ruff（lint + format）+ Bandit（安全扫描）**

```toml
# pyproject.toml
[tool.ruff]
target-version = "py310"
line-length = 120

[tool.ruff.lint]
select = ["E", "W", "F", "I", "N", "UP", "B", "C4", "SIM", "S"]
ignore = ["E501", "B008", "S101"]

[tool.ruff.format]
quote-style = "double"
indent-style = "space"

[tool.bandit]
exclude_dirs = ["tests", "__pycache__"]
skips = ["B101"]
```

**命名规范：**
- 类名：`PascalCase`（如 `IngredientService`）
- 函数/变量：`snake_case`（如 `get_ingredients_by_user`）
- 常量：`UPPER_SNAKE_CASE`（如 `MAX_LOGIN_ATTEMPTS`）
- 私有方法：`_leading_underscore`
- Pydantic 模型：`PascalCase` + 语义后缀（如 `IngredientCreateRequest`）

**异步规范：**
- 所有数据库操作和外部 API 调用使用 `async/await`
- 路由函数统一使用 `async def`
- 使用 `AsyncSession` 而非同步 Session

**异常处理：**
- 业务异常继承自定义 `AppException`
- 路由层捕获异常并转换为 HTTPException
- 不裸露 `except:`，必须记录日志

### 4.2 JavaScript/React 前端规范

**工具：ESLint + Prettier**

```json
// .eslintrc.cjs
{
  "extends": ["eslint:recommended", "plugin:react/recommended", "plugin:react-hooks/recommended"],
  "rules": {
    "react/prop-types": "off",
    "no-unused-vars": "warn",
    "indent": ["error", 2],
    "quotes": ["error", "single"],
    "semi": ["error", "always"]
  }
}
```

**命名规范：**
- 组件文件名：`PascalCase.jsx`（如 `IngredientCard.jsx`）
- 组件名：`PascalCase`（如 `IngredientCard`）
- 函数/变量：`camelCase`（如 `fetchIngredients`）
- 常量：`UPPER_SNAKE_CASE`（如 `API_BASE_URL`）
- CSS 类名：`kebab-case`（如 `ingredient-card`）
- Hook：`use` 前缀（如 `useIngredients`）

**组件规范：**
- 函数组件 + Hooks，不使用 class 组件
- Props 必须有默认值或可选标注
- 组件文件单一职责，一个文件一个组件
- 使用 Ant Design 组件作为基础，不重复造轮子

### 4.3 Git 提交规范

采用 **Conventional Commits**：

```
<type>(<scope>): <subject>

<body>

<footer>
```

**type 列表：**
| type | 说明 |
|------|------|
| feat | 新功能 |
| fix | Bug 修复 |
| docs | 文档变更 |
| style | 代码格式（不影响逻辑） |
| refactor | 重构 |
| test | 测试相关 |
| chore | 构建/工具/依赖 |
| ci | CI/CD 变更 |

**示例：**
```
feat(ingredients): 添加食材批量导入接口
fix(auth): 修复 refresh token 过期未清理问题
docs(api): 更新菜谱接口文档
```

---

## 5. 接口设计标准

### 5.1 RESTful 规范

- 基础路径：`/api/v1`
- 资源用名词复数：`/api/v1/ingredients`
- HTTP 方法语义：GET 查询、POST 创建、PUT 更新、DELETE 删除
- 分页参数：`?page=1&page_size=20`
- 排序参数：`?sort=-created_at`（负号降序）

### 5.2 统一响应格式

**成功响应：**
```json
{
  "code": 0,
  "message": "success",
  "data": { ... }
}
```

**分页响应：**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [...],
    "total": 100,
    "page": 1,
    "page_size": 20
  }
}
```

**错误响应：**
```json
{
  "code": 40001,
  "message": "食材不存在",
  "detail": "Ingredient with id=xxx not found"
}
```

**错误码定义：**
| 范围 | 说明 |
|------|------|
| 0 | 成功 |
| 40001-40099 | 参数校验错误 |
| 40101-40199 | 认证错误 |
| 40301-40399 | 权限错误 |
| 40401-40499 | 资源不存在 |
| 50001-50099 | 服务器内部错误 |

### 5.3 核心接口列表

#### 认证模块
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/v1/auth/register | 用户注册 |
| POST | /api/v1/auth/login | 用户登录 |
| POST | /api/v1/auth/refresh | 刷新 Token |
| POST | /api/v1/auth/logout | 登出 |
| GET | /api/v1/auth/me | 当前用户信息 |

#### 食材管理
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/v1/ingredients | 获取食材列表 |
| POST | /api/v1/ingredients | 添加食材 |
| PUT | /api/v1/ingredients/{id} | 更新食材 |
| DELETE | /api/v1/ingredients/{id} | 删除食材 |
| GET | /api/v1/ingredients/expiring | 获取临期食材 |

#### AI 识别
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/v1/recognition/recognize | 上传图片识别食材 |

#### 菜谱推荐
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/v1/recipes/recommend | 根据食材推荐菜谱 |
| GET | /api/v1/recipes/{id} | 获取菜谱详情 |

#### 营养分析
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/v1/nutrition/summary | 营养摄入统计 |

### 5.4 认证机制

- **JWT 双 Token**：Access Token（15 分钟）+ Refresh Token（7 天）
- 请求头：`Authorization: Bearer <access_token>`
- Token 撤销：黑名单机制
- 登录失败限制：5 次失败后锁定 15 分钟

---

## 6. 数据库设计

### 6.1 ER 关系

```
User (1) ──< (N) Ingredient
User (1) ──< (N) Recipe
Ingredient (N) >──< (N) Recipe  (通过 recipe_ingredients 关联表)
```

### 6.2 表结构

#### users
| 字段 | 类型 | 说明 |
|------|------|------|
| user_id | VARCHAR PK | UUID |
| username | VARCHAR UNIQUE | 用户名 |
| email | VARCHAR UNIQUE | 邮箱 |
| hashed_password | VARCHAR | bcrypt 哈希 |
| is_active | BOOLEAN | 是否启用 |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

#### ingredients
| 字段 | 类型 | 说明 |
|------|------|------|
| ingredient_id | VARCHAR PK | UUID |
| user_id | VARCHAR FK | 所属用户 |
| name | VARCHAR | 食材名称 |
| category | VARCHAR | 分类：vegetable/meat/dairy/staple/fruit/other |
| quantity | INTEGER | 数量 |
| unit | VARCHAR | 单位：个/袋/瓶/块 |
| storage_location | VARCHAR | 存放位置：fridge/freezer/crisper/pantry |
| purchase_date | DATE | 购买日期 |
| expiry_date | DATE | 保质期 |
| image_url | VARCHAR | 图片 URL（可选） |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

#### recipes
| 字段 | 类型 | 说明 |
|------|------|------|
| recipe_id | VARCHAR PK | UUID |
| name | VARCHAR | 菜名 |
| description | TEXT | 简介 |
| cook_time | INTEGER | 烹饪时间（分钟）|
| calories | INTEGER | 热量（kcal）|
| servings | INTEGER | 份数 |
| steps | JSON | 步骤数组 |
| image_url | VARCHAR | 图片 URL |
| source | VARCHAR | 来源：ai/local |
| created_at | DATETIME | 创建时间 |

#### recipe_ingredients（关联表）
| 字段 | 类型 | 说明 |
|------|------|------|
| recipe_id | VARCHAR FK | 菜谱 ID |
| ingredient_name | VARCHAR | 食材名称 |
| amount | VARCHAR | 用量 |
| is_required | BOOLEAN | 是否必需 |

---

## 7. 开发环境配置

### 7.1 环境要求

- Python 3.10+
- Node.js 20+
- Git 2.30+

### 7.2 后端环境

```bash
# 创建虚拟环境
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# 安装依赖
cd backend
pip install -r requirements.txt
pip install -r requirements-test.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 填入 API Key 等

# 初始化数据库
alembic upgrade head

# 启动开发服务器
uvicorn main:app --reload --port 8000
```

### 7.3 前端环境

```bash
cd frontend
npm install
npm run dev  # 默认 http://localhost:3000
```

### 7.4 环境变量

```env
# backend/.env.example

# 数据库
DATABASE_TYPE=sqlite
DATABASE_URL=sqlite+aiosqlite:///./data/fridge.db

# JWT
JWT_SECRET_KEY=your-secret-key-here
JWT_EXPIRE_MINUTES=15
JWT_REFRESH_EXPIRE_DAYS=7

# AI 服务（至少配置一个）
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o
# 或
ZHIPU_API_KEY=
ZHIPU_MODEL=glm-4v

# 应用
ENVIRONMENT=development
LOG_LEVEL=INFO
CORS_ORIGINS=http://localhost:3000
```

### 7.5 Docker 一键启动

```bash
docker-compose up -d
# 前端：http://localhost:3000
# 后端：http://localhost:8000
# API 文档：http://localhost:8000/docs
```

---

## 8. 版本控制策略

### 8.1 分支模型

采用 **GitHub Flow**（轻量级，适合中小项目）：

```
main          ────●────●────●────●────●────
                      \         /
feature/xxx            ●───●───●
```

| 分支 | 说明 |
|------|------|
| main | 生产分支，始终可部署 |
| feature/* | 功能分支，从 main 切出 |
| fix/* | 修复分支 |
| hotfix/* | 紧急修复，从 main 切出，合并回 main |

### 8.2 分支命名

```
feature/ingredient-crud
feature/ai-recognition
fix/login-token-expiry
hotfix/cors-error
```

### 8.3 PR 规范

- PR 标题遵循 Conventional Commits 格式
- PR 描述包含：变更说明、测试方式、影响范围
- 至少 1 人 Review 后合并
- 合并方式：Squash merge（保持 main 历史整洁）

### 8.4 .gitignore 关键项

```
# Python
__pycache__/
*.pyc
.venv/

# Node
node_modules/
dist/

# 环境
.env
.env.local

# 数据
data/
*.db

# IDE
.idea/
.vscode/

# 测试
.coverage
htmlcov/
.pytest_cache/
coverage/
```

### 8.5 pre-commit 钩子

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.4.4
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]
      - id: ruff-format

  - repo: https://github.com/PyCQA/bandit
    rev: 1.7.8
    hooks:
      - id: bandit
        args: ["-c", "backend/pyproject.toml", "-r", "backend/"]

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.6.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-json
      - id: check-added-large-files
        args: [--maxkb=500]
      - id: detect-private-key
```

---

## 9. 测试策略

### 9.1 测试金字塔

```
        ┌─────────┐
        │   E2E   │  ← 少量，覆盖关键用户流程
        ├─────────┤
        │ 集成测试 │  ← 中等，覆盖 API 端到端
        ├─────────┤
        │ 单元测试 │  ← 大量，覆盖业务逻辑
        └─────────┘
```

### 9.2 后端测试

**框架：pytest + pytest-asyncio + httpx（AsyncClient）**

| 测试类型 | 覆盖范围 | 目标覆盖率 |
|----------|----------|------------|
| 单元测试 | Service 层业务逻辑 | ≥ 80% |
| 集成测试 | Router 层 API 端到端 | ≥ 70% |
| 安全测试 | 认证、权限、注入防护 | 关键路径 100% |

**测试命名：** `test_<被测函数>_<场景>_<预期>`  
**示例：** `test_create_ingredient_with_valid_data_returns_201`

**Fixture 设计：**
```python
# conftest.py
@pytest.fixture
async def db_session():
    """每个测试用例独立的数据库会话"""
    ...

@pytest.fixture
async def auth_client(db_session):
    """已认证的 API 客户端"""
    ...

@pytest.fixture
def sample_ingredient():
    """示例食材数据"""
    return {"name": "西红柿", "category": "vegetable", "quantity": 3}
```

### 9.3 前端测试

**框架：Vitest + Testing Library + Playwright**

| 测试类型 | 工具 | 覆盖范围 |
|----------|------|----------|
| 单元测试 | Vitest | 组件渲染、Hook 逻辑 |
| 快照测试 | Vitest | UI 结构回归 |
| E2E 测试 | Playwright | 关键用户流程 |

**E2E 关键流程：**
1. 打开首页 → 看到冰箱看板
2. 添加食材 → 列表更新
3. 点击 AI 识别 → 上传图片 → 返回识别结果
4. 点击菜谱推荐 → 看到可做菜谱
5. 查看营养洞察 → 图表渲染

### 9.4 CI 中的测试流程

```
代码提交
  → 安全扫描（Bandit + npm audit）
  → Lint 检查（Ruff + ESLint）
  → 后端单元测试（pytest --cov）
  → 前端单元测试（vitest --coverage）
  → 构建（vite build）
  → E2E 测试（Playwright）
  → 全部通过 → 允许合并
```

---

## 10. 部署流程

### 10.1 部署架构

```
                    ┌──────────────┐
                    │   用户浏览器   │
                    └──────┬───────┘
                           │
              ┌────────────▼────────────┐
              │   GitHub Pages (前端)    │
              │   echoqili.github.io     │
              └────────────┬────────────┘
                           │ HTTPS API
              ┌────────────▼────────────┐
              │   后端服务器 (Docker)     │
              │   FastAPI + Uvicorn     │
              └────────────┬────────────┘
                           │
              ┌────────────▼────────────┐
              │   SQLite / PostgreSQL   │
              └─────────────────────────┘
```

### 10.2 前端部署（GitHub Pages）

- 触发条件：push 到 main 分支
- 构建命令：`npm run build`
- 产物目录：`frontend/dist`
- 部署方式：GitHub Actions 自动部署到 GitHub Pages
- 访问地址：`https://echoqili.github.io/fridge-manager/`

### 10.3 后端部署（Docker）

```dockerfile
# Dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ .
RUN mkdir -p data
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# docker-compose.yml
version: '3.8'
services:
  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=sqlite+aiosqlite:///./data/fridge.db
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    volumes:
      - ./data:/app/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### 10.4 CI/CD 流水线

```yaml
# .github/workflows/ci.yml 触发条件
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

# Job 依赖关系
security-scan → lint → {frontend-test, backend-test} → build → {e2e-test, docker-build}
```

**流水线阶段：**

1. **安全扫描**：Bandit（Python SAST）+ npm audit（前端依赖）
2. **Lint 检查**：Ruff check + Ruff format check + ESLint
3. **单元测试**：pytest --cov + vitest --coverage
4. **构建**：vite build
5. **E2E 测试**：Playwright
6. **Docker 构建**：仅 main 分支
7. **部署**：前端自动部署到 GitHub Pages

### 10.5 环境管理

| 环境 | 用途 | 数据库 | 部署方式 |
|------|------|--------|----------|
| development | 本地开发 | SQLite | 本地运行 |
| staging | 预发布验证 | PostgreSQL | Docker |
| production | 生产环境 | PostgreSQL | Docker + 反向代理 |

### 10.6 回滚策略

- 前端：GitHub Pages 支持查看历史部署，可通过 Actions re-run 回滚
- 后端：Docker 镜像保留最近 5 个版本，`docker-compose down && docker-compose up -d <旧版本>`
- 数据库：Alembic 支持 downgrade，但生产环境优先使用备份恢复

---

## 附录：开发顺序建议

按以下顺序开发，每一步都可独立验证：

1. **Phase 1 - 基础骨架**：项目初始化、目录结构、配置文件、Docker 环境
2. **Phase 2 - 后端核心**：数据库模型、认证模块、食材 CRUD API
3. **Phase 3 - AI 服务**：图像识别接口、菜谱推荐接口
4. **Phase 4 - 前端核心**：布局、冰箱看板、食材管理页面
5. **Phase 5 - 前端 AI 交互**：拍照上传、菜谱推荐、营养洞察
6. **Phase 6 - 测试与部署**：单元测试、E2E 测试、CI/CD 配置

---

> **请确认以上规范是否满足要求，确认后我将严格按照此规范开始项目开发。**
