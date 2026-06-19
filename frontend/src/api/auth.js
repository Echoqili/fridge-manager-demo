import client from './client';

// 用户登录
export function login(data) {
  return client.post('/auth/login', data);
}

// 用户注册
export function register(data) {
  return client.post('/auth/register', data);
}

// 刷新 Token
export function refresh(refreshToken) {
  return client.post('/auth/refresh', { refresh_token: refreshToken });
}

// 登出
export function logout() {
  return client.post('/auth/logout');
}

// 获取当前用户信息
export function getMe() {
  return client.get('/auth/me');
}
