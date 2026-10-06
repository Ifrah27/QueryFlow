import type { DatasetInfo, QueryHistoryItem, HealthResponse } from '../types/api';
import axios from 'axios';

const API_BASE = 'https://queryflow-production-a30c.up.railway.app/api';

export const api = {
  checkHealth: async (): Promise<HealthResponse> => {
    const res = await axios.get(`${API_BASE}/health`);
    return res.data;
  },

  getDatasets: async (): Promise<DatasetInfo[]> => {
    const res = await axios.get(`${API_BASE}/datasets`);
    return res.data.datasets || [];
  },

  uploadDataset: async (file: File): Promise<DatasetInfo> => {
    const formData = new FormData();
    formData.append('file', file);
    const res = await axios.post(`${API_BASE}/datasets/upload`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return res.data.dataset;
  },

  deleteDataset: async (id: string): Promise<void> => {
    await axios.delete(`${API_BASE}/datasets/${id}`);
  },

  getQueryHistory: async (): Promise<QueryHistoryItem[]> => {
    const res = await axios.get(`${API_BASE}/query-history`);
    return res.data.history || [];
  },

  sendChatMessage: async (message: string, datasetId?: string | null, history: { role: string; content: string }[] = []) => {
    const res = await axios.post(`${API_BASE}/chat`, {
      message,
      dataset_id: datasetId || null,
      history,
    });
    return res.data;
  }
};
