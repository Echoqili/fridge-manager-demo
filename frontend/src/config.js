// 前端全局配置
export const API_BASE_URL = '/api/v1';

export const TOKEN_KEY = 'fridge_token';
export const REFRESH_TOKEN_KEY = 'fridge_refresh_token';
export const USER_KEY = 'fridge_user';

// 主题色：与原 Demo 保持一致
export const THEME_COLORS = {
  cream: '#FFFDF7',
  sage: '#7C9A6B',
  sageLight: '#E8F0E4',
  sageDark: '#5A7550',
  terracotta: '#E07A5F',
  terracottaLight: '#FCEAE6',
  mustard: '#F2CC8F',
  mustardLight: '#FDF5E8',
  charcoal: '#3D405B',
  stone: '#6B7280',
  snow: '#FFFFFF'
};

// 食材分类
export const CATEGORIES = {
  vegetable: '蔬菜',
  meat: '肉类',
  dairy: '蛋奶',
  staple: '主食',
  fruit: '水果',
  other: '其他'
};

// 存放位置
export const STORAGE_LOCATIONS = {
  fridge: '冷藏室',
  freezer: '冷冻室',
  crisper: '蔬果室',
  pantry: '常温柜'
};

// 临期阈值（天）
export const EXPIRING_SOON_DAYS = 2;
