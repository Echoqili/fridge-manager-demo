import client from './client';

// 获取食材列表
export function getIngredients(params) {
  return client.get('/ingredients', { params });
}

// 添加食材
export function createIngredient(data) {
  return client.post('/ingredients', data);
}

// 更新食材
export function updateIngredient(id, data) {
  return client.put(`/ingredients/${id}`, data);
}

// 删除食材
export function deleteIngredient(id) {
  return client.delete(`/ingredients/${id}`);
}

// 获取临期食材
export function getExpiringIngredients(days = 3) {
  return client.get('/ingredients/expiring', { params: { days } });
}
