import { Card, Tag, Space, Typography } from 'antd';
import { ClockCircleOutlined, FireOutlined, TeamOutlined, RobotOutlined } from '@ant-design/icons';

const { Text, Title } = Typography;

function RecipeCard({ recipe, onClick }) {
  const handleClick = () => {
    if (onClick) onClick(recipe);
  };

  const isAiSource = recipe.source === 'ai';
  const matchedCount = recipe.match_count ?? recipe.matchCount ?? 0;

  return (
    <Card
      hoverable
      onClick={handleClick}
      className="recipe-card-wrapper"
      data-testid="recipe-card"
      style={{ cursor: onClick ? 'pointer' : 'default', height: '100%' }}
      cover={
        recipe.image_url ? (
          <img
            alt={recipe.name}
            src={recipe.image_url}
            style={{ height: 160, objectFit: 'cover', borderRadius: '14px 14px 0 0' }}
          />
        ) : (
          <div
            style={{
              height: 160,
              display: 'grid',
              placeItems: 'center',
              fontSize: 56,
              background: 'linear-gradient(135deg, #FDF5E8 0%, #F2CC8F 100%)',
              borderRadius: '14px 14px 0 0'
            }}
          >
            🍳
          </div>
        )
      }
    >
      <Title level={5} style={{ marginBottom: 8 }}>
        {recipe.name}
      </Title>
      <Space size="large" style={{ color: '#6B7280', fontSize: 13, marginBottom: 12 }}>
        <span>
          <ClockCircleOutlined /> {recipe.cook_time || recipe.time || 15} 分钟
        </span>
        <span>
          <FireOutlined /> {recipe.calories || recipe.cal || 0} kcal
        </span>
        <span>
          <TeamOutlined /> {recipe.servings || 2} 人份
        </span>
      </Space>
      <Space size={[4, 4]} wrap style={{ marginBottom: 8 }}>
        {isAiSource && (
          <Tag icon={<RobotOutlined />} color="purple" style={{ borderRadius: 999 }}>
            AI 生成
          </Tag>
        )}
        {matchedCount > 0 && (
          <Tag color="#7C9A6B" style={{ borderRadius: 999 }}>
            匹配 {matchedCount} 种食材
          </Tag>
        )}
        {Array.isArray(recipe.tags) &&
          recipe.tags.map((tag) => (
            <Tag key={tag} color="#7C9A6B" style={{ borderRadius: 999 }}>
              {tag}
            </Tag>
          ))}
      </Space>
      {Array.isArray(recipe.need) && recipe.need.length > 0 && (
        <div style={{ marginTop: 8 }}>
          <Text type="secondary" style={{ fontSize: 12 }}>
            所需食材：
          </Text>
          <Space size={[4, 4]} wrap style={{ marginTop: 4 }}>
            {recipe.need.map((n) => (
              <Tag key={n} style={{ borderRadius: 999, background: '#fff', color: '#5A7550' }}>
                {n}
              </Tag>
            ))}
          </Space>
        </div>
      )}
    </Card>
  );
}

export default RecipeCard;
