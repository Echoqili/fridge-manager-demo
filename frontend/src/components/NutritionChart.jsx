import ECharts from './ECharts';
import { THEME_COLORS } from '../config';

function NutritionChart({ data }) {
  const source = data || {};
  const items = Array.isArray(source) ? source : Object.entries(source).map(([name, value]) => ({ name, value }));

  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'horizontal',
      bottom: 0,
      textStyle: {
        fontFamily: 'Noto Sans SC',
        color: THEME_COLORS.charcoal
      }
    },
    color: [
      THEME_COLORS.sage,
      THEME_COLORS.terracotta,
      THEME_COLORS.mustard,
      '#F4A261',
      THEME_COLORS.stone
    ],
    series: [
      {
        name: '营养分类',
        type: 'pie',
        radius: ['45%', '70%'],
        center: ['50%', '45%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: true,
          formatter: '{b}\n{d}%',
          fontFamily: 'Noto Sans SC',
          color: THEME_COLORS.charcoal
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 16,
            fontWeight: 'bold'
          }
        },
        data: items
      }
    ]
  };

  return (
    <div data-testid="nutrition-chart">
      <ECharts option={option} style={{ height: 320 }} />
    </div>
  );
}

export default NutritionChart;
