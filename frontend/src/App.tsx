import React, { useState, useEffect } from 'react';
import { Sidebar } from './components/Sidebar';
import { Header } from './components/Header';
import { OverviewView } from './components/OverviewView';
import { AskDataView } from './components/AskDataView';
import { DatasetsView } from './components/DatasetsView';
import { QueryHistoryView } from './components/QueryHistoryView';
import { api } from './services/apiClient';
import type { DatasetInfo, ChatMessage, QueryHistoryItem } from './types/api';

export const App: React.FC = () => {
  const [currentPage, setCurrentPage] = useState('overview');
  const [datasets, setDatasets] = useState<DatasetInfo[]>([]);
  const [activeDatasetId, setActiveDatasetId] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [queryHistory, setQueryHistory] = useState<QueryHistoryItem[]>([]);
  const [uploading, setUploading] = useState(false);
  const [loading, setLoading] = useState(false);
  const [dbConnected, setDbConnected] = useState(false);
  const [dbName, setDbName] = useState('project_sql_agent');

  // Load initial health & dataset state
  useEffect(() => {
    loadHealth();
    loadDatasets();
    loadQueryHistory();
  }, []);

  const loadHealth = async () => {
    try {
      const data = await api.checkHealth();
      setDbConnected(data.database_connected);
      setDbName(data.database_name);
    } catch {
      setDbConnected(false);
    }
  };

  const loadDatasets = async () => {
    try {
      const list = await api.getDatasets();
      setDatasets(list);
    } catch (e) {
      console.error('Failed to load datasets:', e);
    }
  };

  const loadQueryHistory = async () => {
    try {
      const history = await api.getQueryHistory();
      setQueryHistory(history);
    } catch (e) {
      console.error('Failed to load query history:', e);
    }
  };

  const handleFileUpload = async (file: File) => {
    setUploading(true);
    try {
      const newDs = await api.uploadDataset(file);
      setDatasets((prev) => [...prev, newDs]);
      setActiveDatasetId(newDs.id);
      setCurrentPage('chat');
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to upload CSV file.');
    } finally {
      setUploading(false);
    }
  };

  const handleDeleteDataset = async (id: string) => {
    try {
      await api.deleteDataset(id);
      setDatasets((prev) => prev.filter((d) => d.id !== id));
      if (activeDatasetId === id) {
        setActiveDatasetId(null);
      }
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to delete dataset.');
    }
  };

  const handleSendMessage = async (text: string) => {
    const userMsg: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: text,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMsg]);
    setLoading(true);

    try {
      const history = messages.slice(-6).map((m) => ({ role: m.role, content: m.content }));
      const res = await api.sendChatMessage(text, activeDatasetId, history);
      const assistantMsg: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: res.answer,
        intent: (res as any).intent || (res.route === 'sql' || res.route === 'etl' ? 'dataset' : 'off_topic'),
        route: res.route,
        sql: res.sql,
        columns: res.columns,
        rows: res.rows,
        row_count: res.row_count,
        execution_status: (res as any).execution_status !== undefined ? (res as any).execution_status : (res.route === 'sql' && res.sql ? 'executed' : null),
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, assistantMsg]);
      loadQueryHistory();
    } catch (err: any) {
      const errorMsg: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: `Error processing query: ${err.response?.data?.detail || err.message}`,
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  const activeDataset = datasets.find((d) => d.id === activeDatasetId) || null;

  return (
    <div className="flex min-h-screen bg-[#F6F7FB]">
      <Sidebar
        currentPage={currentPage}
        setCurrentPage={setCurrentPage}
        datasets={datasets}
        activeDatasetId={activeDatasetId}
        setActiveDatasetId={setActiveDatasetId}
        onFileUpload={handleFileUpload}
        uploading={uploading}
        dbConnected={dbConnected}
        dbName={dbName}
      />

      <main className="flex-1 p-6 lg:p-8 max-w-[1400px] mx-auto w-full overflow-x-hidden">
        {currentPage === 'overview' && (
          <>
            <Header title="Overview" subtitle="Workspace statistics and data activity hub." activeDataset={activeDataset} />
            <OverviewView datasets={datasets} queryHistory={queryHistory} onNavigate={setCurrentPage} />
          </>
        )}

        {currentPage === 'chat' && (
          <>
            <Header title="Ask Data" subtitle="Explore datasets with natural language and SQL-backed insights." activeDataset={activeDataset} />
            <AskDataView
              messages={messages}
              onSendMessage={handleSendMessage}
              loading={loading}
              activeDataset={activeDataset}
            />
          </>
        )}

        {currentPage === 'datasets' && (
          <>
            <Header title="Datasets" subtitle="Manage connected PostgreSQL tables and schema definitions." activeDataset={activeDataset} />
            <DatasetsView datasets={datasets} onDelete={handleDeleteDataset} />
          </>
        )}

        {currentPage === 'history' && (
          <>
            <Header title="Query History" subtitle="Audit trail of generated SQL queries and natural language answers." activeDataset={activeDataset} />
            <QueryHistoryView history={queryHistory} />
          </>
        )}
      </main>
    </div>
  );
};

export default App;
