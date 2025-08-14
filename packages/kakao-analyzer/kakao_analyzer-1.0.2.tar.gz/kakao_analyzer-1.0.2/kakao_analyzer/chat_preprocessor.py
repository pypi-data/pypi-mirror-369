"""KakaoTalk-specific preprocessing for better chat analysis"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Tuple
from datetime import datetime, timedelta
import logging
import re
from collections import defaultdict


class KakaoTalkPreprocessor:
    """Preprocessor specifically designed for KakaoTalk chat patterns"""
    
    def __init__(self, logger: logging.Logger = None):
        self.logger = logger or logging.getLogger(__name__)
        
        # KakaoTalk-specific settings
        self.MESSAGE_GROUP_WINDOW_SECONDS = 60  # 1분 이내 메시지 그룹핑
        self.MIN_GROUP_SIZE = 2  # 최소 2개 이상의 메시지가 있어야 그룹핑
        
        # Korean chat patterns
        self.KOREAN_CHAT_PATTERNS = {
            'laughter': [r'ㅋ+', r'ㅎ+', r'하+', r'호+'],
            'crying': [r'ㅠ+', r'ㅜ+', r'흑+'],
            'agreement': [r'ㅇㅇ', r'응응', r'넵', r'네네', r'맞아+'],
            'short_responses': [r'^ㅇㅋ$', r'^오케$', r'^굿$', r'^ㄱㄱ$', r'^ㄴㄴ$'],
            'continuation': [r'그리고', r'그런데', r'근데', r'아 그리고', r'근데 또'],
            'profanity_indicators': [r'\*+', r'시발', r'ㅂㅅ', r'좆', r'개\w+']
        }
    
    def group_consecutive_messages(self, df: pd.DataFrame) -> pd.DataFrame:
        """Group consecutive messages from same user within time window"""
        
        self.logger.info(f"Grouping consecutive messages (window: {self.MESSAGE_GROUP_WINDOW_SECONDS}s)")
        
        if df.empty:
            return df
        
        # Sort by datetime
        df_sorted = df.sort_values('datetime').reset_index(drop=True)
        
        grouped_messages = []
        current_group = None
        
        for idx, row in df_sorted.iterrows():
            user = row['user']
            message = str(row['message']).strip()
            timestamp = row['datetime']
            
            # Check if this message should be grouped with previous
            should_group = (
                current_group is not None and
                current_group['user'] == user and
                (timestamp - current_group['last_timestamp']).total_seconds() <= self.MESSAGE_GROUP_WINDOW_SECONDS
            )
            
            if should_group:
                # Add to current group
                current_group['messages'].append(message)
                current_group['original_indices'].append(idx)
                current_group['last_timestamp'] = timestamp
                current_group['message_count'] += 1
            else:
                # Finalize previous group if exists
                if current_group is not None:
                    grouped_messages.append(self._finalize_group(current_group))
                
                # Start new group
                current_group = {
                    'user': user,
                    'messages': [message],
                    'original_indices': [idx],
                    'start_timestamp': timestamp,
                    'last_timestamp': timestamp,
                    'message_count': 1
                }
        
        # Don't forget the last group
        if current_group is not None:
            grouped_messages.append(self._finalize_group(current_group))
        
        # Create new dataframe
        grouped_df = pd.DataFrame(grouped_messages)
        
        self.logger.info(f"Grouped {len(df)} messages into {len(grouped_df)} message groups")
        self.logger.info(f"Reduction ratio: {(1 - len(grouped_df)/len(df))*100:.1f}%")
        
        return grouped_df
    
    def _finalize_group(self, group: Dict) -> Dict:
        """Finalize a message group by combining messages intelligently"""
        
        messages = group['messages']
        
        if len(messages) == 1:
            # Single message - no grouping needed
            combined_message = messages[0]
            group_type = 'single'
        else:
            # Multiple messages - combine intelligently
            combined_message, group_type = self._combine_messages(messages)
        
        # Calculate derived statistics
        message_length = len(combined_message)
        word_count = len(combined_message.split()) if combined_message.strip() else 0
        timestamp = group['start_timestamp']
        
        # Korean weekday names
        weekday_names = ['월요일', '화요일', '수요일', '목요일', '금요일', '토요일', '일요일']
        
        return {
            'datetime': timestamp,
            'user': group['user'],
            'message': combined_message,
            'original_count': group['message_count'],
            'group_type': group_type,
            'is_grouped': len(messages) > 1,
            'time_span_seconds': (group['last_timestamp'] - timestamp).total_seconds(),
            'message_length': message_length,
            'word_count': word_count,
            'date_only': timestamp.date(),
            'hour': timestamp.hour,
            'day_of_week': timestamp.weekday(),
            'weekday_name': weekday_names[timestamp.weekday()],
            'is_weekend': timestamp.weekday() >= 5
        }
    
    def _combine_messages(self, messages: List[str]) -> Tuple[str, str]:
        """Intelligently combine multiple messages based on Korean chat patterns"""
        
        # Clean empty messages
        messages = [msg.strip() for msg in messages if msg.strip()]
        
        if not messages:
            return "", "empty"
        
        if len(messages) == 1:
            return messages[0], "single"
        
        # Analyze message patterns
        group_type = self._analyze_message_group_type(messages)
        
        if group_type == "sentence_split":
            # Messages that form a sentence when combined
            combined = " ".join(messages)
        elif group_type == "emotional_burst":
            # Emotional expressions (ㅋㅋㅋ, ㅠㅠㅠ etc.)
            combined = " ".join(messages)
        elif group_type == "list_items":
            # List-like messages
            combined = "\n".join(messages)
        elif group_type == "correction":
            # Correction pattern (last message is the intended one)
            combined = messages[-1] + f" (수정: {' → '.join(messages[:-1])})"
        else:
            # Default: join with spaces
            combined = " ".join(messages)
        
        return combined, group_type
    
    def _analyze_message_group_type(self, messages: List[str]) -> str:
        """Analyze what type of message group this is"""
        
        # Check for emotional bursts (repetitive patterns)
        emotional_count = 0
        for msg in messages:
            for pattern_list in [self.KOREAN_CHAT_PATTERNS['laughter'], 
                               self.KOREAN_CHAT_PATTERNS['crying']]:
                for pattern in pattern_list:
                    if re.search(pattern, msg):
                        emotional_count += 1
                        break
        
        if emotional_count >= len(messages) * 0.7:
            return "emotional_burst"
        
        # Check for sentence splitting (common Korean chat pattern)
        total_length = sum(len(msg) for msg in messages)
        if total_length > 30 and len(messages) >= 3:
            # Check if combining creates a more coherent sentence
            combined = " ".join(messages)
            if self._is_likely_sentence(combined):
                return "sentence_split"
        
        # Check for list items (each message starts with number or bullet)
        list_pattern = r'^[\d\-\*\•]\s*'
        list_count = sum(1 for msg in messages if re.match(list_pattern, msg))
        if list_count >= len(messages) * 0.7:
            return "list_items"
        
        # Check for correction pattern (last message corrects previous)
        if len(messages) >= 2:
            last_msg = messages[-1]
            if any(word in last_msg for word in ['아니', '아니야', '틀렸다', '수정', '다시']):
                return "correction"
        
        return "general"
    
    def _is_likely_sentence(self, text: str) -> bool:
        """Check if text forms a coherent Korean sentence"""
        
        # Simple heuristics for Korean sentence coherence
        korean_sentence_indicators = [
            r'[가-힣]{3,}',  # Contains Korean words
            r'[.!?]$',      # Ends with punctuation
            r'(이다|다|요|어요|아요)$',  # Common Korean endings
        ]
        
        for pattern in korean_sentence_indicators:
            if re.search(pattern, text):
                return True
        
        return False
    
    def analyze_chat_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze Korean-specific chat patterns"""
        
        self.logger.info("Analyzing Korean chat patterns...")
        
        patterns = {}
        
        for pattern_name, pattern_list in self.KOREAN_CHAT_PATTERNS.items():
            pattern_counts = defaultdict(int)
            
            for _, row in df.iterrows():
                message = str(row['message']).lower()
                user = row['user']
                
                for pattern in pattern_list:
                    matches = len(re.findall(pattern, message))
                    if matches > 0:
                        pattern_counts[user] += matches
            
            patterns[pattern_name] = dict(pattern_counts)
        
        # Calculate pattern statistics
        stats = {}
        for pattern_name, user_counts in patterns.items():
            if user_counts:
                stats[pattern_name] = {
                    'total_count': sum(user_counts.values()),
                    'top_users': sorted(user_counts.items(), key=lambda x: x[1], reverse=True)[:3],
                    'user_count': len(user_counts)
                }
            else:
                stats[pattern_name] = {'total_count': 0, 'top_users': [], 'user_count': 0}
        
        return {
            'pattern_details': patterns,
            'pattern_stats': stats,
            'total_messages': len(df),
            'grouped_messages': sum(1 for _, row in df.iterrows() if row.get('is_grouped', False))
        }
    
    def filter_system_messages(self, df: pd.DataFrame) -> pd.DataFrame:
        """Filter out KakaoTalk system messages (votes, settlements, deleted messages)"""
        
        system_message_patterns = [
            r'.*님이 나갔습니다.*',
            r'.*님이 들어왔습니다.*',
            r'.*님을 초대했습니다.*',
            r'.*님이 나가셨습니다.*',
            r'삭제된 메시지입니다\.?',
            r'투표.*',
            r'정산.*',
            r'사진.*',
            r'동영상.*',
            r'파일.*',
            r'음성메시지.*',
            r'이모티콘.*',
            r'링크.*',
            r'^$',  # Empty messages
            r'^\s*$',  # Whitespace only
        ]
        
        # Combine all patterns
        combined_pattern = '|'.join(f'({pattern})' for pattern in system_message_patterns)
        
        # Filter out system messages
        before_count = len(df)
        df_filtered = df[~df['message'].str.contains(combined_pattern, na=False, regex=True)]
        after_count = len(df_filtered)
        
        self.logger.info(f"Filtered system messages: {before_count} → {after_count} "
                        f"({before_count - after_count} system messages removed)")
        
        return df_filtered
    
    def preprocess_for_analysis(self, df: pd.DataFrame, group_messages: bool = True) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """Complete preprocessing pipeline for KakaoTalk data"""
        
        self.logger.info("Starting KakaoTalk-specific preprocessing...")
        
        original_count = len(df)
        
        # Step 0: Filter system messages
        df_filtered = self.filter_system_messages(df)
        filtered_count = len(df_filtered)
        
        # Step 1: Group consecutive messages if enabled
        if group_messages:
            df_processed = self.group_consecutive_messages(df_filtered)
        else:
            df_processed = df_filtered.copy()
            # Add required columns for non-grouped messages
            df_processed['original_count'] = 1
            df_processed['group_type'] = 'single'
            df_processed['is_grouped'] = False
            df_processed['time_span_seconds'] = 0
            
            # Add derived columns that stats calculator expects
            df_processed['message_length'] = df_processed['message'].str.len()
            df_processed['word_count'] = df_processed['message'].str.split().str.len().fillna(0)
            df_processed['date_only'] = df_processed['datetime'].dt.date
            df_processed['hour'] = df_processed['datetime'].dt.hour
            df_processed['day_of_week'] = df_processed['datetime'].dt.weekday
            df_processed['is_weekend'] = df_processed['datetime'].dt.weekday >= 5
            
            # Korean weekday names
            weekday_names = ['월요일', '화요일', '수요일', '목요일', '금요일', '토요일', '일요일']
            df_processed['weekday_name'] = df_processed['day_of_week'].map(lambda x: weekday_names[x])
        
        # Step 2: Analyze chat patterns
        chat_patterns = self.analyze_chat_patterns(df_processed)
        
        # Step 3: Add metadata
        metadata = {
            'original_message_count': original_count,
            'filtered_message_count': filtered_count,
            'processed_message_count': len(df_processed),
            'system_messages_removed': original_count - filtered_count,
            'grouping_enabled': group_messages,
            'reduction_ratio': (1 - len(df_processed)/original_count) * 100 if original_count > 0 else 0,
            'chat_patterns': chat_patterns
        }
        
        self.logger.info(f"Preprocessing complete: {original_count} → {len(df_processed)} messages")
        if group_messages:
            self.logger.info(f"Message reduction: {metadata['reduction_ratio']:.1f}%")
        
        return df_processed, metadata