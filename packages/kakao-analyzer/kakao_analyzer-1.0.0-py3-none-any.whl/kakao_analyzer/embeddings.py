"""Embedding models and vector operations"""

import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple
from abc import ABC, abstractmethod
import logging
from sklearn.metrics.pairwise import cosine_similarity
import json
import pickle
from pathlib import Path
import requests


class EmbeddingBackend(ABC):
    """Abstract base class for embedding backends"""
    
    @abstractmethod
    def encode(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """Encode texts to embeddings"""
        pass
    
    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information"""
        pass


class MockEmbeddingBackend(EmbeddingBackend):
    """Mock embedding backend for testing and fallback"""
    
    def __init__(self, dimension: int = 768):
        self.dimension = dimension
        self.model_name = "mock-embedding"
    
    def encode(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """Generate mock embeddings based on text hash and length"""
        embeddings = []
        
        for text in texts:
            # Create deterministic but varied embedding based on text
            text_hash = hash(text) % (2**32)
            text_length = len(text)
            
            # Create base embedding
            np.random.seed(text_hash % (2**31))
            base_embedding = np.random.normal(0, 1, self.dimension)
            
            # Modify based on text characteristics
            length_factor = min(text_length / 100, 1.0)
            base_embedding *= length_factor
            
            # Add some structure based on common Korean patterns
            if '?' in text:
                base_embedding[:10] += 0.5
            if any(char in text for char in ['ㅋ', 'ㅎ', '!!']):
                base_embedding[10:20] += 0.3
            if any(word in text for word in ['안녕', '감사', '미안']):
                base_embedding[20:30] += 0.4
            
            # Normalize
            base_embedding = base_embedding / np.linalg.norm(base_embedding)
            embeddings.append(base_embedding)
        
        return np.array(embeddings)
    
    def get_model_info(self) -> Dict[str, Any]:
        return {
            'model_name': self.model_name,
            'dimension': self.dimension,
            'type': 'mock'
        }


class SentenceTransformerBackend(EmbeddingBackend):
    """SentenceTransformers-based embedding backend"""
    
    def __init__(self, model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"):
        self.model_name = model_name
        self._model = None
        
    def _load_model(self):
        """Lazy load model"""
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                self._model = SentenceTransformer(self.model_name)
            except ImportError:
                raise ImportError("sentence-transformers library not installed. Using mock backend.")
            except Exception as e:
                raise RuntimeError(f"Failed to load model {self.model_name}: {e}")
    
    def encode(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """Encode texts using SentenceTransformers"""
        self._load_model()
        
        # Process in batches
        embeddings = []
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i + batch_size]
            batch_embeddings = self._model.encode(batch_texts, convert_to_numpy=True)
            embeddings.append(batch_embeddings)
        
        return np.vstack(embeddings) if embeddings else np.array([])
    
    def get_model_info(self) -> Dict[str, Any]:
        self._load_model()
        return {
            'model_name': self.model_name,
            'dimension': self._model.get_sentence_embedding_dimension(),
            'type': 'sentence_transformer'
        }


class OllamaEmbeddingBackend(EmbeddingBackend):
    """Ollama-based embedding backend"""
    
    def __init__(self, model_name: str = "bge-m3:latest", base_url: str = "http://localhost:11434"):
        self.model_name = model_name
        self.base_url = base_url
        
    def encode(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """Encode texts using Ollama embeddings API"""
        embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i + batch_size]
            batch_embeddings = self._encode_batch(batch_texts)
            embeddings.extend(batch_embeddings)
        
        return np.array(embeddings)
    
    def _encode_batch(self, texts: List[str]) -> List[np.ndarray]:
        """Encode a batch of texts"""
        embeddings = []
        
        for text in texts:
            try:
                response = requests.post(
                    f"{self.base_url}/api/embed",
                    json={
                        "model": self.model_name,
                        "input": text
                    },
                    timeout=30
                )
                response.raise_for_status()
                result = response.json()
                embedding = np.array(result.get("embeddings", [])).flatten()
                embeddings.append(embedding)
            except Exception as e:
                # Fallback to zero vector if embedding fails
                logging.warning(f"Failed to get embedding for text, using fallback: {e}")
                embeddings.append(np.zeros(1024))  # Default dimension
        
        return embeddings
    
    def get_model_info(self) -> Dict[str, Any]:
        try:
            # Test with a simple text to get dimension
            test_embedding = self._encode_batch(["test"])[0]
            dimension = len(test_embedding)
        except:
            dimension = 1024  # Default fallback
        
        return {
            'model_name': self.model_name,
            'dimension': dimension,
            'type': 'ollama_embedding',
            'base_url': self.base_url
        }


class EmbeddingManager:
    """Manage embeddings for conversation analysis"""
    
    def __init__(self, config, logger: logging.Logger = None):
        self.config = config
        self.logger = logger or logging.getLogger(__name__)
        self.backend = self._create_backend()
    
    def _create_backend(self) -> EmbeddingBackend:
        """Create appropriate embedding backend"""
        
        # Check for Ollama integration first
        if hasattr(self.config, 'use_ollama') and self.config.use_ollama:
            try:
                ollama_model = "bge-m3:latest" if self.config.embed_model == "bge-m3" else self.config.embed_model
                self.logger.info(f"Using Ollama embedding model: {ollama_model}")
                return OllamaEmbeddingBackend(ollama_model)
            except Exception as e:
                self.logger.warning(f"Failed to load Ollama backend: {e}")
                self.logger.info("Falling back to sentence transformers")
        
        # Try to load specified model with sentence transformers
        try:
            if self.config.embed_model == "bge-m3":
                model_name = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
                self.logger.info(f"Loading embedding model: {model_name} (bge-m3 not available, using fallback)")
                return SentenceTransformerBackend(model_name)
            elif self.config.embed_model in ["sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"]:
                self.logger.info(f"Loading embedding model: {self.config.embed_model}")
                return SentenceTransformerBackend(self.config.embed_model)
            else:
                self.logger.info(f"Loading embedding model: {self.config.embed_model}")
                return SentenceTransformerBackend(self.config.embed_model)
                
        except (ImportError, RuntimeError) as e:
            self.logger.warning(f"Failed to load embedding model: {e}")
            self.logger.info("Using mock embedding backend")
            return MockEmbeddingBackend()
    
    def create_embeddings(self, df: pd.DataFrame, window_size: int = None) -> Dict[str, Any]:
        """Create embeddings for messages and sliding windows"""
        
        window_size = window_size or self.config.topic_window_size
        self.logger.info(f"Creating embeddings (window_size: {window_size})")
        
        if df.empty:
            return {'message_embeddings': np.array([]), 'window_embeddings': np.array([])}
        
        # Message-level embeddings
        messages = df['message'].tolist()
        message_embeddings = self.backend.encode(messages, batch_size=self.config.batch_size)
        
        # Window-level embeddings (sliding window)
        windows = []
        window_info = []
        
        for i in range(len(df) - window_size + 1):
            window_messages = df.iloc[i:i+window_size]['message'].tolist()
            window_text = ' '.join(window_messages)
            windows.append(window_text)
            
            window_info.append({
                'window_id': i,
                'start_idx': i,
                'end_idx': i + window_size - 1,
                'start_time': df.iloc[i]['datetime'],
                'end_time': df.iloc[i + window_size - 1]['datetime'],
                'participants': df.iloc[i:i+window_size]['user'].unique().tolist()
            })
        
        window_embeddings = self.backend.encode(windows, batch_size=self.config.batch_size) if windows else np.array([])
        
        model_info = self.backend.get_model_info()
        
        return {
            'message_embeddings': message_embeddings,
            'window_embeddings': window_embeddings,
            'window_info': window_info,
            'model_info': model_info,
            'window_size': window_size
        }
    
    def save_embeddings(self, embeddings_data: Dict[str, Any], output_path: Path) -> None:
        """Save embeddings to file"""
        
        # Save embeddings as parquet for efficient storage
        embeddings_df = pd.DataFrame({
            'embedding_id': range(len(embeddings_data['message_embeddings'])),
            'embedding': embeddings_data['message_embeddings'].tolist()
        })
        embeddings_df.to_parquet(output_path / 'embeddings.parquet')
        
        # Save window embeddings
        if len(embeddings_data['window_embeddings']) > 0:
            window_embeddings_df = pd.DataFrame({
                'window_id': range(len(embeddings_data['window_embeddings'])),
                'embedding': embeddings_data['window_embeddings'].tolist()
            })
            
            # Add window info
            window_info_df = pd.DataFrame(embeddings_data['window_info'])
            window_embeddings_df = pd.concat([window_embeddings_df, window_info_df], axis=1)
            
            window_embeddings_df.to_parquet(output_path / 'window_embeddings.parquet')
        
        # Save metadata
        metadata = {
            'model_info': embeddings_data['model_info'],
            'window_size': embeddings_data['window_size'],
            'message_count': len(embeddings_data['message_embeddings']),
            'window_count': len(embeddings_data['window_embeddings'])
        }
        
        with open(output_path / 'embeddings_metadata.json', 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2, default=str)
        
        self.logger.info(f"Saved embeddings to {output_path}")
    
    def load_embeddings(self, input_path: Path) -> Dict[str, Any]:
        """Load embeddings from file"""
        
        embeddings_df = pd.read_parquet(input_path / 'embeddings.parquet')
        message_embeddings = np.array(embeddings_df['embedding'].tolist())
        
        # Load window embeddings if they exist
        window_embeddings_path = input_path / 'window_embeddings.parquet'
        if window_embeddings_path.exists():
            window_embeddings_df = pd.read_parquet(window_embeddings_path)
            window_embeddings = np.array(window_embeddings_df['embedding'].tolist())
            window_info = window_embeddings_df[['window_id', 'start_idx', 'end_idx', 'start_time', 'end_time', 'participants']].to_dict('records')
        else:
            window_embeddings = np.array([])
            window_info = []
        
        # Load metadata
        with open(input_path / 'embeddings_metadata.json', 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        return {
            'message_embeddings': message_embeddings,
            'window_embeddings': window_embeddings,
            'window_info': window_info,
            **metadata
        }


def calculate_similarity_matrix(embeddings: np.ndarray) -> np.ndarray:
    """Calculate cosine similarity matrix"""
    if len(embeddings) == 0:
        return np.array([])
    return cosine_similarity(embeddings)


def detect_similarity_changes(similarity_scores: List[float], threshold: float = 0.3) -> List[int]:
    """Detect significant changes in similarity scores"""
    
    if len(similarity_scores) < 2:
        return []
    
    changes = []
    for i in range(1, len(similarity_scores)):
        similarity_drop = similarity_scores[i-1] - similarity_scores[i]
        
        if similarity_drop > threshold:
            changes.append(i)
    
    return changes


def calculate_embedding_statistics(embeddings: np.ndarray) -> Dict[str, Any]:
    """Calculate statistics about embeddings"""
    
    if len(embeddings) == 0:
        return {'error': 'No embeddings provided'}
    
    # Pairwise similarities
    sim_matrix = cosine_similarity(embeddings)
    
    # Remove diagonal (self-similarity)
    similarities = []
    n = len(embeddings)
    for i in range(n):
        for j in range(i+1, n):
            similarities.append(sim_matrix[i, j])
    
    similarities = np.array(similarities)
    
    return {
        'dimension': embeddings.shape[1],
        'count': len(embeddings),
        'similarity_stats': {
            'mean': float(np.mean(similarities)),
            'std': float(np.std(similarities)),
            'min': float(np.min(similarities)),
            'max': float(np.max(similarities)),
            'median': float(np.median(similarities))
        },
        'embedding_norms': {
            'mean': float(np.mean(np.linalg.norm(embeddings, axis=1))),
            'std': float(np.std(np.linalg.norm(embeddings, axis=1)))
        }
    }