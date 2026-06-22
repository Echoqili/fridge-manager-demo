# 鲜知 fridge · AI 冰箱管家

> 打开冰箱就知道今天吃什么 —— 用 AI 让冰箱开口说话，减少食材浪费，让每一餐都更简单、更健康。

**TRAE AI 创造力大赛参赛作品 · 生活娱乐赛道**

---

## 在线体验

🔗 **[立即体验 Demo](https://echoqili.github.io/fridge-manager-demo/)**

> 点击登录页「演示模式体验」按钮，无需注册即可体验全部功能，预填充 12 种常见食材。
> Demo 由项目 `frontend/` 构建并自动部署到 GitHub Pages。

---

## 创意介绍

### 想解决什么问题

每个家庭都面临过这样的困境：冰箱里塞满了食材，却不知道该做什么菜；买了的食材忘记吃，直到过期扔掉；想吃得健康，却不知道营养是否均衡。据统计，中国家庭每年浪费的食物约 1700 万吨，其中大量源于冰箱管理不当。

### 为什么会想到做这个

灵感来自日常生活：每次打开冰箱都在发愁"今天吃什么"，经常发现食材过期了才想起来，买菜时也不清楚家里还有什么。如果冰箱能"开口说话"，告诉我该做什么菜、什么快过期了、缺什么该买了，就能大大减少浪费。

### 产品形态

一个全栈 Web 应用，通过拍照识别、智能库存管理和 AI 菜谱推荐，帮助用户管理冰箱食材、减少浪费、优化膳食搭配。

---

## 功能亮点

### 📸 拍照识食材
上传冰箱照片，AI 自动识别食材种类、数量与建议存放位置。支持 GPT-4o 多模态识别，识别失败时自动降级到本地推断。

### 🧊 智能库存管理
可视化冰箱分区（冷藏室、冷冻室、储物柜），食材一目了然。支持按分类、存储位置筛选，临期食材自动标红提醒。

### ⏰ 临期提醒
自动计算食材保质期，3 天内到期的食材醒目标记，优先推荐使用临期食材的菜谱，减少浪费。预估每次优先消耗可节省 ¥8+。

### ✨ AI 菜谱推荐
根据现有食材智能匹配菜谱，优先使用临期食材。每道菜谱包含烹饪步骤、所需食材、卡路里和份数信息。

### 🛒 购物清单
基于推荐菜谱自动生成缺失食材的购物清单，一键添加，方便采购。

### 📊 营养洞察
按蔬菜、肉类、蛋奶、主食、水果分类统计库存，ECharts 可视化饼图展示营养分布，AI 生成个性化饮食建议。

---

## 目标用户与场景

| 维度 | 描述 |
|------|------|
| 核心用户 | 25-40 岁城市家庭主厨、独居白领、注重健康饮食的年轻人 |
| 使用场景 | 每日做饭前查看冰箱库存、买菜后录入食材、周末规划一周菜谱 |
| 当前痛点 | 食材过期浪费、不知道做什么菜、营养搭配不均衡、重复购买已有食材 |

---

## 价值与意义

- **社会价值**：减少家庭食物浪费，助力环保。每减少 1kg 食物浪费，相当于减少 2.5kg CO₂ 排放
- **效率提升**：从"打开冰箱发呆 10 分钟"到"30 秒获取菜谱推荐"，日均节省 15 分钟决策时间
- **健康价值**：营养可视化 + AI 建议，帮助用户均衡膳食结构

---

## 技术架构

### 前端
- **React 18** + Vite 5 + Ant Design 5
- React Router 6 + Axios + ECharts 数据可视化
- Vitest + Testing Library + Playwright E2E 测试

### 后端
- **FastAPI** + SQLAlchemy 2.0 (async) + SQLite
- Pydantic v2 + python-jose (JWT 双 Token 认证) + passlib (bcrypt)
- OpenAI GPT-4o 多模态图像识别 + 智谱 GLM-4V 降级方案
- Ruff + Bandit 安全扫描 + pytest (29 个测试)

### 基础设施
- Docker + docker-compose 全栈编排
- GitHub Actions CI/CD（8 阶段流水线：安全扫描 → Lint → 测试 → 构建 → E2E → 部署）
- GitHub Pages 自动部署

### 架构亮点
- **前后端分离**：RESTful API + JWT 认证，前后端可独立部署
- **AI 降级机制**：OpenAI → 智谱 → 本地推断，三级 fallback 保证可用性
- **演示模式**：无需后端即可体验全部功能，预填充真实数据
- **统一分类体系**：6 类食材分类（蔬菜/肉类/蛋奶/主食/水果/其他）前后端完全对齐

---

## 项目结构

```
fridge-manager/
├── backend/              # FastAPI 后端
│   ├── core/             # 配置、安全、异常处理
│   ├── models/           # ORM 模型（User/Ingredient/Recipe）
│   ├── schemas/          # Pydantic v2 数据验证
│   ├── services/         # 业务逻辑层（食材/菜谱/识别/营养）
│   ├── routers/          # API 路由（auth/ingredients/recipes/recognition/nutrition）
│   ├── tests/            # 单元测试（29 个，覆盖全部接口）
│   └── main.py           # 应用入口
├── frontend/             # React 前端
│   ├── src/api/          # API 调用层（axios + 拦截器）
│   ├── src/components/   # 通用组件（IngredientCard/RecipeCard/UploadPanel 等）
│   ├── src/pages/        # 页面（Home/Recipes/Nutrition/Auth）
│   ├── src/contexts/     # 全局状态管理（AppContext）
│   ├── src/utils/        # 工具函数（分类推断/临期判断/emoji 映射）
│   └── src/styles/       # 主题样式（莫兰迪暖色系）
├── docs/                 # 设计规范文档
├── DevLog.md             # 开发日志
├── Dockerfile            # 后端容器化
├── docker-compose.yml    # 全栈编排
└── .github/workflows/    # CI/CD 流水线
```

---

## 快速开始

### 在线体验

访问 [Demo 地址](https://echoqili.github.io/fridge-manager-demo/)，点击「演示模式体验」即可。

> **部署说明**：本 Demo 通过 `.github/workflows/ci.yml` 自动构建 `frontend/` 并部署到 GitHub Pages。请确保仓库 **Settings → Pages → Source** 选择 **GitHub Actions**，否则页面不会更新为基于项目的 React 应用。

### 本地开发

**环境要求**：Python 3.10+、Node.js 20+、Git

```bash
# 后端启动
cd backend
python -m venv .venv && .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # 编辑 .env 填入配置
uvicorn main:app --reload --port 8000

# 前端启动
cd frontend
npm install
npm run dev  # http://localhost:3000
```

### Docker 一键启动

```bash
docker-compose up -d
# 前端：http://localhost:3000
# 后端：http://localhost:8000
```

---

## 测试

```bash
# 后端测试（29 个）
cd backend && pytest tests/ -v --cov

# 前端测试（12 个）
cd frontend && npm run test:run

# E2E 测试
cd frontend && npx playwright test
```

---

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/v1/auth/register | 用户注册 |
| POST | /api/v1/auth/login | 用户登录（返回 user 信息） |
| POST | /api/v1/auth/refresh | 刷新令牌 |
| GET | /api/v1/ingredients | 获取食材列表 |
| POST | /api/v1/ingredients | 添加食材 |
| PUT | /api/v1/ingredients/{id} | 更新食材 |
| DELETE | /api/v1/ingredients/{id} | 删除食材 |
| GET | /api/v1/ingredients/expiring | 获取临期食材 |
| POST | /api/v1/recognition/recognize | AI 拍照识别食材 |
| GET | /api/v1/recipes/recommend | AI 菜谱推荐 |
| GET | /api/v1/recipes/{id} | 菜谱详情 |
| GET | /api/v1/nutrition/summary | 营养分析与建议 |

API 文档：http://localhost:8000/docs（Swagger UI）

---

## 开发过程

本项目使用 **TRAE IDE** 完成全部开发，详细开发记录见 [DevLog.md](DevLog.md)。

### 迭代历程

| 版本 | 主要内容 | 状态 |
|------|----------|------|
| v0.1.0 | 项目初始化、核心功能开发、CI/CD 搭建 | 已完成 |
| v0.2.0 | Bug 修复（登录契约/分类体系/E2E）、测试补全 | 已完成 |
| v0.3.0 | 比赛润色（演示模式增强、README 参赛版） | 进行中 |

---

## 赛事信息

本项目为 **TRAE AI 创造力大赛** 参赛作品，生活娱乐赛道。

- 大赛官网：https://www.trae.cn/ai-creativity/result
- 开发工具：TRAE IDE
- 开发语言：Python + JavaScript/React
