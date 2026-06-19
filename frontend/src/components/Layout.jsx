import { Layout as AntLayout, Menu, Avatar, Dropdown, Space, Typography } from 'antd';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import {
  HomeOutlined,
  FireOutlined,
  PieChartOutlined,
  LogoutOutlined,
  UserOutlined
} from '@ant-design/icons';
import { useApp } from '../contexts/AppContext';

const { Header, Content } = AntLayout;
const { Text } = Typography;

const menuItems = [
  { key: '/', icon: <HomeOutlined />, label: '冰箱看板' },
  { key: '/recipes', icon: <FireOutlined />, label: '菜谱推荐' },
  { key: '/nutrition', icon: <PieChartOutlined />, label: '营养洞察' }
];

function Layout() {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useApp();

  const handleMenuClick = ({ key }) => {
    navigate(key);
  };

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const userMenu = {
    items: [
      {
        key: 'logout',
        icon: <LogoutOutlined />,
        label: '退出登录',
        onClick: handleLogout
      }
    ]
  };

  return (
    <AntLayout style={{ minHeight: '100vh' }}>
      <Header
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          position: 'sticky',
          top: 0,
          zIndex: 10,
          boxShadow: '0 2px 12px rgba(61, 64, 91, 0.06)'
        }}
      >
        <Space size="large" align="center">
          <Space size={12} align="center">
            <div className="brand-logo">🥦</div>
            <div>
              <div className="brand-title" style={{ fontSize: 22, lineHeight: 1 }}>
                鲜知 fridge
              </div>
              <Text type="secondary" style={{ fontSize: 12 }}>
                AI 冰箱管家
              </Text>
            </div>
          </Space>
          <Menu
            mode="horizontal"
            selectedKeys={[location.pathname]}
            items={menuItems}
            onClick={handleMenuClick}
            style={{ minWidth: 360, borderBottom: 'none' }}
          />
        </Space>
        <Dropdown menu={userMenu} placement="bottomRight">
          <Space size={8} style={{ cursor: 'pointer' }}>
            <Avatar style={{ backgroundColor: '#7C9A6B' }} icon={<UserOutlined />} />
            <Text>{user?.username || '用户'}</Text>
          </Space>
        </Dropdown>
      </Header>
      <Content>
        <Outlet />
      </Content>
    </AntLayout>
  );
}

export default Layout;
