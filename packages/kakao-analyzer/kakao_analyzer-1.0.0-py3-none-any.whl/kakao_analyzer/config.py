"""Configuration settings for Kakao Analyzer"""

import os
from dataclasses import dataclass
from typing import Optional, List


@dataclass
class Config:
    """Configuration class for Kakao Analyzer"""
    
    # Model settings
    ollama_model: str = "oss:20b"
    embed_model: str = "bge-m3"
    use_ollama: bool = False
    use_splade: bool = False
    
    # Analysis parameters
    window_minutes: int = 30
    topic_window_size: int = 15
    similarity_threshold: float = 0.3
    min_segment_length: int = 5
    
    # Language settings
    language: str = "ko"
    
    # Output settings
    output_dir: Optional[str] = None
    log_level: str = "INFO"
    
    # Processing settings
    batch_size: int = 32
    max_workers: int = 4
    chunk_size: int = 10000
    
    # Visualization settings
    figure_dpi: int = 300
    figure_format: str = "png"
    korean_font: str = "AppleGothic"  # for macOS
    
    # Fun metrics settings
    streak_min_length: int = 3
    reply_timeout_minutes: int = 60
    night_hours: List[int] = None
    
    # KakaoTalk-specific settings
    enable_message_grouping: bool = True
    group_window_seconds: int = 60
    
    def __post_init__(self):
        if self.night_hours is None:
            self.night_hours = [22, 23, 0, 1, 2, 3]
    
    @classmethod
    def from_args(cls, args):
        """Create config from command line arguments"""
        # Handle topic window size (both --topic-window and --topic-window-size)
        topic_window_size = getattr(args, 'topic_window_size', None) or getattr(args, 'topic_window', cls.topic_window_size)
        
        return cls(
            ollama_model=getattr(args, 'model_name', cls.ollama_model),
            embed_model=getattr(args, 'embed_model', cls.embed_model),
            use_ollama=getattr(args, 'use_ollama', cls.use_ollama),
            use_splade=getattr(args, 'use_splade', cls.use_splade),
            window_minutes=getattr(args, 'window_minutes', cls.window_minutes),
            topic_window_size=topic_window_size,
            similarity_threshold=getattr(args, 'similarity_threshold', cls.similarity_threshold),
            figure_dpi=getattr(args, 'figure_dpi', cls.figure_dpi),
            language=getattr(args, 'language', cls.language),
            output_dir=getattr(args, 'outdir', cls.output_dir),
            batch_size=getattr(args, 'batch_size', cls.batch_size),
            max_workers=getattr(args, 'max_workers', cls.max_workers),
            enable_message_grouping=not getattr(args, 'disable_message_grouping', False),
            group_window_seconds=getattr(args, 'group_window_seconds', cls.group_window_seconds),
        )