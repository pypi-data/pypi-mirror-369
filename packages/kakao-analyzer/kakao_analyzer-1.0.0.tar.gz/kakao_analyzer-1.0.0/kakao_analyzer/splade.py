"""SPLADE sparse retrieval backend"""

import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple
from abc import ABC, abstractmethod
import logging
from collections import defaultdict
import json
from pathlib import Path


class SparseBackend(ABC):
    """Abstract base class for sparse retrieval backends"""
    
    @abstractmethod
    def encode_sparse(self, texts: List[str], batch_size: int = 32) -> Tuple[List[Dict[str, float]], Dict[str, Any]]:
        """Encode texts to sparse representations"""
        pass
    
    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information"""
        pass


class MockSparseBackend(SparseBackend):
    """Mock SPLADE backend for testing and fallback"""
    
    def __init__(self, vocab_size: int = 10000):
        self.vocab_size = vocab_size
        self.model_name = "mock-splade"
        self.vocabulary = self._create_mock_vocabulary()
    
    def _create_mock_vocabulary(self) -> Dict[str, int]:
        """Create mock vocabulary based on common Korean words"""
        
        # Common Korean words and patterns
        common_words = [
            '안녕', '감사', '미안', '죄송', '네', '아니', '맞다', '틀렸다',
            '좋다', '나쁘다', '크다', '작다', '많다', '적다', '빠르다', '느리다',
            '사람', '시간', '장소', '일', '것', '때', '곳', '말', '생각', '마음',
            'ㅋㅋ', 'ㅎㅎ', 'ㅠㅠ', 'ㅜㅜ', 'ㄱㄱ', 'ㅇㅋ', 'ㄴㄴ',
            '진짜', '정말', '완전', '아예', '되게', '엄청', '진심', '대박',
            '먹다', '마시다', '가다', '오다', '보다', '듣다', '말하다', '하다'
        ]
        
        vocabulary = {}
        for i, word in enumerate(common_words):
            vocabulary[word] = i
        
        # Add more synthetic tokens
        for i in range(len(common_words), self.vocab_size):
            vocabulary[f"token_{i}"] = i
        
        return vocabulary
    
    def encode_sparse(self, texts: List[str], batch_size: int = 32) -> Tuple[List[Dict[str, float]], Dict[str, Any]]:
        """Generate mock sparse encodings"""
        
        sparse_vectors = []
        
        for text in texts:
            sparse_vector = {}
            
            # Simple token matching with TF-IDF like scoring
            words = text.split()
            word_counts = defaultdict(int)
            
            for word in words:
                if word in self.vocabulary:
                    word_counts[word] += 1
            
            # Convert to sparse representation with mock scores
            for word, count in word_counts.items():
                if word in self.vocabulary:
                    # Mock SPLADE-like score (higher for repeated terms, with some randomness)
                    base_score = np.log(1 + count)
                    vocab_id = self.vocabulary[word]
                    # Add position-based and hash-based variation
                    position_factor = 1.0 + (vocab_id % 100) / 1000
                    hash_factor = 1.0 + (hash(text) % 100) / 1000
                    
                    score = base_score * position_factor * hash_factor
                    sparse_vector[word] = round(score, 4)
            
            # Add some random activations for common patterns
            text_hash = hash(text)
            if '?' in text:
                sparse_vector['[QUESTION]'] = 0.8 + (text_hash % 100) / 500
            if any(char in text for char in ['!', 'ㅋ', 'ㅎ']):
                sparse_vector['[EMOTION]'] = 0.6 + (text_hash % 100) / 500
            
            sparse_vectors.append(sparse_vector)
        
        # Statistics
        stats = {
            'avg_active_tokens': np.mean([len(sv) for sv in sparse_vectors]),
            'max_active_tokens': max([len(sv) for sv in sparse_vectors]) if sparse_vectors else 0,
            'total_unique_tokens': len(set().union(*[sv.keys() for sv in sparse_vectors]))
        }
        
        return sparse_vectors, stats
    
    def get_model_info(self) -> Dict[str, Any]:
        return {
            'model_name': self.model_name,
            'vocab_size': self.vocab_size,
            'type': 'mock_sparse'
        }


class SPLADEBackend(SparseBackend):
    """Real SPLADE backend using transformers"""
    
    def __init__(self, model_name: str = "naver/splade-cocondenser-ensembledistil"):
        self.model_name = model_name
        self._model = None
        self._tokenizer = None
        self.device = "cpu"  # Use CPU for better memory management
    
    def _load_model(self):
        """Lazy load SPLADE model"""
        if self._model is None:
            try:
                from transformers import AutoModelForMaskedLM, AutoTokenizer
                import torch
                
                self._tokenizer = AutoTokenizer.from_pretrained(self.model_name)
                self._model = AutoModelForMaskedLM.from_pretrained(self.model_name)
                self._model.eval()
                self._model.to(self.device)
                
                print(f"✅ Loaded SPLADE model: {self.model_name}")
                
            except ImportError as e:
                raise ImportError(f"transformers library not available: {e}")
            except Exception as e:
                raise RuntimeError(f"Failed to load SPLADE model: {e}")
    
    def encode_sparse(self, texts: List[str], batch_size: int = 8) -> Tuple[List[Dict[str, float]], Dict[str, Any]]:
        """Encode texts using SPLADE model"""
        self._load_model()
        
        import torch
        
        sparse_vectors = []
        
        # Process in smaller batches for memory efficiency
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i + batch_size]
            
            # Tokenize batch
            inputs = self._tokenizer(
                batch_texts, 
                padding=True, 
                truncation=True, 
                max_length=256,  # Reduce max length for efficiency
                return_tensors="pt"
            ).to(self.device)
            
            with torch.no_grad():
                # Get model outputs
                outputs = self._model(**inputs)
                logits = outputs.logits
                
                # Apply log(1 + relu) activation (SPLADE-style)
                sparse_repr = torch.log(1 + torch.relu(logits))
                
                # Process each text in batch
                for j, text in enumerate(batch_texts):
                    # Get non-zero activations
                    text_repr = sparse_repr[j]
                    input_ids = inputs['input_ids'][j]
                    
                    sparse_vector = {}
                    
                    # Extract significant activations
                    for token_idx, activation in enumerate(text_repr):
                        max_activation = activation.max().item()
                        if max_activation > 0.1:  # Threshold for significance
                            token_id = input_ids[token_idx].item()
                            token = self._tokenizer.decode([token_id])
                            
                            # Skip special tokens
                            if token not in ['[CLS]', '[SEP]', '[PAD]', '<s>', '</s>']:
                                sparse_vector[token] = round(max_activation, 4)
                    
                    sparse_vectors.append(sparse_vector)
        
        # Calculate statistics
        stats = {
            'avg_active_tokens': np.mean([len(sv) for sv in sparse_vectors]),
            'max_active_tokens': max([len(sv) for sv in sparse_vectors]) if sparse_vectors else 0,
            'total_unique_tokens': len(set().union(*[sv.keys() for sv in sparse_vectors])),
            'batch_size_used': batch_size
        }
        
        return sparse_vectors, stats
    
    def get_model_info(self) -> Dict[str, Any]:
        return {
            'model_name': self.model_name,
            'type': 'splade_real',
            'device': self.device
        }


class HybridRetriever:
    """Hybrid dense + sparse retrieval system"""
    
    def __init__(self, config, logger: logging.Logger = None):
        self.config = config
        self.logger = logger or logging.getLogger(__name__)
        self.dense_weight = 0.7  # Default weighting
        self.sparse_weight = 0.3
        
        if config.use_splade:
            self.sparse_backend = self._create_sparse_backend()
        else:
            self.sparse_backend = None
    
    def _create_sparse_backend(self) -> SparseBackend:
        """Create sparse backend"""
        try:
            self.logger.info("Loading real SPLADE backend...")
            return SPLADEBackend()
        except (ImportError, RuntimeError) as e:
            self.logger.warning(f"Failed to load real SPLADE backend: {e}")
            self.logger.info("Falling back to mock sparse backend")
            return MockSparseBackend()
    
    def create_sparse_index(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Create sparse index for messages"""
        
        if not self.sparse_backend:
            return {'error': 'SPLADE not enabled'}
        
        self.logger.info("Creating sparse index...")
        
        messages = df['message'].tolist()
        sparse_vectors, stats = self.sparse_backend.encode_sparse(
            messages, 
            batch_size=self.config.batch_size
        )
        
        # Create inverted index for efficient retrieval
        inverted_index = defaultdict(list)
        
        for doc_id, sparse_vector in enumerate(sparse_vectors):
            for token, score in sparse_vector.items():
                inverted_index[token].append({
                    'doc_id': doc_id,
                    'score': score
                })
        
        # Sort by score for each token
        for token in inverted_index:
            inverted_index[token].sort(key=lambda x: x['score'], reverse=True)
        
        model_info = self.sparse_backend.get_model_info()
        
        return {
            'sparse_vectors': sparse_vectors,
            'inverted_index': dict(inverted_index),
            'statistics': stats,
            'model_info': model_info,
            'document_count': len(messages)
        }
    
    def hybrid_search(self, query: str, dense_embeddings: np.ndarray, 
                     sparse_index: Dict[str, Any], query_embedding: np.ndarray,
                     top_k: int = 10) -> List[Dict[str, Any]]:
        """Perform hybrid search using both dense and sparse signals"""
        
        if not self.sparse_backend:
            return self._dense_only_search(query_embedding, dense_embeddings, top_k)
        
        # Get sparse representation of query
        query_sparse, _ = self.sparse_backend.encode_sparse([query])
        query_sparse_vector = query_sparse[0] if query_sparse else {}
        
        # Calculate dense similarities
        dense_similarities = np.dot(dense_embeddings, query_embedding.T).flatten()
        
        # Calculate sparse similarities
        sparse_similarities = np.zeros(len(dense_embeddings))
        
        for token, query_score in query_sparse_vector.items():
            if token in sparse_index['inverted_index']:
                for doc_entry in sparse_index['inverted_index'][token]:
                    doc_id = doc_entry['doc_id']
                    doc_score = doc_entry['score']
                    sparse_similarities[doc_id] += query_score * doc_score
        
        # Normalize similarities
        if dense_similarities.max() > 0:
            dense_similarities = dense_similarities / dense_similarities.max()
        if sparse_similarities.max() > 0:
            sparse_similarities = sparse_similarities / sparse_similarities.max()
        
        # Combine similarities
        hybrid_similarities = (self.dense_weight * dense_similarities + 
                             self.sparse_weight * sparse_similarities)
        
        # Get top results
        top_indices = np.argsort(hybrid_similarities)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            results.append({
                'doc_id': int(idx),
                'dense_score': float(dense_similarities[idx]),
                'sparse_score': float(sparse_similarities[idx]),
                'hybrid_score': float(hybrid_similarities[idx])
            })
        
        return results
    
    def _dense_only_search(self, query_embedding: np.ndarray, 
                          dense_embeddings: np.ndarray, top_k: int) -> List[Dict[str, Any]]:
        """Fallback to dense-only search"""
        
        similarities = np.dot(dense_embeddings, query_embedding.T).flatten()
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            results.append({
                'doc_id': int(idx),
                'dense_score': float(similarities[idx]),
                'sparse_score': 0.0,
                'hybrid_score': float(similarities[idx])
            })
        
        return results
    
    def save_sparse_index(self, sparse_index: Dict[str, Any], output_path: Path) -> None:
        """Save sparse index to file"""
        
        # Save sparse vectors as parquet
        if sparse_index.get('sparse_vectors'):
            sparse_df = pd.DataFrame({
                'doc_id': range(len(sparse_index['sparse_vectors'])),
                'sparse_vector': sparse_index['sparse_vectors']
            })
            sparse_df.to_parquet(output_path / 'splade_scores.parquet')
        
        # Save inverted index and metadata
        metadata = {
            'inverted_index': sparse_index.get('inverted_index', {}),
            'statistics': sparse_index.get('statistics', {}),
            'model_info': sparse_index.get('model_info', {}),
            'document_count': sparse_index.get('document_count', 0),
            'creation_time': pd.Timestamp.now().isoformat()
        }
        
        with open(output_path / 'hybrid_index.meta.json', 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2, default=str)
        
        self.logger.info(f"Saved sparse index to {output_path}")
    
    def generate_sample_queries(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Generate sample retrieval queries for demonstration"""
        
        sample_queries = [
            {
                'query': '여행 이야기',
                'description': '여행 관련 대화를 찾습니다',
                'expected_keywords': ['여행', '가다', '여기', '거기', '사진']
            },
            {
                'query': '게임 얘기',
                'description': '게임 관련 대화를 찾습니다',
                'expected_keywords': ['게임', '플레이', '레벨', '스킬', '승리']
            },
            {
                'query': '음식 먹는 이야기',
                'description': '음식 관련 대화를 찾습니다',
                'expected_keywords': ['먹다', '맛있다', '음식', '요리', '배고프다']
            },
            {
                'query': '재미있는 얘기 뭐 없어?',
                'description': '재미있는 대화나 농담을 찾습니다',
                'expected_keywords': ['재미있다', 'ㅋㅋ', '웃기다', '농담', '장난']
            },
            {
                'query': '약속 잡는 이야기',
                'description': '약속이나 만남에 관한 대화를 찾습니다',
                'expected_keywords': ['약속', '만나다', '시간', '장소', '언제']
            }
        ]
        
        return sample_queries