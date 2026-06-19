import { useState } from 'react';
import { Upload, Card, Typography, Spin, Alert, Space, Tag } from 'antd';
import { InboxOutlined, CameraOutlined } from '@ant-design/icons';
import { recognizeImage } from '../api/recognition';

const { Dragger } = Upload;
const { Title, Text } = Typography;

function UploadPanel({ onRecognized }) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [results, setResults] = useState(null);

  const handleUpload = async (file) => {
    setLoading(true);
    setError(null);
    setResults(null);
    try {
      const data = await recognizeImage(file);
      const detected = Array.isArray(data) ? data : data?.items || [];
      setResults(detected);
      if (onRecognized) {
        onRecognized(detected);
      }
    } catch (e) {
      setError(e.message || '识别失败，请重试');
    } finally {
      setLoading(false);
    }
    return false; // 阻止 antd 自动上传
  };

  return (
    <Card>
      <Title level={5}>
        <Space>
          <CameraOutlined />
          拍照识食材
        </Space>
      </Title>
      <Dragger
        accept="image/*"
        multiple={false}
        showUploadList={false}
        beforeUpload={handleUpload}
        disabled={loading}
      >
        {loading ? (
          <Spin tip="AI 正在识别冰箱食材…" size="large">
            <div style={{ padding: 32 }} />
          </Spin>
        ) : (
          <>
            <p className="ant-upload-drag-icon">
              <InboxOutlined style={{ color: '#7C9A6B', fontSize: 48 }} />
            </p>
            <p className="ant-upload-text" style={{ fontWeight: 700, color: '#5A7550' }}>
              点击上传冰箱照片，或拖拽图片到这里
            </p>
            <p className="ant-upload-hint" style={{ color: '#6B7280' }}>
              支持 JPG / PNG，AI 会自动识别食材与数量
            </p>
          </>
        )}
      </Dragger>

      {error && (
        <Alert
          type="error"
          message={error}
          showIcon
          style={{ marginTop: 16 }}
        />
      )}

      {results && results.length > 0 && (
        <div style={{ marginTop: 16 }}>
          <Text strong>识别结果（{results.length} 种食材）：</Text>
          <Space size={[8, 8]} wrap style={{ marginTop: 8 }}>
            {results.map((item, idx) => (
              <Tag key={idx} color="green" style={{ borderRadius: 999 }}>
                {item.name} ×{item.quantity || item.qty || 1}
              </Tag>
            ))}
          </Space>
        </div>
      )}

      {results && results.length === 0 && !error && (
        <Alert
          type="info"
          message="未识别到食材，请尝试更清晰的照片"
          showIcon
          style={{ marginTop: 16 }}
        />
      )}
    </Card>
  );
}

export default UploadPanel;
