import { test, expect } from '@playwright/test';

// 真实后端登录/注册 E2E 测试
// 用法：E2E_REAL_BACKEND_URL=http://192.168.88.151:8000 npx playwright test e2e/auth-real.spec.js
// 未设置该环境变量时自动跳过，避免在 CI 中失败
const backendUrl = process.env.E2E_REAL_BACKEND_URL;

test.describe('真实后端登录场景', () => {
  test.beforeEach(async ({ page }) => {
    if (!backendUrl) {
      test.skip();
    }
    await page.goto('/login');
  });

  test('新用户注册并登录后进入首页', async ({ page }) => {
    const timestamp = Date.now();
    const username = `e2e_user_${timestamp}`;
    const email = `e2e_${timestamp}@example.com`;
    const password = 'Test@123456';

    // 切换到注册 Tab
    await page.click('text=注册');
    await expect(page.locator('text=注册成功，请登录')).not.toBeVisible();

    // 填写注册表单（限定在当前活动 Tab，避免与登录表单冲突）
    const registerPane = page.locator('.ant-tabs-tabpane-active');
    await registerPane.locator('input[placeholder="请输入用户名"]').fill(username);
    await registerPane.locator('input[placeholder="请输入邮箱"]').fill(email);
    await registerPane.locator('input[placeholder="请输入密码"]').fill(password);
    await registerPane.locator('button[type="submit"]').click();

    // 等待注册成功提示并自动回到登录 Tab
    await expect(page.locator('.ant-message-notice:has-text("注册成功")')).toBeVisible({ timeout: 15000 });

    // 登录
    const loginPane = page.locator('.ant-tabs-tabpane-active');
    await loginPane.locator('input[placeholder="请输入用户名"]').fill(username);
    await loginPane.locator('input[placeholder="请输入密码"]').fill(password);
    await loginPane.locator('button[type="submit"]').click();

    // 验证进入首页
    await expect(page).toHaveURL('http://localhost:3000/');
    await expect(page.locator('text=打开冰箱，就知道今天吃什么')).toBeVisible({ timeout: 15000 });

    // 验证登录态已持久化
    const token = await page.evaluate(() => localStorage.getItem('fridge_token'));
    expect(token).toBeTruthy();

    const user = await page.evaluate(() => localStorage.getItem('fridge_user'));
    expect(user).toContain(username);
  });

  test('登录后可添加食材并在列表中查看', async ({ page }) => {
    const timestamp = Date.now();
    const username = `e2e_user_${timestamp}`;
    const email = `e2e_${timestamp}@example.com`;
    const password = 'Test@123456';

    // 注册
    await page.click('text=注册');
    const registerPane2 = page.locator('.ant-tabs-tabpane-active');
    await registerPane2.locator('input[placeholder="请输入用户名"]').fill(username);
    await registerPane2.locator('input[placeholder="请输入邮箱"]').fill(email);
    await registerPane2.locator('input[placeholder="请输入密码"]').fill(password);
    await registerPane2.locator('button[type="submit"]').click();
    await expect(page.locator('.ant-message-notice:has-text("注册成功")')).toBeVisible({ timeout: 15000 });

    // 登录
    const loginPane2 = page.locator('.ant-tabs-tabpane-active');
    await loginPane2.locator('input[placeholder="请输入用户名"]').fill(username);
    await loginPane2.locator('input[placeholder="请输入密码"]').fill(password);
    await loginPane2.locator('button[type="submit"]').click();
    await expect(page).toHaveURL('http://localhost:3000/');
    await expect(page.locator('text=打开冰箱，就知道今天吃什么')).toBeVisible({ timeout: 15000 });

    // 添加食材（通过回车提交，避免 Ant Design 按钮文本空格导致选择器不匹配）
    await page.locator('input[placeholder="食材名称，如：西红柿"]').fill('E2E测试牛肉');
    await page.locator('input[placeholder="数量"]').fill('2');
    await page.locator('input[placeholder="食材名称，如：西红柿"]').press('Enter');

    // 确认食材出现在列表中
    await expect(page.locator('text=E2E测试牛肉').first()).toBeVisible({ timeout: 15000 });

    // 验证后端持久化：刷新页面后仍然存在
    await page.reload();
    await expect(page.locator('text=E2E测试牛肉').first()).toBeVisible({ timeout: 15000 });
  });
});
