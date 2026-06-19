import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { ConfigProvider } from 'antd';
import NutritionPage from '../src/pages/NutritionPage';
import { AppContext } from '../src/contexts/AppContext';
import { getNutritionSummary } from '../src/api/nutrition';



// mock 自定义 ECharts 组件，避免 jsdom 中 canvas 初始化失败
vi.mock('../src/components/ECharts', () => ({
  default: function MockECharts({ option }) {
    return <div data-testid="echarts-mock">{JSON.stringify(option)}</div>;
  }
}));

vi.mock('../src/api/nutrition', () => ({
  getNutritionSummary: vi.fn()
}));

function renderPage(contextValue = {}) {
  const value = {
    ingredients: [],
    ...contextValue
  };
  return render(
    <ConfigProvider>
      <AppContext.Provider value={value}>
        <NutritionPage />
      </AppContext.Provider>
    </ConfigProvider>
  );
}

describe('NutritionPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('渲染页面标题', () => {
    renderPage();
    expect(screen.getByText('营养洞察')).toBeInTheDocument();
    expect(screen.getByText('了解你的冰箱营养构成，AI 给出均衡饮食建议')).toBeInTheDocument();
  });

  it('空食材时显示默认 AI 建议', () => {
    renderPage();
    expect(screen.getByText('添加食材后，我会根据你的库存给出营养搭配建议。')).toBeInTheDocument();
  });

  it('根据食材显示本地分类统计', () => {
    const ingredients = [
      { name: '西红柿', category: 'vegetable' },
      { name: '鸡蛋', category: 'dairy' },
      { name: '牛肉', category: 'meat' }
    ];
    renderPage({ ingredients });
    expect(screen.getByText('🥬 蔬菜类').closest('.ant-statistic').querySelector('.ant-statistic-content-value')).toHaveTextContent('1');
    expect(screen.getByText('🥩 肉类').closest('.ant-statistic').querySelector('.ant-statistic-content-value')).toHaveTextContent('1');
    expect(screen.getByText('🥚 蛋奶类').closest('.ant-statistic').querySelector('.ant-statistic-content-value')).toHaveTextContent('1');
  });

  it('蛋白质不足时给出建议', () => {
    renderPage({ ingredients: [{ name: '西红柿', category: 'vegetable' }] });
    expect(screen.getByText('本周蛋白质摄入偏少，建议补充鸡蛋、牛奶或肉类。')).toBeInTheDocument();
  });

  it('蔬菜不足时给出建议', () => {
    renderPage({ ingredients: [{ name: '牛肉', category: 'meat' }] });
    expect(screen.getByText('蔬菜库存不足，记得采购新鲜蔬菜平衡膳食。')).toBeInTheDocument();
  });

  it('调用后端营养摘要 API', async () => {
    getNutritionSummary.mockResolvedValue({ vegetable: 2, meat: 1 });
    renderPage({ ingredients: [] });
    await waitFor(() => {
      expect(getNutritionSummary).toHaveBeenCalledTimes(1);
    });
  });

  it('后端失败时使用本地统计', async () => {
    getNutritionSummary.mockRejectedValue(new Error('network error'));
    renderPage({ ingredients: [{ name: '苹果', category: 'fruit' }] });
    await waitFor(() => {
      expect(getNutritionSummary).toHaveBeenCalledTimes(1);
    });
    expect(screen.getByText('🍎 水果').closest('.ant-statistic').querySelector('.ant-statistic-content-value')).toHaveTextContent('1');
  });
});
