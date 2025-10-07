import React, { useState } from 'react';
import { TrendingUp, Calendar, BarChart3, Loader2 } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts';
import { apiService } from '../services/api';

const TrendsPage: React.FC = () => {
  const [facet, setFacet] = useState('all');
  const [granularity, setGranularity] = useState('year');
  const [fromDate, setFromDate] = useState('');
  const [toDate, setToDate] = useState('');
  const [minCooccurrence, setMinCooccurrence] = useState(2);

  // Fetch trends data
  const { data: trendsData, isLoading, error } = useQuery({
    queryKey: ['trends', facet, granularity, fromDate, toDate, minCooccurrence],
    queryFn: () => apiService.getTrends(facet, fromDate || undefined, toDate || undefined, granularity, minCooccurrence),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

  const facets = [
    { value: 'all', label: 'All Content' },
    { value: 'AI', label: 'Artificial Intelligence' },
    { value: 'AR_VR', label: 'AR/VR' },
    { value: 'Robotics', label: 'Robotics' },
    { value: 'Generative', label: 'Generative Art' },
    { value: 'HCI', label: 'Human-Computer Interaction' },
    { value: 'Fabrication', label: 'Digital Fabrication' },
  ];

  const granularities = [
    { value: 'year', label: 'Year' },
    { value: 'month', label: 'Month' },
    { value: 'quarter', label: 'Quarter' },
  ];

  const formatTooltipValue = (value: number, name: string) => {
    if (name === 'count') return [`${value} documents`, 'Count'];
    if (name === 'trend_slope') return [`${value.toFixed(3)}`, 'Trend Slope'];
    return [value, name];
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
          Trend Analysis
        </h1>
        <p className="text-gray-600 dark:text-gray-300">
          Explore temporal patterns and co-occurrence trends in art-technology content
        </p>
      </div>

      {/* Controls */}
      <div className="card">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Facet
            </label>
            <select
              value={facet}
              onChange={(e) => setFacet(e.target.value)}
              className="input-field"
            >
              {facets.map((f) => (
                <option key={f.value} value={f.value}>
                  {f.label}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Granularity
            </label>
            <select
              value={granularity}
              onChange={(e) => setGranularity(e.target.value)}
              className="input-field"
            >
              {granularities.map((g) => (
                <option key={g.value} value={g.value}>
                  {g.label}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              From Date
            </label>
            <input
              type="date"
              value={fromDate}
              onChange={(e) => setFromDate(e.target.value)}
              className="input-field"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              To Date
            </label>
            <input
              type="date"
              value={toDate}
              onChange={(e) => setToDate(e.target.value)}
              className="input-field"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Min Co-occurrence
            </label>
            <input
              type="number"
              min="1"
              value={minCooccurrence}
              onChange={(e) => setMinCooccurrence(Number(e.target.value))}
              className="input-field"
            />
          </div>
        </div>
      </div>

      {/* Loading State */}
      {isLoading && (
        <div className="card text-center">
          <Loader2 className="w-8 h-8 animate-spin mx-auto mb-4 text-primary-600" />
          <p className="text-gray-600 dark:text-gray-300">Analyzing trends...</p>
        </div>
      )}

      {/* Error State */}
      {error && (
        <div className="card bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800">
          <p className="text-red-800 dark:text-red-200">
            Error: {error instanceof Error ? error.message : 'Trend analysis failed'}
          </p>
        </div>
      )}

      {/* Trends Data */}
      {trendsData && !isLoading && (
        <div className="space-y-8">
          {/* Temporal Trends Chart */}
          <div className="card">
            <div className="flex items-center space-x-2 mb-6">
              <TrendingUp className="w-6 h-6 text-primary-600" />
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                Temporal Trends - {facets.find(f => f.value === facet)?.label}
              </h2>
            </div>

            {trendsData.trends.length > 0 ? (
              <div className="h-96">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={trendsData.trends}>
                    <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
                    <XAxis 
                      dataKey="time_period" 
                      className="text-sm"
                      tick={{ fontSize: 12 }}
                    />
                    <YAxis 
                      className="text-sm"
                      tick={{ fontSize: 12 }}
                    />
                    <Tooltip 
                      formatter={formatTooltipValue}
                      labelStyle={{ color: '#374151' }}
                      contentStyle={{ 
                        backgroundColor: 'white', 
                        border: '1px solid #e5e7eb',
                        borderRadius: '8px'
                      }}
                    />
                    <Line 
                      type="monotone" 
                      dataKey="count" 
                      stroke="#0ea5e9" 
                      strokeWidth={2}
                      dot={{ fill: '#0ea5e9', strokeWidth: 2, r: 4 }}
                      activeDot={{ r: 6, stroke: '#0ea5e9', strokeWidth: 2 }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            ) : (
              <div className="text-center py-8">
                <BarChart3 className="w-12 h-12 mx-auto mb-4 text-gray-400" />
                <p className="text-gray-600 dark:text-gray-300">
                  No trend data available for the selected parameters.
                </p>
              </div>
            )}
          </div>

          {/* Trend Statistics */}
          {trendsData.trends.length > 0 && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="card text-center">
                <div className="text-2xl font-bold text-primary-600 dark:text-primary-400 mb-2">
                  {trendsData.trends.length}
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400">Time Periods</div>
              </div>
              <div className="card text-center">
                <div className="text-2xl font-bold text-primary-600 dark:text-primary-400 mb-2">
                  {trendsData.trends.reduce((sum, t) => sum + t.count, 0).toLocaleString()}
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400">Total Documents</div>
              </div>
              <div className="card text-center">
                <div className="text-2xl font-bold text-primary-600 dark:text-primary-400 mb-2">
                  {trendsData.trends.length > 0 ? 
                    (trendsData.trends.reduce((sum, t) => sum + t.count, 0) / trendsData.trends.length).toFixed(1) : 
                    '0'
                  }
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400">Avg per Period</div>
              </div>
            </div>
          )}

          {/* Co-occurrence Analysis */}
          <div className="card">
            <div className="flex items-center space-x-2 mb-6">
              <BarChart3 className="w-6 h-6 text-secondary-600" />
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                Tag Co-occurrence Analysis
              </h2>
            </div>

            {trendsData.cooccurrence.length > 0 ? (
              <div className="space-y-4">
                {/* Top Co-occurrences Chart */}
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart 
                      data={trendsData.cooccurrence.slice(0, 10).map(cooc => ({
                        name: `${cooc.tag1} + ${cooc.tag2}`,
                        count: cooc.count,
                        correlation: cooc.correlation || 0
                      }))}
                      layout="horizontal"
                    >
                      <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
                      <XAxis type="number" className="text-sm" tick={{ fontSize: 12 }} />
                      <YAxis 
                        type="category" 
                        dataKey="name" 
                        className="text-sm" 
                        tick={{ fontSize: 10 }}
                        width={120}
                      />
                      <Tooltip 
                        formatter={(value, name) => [
                          name === 'count' ? `${value} occurrences` : value.toFixed(3),
                          name === 'count' ? 'Count' : 'Correlation'
                        ]}
                      />
                      <Bar dataKey="count" fill="#d946ef" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>

                {/* Co-occurrence Table */}
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-gray-200 dark:border-gray-700">
                        <th className="text-left py-2 font-medium text-gray-700 dark:text-gray-300">Tags</th>
                        <th className="text-right py-2 font-medium text-gray-700 dark:text-gray-300">Count</th>
                        <th className="text-right py-2 font-medium text-gray-700 dark:text-gray-300">Correlation</th>
                      </tr>
                    </thead>
                    <tbody>
                      {trendsData.cooccurrence.slice(0, 20).map((cooc, index) => (
                        <tr key={index} className="border-b border-gray-100 dark:border-gray-800">
                          <td className="py-2 text-gray-900 dark:text-gray-100">
                            <span className="font-medium">{cooc.tag1}</span> + <span className="font-medium">{cooc.tag2}</span>
                          </td>
                          <td className="text-right py-2 text-gray-600 dark:text-gray-400">
                            {cooc.count}
                          </td>
                          <td className="text-right py-2 text-gray-600 dark:text-gray-400">
                            {cooc.correlation ? cooc.correlation.toFixed(3) : 'N/A'}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            ) : (
              <div className="text-center py-8">
                <Calendar className="w-12 h-12 mx-auto mb-4 text-gray-400" />
                <p className="text-gray-600 dark:text-gray-300">
                  No co-occurrence data available for the selected parameters.
                </p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default TrendsPage;
