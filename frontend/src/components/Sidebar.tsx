import React from 'react';
import { LayoutDashboard, MessageSquare, Database, History, Upload, Server, CheckCircle, XCircle } from 'lucide-react';
import type { DatasetInfo } from '../types/api';

interface SidebarProps {
  currentPage: string;
  setCurrentPage: (page: string) => void;
  datasets: DatasetInfo[];
  activeDatasetId: string | null;
  setActiveDatasetId: (id: string | null) => void;
  onFileUpload: (file: File) => void;
  uploading: boolean;
  dbConnected: boolean;
  dbName: string;
}

export const Sidebar: React.FC<SidebarProps> = ({
  currentPage,
  setCurrentPage,
  datasets,
  activeDatasetId,
  setActiveDatasetId,
  onFileUpload,
  uploading,
  dbConnected,
  dbName,
}) => {
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      onFileUpload(e.target.files[0]);
    }
  };

  return (
    <aside className="w-64 bg-[#0B1220] text-slate-300 flex flex-col h-screen border-r border-slate-800 shrink-0 sticky top-0">
      {/* Brand Header */}
      <div className="p-4 flex items-center gap-3 border-b border-slate-800/60">
        <img src="/queryflow-logo.png" alt="QueryFlow Logo" className="w-10 h-10 object-contain shrink-0" />
        <div className="min-w-0">
          <h1 className="font-extrabold text-white text-base leading-tight tracking-tight">QueryFlow</h1>
          <p className="text-[11px] text-indigo-300 font-medium tracking-tight truncate">Ask. Analyze. Transform.</p>
        </div>
      </div>

      {/* Main Menu Navigation */}
      <div className="p-4 flex-1 overflow-y-auto space-y-6">
        <div>
          <div className="text-[11px] font-bold text-slate-500 tracking-wider uppercase mb-2 px-2">Workspace</div>
          <nav className="space-y-1">
            <button
              onClick={() => setCurrentPage('overview')}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                currentPage === 'overview'
                  ? 'bg-indigo-600/20 text-white border-l-4 border-indigo-500 rounded-l-none'
                  : 'text-slate-400 hover:bg-slate-800/60 hover:text-slate-200'
              }`}
            >
              <LayoutDashboard className="w-4 h-4" />
              Overview
            </button>
            <button
              onClick={() => setCurrentPage('chat')}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                currentPage === 'chat'
                  ? 'bg-indigo-600/20 text-white border-l-4 border-indigo-500 rounded-l-none'
                  : 'text-slate-400 hover:bg-slate-800/60 hover:text-slate-200'
              }`}
            >
              <MessageSquare className="w-4 h-4" />
              Ask Data
            </button>
            <button
              onClick={() => setCurrentPage('datasets')}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                currentPage === 'datasets'
                  ? 'bg-indigo-600/20 text-white border-l-4 border-indigo-500 rounded-l-none'
                  : 'text-slate-400 hover:bg-slate-800/60 hover:text-slate-200'
              }`}
            >
              <Database className="w-4 h-4" />
              Datasets
            </button>
            <button
              onClick={() => setCurrentPage('history')}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                currentPage === 'history'
                  ? 'bg-indigo-600/20 text-white border-l-4 border-indigo-500 rounded-l-none'
                  : 'text-slate-400 hover:bg-slate-800/60 hover:text-slate-200'
              }`}
            >
              <History className="w-4 h-4" />
              Query History
            </button>
          </nav>
        </div>

        {/* Upload Zone */}
        <div>
          <div className="text-[11px] font-bold text-slate-500 tracking-wider uppercase mb-2 px-2">Data Upload</div>
          <label className="border border-dashed border-slate-700 hover:border-indigo-500 bg-[#151D2A] rounded-xl p-3.5 text-center cursor-pointer block transition-all group">
            <Upload className="w-5 h-5 mx-auto text-slate-400 group-hover:text-indigo-400 mb-1" />
            <span className="text-xs font-semibold text-slate-300 block">
              {uploading ? 'Importing CSV...' : 'Upload CSV File'}
            </span>
            <span className="text-[10px] text-slate-500 block">Auto-imported to PostgreSQL</span>
            <input
              type="file"
              accept=".csv"
              className="hidden"
              onChange={handleFileChange}
              disabled={uploading}
            />
          </label>
        </div>

        {/* Active Dataset Selector */}
        {datasets.length > 0 && (
          <div>
            <div className="text-[11px] font-bold text-slate-500 tracking-wider uppercase mb-2 px-2">Active Context</div>
            <select
              value={activeDatasetId || 'builtin'}
              onChange={(e) => setActiveDatasetId(e.target.value === 'builtin' ? null : e.target.value)}
              className="w-full bg-[#151D2A] border border-slate-700 text-slate-200 text-xs rounded-lg p-2.5 focus:ring-1 focus:ring-indigo-500 outline-none"
            >
              <option value="builtin">Built-in Database</option>
              {datasets.map((ds) => (
                <option key={ds.id} value={ds.id}>
                  📄 {ds.filename}
                </option>
              ))}
            </select>
          </div>
        )}
      </div>

      {/* Footer System Status */}
      <div className="p-4 border-t border-slate-800/80 bg-[#0B1220]">
        <div className="bg-[#151D2A] border border-slate-800 rounded-xl p-3">
          <div className="flex items-center gap-2">
            {dbConnected ? (
              <CheckCircle className="w-4 h-4 text-emerald-500" />
            ) : (
              <XCircle className="w-4 h-4 text-rose-500" />
            )}
            <span className="text-xs font-semibold text-slate-200">
              {dbConnected ? 'PostgreSQL Connected' : 'PostgreSQL Offline'}
            </span>
          </div>
          <div className="text-[11px] text-slate-400 mt-1 flex items-center gap-1">
            <Server className="w-3 h-3 text-slate-500" />
            Target: <code className="text-slate-300 font-mono">{dbName}</code>
          </div>
        </div>
      </div>
    </aside>
  );
};
