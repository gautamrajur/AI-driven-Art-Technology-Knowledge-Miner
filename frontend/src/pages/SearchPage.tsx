import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Search, ExternalLink, Calendar, Globe, Loader2 } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { apiService } from '../services/api';

const SearchPage: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const [query, setQuery] = useState(searchParams.get('q') || '');
  const [nResults, setNResults] = useState(10);
  const [hybrid, setHybrid] = useState(true);

  // Update query when URL params change
  useEffect(() => {
    const urlQuery = searchParams.get('q');
    if (urlQuery && urlQuery !== query) {
      setQuery(urlQuery);
    }
  }, [searchParams, query]);

  // Search query
  const { data: searchResults, isLoading, error } = useQuery({
    queryKey: ['search', query, nResults, hybrid],
    queryFn: () => apiService.search(query, nResults, hybrid),
    enabled: !!query.trim(),
    staleTime: 2 * 60 * 1000, // 2 minutes
  });

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      setSearchParams({ q: query.trim() });
    }
  };

  const formatDate = (dateString?: string) => {
    if (!dateString) return 'Unknown date';
    try {
      return new Date(dateString).toLocaleDateString();
    } catch {
      return dateString;
    }
  };

  const highlightText = (text: string, query: string) => {
    if (!query.trim()) return text;
    
    const regex = new RegExp(`(${query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi');
    const parts = text.split(regex);
    
    return parts.map((part, index) => 
      regex.test(part) ? (
        <mark key={index} className="bg-yellow-200 dark:bg-yellow-800 px-1 rounded">
          {part}
        </mark>
      ) : (
        part
      )
    );
  };

  return (
    <div className="space-y-8">
      {/* Search Header */}
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
          Search Knowledge Base
        </h1>
        <p className="text-gray-600 dark:text-gray-300">
          Discover art-technology intersections using intelligent search
        </p>
      </div>

      {/* Search Form */}
      <div className="card">
        <form onSubmit={handleSearch} className="space-y-4">
          <div className="relative">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search for art-technology intersections..."
              className="input-field pr-12"
            />
            <button
              type="submit"
              className="absolute right-2 top-2 bottom-2 px-4 bg-primary-600 hover:bg-primary-700 text-white rounded-md transition-colors duration-200 flex items-center space-x-2"
            >
              <Search className="w-4 h-4" />
              <span>Search</span>
            </button>
          </div>

          {/* Search Options */}
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Number of Results
              </label>
              <select
                value={nResults}
                onChange={(e) => setNResults(Number(e.target.value))}
                className="input-field"
              >
                <option value={5}>5 results</option>
                <option value={10}>10 results</option>
                <option value={20}>20 results</option>
                <option value={50}>50 results</option>
              </select>
            </div>
            <div className="flex-1">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Search Type
              </label>
              <select
                value={hybrid ? 'hybrid' : 'vector'}
                onChange={(e) => setHybrid(e.target.value === 'hybrid')}
                className="input-field"
              >
                <option value="hybrid">Hybrid (Vector + Keyword)</option>
                <option value="vector">Vector Only</option>
              </select>
            </div>
          </div>
        </form>
      </div>

      {/* Search Results */}
      {isLoading && (
        <div className="card text-center">
          <Loader2 className="w-8 h-8 animate-spin mx-auto mb-4 text-primary-600" />
          <p className="text-gray-600 dark:text-gray-300">Searching...</p>
        </div>
      )}

      {error && (
        <div className="card bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800">
          <p className="text-red-800 dark:text-red-200">
            Error: {error instanceof Error ? error.message : 'Search failed'}
          </p>
        </div>
      )}

      {searchResults && !isLoading && (
        <div className="space-y-6">
          {/* Results Summary */}
          <div className="text-center">
            <p className="text-gray-600 dark:text-gray-300">
              Found {searchResults.total_results} results for "{searchResults.query}"
            </p>
          </div>

          {/* Results List */}
          {searchResults.results.length === 0 ? (
            <div className="card text-center">
              <p className="text-gray-600 dark:text-gray-300">
                No results found. Try a different search query.
              </p>
            </div>
          ) : (
            <div className="space-y-6">
              {searchResults.results.map((result, index) => (
                <div key={index} className="card hover:shadow-lg transition-shadow duration-200">
                  <div className="flex justify-between items-start mb-3">
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white flex-1">
                      {highlightText(result.title, query)}
                    </h3>
                    <div className="flex items-center space-x-2 ml-4">
                      <span className="text-sm text-gray-500 dark:text-gray-400">
                        Score: {result.relevance_score.toFixed(3)}
                      </span>
                      <a
                        href={result.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-primary-600 hover:text-primary-700 dark:text-primary-400 dark:hover:text-primary-300"
                      >
                        <ExternalLink className="w-4 h-4" />
                      </a>
                    </div>
                  </div>

                  <div className="mb-4">
                    <p className="text-gray-700 dark:text-gray-300 leading-relaxed">
                      {highlightText(result.content, query)}
                    </p>
                  </div>

                  <div className="flex flex-wrap items-center gap-4 text-sm text-gray-500 dark:text-gray-400">
                    <div className="flex items-center space-x-1">
                      <Globe className="w-4 h-4" />
                      <span>{result.domain}</span>
                    </div>
                    {result.publish_date && (
                      <div className="flex items-center space-x-1">
                        <Calendar className="w-4 h-4" />
                        <span>{formatDate(result.publish_date)}</span>
                      </div>
                    )}
                    <div className="text-xs">
                      Chunk {result.chunk_index + 1} of {result.total_chunks}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* No Query State */}
      {!query.trim() && !isLoading && (
        <div className="card text-center">
          <Search className="w-12 h-12 mx-auto mb-4 text-gray-400" />
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
            Start Your Search
          </h3>
          <p className="text-gray-600 dark:text-gray-300">
            Enter a query above to discover art-technology intersections in our knowledge base.
          </p>
        </div>
      )}
    </div>
  );
};

export default SearchPage;
