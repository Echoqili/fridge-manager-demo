# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: smoke.spec.js >> 演示模式登录后看到冰箱看板
- Location: e2e\smoke.spec.js:9:1

# Error details

```
Error: expect(locator).toBeVisible() failed

Locator: locator('text=打开冰箱，就知道今天吃什么')
Expected: visible
Timeout: 15000ms
Error: element(s) not found

Call log:
  - Expect "toBeVisible" with timeout 15000ms
  - waiting for locator('text=打开冰箱，就知道今天吃什么')
    - waiting for" http://localhost:3000/login" navigation to finish...
    - navigated to "http://localhost:3000/login"

```

```yaml
- text: 🥦
- heading "鲜知 fridge" [level=3]
- text: AI 冰箱管家 · 剩菜变菜谱，过期早知道
- tablist:
  - tab "登录" [selected]
  - tab "注册"
- tabpanel "登录":
  - text: 用户名
  - img "user"
  - textbox "用户名":
    - /placeholder: 请输入用户名
  - text: 密码
  - img "lock"
  - textbox "密码":
    - /placeholder: 请输入密码
  - img "eye-invisible"
  - button "登 录"
- text: 或者
- button "🚀 演示模式快速体验"
```

# Test source

```ts
  1  | import { test, expect } from '@playwright/test';
  2  | 
  3  | test('打开首页看到冰箱看板', async ({ page }) => {
  4  |   await page.goto('/');
  5  |   // 应该跳转到登录页或首页
  6  |   await expect(page).toHaveURL(/\/(login)?$/);
  7  | });
  8  | 
  9  | test('演示模式登录后看到冰箱看板', async ({ page }) => {
  10 |   await page.goto('/login');
  11 |   await page.click('text=演示模式快速体验');
  12 |   await page.waitForURL('**/');
> 13 |   await expect(page.locator('text=打开冰箱，就知道今天吃什么')).toBeVisible({ timeout: 15000 });
     |                                                    ^ Error: expect(locator).toBeVisible() failed
  14 | });
  15 | 
  16 | test('点击菜谱推荐导航', async ({ page }) => {
  17 |   // 先进入演示模式
  18 |   await page.goto('/login');
  19 |   await page.click('text=演示模式快速体验');
  20 |   await page.waitForURL('**/');
  21 |   // 点击菜谱推荐菜单
  22 |   await page.click('text=菜谱推荐');
  23 |   await expect(page).toHaveURL('**/recipes');
  24 |   await expect(page.locator('text=菜谱推荐').first()).toBeVisible({ timeout: 15000 });
  25 | });
  26 | 
  27 | test('查看营养洞察页', async ({ page }) => {
  28 |   await page.goto('/login');
  29 |   await page.click('text=演示模式快速体验');
  30 |   await page.waitForURL('**/');
  31 |   await page.click('text=营养洞察');
  32 |   await expect(page).toHaveURL('**/nutrition');
  33 | });
  34 | 
```