import React, { useState, useMemo } from 'react';
import { Copy, Check, Code } from 'lucide-react';
import { format } from 'sql-formatter';

interface SqlBlockProps {
  sql: string;
}

export const SqlBlock: React.FC<SqlBlockProps> = ({ sql }) => {
  const [copied, setCopied] = useState(false);

  // Prettify SQL formatting using sql-formatter
  const formattedSql = useMemo(() => {
    if (!sql) return '';
    try {
      return format(sql, { language: 'postgresql', tabWidth: 2, keywordCase: 'upper' });
    } catch {
      return sql;
    }
  }, [sql]);

  const handleCopy = () => {
    if (!formattedSql) return;
    navigator.clipboard.writeText(formattedSql);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  // SQL syntax highlighting helper for SQL keywords, strings, and numbers
  const highlightedTokens = useMemo(() => {
    if (!formattedSql) return null;

    const lines = formattedSql.split('\n');

    return lines.map((line, lIdx) => {
      const tokens = line.split(
        /(\b(?:SELECT|FROM|WHERE|JOIN|LEFT|RIGHT|INNER|OUTER|ON|GROUP BY|ORDER BY|HAVING|LIMIT|OFFSET|AS|AND|OR|NOT|IN|IS|NULL|LIKE|ILIKE|COUNT|AVG|MIN|MAX|SUM|STDDEV|CAST|COALESCE|CASE|WHEN|THEN|ELSE|END|CREATE|INSERT|UPDATE|DELETE|DROP|TABLE|INDEX|BOOLEAN|INTEGER|VARCHAR|DECIMAL|TIMESTAMP|DATE|TRUNCATE|CASCADE)\b|'[^']*'|"[^"]*"|\b\d+(?:\.\d+)?\b)/g
      );

      return (
        <div key={lIdx} className="table-row font-mono leading-relaxed">
          <span className="table-cell select-none text-right pr-4 text-slate-600 text-[11px] w-7 font-mono">{lIdx + 1}</span>
          <span className="table-cell whitespace-pre font-mono">
            {tokens.map((token, tIdx) => {
              if (!token) return null;
              const upper = token.toUpperCase();
              if (
                /^(SELECT|FROM|WHERE|JOIN|LEFT|RIGHT|INNER|OUTER|ON|GROUP BY|ORDER BY|HAVING|LIMIT|OFFSET|AS|AND|OR|NOT|IN|IS|NULL|LIKE|ILIKE|COUNT|AVG|MIN|MAX|SUM|STDDEV|CAST|COALESCE|CASE|WHEN|THEN|ELSE|END|CREATE|INSERT|UPDATE|DELETE|DROP|TABLE|INDEX|BOOLEAN|INTEGER|VARCHAR|DECIMAL|TIMESTAMP|DATE|TRUNCATE|CASCADE)$/.test(
                  upper
                )
              ) {
                return <span key={tIdx} className="text-cyan-400 font-bold">{token}</span>;
              }
              if (/^'[^']*'|^"[^"]*"$/.test(token)) {
                return <span key={tIdx} className="text-emerald-300">{token}</span>;
              }
              if (/^\d+(?:\.\d+)?$/.test(token)) {
                return <span key={tIdx} className="text-amber-300">{token}</span>;
              }
              return <span key={tIdx} className="text-slate-200">{token}</span>;
            })}
          </span>
        </div>
      );
    });
  }, [formattedSql]);

  return (
    <div className="my-3 rounded-xl border border-slate-800 bg-[#0F172A] overflow-hidden shadow-lg font-mono text-left">
      {/* Code Editor Header Bar */}
      <div className="px-4 py-2.5 bg-[#1E293B] border-b border-slate-800 flex items-center justify-between select-none">
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1.5 mr-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-rose-500/80 inline-block"></span>
            <span className="w-2.5 h-2.5 rounded-full bg-amber-500/80 inline-block"></span>
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-500/80 inline-block"></span>
          </div>
          <Code className="w-4 h-4 text-cyan-400" />
          <span className="text-xs font-bold text-slate-200 tracking-wide uppercase font-mono">SQL Query</span>
          <span className="text-[10px] bg-cyan-950 text-cyan-400 border border-cyan-800/60 px-1.5 py-0.5 rounded font-mono font-medium">PostgreSQL</span>
        </div>
        <button
          type="button"
          onClick={handleCopy}
          className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-300 hover:text-white bg-slate-800 hover:bg-slate-700 border border-slate-700 px-2.5 py-1 rounded-lg transition-all active:scale-95"
          title="Copy SQL Query"
        >
          {copied ? (
            <>
              <Check className="w-3.5 h-3.5 text-emerald-400" />
              <span className="text-emerald-400 font-medium">Copied!</span>
            </>
          ) : (
            <>
              <Copy className="w-3.5 h-3.5 text-slate-400" />
              <span>Copy SQL</span>
            </>
          )}
        </button>
      </div>

      {/* Dark Code Block Output */}
      <div className="p-4 bg-[#0B1220] overflow-x-auto text-xs font-mono leading-relaxed text-slate-200">
        <div className="table w-full border-collapse font-mono">
          {highlightedTokens}
        </div>
      </div>
    </div>
  );
};

