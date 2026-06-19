import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { ConfigProvider } from 'antd';
import RecipeCard from '../src/components/RecipeCard';

const mockRecipe = {
  recipe_id: 'r1',
  name: '西红柿炒鸡蛋',
  tags: ['家常', '快手'],
  cook_time: 10,
  calories: 280,
  servings: 2,
  need: ['西红柿', '鸡蛋'],
  steps: ['步骤一', '步骤二']
};

function renderCard(props = {}) {
  return render(
    <ConfigProvider>
      <RecipeCard recipe={mockRecipe} {...props} />
    </ConfigProvider>
  );
}

describe('RecipeCard', () => {
  it('应该渲染菜谱名称', () => {
    renderCard();
    expect(screen.getByText('西红柿炒鸡蛋')).toBeInTheDocument();
  });

  it('应该显示烹饪时间、热量、份数', () => {
    renderCard();
    expect(screen.getByText(/10 分钟/)).toBeInTheDocument();
    expect(screen.getByText(/280 kcal/)).toBeInTheDocument();
    expect(screen.getByText(/2 人份/)).toBeInTheDocument();
  });

  it('应该显示标签', () => {
    renderCard();
    expect(screen.getByText('家常')).toBeInTheDocument();
    expect(screen.getByText('快手')).toBeInTheDocument();
  });

  it('应该显示所需食材', () => {
    renderCard();
    expect(screen.getByText('西红柿')).toBeInTheDocument();
    expect(screen.getByText('鸡蛋')).toBeInTheDocument();
  });

  it('点击时触发 onClick 回调', () => {
    const onClick = vi.fn();
    renderCard({ onClick });
    fireEvent.click(screen.getByTestId('recipe-card'));
    expect(onClick).toHaveBeenCalledWith(mockRecipe);
  });

  it('没有图片时显示默认 emoji', () => {
    renderCard();
    expect(screen.getByText('🍳')).toBeInTheDocument();
  });

  it('有图片时显示图片', () => {
    render(
      <ConfigProvider>
        <RecipeCard recipe={{ ...mockRecipe, image_url: 'https://example.com/img.jpg' }} />
      </ConfigProvider>
    );
    const img = screen.getByAltText('西红柿炒鸡蛋');
    expect(img).toBeInTheDocument();
    expect(img.src).toBe('https://example.com/img.jpg');
  });
});
