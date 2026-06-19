import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ConfigProvider, App } from 'antd';
import { MemoryRouter } from 'react-router-dom';
import AuthPage from '../src/pages/AuthPage';
import { AppContext } from '../src/contexts/AppContext';
import * as authApi from '../src/api/auth';

// mock auth api
vi.mock('../src/api/auth', () => ({
  register: vi.fn()
}));

const mockedNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockedNavigate
  };
});

function renderPage(contextValue = {}) {
  const value = {
    user: null,
    login: vi.fn(),
    demoLogin: vi.fn(),
    logout: vi.fn(),
    ...contextValue
  };
  return render(
    <MemoryRouter>
      <App>
        <ConfigProvider>
          <AppContext.Provider value={value}>
            <AuthPage />
          </AppContext.Provider>
        </ConfigProvider>
      </App>
    </MemoryRouter>
  );
}

describe('AuthPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('渲染登录和注册 Tab', () => {
    renderPage();
    expect(screen.getByText('登录')).toBeInTheDocument();
    expect(screen.getByText('注册')).toBeInTheDocument();
  });

  it('显示品牌标题和演示模式按钮', () => {
    renderPage();
    expect(screen.getByText('鲜知 fridge')).toBeInTheDocument();
    expect(screen.getByText('🚀 演示模式快速体验')).toBeInTheDocument();
  });

  it('点击演示模式调用 demoLogin 并跳转', async () => {
    const demoLogin = vi.fn();
    renderPage({ demoLogin });
    const demoBtn = screen.getByText('🚀 演示模式快速体验');
    await userEvent.click(demoBtn);
    await waitFor(() => {
      expect(demoLogin).toHaveBeenCalledTimes(1);
    });
  });

  it('登录表单提交时调用 login', async () => {
    const login = vi.fn().mockResolvedValue(undefined);
    renderPage({ login });

    await userEvent.type(screen.getByPlaceholderText('请输入用户名'), 'testuser');
    await userEvent.type(screen.getByPlaceholderText('请输入密码'), 'password123');
    fireEvent.click(screen.getByRole('button', { name: /登\s*录/i }));

    await waitFor(() => {
      expect(login).toHaveBeenCalledWith({ username: 'testuser', password: 'password123' });
    });
  });

  it('切换到注册 Tab 并提交注册表单', async () => {
    authApi.register.mockResolvedValue({});
    renderPage();

    await userEvent.click(screen.getByText('注册'));
    await userEvent.type(screen.getAllByPlaceholderText('请输入用户名')[1], 'newuser');
    await userEvent.type(screen.getByPlaceholderText('请输入邮箱'), 'new@example.com');
    await userEvent.type(screen.getAllByPlaceholderText('请输入密码')[1], '123456');
    fireEvent.click(screen.getByRole('button', { name: /注\s*册/i }));

    await waitFor(() => {
      expect(authApi.register).toHaveBeenCalledWith({
        username: 'newuser',
        email: 'new@example.com',
        password: '123456'
      });
    });
  });
});
