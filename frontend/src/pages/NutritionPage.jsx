import { useState, useEffect, useMemo } from 'react';
import { Row, Col, Card, Typography, Spin, Empty, Space, Statistic } from 'antd';
import { PieChartOutlined, BulbOutlined } from '@ant-design/icons';
import NutritionChart from '../components/NutritionChart';
import { getNutritionSummary } from '../api/nutrition';
import { useApp } from '../contexts/AppContext';
import { getCategoryStats } from '../utils/helpers';
import { CATEGORIES } from '../config';

const { Title, Text } = Typography;

function NutritionPage() {
  const { ingredients } = useApp();
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(false);

  // 本地计算分类统计（兜底）
  const localStats = useMemo(() => getCategoryStats(ingredients), [ingredients]);

  const chartData = useMemo(() => {
    const source = summary || localStats;
    return Object.entries(source)
      .filter(([, value]) => value > 0)
      .map(([key, value]) => ({
        name: CATEGORIES[key] || key,
        value
      }));
  }, [summary, localStats]);

  // AI 建议
  const insight = useMemo(() => {
    if (ingredients.length === 0) {
      return '添加食材后，我会根据你的库存给出营养搭配建议。';
    }
    if (localStats.meat === 0 && localStats.dairy === 0) {
      return '本周蛋白质摄入偏少，建议补充鸡蛋、牛奶或肉类。';
    }
    if (localStats.vegetable === 0) {
      return '蔬菜库存不足，记得采购新鲜蔬菜平衡膳食。';
    }
    if (localStats.fruit === 0) {
      return '冰箱里没有水果，饭后吃点水果补充维生素吧。';
    }
    return '营养搭配不错！建议优先食用临期食材，减少浪费。';
  }, [ingredients, localStats]);

  useEffect(() => {
    const loadSummary = async () => {
      setLoading(true);
      try {
        const data = await getNutritionSummary();
        setSummary(data);
      } catch (e) {
        // 使用本地计算
      } finally {
        setLoading(false);
      }
    };
    loadSummary();
  }, []);

  return (
    <div className="page-container" data-testid="nutrition-page">
      <Title level={3}>
        <PieChartOutlined /> 营养洞察
      </Title>
      <Text type="secondary">了解你的冰箱营养构成，AI 给出均衡饮食建议</Text>

      <Row gutter={[24, 24]} style={{ marginTop: 24 }}>
        <Col xs={24} lg={14}>
          <Card title="营养分类占比">
            <Spin spinning={loading}>
              {chartData.length > 0 ? (
                <NutritionChart data={chartData} />
              ) : (
                <Empty description="暂无营养数据" style={{ padding: 48 }} />
              )}
            </Spin>
          </Card>
        </Col>

        <Col xs={24} lg={10}>
          <Space direction="vertical" size={24} style={{ width: '100%' }}>
            <Card title="分类统计">
              <Row gutter={[16, 16]}>
                <Col span={12}>
                  <Statistic title="🥬 蔬菜类" value={localStats.vegetable} valueStyle={{ color: '#7C9A6B' }} />
                </Col>
                <Col span={12}>
                  <Statistic title="🥩 肉类" value={localStats.meat} valueStyle={{ color: '#E07A5F' }} />
                </Col>
                <Col span={12}>
                  <Statistic title="🥚 蛋奶类" value={localStats.dairy} valueStyle={{ color: '#E8C547' }} />
                </Col>
                <Col span={12}>
                  <Statistic title="🍚 主食" value={localStats.staple} valueStyle={{ color: '#F2CC8F' }} />
                </Col>
                <Col span={12}>
                  <Statistic title="🍎 水果" value={localStats.fruit} valueStyle={{ color: '#F4A261' }} />
                </Col>
              </Row>
            </Card>

            <Card title={<><BulbOutlined /> AI 建议</>}>
              <div className="insight-tip">
                <Text strong style={{ color: '#E07A5F', display: 'block', marginBottom: 4 }}>
                  💡 AI 建议
                </Text>
                <Text>{insight}</Text>
              </div>
            </Card>
          </Space>
        </Col>
      </Row>
    </div>
  );
}

export default NutritionPage;
