import client from './client';

// 上传图片识别食材（FormData 上传）
export function recognizeImage(file) {
  const formData = new FormData();
  formData.append('file', file);
  return client.post('/recognition/recognize', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    },
    timeout: 60000
  });
}
