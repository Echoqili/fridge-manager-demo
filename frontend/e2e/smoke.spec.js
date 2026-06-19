import { test, expect } from '@playwright/test';

// 演示模式登录辅助
async function demoLogin(page) {
  await page.goto('/login');
  await page.click('text=演示模式快速体验');
  await page.waitForURL('**/');
}

test('打开首页看到冰箱看板', async ({ page }) => {
  await page.goto('/');
  // 应该跳转到登录页或首页
  await expect(page).toHaveURL(/\/(login)?$/);
});

test('演示模式登录后看到冰箱看板', async ({ page }) => {
  await demoLogin(page);
  await expect(page.locator('text=打开冰箱，就知道今天吃什么')).toBeVisible({ timeout: 15000 });
});

test('点击菜谱推荐导航', async ({ page }) => {
  await demoLogin(page);
  await page.click('text=菜谱推荐');
  await expect(page).toHaveURL('**/recipes');
  await expect(page.locator('text=菜谱推荐').first()).toBeVisible({ timeout: 15000 });
});

test('查看营养洞察页', async ({ page }) => {
  await demoLogin(page);
  await page.click('text=营养洞察');
  await expect(page).toHaveURL('**/nutrition');
});

test('首页显示统计数据', async ({ page }) => {
  await demoLogin(page);
  await expect(page.locator('text=冰箱食材')).toBeVisible({ timeout: 15000 });
  await expect(page.locator('text=即将过期')).toBeVisible();
  await expect(page.locator('text=可做菜谱')).toBeVisible();
});

test('首页显示手动添加食材表单', async ({ page }) => {
  await demoLogin(page);
  await expect(page.locator('text=➕ 手动添加食材')).toBeVisible({ timeout: 15000 });
  await expect(page.locator('input[placeholder*="食材名称"]')).toBeVisible();
});

test('首页显示冰箱分区标签', async ({ page }) => {
  await demoLogin(page);
  await expect(page.locator('text=我的冰箱')).toBeVisible({ timeout: 15000 });
  // 应该有冷藏、冷冻等标签
  const tabs = page.locator('.ant-tabs-tab');
  await expect(tabs.first()).toBeVisible();
});

test('点击生成菜谱按钮', async ({ page }) => {
  await demoLogin(page);
  // 等待页面加载
  await expect(page.locator('text=AI 推荐菜谱')).toBeVisible({ timeout: 15000 });
  // 点击生成菜谱
  await page.click('text=生成菜谱');
  // 等待菜谱加载或提示
  await page.waitForTimeout(3000);
  // 应该显示菜谱卡片或提示信息
  const hasRecipe = await page.locator('[data-testid="recipe-card"]').count();
  const hasMessage = await page.locator('.ant-message-notice').count();
  expect(hasRecipe + hasMessage).toBeGreaterThan(0);
});

test('购物清单区域可见', async ({ page }) => {
  await demoLogin(page);
  await expect(page.locator('text=购物清单')).toBeVisible({ timeout: 15000 });
});

test('登出演示模式', async ({ page }) => {
  await demoLogin(page);
  await page.waitForTimeout(1000);
  // 点击退出按钮（可能在头部或侧边栏）
  const logoutBtn = page.locator('text=退出').or(page.locator('text=登出')).or(page.locator('text=注销'));
  if (await logoutBtn.count() > 0) {
    await logoutBtn.first().click();
    await page.waitForTimeout(2000);
    // 应该返回登录页或首页
    await expect(page).toHaveURL(/\/(login)?$/);
  }
});
