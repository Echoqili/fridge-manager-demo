import { Tag, Space, Typography, Popconfirm } from 'antd';
import { DeleteOutlined, WarningOutlined } from '@ant-design/icons';
import { getEmoji, isExpiringSoon, getCategoryColor, inferCategory } from '../utils/helpers';
import { CATEGORIES, STORAGE_LOCATIONS } from '../config';

const { Text } = Typography;

function IngredientCard({ ingredient, onDelete }) {
  const name = ingredient.name;
  const quantity = ingredient.quantity ?? ingredient.qty ?? 1;
  const unit = ingredient.unit || '';
  const storageLocation = ingredient.storage_location || ingredient.shelf || 'fridge';
  const locationLabel = STORAGE_LOCATIONS[storageLocation] || storageLocation;
  const category = ingredient.category || inferCategory(name);
  const categoryLabel = CATEGORIES[category] || '其他';
  const expiring = isExpiringSoon(ingredient);
  const daysLeft = ingredient.daysLeft !== undefined
    ? ingredient.daysLeft
    : null;

  const handleDelete = () => {
    if (onDelete) {
      onDelete(ingredient.ingredient_id || ingredient.id);
    }
  };

  return (
    <div
      className={`ingredient-card pop-in ${expiring ? 'expiring-soon' : ''}`}
      data-testid="ingredient-card"
    >
      <span style={{ fontSize: 18 }}>{getEmoji(name)}</span>
      <Text strong>{name}</Text>
      <Text type="secondary" style={{ fontWeight: 500 }}>
        ×{quantity}{unit}
      </Text>
      <Tag color={getCategoryColor(category)} style={{ marginInlineEnd: 0 }}>
        {categoryLabel}
      </Tag>
      <Text type="secondary" style={{ fontSize: 12 }}>
        {locationLabel}
      </Text>
      {expiring && (
        <Space size={2}>
          <WarningOutlined style={{ color: '#E07A5F' }} />
          {daysLeft !== null && (
            <Text type="danger" style={{ fontSize: 12 }}>
              {daysLeft}天
            </Text>
          )}
        </Space>
      )}
      {onDelete && (
        <Popconfirm title="确定移除该食材？" onConfirm={handleDelete} okText="移除" cancelText="取消">
          <DeleteOutlined style={{ color: '#9ca3af', cursor: 'pointer' }} data-testid="delete-ingredient" />
        </Popconfirm>
      )}
    </div>
  );
}

export default IngredientCard;
