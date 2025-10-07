#!/usr/bin/env python3
"""
System validation script for Art & Technology Knowledge Miner.
Tests all components and provides a comprehensive health check.
"""

import sys
import time
import requests
from pathlib import Path
from typing import Dict, List, Any
import json

# Add pipeline to path
sys.path.append(str(Path(__file__).parent.parent / 'pipeline'))


class SystemValidator:
    """Validates the entire system."""
    
    def __init__(self):
        self.results = {}
        self.errors = []
        self.warnings = []
    
    def validate_pipeline(self) -> Dict[str, Any]:
        """Validate pipeline components."""
        print("Validating pipeline components...")
        pipeline_results = {}
        
        try:
            # Test imports
            from ingest import WebIngester
            from preprocess import ContentPreprocessor
            from embed_store import EmbeddingStore
            from summarize import ContentSummarizer
            from rag import ArtTechRAG
            from trends import TrendAnalyzer
            
            pipeline_results['imports'] = True
            
            # Test configuration loading
            ingester = WebIngester()
            pipeline_results['config_loading'] = True
            
            # Test preprocessor
            preprocessor = ContentPreprocessor()
            test_content = "This is a test document about art and technology."
            chunks = preprocessor.chunk_content(test_content, {'url': 'http://test.com'})
            pipeline_results['preprocessing'] = len(chunks) > 0
            
            # Test embedding store
            store = EmbeddingStore(collection_name="test_collection")
            pipeline_results['embedding_store'] = True
            
            # Test summarizer
            summarizer = ContentSummarizer()
            summary = summarizer.summarize_text(test_content)
            pipeline_results['summarization'] = summary is not None
            
            # Test RAG
            rag = ArtTechRAG(store)
            pipeline_results['rag_system'] = True
            
            # Test trend analyzer
            analyzer = TrendAnalyzer(store)
            pipeline_results['trend_analysis'] = True
            
        except Exception as e:
            pipeline_results['error'] = str(e)
            self.errors.append(f"Pipeline validation failed: {e}")
        
        return pipeline_results
    
    def validate_backend(self) -> Dict[str, Any]:
        """Validate backend API."""
        print("Validating backend API...")
        backend_results = {}
        
        try:
            # Test health endpoint
            response = requests.get("http://localhost:8000/healthz", timeout=10)
            backend_results['health_endpoint'] = response.status_code == 200
            
            if response.status_code == 200:
                health_data = response.json()
                backend_results['services_status'] = health_data.get('services', {})
                backend_results['database_status'] = health_data.get('database', False)
            
            # Test search endpoint
            response = requests.get("http://localhost:8000/search?q=test", timeout=10)
            backend_results['search_endpoint'] = response.status_code == 200
            
            # Test trends endpoint
            response = requests.get("http://localhost:8000/trends", timeout=10)
            backend_results['trends_endpoint'] = response.status_code == 200
            
            # Test stats endpoint
            response = requests.get("http://localhost:8000/stats", timeout=10)
            backend_results['stats_endpoint'] = response.status_code == 200
            
        except requests.exceptions.ConnectionError:
            backend_results['error'] = "Backend not running"
            self.warnings.append("Backend API not accessible - make sure to run 'make up' or start the backend")
        except Exception as e:
            backend_results['error'] = str(e)
            self.errors.append(f"Backend validation failed: {e}")
        
        return backend_results
    
    def validate_frontend(self) -> Dict[str, Any]:
        """Validate frontend."""
        print("Validating frontend...")
        frontend_results = {}
        
        try:
            # Test frontend accessibility
            response = requests.get("http://localhost:5173", timeout=10)
            frontend_results['frontend_accessible'] = response.status_code == 200
            
            # Check if it's serving HTML
            frontend_results['serves_html'] = 'text/html' in response.headers.get('content-type', '')
            
        except requests.exceptions.ConnectionError:
            frontend_results['error'] = "Frontend not running"
            self.warnings.append("Frontend not accessible - make sure to run 'make up' or start the frontend")
        except Exception as e:
            frontend_results['error'] = str(e)
            self.errors.append(f"Frontend validation failed: {e}")
        
        return frontend_results
    
    def validate_demo_data(self) -> Dict[str, Any]:
        """Validate demo data."""
        print("Validating demo data...")
        demo_results = {}
        
        demo_dir = Path(__file__).parent.parent / 'demo_data'
        
        if not demo_dir.exists():
            demo_results['error'] = "Demo data directory not found"
            self.warnings.append("Demo data not found - run create_demo_data.py to create demo dataset")
            return demo_results
        
        try:
            # Check demo documents
            demo_docs_file = demo_dir / 'demo_documents.json'
            if demo_docs_file.exists():
                with open(demo_docs_file, 'r') as f:
                    demo_docs = json.load(f)
                demo_results['demo_documents'] = len(demo_docs)
            else:
                demo_results['demo_documents'] = 0
            
            # Check ChromaDB
            chroma_dir = demo_dir / 'chroma_db'
            if chroma_dir.exists():
                demo_results['chroma_db_exists'] = True
                
                # Test embedding store
                from embed_store import EmbeddingStore
                store = EmbeddingStore(
                    collection_name="demo_art_tech_knowledge",
                    persist_directory=str(chroma_dir)
                )
                stats = store.get_collection_stats()
                demo_results['total_chunks'] = stats.get('total_chunks', 0)
            else:
                demo_results['chroma_db_exists'] = False
            
        except Exception as e:
            demo_results['error'] = str(e)
            self.errors.append(f"Demo data validation failed: {e}")
        
        return demo_results
    
    def validate_docker(self) -> Dict[str, Any]:
        """Validate Docker setup."""
        print("Validating Docker setup...")
        docker_results = {}
        
        try:
            import subprocess
            
            # Check if Docker is running
            result = subprocess.run(['docker', 'ps'], capture_output=True, text=True)
            docker_results['docker_running'] = result.returncode == 0
            
            # Check if our containers are running
            if docker_results['docker_running']:
                containers = ['art-tech-backend', 'art-tech-frontend', 'art-tech-chromadb']
                running_containers = []
                
                for container in containers:
                    result = subprocess.run(['docker', 'ps', '--filter', f'name={container}', '--format', '{{.Names}}'], 
                                          capture_output=True, text=True)
                    if container in result.stdout:
                        running_containers.append(container)
                
                docker_results['running_containers'] = running_containers
                docker_results['all_containers_running'] = len(running_containers) == len(containers)
            
        except Exception as e:
            docker_results['error'] = str(e)
            self.warnings.append(f"Docker validation failed: {e}")
        
        return docker_results
    
    def run_validation(self) -> Dict[str, Any]:
        """Run complete system validation."""
        print("Art & Technology Knowledge Miner - System Validation")
        print("=" * 60)
        
        self.results['pipeline'] = self.validate_pipeline()
        self.results['backend'] = self.validate_backend()
        self.results['frontend'] = self.validate_frontend()
        self.results['demo_data'] = self.validate_demo_data()
        self.results['docker'] = self.validate_docker()
        
        return self.results
    
    def print_summary(self):
        """Print validation summary."""
        print("\nValidation Summary")
        print("=" * 40)
        
        # Pipeline
        pipeline_ok = not self.results['pipeline'].get('error')
        print(f"Pipeline Components: {'✅ PASS' if pipeline_ok else '❌ FAIL'}")
        
        # Backend
        backend_ok = not self.results['backend'].get('error')
        print(f"Backend API: {'✅ PASS' if backend_ok else '❌ FAIL'}")
        
        # Frontend
        frontend_ok = not self.results['frontend'].get('error')
        print(f"Frontend: {'✅ PASS' if frontend_ok else '❌ FAIL'}")
        
        # Demo Data
        demo_ok = not self.results['demo_data'].get('error')
        print(f"Demo Data: {'✅ PASS' if demo_ok else '❌ FAIL'}")
        
        # Docker
        docker_ok = not self.results['docker'].get('error')
        print(f"Docker Setup: {'✅ PASS' if docker_ok else '❌ FAIL'}")
        
        # Overall status
        overall_ok = pipeline_ok and backend_ok and frontend_ok and demo_ok
        print(f"\nOverall Status: {'✅ SYSTEM READY' if overall_ok else '❌ ISSUES FOUND'}")
        
        # Print errors
        if self.errors:
            print(f"\nErrors ({len(self.errors)}):")
            for error in self.errors:
                print(f"  ❌ {error}")
        
        # Print warnings
        if self.warnings:
            print(f"\nWarnings ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  ⚠️  {warning}")
        
        # Print recommendations
        print("\nRecommendations:")
        if not backend_ok:
            print("  • Start the backend: make dev-backend")
        if not frontend_ok:
            print("  • Start the frontend: make dev-frontend")
        if not demo_ok:
            print("  • Create demo data: python scripts/create_demo_data.py")
        if not docker_ok:
            print("  • Start with Docker: make up")
        
        if overall_ok:
            print("  • System is ready! Visit http://localhost:5173")
            print("  • Run benchmark: python scripts/benchmark_efficiency.py")


def main():
    """Run system validation."""
    validator = SystemValidator()
    results = validator.run_validation()
    validator.print_summary()
    
    # Save results
    results_file = Path(__file__).parent / 'validation_results.json'
    with open(results_file, 'w') as f:
        json.dump({
            'results': results,
            'errors': validator.errors,
            'warnings': validator.warnings,
            'timestamp': time.time()
        }, f, indent=2)
    
    print(f"\nDetailed results saved to: {results_file}")


if __name__ == "__main__":
    main()
