export interface DatasetInfo {
  id: string;
  filename: string;
  table_name: string;
  row_count: number;
  col_count: number;
  columns: string[];
  column_mapping: Record<string, string>;
  schema: Record<string, string>;
  preview_records?: Record<string, any>[];
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  intent?: 'dataset' | 'off_topic' | 'unclear';
  route?: string;
  sql?: string;
  columns?: string[];
  rows?: any[][];
  row_count?: number;
  execution_status?: string | null;
  timestamp: string;
}

export interface QueryHistoryItem {
  question: string;
  dataset: string;
  answer: string;
  sql?: string;
  route?: string;
  row_count?: number;
}

export interface HealthResponse {
  status: string;
  database_connected: boolean;
  database_name: string;
}
