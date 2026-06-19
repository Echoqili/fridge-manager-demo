# DevLog — 鲜知 fridge · AI 冰箱管家 开发日志

> 本文档记录项目的迭代开发过程，包含开发计划、功能变更、技术决策、实现细节、测试结果及问题追踪。

---

## v0.1.0 — 初始项目搭建 (2026-06-17 ~ 2026-06-18)

### 主要开发任务
- 项目初始化：前后端分离架构（FastAPI + React）
- 后端核心：数据库模型、JWT 认证、食材 CRUD API
- AI 服务层：OpenAI GPT-4o 图像识别、本地菜谱推荐
- 前端核心：布局、冰箱看板、食材管理、菜谱推荐、营养洞察
- 基础设施：Docker、GitHub Actions CI/CD、GitHub Pages 部署

### 完成情况
- [x] 用户认证全流程（注册/登录/刷新/登出/鉴权）
- [x] 食材 CRUD + 临期查询 + 分类过滤
- [x] 菜谱推荐（本地库匹配排序）+ 详情查看
- [x] 图像识别（OpenAI GPT-4o + 降级兜底）
- [x] 营养分类统计 + 建议生成
- [x] 前端全部页面与组件（含 API 不可用时的本地兜底）
- [x] CI/CD 流水线（安全扫描/Lint/测试/构建/E2E/部署）
- [x] 后端单元测试 24 个（auth/ingredients/recipes/recognition）

### 已知问题（遗留至 v0.2.0）
1. **登录契约 Bug**：后端 `TokenResponse` 不返回 `user` 字段，前端 `AppContext.jsx` 期望 `data.user`，导致真实登录后 `userInfo` 为 `undefined`，用户被立即重定向回登录页
2. **前后端分类体系不一致**：后端使用 `meat`/`dairy`（6 类），前端 `config.js` 缺少 `dairy`（5 类），`helpers.js` 用 `protein` 替代 `meat`+`dairy`
3. **E2E 测试失败**：演示模式使用 `window.location.href = '/'` 导致整页刷新，Playwright `waitForURL` 时序冲突，3/4 个 E2E 测试失败
4. **deploy.yml 问题**：与 `ci.yml` 中的 deploy job 功能重复，且 `upload-pages-artifact` 的 `path: '.'` 上传整个仓库而非 `frontend/dist`
5. **营养分析接口无测试**：`/nutrition/summary` 端点完全没有测试覆盖
6. **智谱 GLM-4V 识别为桩代码**：`_recognize_with_zhipu` 直接 return None
7. **Alembic 迁移目录为空**：依赖 `create_all` 建表，无版本管理

---

## v0.2.0 — Bug 修复与测试补全 (2026-06-19)

### 迭代目标
修复 v0.1.0 遗留的关键 Bug，统一前后端数据契约，补全测试覆盖，确保 CI 流水线可全量通过。

### 开发任务清单

| # | 任务 | 优先级 | 状态 |
|---|------|--------|------|
| 1 | 修复登录契约 Bug（后端返回 user 信息） | 高 | 已完成 |
| 2 | 统一前后端分类体系（meat/dairy 6 类） | 高 | 已完成 |
| 3 | 修复 E2E 测试失败（演示模式导航） | 高 | 已完成 |
| 4 | 修复 deploy.yml（删除重复 + 修正 path） | 中 | 已完成 |
| 5 | 补充营养分析接口测试 test_nutrition.py | 中 | 已完成 |
| 6 | 运行全量测试验证 | 高 | 已完成 |

### 技术决策

#### 决策 1：登录响应包含 user 字段
- **方案**：在 `TokenResponse` 中添加可选的 `user: UserResponse | None` 字段，登录和刷新接口返回用户信息
- **理由**：前端 `AppContext.login()` 依赖 `data.user` 设置用户状态，修改后端比修改前端更符合 RESTful 惯例（登录即返回用户信息），且不破坏已有 API 契约（字段可选）
- **影响**：`backend/schemas/auth.py`、`backend/routers/auth.py`

#### 决策 2：前端分类体系统一为后端 6 类
- **方案**：前端 `config.js` 的 `CATEGORIES` 添加 `dairy: '蛋奶'`，`helpers.js` 的 `CATEGORY_KEYWORDS` 将 `protein` 拆分为 `meat` 和 `dairy`，`getCategoryColor`/`getCategoryIcon`/`getCategoryStats` 同步更新
- **理由**：后端 `Literal["vegetable", "meat", "dairy", "staple", "fruit", "other"]` 是数据源标准，前端应适配后端而非反之
- **影响**：`frontend/src/config.js`、`frontend/src/utils/helpers.js`、`frontend/src/pages/NutritionPage.jsx`

#### 决策 3：演示模式改用 React Router 导航
- **方案**：`AuthPage.jsx` 的 `handleDemoLogin` 改用 `navigate('/')` 替代 `window.location.href = '/'`，并通过 `AppContext` 设置用户状态
- **理由**：`window.location.href` 触发整页刷新，Playwright 的 `waitForURL` 与后续断言存在时序竞争；使用 SPA 导航可避免此问题
- **影响**：`frontend/src/pages/AuthPage.jsx`

### 实现详情

#### 1. 修复登录契约 Bug

**问题**：后端 `TokenResponse` 只返回 `access_token`/`refresh_token`/`token_type`，前端 `AppContext.login()` 期望 `data.user` 字段，导致真实登录后 `userInfo` 为 `undefined`，用户被立即重定向回登录页。

**修复方案**：
- [backend/schemas/auth.py](file:///D:/Pycharm_workplace/github/fridge-manager/backend/schemas/auth.py)：将 `UserResponse` 类定义移至 `TokenResponse` 之前（解决前向引用），在 `TokenResponse` 中添加 `user: UserResponse | None` 可选字段
- [backend/routers/auth.py](file:///D:/Pycharm_workplace/github/fridge-manager/backend/routers/auth.py)：`login` 和 `refresh` 接口返回时附带 `UserResponse.model_validate(user)`

**影响范围**：后端 API 响应结构变更（新增可选字段，向后兼容）

#### 2. 统一前后端分类体系

**问题**：后端使用 6 类分类（vegetable/meat/dairy/staple/fruit/other），前端 `config.js` 缺少 `dairy`（仅 5 类），`helpers.js` 用 `protein` 替代 `meat`+`dairy`，导致数据不一致。

**修复方案**：
- [frontend/src/config.js](file:///D:/Pycharm_workplace/github/fridge-manager/frontend/src/config.js)：`CATEGORIES` 添加 `dairy: '蛋奶'`，`meat` 改为 `'肉类'`
- [frontend/src/utils/helpers.js](file:///D:/Pycharm_workplace/github/fridge-manager/frontend/src/utils/helpers.js)：
  - `CATEGORY_KEYWORDS` 将 `protein` 拆分为 `meat`（牛肉/猪肉/鸡肉/鱼/虾）和 `dairy`（鸡蛋/蛋/牛奶/酸奶/豆腐/芝士/黄油）
  - `getCategoryColor` 添加 `meat`/`dairy` 颜色映射
  - `getCategoryIcon` 添加 `meat`/`dairy` 图标映射
  - `getCategoryStats` 初始化对象改为 6 类
- [frontend/src/pages/NutritionPage.jsx](file:///D:/Pycharm_workplace/github/fridge-manager/frontend/src/pages/NutritionPage.jsx)：分类统计显示从 4 格改为 5 格（蔬菜/肉类/蛋奶/主食/水果），AI 建议逻辑改为检查 `meat` 和 `dairy` 同时为 0

#### 3. 修复 E2E 测试失败

**问题**：演示模式使用 `window.location.href = '/'` 触发整页刷新，Playwright `waitForURL` 与后续断言存在时序竞争，3/4 个 E2E 测试失败。同时，演示模式直接写 localStorage 但不更新 React 状态，SPA 导航后 `ProtectedRoute` 会重定向回 `/login`。

**修复方案**：
- [frontend/src/contexts/AppContext.jsx](file:///D:/Pycharm_workplace/github/fridge-manager/frontend/src/contexts/AppContext.jsx)：新增 `demoLogin()` 函数，设置 localStorage 同时调用 `setUser(demoUser)` 更新 React 状态，并暴露到 Context value
- [frontend/src/pages/AuthPage.jsx](file:///D:/Pycharm_workplace/github/fridge-manager/frontend/src/pages/AuthPage.jsx)：`handleDemoLogin` 改用 `demoLogin()` + `navigate('/')` 替代 `window.location.href`，移除不再需要的 `TOKEN_KEY`/`USER_KEY` 导入

#### 4. 修复 deploy.yml

**问题**：`deploy.yml` 与 `ci.yml` 中的 deploy job 功能重复，且 `upload-pages-artifact` 的 `path: '.'` 上传整个仓库而非 `frontend/dist`。

**修复方案**：删除 `deploy.yml`，保留 `ci.yml` 中已有的正确 deploy job（使用 `path: frontend/dist`，依赖 e2e-test 通过后执行）。

#### 5. 补充营养分析接口测试

**新增文件**：[backend/tests/test_nutrition.py](file:///D:/Pycharm_workplace/github/fridge-manager/backend/tests/test_nutrition.py)

5 个测试用例：
| 测试名 | 覆盖场景 |
|--------|----------|
| `test_nutrition_summary_empty` | 空库存时返回 total=0，所有分类计数为 0，有多条建议 |
| `test_nutrition_summary_with_ingredients` | 3 种分类食材的统计正确，中文名标签存在 |
| `test_nutrition_summary_all_categories` | 覆盖全部 6 个分类的统计 |
| `test_nutrition_summary_advice_balanced` | 食材均衡时返回正面建议（含"均衡"关键词） |
| `test_nutrition_requires_auth` | 无认证访问返回 401 |

### 测试结果

| 测试类型 | 工具 | 结果 |
|----------|------|------|
| 后端单元测试 | pytest + pytest-asyncio | **29 passed** (含新增 5 个营养测试) |
| 前端单元测试 | Vitest | **12 passed** (4 suites) |
| 后端 Lint | Ruff check | **All checks passed** |
| 后端 Format | Ruff format --check | **36 files already formatted** |
| 前端 Lint | ESLint | **0 errors** |

### 代码变更清单

| 文件 | 变更类型 | 说明 |
|------|----------|------|
| `backend/schemas/auth.py` | 修改 | `UserResponse` 移至 `TokenResponse` 前，`TokenResponse` 添加 `user` 字段 |
| `backend/routers/auth.py` | 修改 | `login`/`refresh` 返回 `UserResponse` |
| `backend/tests/test_nutrition.py` | 新增 | 5 个营养分析接口测试 |
| `frontend/src/config.js` | 修改 | `CATEGORIES` 添加 `dairy`，`meat` 改为 `'肉类'` |
| `frontend/src/utils/helpers.js` | 修改 | `protein` 拆分为 `meat`+`dairy`，颜色/图标/统计同步更新 |
| `frontend/src/pages/NutritionPage.jsx` | 修改 | 分类统计显示 5 格，AI 建议逻辑适配新分类 |
| `frontend/src/contexts/AppContext.jsx` | 修改 | 新增 `demoLogin` 函数并暴露到 Context |
| `frontend/src/pages/AuthPage.jsx` | 修改 | 演示模式改用 `demoLogin`+`navigate` |
| `.github/workflows/deploy.yml` | 删除 | 与 `ci.yml` 重复且 path 错误 |

### 未解决问题

1. **智谱 GLM-4V 识别仍为桩代码**：`recognition_service.py` 的 `_recognize_with_zhipu` 直接 return None，需集成智谱 SDK
2. **AI 菜谱推荐未实现**：`recipe_service.py` 中 AI 调用部分仅注释说明，实际只返回本地结果
3. **Alembic 迁移目录为空**：依赖 `create_all` 建表，无版本管理脚本
4. **`useIngredients.js` 冗余**：完整实现但未被任何组件引用
5. **`RecipeIngredientModel` 未使用**：模型已定义但服务层未实际查询
6. **E2E 测试需在 CI 环境验证**：本地修复了演示模式导航逻辑，但 Playwright 测试需在 CI 环境中最终验证

### 后续计划 (v0.3.0)

1. 集成智谱 GLM-4V 图像识别（替换桩代码）
2. 实现 AI 菜谱推荐（调用 LLM 生成菜谱）
3. 创建 Alembic 初始迁移脚本
4. 清理冗余代码（`useIngredients.js`、未使用的 `RecipeIngredientModel`）
5. 补充前端组件测试（AuthPage、NutritionPage、RecipesPage）
6. 在 CI 环境中验证 E2E 测试通过

---

## v0.3.0 — 比赛润色与演示增强 (2026-06-19)

### 迭代目标
根据 TRAE AI 创造力大赛评审要求（创意价值、TRAE 实践过程、Demo 体验、参赛帖质量），对项目进行参赛润色，重点增强演示体验和文档完整性。

### 开发任务清单

| # | 任务 | 优先级 | 状态 |
|---|------|--------|------|
| 1 | 分析比赛评审要求并制定润色计划 | 高 | 已完成 |
| 2 | 增强演示模式：预填充 12 种真实食材数据 | 高 | 已完成 |
| 3 | 演示模式支持本地 CRUD（无需后端） | 高 | 已完成 |
| 4 | 润色 README.md 为比赛参赛版本 | 高 | 已完成 |
| 5 | 创建参赛帖模板文档 CONTEST_POST.md | 高 | 已完成 |
| 6 | 验证前端构建和测试通过 | 中 | 已完成 |

### 技术决策

#### 决策 1：演示模式预填充数据 + 本地 CRUD
- **方案**：在 `AppContext` 中添加 `DEMO_INGREDIENTS`（12 种食材，覆盖全部 6 个分类），`demoLogin` 时自动填充；所有 CRUD 操作通过 `isDemo` 标志区分，演示模式直接操作本地状态
- **理由**：比赛评委需要一键体验全部功能，不能依赖后端部署。预填充数据让评委立即看到丰富的界面，本地 CRUD 让评委可以添加/删除食材体验交互
- **影响**：`frontend/src/contexts/AppContext.jsx`

#### 决策 2：README 重构为参赛版
- **方案**：README 从技术文档重构为参赛展示文档，包含创意介绍、目标用户、价值意义、功能亮点、技术架构、开发过程
- **理由**：比赛评审要求参赛帖结构完整、便于评审，README 是评委了解项目的第一入口
- **影响**：`README.md`

#### 决策 3：创建参赛帖模板
- **方案**：创建 `docs/CONTEST_POST.md`，按初赛 Demo 帖要求（Demo 简介/创作思路/体验地址/TRAE 实践过程）预写模板，用户只需填入 Session ID 和截图
- **理由**：初赛要求 4 个板块结构完整，需 3+ 截图和 3+ Session ID，模板确保不遗漏
- **影响**：`docs/CONTEST_POST.md`（新增）

### 实现详情

#### 1. 演示模式增强

**预填充数据**（12 种食材，覆盖 6 个分类）：
- 蔬菜：西红柿、土豆、西兰花、洋葱、胡萝卜
- 肉类：牛肉、鸡肉
- 蛋奶：鸡蛋、牛奶
- 主食：米饭
- 水果：香蕉、草莓
- 包含真实的购买日期、过期日期、存储位置，部分食材设置为临期（3 天内到期）

**本地 CRUD**：
- `isDemo` 状态标志区分演示/真实模式
- `addIngredient`：演示模式生成 `d{timestamp}` ID，直接追加到状态
- `removeIngredient`：演示模式直接过滤状态
- `updateIngredient`：演示模式直接更新状态
- `refreshIngredients`：演示模式返回预填充数据
- `logout`：演示模式跳过 API 调用

#### 2. README 参赛版

重构为以下结构：
1. 在线体验（Demo 链接 + 演示模式说明）
2. 创意介绍（问题/动机/产品形态）
3. 功能亮点（6 大功能详细说明）
4. 目标用户与场景（表格形式）
5. 价值与意义（社会/效率/健康三维度）
6. 技术架构（前端/后端/基础设施/架构亮点）
7. 项目结构
8. 快速开始
9. 测试
10. API 接口
11. 开发过程（迭代历程表）
12. 赛事信息

#### 3. 参赛帖模板

按初赛要求 4 大板块预写：
- Demo 简介（产品形态/用户/功能 + 截图占位）
- 创作思路（灵感/痛点/方向选择）
- 体验地址（在线链接 + 演示模式说明）
- TRAE 实践过程（4 步开发流程 + Session ID 占位 + 踩坑记录 + 技术栈表）

### 测试结果

| 测试类型 | 结果 |
|----------|------|
| 前端构建 | **Build 成功** (25.50s, 3692 modules) |
| 前端单元测试 | **12 passed** (2 suites) |

### 代码变更清单

| 文件 | 变更类型 | 说明 |
|------|----------|------|
| `frontend/src/contexts/AppContext.jsx` | 修改 | 添加 DEMO_INGREDIENTS、isDemo 状态、本地 CRUD |
| `README.md` | 重写 | 从技术文档重构为参赛展示文档 |
| `docs/CONTEST_POST.md` | 新增 | 初赛参赛帖模板 |

### 未解决问题

1. 需要用户填入实际的 TRAE Session ID（至少 3 个）
2. 需要用户截取开发过程截图（至少 3 张）
3. GitHub Pages 部署需推送代码后触发 CI
4. 智谱 GLM-4V 识别仍为桩代码（v0.4.0 计划）
5. AI 菜谱推荐未实现（v0.4.0 计划）

### 后续计划 (v0.4.0)

1. 推送代码到 GitHub 触发 CI/CD 部署
2. 集成智谱 GLM-4V 图像识别
3. 实现 AI 菜谱推荐
4. 补充前端组件测试
5. 优化前端构建体积（代码分割）

---

## v0.4.0 — AI 菜谱推荐 (2026-06-19)

### 迭代目标
实现基于 LLM 的 AI 菜谱推荐，根据用户冰箱中的现有食材动态生成个性化菜谱，并在前端展示 AI 生成标识。

### 开发任务清单

| # | 任务 | 优先级 | 状态 |
|---|------|--------|------|
| 1 | 设计 LLM 菜谱生成提示词和解析逻辑 | 高 | 已完成 |
| 2 | 实现 OpenAI GPT 菜谱生成服务 | 高 | 已完成 |
| 3 | AI 菜谱与本地菜谱合并去重排序 | 高 | 已完成 |
| 4 | 扩展菜谱详情支持 AI 生成 ID | 高 | 已完成 |
| 5 | 前端 RecipeCard 显示 AI 标签和匹配数 | 中 | 已完成 |
| 6 | 补充 AI 菜谱推荐测试 | 高 | 已完成 |
| 7 | 运行全量测试验证 | 高 | 已完成 |

### 技术决策

#### 决策 1：OpenAI GPT 生成结构化 JSON
- **方案**：使用 `gpt-4o` 模型，提示词要求返回严格的 JSON 数组，包含 name/description/cook_time/calories/servings/ingredients/steps 字段
- **理由**：项目已依赖 `openai` 库，结构化 JSON 便于后端解析为 Pydantic Schema，前端无需改动数据结构
- **影响**：`backend/services/recipe_service.py`

#### 决策 2：AI 菜谱优先，本地库兜底
- **方案**：`recommend_recipes()` 先调用 LLM 生成菜谱，若失败或超时则使用本地预设菜谱库；合并时按匹配数降序，匹配数相同时 AI 菜谱优先
- **理由**：保证 AI 不可用时用户体验不中断；AI 生成菜谱更具创意，应优先展示
- **影响**：`backend/services/recipe_service.py` 中 `_deduplicate_recipes()`

#### 决策 3：AI 菜谱详情通过推荐列表获取
- **方案**：AI 生成的菜谱 ID 形如 `ai-0`、`ai-1`，不持久化到数据库；详情页从推荐列表的客户端状态中获取
- **理由**：简化实现，避免每次请求详情都调用一次 LLM；若用户刷新详情页，可回退到推荐列表
- **影响**：`get_recipe_by_id()` 对 `ai-` ID 返回提示信息；前端详情弹窗从推荐列表传入

### 实现详情

#### 1. 后端 LLM 菜谱生成

新增/修改函数：
- `_build_recipe_prompt(user_ingredients, limit)`：构造包含食材列表和 JSON 格式要求的提示词
- `_clean_json_content(content)`：清理 LLM 可能返回的 Markdown 代码块标记
- `_parse_ai_recipes(raw_content)`：解析并规范化 LLM 返回的 JSON，确保字段类型正确
- `_generate_recipes_with_openai(user_ingredients, limit)`：调用 OpenAI API，失败时返回 None
- `_deduplicate_recipes(ai_recipes, local_recipes, ...)`：合并 AI 和本地菜谱，按匹配数排序，去重

菜谱响应中 `source` 字段为 `"ai"`，`recipe_id` 为 `"ai-{index}"`。

#### 2. 前端展示增强

[frontend/src/components/RecipeCard.jsx](file:///D:/Pycharm_workplace/github/fridge-manager/frontend/src/components/RecipeCard.jsx)：
- 当 `recipe.source === 'ai'` 时显示紫色 `AI 生成` 标签（带 RobotOutlined 图标）
- 显示 `匹配 N 种食材` 标签，帮助用户判断菜谱与现有食材的契合度

### 测试结果

| 测试类型 | 工具 | 结果 |
|----------|------|------|
| 后端单元测试 | pytest | **32 passed**（新增 3 个 AI 菜谱测试） |
| 前端单元测试 | Vitest | **12 passed** |
| 前端生产构建 | vite build | **成功**（3692 modules） |

### 代码变更清单

| 文件 | 变更类型 | 说明 |
|------|----------|------|
| `backend/services/recipe_service.py` | 修改 | 新增 LLM 菜谱生成、解析、合并去重逻辑；OpenAI 导入移至模块顶部 |
| `backend/tests/test_recipes.py` | 修改 | 新增 3 个 AI 菜谱推荐测试 |
| `frontend/src/components/RecipeCard.jsx` | 修改 | 显示 AI 生成标签和匹配食材数量 |

### 未解决问题

1. 智谱 GLM-4V 图像识别仍为桩代码
2. Alembic 迁移目录为空
3. AI 菜谱详情页刷新时会丢失（未持久化）
4. 需要推送代码到 GitHub 触发 CI/CD 部署
5. 需要用户填入 TRAE Session ID 和截图到参赛帖

### 后续计划 (v0.5.0)

1. 集成智谱 GLM-4V 图像识别（替换桩代码）
2. 创建 Alembic 初始迁移脚本
3. 持久化 AI 生成菜谱到数据库，支持详情页刷新
4. 补充前端组件测试（AuthPage、NutritionPage、RecipesPage）
5. 推送代码并验证 GitHub Pages 部署

---

## v0.5.0 — 智谱 GLM-4V + 购物清单持久化 + 工程化完善 (2026-06-19)

### 迭代目标
完成 v0.4.0 遗留的全部工程化任务：替换智谱 GLM-4V 桩代码、实现购物清单后端持久化、创建 Alembic 迁移脚本、补充前端测试与构建优化、完善 E2E 测试覆盖。

### 开发任务清单

| # | 任务 | 优先级 | 状态 |
|---|------|--------|------|
| 1 | 智谱 GLM-4V 图像识别（替换桩代码） | 高 | 已完成 |
| 2 | 购物清单持久化（后端 API + 数据库 + 前端集成） | 高 | 已完成 |
| 3 | 创建 Alembic 数据库迁移脚本 | 高 | 已完成 |
| 4 | 补充前端组件测试（ShoppingList） | 中 | 已完成 |
| 5 | 优化前端构建体积（手动分包） | 中 | 已完成 |
| 6 | 完善 E2E 测试（4→11 个用例） | 中 | 已完成 |

### 技术决策

#### 决策 1：智谱 GLM-4V 使用 httpx 直接调用而非 SDK
- **方案**：通过 `httpx.AsyncClient` 调用智谱开放平台 REST API（`https://open.bigmodel.cn/api/paas/v4/chat/completions`），发送 base64 图片 + JSON 提示词
- **理由**：项目已依赖 `httpx`，无需引入 `zhipuai` SDK；REST API 接口与 OpenAI 兼容，复用提示词和解析逻辑
- **影响**：`backend/services/recognition_service.py` 中 `_recognize_with_zhipu()`

#### 决策 2：购物清单独立数据表 + 批量 API
- **方案**：新建 `shopping_list_items` 表（item_id/user_id/name/quantity/checked），提供 CRUD + 批量添加 + 清空 API；前端生成菜谱后自动同步缺失食材到购物清单
- **理由**：独立表便于持久化和多设备同步；批量 API 减少网络请求；演示模式降级为本地计算
- **影响**：`backend/models/shopping_list.py`、`backend/routers/shopping_list.py`、`frontend/src/api/shoppingList.js`、`frontend/src/pages/HomePage.jsx`

#### 决策 3：Alembic 迁移脚本手写而非 autogenerate
- **方案**：手动编写初始迁移脚本 `0001_initial_schema`，覆盖全部 5 张表
- **理由**：autogenerate 需要连接真实数据库，CI 环境可能无 DB；手写脚本可控性更强
- **影响**：`backend/alembic/versions/2026_06_19_0001_initial_schema.py`

#### 决策 4：Vite 手动分包策略
- **方案**：在 `vite.config.js` 的 `build.rollupOptions.output.manualChunks` 中将依赖拆分为 `react-vendor`、`antd-vendor`、`echarts-vendor`、`utils-vendor` 四个 chunk
- **理由**：第三方库变更频率低，独立 chunk 可利用浏览器缓存；ECharts 体积大，分离后首屏加载更快
- **影响**：`frontend/vite.config.js`

### 实现详情

#### 1. 智谱 GLM-4V 图像识别

[backend/services/recognition_service.py](file:///D:/Pycharm_workplace/github/fridge-manager/backend/services/recognition_service.py)：
- `_recognize_with_zhipu()`：通过 `httpx.AsyncClient` POST 到智谱 API，发送 base64 图片和 JSON 提示词，解析返回的食材列表
- 新增 `_clean_json_content()` 辅助函数，清理 LLM 返回的 Markdown 代码块标记（OpenAI 和智谱共用）
- 识别链路：OpenAI GPT-4o → 智谱 GLM-4V → 本地预设列表（三级降级）

#### 2. 购物清单持久化

**后端新增文件**：
- `backend/models/shopping_list.py`：`ShoppingListItemModel`（item_id/user_id/name/quantity/checked/timestamps）
- `backend/schemas/shopping_list.py`：Create/Update/BatchCreate/Response Schema
- `backend/services/shopping_list_service.py`：get/add/batch_add/update/delete/clear 服务
- `backend/routers/shopping_list.py`：6 个 API 端点（GET/POST/POST batch/PUT/DELETE/DELETE all）
- `backend/tests/test_shopping_list.py`：7 个测试用例

**前端新增/修改**：
- `frontend/src/api/shoppingList.js`：6 个 API 调用函数
- `frontend/src/components/ShoppingList.jsx`：新增 `onDelete` 回调和删除按钮（Popconfirm 确认）
- `frontend/src/pages/HomePage.jsx`：登录用户从后端加载购物清单；生成菜谱后自动同步缺失食材；演示模式降级为本地计算

#### 3. Alembic 迁移脚本

- `backend/alembic/versions/2026_06_19_0001_initial_schema.py`：创建 users/ingredients/recipes/recipe_ingredients/shopping_list_items 五张表
- 修复 `alembic.ini` 中文注释导致的 GBK 编码问题（改为英文注释）

#### 4. 前端测试与构建优化

- `frontend/tests/ShoppingList.test.jsx`：6 个测试（空状态/字符串数组/对象数组/勾选回调/删除按钮/无删除按钮）
- `frontend/tests/HomePage.test.jsx`：补充 `isDemo`/`demoLogin` mock 和 shoppingList API mock
- `frontend/vite.config.js`：新增 `build.rollupOptions.output.manualChunks` 分包配置

#### 5. E2E 测试完善

- `frontend/e2e/smoke.spec.js`：从 4 个扩展到 11 个用例，新增统计数据/表单/分区标签/生成菜谱/购物清单/登出等场景

### 测试结果

| 测试类型 | 工具 | 结果 |
|----------|------|------|
| 后端单元测试 | pytest | **41 passed**（新增 9 个：智谱 3 + 购物清单 7，减去重复计数） |
| 前端单元测试 | Vitest | **18 passed**（新增 6 个 ShoppingList 测试） |
| 前端生产构建 | vite build | **成功**（4 个 vendor chunk 分包） |
| E2E 测试 | Playwright | **11 个用例**（从 4 个扩展） |

### 代码变更清单

| 文件 | 变更类型 | 说明 |
|------|----------|------|
| `backend/services/recognition_service.py` | 修改 | 实现智谱 GLM-4V 识别；新增 `_clean_json_content()`；OpenAI 解析复用清理函数 |
| `backend/models/shopping_list.py` | 新增 | 购物清单数据模型 |
| `backend/schemas/shopping_list.py` | 新增 | 购物清单 Schema |
| `backend/services/shopping_list_service.py` | 新增 | 购物清单服务层 |
| `backend/routers/shopping_list.py` | 新增 | 购物清单路由（6 个端点） |
| `backend/tests/test_shopping_list.py` | 新增 | 7 个购物清单测试 |
| `backend/tests/test_recognition.py` | 修改 | 新增智谱 GLM-4V 识别和降级测试 |
| `backend/models/__init__.py` | 修改 | 导出 ShoppingListItemModel |
| `backend/models/database.py` | 修改 | init_db 导入 shopping_list 模型 |
| `backend/tests/conftest.py` | 修改 | 导入 shopping_list 模型 |
| `backend/alembic/env.py` | 修改 | 导入 shopping_list 模型 |
| `backend/alembic.ini` | 修改 | 中文注释改英文，修复 GBK 编码问题 |
| `backend/alembic/versions/2026_06_19_0001_initial_schema.py` | 新增 | 初始迁移脚本（5 张表） |
| `backend/main.py` | 修改 | 注册 shopping_list 路由 |
| `frontend/src/api/shoppingList.js` | 新增 | 购物清单 API 调用 |
| `frontend/src/components/ShoppingList.jsx` | 修改 | 新增删除按钮和 onDelete 回调 |
| `frontend/src/pages/HomePage.jsx` | 修改 | 购物清单持久化集成；解构 isDemo/user |
| `frontend/tests/ShoppingList.test.jsx` | 新增 | 6 个 ShoppingList 组件测试 |
| `frontend/tests/HomePage.test.jsx` | 修改 | 补充 isDemo/demoLogin/shoppingList mock |
| `frontend/vite.config.js` | 修改 | 新增手动分包构建优化 |
| `frontend/e2e/smoke.spec.js` | 修改 | 扩展至 11 个 E2E 用例 |

### 未解决问题

1. AI 菜谱详情页刷新时仍会丢失（未持久化到数据库）
2. E2E 测试依赖演示模式，未覆盖真实登录用户流程
3. 购物清单在演示模式下不持久化（仅本地 state）

### 后续计划 (v0.6.0)

1. 持久化 AI 生成菜谱到数据库，支持详情页刷新
2. 推送代码到 GitHub 触发 CI/CD 部署
3. 补充 AuthPage、NutritionPage 组件测试
4. 优化 ECharts 按需导入，进一步减小构建体积

---

## v0.6.0 — AI 菜谱持久化 + 测试覆盖提升 + ECharts 按需导入 (2026-06-19)

### 迭代目标
完成 v0.5.0 遗留任务：将 AI 生成的菜谱持久化到数据库以支持详情页刷新，补充 AuthPage/NutritionPage 前端组件测试，使用 ECharts 按需导入进一步减小构建体积，并推送代码到 GitHub 触发 CI/CD 部署。

### 开发任务清单

| # | 任务 | 优先级 | 状态 |
|---|------|--------|------|
| 1 | AI 生成菜谱持久化到数据库 | 高 | 已完成 |
| 2 | 补充 AuthPage 组件测试 | 中 | 已完成 |
| 3 | 补充 NutritionPage 组件测试 | 中 | 已完成 |
| 4 | ECharts 按需导入优化 | 中 | 已完成 |
| 5 | 推送代码到 GitHub 触发 CI/CD | 高 | 已完成 |

### 技术决策

#### 决策 1：AI 菜谱生成后立即写入数据库
- **方案**：`recommend_recipes()` 调用 OpenAI 生成菜谱后，通过 `_save_ai_recipes_to_db()` 将每道菜谱写入 `recipes` 表和 `recipe_ingredients` 表，返回真实 `recipe_id`（UUID）
- **理由**：前端详情页刷新时可直接通过 `/api/v1/recipes/{recipe_id}` 查询数据库，避免 AI 生成菜谱为临时对象
- **影响**：`backend/services/recipe_service.py`、`backend/models/recipe.py`

#### 决策 2：RecipeModel 添加 relationship 自动加载 ingredients
- **方案**：`RecipeModel` 添加 `ingredients` relationship（`selectin` 加载），`RecipeIngredientModel` 反向关联 `recipe`
- **理由**：查询菜谱详情时一次性加载所有食材，`_recipe_model_to_response()` 可直接从 ORM 对象构建响应
- **影响**：`backend/models/recipe.py`

#### 决策 3：封装按需 ECharts 组件替代 echarts-for-react
- **方案**：新建 `frontend/src/components/ECharts.jsx`，仅导入 `echarts/core`、PieChart、Tooltip、Legend、Grid、CanvasRenderer；`NutritionChart` 改用该组件
- **理由**：`echarts-for-react` 默认引入完整 echarts，按需导入可显著减少 vendor chunk 体积
- **影响**：`frontend/src/components/ECharts.jsx`、`frontend/src/components/NutritionChart.jsx`

#### 决策 4：Mock react-router-dom useNavigate 以测试 AuthPage
- **方案**：在 `AuthPage.test.jsx` 中 mock `useNavigate`，使用 `MemoryRouter` 提供路由上下文
- **理由**：AuthPage 使用 `useNavigate` 跳转，测试环境需要避免真实路由副作用
- **影响**：`frontend/tests/AuthPage.test.jsx`

### 实现详情

#### 1. AI 菜谱持久化

[backend/services/recipe_service.py](file:///D:/Pycharm_workplace/github/fridge-manager/backend/services/recipe_service.py)：
- 新增 `_save_ai_recipes_to_db()`：将 AI 生成的菜谱及食材写入数据库，source 标记为 `ai`
- 新增 `_recipe_model_to_response()`：将 `RecipeModel` ORM 对象转换为 `RecipeResponse`
- `recommend_recipes()`：AI 生成菜谱后先持久化，再返回给前端
- `get_recipe_by_id()`：移除对 `ai-*` 前缀的特殊处理，统一从数据库查询（本地菜谱仍通过 `local-*` 前缀支持）

[backend/models/recipe.py](file:///D:/Pycharm_workplace/github/fridge-manager/backend/models/recipe.py)：
- `RecipeModel` 添加 `ingredients` relationship（`cascade="all, delete-orphan"`、`lazy="selectin"`）
- `RecipeIngredientModel` 添加 `recipe` 反向 relationship

#### 2. 前端测试补充

**AuthPage 测试**（`frontend/tests/AuthPage.test.jsx`）：
- 5 个用例：渲染 Tab、显示品牌和演示按钮、演示模式登录、登录表单提交、注册表单提交
- mock `react-router-dom` 的 `useNavigate` 和 `../src/api/auth` 的 `register`

**NutritionPage 测试**（`frontend/tests/NutritionPage.test.jsx`）：
- 7 个用例：渲染标题、空食材建议、本地分类统计、蛋白质不足建议、蔬菜不足建议、调用后端 API、后端失败兜底
- mock 自定义 `ECharts` 组件避免 jsdom 中 canvas 初始化失败

#### 3. ECharts 按需导入

- `frontend/src/components/ECharts.jsx`：基于 `echarts/core` 只注册饼图、标题/提示/图例/网格组件和 Canvas 渲染器
- `frontend/src/components/NutritionChart.jsx`：移除 `echarts-for-react` 全量导入，改用 `ECharts`
- 构建后 `echarts-vendor` chunk 约 458 KB，与业务代码完全分离

### 测试结果

| 测试类型 | 工具 | 结果 |
|----------|------|------|
| 后端单元测试 | pytest | **42 passed**（新增 1 个 AI 菜谱详情查询测试） |
| 前端单元测试 | Vitest | **30 passed**（新增 12 个：AuthPage 5 + NutritionPage 7） |
| 前端生产构建 | vite build | **成功**（5 个 chunk：react/antd/echarts/utils/index） |
| E2E 测试 | Playwright | **11 个用例** |

### 代码变更清单

| 文件 | 变更类型 | 说明 |
|------|----------|------|
| `backend/services/recipe_service.py` | 修改 | AI 菜谱持久化；新增 `_save_ai_recipes_to_db`/`_recipe_model_to_response` |
| `backend/models/recipe.py` | 修改 | 添加 `ingredients`/`recipe` relationship |
| `backend/tests/test_recipes.py` | 修改 | 更新 AI 测试验证持久化；新增 AI 菜谱详情查询测试 |
| `frontend/src/components/ECharts.jsx` | 新增 | 按需导入 ECharts 的 React 包装组件 |
| `frontend/src/components/NutritionChart.jsx` | 修改 | 改用按需 ECharts 组件 |
| `frontend/tests/AuthPage.test.jsx` | 新增 | 5 个 AuthPage 测试 |
| `frontend/tests/NutritionPage.test.jsx` | 新增 | 7 个 NutritionPage 测试 |
| `frontend/tests/NutritionPage.test.jsx` | 修改 | mock 自定义 ECharts 组件 |

### 未解决问题

1. Ant Design 全量导入导致 `antd-vendor` chunk 仍达 813 KB，后续可改用 `babel-plugin-import` 或 `antd/es/*` 按需导入
2. E2E 测试仍依赖演示模式，未覆盖真实登录用户流程
3. GitHub Actions 部署脚本需要验证 GitHub Pages 是否正常发布

### 后续计划 (v0.7.0)

1. Ant Design 按需导入，进一步减小构建体积
2. 在虚拟机 `192.168.88.151` 上部署后端并验证完整流程
3. 补充 RecipesPage 组件测试
4. 优化 E2E 测试覆盖真实登录场景
