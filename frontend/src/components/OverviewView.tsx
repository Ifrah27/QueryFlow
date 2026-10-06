import React from 'react';
import { Sparkles, FileText, Database, Table, Layers, ArrowUpRight, MessageSquare } from 'lucide-react';
import type { DatasetInfo, QueryHistoryItem } from '../types/api';

interface OverviewViewProps {
  datasets: DatasetInfo[];
  queryHistory: QueryHistoryItem[];
  onNavigate: (page: string) => void;
}

export const OverviewView: React.FC<OverviewViewProps> = ({ datasets, queryHistory, onNavigate }) => {
  const totalDatasets = datasets.length;
  const totalRows = datasets.reduce((acc, d) => acc + d.row_count, 0);
  const totalCols = datasets.reduce((acc, d) => acc + d.col_count, 0);
  const totalQueries = queryHistory.length;

  return (
    <div className="space-y-6">
      {/* Hero Banner */}
      <div className="relative overflow-hidden bg-gradient-to-r from-white to-indigo-50/60 border border-indigo-100 rounded-2xl p-6 sm:p-8 shadow-sm">
        <div className="relative z-10 max-w-3xl">
          <div className="inline-flex items-center gap-2 text-xs font-bold text-indigo-600 uppercase tracking-wider mb-2">
            <img src="/queryflow-logo.png" alt="QueryFlow" className="w-5 h-5 object-contain" />
            <span>QueryFlow Workspace &bull; Ask. Analyze. Transform.</span>
          </div>
          <h2 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
            Your data, intelligently explored.
          </h2>
          <p className="text-slate-600 text-sm font-medium mt-2 leading-relaxed">
            QueryFlow is an AI-powered data analysis platform that lets you explore datasets using natural language. Ask questions about your data, and QueryFlow generates and safely executes SQL against your PostgreSQL datasets to return clear answers, structured results, and actionable insights.
          </p>
          <div className="mt-5 flex items-center gap-3">
            <button
              onClick={() => onNavigate('chat')}
              className="inline-flex items-center gap-2 bg-gradient-to-r from-[#5B5CE2] to-[#7C5CFC] text-white px-4 py-2.5 rounded-xl font-semibold text-sm shadow-md shadow-indigo-500/20 hover:opacity-95 transition-all"
            >
              <MessageSquare className="w-4 h-4" />
              Ask Data Now
            </button>
            <button
              onClick={() => onNavigate('datasets')}
              className="inline-flex items-center gap-2 bg-white text-slate-700 border border-slate-200 px-4 py-2.5 rounded-xl font-semibold text-sm hover:bg-slate-50 transition-all"
            >
              <Database className="w-4 h-4 text-slate-500" />
              Manage Datasets
            </button>
          </div>
        </div>
      </div>

      {/* Stat Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white border border-slate-200/80 rounded-xl p-5 shadow-sm hover:shadow-md transition-all">
          <div className="w-9 h-9 rounded-lg bg-indigo-50 text-indigo-600 flex items-center justify-center mb-3">
            <FileText className="w-5 h-5" />
          </div>
          <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider block">Datasets</span>
          <span className="text-2xl font-extrabold text-slate-900 mt-1 block">{totalDatasets.toLocaleString()}</span>
          <span className="text-xs text-slate-500 mt-1 block font-medium">Active imported datasets</span>
        </div>

        <div className="bg-white border border-slate-200/80 rounded-xl p-5 shadow-sm hover:shadow-md transition-all">
          <div className="w-9 h-9 rounded-lg bg-purple-50 text-purple-600 flex items-center justify-center mb-3">
            <Layers className="w-5 h-5" />
          </div>
          <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider block">Rows Analyzed</span>
          <span className="text-2xl font-extrabold text-slate-900 mt-1 block">{totalRows.toLocaleString()}</span>
          <span className="text-xs text-slate-500 mt-1 block font-medium">Postgres record count</span>
        </div>

        <div className="bg-white border border-slate-200/80 rounded-xl p-5 shadow-sm hover:shadow-md transition-all">
          <div className="w-9 h-9 rounded-lg bg-emerald-50 text-emerald-600 flex items-center justify-center mb-3">
            <Table className="w-5 h-5" />
          </div>
          <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider block">Columns</span>
          <span className="text-2xl font-extrabold text-slate-900 mt-1 block">{totalCols.toLocaleString()}</span>
          <span className="text-xs text-slate-500 mt-1 block font-medium">Structured features</span>
        </div>

        <div className="bg-white border border-slate-200/80 rounded-xl p-5 shadow-sm hover:shadow-md transition-all">
          <div className="w-9 h-9 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center mb-3">
            <Sparkles className="w-5 h-5" />
          </div>
          <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider block">Queries Executed</span>
          <span className="text-2xl font-extrabold text-slate-900 mt-1 block">{totalQueries.toLocaleString()}</span>
          <span className="text-xs text-slate-500 mt-1 block font-medium">Agent SQL executions</span>
        </div>
      </div>

      {/* Connected Datasets & Activity Columns */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-base font-bold text-slate-900">Connected Datasets</h3>
            <button onClick={() => onNavigate('datasets')} className="text-xs font-semibold text-indigo-600 hover:text-indigo-700 flex items-center gap-1">
              View all <ArrowUpRight className="w-3.5 h-3.5" />
            </button>
          </div>

          {datasets.length === 0 ? (
            <div className="bg-white border border-slate-200 rounded-xl p-8 text-center">
              <FileText className="w-8 h-8 text-slate-400 mx-auto mb-2" />
              <p className="text-sm font-bold text-slate-900">No Custom Datasets Connected</p>
              <p className="text-xs text-slate-500 mt-1">Upload a CSV file from the sidebar to analyze your own custom dataset.</p>
            </div>
          ) : (
            <div className="space-y-3">
              {datasets.map((ds) => (
                <div key={ds.id} className="bg-white border border-slate-200/80 rounded-xl p-4 flex items-center justify-between shadow-sm hover:shadow-md transition-all">
                  <div>
                    <h4 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                      <FileText className="w-4 h-4 text-indigo-600" />
                      {ds.filename}
                    </h4>
                    <p className="text-xs text-slate-500 mt-1">
                      Table: <code className="text-slate-700 bg-slate-100 px-1.5 py-0.5 rounded font-mono">{ds.table_name}</code> &bull; {ds.row_count.toLocaleString()} rows &bull; {ds.col_count} columns
                    </p>
                  </div>
                  <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200 text-xs font-semibold">
                    Ready
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Recent Queries */}
        <div className="space-y-4">
          <h3 className="text-base font-bold text-slate-900">Recent Activity</h3>
          {queryHistory.length === 0 ? (
            <div className="bg-white border border-slate-200 rounded-xl p-8 text-center">
              <MessageSquare className="w-8 h-8 text-slate-400 mx-auto mb-2" />
              <p className="text-sm font-bold text-slate-900">No Queries Recorded Yet</p>
              <p className="text-xs text-slate-500 mt-1">Go to 'Ask Data' to execute your first query.</p>
            </div>
          ) : (
            <div className="space-y-3">
              {queryHistory.slice(0, 4).map((q, idx) => (
                <div key={idx} className="bg-white border border-slate-200/80 rounded-xl p-3.5 shadow-sm">
                  <p className="text-xs font-bold text-slate-900 line-clamp-2">{q.question}</p>
                  <div className="flex items-center justify-between text-[11px] text-slate-500 mt-2">
                    <span>Dataset: <code className="text-slate-700">{q.dataset}</code></span>
                    <span className="text-emerald-600 font-semibold">✓ Executed</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
