"""Dataset optimization and intelligent chunking for large-scale analysis"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
import logging
from pathlib import Path
from datetime import datetime
import json


class DatasetOptimizer:
    """Optimize dataset processing for large-scale analysis"""
    
    def __init__(self, config, logger: Optional[logging.Logger] = None):
        self.config = config
        self.logger = logger or logging.getLogger(__name__)
        
        # Optimization thresholds
        self.LARGE_DATASET_THRESHOLD = 5000  # Messages
        self.VERY_LARGE_DATASET_THRESHOLD = 20000  # Messages
        self.EMBEDDING_BATCH_SIZE_LARGE = 16  # Smaller batches for large datasets
        self.SPLADE_BATCH_SIZE_LARGE = 4   # Very small batches for SPLADE
        
    def analyze_dataset_size(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze dataset characteristics and suggest optimizations"""
        
        total_messages = len(df)
        unique_users = df['user'].nunique()
        date_span = (df['datetime'].max() - df['datetime'].min()).days
        avg_message_length = df['message'].str.len().mean()
        
        # Estimate computational complexity
        embedding_complexity = self._estimate_embedding_complexity(total_messages, avg_message_length)
        splade_complexity = self._estimate_splade_complexity(total_messages, avg_message_length)
        
        # Suggest optimizations
        optimization_strategy = self._suggest_optimization_strategy(
            total_messages, unique_users, embedding_complexity, splade_complexity
        )
        
        return {
            'total_messages': total_messages,
            'unique_users': unique_users,
            'date_span_days': date_span,
            'avg_message_length': avg_message_length,
            'dataset_category': self._categorize_dataset_size(total_messages),
            'embedding_complexity': embedding_complexity,
            'splade_complexity': splade_complexity,
            'optimization_strategy': optimization_strategy,
            'recommended_subset_size': self._recommend_subset_size(total_messages),
            'estimated_processing_time': self._estimate_processing_time(total_messages, embedding_complexity)
        }
    
    def create_intelligent_subset(self, df: pd.DataFrame, subset_size: int, strategy: str = "balanced") -> pd.DataFrame:
        """Create an intelligent subset that maintains dataset characteristics"""
        
        if len(df) <= subset_size:
            return df
        
        self.logger.info(f"Creating intelligent subset of {subset_size} messages from {len(df)} total")
        
        if strategy == "balanced":
            return self._create_balanced_subset(df, subset_size)
        elif strategy == "temporal":
            return self._create_temporal_subset(df, subset_size)
        elif strategy == "diverse":
            return self._create_diverse_subset(df, subset_size)
        elif strategy == "random":
            return df.sample(n=subset_size, random_state=42)
        else:
            return self._create_balanced_subset(df, subset_size)
    
    def optimize_processing_config(self, df: pd.DataFrame, analysis_config: Dict) -> Dict[str, Any]:
        """Optimize processing configuration based on dataset size"""
        
        total_messages = len(df)
        optimized_config = analysis_config.copy()
        
        if total_messages > self.VERY_LARGE_DATASET_THRESHOLD:
            # Very large dataset optimizations
            optimized_config.update({
                'embedding_batch_size': self.EMBEDDING_BATCH_SIZE_LARGE // 2,
                'splade_batch_size': self.SPLADE_BATCH_SIZE_LARGE // 2,
                'topic_window_size': min(10, analysis_config.get('topic_window_size', 15)),
                'max_workers': min(2, analysis_config.get('max_workers', 4)),
                'chunk_processing': True,
                'memory_efficient_mode': True
            })
        elif total_messages > self.LARGE_DATASET_THRESHOLD:
            # Large dataset optimizations
            optimized_config.update({
                'embedding_batch_size': self.EMBEDDING_BATCH_SIZE_LARGE,
                'splade_batch_size': self.SPLADE_BATCH_SIZE_LARGE,
                'topic_window_size': min(12, analysis_config.get('topic_window_size', 15)),
                'max_workers': min(3, analysis_config.get('max_workers', 4)),
                'chunk_processing': True
            })
        else:
            # Standard dataset
            optimized_config.update({
                'embedding_batch_size': analysis_config.get('batch_size', 32),
                'splade_batch_size': 8,
                'chunk_processing': False
            })
        
        return optimized_config
    
    def create_processing_chunks(self, df: pd.DataFrame, chunk_size: int = None) -> List[pd.DataFrame]:
        """Create processing chunks for memory-efficient analysis"""
        
        if chunk_size is None:
            chunk_size = min(2000, max(500, len(df) // 4))  # Adaptive chunk size
        
        chunks = []
        for i in range(0, len(df), chunk_size):
            chunk = df.iloc[i:i + chunk_size].copy()
            chunks.append(chunk)
        
        self.logger.info(f"Created {len(chunks)} processing chunks of ~{chunk_size} messages each")
        return chunks
    
    def estimate_memory_usage(self, df: pd.DataFrame, include_embeddings: bool = True, include_splade: bool = True) -> Dict[str, float]:
        """Estimate memory usage for different analysis components"""
        
        total_messages = len(df)
        
        # Base data memory (MB)
        base_memory = df.memory_usage(deep=True).sum() / 1024 / 1024
        
        # Embedding memory estimation (768-dim embeddings)
        embedding_memory = 0
        if include_embeddings:
            embedding_memory = (total_messages * 768 * 4) / 1024 / 1024  # 4 bytes per float32
        
        # SPLADE memory estimation (sparse vectors)
        splade_memory = 0
        if include_splade:
            # Estimate ~50 active tokens per message on average
            splade_memory = (total_messages * 50 * 4) / 1024 / 1024  # Sparse representation
        
        # Additional analysis memory
        analysis_memory = total_messages * 0.01  # MB, rough estimate
        
        total_memory = base_memory + embedding_memory + splade_memory + analysis_memory
        
        return {
            'base_data_mb': base_memory,
            'embeddings_mb': embedding_memory,
            'splade_mb': splade_memory,
            'analysis_mb': analysis_memory,
            'total_estimated_mb': total_memory,
            'total_estimated_gb': total_memory / 1024
        }
    
    def _categorize_dataset_size(self, total_messages: int) -> str:
        """Categorize dataset size"""
        if total_messages < 1000:
            return "small"
        elif total_messages < self.LARGE_DATASET_THRESHOLD:
            return "medium"
        elif total_messages < self.VERY_LARGE_DATASET_THRESHOLD:
            return "large"
        else:
            return "very_large"
    
    def _estimate_embedding_complexity(self, total_messages: int, avg_length: float) -> Dict[str, float]:
        """Estimate computational complexity for embeddings"""
        
        # Rough complexity estimation based on message count and length
        base_complexity = total_messages * (avg_length / 100) * 1.0
        
        return {
            'relative_complexity': base_complexity,
            'estimated_time_minutes': base_complexity / 100,  # Very rough estimate
            'memory_intensive': total_messages > 5000
        }
    
    def _estimate_splade_complexity(self, total_messages: int, avg_length: float) -> Dict[str, float]:
        """Estimate computational complexity for SPLADE"""
        
        # SPLADE is more computationally expensive than standard embeddings
        base_complexity = total_messages * (avg_length / 50) * 3.0  # 3x multiplier for SPLADE
        
        return {
            'relative_complexity': base_complexity,
            'estimated_time_minutes': base_complexity / 50,  # SPLADE is slower
            'memory_intensive': total_messages > 2000
        }
    
    def _suggest_optimization_strategy(self, total_messages: int, unique_users: int, 
                                     embedding_complexity: Dict, splade_complexity: Dict) -> Dict[str, Any]:
        """Suggest optimization strategy based on dataset characteristics"""
        
        strategies = []
        
        if total_messages > self.VERY_LARGE_DATASET_THRESHOLD:
            strategies.extend([
                "use_subset_analysis",
                "enable_chunked_processing", 
                "reduce_batch_sizes",
                "disable_expensive_features"
            ])
        elif total_messages > self.LARGE_DATASET_THRESHOLD:
            strategies.extend([
                "reduce_batch_sizes",
                "enable_chunked_processing"
            ])
        
        if splade_complexity['memory_intensive']:
            strategies.append("limit_splade_batch_size")
        
        if embedding_complexity['memory_intensive']:
            strategies.append("use_ollama_embeddings")  # More memory efficient
        
        return {
            'recommended_strategies': strategies,
            'should_use_subset': total_messages > 10000,
            'enable_progressive_analysis': total_messages > 15000,
            'priority_features': self._prioritize_features(total_messages)
        }
    
    def _prioritize_features(self, total_messages: int) -> List[str]:
        """Prioritize analysis features based on dataset size"""
        
        if total_messages > 15000:
            # Focus on core features for very large datasets
            return [
                "basic_stats",
                "fun_metrics", 
                "embeddings_lite",
                "topic_analysis_basic"
            ]
        elif total_messages > 8000:
            # Standard feature set for large datasets
            return [
                "basic_stats",
                "fun_metrics",
                "embeddings",
                "topic_analysis", 
                "mood_analysis_basic"
            ]
        else:
            # Full feature set for manageable datasets
            return [
                "basic_stats",
                "fun_metrics",
                "embeddings",
                "topic_analysis",
                "mood_analysis",
                "rhythm_analysis",
                "splade_indexing"
            ]
    
    def _recommend_subset_size(self, total_messages: int) -> int:
        """Recommend optimal subset size"""
        
        if total_messages <= 2000:
            return total_messages
        elif total_messages <= 5000:
            return min(1500, total_messages)
        elif total_messages <= 10000:
            return min(2000, total_messages)
        else:
            return min(3000, total_messages)
    
    def _estimate_processing_time(self, total_messages: int, embedding_complexity: Dict) -> Dict[str, float]:
        """Estimate processing time for different components"""
        
        base_time = total_messages / 1000  # 1 minute per 1000 messages baseline
        
        return {
            'basic_analysis_minutes': base_time * 0.5,
            'embeddings_minutes': embedding_complexity['estimated_time_minutes'],
            'splade_minutes': embedding_complexity['estimated_time_minutes'] * 2,
            'total_estimated_minutes': base_time + embedding_complexity['estimated_time_minutes'] * 2
        }
    
    def _create_balanced_subset(self, df: pd.DataFrame, subset_size: int) -> pd.DataFrame:
        """Create a balanced subset maintaining user and temporal distribution"""
        
        # Sample proportionally by user
        user_counts = df['user'].value_counts()
        user_ratios = user_counts / len(df)
        
        selected_indices = []
        
        for user, ratio in user_ratios.items():
            user_messages = df[df['user'] == user]
            n_to_sample = int(subset_size * ratio)
            
            if n_to_sample > 0 and len(user_messages) > 0:
                # Sample temporally distributed messages from this user
                sampled = user_messages.sample(
                    n=min(n_to_sample, len(user_messages)), 
                    random_state=42
                ).index
                selected_indices.extend(sampled)
        
        # If we don't have enough, randomly sample more
        if len(selected_indices) < subset_size:
            remaining = subset_size - len(selected_indices)
            remaining_df = df.drop(selected_indices)
            if len(remaining_df) > 0:
                additional = remaining_df.sample(
                    n=min(remaining, len(remaining_df)), 
                    random_state=42
                ).index
                selected_indices.extend(additional)
        
        return df.loc[selected_indices].sort_values('datetime').reset_index(drop=True)
    
    def _create_temporal_subset(self, df: pd.DataFrame, subset_size: int) -> pd.DataFrame:
        """Create a subset that spans the entire temporal range"""
        
        df_sorted = df.sort_values('datetime')
        
        # Sample evenly across time
        indices = np.linspace(0, len(df_sorted) - 1, subset_size, dtype=int)
        
        return df_sorted.iloc[indices].reset_index(drop=True)
    
    def _create_diverse_subset(self, df: pd.DataFrame, subset_size: int) -> pd.DataFrame:
        """Create a diverse subset maximizing message variety"""
        
        # Priority sampling based on message length, user diversity, and temporal spread
        df_scored = df.copy()
        
        # Score messages based on diversity factors
        df_scored['length_score'] = df_scored['message'].str.len()
        df_scored['user_rarity'] = df_scored['user'].map(1 / df_scored['user'].value_counts())
        
        # Normalize scores
        df_scored['length_score'] = (df_scored['length_score'] - df_scored['length_score'].min()) / (df_scored['length_score'].max() - df_scored['length_score'].min())
        df_scored['user_rarity'] = (df_scored['user_rarity'] - df_scored['user_rarity'].min()) / (df_scored['user_rarity'].max() - df_scored['user_rarity'].min())
        
        # Combined diversity score
        df_scored['diversity_score'] = df_scored['length_score'] * 0.3 + df_scored['user_rarity'] * 0.7
        
        # Sample based on diversity scores
        sampled = df_scored.nlargest(subset_size, 'diversity_score')
        
        return sampled.drop(['length_score', 'user_rarity', 'diversity_score'], axis=1).sort_values('datetime').reset_index(drop=True)
    
    def save_subset_analysis_report(self, original_df: pd.DataFrame, subset_df: pd.DataFrame, 
                                  output_path: Path, optimization_info: Dict) -> None:
        """Save a report about the subset analysis"""
        
        report = {
            'subset_creation_timestamp': datetime.now().isoformat(),
            'original_dataset': {
                'total_messages': len(original_df),
                'unique_users': original_df['user'].nunique(),
                'date_range': {
                    'start': original_df['datetime'].min().isoformat(),
                    'end': original_df['datetime'].max().isoformat()
                }
            },
            'subset_dataset': {
                'total_messages': len(subset_df),
                'unique_users': subset_df['user'].nunique(),
                'date_range': {
                    'start': subset_df['datetime'].min().isoformat(),
                    'end': subset_df['datetime'].max().isoformat()
                },
                'subset_ratio': len(subset_df) / len(original_df)
            },
            'optimization_info': optimization_info,
            'quality_metrics': self._calculate_subset_quality(original_df, subset_df)
        }
        
        with open(output_path / 'subset_analysis_report.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2, default=str)
    
    def _calculate_subset_quality(self, original_df: pd.DataFrame, subset_df: pd.DataFrame) -> Dict[str, float]:
        """Calculate quality metrics for the subset"""
        
        # User representation quality
        orig_user_dist = original_df['user'].value_counts(normalize=True).sort_index()
        subset_user_dist = subset_df['user'].value_counts(normalize=True).sort_index()
        
        # Ensure same users
        common_users = set(orig_user_dist.index) & set(subset_user_dist.index)
        user_representation_score = len(common_users) / len(orig_user_dist.index)
        
        # Temporal coverage
        orig_span = (original_df['datetime'].max() - original_df['datetime'].min()).total_seconds()
        subset_span = (subset_df['datetime'].max() - subset_df['datetime'].min()).total_seconds()
        temporal_coverage = min(1.0, subset_span / orig_span) if orig_span > 0 else 1.0
        
        # Message length distribution similarity
        orig_lengths = original_df['message'].str.len()
        subset_lengths = subset_df['message'].str.len()
        
        length_similarity = 1 - abs(orig_lengths.mean() - subset_lengths.mean()) / orig_lengths.mean()
        
        return {
            'user_representation_score': user_representation_score,
            'temporal_coverage_score': temporal_coverage,
            'message_length_similarity': length_similarity,
            'overall_quality_score': (user_representation_score + temporal_coverage + length_similarity) / 3
        }