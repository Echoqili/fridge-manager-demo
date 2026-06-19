import client from './client';

// 根据食材推荐菜谱
export function recommendRecipes(params) {
  return client.get('/recipes/recommend', { params });
}

// 获取菜谱详情
export function getRecipeById(id) {
  return client.get(`/recipes/${id}`);
}
