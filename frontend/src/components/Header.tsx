import React from 'react';
import { Database } from 'lucide-react';
import type { DatasetInfo } from '../types/api';

interface HeaderProps {
  title: string;
  subtitle: string;
  activeDataset: DatasetInfo | null;
}

export const Header: React.FC<HeaderProps> = ({ title, subtitle, activeDataset }) => {
  return (
    <header className="flex flex-col md:flex-row md:items-center justify-between pb-5 border-b border-slate-200/80 mb-6 gap-3">
      <div>
        <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">{title}</h1>
        <p className="text-sm font-medium text-slate-500 mt-0.5">{subtitle}</p>
      </div>
      <div>
        {activeDataset ? (
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-indigo-50 text-indigo-700 border border-indigo-200 text-xs font-semibold">
            <Database className="w-3.5 h-3.5 text-indigo-600" />
            <span>{activeDataset.filename}</span>
            <span className="text-indigo-400">&bull;</span>
            <span className="text-indigo-600 font-mono">{activeDataset.row_count.toLocaleString()} rows</span>
          </div>
        ) : (
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-100 text-slate-700 border border-slate-200 text-xs font-semibold">
            <Database className="w-3.5 h-3.5 text-slate-500" />
            <span>Built-in Database Context</span>
          </div>
        )}
      </div>
    </header>
  );
};
