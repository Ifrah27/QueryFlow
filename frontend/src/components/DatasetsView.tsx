import React, { useState } from 'react';
import { Database, Trash2, Table, Eye, Layers } from 'lucide-react';
import type { DatasetInfo } from '../types/api';

interface DatasetsViewProps {
  datasets: DatasetInfo[];
  onDelete: (id: string) => void;
}

export const DatasetsView: React.FC<DatasetsViewProps> = ({ datasets, onDelete }) => {
  const [selectedDs, setSelectedDs] = useState<DatasetInfo | null>(null);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-slate-900">Datasets Management</h2>
          <p className="text-xs text-slate-500 mt-0.5">Explore PostgreSQL schema definitions and dataset previews.</p>
        </div>
      </div>

      {datasets.length === 0 ? (
        <div className="bg-white border border-slate-200 rounded-2xl p-12 text-center">
          <Database className="w-12 h-12 text-slate-300 mx-auto mb-3" />
          <h3 className="text-base font-bold text-slate-900">No Custom Datasets Found</h3>
          <p className="text-xs text-slate-500 max-w-sm mx-auto mt-1">
            Upload CSV files from the sidebar. They will automatically be parsed and inserted into PostgreSQL.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {datasets.map((ds) => (
            <div key={ds.id} className="bg-white border border-slate-200/80 rounded-xl p-5 shadow-sm hover:shadow-md transition-all space-y-4">
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
                    <Database className="w-4 h-4 text-indigo-600" />
                    {ds.filename}
                  </h3>
                  <p className="text-xs text-slate-500 mt-1">
                    Table: <code className="text-indigo-600 font-mono bg-indigo-50 px-1.5 py-0.5 rounded">{ds.table_name}</code>
                  </p>
                </div>
                <button
                  onClick={() => onDelete(ds.id)}
                  className="text-slate-400 hover:text-rose-600 p-1.5 rounded-lg hover:bg-rose-50 transition-all"
                  title="Drop PostgreSQL Table"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>

              <div className="flex items-center gap-4 text-xs font-semibold text-slate-600 bg-slate-50 p-2.5 rounded-lg border border-slate-100">
                <div className="flex items-center gap-1.5">
                  <Layers className="w-3.5 h-3.5 text-slate-400" />
                  <span>{ds.row_count.toLocaleString()} rows</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <Table className="w-3.5 h-3.5 text-slate-400" />
                  <span>{ds.col_count} columns</span>
                </div>
              </div>

              <button
                onClick={() => setSelectedDs(selectedDs?.id === ds.id ? null : ds)}
                className="w-full flex items-center justify-center gap-2 bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold text-xs py-2 rounded-lg transition-all"
              >
                <Eye className="w-3.5 h-3.5" />
                {selectedDs?.id === ds.id ? 'Hide Details' : 'View Schema & Preview'}
              </button>

              {/* Expandable Schema Table */}
              {selectedDs?.id === ds.id && (
                <div className="pt-3 border-t border-slate-100 space-y-3">
                  <div>
                    <h4 className="text-xs font-bold text-slate-800 mb-1.5">Schema Definition</h4>
                    <div className="overflow-x-auto border border-slate-200 rounded-lg">
                      <table className="w-full text-left text-xs">
                        <thead className="bg-slate-50 text-slate-600 font-bold border-b border-slate-200">
                          <tr>
                            <th className="p-2">Postgres Column</th>
                            <th className="p-2">Type</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-100">
                          {Object.entries(ds.schema).map(([col, type]) => (
                            <tr key={col}>
                              <td className="p-2 font-mono text-slate-900">{col}</td>
                              <td className="p-2 text-indigo-600 font-semibold">{type}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>

                  {ds.preview_records && ds.preview_records.length > 0 && (
                    <div>
                      <h4 className="text-xs font-bold text-slate-800 mb-1.5">Preview (First 10 Rows)</h4>
                      <div className="overflow-x-auto border border-slate-200 rounded-lg max-h-48">
                        <table className="w-full text-left text-[11px]">
                          <thead className="bg-slate-50 text-slate-600 font-bold border-b border-slate-200">
                            <tr>
                              {Object.keys(ds.preview_records[0]).map((h) => (
                                <th key={h} className="p-2 whitespace-nowrap">{h}</th>
                              ))}
                            </tr>
                          </thead>
                          <tbody className="divide-y divide-slate-100">
                            {ds.preview_records.map((r, i) => (
                              <tr key={i}>
                                {Object.values(r).map((v: any, j) => (
                                  <td key={j} className="p-2 whitespace-nowrap text-slate-700">{String(v)}</td>
                                ))}
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
