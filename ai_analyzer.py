"""
AI analyzer module for extracting embeddings and categories from images and videos.
"""
import os
import torch
import numpy as np
from PIL import Image
import cv2
from typing import List, Tuple, Optional
import clip
from sentence_transformers import SentenceTransformer

# Try to use GPU if available
device = "cuda" if torch.cuda.is_available() else "cpu"


class MediaAnalyzer:
    """Analyzes media files and generates embeddings for semantic search."""
    
    def __init__(self, model_size="ViT-B/32", num_video_frames=16):
        """
        Initialize the AI models.
        
        Args:
            model_size: CLIP model size - "ViT-B/32" (faster), "ViT-B/16" (better), "ViT-L/14" (best but slow)
            num_video_frames: Number of frames to sample from videos
        """
        print(f"Loading AI models on {device}...")
        
        # Load CLIP model for vision embeddings
        # Options: "ViT-B/32" (fastest, default), "ViT-B/16" (better), "ViT-L/14" (best but slower)
        self.clip_model, self.clip_preprocess = clip.load(model_size, device=device)
        self.clip_model.eval()
        
        # Load sentence transformer for text embeddings
        self.text_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Configuration
        self.num_video_frames = num_video_frames
        self.embedding_dim = self.clip_model.visual.output_dim  # Get actual embedding dimension
        
        print(f"Models loaded successfully! Using {model_size} with {num_video_frames} video frames.")
        print(f"Embedding dimension: {self.embedding_dim}")
    
    def extract_image_embedding(self, image_path: str) -> np.ndarray:
        """
        Extract embedding from an image using CLIP.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Normalized embedding vector
        """
        try:
            image = Image.open(image_path).convert('RGB')
            image_tensor = self.clip_preprocess(image).unsqueeze(0).to(device)
            
            with torch.no_grad():
                image_features = self.clip_model.encode_image(image_tensor)
                # Normalize the embedding
                image_features = image_features / image_features.norm(dim=-1, keepdim=True)
            
            return image_features.cpu().numpy().flatten()
        except Exception as e:
            print(f"Error processing image {image_path}: {e}")
            return np.zeros(self.embedding_dim)  # Return zero vector on error
    
    def extract_video_embedding(self, video_path: str, num_frames: int = None) -> np.ndarray:
        """
        Extract embedding from a video by sampling frames.
        
        Args:
            video_path: Path to the video file
            num_frames: Number of frames to sample (uses default if None)
            
        Returns:
            Average normalized embedding vector
        """
        if num_frames is None:
            num_frames = self.num_video_frames
            
        try:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                return np.zeros(self.embedding_dim)
            
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            if total_frames == 0:
                return np.zeros(self.embedding_dim)
            
            frame_embeddings = []
            
            # Sample frames evenly throughout the video, with more focus on beginning/middle
            # (videos often have most relevant content in first half)
            if num_frames <= total_frames:
                # Use weighted sampling: more frames from beginning
                first_half = int(num_frames * 0.6)
                second_half = num_frames - first_half
                
                indices_first = np.linspace(0, total_frames // 2, first_half, dtype=int)
                indices_second = np.linspace(total_frames // 2, total_frames - 1, second_half, dtype=int)
                frame_indices = np.concatenate([indices_first, indices_second])
            else:
                frame_indices = np.arange(0, total_frames)
            
            for idx in frame_indices:
                cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
                ret, frame = cap.read()
                if ret:
                    # Convert BGR to RGB
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    image = Image.fromarray(frame_rgb)
                    image_tensor = self.clip_preprocess(image).unsqueeze(0).to(device)
                    
                    with torch.no_grad():
                        frame_features = self.clip_model.encode_image(image_tensor)
                        frame_features = frame_features / frame_features.norm(dim=-1, keepdim=True)
                        frame_embeddings.append(frame_features.cpu().numpy())
            
            cap.release()
            
            if frame_embeddings:
                # Average the frame embeddings
                avg_embedding = np.mean(frame_embeddings, axis=0).flatten()
                # Normalize again
                avg_embedding = avg_embedding / np.linalg.norm(avg_embedding)
                return avg_embedding
            else:
                return np.zeros(self.embedding_dim)
                
        except Exception as e:
            print(f"Error processing video {video_path}: {e}")
            return np.zeros(512)
    
    def generate_categories(self, image_path: str, candidate_categories: List[str] = None) -> List[Tuple[str, float]]:
        """
        Generate category predictions for an image.
        
        Args:
            image_path: Path to the image file
            candidate_categories: List of category labels to score
            
        Returns:
            List of (category, score) tuples sorted by score
        """
        if candidate_categories is None:
            candidate_categories = [
                "a person drawing", "a person painting", "a person cooking",
                "a person eating", "a person exercising", "a person working",
                "a person reading", "a person sleeping", "a person talking",
                "outdoor scene", "indoor scene", "nature", "city", "beach",
                "party", "celebration", "family", "friends", "pets", "animals"
            ]
        
        try:
            image = Image.open(image_path).convert('RGB')
            image_tensor = self.clip_preprocess(image).unsqueeze(0).to(device)
            
            # Tokenize categories
            text_tokens = clip.tokenize(candidate_categories).to(device)
            
            with torch.no_grad():
                image_features = self.clip_model.encode_image(image_tensor)
                text_features = self.clip_model.encode_text(text_tokens)
                
                # Normalize
                image_features = image_features / image_features.norm(dim=-1, keepdim=True)
                text_features = text_features / text_features.norm(dim=-1, keepdim=True)
                
                # Compute similarity
                similarity = (100.0 * image_features @ text_features.T).softmax(dim=-1)
            
            # Get top categories
            scores = similarity.cpu().numpy().flatten()
            category_scores = list(zip(candidate_categories, scores))
            category_scores.sort(key=lambda x: x[1], reverse=True)
            
            return category_scores[:5]  # Return top 5
            
        except Exception as e:
            print(f"Error categorizing {image_path}: {e}")
            return []
    
    def encode_text_query(self, query: str, expand_query: bool = True) -> np.ndarray:
        """
        Encode a text query into an embedding for search.
        
        Args:
            query: Natural language search query
            expand_query: Whether to expand query with related terms for better matching
            
        Returns:
            Embedding vector
        """
        # Query expansion for better matching
        if expand_query:
            query = self._expand_query(query)
        
        # Use CLIP's text encoder for better alignment with image embeddings
        try:
            # Try multiple query formulations and average them for better accuracy
            query_variations = [
                query,  # Original
                f"a photo of {query}",  # Photo description
                f"a video of {query}",  # Video description
                f"an image showing {query}",  # Image description
            ]
            
            text_tokens = clip.tokenize(query_variations).to(device)
            with torch.no_grad():
                text_features = self.clip_model.encode_text(text_tokens)
                text_features = text_features / text_features.norm(dim=-1, keepdim=True)
                # Average the query variations for more robust matching
                avg_features = text_features.mean(dim=0, keepdim=True)
                avg_features = avg_features / avg_features.norm(dim=-1, keepdim=True)
            return avg_features.cpu().numpy().flatten()
        except Exception as e:
            print(f"Error encoding query: {e}")
            # Fallback to sentence transformer
            return self.text_model.encode(query)
    
    def _expand_query(self, query: str) -> str:
        """
        Expand query with related terms for better matching.
        
        Args:
            query: Original search query
            
        Returns:
            Expanded query string
        """
        # Simple keyword expansion based on common patterns
        expansions = {
            "drawing": ["drawing", "sketching", "art", "illustration"],
            "cooking": ["cooking", "baking", "preparing food"],
            "eating": ["eating", "dining", "meal", "food"],
            "exercising": ["exercising", "working out", "fitness", "sports"],
            "reading": ["reading", "book", "study"],
            "sleeping": ["sleeping", "rest", "bed"],
            "talking": ["talking", "speaking", "conversation", "chatting"],
            "outdoor": ["outdoor", "outside", "nature", "park", "garden"],
            "indoor": ["indoor", "inside", "home", "room"],
            "dog": ["dog", "puppy", "canine", "pet"],
            "cat": ["cat", "kitten", "feline", "pet"],
        }
        
        query_lower = query.lower()
        expanded_terms = [query]
        
        # Check for keywords and add expansions
        for key, terms in expansions.items():
            if key in query_lower:
                expanded_terms.extend(terms)
                break
        
        # Return original query with context (CLIP works better with natural language)
        return query


