import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, TrendingUp, Database, Sparkles, ArrowRight } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { apiService } from '../services/api';

const HomePage: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const navigate = useNavigate();

  // Fetch stats for the hero section
  const { data: stats } = useQuery({
    queryKey: ['stats'],
    queryFn: apiService.getStats,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/search?q=${encodeURIComponent(searchQuery.trim())}`);
    }
  };

  const features = [
    {
      icon: Search,
      title: 'Intelligent Search',
      description: 'Discover art-technology intersections using hybrid search combining vector similarity and keyword matching.',
    },
    {
      icon: TrendingUp,
      title: 'Trend Analysis',
      description: 'Analyze temporal patterns and co-occurrence trends in art-technology content over time.',
    },
    {
      icon: Database,
      title: 'Rich Sources',
      description: 'Explore curated sources from museums, galleries, academic papers, and creative technology platforms.',
    },
    {
      icon: Sparkles,
      title: 'AI-Powered Insights',
      description: 'Get AI-generated summaries and insights about the intersection of art and technology.',
    },
  ];

  const quickQueries = [
    'artificial intelligence in art',
    'computer vision museums',
    'robotics performance art',
    'AR VR exhibitions',
    'generative art hardware',
  ];

  return (
    <div className="space-y-16">
      {/* Hero Section */}
      <div className="text-center">
        <h1 className="text-4xl md:text-6xl font-bold text-gray-900 dark:text-white mb-6">
          Discover Art & Technology
          <span className="block bg-gradient-to-r from-primary-600 to-secondary-600 bg-clip-text text-transparent">
            Intersections
          </span>
        </h1>
        <p className="text-xl text-gray-600 dark:text-gray-300 mb-8 max-w-3xl mx-auto">
          Mine the public web for instances of art–technology interplay, explore cultural-technical 
          intersections, and discover historical patterns in creative innovation.
        </p>

        {/* Search Bar */}
        <form onSubmit={handleSearch} className="max-w-2xl mx-auto mb-8">
          <div className="relative">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search for art-technology intersections..."
              className="w-full px-6 py-4 text-lg border border-gray-300 dark:border-gray-600 rounded-full focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
            />
            <button
              type="submit"
              className="absolute right-2 top-2 bottom-2 px-6 bg-primary-600 hover:bg-primary-700 text-white rounded-full transition-colors duration-200 flex items-center space-x-2"
            >
              <Search className="w-5 h-5" />
              <span>Search</span>
            </button>
          </div>
        </form>

        {/* Quick Queries */}
        <div className="flex flex-wrap justify-center gap-2 mb-8">
          {quickQueries.map((query) => (
            <button
              key={query}
              onClick={() => {
                setSearchQuery(query);
                navigate(`/search?q=${encodeURIComponent(query)}`);
              }}
              className="px-4 py-2 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-full hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors duration-200 text-sm"
            >
              {query}
            </button>
          ))}
        </div>

        {/* Stats */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-2xl mx-auto">
            <div className="text-center">
              <div className="text-3xl font-bold text-primary-600 dark:text-primary-400">
                {stats.total_chunks.toLocaleString()}
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-400">Knowledge Chunks</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-primary-600 dark:text-primary-400">
                {stats.total_documents.toLocaleString()}
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-400">Sources</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-primary-600 dark:text-primary-400">
                {stats.unique_domains.toLocaleString()}
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-400">Domains</div>
            </div>
          </div>
        )}
      </div>

      {/* Features Section */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
        {features.map((feature, index) => {
          const Icon = feature.icon;
          return (
            <div key={index} className="card text-center">
              <div className="w-12 h-12 bg-primary-100 dark:bg-primary-900 rounded-lg flex items-center justify-center mx-auto mb-4">
                <Icon className="w-6 h-6 text-primary-600 dark:text-primary-400" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                {feature.title}
              </h3>
              <p className="text-gray-600 dark:text-gray-300 text-sm">
                {feature.description}
              </p>
            </div>
          );
        })}
      </div>

      {/* CTA Section */}
      <div className="bg-gradient-to-r from-primary-600 to-secondary-600 rounded-2xl p-8 text-center text-white">
        <h2 className="text-3xl font-bold mb-4">Ready to Explore?</h2>
        <p className="text-xl mb-6 opacity-90">
          Start discovering the fascinating intersections between art and technology.
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <button
            onClick={() => navigate('/trends')}
            className="bg-white text-primary-600 hover:bg-gray-100 font-medium py-3 px-6 rounded-lg transition-colors duration-200 flex items-center justify-center space-x-2"
          >
            <TrendingUp className="w-5 h-5" />
            <span>View Trends</span>
            <ArrowRight className="w-4 h-4" />
          </button>
          <button
            onClick={() => navigate('/sources')}
            className="bg-transparent border-2 border-white text-white hover:bg-white hover:text-primary-600 font-medium py-3 px-6 rounded-lg transition-colors duration-200 flex items-center justify-center space-x-2"
          >
            <Database className="w-5 h-5" />
            <span>Browse Sources</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default HomePage;
