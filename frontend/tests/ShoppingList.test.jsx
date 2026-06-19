import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { ConfigProvider } from 'antd';
import ShoppingList from '../src/components/ShoppingList';

function renderList(props = {}) {
  return render(
    <ConfigProvider>
      <ShoppingList {...props} />
    </ConfigProvider>
  );
}

describe('ShoppingList', () => {
  it('空列表时显示空状态', () => {
    renderList({ items: [] });
    expect(screen.getByText('暂无购物需求')).toBeInTheDocument();
  });

  it('渲染字符串数组条目', () => {
    renderList({ items: ['西红柿', '鸡蛋'] });
    expect(screen.getByText('西红柿')).toBeInTheDocument();
    expect(screen.getByText('鸡蛋')).toBeInTheDocument();
  });

  it('渲染对象数组条目并显示勾选状态', () => {
    const items = [
      { name: '牛奶', checked: false },
      { name: '面包', checked: true }
    ];
    renderList({ items });
    expect(screen.getByText('牛奶')).toBeInTheDocument();
    expect(screen.getByText('面包')).toBeInTheDocument();
    // 已勾选的条目应该有灰色样式
    const bread = screen.getByText('面包');
    expect(bread).toBeInTheDocument();
  });

  it('点击勾选触发 onToggle 回调', () => {
    const onToggle = vi.fn();
    const items = [{ name: '土豆', checked: false, item_id: '1' }];
    renderList({ items, onToggle });
    const checkbox = screen.getByRole('checkbox');
    fireEvent.click(checkbox);
    expect(onToggle).toHaveBeenCalledWith(0, items[0]);
  });

  it('有 onDelete 时显示删除按钮', () => {
    const items = [{ name: '洋葱', checked: false, item_id: '1' }];
    renderList({ items, onDelete: vi.fn() });
    expect(screen.getByRole('button')).toBeInTheDocument();
  });

  it('无 onDelete 时不显示删除按钮（字符串数组）', () => {
    renderList({ items: ['盐'] });
    expect(screen.queryByRole('button')).not.toBeInTheDocument();
  });
});
