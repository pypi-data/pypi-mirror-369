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
    
    def __init__(self, model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2", device: str = None):
        self.model_name = model_name
        self.device = device
        self._model = None
        
    def _load_model(self):
        """Lazy load model with automatic device detection"""
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                
                # Auto-detect device if not specified
                if self.device is None:
                    try:
                        import torch
                        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
                    except ImportError:
                        self.device = 'cpu'
                
                # Load model with device specification
                self._model = SentenceTransformer(self.model_name, device=self.device)
                
                # Log model loading info
                logger = logging.getLogger(__name__)
                logger.info(f"🤖 Embedding 모델 로드:")
                logger.info(f"   📦 모델: {self.model_name}")
                logger.info(f"   🔧 디바이스: {self.device}")
                
                if self.device == 'cuda':
                    try:
                        import torch
                        memory_allocated = torch.cuda.memory_allocated() / (1024**3)
                        logger.info(f"   💾 GPU 메모리 사용: {memory_allocated:.2f}GB")
                    except:
                        pass
                        
            except ImportError:
                raise ImportError("sentence-transformers library not installed. Using mock backend.")
            except Exception as e:
                raise RuntimeError(f"Failed to load model {self.model_name}: {e}")
    
    def encode(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """Encode texts using SentenceTransformers"""
        self._load_model()
        
        # Process in batches with progress logging
        embeddings = []
        total_batches = (len(texts) + batch_size - 1) // batch_size
        
        for batch_idx, i in enumerate(range(0, len(texts), batch_size), 1):
            batch_texts = texts[i:i + batch_size]
            batch_embeddings = self._model.encode(batch_texts, convert_to_numpy=True)
            embeddings.append(batch_embeddings)
            
            # Log progress every 10 batches or at the end
            if batch_idx % 10 == 0 or batch_idx == total_batches:
                progress = (batch_idx / total_batches) * 100
                logging.getLogger(__name__).info(f"   📈 Progress: {progress:.1f}% ({batch_idx}/{total_batches} batches)")
        
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
        total_batches = (len(texts) + batch_size - 1) // batch_size
        
        for batch_idx, i in enumerate(range(0, len(texts), batch_size), 1):
            batch_texts = texts[i:i + batch_size]
            batch_embeddings = self._encode_batch(batch_texts)
            embeddings.extend(batch_embeddings)
            
            # Log progress every 5 batches or at the end (Ollama is slower)
            if batch_idx % 5 == 0 or batch_idx == total_batches:
                progress = (batch_idx / total_batches) * 100
                logging.getLogger(__name__).info(f"   📈 Progress: {progress:.1f}% ({batch_idx}/{total_batches} batches)")
        
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
        
        # Setup GPU and device configuration
        self.device_info = self._setup_device()
        
        # Update config with optimal batch size if not specified
        if hasattr(self.config, 'batch_size') and self.config.batch_size == 32:  # Default value
            optimal_batch_size = self.device_info.get('recommended_batch_size', 32)
            self.config.batch_size = optimal_batch_size
            self.logger.info(f"🎯 최적화된 배치 크기 설정: {optimal_batch_size}")
        
        self.backend = self._create_backend()
    
    def _setup_device(self) -> Dict[str, Any]:
        """Setup device configuration with GPU optimization"""
        from .utils import setup_device
        return setup_device(self.logger)
    
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
            # Get device from device_info
            device = self.device_info.get('device', 'cpu')
            
            if self.config.embed_model == "bge-m3":
                model_name = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
                self.logger.info(f"Loading embedding model: {model_name} (bge-m3 not available, using fallback)")
                return SentenceTransformerBackend(model_name, device=device)
            elif self.config.embed_model in ["sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"]:
                self.logger.info(f"Loading embedding model: {self.config.embed_model}")
                return SentenceTransformerBackend(self.config.embed_model, device=device)
            else:
                self.logger.info(f"Loading embedding model: {self.config.embed_model}")
                return SentenceTransformerBackend(self.config.embed_model, device=device)
                
        except (ImportError, RuntimeError) as e:
            self.logger.warning(f"Failed to load embedding model: {e}")
            self.logger.info("Using mock embedding backend")
            return MockEmbeddingBackend()
    
    def _estimate_processing_time(self, total_texts: int, backend_type: str) -> str:
        """Estimate processing time based on text count and backend type"""
        
        # Rough estimates based on typical performance (texts per second)
        performance_estimates = {
            'mock': 5000,  # Very fast
            'sentence_transformer': 100,  # Moderate
            'ollama_embedding': 20,  # Slower due to API calls
            'unknown': 50  # Conservative estimate
        }
        
        texts_per_second = performance_estimates.get(backend_type, 50)
        estimated_seconds = total_texts / texts_per_second
        
        if estimated_seconds < 60:
            return f"{estimated_seconds:.1f} seconds"
        elif estimated_seconds < 3600:
            return f"{estimated_seconds/60:.1f} minutes"
        else:
            return f"{estimated_seconds/3600:.1f} hours"
    
    def _format_duration(self, seconds: float) -> str:
        """Format duration in human-readable format"""
        if seconds < 60:
            return f"{seconds:.1f} seconds"
        elif seconds < 3600:
            return f"{seconds/60:.1f} minutes"
        else:
            return f"{seconds/3600:.1f} hours"
    
    def create_embeddings(self, df: pd.DataFrame, window_size: int = None) -> Dict[str, Any]:
        """Create embeddings for messages and sliding windows"""
        
        window_size = window_size or self.config.topic_window_size
        
        if df.empty:
            return {'message_embeddings': np.array([]), 'window_embeddings': np.array([])}
        
        # Calculate estimated processing time
        num_messages = len(df)
        num_windows = max(0, num_messages - window_size + 1)
        total_texts = num_messages + num_windows
        
        # Estimate processing time based on backend type and text count
        backend_type = self.backend.get_model_info().get('type', 'unknown')
        estimated_time = self._estimate_processing_time(total_texts, backend_type)
        
        self.logger.info(f"🚀 Starting embedding generation:")
        self.logger.info(f"   📊 Messages to process: {num_messages:,}")
        self.logger.info(f"   🪟 Windows to create: {num_windows:,}")
        self.logger.info(f"   📝 Total texts to embed: {total_texts:,}")
        self.logger.info(f"   ⏱️  Estimated time: {estimated_time}")
        self.logger.info(f"   🤖 Backend: {backend_type}")
        self.logger.info(f"   📦 Batch size: {self.config.batch_size}")
        self.logger.info(f"   🪟 Window size: {window_size}")
        
        import time
        start_time = time.time()
        
        # Message-level embeddings
        self.logger.info("🔤 Processing message embeddings...")
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
        
        # Window-level embeddings
        if windows:
            self.logger.info("🪟 Processing window embeddings...")
            window_embeddings = self.backend.encode(windows, batch_size=self.config.batch_size)
        else:
            window_embeddings = np.array([])
        
        # Calculate actual processing time
        end_time = time.time()
        actual_duration = end_time - start_time
        
        model_info = self.backend.get_model_info()
        
        # Log completion summary
        self.logger.info(f"✅ Embedding generation completed!")
        self.logger.info(f"   ⏰ Actual time: {self._format_duration(actual_duration)}")
        self.logger.info(f"   🎯 Processing rate: {total_texts/actual_duration:.1f} texts/second")
        self.logger.info(f"   📊 Generated {len(message_embeddings):,} message embeddings")
        self.logger.info(f"   🪟 Generated {len(window_embeddings):,} window embeddings")
        
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