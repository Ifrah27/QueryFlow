import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkBreaks from 'remark-breaks';
import { Send, Download, CheckCircle, Table, BarChart2 } from 'lucide-react';
import type { ChatMessage, DatasetInfo } from '../types/api';
import { SmartChart } from './SmartChart';
import { SqlBlock } from './SqlBlock';

interface AskDataViewProps {
  messages: ChatMessage[];
  onSendMessage: (msg: string) => void;
  loading: boolean;
  activeDataset: DatasetInfo | null;
}

export const AskDataView: React.FC<AskDataViewProps> = ({
  messages,
  onSendMessage,
  loading,
  activeDataset,
}) => {
  const [input, setInput] = useState('');
  const [activeTabMap, setActiveTabMap] = useState<Record<string, 'table' | 'chart'>>({});

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || loading) return;
    onSendMessage(input.trim());
    setInput('');
  };

  const downloadCSV = (cols: string[], rows: any[][], filename = 'query_results.csv') => {
    const csvContent = [
      cols.join(','),
      ...rows.map((r) => r.map((cell) => `"${String(cell).replace(/"/g, '""')}"`).join(',')),
    ].join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', filename);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="flex flex-col h-[calc(100vh-140px)]">
      {/* Messages Scroll Container */}
      <div className="flex-1 overflow-y-auto pr-2 space-y-6 pb-6">
        {messages.length === 0 ? (
          <div className="bg-white border border-slate-200/80 rounded-2xl p-8 sm:p-12 text-center max-w-2xl mx-auto mt-4 shadow-sm">
            <div className="w-12 h-12 rounded-2xl bg-[#0B1220] p-1.5 flex items-center justify-center mx-auto mb-4 shadow-md shadow-indigo-500/10 border border-slate-800">
              <img src="/queryflow-logo.png" alt="QueryFlow" className="w-full h-full object-contain" />
            </div>
            <h3 className="text-xl font-extrabold text-slate-900 tracking-tight">What would you like to know?</h3>
            <p className="text-sm font-medium text-slate-500 mt-2 max-w-md mx-auto">
              Ask questions about your data in plain English and get SQL-powered insights instantly.
            </p>

            {/* Prompts Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mt-8 text-left">
              <button
                onClick={() => onSendMessage('How many records are in this dataset?')}
                className="p-3.5 rounded-xl border border-slate-200 hover:border-indigo-400 hover:bg-indigo-50/50 transition-all text-xs font-semibold text-slate-700 flex items-center justify-between group"
              >
                <span>📊 How many records are in this dataset?</span>
                <span className="text-slate-400 group-hover:text-indigo-600">&rarr;</span>
              </button>
              <button
                onClick={() => onSendMessage('Show me the top 5 records from the dataset.')}
                className="p-3.5 rounded-xl border border-slate-200 hover:border-indigo-400 hover:bg-indigo-50/50 transition-all text-xs font-semibold text-slate-700 flex items-center justify-between group"
              >
                <span>🔍 Show me the top 5 records from the dataset</span>
                <span className="text-slate-400 group-hover:text-indigo-600">&rarr;</span>
              </button>
              <button
                onClick={() => onSendMessage('Generate SQL to calculate summary metrics for numeric columns.')}
                className="p-3.5 rounded-xl border border-slate-200 hover:border-indigo-400 hover:bg-indigo-50/50 transition-all text-xs font-semibold text-slate-700 flex items-center justify-between group"
              >
                <span>📝 Calculate summary metrics for columns</span>
                <span className="text-slate-400 group-hover:text-indigo-600">&rarr;</span>
              </button>
              <button
                onClick={() => onSendMessage("I want to extract the data from the API endpoint 'https://pokeapi.co/api/v2/pokemon' and save it to data/extract folder in the csv format.")}
                className="p-3.5 rounded-xl border border-slate-200 hover:border-indigo-400 hover:bg-indigo-50/50 transition-all text-xs font-semibold text-slate-700 flex items-center justify-between group"
              >
                <span>⚡ Run Pokémon API ETL extraction pipeline</span>
                <span className="text-slate-400 group-hover:text-indigo-600">&rarr;</span>
              </button>
            </div>
          </div>
        ) : (
          messages.map((msg) => (
            <div key={msg.id} className={`flex gap-3 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              {msg.role === 'assistant' && (
                <div className="w-8 h-8 rounded-xl bg-[#0B1220] p-1 flex items-center justify-center shrink-0 shadow-md shadow-indigo-500/10 border border-slate-800">
                  <img src="/queryflow-logo.png" alt="QueryFlow" className="w-full h-full object-contain" />
                </div>
              )}

              <div className={`max-w-3xl rounded-2xl p-5 shadow-sm space-y-4 ${
                msg.role === 'user'
                  ? 'bg-gradient-to-r from-[#5B5CE2] to-[#7C5CFC] text-white rounded-br-none'
                  : 'bg-white border border-slate-200/80 text-slate-900 rounded-bl-none'
              }`}>
                {/* Markdown Formatted Message Text */}
                <div className="text-sm font-medium leading-relaxed max-w-none text-left">
                  {msg.role === 'user' ? (
                    <p className="m-0 text-white font-medium leading-relaxed">{msg.content}</p>
                  ) : (
                    <ReactMarkdown
                      remarkPlugins={[remarkGfm, remarkBreaks]}
                      components={{
                        p: ({ children }) => <p className="mb-2.5 last:mb-0 leading-relaxed text-slate-800 font-normal">{children}</p>,
                        strong: ({ children }) => <strong className="font-bold text-slate-900">{children}</strong>,
                        b: ({ children }) => <b className="font-bold text-slate-900">{children}</b>,
                        em: ({ children }) => <em className="italic text-slate-800">{children}</em>,
                        h1: ({ children }) => <h1 className="text-lg font-bold text-slate-900 mt-3 mb-2">{children}</h1>,
                        h2: ({ children }) => <h2 className="text-base font-bold text-slate-900 mt-3 mb-2">{children}</h2>,
                        h3: ({ children }) => <h3 className="text-sm font-bold text-slate-900 mt-2 mb-1">{children}</h3>,
                        h4: ({ children }) => <h4 className="text-xs font-bold uppercase tracking-wider text-slate-700 mt-2 mb-1">{children}</h4>,
                        ul: ({ children }) => <ul className="list-disc list-outside ml-5 my-2 space-y-1 text-slate-800">{children}</ul>,
                        ol: ({ children }) => <ol className="list-decimal list-outside ml-5 my-2 space-y-1 text-slate-800">{children}</ol>,
                        li: ({ children }) => <li className="pl-1 text-slate-800 leading-relaxed">{children}</li>,
                        code: ({ node, inline, className, children, ...props }: any) => {
                          const match = /language-(\w+)/.exec(className || '');
                          const codeText = String(children).replace(/\n$/, '');
                          if (!inline && (match?.[1] === 'sql' || className?.includes('sql'))) {
                            return <SqlBlock sql={codeText} />;
                          }
                          if (!inline && match) {
                            return (
                              <div className="my-3 rounded-xl border border-slate-800 bg-[#0F172A] p-4 overflow-x-auto font-mono text-xs text-slate-200">
                                <pre className="whitespace-pre font-mono">{codeText}</pre>
                              </div>
                            );
                          }
                          return (
                            <code className="bg-slate-100 text-indigo-600 px-1.5 py-0.5 rounded font-mono text-xs border border-slate-200" {...props}>
                              {children}
                            </code>
                          );
                        }
                      }}
                    >
                      {(() => {
                        let text = msg.content || '';
                        if (text.includes('[CONTEXT:') && text.includes('].')) {
                          text = text.split('].').slice(1).join('].').trim();
                        }
                        if (text.includes('Current question:')) {
                          text = text.split('Current question:').slice(1).join('Current question:').trim();
                        }
                        return text;
                      })()}
                    </ReactMarkdown>
                  )}
                </div>

                {/* Assistant Workflow Status Row (Only for executed dataset queries) */}
                {msg.role === 'assistant' && (msg.execution_status === 'executed' || (msg.intent === 'dataset' && (msg.sql || (msg.columns && msg.columns.length > 0)))) && (
                  <div className="flex items-center gap-3 text-xs font-semibold text-emerald-600 bg-slate-50 border border-slate-100 rounded-lg p-2.5">
                    <span className="flex items-center gap-1">
                      <CheckCircle className="w-3.5 h-3.5 text-emerald-500" />
                      Generated
                    </span>
                    <span className="text-slate-300">&rarr;</span>
                    <span className="flex items-center gap-1">
                      <CheckCircle className="w-3.5 h-3.5 text-emerald-500" />
                      Validated
                    </span>
                    <span className="text-slate-300">&rarr;</span>
                    <span className="flex items-center gap-1">
                      <CheckCircle className="w-3.5 h-3.5 text-emerald-500" />
                      Executed
                    </span>
                  </div>
                )}

                {/* Formatted Prettified SQL Block Component (Only for dataset queries) */}
                {msg.sql && (msg.intent === 'dataset' || msg.route === 'sql') && <SqlBlock sql={msg.sql} />}

                {/* Tabular Output & Visualization Options */}
                {msg.columns && msg.columns.length > 0 && msg.rows && msg.rows.length > 0 && (
                  <div className="space-y-3 pt-2">
                    <div className="flex items-center justify-between border-b border-slate-100 pb-2">
                      <div className="flex items-center gap-2 text-xs font-bold text-slate-700">
                        <span>Query Results</span>
                        <span className="px-2 py-0.5 rounded-full bg-slate-100 text-slate-600 font-mono text-[10px]">
                          {msg.row_count} rows
                        </span>
                      </div>
                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => setActiveTabMap((prev) => ({ ...prev, [msg.id]: 'table' }))}
                          className={`p-1.5 rounded-md text-xs font-semibold flex items-center gap-1 ${
                            (activeTabMap[msg.id] || 'table') === 'table'
                              ? 'bg-indigo-50 text-indigo-600'
                              : 'text-slate-400 hover:text-slate-600'
                          }`}
                        >
                          <Table className="w-3.5 h-3.5" />
                          Table
                        </button>
                        <button
                          onClick={() => setActiveTabMap((prev) => ({ ...prev, [msg.id]: 'chart' }))}
                          className={`p-1.5 rounded-md text-xs font-semibold flex items-center gap-1 ${
                            activeTabMap[msg.id] === 'chart'
                              ? 'bg-indigo-50 text-indigo-600'
                              : 'text-slate-400 hover:text-slate-600'
                          }`}
                        >
                          <BarChart2 className="w-3.5 h-3.5" />
                          Chart
                        </button>
                        <button
                          onClick={() => downloadCSV(msg.columns || [], msg.rows || [])}
                          className="px-2.5 py-1 rounded-lg border border-slate-200 text-slate-700 hover:bg-slate-50 text-xs font-semibold flex items-center gap-1 transition-all"
                        >
                          <Download className="w-3.5 h-3.5 text-slate-500" />
                          Download CSV
                        </button>
                      </div>
                    </div>

                    {/* View Switch */}
                    {activeTabMap[msg.id] === 'chart' ? (
                      <SmartChart columns={msg.columns} rows={msg.rows} />
                    ) : (
                      <div className="overflow-x-auto border border-slate-200 rounded-xl max-h-64">
                        <table className="w-full text-left text-xs">
                          <thead className="bg-slate-50 text-slate-700 font-bold border-b border-slate-200 sticky top-0">
                            <tr>
                              {msg.columns.map((col, idx) => (
                                <th key={idx} className="p-2.5 whitespace-nowrap">{col}</th>
                              ))}
                            </tr>
                          </thead>
                          <tbody className="divide-y divide-slate-100">
                            {msg.rows.map((row, idx) => (
                              <tr key={idx} className="hover:bg-slate-50/80">
                                {row.map((cell: any, cIdx: number) => (
                                  <td key={cIdx} className="p-2.5 whitespace-nowrap text-slate-800 font-mono text-[11px]">
                                    {String(cell)}
                                  </td>
                                ))}
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          ))
        )}

        {/* Loading Spinner Indicator */}
        {loading && (
          <div className="flex gap-3 items-center text-slate-500 text-xs font-medium bg-white border border-slate-200 rounded-xl p-4 max-w-md">
            <div className="w-4 h-4 border-2 border-indigo-600 border-t-transparent rounded-full animate-spin"></div>
            <span>Agent is curating prompt & querying PostgreSQL...</span>
          </div>
        )}
      </div>

      {/* Fixed Composer Bar */}
      <form onSubmit={handleSubmit} className="relative mt-auto">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder={activeDataset ? `Ask anything about ${activeDataset.filename}...` : "Ask anything about your data..."}
          disabled={loading}
          className="w-full bg-white border border-slate-300 rounded-2xl py-3.5 pl-4 pr-12 text-sm text-slate-900 shadow-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent placeholder:text-slate-400"
        />
        <button
          type="submit"
          disabled={!input.trim() || loading}
          className="absolute right-2 top-2 w-9 h-9 rounded-xl bg-gradient-to-r from-[#5B5CE2] to-[#7C5CFC] text-white flex items-center justify-center shadow-md shadow-indigo-500/30 hover:opacity-95 disabled:opacity-50 transition-all"
        >
          <Send className="w-4 h-4" />
        </button>
      </form>
    </div>
  );
};
