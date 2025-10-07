"""
Embedding and vector storage module using SentenceTransformers and ChromaDB.
"""

import os
import pickle
from typing import List, Dict, Optional, Tuple
from pathlib import Path

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from loguru import logger

from .preprocess import ProcessedChunk


class EmbeddingStore:
    """Handles embedding generation and vector storage."""
    
    def __init__(self, 
                 collection_name: str = "art_tech_knowledge",
                 persist_directory: str = "./chroma_db",
                 embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.collection_name = collection_name
        self.persist_directory = persist_directory
        self.embedding_model_name = embedding_model
        
        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Initialize embedding model
        self.embedding_model = SentenceTransformer(embedding_model)
        
        # Get or create collection
        self.collection = self._get_or_create_collection()
        
        logger.info(f"Initialized EmbeddingStore with model: {embedding_model}")
        logger.info(f"Collection: {collection_name}, Directory: {persist_directory}")
    
    def _get_or_create_collection(self):
        """Get existing collection or create new one."""
        try:
            collection = self.client.get_collection(name=self.collection_name)
            logger.info(f"Loaded existing collection: {self.collection_name}")
            return collection
        except ValueError:
            # Collection doesn't exist, create it
            collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "Art & Technology Knowledge Base"}
            )
            logger.info(f"Created new collection: {self.collection_name}")
            return collection
    
    def add_chunks(self, chunks: List[ProcessedChunk], batch_size: int = 100) -> int:
        """Add chunks to the vector store."""
        if not chunks:
            return 0
        
        logger.info(f"Adding {len(chunks)} chunks to vector store")
        
        # Prepare data for ChromaDB
        documents = []
        metadatas = []
        ids = []
        
        for chunk in chunks:
            documents.append(chunk.content)
            metadatas.append({
                'url': chunk.source_url,
                'title': chunk.metadata.get('title', ''),
                'domain': chunk.metadata.get('domain', ''),
                'publish_date': chunk.metadata.get('publish_date', ''),
                'chunk_index': chunk.chunk_index,
                'total_chunks': chunk.total_chunks,
                'processed_at': chunk.metadata.get('processed_at', ''),
                'chunk_id': chunk.chunk_id
            })
            ids.append(chunk.chunk_id)
        
        # Add in batches
        total_added = 0
        for i in range(0, len(documents), batch_size):
            batch_docs = documents[i:i + batch_size]
            batch_metadatas = metadatas[i:i + batch_size]
            batch_ids = ids[i:i + batch_size]
            
            try:
                self.collection.add(
                    documents=batch_docs,
                    metadatas=batch_metadatas,
                    ids=batch_ids
                )
                total_added += len(batch_docs)
                logger.info(f"Added batch {i//batch_size + 1}: {len(batch_docs)} chunks")
            except Exception as e:
                logger.error(f"Failed to add batch {i//batch_size + 1}: {e}")
                continue
        
        logger.info(f"Successfully added {total_added} chunks to vector store")
        return total_added
    
    def search(self, 
               query: str, 
               n_results: int = 10,
               filter_metadata: Optional[Dict] = None) -> List[Dict]:
        """Search for similar chunks."""
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where=filter_metadata
            )
            
            # Format results
            formatted_results = []
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    formatted_results.append({
                        'content': doc,
                        'metadata': results['metadatas'][0][i],
                        'distance': results['distances'][0][i] if results['distances'] else None,
                        'id': results['ids'][0][i]
                    })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []
    
    def hybrid_search(self, 
                     query: str, 
                     n_results: int = 10,
                     keyword_weight: float = 0.3,
                     vector_weight: float = 0.7) -> List[Dict]:
        """Perform hybrid search combining vector similarity and keyword matching."""
        # Vector search
        vector_results = self.search(query, n_results=n_results)
        
        # Keyword search (simple implementation)
        keyword_results = self._keyword_search(query, n_results=n_results)
        
        # Combine and rank results
        combined_results = self._combine_search_results(
            vector_results, keyword_results, vector_weight, keyword_weight
        )
        
        return combined_results[:n_results]
    
    def _keyword_search(self, query: str, n_results: int = 10) -> List[Dict]:
        """Simple keyword-based search."""
        query_words = set(query.lower().split())
        
        # Get all documents (this is inefficient for large collections)
        try:
            all_results = self.collection.get()
            if not all_results['documents']:
                return []
            
            scored_results = []
            for i, doc in enumerate(all_results['documents']):
                doc_words = set(doc.lower().split())
                overlap = len(query_words.intersection(doc_words))
                if overlap > 0:
                    scored_results.append({
                        'content': doc,
                        'metadata': all_results['metadatas'][i],
                        'keyword_score': overlap / len(query_words),
                        'id': all_results['ids'][i]
                    })
            
            # Sort by keyword score
            scored_results.sort(key=lambda x: x['keyword_score'], reverse=True)
            return scored_results[:n_results]
            
        except Exception as e:
            logger.error(f"Keyword search failed: {e}")
            return []
    
    def _combine_search_results(self, 
                               vector_results: List[Dict],
                               keyword_results: List[Dict],
                               vector_weight: float,
                               keyword_weight: float) -> List[Dict]:
        """Combine and rank search results."""
        # Create a map of results by ID
        result_map = {}
        
        # Add vector results
        for result in vector_results:
            result_id = result['id']
            result_map[result_id] = result.copy()
            result_map[result_id]['vector_score'] = 1 - result.get('distance', 1)
            result_map[result_id]['keyword_score'] = 0
        
        # Add keyword results
        for result in keyword_results:
            result_id = result['id']
            if result_id in result_map:
                result_map[result_id]['keyword_score'] = result['keyword_score']
            else:
                result_map[result_id] = result.copy()
                result_map[result_id]['vector_score'] = 0
        
        # Calculate combined scores
        combined_results = []
        for result in result_map.values():
            combined_score = (
                result.get('vector_score', 0) * vector_weight +
                result.get('keyword_score', 0) * keyword_weight
            )
            result['combined_score'] = combined_score
            combined_results.append(result)
        
        # Sort by combined score
        combined_results.sort(key=lambda x: x['combined_score'], reverse=True)
        return combined_results
    
    def get_collection_stats(self) -> Dict:
        """Get statistics about the collection."""
        try:
            count = self.collection.count()
            return {
                'total_chunks': count,
                'collection_name': self.collection_name,
                'embedding_model': self.embedding_model_name,
                'persist_directory': self.persist_directory
            }
        except Exception as e:
            logger.error(f"Failed to get collection stats: {e}")
            return {}
    
    def delete_collection(self):
        """Delete the entire collection."""
        try:
            self.client.delete_collection(name=self.collection_name)
            logger.info(f"Deleted collection: {self.collection_name}")
        except Exception as e:
            logger.error(f"Failed to delete collection: {e}")
    
    def export_collection(self, export_path: str):
        """Export collection data to a file."""
        try:
            all_data = self.collection.get()
            
            export_data = {
                'documents': all_data['documents'],
                'metadatas': all_data['metadatas'],
                'ids': all_data['ids'],
                'collection_name': self.collection_name,
                'embedding_model': self.embedding_model_name
            }
            
            with open(export_path, 'wb') as f:
                pickle.dump(export_data, f)
            
            logger.info(f"Exported collection to: {export_path}")
            
        except Exception as e:
            logger.error(f"Failed to export collection: {e}")
    
    def import_collection(self, import_path: str):
        """Import collection data from a file."""
        try:
            with open(import_path, 'rb') as f:
                import_data = pickle.load(f)
            
            # Clear existing collection
            self.delete_collection()
            self.collection = self._get_or_create_collection()
            
            # Add imported data
            self.collection.add(
                documents=import_data['documents'],
                metadatas=import_data['metadatas'],
                ids=import_data['ids']
            )
            
            logger.info(f"Imported collection from: {import_path}")
            
        except Exception as e:
            logger.error(f"Failed to import collection: {e}")


# Utility functions
def create_embeddings(texts: List[str], model_name: str = "sentence-transformers/all-MiniLM-L6-v2") -> List[List[float]]:
    """Create embeddings for a list of texts."""
    model = SentenceTransformer(model_name)
    embeddings = model.encode(texts)
    return embeddings.tolist()


def cosine_similarity(a: List[float], b: List[float]) -> float:
    """Calculate cosine similarity between two vectors."""
    import numpy as np
    
    a_np = np.array(a)
    b_np = np.array(b)
    
    dot_product = np.dot(a_np, b_np)
    norm_a = np.linalg.norm(a_np)
    norm_b = np.linalg.norm(b_np)
    
    if norm_a == 0 or norm_b == 0:
        return 0
    
    return dot_product / (norm_a * norm_b)


if __name__ == "__main__":
    # Test the embedding store
    store = EmbeddingStore()
    
    # Test search
    results = store.search("artificial intelligence art", n_results=5)
    print(f"Found {len(results)} results")
    
    for result in results:
        print(f"- {result['metadata']['title']}: {result['content'][:100]}...")
