import { createContext, useContext, useState, useCallback, useEffect } from 'react';
import * as authApi from '../api/auth';
import * as ingredientApi from '../api/ingredients';
import { TOKEN_KEY, USER_KEY } from '../config';

// 演示模式预填充食材数据
const DEMO_INGREDIENTS = [
  { ingredient_id: 'd1', name: '西红柿', category: 'vegetable', quantity: 4, unit: '个', storage_location: 'fridge', purchase_date: '2026-06-17', expiry_date: '2026-06-22' },
  { ingredient_id: 'd2', name: '鸡蛋', category: 'dairy', quantity: 8, unit: '个', storage_location: 'fridge', purchase_date: '2026-06-15', expiry_date: '2026-06-28' },
  { ingredient_id: 'd3', name: '牛肉', category: 'meat', quantity: 500, unit: '克', storage_location: 'freezer', purchase_date: '2026-06-14', expiry_date: '2026-06-20' },
  { ingredient_id: 'd4', name: '土豆', category: 'vegetable', quantity: 3, unit: '个', storage_location: 'pantry', purchase_date: '2026-06-12', expiry_date: '2026-07-10' },
  { ingredient_id: 'd5', name: '牛奶', category: 'dairy', quantity: 1, unit: '瓶', storage_location: 'fridge', purchase_date: '2026-06-16', expiry_date: '2026-06-21' },
  { ingredient_id: 'd6', name: '西兰花', category: 'vegetable', quantity: 1, unit: '颗', storage_location: 'fridge', purchase_date: '2026-06-17', expiry_date: '2026-06-24' },
  { ingredient_id: 'd7', name: '香蕉', category: 'fruit', quantity: 5, unit: '根', storage_location: 'pantry', purchase_date: '2026-06-18', expiry_date: '2026-06-23' },
  { ingredient_id: 'd8', name: '洋葱', category: 'vegetable', quantity: 2, unit: '个', storage_location: 'pantry', purchase_date: '2026-06-10', expiry_date: '2026-07-05' },
  { ingredient_id: 'd9', name: '米饭', category: 'staple', quantity: 1, unit: '份', storage_location: 'pantry', purchase_date: '2026-06-18', expiry_date: '2026-06-20' },
  { ingredient_id: 'd10', name: '胡萝卜', category: 'vegetable', quantity: 3, unit: '根', storage_location: 'fridge', purchase_date: '2026-06-15', expiry_date: '2026-06-30' },
  { ingredient_id: 'd11', name: '鸡肉', category: 'meat', quantity: 300, unit: '克', storage_location: 'freezer', purchase_date: '2026-06-13', expiry_date: '2026-06-25' },
  { ingredient_id: 'd12', name: '草莓', category: 'fruit', quantity: 1, unit: '盒', storage_location: 'fridge', purchase_date: '2026-06-18', expiry_date: '2026-06-20' },
];

export const AppContext = createContext(null);

export function AppProvider({ children }) {
  const [user, setUser] = useState(() => {
    const stored = localStorage.getItem(USER_KEY);
    return stored ? JSON.parse(stored) : null;
  });
  const [ingredients, setIngredients] = useState([]);
  const [loading, setLoading] = useState(false);
  const [isDemo, setIsDemo] = useState(() => localStorage.getItem(TOKEN_KEY) === 'demo-token');

  // 登录
  const login = useCallback(async (credentials) => {
    const data = await authApi.login(credentials);
    const { access_token, user: userInfo } = data;
    localStorage.setItem(TOKEN_KEY, access_token);
    localStorage.setItem(USER_KEY, JSON.stringify(userInfo));
    setUser(userInfo);
    setIsDemo(false);
    return userInfo;
  }, []);

  // 演示模式登录（不调用 API，直接设置本地状态 + 预填充数据）
  const demoLogin = useCallback(() => {
    const demoUser = { username: 'demo', user_id: 'demo' };
    localStorage.setItem(TOKEN_KEY, 'demo-token');
    localStorage.setItem(USER_KEY, JSON.stringify(demoUser));
    setUser(demoUser);
    setIsDemo(true);
    setIngredients(DEMO_INGREDIENTS);
    return demoUser;
  }, []);

  // 登出
  const logout = useCallback(async () => {
    if (!isDemo) {
      try {
        await authApi.logout();
      } catch (e) {
        // 忽略登出接口错误
      }
    }
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
    setUser(null);
    setIngredients([]);
    setIsDemo(false);
  }, [isDemo]);

  // 刷新食材列表
  const refreshIngredients = useCallback(async () => {
    if (!user) return [];
    if (isDemo) {
      setIngredients(DEMO_INGREDIENTS);
      return DEMO_INGREDIENTS;
    }
    setLoading(true);
    try {
      const data = await ingredientApi.getIngredients();
      const list = Array.isArray(data) ? data : data?.items || [];
      setIngredients(list);
      return list;
    } catch (e) {
      return [];
    } finally {
      setLoading(false);
    }
  }, [user, isDemo]);

  // 添加食材
  const addIngredient = useCallback(async (ingredient) => {
    if (isDemo) {
      const created = {
        ...ingredient,
        ingredient_id: `d${Date.now()}`,
        category: ingredient.category || 'other',
      };
      setIngredients((prev) => [...prev, created]);
      return created;
    }
    const created = await ingredientApi.createIngredient(ingredient);
    setIngredients((prev) => [...prev, created]);
    return created;
  }, [isDemo]);

  // 移除食材
  const removeIngredient = useCallback(async (id) => {
    if (isDemo) {
      setIngredients((prev) => prev.filter((item) => item.ingredient_id !== id && item.id !== id));
      return;
    }
    await ingredientApi.deleteIngredient(id);
    setIngredients((prev) => prev.filter((item) => item.ingredient_id !== id && item.id !== id));
  }, [isDemo]);

  // 更新食材
  const updateIngredient = useCallback(async (id, data) => {
    if (isDemo) {
      setIngredients((prev) =>
        prev.map((item) =>
          (item.ingredient_id === id || item.id === id) ? { ...item, ...data } : item
        )
      );
      return { ...data };
    }
    const updated = await ingredientApi.updateIngredient(id, data);
    setIngredients((prev) =>
      prev.map((item) =>
        (item.ingredient_id === id || item.id === id) ? { ...item, ...updated } : item
      )
    );
    return updated;
  }, [isDemo]);

  // 登录后加载食材
  useEffect(() => {
    if (user) {
      refreshIngredients();
    }
  }, [user, refreshIngredients]);

  const value = {
    user,
    ingredients,
    loading,
    isDemo,
    login,
    demoLogin,
    logout,
    refreshIngredients,
    addIngredient,
    removeIngredient,
    updateIngredient,
    setIngredients
  };

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
}

export function useApp() {
  const ctx = useContext(AppContext);
  if (!ctx) {
    throw new Error('useApp 必须在 AppProvider 内使用');
  }
  return ctx;
}

export default AppContext;
