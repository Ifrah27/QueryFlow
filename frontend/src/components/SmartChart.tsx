import React from 'react';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';

interface SmartChartProps {
  columns: string[];
  rows: any[][];
}

export const SmartChart: React.FC<SmartChartProps> = ({ columns, rows }) => {
  if (!columns || !rows || columns.length < 2 || rows.length === 0) {
    return null;
  }

  const data = rows.slice(0, 20).map((row) => {
    const obj: Record<string, any> = {};
    columns.forEach((col, idx) => {
      const val = row[idx];
      obj[col] = typeof val === 'number' ? val : String(val);
    });
    return obj;
  });

  const xKey = columns[0];
  const yKey = columns[1];
  const isYNumeric = typeof data[0][yKey] === 'number';

  if (!isYNumeric) {
    return null;
  }

  return (
    <div className="bg-white border border-slate-200 rounded-xl p-4 space-y-3 mt-4">
      <div className="flex items-center justify-between">
        <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider">
          Visualization: {xKey} vs {yKey}
        </h4>
      </div>
      <div className="h-64 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" />
            <XAxis dataKey={xKey} tick={{ fontSize: 11 }} />
            <YAxis tick={{ fontSize: 11 }} />
            <Tooltip contentStyle={{ backgroundColor: '#0F172A', color: '#FFF', borderRadius: '8px', fontSize: '12px' }} />
            <Bar dataKey={yKey} fill="#5B5CE2" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
