# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: smoke.spec.js >> 点击菜谱推荐导航
- Location: e2e\smoke.spec.js:16:1

# Error details

```
Test timeout of 60000ms exceeded.
```

```
Error: page.click: Test timeout of 60000ms exceeded.
Call log:
  - waiting for locator('text=菜谱推荐')

```

# Page snapshot

```yaml
- generic [ref=e7]:
  - generic [ref=e9]:
    - generic [ref=e10]: 🥦
    - heading "鲜知 fridge" [level=3] [ref=e11]
    - text: AI 冰箱管家 · 剩菜变菜谱，过期早知道
  - generic [ref=e13]:
    - tablist [ref=e14]:
      - generic [ref=e16]:
        - tab "登录" [selected] [ref=e18] [cursor=pointer]
        - tab "注册" [ref=e20] [cursor=pointer]
    - tabpanel "登录" [ref=e23]:
      - generic [ref=e24]:
        - generic [ref=e26]:
          - generic "用户名" [ref=e28]
          - generic [ref=e32]:
            - img "user" [ref=e34]:
              - img [ref=e35]
            - textbox "用户名" [ref=e37]:
              - /placeholder: 请输入用户名
        - generic [ref=e39]:
          - generic "密码" [ref=e41]
          - generic [ref=e45]:
            - img "lock" [ref=e47]:
              - img [ref=e48]
            - textbox "密码" [ref=e50]:
              - /placeholder: 请输入密码
            - img "eye-invisible" [ref=e52] [cursor=pointer]:
              - img [ref=e53]
        - button "登 录" [ref=e56] [cursor=pointer]:
          - generic [ref=e57]: 登 录
  - generic [ref=e59]:
    - generic [ref=e60]: 或者
    - button "🚀 演示模式快速体验" [ref=e61] [cursor=pointer]:
      - generic [ref=e62]: 🚀 演示模式快速体验
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
  13 |   await expect(page.locator('text=打开冰箱，就知道今天吃什么')).toBeVisible({ timeout: 15000 });
  14 | });
  15 | 
  16 | test('点击菜谱推荐导航', async ({ page }) => {
  17 |   // 先进入演示模式
  18 |   await page.goto('/login');
  19 |   await page.click('text=演示模式快速体验');
  20 |   await page.waitForURL('**/');
  21 |   // 点击菜谱推荐菜单
> 22 |   await page.click('text=菜谱推荐');
     |              ^ Error: page.click: Test timeout of 60000ms exceeded.
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