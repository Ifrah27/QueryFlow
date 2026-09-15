import React, { useState } from 'react';
import { History, ChevronDown, ChevronUp } from 'lucide-react';
import type { QueryHistoryItem } from '../types/api';

import { SqlBlock } from './SqlBlock';

interface QueryHistoryViewProps {
  history: QueryHistoryItem[];
}

export const QueryHistoryView: React.FC<QueryHistoryViewProps> = ({ history }) => {
  const [expandedIndex, setExpandedIndex] = useState<number | null>(0);

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-slate-900">Query History Audit Log</h2>
        <p className="text-xs text-slate-500 mt-0.5">Complete record of natural language prompts and generated SQL queries.</p>
      </div>

      {history.length === 0 ? (
        <div className="bg-white border border-slate-200 rounded-2xl p-12 text-center">
          <History className="w-12 h-12 text-slate-300 mx-auto mb-3" />
          <h3 className="text-base font-bold text-slate-900">No Query History Recorded</h3>
          <p className="text-xs text-slate-500 max-w-sm mx-auto mt-1">
            Questions asked in 'Ask Data' will automatically appear here with full execution trace.
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {history.map((q, idx) => (
            <div key={idx} className="bg-white border border-slate-200/80 rounded-xl p-4 shadow-sm space-y-3">
              <div
                onClick={() => setExpandedIndex(expandedIndex === idx ? null : idx)}
                className="flex items-center justify-between cursor-pointer"
              >
                <div className="flex items-center gap-3">
                  <div className="w-7 h-7 rounded-lg bg-emerald-50 text-emerald-600 flex items-center justify-center text-xs font-bold shrink-0">
                    ✓
                  </div>
                  <div>
                    <h3 className="text-sm font-bold text-slate-900">{q.question}</h3>
                    <p className="text-xs text-slate-500 mt-0.5">
                      Dataset: <code className="text-indigo-600 bg-indigo-50 px-1.5 py-0.5 rounded font-mono">{q.dataset}</code>
                    </p>
                  </div>
                </div>
                {expandedIndex === idx ? (
                  <ChevronUp className="w-4 h-4 text-slate-400" />
                ) : (
                  <ChevronDown className="w-4 h-4 text-slate-400" />
                )}
              </div>

              {expandedIndex === idx && (
                <div className="pt-3 border-t border-slate-100 space-y-3 text-xs">
                  <div>
                    <h4 className="font-bold text-slate-800 mb-1">Natural Language Answer</h4>
                    <p className="text-slate-600 bg-slate-50 p-3 rounded-lg border border-slate-100 leading-relaxed">
                      {q.answer}
                    </p>
                  </div>

                  {q.sql && <SqlBlock sql={q.sql} />}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
