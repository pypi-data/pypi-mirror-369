"""Data loading and preprocessing for Kakao CSV files"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import re
from datetime import datetime
import logging

from .utils import detect_encoding, parse_datetime_flexible, normalize_message


class KakaoDataLoader:
    """Load and preprocess Kakao Talk CSV files"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        self.schema_info = {}
        
    def load_csv(self, file_path: str) -> pd.DataFrame:
        """Load CSV with automatic encoding detection and schema inference"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Detect encoding
        encoding = detect_encoding(str(file_path))
        self.logger.info(f"Detected encoding: {encoding}")
        
        # Try to load CSV
        try:
            df = pd.read_csv(file_path, encoding=encoding)
            self.logger.info(f"Loaded {len(df)} rows, {len(df.columns)} columns")
        except Exception as e:
            self.logger.error(f"Failed to load CSV: {e}")
            raise
        
        # Infer and normalize schema
        df = self._normalize_schema(df)
        
        # Preprocess data
        df = self._preprocess_data(df)
        
        return df
    
    def _normalize_schema(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize column names and schema"""
        original_columns = df.columns.tolist()
        self.logger.info(f"Original columns: {original_columns}")
        
        # Common column name mappings
        column_mappings = {
            # Date/Time columns
            'datetime': ['date', 'time', 'datetime', '날짜', '시간', '일시'],
            'user': ['user', 'sender', 'name', 'username', '사용자', '발신자', '이름'],
            'message': ['message', 'text', 'content', 'msg', '메시지', '내용', '텍스트']
        }
        
        # Find best matching columns
        normalized_cols = {}
        
        for target_col, candidates in column_mappings.items():
            best_match = None
            for col in df.columns:
                col_lower = col.lower().strip()
                if any(candidate in col_lower for candidate in candidates):
                    # Skip if we already assigned this column to another target
                    if col not in normalized_cols.values():
                        best_match = col
                        break
            
            if best_match:
                normalized_cols[target_col] = best_match
            else:
                # Fallback to positional mapping for standard CSV format
                if target_col == 'datetime' and len(df.columns) >= 1:
                    # Prefer 'datetime' over 'date' if both exist
                    if 'datetime' in df.columns and 'datetime' not in normalized_cols.values():
                        normalized_cols[target_col] = 'datetime'
                    elif 'date' in df.columns and 'date' not in normalized_cols.values():
                        normalized_cols[target_col] = 'date'
                    else:
                        normalized_cols[target_col] = df.columns[0]
                elif target_col == 'user' and len(df.columns) >= 2:
                    normalized_cols[target_col] = df.columns[1]
                elif target_col == 'message' and len(df.columns) >= 3:
                    normalized_cols[target_col] = df.columns[2]
        
        # Rename columns
        rename_map = {v: k for k, v in normalized_cols.items()}
        df = df.rename(columns=rename_map)
        
        # Remove any duplicate columns
        df = df.loc[:, ~df.columns.duplicated()]
        
        # Keep only required columns
        required_cols = ['datetime', 'user', 'message']
        available_columns = [col for col in required_cols if col in df.columns]
        df = df[available_columns]
        
        # Store schema info
        self.schema_info = {
            'original_columns': original_columns,
            'normalized_mapping': normalized_cols,
            'final_columns': df.columns.tolist()
        }
        
        self.logger.info(f"Normalized columns: {df.columns.tolist()}")
        
        # Ensure required columns exist
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if missing_cols:
            raise ValueError(f"Missing required columns after normalization: {missing_cols}")
        
        return df
    
    def _preprocess_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Preprocess the loaded data"""
        self.logger.info("Starting data preprocessing...")
        
        # Parse datetime
        df['datetime'] = df['datetime'].apply(parse_datetime_flexible)
        
        # Remove rows with invalid datetime
        initial_count = len(df)
        df = df.dropna(subset=['datetime'])
        invalid_count = initial_count - len(df)
        
        if invalid_count > 0:
            self.logger.warning(f"Removed {invalid_count} rows with invalid datetime")
        
        # Normalize messages
        df['message'] = df['message'].apply(normalize_message)
        
        # Remove empty messages
        df = df[df['message'].str.len() > 0]
        
        # Clean user names
        df['user'] = df['user'].fillna('Unknown').astype(str).str.strip()
        
        # Sort by datetime
        df = df.sort_values('datetime').reset_index(drop=True)
        
        # Add derived columns
        df['date_only'] = df['datetime'].dt.date
        df['year'] = df['datetime'].dt.year
        df['month'] = df['datetime'].dt.month
        df['day'] = df['datetime'].dt.day
        df['weekday'] = df['datetime'].dt.dayofweek  # 0=Monday
        df['hour'] = df['datetime'].dt.hour
        df['minute'] = df['datetime'].dt.minute
        
        # Add weekday names in Korean
        weekday_names = ['월요일', '화요일', '수요일', '목요일', '금요일', '토요일', '일요일']
        df['weekday_name'] = df['weekday'].apply(lambda x: weekday_names[x])
        
        # Add message length stats
        df['message_length'] = df['message'].str.len()
        df['word_count'] = df['message'].apply(lambda x: len(str(x).split()) if x else 0)
        
        self.logger.info(f"Preprocessing completed. Final dataset: {len(df)} rows")
        
        return df
    
    def get_data_overview(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate data overview statistics"""
        if df.empty:
            return {'error': 'Empty dataset'}
        
        overview = {
            'total_messages': len(df),
            'date_range': {
                'start': df['datetime'].min().isoformat() if not df.empty else None,
                'end': df['datetime'].max().isoformat() if not df.empty else None,
                'days': (df['datetime'].max() - df['datetime'].min()).days if not df.empty else 0
            },
            'users': {
                'unique_count': df['user'].nunique(),
                'names': df['user'].unique().tolist()
            },
            'message_stats': {
                'avg_length': df['message_length'].mean(),
                'avg_words': df['word_count'].mean(),
                'total_words': df['word_count'].sum()
            },
            'time_distribution': {
                'by_hour': df['hour'].value_counts().sort_index().to_dict(),
                'by_weekday': df['weekday_name'].value_counts().to_dict()
            },
            'schema_info': self.schema_info
        }
        
        return overview
    
    def validate_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Validate loaded data quality"""
        validation = {
            'is_valid': True,
            'warnings': [],
            'errors': []
        }
        
        # Check for required columns
        required_cols = ['datetime', 'user', 'message']
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if missing_cols:
            validation['errors'].append(f"Missing required columns: {missing_cols}")
            validation['is_valid'] = False
        
        # Check for empty data
        if df.empty:
            validation['errors'].append("Dataset is empty")
            validation['is_valid'] = False
            return validation
        
        # Check datetime range
        date_range = (df['datetime'].max() - df['datetime'].min()).days
        if date_range < 1:
            validation['warnings'].append("Data spans less than 1 day")
        
        # Check user count
        user_count = df['user'].nunique()
        if user_count < 2:
            validation['warnings'].append("Only one user found in data")
        
        # Check message length distribution
        empty_messages = (df['message'].str.len() == 0).sum()
        if empty_messages > 0:
            validation['warnings'].append(f"Found {empty_messages} empty messages")
        
        # Check for potential system messages
        system_patterns = [
            r'.*님이 .*초대.*',
            r'.*님이 나갔습니다.*',
            r'.*사진.*',
            r'.*동영상.*'
        ]
        
        system_count = 0
        for pattern in system_patterns:
            system_count += df['message'].str.match(pattern, na=False).sum()
        
        if system_count > len(df) * 0.1:  # More than 10% system messages
            validation['warnings'].append(f"High system message ratio: {system_count}/{len(df)}")
        
        return validation
    
    def load_and_validate(self, file_path: str) -> Tuple[pd.DataFrame, Dict[str, Any], Dict[str, Any]]:
        """Load CSV file and validate the data"""
        # Load data
        df = self.load_csv(file_path)
        
        # Get data info
        data_info = self.get_data_overview(df)
        
        # Validate data
        validation_results = self.validate_data(df)
        
        return df, data_info, validation_results
    
    def get_data_info(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Get data information - alias for get_data_overview"""
        return self.get_data_overview(df)
    
    def validate_dataframe(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Validate dataframe - alias for validate_data"""
        return self.validate_data(df)