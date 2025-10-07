#!/usr/bin/env python3
"""
Create demo dataset for Art & Technology Knowledge Miner.
This script creates a small, curated dataset for demonstration purposes.
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add pipeline to path
sys.path.append(str(Path(__file__).parent.parent / 'pipeline'))

from preprocess import BatchPreprocessor
from embed_store import EmbeddingStore


def create_demo_documents():
    """Create demo documents with art-technology content."""
    documents = [
        {
            'url': 'https://example.com/ai-art-museum',
            'title': 'AI Art Exhibition Opens at Modern Museum',
            'content': '''
            The Modern Museum of Art has opened a groundbreaking exhibition showcasing artificial intelligence in contemporary art. 
            The exhibition features works by leading artists who use machine learning algorithms to create stunning visual pieces. 
            Visitors can interact with AI-powered installations that respond to their movements and emotions. 
            The museum's curators believe this represents a new frontier in artistic expression, where technology and creativity merge seamlessly.
            The exhibition includes works that explore themes of human-AI collaboration, algorithmic beauty, and the future of digital creativity.
            ''',
            'publish_date': '2024-01-15',
            'domain': 'example.com'
        },
        {
            'url': 'https://tech-art.org/robotics-performance',
            'title': 'Robotic Performance Art Takes Center Stage',
            'content': '''
            A new wave of performance art is emerging that incorporates robotics and automation. 
            Artists are programming robots to perform choreographed dances, create music, and even paint canvases. 
            These robotic performers challenge traditional notions of what constitutes art and who can be an artist. 
            The performances often explore themes of human-robot interaction, artificial creativity, and the boundaries between organic and synthetic expression.
            Critics have praised the technical innovation while questioning the emotional depth of machine-generated art.
            ''',
            'publish_date': '2024-02-20',
            'domain': 'tech-art.org'
        },
        {
            'url': 'https://digital-gallery.com/ar-exhibition',
            'title': 'Augmented Reality Transforms Gallery Experience',
            'content': '''
            The Digital Gallery has launched an innovative augmented reality exhibition that transforms how visitors experience art. 
            Using AR technology, visitors can see artworks come to life, interact with digital elements, and explore hidden layers of meaning. 
            The exhibition features both traditional paintings enhanced with AR overlays and purely digital artworks that exist only in augmented space. 
            This technology allows for new forms of storytelling and artistic expression that were previously impossible.
            The gallery's director believes AR represents the future of art exhibition and visitor engagement.
            ''',
            'publish_date': '2024-03-10',
            'domain': 'digital-gallery.com'
        },
        {
            'url': 'https://creative-tech.edu/generative-art-research',
            'title': 'University Research Advances Generative Art Techniques',
            'content': '''
            Researchers at Creative Technology University have developed new algorithms for generative art creation. 
            Their work combines computer vision, machine learning, and traditional artistic principles to create unique digital artworks. 
            The research team has published several papers on algorithmic creativity and the role of AI in artistic expression. 
            Their generative art system can create paintings, sculptures, and interactive installations based on input parameters and artistic styles.
            The university has established a new lab dedicated to exploring the intersection of technology and creativity.
            ''',
            'publish_date': '2024-01-30',
            'domain': 'creative-tech.edu'
        },
        {
            'url': 'https://museum-tech.org/virtual-reality-art',
            'title': 'Virtual Reality Opens New Dimensions for Artists',
            'content': '''
            Virtual reality technology is revolutionizing how artists create and present their work. 
            VR art installations allow viewers to step inside paintings, explore 3D sculptures from all angles, and experience immersive storytelling. 
            Artists are using VR tools to create environments that would be impossible in physical space, pushing the boundaries of spatial art. 
            Museums are investing heavily in VR technology to enhance visitor experiences and reach new audiences.
            The technology enables new forms of collaborative art creation across geographical boundaries.
            ''',
            'publish_date': '2024-02-15',
            'domain': 'museum-tech.org'
        },
        {
            'url': 'https://art-ai.com/neural-style-transfer',
            'title': 'Neural Style Transfer Creates New Artistic Possibilities',
            'content': '''
            Neural style transfer technology is enabling artists to create unique works by combining different artistic styles. 
            This AI technique analyzes the style of one artwork and applies it to another image, creating hybrid pieces that blend multiple artistic traditions. 
            Artists are using this technology to explore new aesthetic possibilities and challenge traditional notions of artistic style. 
            The technique has been applied to everything from classical paintings to contemporary digital art.
            Critics debate whether AI-assisted art maintains the authenticity and emotional depth of traditional artistic creation.
            ''',
            'publish_date': '2024-03-05',
            'domain': 'art-ai.com'
        },
        {
            'url': 'https://interactive-art.net/haptic-interfaces',
            'title': 'Haptic Technology Enhances Interactive Art Experiences',
            'content': '''
            Haptic technology is being integrated into interactive art installations to create multi-sensory experiences. 
            Visitors can feel textures, vibrations, and forces that correspond to visual and auditory elements of the artwork. 
            This technology enables artists to create immersive experiences that engage multiple senses simultaneously. 
            Museums are experimenting with haptic interfaces to make art more accessible to visitors with visual impairments.
            The technology opens new possibilities for tactile art and sensory storytelling.
            ''',
            'publish_date': '2024-01-25',
            'domain': 'interactive-art.net'
        },
        {
            'url': 'https://digital-fabrication.org/3d-printing-art',
            'title': '3D Printing Revolutionizes Sculpture and Installation Art',
            'content': '''
            Three-dimensional printing technology is transforming sculpture and installation art by enabling complex geometries and rapid prototyping. 
            Artists are using 3D printing to create intricate sculptures that would be impossible to make by traditional methods. 
            The technology allows for precise control over form, texture, and material properties, opening new creative possibilities. 
            Some artists are exploring the aesthetic potential of 3D printing artifacts and layer lines as design elements.
            The technology is making art creation more accessible and enabling new forms of collaborative design.
            ''',
            'publish_date': '2024-02-28',
            'domain': 'digital-fabrication.org'
        },
        {
            'url': 'https://media-art.org/computer-vision-museums',
            'title': 'Computer Vision Enhances Museum Visitor Analytics',
            'content': '''
            Museums are implementing computer vision systems to analyze visitor behavior and optimize exhibition layouts. 
            These systems track how visitors move through galleries, which artworks attract attention, and how long people spend viewing different pieces. 
            The data helps curators understand visitor preferences and create more engaging exhibitions. 
            Computer vision is also being used to detect emotions and engagement levels, providing insights into the impact of different artworks.
            Privacy advocates have raised concerns about visitor tracking and data collection in cultural institutions.
            ''',
            'publish_date': '2024-03-15',
            'domain': 'media-art.org'
        },
        {
            'url': 'https://creative-algorithms.com/procedural-art',
            'title': 'Procedural Art Generation Explores Algorithmic Creativity',
            'content': '''
            Procedural art generation uses algorithms to create artworks based on mathematical rules and random processes. 
            Artists program systems that generate unique pieces each time they run, exploring the intersection of mathematics and aesthetics. 
            This approach challenges traditional notions of authorship and artistic control, raising questions about the role of the artist in algorithmic creation. 
            Procedural art has applications in video games, digital media, and interactive installations.
            The field is expanding rapidly as computational power increases and new algorithms are developed.
            ''',
            'publish_date': '2024-01-20',
            'domain': 'creative-algorithms.com'
        }
    ]
    
    return documents


def create_demo_dataset():
    """Create and process demo dataset."""
    print("Creating demo dataset...")
    
    # Create demo documents
    documents = create_demo_documents()
    print(f"Created {len(documents)} demo documents")
    
    # Save raw documents
    demo_dir = Path(__file__).parent.parent / 'demo_data'
    demo_dir.mkdir(exist_ok=True)
    
    with open(demo_dir / 'demo_documents.json', 'w') as f:
        json.dump(documents, f, indent=2)
    
    print(f"Saved demo documents to {demo_dir / 'demo_documents.json'}")
    
    # Process documents into chunks
    preprocessor = BatchPreprocessor(chunk_size=500, chunk_overlap=100)
    chunks = preprocessor.process_documents(documents)
    chunks = preprocessor.filter_chunks(chunks, min_length=50)
    
    print(f"Created {len(chunks)} chunks from {len(documents)} documents")
    
    # Create embedding store
    store = EmbeddingStore(
        collection_name="demo_art_tech_knowledge",
        persist_directory=str(demo_dir / 'chroma_db'),
        embedding_model="sentence-transformers/all-MiniLM-L6-v2"
    )
    
    # Add chunks to store
    added_count = store.add_chunks(chunks)
    print(f"Added {added_count} chunks to vector store")
    
    # Get stats
    stats = store.get_collection_stats()
    print(f"Collection stats: {stats}")
    
    # Test search
    print("\nTesting search functionality...")
    results = store.hybrid_search("artificial intelligence art", n_results=3)
    print(f"Found {len(results)} results for 'artificial intelligence art'")
    
    for i, result in enumerate(results, 1):
        print(f"{i}. {result['metadata']['title']}")
        print(f"   Score: {result.get('combined_score', 0):.3f}")
        print(f"   Content: {result['content'][:100]}...")
        print()
    
    print("Demo dataset creation complete!")
    print(f"Demo data saved to: {demo_dir}")
    print(f"ChromaDB collection: demo_art_tech_knowledge")
    
    return demo_dir


if __name__ == "__main__":
    create_demo_dataset()
