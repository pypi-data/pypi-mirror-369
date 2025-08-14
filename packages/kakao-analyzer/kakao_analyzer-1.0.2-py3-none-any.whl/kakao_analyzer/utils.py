"""Utility functions for Kakao Analyzer"""

import os
import re
import logging
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import json
import hashlib
from datetime import datetime, timedelta


def setup_logger(log_file: str, level: str = "INFO") -> logging.Logger:
    """Setup logging configuration"""
    logger = logging.getLogger("kakao_analyzer")
    logger.setLevel(getattr(logging, level.upper()))
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # File handler
    fh = logging.FileHandler(log_file, encoding='utf-8')
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    
    # Console handler
    ch = logging.StreamHandler()
    ch.setLevel(getattr(logging, level.upper()))
    ch.setFormatter(formatter)
    
    logger.addHandler(fh)
    logger.addHandler(ch)
    
    return logger


def create_output_directories(output_dir: Path) -> Dict[str, Path]:
    """Create output directory structure - alias for create_output_structure"""
    return create_output_structure(output_dir)


def create_output_structure(output_dir: Path) -> Dict[str, Path]:
    """Create output directory structure"""
    structure = {
        'summary': output_dir / 'summary',
        'basics': output_dir / 'basics',
        'context': output_dir / 'context',
        'fun': output_dir / 'fun',
        'figures': output_dir / 'figures',
        'reports': output_dir / 'reports',
        'logs': output_dir / 'logs'
    }
    
    for dir_path in structure.values():
        dir_path.mkdir(parents=True, exist_ok=True)
    
    return structure


def detect_encoding(file_path: str) -> str:
    """Detect file encoding (UTF-8 or CP949)"""
    encodings = ['utf-8', 'cp949', 'euc-kr']
    
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                f.read(1024)  # Try to read first 1KB
            return encoding
        except UnicodeDecodeError:
            continue
    
    return 'utf-8'  # Default fallback


def normalize_message(text: str) -> str:
    """Normalize message text"""
    if pd.isna(text):
        return ""
    
    text = str(text).strip()
    
    # Remove system messages patterns
    system_patterns = [
        r'.*님이 .*님.*을? 초대했습니다\.',
        r'.*님이 나갔습니다\.',
        r'.*님이 들어왔습니다\.',
        r'.*님이 .*님의? 메시지를 가렸습니다\.',
        r'.*사진.*',
        r'.*동영상.*',
        r'.*파일.*',
        r'.*음성메시지.*',
        r'.*이모티콘.*',
        r'.*스티커.*'
    ]
    
    for pattern in system_patterns:
        if re.match(pattern, text):
            return ""
    
    return text


def extract_keywords(text: str, min_length: int = 2, max_keywords: int = 10) -> List[str]:
    """Extract keywords from text (simple version)"""
    if not text:
        return []
    
    # Simple keyword extraction (can be enhanced with proper Korean NLP)
    words = re.findall(r'[가-힣a-zA-Z0-9]+', text)
    words = [w for w in words if len(w) >= min_length]
    
    # Remove common stop words
    stop_words = {'이', '그', '저', '것', '들', '수', '있', '없', '하', '되', '이다', '하다', '되다', '아니다'}
    words = [w for w in words if w not in stop_words]
    
    # Count frequency and return top keywords
    from collections import Counter
    counter = Counter(words)
    return [word for word, _ in counter.most_common(max_keywords)]


def calculate_gini_coefficient(values: List[float]) -> float:
    """Calculate Gini coefficient for inequality measurement"""
    if not values:
        return 0.0
    
    # Convert to numpy array for easier calculation
    import numpy as np
    array = np.array(values, dtype=float)
    
    if np.sum(array) == 0:
        return 0.0
    
    # Sort the array
    sorted_array = np.sort(array)
    n = len(sorted_array)
    
    # Calculate Gini coefficient using standard formula
    # Gini = (2 * sum(i * y_i)) / (n * sum(y_i)) - (n + 1) / n
    # where y_i is sorted values and i is rank (1-indexed)
    
    cumsum = np.sum(sorted_array)
    numerator = 2 * np.sum(np.arange(1, n + 1) * sorted_array)
    gini = (numerator / (n * cumsum)) - (n + 1) / n
    
    return max(0.0, min(1.0, gini))


def parse_datetime_flexible(date_str) -> Optional[datetime]:
    """Flexible datetime parsing for various formats"""
    try:
        if date_str is None:
            return None
        if hasattr(date_str, 'isna') and date_str.isna().any():
            return None
        if pd.isna(date_str):
            return None
    except (ValueError, TypeError):
        pass
    
    date_str = str(date_str).strip()
    
    # Common datetime patterns
    patterns = [
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%d %H:%M',
        '%Y.%m.%d %H:%M:%S',
        '%Y.%m.%d %H:%M',
        '%m/%d/%Y %H:%M:%S',
        '%m/%d/%Y %H:%M'
    ]
    
    for pattern in patterns:
        try:
            return datetime.strptime(date_str, pattern)
        except ValueError:
            continue
    
    return None


def hash_text(text: str) -> str:
    """Generate hash for text"""
    return hashlib.md5(text.encode('utf-8')).hexdigest()[:8]


def save_json(data: Any, file_path: Path) -> None:
    """Save data as JSON with proper encoding"""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)


def load_json(file_path: Path) -> Any:
    """Load JSON data"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def format_duration(seconds: int) -> str:
    """Format duration in human readable format"""
    if seconds < 60:
        return f"{seconds}초"
    elif seconds < 3600:
        return f"{seconds//60}분 {seconds%60}초"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}시간 {minutes}분"


def get_time_bins(start_time: datetime, end_time: datetime, bin_size_minutes: int = 60) -> List[Tuple[datetime, datetime]]:
    """Generate time bins for analysis"""
    bins = []
    current = start_time.replace(minute=0, second=0, microsecond=0)
    
    while current < end_time:
        next_bin = current + timedelta(minutes=bin_size_minutes)
        bins.append((current, min(next_bin, end_time)))
        current = next_bin
    
    return bins


def get_gpu_info() -> Dict[str, Any]:
    """Get GPU information and availability"""
    gpu_info = {
        'available': False,
        'device_count': 0,
        'device_name': None,
        'memory_total': 0,
        'memory_free': 0,
        'memory_used': 0,
        'cuda_version': None,
        'device': 'cpu'
    }
    
    try:
        import torch
        
        if torch.cuda.is_available():
            gpu_info['available'] = True
            gpu_info['device_count'] = torch.cuda.device_count()
            gpu_info['cuda_version'] = torch.version.cuda
            
            # Get info for first GPU
            current_device = torch.cuda.current_device()
            gpu_info['device_name'] = torch.cuda.get_device_name(current_device)
            
            # Memory info
            memory_stats = torch.cuda.memory_stats(current_device)
            gpu_info['memory_total'] = torch.cuda.get_device_properties(current_device).total_memory
            gpu_info['memory_free'] = gpu_info['memory_total'] - torch.cuda.memory_allocated(current_device)
            gpu_info['memory_used'] = torch.cuda.memory_allocated(current_device)
            
            gpu_info['device'] = 'cuda'
            
    except ImportError:
        pass  # PyTorch not available
    except Exception as e:
        logging.getLogger(__name__).warning(f"Error getting GPU info: {e}")
    
    return gpu_info


def setup_gpu_memory_management(target_memory_fraction: float = 0.75) -> Dict[str, Any]:
    """Setup GPU memory management with target fraction usage"""
    result = {
        'success': False,
        'device': 'cpu',
        'memory_limit_set': False,
        'target_memory_mb': 0,
        'message': 'CPU only'
    }
    
    try:
        import torch
        
        if not torch.cuda.is_available():
            return result
        
        gpu_info = get_gpu_info()
        if not gpu_info['available']:
            return result
        
        # Calculate target memory
        total_memory = gpu_info['memory_total']
        target_memory = int(total_memory * target_memory_fraction)
        target_memory_mb = target_memory // (1024 * 1024)
        
        # Set memory fraction
        torch.cuda.set_per_process_memory_fraction(target_memory_fraction)
        
        # Clear cache to start fresh
        torch.cuda.empty_cache()
        
        result.update({
            'success': True,
            'device': 'cuda',
            'memory_limit_set': True,
            'target_memory_mb': target_memory_mb,
            'message': f'GPU memory limit set to {target_memory_mb}MB ({target_memory_fraction*100:.0f}%)'
        })
        
        # Log the setup
        logger = logging.getLogger(__name__)
        logger.info(f"🚀 GPU 메모리 관리 설정:")
        logger.info(f"   🎯 GPU: {gpu_info['device_name']}")
        logger.info(f"   💾 전체 메모리: {total_memory // (1024*1024):,}MB")
        logger.info(f"   🎚️  사용 제한: {target_memory_mb:,}MB ({target_memory_fraction*100:.0f}%)")
        logger.info(f"   ✅ CUDA 버전: {gpu_info['cuda_version']}")
        
    except ImportError:
        result['message'] = 'PyTorch not available'
    except Exception as e:
        result['message'] = f'Error setting up GPU memory: {e}'
        logging.getLogger(__name__).warning(result['message'])
    
    return result


def get_optimal_batch_size(device: str, base_batch_size: int = 32) -> int:
    """Get optimal batch size based on device capabilities"""
    if device == 'cpu':
        return base_batch_size
    
    try:
        import torch
        
        if not torch.cuda.is_available():
            return base_batch_size
        
        # Get GPU memory info
        gpu_info = get_gpu_info()
        memory_gb = gpu_info['memory_total'] / (1024**3)
        
        # Scale batch size based on GPU memory
        if memory_gb >= 12:  # High-end GPU
            return min(base_batch_size * 4, 128)
        elif memory_gb >= 8:  # Mid-range GPU
            return min(base_batch_size * 2, 64)
        elif memory_gb >= 4:  # Entry-level GPU
            return min(base_batch_size * 1.5, 48)
        else:  # Low memory GPU
            return base_batch_size
            
    except Exception:
        return base_batch_size


def setup_device(logger: logging.Logger = None) -> Dict[str, Any]:
    """Setup optimal device configuration"""
    if logger is None:
        logger = logging.getLogger(__name__)
    
    # Get GPU info
    gpu_info = get_gpu_info()
    
    if gpu_info['available']:
        # Setup GPU memory management
        memory_setup = setup_gpu_memory_management(target_memory_fraction=0.75)
        
        return {
            'device': 'cuda',
            'gpu_info': gpu_info,
            'memory_setup': memory_setup,
            'recommended_batch_size': get_optimal_batch_size('cuda')
        }
    else:
        logger.info("🖥️  GPU를 사용할 수 없습니다. CPU 모드로 실행합니다.")
        return {
            'device': 'cpu',
            'gpu_info': gpu_info,
            'memory_setup': {'success': False, 'message': 'No GPU available'},
            'recommended_batch_size': get_optimal_batch_size('cpu')
        }