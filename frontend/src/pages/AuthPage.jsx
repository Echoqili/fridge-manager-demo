import { useState } from 'react';
import { Card, Tabs, Form, Input, Button, Typography, Space, App } from 'antd';
import { UserOutlined, LockOutlined, MailOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { useApp } from '../contexts/AppContext';
import * as authApi from '../api/auth';

const { Title, Text, Paragraph } = Typography;

function AuthPage() {
  const [activeTab, setActiveTab] = useState('login');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { login, demoLogin } = useApp();
  const { message } = App.useApp();

  const handleLogin = async (values) => {
    setLoading(true);
    try {
      await login(values);
      message.success('登录成功');
      navigate('/');
    } catch (e) {
      message.error(e.message || '登录失败');
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (values) => {
    setLoading(true);
    try {
      await authApi.register(values);
      message.success('注册成功，请登录');
      setActiveTab('login');
    } catch (e) {
      message.error(e.message || '注册失败');
    } finally {
      setLoading(false);
    }
  };

  // 演示账号快速登录
  const handleDemoLogin = async () => {
    setLoading(true);
    try {
      demoLogin();
      message.success('已进入演示模式');
      navigate('/');
    } catch (e) {
      message.error('演示模式启动失败');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      style={{
        minHeight: '100vh',
        display: 'grid',
        placeItems: 'center',
        background: 'linear-gradient(135deg, #E8F0E4 0%, #FFFDF7 50%, #FDF5E8 100%)',
        padding: 24
      }}
    >
      <Card style={{ width: 420, maxWidth: '100%', boxShadow: '0 16px 48px rgba(61, 64, 91, 0.12)' }}>
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
          <div style={{ textAlign: 'center' }}>
            <div
              className="brand-logo"
              style={{ width: 64, height: 64, margin: '0 auto 12px', fontSize: 32 }}
            >
              🥦
            </div>
            <Title level={3} className="brand-title" style={{ marginBottom: 0 }}>
              鲜知 fridge
            </Title>
            <Text type="secondary">AI 冰箱管家 · 剩菜变菜谱，过期早知道</Text>
          </div>

          <Tabs
            activeKey={activeTab}
            onChange={setActiveTab}
            centered
            items={[
              {
                key: 'login',
                label: '登录',
                children: (
                  <Form onFinish={handleLogin} layout="vertical" requiredMark={false}>
                    <Form.Item
                      name="username"
                      label="用户名"
                      rules={[{ required: true, message: '请输入用户名' }]}
                    >
                      <Input prefix={<UserOutlined />} placeholder="请输入用户名" />
                    </Form.Item>
                    <Form.Item
                      name="password"
                      label="密码"
                      rules={[{ required: true, message: '请输入密码' }]}
                    >
                      <Input.Password prefix={<LockOutlined />} placeholder="请输入密码" />
                    </Form.Item>
                    <Button type="primary" htmlType="submit" block loading={loading}>
                      登录
                    </Button>
                  </Form>
                )
              },
              {
                key: 'register',
                label: '注册',
                children: (
                  <Form onFinish={handleRegister} layout="vertical" requiredMark={false}>
                    <Form.Item
                      name="username"
                      label="用户名"
                      rules={[{ required: true, message: '请输入用户名' }]}
                    >
                      <Input prefix={<UserOutlined />} placeholder="请输入用户名" />
                    </Form.Item>
                    <Form.Item
                      name="email"
                      label="邮箱"
                      rules={[
                        { required: true, message: '请输入邮箱' },
                        { type: 'email', message: '邮箱格式不正确' }
                      ]}
                    >
                      <Input prefix={<MailOutlined />} placeholder="请输入邮箱" />
                    </Form.Item>
                    <Form.Item
                      name="password"
                      label="密码"
                      rules={[
                        { required: true, message: '请输入密码' },
                        { min: 6, message: '密码至少 6 位' }
                      ]}
                    >
                      <Input.Password prefix={<LockOutlined />} placeholder="请输入密码" />
                    </Form.Item>
                    <Button type="primary" htmlType="submit" block loading={loading}>
                      注册
                    </Button>
                  </Form>
                )
              }
            ]}
          />

          <div style={{ textAlign: 'center' }}>
            <Paragraph type="secondary" style={{ fontSize: 12, marginBottom: 8 }}>
              或者
            </Paragraph>
            <Button type="default" block onClick={handleDemoLogin} loading={loading}>
              🚀 演示模式快速体验
            </Button>
          </div>
        </Space>
      </Card>
    </div>
  );
}

export default AuthPage;
