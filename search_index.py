"""
Search index module for storing and searching media embeddings.
"""
import os
import json
import pickle
import numpy as np
import faiss
from pathlib import Path
from typing import List, Dict, Tuple
from datetime import datetime


class MediaSearchIndex:
    """Manages the vector index for semantic media search."""
    
    def __init__(self, index_path: str = "./data/index"):
        """
        Initialize the search index.
        
        Args:
            index_path: Base path for storing index files
        """
        self.index_path = index_path
        self.embeddings_file = os.path.join(index_path, "embeddings.npy")
        self.metadata_file = os.path.join(index_path, "metadata.json")
        self.faiss_index_file = os.path.join(index_path, "faiss.index")
        
        os.makedirs(index_path, exist_ok=True)
        
        # Initialize index
        # Note: Dimension will be set when first embedding is added
        # Default is 512 for ViT-B/32, but can be 768 for ViT-B/16 or ViT-L/14
        self.dimension = None
        self.faiss_index = None
        self.embeddings = None
        self.metadata = []
        
        self._load_index()
    
    def _load_index(self):
        """Load existing index if available."""
        if os.path.exists(self.faiss_index_file) and os.path.exists(self.metadata_file):
            try:
                # Load FAISS index
                self.faiss_index = faiss.read_index(self.faiss_index_file)
                self.dimension = self.faiss_index.d
                
                # Load metadata
                with open(self.metadata_file, 'r') as f:
                    self.metadata = json.load(f)
                
                print(f"Loaded index with {len(self.metadata)} entries (dimension: {self.dimension})")
            except Exception as e:
                print(f"Error loading index: {e}. Creating new index.")
                self._create_new_index()
        else:
            self._create_new_index()
    
    def _create_new_index(self, dimension=None):
        """Create a new FAISS index."""
        if dimension is None:
            dimension = self.dimension if self.dimension else 512  # Default to 512
        # Use L2 distance (Euclidean) for normalized embeddings
        self.faiss_index = faiss.IndexFlatL2(dimension)
        self.dimension = dimension
        self.metadata = []
    
    def add_media(self, file_path: str, embedding: np.ndarray, file_type: str = "image"):
        """
        Add a media file to the index.
        
        Args:
            file_path: Path to the media file
            embedding: Embedding vector
            file_type: Type of media ("image" or "video")
        """
        if embedding is None or embedding.size == 0:
            print(f"Skipping {file_path}: invalid embedding")
            return
        
        # Ensure embedding is the right shape
        if embedding.ndim > 1:
            embedding = embedding.flatten()
        
        embedding_dim = embedding.shape[0]
        
        # Initialize dimension on first add if not set
        if self.dimension is None:
            self.dimension = embedding_dim
            if self.faiss_index is None:
                self._create_new_index(embedding_dim)
        
        if embedding_dim != self.dimension:
            print(f"Skipping {file_path}: embedding dimension mismatch ({embedding_dim} != {self.dimension})")
            return
        
        # Add to FAISS index
        embedding_float32 = embedding.astype('float32').reshape(1, -1)
        self.faiss_index.add(embedding_float32)
        
        # Store metadata
        metadata_entry = {
            "file_path": file_path,
            "file_type": file_type,
            "index": len(self.metadata),
            "added_at": datetime.now().isoformat()
        }
        self.metadata.append(metadata_entry)
    
    def search(self, query_embedding: np.ndarray, k: int = 10) -> List[Dict]:
        """
        Search for similar media files.
        
        Args:
            query_embedding: Query embedding vector
            k: Number of results to return
            
        Returns:
            List of metadata dictionaries for matching files
        """
        if self.faiss_index.ntotal == 0:
            return []
        
        # Ensure embedding is the right shape
        if query_embedding.ndim > 1:
            query_embedding = query_embedding.flatten()
        
        if query_embedding.shape[0] != self.dimension:
            print(f"Query embedding dimension mismatch: {query_embedding.shape[0]} != {self.dimension}")
            return []
        
        # Search - use cosine similarity for normalized embeddings (more accurate)
        query_float32 = query_embedding.astype('float32').reshape(1, -1)
        
        # For normalized embeddings, cosine similarity = 1 - (L2 distance^2 / 2)
        # But FAISS IndexFlatL2 returns squared L2 distance, so we convert properly
        distances, indices = self.faiss_index.search(query_float32, min(k * 2, self.faiss_index.ntotal))
        
        # Build results with better similarity calculation
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.metadata):
                result = self.metadata[idx].copy()
                # For normalized embeddings, distance^2 = 2(1 - cosine_similarity)
                # So cosine_similarity = 1 - (distance^2 / 2)
                squared_distance = float(distances[0][i])
                cosine_similarity = max(0.0, 1.0 - (squared_distance / 2.0))
                result['distance'] = squared_distance
                result['similarity'] = cosine_similarity
                results.append(result)
        
        # Sort by similarity (descending) and filter low-confidence results
        results.sort(key=lambda x: x['similarity'], reverse=True)
        
        # Filter results below similarity threshold (0.3 = 30% similarity)
        min_similarity = 0.3
        filtered_results = [r for r in results if r['similarity'] >= min_similarity]
        
        # Return top k results
        return filtered_results[:k]
    
    def save(self):
        """Save the index to disk."""
        try:
            # Save FAISS index
            faiss.write_index(self.faiss_index, self.faiss_index_file)
            
            # Save metadata
            with open(self.metadata_file, 'w') as f:
                json.dump(self.metadata, f, indent=2)
            
            print(f"Index saved with {len(self.metadata)} entries")
        except Exception as e:
            print(f"Error saving index: {e}")
    
    def get_stats(self) -> Dict:
        """Get statistics about the index."""
        return {
            "total_entries": len(self.metadata),
            "images": sum(1 for m in self.metadata if m.get("file_type") == "image"),
            "videos": sum(1 for m in self.metadata if m.get("file_type") == "video"),
            "dimension": self.dimension
        }


