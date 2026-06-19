import { Checkbox, List, Typography, Empty, Space, Button, Popconfirm } from 'antd';
import { DeleteOutlined } from '@ant-design/icons';
import { getEmoji } from '../utils/helpers';

const { Text } = Typography;

function ShoppingList({ items, onToggle, onDelete }) {
  if (!items || items.length === 0) {
    return (
      <Empty
        image="📝"
        description="暂无购物需求"
        style={{ padding: 24 }}
      />
    );
  }

  const handleToggle = (item, index) => {
    if (onToggle) {
      onToggle(index, item);
    }
  };

  const handleDelete = (item) => {
    if (onDelete) {
      onDelete(item);
    }
  };

  return (
    <List
      data-testid="shopping-list"
      dataSource={items}
      renderItem={(item, index) => {
        const name = typeof item === 'string' ? item : item.name;
        const checked = typeof item === 'object' ? item.checked : false;
        return (
          <List.Item
            style={{ borderBottom: '1px solid #f0f0f0', padding: '12px 0' }}
            actions={
              onDelete && typeof item === 'object'
                ? [
                    <Popconfirm
                      key="delete"
                      title="确定删除？"
                      onConfirm={() => handleDelete(item)}
                      okText="删除"
                      cancelText="取消"
                    >
                      <Button type="text" size="small" danger icon={<DeleteOutlined />} />
                    </Popconfirm>
                  ]
                : undefined
            }
          >
            <Space>
              <Checkbox
                checked={checked}
                onChange={() => handleToggle(item, index)}
                style={{ accentColor: '#7C9A6B' }}
              />
              <span style={{ fontSize: 18 }}>{getEmoji(name)}</span>
              <Text
                delete={checked}
                style={checked ? { color: '#9ca3af' } : {}}
              >
                {name}
              </Text>
            </Space>
          </List.Item>
        );
      }}
    />
  );
}

export default ShoppingList;
