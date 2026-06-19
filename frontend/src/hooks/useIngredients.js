import { useState, useCallback } from 'react';
import { useApp } from '../contexts/AppContext';
import * as ingredientApi from '../api/ingredients';

// 食材管理 Hook：获取列表、添加、删除、更新
export function useIngredients() {
  const { ingredients, setIngredients, addIngredient: ctxAdd, removeIngredient: ctxRemove, updateIngredient: ctxUpdate } = useApp();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // 获取食材列表
  const fetchIngredients = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await ingredientApi.getIngredients();
      const list = Array.isArray(data) ? data : data?.items || [];
      setIngredients(list);
      return list;
    } catch (e) {
      setError(e.message || '获取食材失败');
      return [];
    } finally {
      setLoading(false);
    }
  }, [setIngredients]);

  // 添加食材
  const addIngredient = useCallback(async (ingredient) => {
    setError(null);
    try {
      return await ctxAdd(ingredient);
    } catch (e) {
      setError(e.message || '添加食材失败');
      throw e;
    }
  }, [ctxAdd]);

  // 删除食材
  const deleteIngredient = useCallback(async (id) => {
    setError(null);
    try {
      await ctxRemove(id);
    } catch (e) {
      setError(e.message || '删除食材失败');
      throw e;
    }
  }, [ctxRemove]);

  // 更新食材
  const updateIngredient = useCallback(async (id, data) => {
    setError(null);
    try {
      return await ctxUpdate(id, data);
    } catch (e) {
      setError(e.message || '更新食材失败');
      throw e;
    }
  }, [ctxUpdate]);

  // 获取临期食材
  const fetchExpiring = useCallback(async (days = 3) => {
    try {
      return await ingredientApi.getExpiringIngredients(days);
    } catch (e) {
      setError(e.message || '获取临期食材失败');
      return [];
    }
  }, []);

  return {
    ingredients,
    loading,
    error,
    fetchIngredients,
    addIngredient,
    deleteIngredient,
    updateIngredient,
    fetchExpiring
  };
}

export default useIngredients;
