"""Basic statistics and metrics calculation"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Tuple
from collections import Counter, defaultdict
import re
import logging

from .utils import extract_keywords, format_duration


class BasicStatsCalculator:
    """Calculate basic statistics for Kakao chat data"""
    
    def __init__(self, logger: logging.Logger = None):
        self.logger = logger or logging.getLogger(__name__)
    
    def calculate_all_stats(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate all basic statistics"""
        self.logger.info("Calculating basic statistics...")
        
        stats = {
            'per_user': self.calculate_per_user_stats(df),
            'temporal': self.calculate_temporal_stats(df),
            'global_words': self.calculate_global_word_stats(df),
            'emoji_stats': self.calculate_emoji_stats(df),
            'summary': self.calculate_summary_stats(df)
        }
        
        self.logger.info("Basic statistics calculation completed")
        return stats
    
    def calculate_per_user_stats(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Calculate per-user statistics"""
        user_stats = []
        
        for user in df['user'].unique():
            user_df = df[df['user'] == user]
            
            # Basic message stats
            total_messages = len(user_df)
            total_words = user_df['word_count'].sum()
            avg_message_length = user_df['message_length'].mean()
            avg_words_per_message = user_df['word_count'].mean()
            
            # Time-based stats
            active_days = user_df['date_only'].nunique()
            first_message = user_df['datetime'].min()
            last_message = user_df['datetime'].max()
            
            # Most active periods
            top_hours = user_df['hour'].value_counts().head(3).to_dict()
            top_weekdays = user_df['weekday_name'].value_counts().head(3).to_dict()
            
            # Keywords and common phrases
            all_text = ' '.join(user_df['message'].astype(str))
            top_keywords = extract_keywords(all_text, max_keywords=10)
            
            # Emojis and expressions
            emoji_pattern = r'[😀-🙏🌀-🗿💀-💯🚀-🛿]|ㅋ+|ㅎ+|ㄱ+|ㅠ+|ㅜ+'
            emojis = re.findall(emoji_pattern, all_text)
            top_emojis = dict(Counter(emojis).most_common(5))
            
            user_stats.append({
                'user': user,
                'total_messages': total_messages,
                'total_words': total_words,
                'avg_message_length': round(avg_message_length, 2),
                'avg_words_per_message': round(avg_words_per_message, 2),
                'active_days': active_days,
                'first_message': first_message.isoformat(),
                'last_message': last_message.isoformat(),
                'top_hours': top_hours,
                'top_weekdays': top_weekdays,
                'top_keywords': top_keywords,
                'top_emojis': top_emojis,
                'messages_per_day': round(total_messages / max(active_days, 1), 2),
                'participation_ratio': round(total_messages / len(df) * 100, 2)
            })
        
        return sorted(user_stats, key=lambda x: x['total_messages'], reverse=True)
    
    def calculate_temporal_stats(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate temporal distribution statistics"""
        
        # Hourly distribution (0-23)
        hourly = df['hour'].value_counts().sort_index()
        hourly_dict = {f"{h:02d}": count for h, count in hourly.items()}
        
        # Daily time series
        daily = df.groupby('date_only').size().reset_index(name='count')
        daily['date_only'] = daily['date_only'].astype(str)
        
        # Weekly patterns
        weekday_dist = df['weekday_name'].value_counts()
        weekday_order = ['월요일', '화요일', '수요일', '목요일', '금요일', '토요일', '일요일']
        weekday_ordered = {day: weekday_dist.get(day, 0) for day in weekday_order}
        
        # Monthly patterns
        monthly = df.groupby([df['datetime'].dt.year, df['datetime'].dt.month]).size()
        monthly_dict = {f"{year}-{month:02d}": count for (year, month), count in monthly.items()}
        
        # Peak activity analysis
        peak_hour = hourly.idxmax()
        peak_day = weekday_dist.idxmax()
        
        # Activity patterns
        morning_msgs = df[df['hour'].between(6, 11)].shape[0]
        afternoon_msgs = df[df['hour'].between(12, 17)].shape[0]
        evening_msgs = df[df['hour'].between(18, 23)].shape[0]
        night_msgs = df[df['hour'].isin([0, 1, 2, 3, 4, 5])].shape[0]
        
        total = len(df)
        
        return {
            'hourly_distribution': hourly_dict,
            'daily_timeseries': daily.to_dict('records'),
            'weekday_distribution': weekday_ordered,
            'monthly_distribution': monthly_dict,
            'peak_activity': {
                'peak_hour': f"{peak_hour:02d}:00",
                'peak_day': peak_day,
                'peak_hour_count': int(hourly.max()),
                'peak_day_count': int(weekday_dist.max())
            },
            'time_period_distribution': {
                'morning_6_11': {'count': morning_msgs, 'percent': round(morning_msgs/total*100, 1)},
                'afternoon_12_17': {'count': afternoon_msgs, 'percent': round(afternoon_msgs/total*100, 1)},
                'evening_18_23': {'count': evening_msgs, 'percent': round(evening_msgs/total*100, 1)},
                'night_0_5': {'count': night_msgs, 'percent': round(night_msgs/total*100, 1)}
            }
        }
    
    def calculate_global_word_stats(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate global word frequency statistics"""
        
        # Combine all messages
        all_text = ' '.join(df['message'].astype(str))
        
        # Basic word tokenization (space-based)
        words = all_text.split()
        words = [w for w in words if len(w) >= 2]  # Filter short words
        
        # Korean character-based words
        korean_words = re.findall(r'[가-힣]{2,}', all_text)
        
        # Common expressions and reactions
        reactions = re.findall(r'ㅋ+|ㅎ+|ㅠ+|ㅜ+|ㅋㅋ+|ㄱㄱ|ㅇㅋ|ㄴㄴ', all_text)
        
        # N-grams for common phrases
        bigrams = []
        for i in range(len(words) - 1):
            bigrams.append(f"{words[i]} {words[i+1]}")
        
        # Count frequencies
        word_freq = Counter(words).most_common(50)
        korean_word_freq = Counter(korean_words).most_common(30)
        reaction_freq = Counter(reactions).most_common(20)
        bigram_freq = Counter(bigrams).most_common(20)
        
        return {
            'total_words': len(words),
            'unique_words': len(set(words)),
            'total_korean_words': len(korean_words),
            'unique_korean_words': len(set(korean_words)),
            'word_frequency': [{'word': word, 'count': count} for word, count in word_freq],
            'korean_word_frequency': [{'word': word, 'count': count} for word, count in korean_word_freq],
            'reaction_frequency': [{'reaction': reaction, 'count': count} for reaction, count in reaction_freq],
            'bigram_frequency': [{'bigram': bigram, 'count': count} for bigram, count in bigram_freq],
            'vocabulary_richness': round(len(set(words)) / len(words) * 100, 2) if words else 0
        }
    
    def calculate_emoji_stats(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate emoji and emoticon statistics"""
        
        all_text = ' '.join(df['message'].astype(str))
        
        # Unicode emoji pattern
        emoji_pattern = r'[😀-🙏🌀-🗿💀-💯🚀-🛿]'
        emojis = re.findall(emoji_pattern, all_text)
        
        # Korean text emoticons
        emoticon_patterns = [
            r'ㅋ+',
            r'ㅎ+', 
            r'ㅠ+',
            r'ㅜ+',
            r'ㄷㄷ+',
            r'\^+\^+',
            r'ㅇㅋ',
            r'ㄱㄱ',
            r'ㄴㄴ'
        ]
        
        emoticons = []
        for pattern in emoticon_patterns:
            emoticons.extend(re.findall(pattern, all_text))
        
        # Top emojis and emoticons
        top_emojis = Counter(emojis).most_common(15)
        top_emoticons = Counter(emoticons).most_common(15)
        
        return {
            'total_emojis': len(emojis),
            'unique_emojis': len(set(emojis)),
            'total_emoticons': len(emoticons),
            'unique_emoticons': len(set(emoticons)),
            'top_emojis': [{'emoji': emoji, 'count': count} for emoji, count in top_emojis],
            'top_emoticons': [{'emoticon': emoticon, 'count': count} for emoticon, count in top_emoticons],
            'emoji_usage_rate': round(len(emojis) / len(df) * 100, 2),
            'emoticon_usage_rate': round(len(emoticons) / len(df) * 100, 2)
        }
    
    def calculate_summary_stats(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate overall summary statistics"""
        
        if df.empty:
            return {'error': 'Empty dataset'}
        
        # Time span
        time_span = df['datetime'].max() - df['datetime'].min()
        
        # User activity
        user_message_counts = df['user'].value_counts()
        
        # Additional word count statistics (filtered and unfiltered)
        # Create filtered word count by removing short words and common particles
        filtered_word_counts = []
        for message in df['message']:
            words = str(message).split()
            # Filter words: length >= 2, exclude common Korean particles
            filtered_words = [w for w in words if len(w) >= 2 and w not in ['은', '는', '이', '가', '을', '를', '에', '와', '과', '로', '으로', '의', '도', '만', '까지', '부터']]
            filtered_word_counts.append(len(filtered_words))
        
        df_temp = df.copy()
        df_temp['filtered_word_count'] = filtered_word_counts

        return {
            'total_messages': len(df),
            'unique_users': df['user'].nunique(),
            'date_range': {
                'start': df['datetime'].min().isoformat(),
                'end': df['datetime'].max().isoformat(),
                'total_days': time_span.days + 1,
                'total_hours': round(time_span.total_seconds() / 3600, 1)
            },
            'activity_summary': {
                'messages_per_day': round(len(df) / (time_span.days + 1), 2),
                'messages_per_hour': round(len(df) / (time_span.total_seconds() / 3600), 2),
                'active_days': df['date_only'].nunique(),
                'most_active_user': user_message_counts.index[0],
                'most_active_user_count': int(user_message_counts.iloc[0]),
                'most_active_user_percent': round(user_message_counts.iloc[0] / len(df) * 100, 1)
            },
            'message_characteristics': {
                'avg_length': round(df['message_length'].mean(), 1),
                'avg_words': round(df['word_count'].mean(), 1),
                'avg_filtered_words': round(df_temp['filtered_word_count'].mean(), 1),
                'median_length': int(df['message_length'].median()),
                'median_words': int(df['word_count'].median()),
                'median_filtered_words': int(df_temp['filtered_word_count'].median()),
                'max_length': int(df['message_length'].max()),
                'max_words': int(df['word_count'].max()),
                'max_filtered_words': int(df_temp['filtered_word_count'].max()),
                'total_words': int(df['word_count'].sum()),
                'total_filtered_words': int(df_temp['filtered_word_count'].sum())
            }
        }