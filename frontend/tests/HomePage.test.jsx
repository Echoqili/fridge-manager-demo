import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { ConfigProvider, App as AntApp } from 'antd';
import HomePage from '../src/pages/HomePage';
import { AppProvider, AppContext } from '../src/contexts/AppContext';

// Mock API 模块
vi.mock('../src/api/ingredients', () => ({
  getIngredients: vi.fn(() => Promise.resolve([])),
  createIngredient: vi.fn(),
  updateIngredient: vi.fn(),
  deleteIngredient: vi.fn(() => Promise.resolve()),
  getExpiringIngredients: vi.fn()
}));

vi.mock('../src/api/recipes', () => ({
  recommendRecipes: vi.fn(() => Promise.resolve([])),
  getRecipeById: vi.fn()
}));

vi.mock('../src/api/recognition', () => ({
  recognizeImage: vi.fn()
}));

vi.mock('../src/api/nutrition', () => ({
  getNutritionSummary: vi.fn(() => Promise.resolve({}))
}));

vi.mock('../src/api/shoppingList', () => ({
  getShoppingList: vi.fn(() => Promise.resolve([])),
  addShoppingItem: vi.fn(),
  batchAddShoppingItems: vi.fn(() => Promise.resolve([])),
  updateShoppingItem: vi.fn(),
  deleteShoppingItem: vi.fn(),
  clearShoppingList: vi.fn()
}));

vi.mock('../src/api/auth', () => ({
  login: vi.fn(),
  register: vi.fn(),
  refresh: vi.fn(),
  logout: vi.fn(),
  getMe: vi.fn()
}));

const mockIngredients = [
  { ingredient_id: '1', name: '西红柿', quantity: 3, storage_location: 'crisper', daysLeft: 2, category: 'vegetable' },
  { ingredient_id: '2', name: '鸡蛋', quantity: 6, storage_location: 'fridge', daysLeft: 7, category: 'protein' },
  { ingredient_id: '3', name: '牛奶', quantity: 1, storage_location: 'fridge', daysLeft: 4, category: 'protein' }
];

function renderWithProviders(ui, { ingredients = [], user = { username: 'test' } } = {}) {
  const value = {
    user,
    ingredients,
    loading: false,
    isDemo: false,
    login: vi.fn(),
    demoLogin: vi.fn(),
    logout: vi.fn(),
    refreshIngredients: vi.fn(),
    addIngredient: vi.fn(),
    removeIngredient: vi.fn(),
    updateIngredient: vi.fn(),
    setIngredients: vi.fn()
  };

  return render(
    <ConfigProvider>
      <AntApp>
        <MemoryRouter>
          <AppContext.Provider value={value}>{ui}</AppContext.Provider>
        </MemoryRouter>
      </AntApp>
    </ConfigProvider>
  );
}

describe('HomePage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('应该渲染首页标题和看板', async () => {
    renderWithProviders(<HomePage />, { ingredients: [] });
    expect(screen.getByTestId('home-page')).toBeInTheDocument();
    expect(screen.getByText('打开冰箱，就知道今天吃什么')).toBeInTheDocument();
  });

  it('应该显示食材统计数据', async () => {
    renderWithProviders(<HomePage />, { ingredients: mockIngredients });
    await waitFor(() => {
      expect(screen.getByText('冰箱食材')).toBeInTheDocument();
      expect(screen.getByText('即将过期')).toBeInTheDocument();
      expect(screen.getByText('可做菜谱')).toBeInTheDocument();
    });
  });

  it('空冰箱时显示空状态', () => {
    renderWithProviders(<HomePage />, { ingredients: [] });
    expect(screen.getByText('冰箱还是空的，拍张照片或手动添加食材吧')).toBeInTheDocument();
  });

  it('有食材时显示食材卡片', async () => {
    renderWithProviders(<HomePage />, { ingredients: mockIngredients });
    await waitFor(() => {
      const cards = screen.getAllByTestId('ingredient-card');
      expect(cards.length).toBeGreaterThan(0);
    });
  });

  it('显示手动添加表单', () => {
    renderWithProviders(<HomePage />, { ingredients: [] });
    expect(screen.getByPlaceholderText('食材名称，如：西红柿')).toBeInTheDocument();
  });
});
