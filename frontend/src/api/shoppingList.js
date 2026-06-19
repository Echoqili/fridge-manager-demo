import client from './client';

// 获取购物清单
export function getShoppingList() {
  return client.get('/shopping-list');
}

// 添加购物清单条目
export function addShoppingItem(item) {
  return client.post('/shopping-list', item);
}

// 批量添加购物清单条目
export function batchAddShoppingItems(items) {
  return client.post('/shopping-list/batch', { items });
}

// 更新购物清单条目（勾选/改名/改数量）
export function updateShoppingItem(itemId, data) {
  return client.put(`/shopping-list/${itemId}`, data);
}

// 删除购物清单条目
export function deleteShoppingItem(itemId) {
  return client.delete(`/shopping-list/${itemId}`);
}

// 清空购物清单
export function clearShoppingList() {
  return client.delete('/shopping-list');
}
