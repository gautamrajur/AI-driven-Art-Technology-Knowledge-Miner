import React from 'react';
import { Sparkles, Brain, Search, TrendingUp, Database, Code, Users, Heart } from 'lucide-react';

const AboutPage: React.FC = () => {
  const features = [
    {
      icon: Search,
      title: 'Intelligent Search',
      description: 'Hybrid search combining vector similarity with keyword matching for precise results.',
    },
    {
      icon: TrendingUp,
      title: 'Trend Analysis',
      description: 'Statistical analysis of temporal patterns and co-occurrence trends in art-technology content.',
    },
    {
      icon: Brain,
      title: 'AI-Powered Insights',
      description: 'RAG (Retrieval-Augmented Generation) for AI-generated summaries and insights.',
    },
    {
      icon: Database,
      title: 'Rich Knowledge Base',
      description: 'Curated collection of art-technology intersections from diverse sources.',
    },
  ];

  const technologies = [
    { name: 'FastAPI', description: 'High-performance Python web framework' },
    { name: 'React + TypeScript', description: 'Modern frontend with type safety' },
    { name: 'ChromaDB', description: 'Vector database for embeddings' },
    { name: 'LangChain', description: 'Framework for LLM applications' },
    { name: 'Sentence Transformers', description: 'State-of-the-art embeddings' },
    { name: 'TailwindCSS', description: 'Utility-first CSS framework' },
    { name: 'React Query', description: 'Data fetching and caching' },
    { name: 'Recharts', description: 'Data visualization library' },
  ];

  return (
    <div className="space-y-16">
      {/* Hero Section */}
      <div className="text-center">
        <h1 className="text-4xl md:text-6xl font-bold text-gray-900 dark:text-white mb-6">
          About Art & Technology
          <span className="block bg-gradient-to-r from-primary-600 to-secondary-600 bg-clip-text text-transparent">
            Knowledge Miner
          </span>
        </h1>
        <p className="text-xl text-gray-600 dark:text-gray-300 mb-8 max-w-3xl mx-auto">
          A comprehensive platform for discovering, analyzing, and exploring the fascinating 
          intersections between art and technology through AI-powered knowledge mining.
        </p>
      </div>

      {/* Mission */}
      <div className="card">
        <div className="text-center">
          <Heart className="w-12 h-12 mx-auto mb-4 text-red-500" />
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">Our Mission</h2>
          <p className="text-lg text-gray-600 dark:text-gray-300 max-w-3xl mx-auto">
            To democratize access to knowledge about art-technology intersections by mining the public web, 
            creating a comprehensive knowledge base, and providing intelligent tools for discovery and analysis. 
            We believe that understanding these intersections is crucial for fostering innovation and creativity 
            in our increasingly digital world.
          </p>
        </div>
      </div>

      {/* Features */}
      <div>
        <h2 className="text-3xl font-bold text-center text-gray-900 dark:text-white mb-8">
          Key Features
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {features.map((feature, index) => {
            const Icon = feature.icon;
            return (
              <div key={index} className="card">
                <div className="flex items-start space-x-4">
                  <div className="w-12 h-12 bg-primary-100 dark:bg-primary-900 rounded-lg flex items-center justify-center flex-shrink-0">
                    <Icon className="w-6 h-6 text-primary-600 dark:text-primary-400" />
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                      {feature.title}
                    </h3>
                    <p className="text-gray-600 dark:text-gray-300">
                      {feature.description}
                    </p>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* How It Works */}
      <div className="card">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6 text-center">
          How It Works
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="text-center">
            <div className="w-16 h-16 bg-primary-100 dark:bg-primary-900 rounded-full flex items-center justify-center mx-auto mb-4">
              <span className="text-2xl font-bold text-primary-600 dark:text-primary-400">1</span>
            </div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">Discover</h3>
            <p className="text-gray-600 dark:text-gray-300">
              We crawl the web using DuckDuckGo search to discover content about art-technology intersections.
            </p>
          </div>
          <div className="text-center">
            <div className="w-16 h-16 bg-primary-100 dark:bg-primary-900 rounded-full flex items-center justify-center mx-auto mb-4">
              <span className="text-2xl font-bold text-primary-600 dark:text-primary-400">2</span>
            </div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">Process</h3>
            <p className="text-gray-600 dark:text-gray-300">
              Content is cleaned, chunked, and embedded using state-of-the-art AI models for semantic understanding.
            </p>
          </div>
          <div className="text-center">
            <div className="w-16 h-16 bg-primary-100 dark:bg-primary-900 rounded-full flex items-center justify-center mx-auto mb-4">
              <span className="text-2xl font-bold text-primary-600 dark:text-primary-400">3</span>
            </div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">Explore</h3>
            <p className="text-gray-600 dark:text-gray-300">
              Users can search, analyze trends, and discover insights through our intuitive interface.
            </p>
          </div>
        </div>
      </div>

      {/* Technology Stack */}
      <div>
        <h2 className="text-3xl font-bold text-center text-gray-900 dark:text-white mb-8">
          Technology Stack
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {technologies.map((tech, index) => (
            <div key={index} className="card text-center">
              <Code className="w-8 h-8 mx-auto mb-3 text-primary-600" />
              <h3 className="font-semibold text-gray-900 dark:text-white mb-2">{tech.name}</h3>
              <p className="text-sm text-gray-600 dark:text-gray-300">{tech.description}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Team */}
      <div className="card text-center">
        <Users className="w-12 h-12 mx-auto mb-4 text-primary-600" />
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">Built with ❤️</h2>
        <p className="text-lg text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
          This project was created as a demonstration of modern AI and web technologies working together 
          to solve real-world knowledge discovery challenges. It showcases the power of combining 
          traditional web crawling with modern AI techniques for meaningful insights.
        </p>
      </div>

      {/* Open Source */}
      <div className="card text-center bg-gradient-to-r from-primary-50 to-secondary-50 dark:from-primary-900/20 dark:to-secondary-900/20">
        <Sparkles className="w-12 h-12 mx-auto mb-4 text-primary-600" />
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">Open Source</h2>
        <p className="text-lg text-gray-600 dark:text-gray-300 max-w-2xl mx-auto mb-6">
          This project is open source and available on GitHub. We welcome contributions, 
          suggestions, and feedback from the community.
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <a
            href="https://github.com/suhasramanand/art-tech-knowledge-miner"
            target="_blank"
            rel="noopener noreferrer"
            className="btn-primary inline-flex items-center justify-center space-x-2"
          >
            <Code className="w-5 h-5" />
            <span>View on GitHub</span>
          </a>
          <a
            href="https://github.com/suhasramanand/art-tech-knowledge-miner/issues"
            target="_blank"
            rel="noopener noreferrer"
            className="btn-secondary inline-flex items-center justify-center space-x-2"
          >
            <span>Report Issues</span>
          </a>
        </div>
      </div>
    </div>
  );
};

export default AboutPage;
