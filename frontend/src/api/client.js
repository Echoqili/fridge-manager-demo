import axios from 'axios';
import { API_BASE_URL, TOKEN_KEY } from '../config';

// Axios 实例
const client = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json'
  }
});

// 请求拦截器：添加 Authorization Bearer token
client.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem(TOKEN_KEY);
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// 响应拦截器：统一响应格式处理 + 401 跳转登录
client.interceptors.response.use(
  (response) => {
    // 统一响应处理：response.data.data 提取数据
    const payload = response.data;
    if (payload && typeof payload === 'object' && 'code' in payload) {
      if (payload.code === 0) {
        return payload.data;
      }
      // 业务错误
      const error = new Error(payload.message || '请求失败');
      error.code = payload.code;
      error.detail = payload.detail;
      return Promise.reject(error);
    }
    return payload;
  },
  (error) => {
    const { response } = error;
    if (response && response.status === 401) {
      // 401 跳转登录
      localStorage.removeItem(TOKEN_KEY);
      if (window.location.pathname !== '/login') {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export default client;
