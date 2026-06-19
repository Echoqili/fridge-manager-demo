import { theme } from 'antd';
import { THEME_COLORS } from '../config';

// Ant Design 5 主题 token 自定义
export const customTheme = {
  token: {
    colorPrimary: THEME_COLORS.sage,
    colorSuccess: THEME_COLORS.sage,
    colorWarning: THEME_COLORS.mustard,
    colorError: THEME_COLORS.terracotta,
    colorInfo: THEME_COLORS.sage,
    colorTextBase: THEME_COLORS.charcoal,
    colorBgBase: THEME_COLORS.cream,
    borderRadius: 14,
    borderRadiusLG: 24,
    borderRadiusSM: 10,
    fontFamily: '\'Noto Sans SC\', system-ui, -apple-system, sans-serif',
    fontSize: 14,
    boxShadow: '0 8px 32px rgba(61, 64, 91, 0.08)',
    boxShadowSecondary: '0 4px 16px rgba(61, 64, 91, 0.06)'
  },
  components: {
    Layout: {
      headerBg: THEME_COLORS.snow,
      headerHeight: 72,
      headerPadding: '0 32px',
      bodyBg: THEME_COLORS.cream,
      siderBg: THEME_COLORS.snow
    },
    Card: {
      borderRadiusLG: 24,
      boxShadowTertiary: '0 8px 32px rgba(61, 64, 91, 0.08)'
    },
    Button: {
      borderRadius: 999,
      controlHeight: 40,
      fontWeight: 600
    },
    Menu: {
      itemBg: 'transparent',
      itemSelectedBg: THEME_COLORS.sageLight,
      itemSelectedColor: THEME_COLORS.sageDark,
      itemHoverBg: THEME_COLORS.sageLight
    },
    Tag: {
      borderRadiusSM: 999
    }
  },
  algorithm: theme.defaultAlgorithm
};
