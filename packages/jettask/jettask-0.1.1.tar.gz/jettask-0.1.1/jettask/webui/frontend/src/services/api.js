import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';
const WS_BASE_URL = 'ws://localhost:8000/ws';

// 创建 axios 实例
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
});

// 获取全局统计信息
export const fetchGlobalStats = async () => {
  try {
    const response = await api.get('/stats');
    return response.data.data;
  } catch (error) {
    console.error('Failed to fetch global stats:', error);
    throw error;
  }
};

// 获取队列列表
export const fetchQueues = async () => {
  try {
    const response = await api.get('/queues');
    return response.data;
  } catch (error) {
    console.error('Failed to fetch queues:', error);
    throw error;
  }
};

// 获取队列时间线数据
export const fetchQueueTimeline = async (params) => {
  try {
    const response = await api.post('/queue-timeline', params);
    return response.data;
  } catch (error) {
    console.error('Failed to fetch queue timeline:', error);
    throw error;
  }
};

// WebSocket 连接
export const connectWebSocket = (onMessage, onError) => {
  const ws = new WebSocket(`${WS_BASE_URL}/monitor`);
  
  ws.onopen = () => {
    console.log('WebSocket connected');
  };
  
  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      onMessage(data);
    } catch (error) {
      console.error('Failed to parse WebSocket message:', error);
    }
  };
  
  ws.onerror = (error) => {
    console.error('WebSocket error:', error);
    if (onError) onError(error);
  };
  
  ws.onclose = () => {
    console.log('WebSocket disconnected');
  };
  
  return ws;
};

export default api;