import { useState, useMemo, useEffect, useCallback } from 'react';
import {
  Row,
  Col,
  Card,
  Statistic,
  Tabs,
  Form,
  Input,
  InputNumber,
  Select,
  Button,
  Space,
  Typography,
  Empty,
  App
} from 'antd';
import {
  ShoppingOutlined,
  FireOutlined,
  WarningOutlined,
  DollarOutlined
} from '@ant-design/icons';
import { useApp } from '../contexts/AppContext';
import IngredientCard from '../components/IngredientCard';
import UploadPanel from '../components/UploadPanel';
import ShoppingList from '../components/ShoppingList';
import RecipeCard from '../components/RecipeCard';
import { recommendRecipes } from '../api/recipes';
import * as shoppingApi from '../api/shoppingList';
import {
  isExpiringSoon,
  calculateSavings,
  inferCategory,
  getEmoji
} from '../utils/helpers';
import { STORAGE_LOCATIONS } from '../config';

const { Title, Text } = Typography;

// 本地兜底菜谱库（API 不可用时使用）
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

function HomePage() {
  const { user, isDemo, ingredients, addIngredient, removeIngredient } = useApp();
  const { message } = App.useApp();
  const [form] = Form.useForm();
  const [recipes, setRecipes] = useState([]);
  const [recipesLoading, setRecipesLoading] = useState(false);
  const [shoppingItems, setShoppingItems] = useState([]);
  const [shoppingLoading, setShoppingLoading] = useState(false);

  // 统计数据
  const stats = useMemo(() => {
    const total = ingredients.length;
    const expiring = ingredients.filter((i) => isExpiringSoon(i)).length;
    const savings = calculateSavings(ingredients);
    return { total, expiring, savings, recipes: recipes.length };
  }, [ingredients, recipes]);

  // 按存放位置分组
  const groupedIngredients = useMemo(() => {
    const groups = { fridge: [], freezer: [], crisper: [], pantry: [] };
    ingredients.forEach((item) => {
      const loc = item.storage_location || item.shelf || 'fridge';
      const key = STORAGE_LOCATIONS[loc] ? loc : 'fridge';
      if (!groups[key]) groups[key] = [];
      groups[key].push(item);
    });
    return groups;
  }, [ingredients]);

  // 匹配本地菜谱
  const matchingLocalRecipes = useMemo(() => {
    const names = ingredients.map((i) => i.name);
    return LOCAL_RECIPES.filter((r) =>
      r.need.some((n) => names.some((name) => name && name.includes(n)))
    );
  }, [ingredients]);

  // 生成菜谱推荐
  const handleGenerateRecipes = async () => {
    if (ingredients.length === 0) {
      message.warning('冰箱是空的，先添加食材吧');
      return;
    }
    setRecipesLoading(true);
    try {
      const data = await recommendRecipes({
        ingredients: ingredients.map((i) => i.name)
      });
      const list = Array.isArray(data) ? data : data?.items || [];
      const finalRecipes = list.length > 0 ? list : matchingLocalRecipes;
      setRecipes(finalRecipes);
      // 同步缺失食材到购物清单
      syncMissingToShoppingList(finalRecipes);
      message.success('已为你生成最优菜谱，优先消耗临期食材');
    } catch (e) {
      // API 不可用，使用本地菜谱
      setRecipes(matchingLocalRecipes);
      syncMissingToShoppingList(matchingLocalRecipes);
      message.success('已为你生成推荐菜谱');
    } finally {
      setRecipesLoading(false);
    }
  };

  // 手动添加食材
  const handleAdd = async (values) => {
    try {
      const payload = {
        name: values.name,
        quantity: values.quantity || 1,
        unit: '个',
        category: inferCategory(values.name),
        storage_location: values.storage_location || 'fridge',
        purchase_date: new Date().toISOString().slice(0, 10),
        expiry_date: new Date(Date.now() + 7 * 86400000).toISOString().slice(0, 10)
      };
      await addIngredient(payload);
      message.success(`已添加 ${getEmoji(values.name)} ${values.name}`);
      form.resetFields();
    } catch (e) {
      message.error(e.message || '添加失败');
    }
  };

  // 删除食材
  const handleDelete = async (id) => {
    try {
      await removeIngredient(id);
      message.success('已移除食材');
    } catch (e) {
      message.error(e.message || '删除失败');
    }
  };

  // 识别结果回调
  const handleRecognized = (detected) => {
    if (detected && detected.length > 0) {
      message.success(`识别成功！新增 ${detected.length} 种食材`);
    }
  };

  // 加载购物清单（登录用户从后端获取，演示模式使用本地计算）
  const refreshShoppingList = useCallback(async () => {
    if (isDemo || !user) {
      // 演示模式：根据菜谱缺失食材计算
      if (recipes.length === 0) {
        setShoppingItems([]);
        return;
      }
      const names = ingredients.map((i) => i.name);
      const missing = new Set();
      recipes.forEach((r) => {
        (r.need || r.ingredients || []).forEach((n) => {
          const name = typeof n === 'string' ? n : n?.ingredient_name || n?.name;
          if (name && !names.some((nm) => nm && nm.includes(name))) {
            missing.add(name);
          }
        });
      });
      setShoppingItems(Array.from(missing).map((name) => ({ name, checked: false })));
      return;
    }
    setShoppingLoading(true);
    try {
      const data = await shoppingApi.getShoppingList();
      setShoppingItems(Array.isArray(data) ? data : []);
    } catch (e) {
      setShoppingItems([]);
    } finally {
      setShoppingLoading(false);
    }
  }, [isDemo, user, recipes, ingredients]);

  useEffect(() => {
    refreshShoppingList();
  }, [refreshShoppingList]);

  // 购物清单勾选/取消勾选
  const handleToggleShoppingItem = async (index, item) => {
    if (isDemo || !item.item_id) {
      setShoppingItems((prev) =>
        prev.map((it, i) => (i === index ? { ...it, checked: !it.checked } : it))
      );
      return;
    }
    try {
      await shoppingApi.updateShoppingItem(item.item_id, { checked: !item.checked });
      setShoppingItems((prev) =>
        prev.map((it, i) => (i === index ? { ...it, checked: !it.checked } : it))
      );
    } catch (e) {
      message.error('更新失败');
    }
  };

  // 删除购物清单条目
  const handleDeleteShoppingItem = async (item) => {
    if (isDemo || !item.item_id) {
      setShoppingItems((prev) => prev.filter((it) => it.name !== item.name));
      return;
    }
    try {
      await shoppingApi.deleteShoppingItem(item.item_id);
      setShoppingItems((prev) => prev.filter((it) => it.item_id !== item.item_id));
      message.success('已删除');
    } catch (e) {
      message.error('删除失败');
    }
  };

  // 生成菜谱后自动将缺失食材同步到购物清单
  const syncMissingToShoppingList = async (recipesList) => {
    const names = ingredients.map((i) => i.name);
    const missing = new Set();
    recipesList.forEach((r) => {
      (r.need || r.ingredients || []).forEach((n) => {
        const name = typeof n === 'string' ? n : n?.ingredient_name || n?.name;
        if (name && !names.some((nm) => nm && nm.includes(name))) {
          missing.add(name);
        }
      });
    });
    const missingItems = Array.from(missing).map((name) => ({ name, quantity: '1个' }));

    if (isDemo || !user) {
      setShoppingItems(missingItems.map((it) => ({ ...it, checked: false })));
      return;
    }
    if (missingItems.length === 0) return;
    try {
      await shoppingApi.clearShoppingList();
      const created = await shoppingApi.batchAddShoppingItems(missingItems);
      setShoppingItems(created);
    } catch (e) {
      // 静默失败，不影响菜谱推荐
    }
  };

  const shelfTabs = Object.entries(STORAGE_LOCATIONS).map(([key, label]) => ({
    key,
    label: label,
    children: (
      <div className="shelf">
        <div className="shelf-label">{label}</div>
        {groupedIngredients[key] && groupedIngredients[key].length > 0 ? (
          <Space size={[8, 8]} wrap>
            {groupedIngredients[key].map((item) => (
              <IngredientCard
                key={item.ingredient_id || item.id}
                ingredient={item}
                onDelete={handleDelete}
              />
            ))}
          </Space>
        ) : (
          <Text type="secondary" style={{ fontSize: 13 }}>
            暂无食材
          </Text>
        )}
      </div>
    )
  }));

  return (
    <div className="page-container" data-testid="home-page">
      {/* Hero 数据看板 */}
      <div className="hero-card">
        <Title level={3} style={{ color: '#fff', marginBottom: 8, position: 'relative' }}>
          打开冰箱，就知道今天吃什么
        </Title>
        <Text style={{ color: '#fff', opacity: 0.92, position: 'relative' }}>
          拍一张照片，AI 自动识别食材、提醒临期、推荐菜谱，还能一键生成购物清单。让每一餐都不浪费。
        </Text>
        <Row gutter={32} style={{ marginTop: 24, position: 'relative' }}>
          <Col>
            <Statistic
              title={<span style={{ color: '#fff', opacity: 0.85 }}>冰箱食材</span>}
              value={stats.total}
              valueStyle={{ color: '#fff', fontWeight: 900 }}
            />
          </Col>
          <Col>
            <Statistic
              title={<span style={{ color: '#fff', opacity: 0.85 }}>即将过期</span>}
              value={stats.expiring}
              prefix={<WarningOutlined />}
              valueStyle={{ color: '#F2CC8F', fontWeight: 900 }}
            />
          </Col>
          <Col>
            <Statistic
              title={<span style={{ color: '#fff', opacity: 0.85 }}>可做菜谱</span>}
              value={stats.recipes}
              prefix={<FireOutlined />}
              valueStyle={{ color: '#fff', fontWeight: 900 }}
            />
          </Col>
          <Col>
            <Statistic
              title={<span style={{ color: '#fff', opacity: 0.85 }}>预计节省(元)</span>}
              value={stats.savings}
              prefix={<DollarOutlined />}
              valueStyle={{ color: '#fff', fontWeight: 900 }}
            />
          </Col>
        </Row>
      </div>

      <Row gutter={[24, 24]}>
        <Col xs={24} lg={16}>
          {/* 拍照识食材 */}
          <div style={{ marginBottom: 24 }}>
            <UploadPanel onRecognized={handleRecognized} />
          </div>

          {/* 手动添加 + 冰箱可视化 */}
          <Card>
            <Title level={5}>➕ 手动添加食材</Title>
            <Form
              form={form}
              layout="inline"
              onFinish={handleAdd}
              style={{ marginBottom: 16, flexWrap: 'wrap', gap: 8 }}
            >
              <Form.Item name="name" rules={[{ required: true, message: '请输入食材名称' }]}>
                <Input placeholder="食材名称，如：西红柿" style={{ width: 180 }} />
              </Form.Item>
              <Form.Item name="quantity" initialValue={1}>
                <InputNumber min={1} placeholder="数量" style={{ width: 100 }} />
              </Form.Item>
              <Form.Item name="storage_location" initialValue="fridge">
                <Select style={{ width: 130 }} options={Object.entries(STORAGE_LOCATIONS).map(([k, v]) => ({ value: k, label: v }))} />
              </Form.Item>
              <Form.Item>
                <Button type="primary" htmlType="submit">
                  添加
                </Button>
              </Form.Item>
            </Form>

            <Title level={5}>🧊 我的冰箱</Title>
            {ingredients.length === 0 ? (
              <Empty
                image="🍃"
                description="冰箱还是空的，拍张照片或手动添加食材吧"
                style={{ padding: 24 }}
              />
            ) : (
              <Tabs items={shelfTabs} defaultActiveKey="fridge" />
            )}
          </Card>
        </Col>

        {/* 侧边栏：购物清单 + AI 推荐菜谱 */}
        <Col xs={24} lg={8}>
          <Space direction="vertical" size={24} style={{ width: '100%' }}>
            <Card title={<><ShoppingOutlined /> 购物清单</>}>
              <ShoppingList
                items={shoppingItems}
                onToggle={handleToggleShoppingItem}
                onDelete={handleDeleteShoppingItem}
              />
            </Card>

            <Card
              title={<><FireOutlined /> AI 推荐菜谱</>}
              extra={
                <Button type="primary" size="small" onClick={handleGenerateRecipes} loading={recipesLoading}>
                  生成菜谱
                </Button>
              }
            >
              {recipes.length === 0 ? (
                <Empty
                  image="🍳"
                  description="点击「生成菜谱」获取推荐"
                  style={{ padding: 16 }}
                />
              ) : (
                <Space direction="vertical" size={12} style={{ width: '100%' }}>
                  {recipes.slice(0, 3).map((r) => (
                    <RecipeCard key={r.recipe_id || r.id || r.name} recipe={r} />
                  ))}
                </Space>
              )}
            </Card>
          </Space>
        </Col>
      </Row>
    </div>
  );
}

export default HomePage;
