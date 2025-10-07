"""
RAG (Retrieval-Augmented Generation) module using LangChain.
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

from langchain.chains import RetrievalQA
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.schema import Document
from loguru import logger

from .embed_store import EmbeddingStore
from .summarize import ContentSummarizer


@dataclass
class RAGResponse:
    """Represents a RAG response with sources."""
    answer: str
    sources: List[Dict]
    confidence_score: Optional[float] = None
    query: Optional[str] = None


class ArtTechRAG:
    """RAG system specialized for art-technology knowledge."""
    
    def __init__(self, 
                 embedding_store: EmbeddingStore,
                 llm_model: str = "gpt-3.5-turbo",
                 openai_api_key: Optional[str] = None):
        self.embedding_store = embedding_store
        self.llm_model = llm_model
        self.openai_api_key = openai_api_key
        
        # Initialize LLM
        self.llm = self._initialize_llm()
        
        # Initialize summarizer for context condensation
        self.summarizer = ContentSummarizer()
        
        # Create specialized prompt template
        self.prompt_template = self._create_prompt_template()
        
        logger.info(f"Initialized ArtTechRAG with LLM: {llm_model}")
    
    def _initialize_llm(self):
        """Initialize the language model."""
        try:
            if self.openai_api_key:
                return OpenAI(
                    model_name=self.llm_model,
                    openai_api_key=self.openai_api_key,
                    temperature=0.1
                )
            else:
                # Fallback to a local model or mock
                logger.warning("No OpenAI API key provided, using mock LLM")
                return MockLLM()
        except Exception as e:
            logger.error(f"Failed to initialize LLM: {e}")
            return MockLLM()
    
    def _create_prompt_template(self) -> PromptTemplate:
        """Create a specialized prompt template for art-tech queries."""
        template = """
You are an expert in the intersection of art and technology. Use the following context to answer questions about how technology is being used in art, creative applications of AI, digital art installations, and related topics.

Context:
{context}

Question: {question}

Instructions:
- Provide accurate, informative answers based on the context
- If the context doesn't contain enough information, say so
- Focus on the artistic and technological aspects
- Mention specific examples when available
- Be concise but comprehensive

Answer:"""
        
        return PromptTemplate(
            template=template,
            input_variables=["context", "question"]
        )
    
    def query(self, question: str, n_sources: int = 5) -> RAGResponse:
        """Query the RAG system."""
        try:
            # Retrieve relevant documents
            search_results = self.embedding_store.hybrid_search(
                question, 
                n_results=n_sources
            )
            
            if not search_results:
                return RAGResponse(
                    answer="I couldn't find relevant information to answer your question.",
                    sources=[],
                    query=question
                )
            
            # Prepare context
            context = self._prepare_context(search_results)
            
            # Generate answer using LLM
            answer = self._generate_answer(question, context)
            
            # Prepare sources
            sources = self._prepare_sources(search_results)
            
            return RAGResponse(
                answer=answer,
                sources=sources,
                query=question
            )
            
        except Exception as e:
            logger.error(f"RAG query failed: {e}")
            return RAGResponse(
                answer=f"An error occurred while processing your question: {str(e)}",
                sources=[],
                query=question
            )
    
    def _prepare_context(self, search_results: List[Dict]) -> str:
        """Prepare context from search results."""
        context_parts = []
        
        for i, result in enumerate(search_results):
            content = result['content']
            metadata = result['metadata']
            
            # Add source information
            source_info = f"[Source {i+1}]"
            if metadata.get('title'):
                source_info += f" {metadata['title']}"
            if metadata.get('url'):
                source_info += f" ({metadata['url']})"
            
            context_parts.append(f"{source_info}\n{content}")
        
        return "\n\n".join(context_parts)
    
    def _generate_answer(self, question: str, context: str) -> str:
        """Generate answer using the LLM."""
        try:
            # Use the prompt template
            prompt = self.prompt_template.format(context=context, question=question)
            
            # Generate response
            response = self.llm(prompt)
            
            return response.strip()
            
        except Exception as e:
            logger.error(f"Answer generation failed: {e}")
            return "I'm sorry, I couldn't generate an answer to your question."
    
    def _prepare_sources(self, search_results: List[Dict]) -> List[Dict]:
        """Prepare source information."""
        sources = []
        
        for result in search_results:
            metadata = result['metadata']
            source = {
                'title': metadata.get('title', 'Untitled'),
                'url': metadata.get('url', ''),
                'domain': metadata.get('domain', ''),
                'publish_date': metadata.get('publish_date', ''),
                'content_preview': result['content'][:200] + "..." if len(result['content']) > 200 else result['content'],
                'relevance_score': result.get('combined_score', 0)
            }
            sources.append(source)
        
        return sources
    
    def get_context_summary(self, question: str, n_sources: int = 10) -> str:
        """Get a summary of relevant context without generating an answer."""
        try:
            search_results = self.embedding_store.hybrid_search(
                question, 
                n_results=n_sources
            )
            
            if not search_results:
                return "No relevant context found."
            
            # Combine all content
            all_content = " ".join(result['content'] for result in search_results)
            
            # Summarize the context
            summary = self.summarizer.summarize_text(all_content)
            
            if summary:
                return summary.content
            else:
                return "Could not summarize the context."
                
        except Exception as e:
            logger.error(f"Context summarization failed: {e}")
            return f"Error summarizing context: {str(e)}"


class MockLLM:
    """Mock LLM for testing when OpenAI API is not available."""
    
    def __call__(self, prompt: str) -> str:
        """Generate a mock response."""
        return """
Based on the provided context, I can see information about the intersection of art and technology. 
The context discusses various applications of artificial intelligence, computer vision, and digital technologies 
in artistic contexts. This represents a growing field where technological innovation meets creative expression, 
leading to new forms of interactive art, digital installations, and computational creativity.
        """.strip()


class ContextCondenser:
    """Condenses context to fit within LLM limits."""
    
    def __init__(self, max_context_length: int = 3000):
        self.max_context_length = max_context_length
    
    def condense_context(self, context: str) -> str:
        """Condense context to fit within limits."""
        if len(context) <= self.max_context_length:
            return context
        
        # Simple truncation with ellipsis
        return context[:self.max_context_length - 100] + "...\n[Context truncated]"


class AnswerSynthesizer:
    """Synthesizes answers from multiple sources."""
    
    def __init__(self, rag_system: ArtTechRAG):
        self.rag_system = rag_system
    
    def synthesize_answer(self, question: str, max_iterations: int = 3) -> RAGResponse:
        """Synthesize answer by iteratively refining the query."""
        current_question = question
        best_response = None
        
        for iteration in range(max_iterations):
            response = self.rag_system.query(current_question)
            
            if not best_response or len(response.sources) > len(best_response.sources):
                best_response = response
            
            # Refine question based on sources
            if response.sources:
                # Extract key terms from sources
                key_terms = self._extract_key_terms(response.sources)
                if key_terms:
                    current_question = f"{question} Focus on: {', '.join(key_terms[:3])}"
        
        return best_response or RAGResponse(
            answer="Could not synthesize an answer.",
            sources=[],
            query=question
        )
    
    def _extract_key_terms(self, sources: List[Dict]) -> List[str]:
        """Extract key terms from sources."""
        # Simple keyword extraction
        all_text = " ".join(source['content_preview'] for source in sources)
        
        # Extract words that appear frequently
        from collections import Counter
        import re
        
        words = re.findall(r'\b[a-zA-Z]{4,}\b', all_text.lower())
        word_counts = Counter(words)
        
        # Filter common words
        stop_words = {'this', 'that', 'with', 'from', 'they', 'have', 'been', 'were', 'said', 'each', 'which', 'their', 'time', 'will', 'about', 'there', 'could', 'other', 'after', 'first', 'well', 'also', 'where', 'much', 'some', 'these', 'into', 'more', 'than', 'very', 'what', 'know', 'just', 'over', 'think', 'also', 'back', 'here', 'work', 'life', 'only', 'still', 'should', 'through', 'before', 'being', 'made', 'right', 'while', 'during', 'without', 'under', 'between', 'among', 'within', 'beyond', 'above', 'below', 'around', 'near', 'far', 'close', 'open', 'high', 'low', 'big', 'small', 'long', 'short', 'wide', 'narrow', 'deep', 'shallow', 'thick', 'thin', 'heavy', 'light', 'fast', 'slow', 'quick', 'easy', 'hard', 'simple', 'complex', 'new', 'old', 'young', 'fresh', 'clean', 'dirty', 'hot', 'cold', 'warm', 'cool', 'dry', 'wet', 'full', 'empty', 'rich', 'poor', 'good', 'bad', 'better', 'worse', 'best', 'worst', 'same', 'different', 'similar', 'opposite', 'true', 'false', 'real', 'fake', 'natural', 'artificial', 'human', 'machine', 'digital', 'analog', 'virtual', 'physical', 'online', 'offline', 'public', 'private', 'free', 'paid', 'open', 'closed', 'active', 'passive', 'positive', 'negative', 'forward', 'backward', 'up', 'down', 'left', 'right', 'north', 'south', 'east', 'west', 'inside', 'outside', 'front', 'back', 'top', 'bottom', 'center', 'middle', 'edge', 'corner', 'side', 'end', 'beginning', 'start', 'finish', 'complete', 'incomplete', 'whole', 'part', 'piece', 'bit', 'lot', 'many', 'few', 'some', 'all', 'none', 'every', 'each', 'both', 'either', 'neither', 'one', 'two', 'three', 'first', 'second', 'third', 'last', 'next', 'previous', 'current', 'recent', 'past', 'future', 'now', 'then', 'today', 'yesterday', 'tomorrow', 'week', 'month', 'year', 'day', 'night', 'morning', 'afternoon', 'evening', 'hour', 'minute', 'second', 'moment', 'instant', 'period', 'time', 'age', 'generation', 'era', 'century', 'decade', 'season', 'spring', 'summer', 'autumn', 'winter', 'january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'}
        
        filtered_words = [word for word, count in word_counts.most_common(10) if word not in stop_words]
        return filtered_words


if __name__ == "__main__":
    # Test the RAG system
    from .embed_store import EmbeddingStore
    
    # Initialize components
    store = EmbeddingStore()
    rag = ArtTechRAG(store)
    
    # Test query
    response = rag.query("How is artificial intelligence being used in art?")
    
    print(f"Question: {response.query}")
    print(f"Answer: {response.answer}")
    print(f"Sources: {len(response.sources)}")
    
    for i, source in enumerate(response.sources):
        print(f"Source {i+1}: {source['title']} - {source['url']}")
