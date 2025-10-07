import React from 'react';
import { Database, ExternalLink, Calendar, Globe, Loader2 } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { apiService } from '../services/api';

const SourcesPage: React.FC = () => {
  const { data: stats, isLoading, error } = useQuery({
    queryKey: ['stats'],
    queryFn: apiService.getStats,
    staleTime: 5 * 60 * 1000,
  });

  const formatDate = (dateString?: string) => {
    if (!dateString) return 'Unknown';
    try {
      return new Date(dateString).toLocaleDateString();
    } catch {
      return dateString;
    }
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
          Knowledge Base Sources
        </h1>
        <p className="text-gray-600 dark:text-gray-300">
          Explore the sources and statistics of our art-technology knowledge base
        </p>
      </div>

      {/* Loading State */}
      {isLoading && (
        <div className="card text-center">
          <Loader2 className="w-8 h-8 animate-spin mx-auto mb-4 text-primary-600" />
          <p className="text-gray-600 dark:text-gray-300">Loading statistics...</p>
        </div>
      )}

      {/* Error State */}
      {error && (
        <div className="card bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800">
          <p className="text-red-800 dark:text-red-200">
            Error: {error instanceof Error ? error.message : 'Failed to load statistics'}
          </p>
        </div>
      )}

      {/* Statistics */}
      {stats && !isLoading && (
        <div className="space-y-8">
          {/* Overview Stats */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="card text-center">
              <Database className="w-8 h-8 mx-auto mb-3 text-primary-600" />
              <div className="text-2xl font-bold text-gray-900 dark:text-white mb-1">
                {stats.total_chunks.toLocaleString()}
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-400">Knowledge Chunks</div>
            </div>
            
            <div className="card text-center">
              <Globe className="w-8 h-8 mx-auto mb-3 text-secondary-600" />
              <div className="text-2xl font-bold text-gray-900 dark:text-white mb-1">
                {stats.total_documents.toLocaleString()}
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-400">Documents</div>
            </div>
            
            <div className="card text-center">
              <ExternalLink className="w-8 h-8 mx-auto mb-3 text-green-600" />
              <div className="text-2xl font-bold text-gray-900 dark:text-white mb-1">
                {stats.unique_domains.toLocaleString()}
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-400">Unique Domains</div>
            </div>
            
            <div className="card text-center">
              <Calendar className="w-8 h-8 mx-auto mb-3 text-orange-600" />
              <div className="text-2xl font-bold text-gray-900 dark:text-white mb-1">
                {stats.date_range.min && stats.date_range.max ? 
                  `${formatDate(stats.date_range.min)} - ${formatDate(stats.date_range.max)}` :
                  'N/A'
                }
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-400">Date Range</div>
            </div>
          </div>

          {/* Collection Info */}
          <div className="card">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
              Collection Information
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h3 className="font-medium text-gray-700 dark:text-gray-300 mb-2">Collection Name</h3>
                <p className="text-gray-900 dark:text-white">{stats.collection_name}</p>
              </div>
              <div>
                <h3 className="font-medium text-gray-700 dark:text-gray-300 mb-2">Embedding Model</h3>
                <p className="text-gray-900 dark:text-white">{stats.embedding_model}</p>
              </div>
            </div>
          </div>

          {/* Data Sources */}
          <div className="card">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
              Data Sources
            </h2>
            <p className="text-gray-600 dark:text-gray-300 mb-4">
              Our knowledge base is built from publicly available web content that intersects 
              art and technology. We crawl and index content from:
            </p>
            <ul className="space-y-2 text-gray-600 dark:text-gray-300">
              <li className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-primary-500 rounded-full"></div>
                <span>Museum and gallery websites</span>
              </li>
              <li className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-primary-500 rounded-full"></div>
                <span>Academic papers and research publications</span>
              </li>
              <li className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-primary-500 rounded-full"></div>
                <span>Creative technology platforms and blogs</span>
              </li>
              <li className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-primary-500 rounded-full"></div>
                <span>Art and technology conference proceedings</span>
              </li>
              <li className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-primary-500 rounded-full"></div>
                <span>Digital art and media art platforms</span>
              </li>
            </ul>
          </div>

          {/* Methodology */}
          <div className="card">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
              Data Processing Methodology
            </h2>
            <div className="space-y-4 text-gray-600 dark:text-gray-300">
              <div>
                <h3 className="font-medium text-gray-900 dark:text-white mb-2">1. Content Discovery</h3>
                <p>We use DuckDuckGo search to discover relevant web pages using art-technology intersection queries.</p>
              </div>
              <div>
                <h3 className="font-medium text-gray-900 dark:text-white mb-2">2. Content Extraction</h3>
                <p>We extract clean text content using Trafilatura, respecting robots.txt and implementing respectful crawling practices.</p>
              </div>
              <div>
                <h3 className="font-medium text-gray-900 dark:text-white mb-2">3. Content Filtering</h3>
                <p>We filter content to ensure it contains both art-related and technology-related terms for relevance.</p>
              </div>
              <div>
                <h3 className="font-medium text-gray-900 dark:text-white mb-2">4. Text Processing</h3>
                <p>We chunk content into manageable pieces and generate embeddings using sentence-transformers.</p>
              </div>
              <div>
                <h3 className="font-medium text-gray-900 dark:text-white mb-2">5. Vector Storage</h3>
                <p>We store embeddings and metadata in ChromaDB for efficient similarity search and retrieval.</p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SourcesPage;
