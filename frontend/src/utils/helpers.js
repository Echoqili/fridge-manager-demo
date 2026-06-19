import dayjs from 'dayjs';
import { THEME_COLORS, EXPIRING_SOON_DAYS } from '../config';

// 食材 emoji 映射
const EMOJI_MAP = {
  '西红柿': '🍅', '番茄': '🍅', '鸡蛋': '🥚', '蛋': '🥚',
  '牛奶': '🥛', '酸奶': '🥛', '牛肉': '🥩', '猪肉': '🥓',
  '鸡肉': '🍗', '鱼': '🐟', '虾': '🦐', '胡萝卜': '🥕',
  '土豆': '🥔', '洋葱': '🧅', '大蒜': '🧄', '青椒': '🫑',
  '菠菜': '🥬', '生菜': '🥬', '白菜': '🥬', '西兰花': '🥦',
  '苹果': '🍎', '香蕉': '🍌', '橙子': '🍊', '葡萄': '🍇',
  '草莓': '🍓', '西瓜': '🍉', '米饭': '🍚', '面条': '🍜',
  '面包': '🍞', '豆腐': '🧈', '芝士': '🧀', '黄油': '🧈',
  '蘑菇': '🍄', '玉米': '🌽', '茄子': '🍆', '黄瓜': '🥒',
  '柠檬': '🍋', '葱': '🌱', '姜': '🫚'
};

// 食材分类关键词
const CATEGORY_KEYWORDS = {
  vegetable: ['西红柿', '番茄', '胡萝卜', '土豆', '洋葱', '大蒜', '青椒', '菠菜', '生菜', '白菜', '西兰花', '黄瓜', '茄子', '蘑菇', '玉米', '葱', '姜'],
  meat: ['牛肉', '猪肉', '鸡肉', '鱼', '虾'],
  dairy: ['鸡蛋', '蛋', '牛奶', '酸奶', '豆腐', '芝士', '黄油'],
  staple: ['米饭', '面条', '面包'],
  fruit: ['苹果', '香蕉', '橙子', '葡萄', '草莓', '西瓜', '柠檬']
};

// 格式化日期
export function formatDate(date, format = 'YYYY-MM-DD') {
  if (!date) return '';
  return dayjs(date).format(format);
}

// 判断是否即将过期
export function isExpiringSoon(ingredient, days = EXPIRING_SOON_DAYS) {
  if (!ingredient.expiry_date && ingredient.daysLeft === undefined) {
    return false;
  }
  const daysLeft = ingredient.daysLeft !== undefined
    ? ingredient.daysLeft
    : dayjs(ingredient.expiry_date).diff(dayjs(), 'day');
  return daysLeft <= days;
}

// 根据食材名称获取 emoji
export function getEmoji(name) {
  if (!name) return '🍽';
  for (const key in EMOJI_MAP) {
    if (name.includes(key)) return EMOJI_MAP[key];
  }
  return '🍽';
}

// 根据食材名称推断分类
export function inferCategory(name) {
  if (!name) return 'other';
  for (const [cat, keys] of Object.entries(CATEGORY_KEYWORDS)) {
    if (keys.some((k) => name.includes(k))) return cat;
  }
  return 'other';
}

// 获取分类颜色
export function getCategoryColor(category) {
  const colorMap = {
    vegetable: THEME_COLORS.sage,
    meat: THEME_COLORS.terracotta,
    dairy: '#E8C547',
    staple: THEME_COLORS.mustard,
    fruit: '#F4A261',
    other: THEME_COLORS.stone
  };
  return colorMap[category] || colorMap.other;
}

// 获取分类图标（emoji）
export function getCategoryIcon(category) {
  const iconMap = {
    vegetable: '🥬',
    meat: '🥩',
    dairy: '🥚',
    staple: '🍚',
    fruit: '🍎',
    other: '🍽'
  };
  return iconMap[category] || iconMap.other;
}

// 计算预计节省金额（临期食材优先消耗）
export function calculateSavings(ingredients) {
  if (!Array.isArray(ingredients)) return 0;
  return ingredients.reduce((sum, item) => {
    if (isExpiringSoon(item)) {
      return sum + 8;
    }
    return sum;
  }, 0);
}

// 获取分类统计
export function getCategoryStats(ingredients) {
  const stats = { vegetable: 0, meat: 0, dairy: 0, staple: 0, fruit: 0, other: 0 };
  ingredients.forEach((item) => {
    const cat = item.category || inferCategory(item.name);
    stats[cat] = (stats[cat] || 0) + (item.quantity || item.qty || 1);
  });
  return stats;
}
