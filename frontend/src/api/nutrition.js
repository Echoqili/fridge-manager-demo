import client from './client';

// 获取营养摄入统计
export function getNutritionSummary(params) {
  return client.get('/nutrition/summary', { params });
}
