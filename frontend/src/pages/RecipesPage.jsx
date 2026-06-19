import { useState, useEffect } from 'react';
import { Row, Col, Card, Typography, Space, Empty, Spin, Button, Steps, Tag } from 'antd';
import { FireOutlined, ArrowLeftOutlined } from '@ant-design/icons';
import RecipeCard from '../components/RecipeCard';
import { recommendRecipes, getRecipeById } from '../api/recipes';
import { useApp } from '../contexts/AppContext';

const { Title, Text } = Typography;

// 本地兜底菜谱库
const LOCAL_RECIPES = [
  {
    recipe_id: 'r1',
    name: '西红柿炒鸡蛋',
    tags: ['家常', '快手', '高蛋白'],
    cook_time: 10,
    calories: 280,
    servings: 2,
    need: ['西红柿', '鸡蛋'],
    steps: ['西红柿切块，鸡蛋打散备用', '热锅倒油，炒熟鸡蛋盛出', '再炒西红柿出汁，倒入鸡蛋翻炒', '加盐调味，撒葱花出锅']
  },
  {
    recipe_id: 'r2',
    name: '土豆炖牛肉',
    tags: ['下饭', '暖胃', '高蛋白'],
    cook_time: 45,
    calories: 520,
    servings: 3,
    need: ['土豆', '牛肉', '洋葱', '胡萝卜'],
    steps: ['牛肉切块焯水去血沫', '洋葱爆香，加入牛肉翻炒上色', '加水炖煮 30 分钟', '加入土豆、胡萝卜继续炖 15 分钟', '加盐、生抽调味即可']
  },
  {
    recipe_id: 'r3',
    name: '蒜蓉西兰花',
    tags: ['低脂', '健康', '素食'],
    cook_time: 8,
    calories: 120,
    servings: 2,
    need: ['西兰花', '大蒜'],
    steps: ['西兰花掰小朵焯水 1 分钟', '大蒜切末', '热锅爆香蒜末', '倒入西兰花快炒，加盐出锅']
  },
  {
    recipe_id: 'r4',
    name: '香蕉牛奶昔',
    tags: ['早餐', '甜品', '补钙'],
    cook_time: 3,
    calories: 210,
    servings: 1,
    need: ['香蕉', '牛奶'],
    steps: ['香蕉切段', '与牛奶一起放入搅拌机', '打 30 秒至顺滑', '倒入杯中即可享用']
  },
  {
    recipe_id: 'r5',
    name: '鸡肉蔬菜炒饭',
    tags: ['一人食', '饱腹', '均衡'],
    cook_time: 15,
    calories: 450,
    servings: 1,
    need: ['鸡肉', '米饭', '胡萝卜', '鸡蛋'],
    steps: ['鸡肉切丁，胡萝卜切丁，鸡蛋打散', '先炒鸡蛋，再加入鸡肉炒熟', '倒入米饭和胡萝卜丁翻炒均匀', '加盐、生抽调味即可']
  }
];

function RecipesPage() {
  const { ingredients } = useApp();
  const [recipes, setRecipes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selected, setSelected] = useState(null);
  const [detailLoading, setDetailLoading] = useState(false);

  const loadRecipes = async () => {
    setLoading(true);
    try {
      const data = await recommendRecipes({
        ingredients: ingredients.map((i) => i.name)
      });
      const list = Array.isArray(data) ? data : data?.items || [];
      setRecipes(list.length > 0 ? list : LOCAL_RECIPES);
    } catch (e) {
      setRecipes(LOCAL_RECIPES);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadRecipes();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleSelect = async (recipe) => {
    setSelected(recipe);
    setDetailLoading(true);
    const id = recipe.recipe_id || recipe.id;
    if (id) {
      try {
        const detail = await getRecipeById(id);
        if (detail && detail.steps) {
          setSelected(detail);
        }
      } catch (e) {
        // 使用列表中的数据
      }
    }
    setDetailLoading(false);
  };

  return (
    <div className="page-container" data-testid="recipes-page">
      <Title level={3}>
        <FireOutlined /> 菜谱推荐
      </Title>
      <Text type="secondary">根据你的冰箱食材，AI 为你推荐最合适的菜谱</Text>

      {selected ? (
        <Card style={{ marginTop: 24 }}>
          <Button
            type="text"
            icon={<ArrowLeftOutlined />}
            onClick={() => setSelected(null)}
            style={{ marginBottom: 16 }}
          >
            返回列表
          </Button>
          <Spin spinning={detailLoading}>
            <Title level={4}>{selected.name}</Title>
            <Space size="large" style={{ color: '#6B7280', marginBottom: 16 }}>
              <span>⏱ {selected.cook_time || selected.time || 15} 分钟</span>
              <span>🔥 {selected.calories || selected.cal || 0} kcal</span>
              <span>🍽 {selected.servings || 2} 人份</span>
            </Space>
            {Array.isArray(selected.tags) && selected.tags.length > 0 && (
              <Space size={[4, 4]} wrap style={{ marginBottom: 16 }}>
                {selected.tags.map((t) => (
                  <Tag key={t} color="green">{t}</Tag>
                ))}
              </Space>
            )}
            {Array.isArray(selected.need) && selected.need.length > 0 && (
              <div style={{ marginBottom: 16 }}>
                <Text strong>所需食材：</Text>
                <Space size={[4, 4]} wrap style={{ marginTop: 8 }}>
                  {selected.need.map((n) => (
                    <Tag key={n} style={{ borderRadius: 999 }}>{n}</Tag>
                  ))}
                </Space>
              </div>
            )}
            {Array.isArray(selected.steps) && selected.steps.length > 0 && (
              <div>
                <Text strong>烹饪步骤：</Text>
                <Steps
                  direction="vertical"
                  current={selected.steps.length}
                  items={selected.steps.map((step, idx) => ({
                    title: `步骤 ${idx + 1}`,
                    description: step
                  }))}
                  style={{ marginTop: 16 }}
                />
              </div>
            )}
          </Spin>
        </Card>
      ) : (
        <Row gutter={[16, 16]} style={{ marginTop: 24 }}>
          {loading ? (
            <Col span={24} style={{ textAlign: 'center', padding: 48 }}>
              <Spin tip="加载推荐菜谱…" />
            </Col>
          ) : recipes.length === 0 ? (
            <Col span={24}>
              <Empty description="暂无推荐菜谱，先去添加食材吧" />
            </Col>
          ) : (
            recipes.map((r) => (
              <Col xs={24} sm={12} lg={8} key={r.recipe_id || r.id || r.name}>
                <RecipeCard recipe={r} onClick={handleSelect} />
              </Col>
            ))
          )}
        </Row>
      )}
    </div>
  );
}

export default RecipesPage;
