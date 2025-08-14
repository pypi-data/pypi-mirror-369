"""Context and topic analysis using embeddings"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import logging
from collections import Counter
import json

from .embeddings import calculate_similarity_matrix, detect_similarity_changes
from .utils import extract_keywords, hash_text


class TopicAnalyzer:
    """Analyze conversation topics and context shifts"""
    
    def __init__(self, config, logger: logging.Logger = None):
        self.config = config
        self.logger = logger or logging.getLogger(__name__)
        self.similarity_threshold = config.similarity_threshold
        self.min_segment_length = config.min_segment_length
    
    def detect_topic_segments(self, df: pd.DataFrame, embeddings_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect topic segments using sliding window embeddings"""
        
        self.logger.info("Detecting topic segments...")
        
        window_embeddings = embeddings_data['window_embeddings']
        window_info = embeddings_data['window_info']
        
        if len(window_embeddings) == 0:
            return []
        
        # Calculate adjacent window similarities
        similarities = []
        for i in range(len(window_embeddings) - 1):
            sim = np.dot(window_embeddings[i], window_embeddings[i+1])
            similarities.append(sim)
        
        # Detect topic shifts (significant similarity drops)
        shift_points = detect_similarity_changes(similarities, self.similarity_threshold)
        
        # Create segments
        segments = []
        segment_starts = [0] + shift_points + [len(window_embeddings)]
        
        for i in range(len(segment_starts) - 1):
            start_window = segment_starts[i]
            end_window = segment_starts[i + 1]
            
            if end_window - start_window < 2:  # Skip very short segments
                continue
            
            # Get message indices for this segment
            start_msg_idx = window_info[start_window]['start_idx']
            end_msg_idx = window_info[end_window - 1]['end_idx']
            
            segment_df = df.iloc[start_msg_idx:end_msg_idx + 1]
            
            if len(segment_df) < self.min_segment_length:
                continue
            
            # Check if segment spans too much time (more than 7 days)
            start_time = segment_df.iloc[0]['datetime']
            end_time = segment_df.iloc[-1]['datetime']
            duration_days = (end_time - start_time).total_seconds() / (24 * 3600)
            
            if duration_days > 7:  # Split long segments by time
                # Split into smaller time-based segments
                time_segments = self._split_by_time(segment_df, max_days=3)
                for j, time_seg in enumerate(time_segments):
                    if len(time_seg) >= self.min_segment_length:
                        segment_analysis = self._analyze_segment(time_seg, f"{i}_{j}")
                        segments.append(segment_analysis)
            else:
                # Analyze segment as is
                segment_analysis = self._analyze_segment(segment_df, i)
                segments.append(segment_analysis)
        
        self.logger.info(f"Detected {len(segments)} topic segments")
        return segments
    
    def _split_by_time(self, df: pd.DataFrame, max_days: int = 3) -> List[pd.DataFrame]:
        """Split a long segment into time-based chunks"""
        
        segments = []
        df_sorted = df.sort_values('datetime').reset_index(drop=True)
        
        if df_sorted.empty:
            return segments
        
        current_start = 0
        start_time = df_sorted.iloc[0]['datetime']
        
        for i in range(len(df_sorted)):
            current_time = df_sorted.iloc[i]['datetime']
            days_diff = (current_time - start_time).total_seconds() / (24 * 3600)
            
            if days_diff > max_days:
                # Create segment from current_start to i-1
                if i > current_start:
                    segment = df_sorted.iloc[current_start:i].copy()
                    segments.append(segment)
                
                # Start new segment
                current_start = i
                start_time = current_time
        
        # Add final segment
        if current_start < len(df_sorted):
            segment = df_sorted.iloc[current_start:].copy()
            segments.append(segment)
        
        return segments
    
    def _analyze_segment(self, segment_df: pd.DataFrame, segment_id: int) -> Dict[str, Any]:
        """Analyze a single topic segment"""
        
        # Basic segment info
        start_time = segment_df.iloc[0]['datetime']
        end_time = segment_df.iloc[-1]['datetime']
        duration = (end_time - start_time).total_seconds() / 60
        
        # Participants and activity
        participants = segment_df['user'].unique().tolist()
        participant_counts = segment_df['user'].value_counts().to_dict()
        
        # Content analysis
        all_text = ' '.join(segment_df['message'].astype(str))
        keywords = extract_keywords(all_text, max_keywords=10)
        
        # Message characteristics
        avg_message_length = segment_df['message_length'].mean()
        avg_word_count = segment_df['word_count'].mean()
        total_messages = len(segment_df)
        
        # Temporal patterns
        hours = segment_df['hour'].unique().tolist()
        dominant_hour = segment_df['hour'].mode().iloc[0] if not segment_df['hour'].mode().empty else None
        
        # Activity pattern
        message_intervals = []
        for i in range(1, len(segment_df)):
            interval = (segment_df.iloc[i]['datetime'] - segment_df.iloc[i-1]['datetime']).total_seconds()
            message_intervals.append(interval)
        
        avg_interval = np.mean(message_intervals) if message_intervals else 0
        
        # Generate summary (simplified without LLM)
        summary = self._generate_simple_summary(segment_df, keywords)
        
        return {
            'segment_id': segment_id,
            'start_time': start_time,
            'end_time': end_time,
            'duration_minutes': round(duration, 2),
            'message_count': total_messages,
            'participants': participants,
            'participant_counts': participant_counts,
            'keywords': keywords,
            'summary': summary,
            'characteristics': {
                'avg_message_length': round(avg_message_length, 2),
                'avg_word_count': round(avg_word_count, 2),
                'avg_message_interval_seconds': round(avg_interval, 2),
                'dominant_hour': dominant_hour,
                'active_hours': sorted(hours),
                'interaction_density': round(total_messages / max(duration, 1), 2)  # messages per minute
            },
            'sample_messages': [
                {
                    'user': row['user'],
                    'message': row['message'][:100] + '...' if len(row['message']) > 100 else row['message'],
                    'time': row['datetime'].strftime('%H:%M')
                }
                for _, row in segment_df.head(3).iterrows()
            ]
        }
    
    def _generate_simple_summary(self, segment_df: pd.DataFrame, keywords: List[str]) -> str:
        """Generate simple rule-based summary"""
        
        participants = segment_df['user'].unique()
        top_keywords = keywords[:5]
        duration = (segment_df.iloc[-1]['datetime'] - segment_df.iloc[0]['datetime']).total_seconds() / 60
        
        # Basic template-based summary
        if len(participants) == 1:
            summary = f"{participants[0]}의 메시지"
        else:
            summary = f"{', '.join(participants[:2])} 등 {len(participants)}명의 대화"
        
        if top_keywords:
            summary += f" (주요 키워드: {', '.join(top_keywords[:3])})"
        
        if duration > 60:
            summary += f" - {int(duration/60)}시간 {int(duration%60)}분간"
        else:
            summary += f" - {int(duration)}분간"
        
        return summary
    
    def analyze_topic_shifts(self, segments: List[Dict[str, Any]], df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze topic shift patterns"""
        
        if not segments:
            return {}
        
        # Daily topic shift counts
        shift_dates = []
        for i in range(1, len(segments)):
            shift_time = segments[i]['start_time']
            shift_dates.append(shift_time.date())
        
        daily_shifts = Counter(shift_dates)
        daily_shifts_df = pd.DataFrame([
            {'date': date, 'shift_count': count}
            for date, count in daily_shifts.items()
        ])
        if not daily_shifts_df.empty:
            daily_shifts_df = daily_shifts_df.sort_values('date')
        
        # Hourly patterns
        shift_hours = [segments[i]['start_time'].hour for i in range(1, len(segments))]
        hourly_shifts = Counter(shift_hours)
        
        # Shift characteristics
        shift_intervals = []
        for i in range(1, len(segments)):
            interval = (segments[i]['start_time'] - segments[i-1]['end_time']).total_seconds() / 60
            shift_intervals.append(interval)
        
        # Participant involvement in shifts
        shift_participants = []
        for i in range(1, len(segments)):
            prev_participants = set(segments[i-1]['participants'])
            curr_participants = set(segments[i]['participants'])
            
            # Who left, who joined, who stayed
            left = prev_participants - curr_participants
            joined = curr_participants - prev_participants
            stayed = prev_participants & curr_participants
            
            shift_participants.append({
                'shift_id': i,
                'left': list(left),
                'joined': list(joined),
                'stayed': list(stayed),
                'continuity_ratio': len(stayed) / len(prev_participants) if prev_participants else 0
            })
        
        # Topic stability metrics
        segment_durations = [seg['duration_minutes'] for seg in segments]
        segment_message_counts = [seg['message_count'] for seg in segments]
        
        weekday_names = ['월요일', '화요일', '수요일', '목요일', '금요일', '토요일', '일요일']
        shift_weekdays = [segments[i]['start_time'].weekday() for i in range(1, len(segments))]
        weekday_shift_counts = {weekday_names[i]: shift_weekdays.count(i) for i in range(7)}
        
        return {
            'total_shifts': len(segments) - 1 if len(segments) > 1 else 0,
            'total_segments': len(segments),
            'daily_shifts': daily_shifts_df.to_dict('records'),
            'hourly_shift_distribution': {f"{h:02d}": hourly_shifts.get(h, 0) for h in range(24)},
            'weekday_shift_distribution': weekday_shift_counts,
            'shift_intervals': {
                'avg_minutes': round(np.mean(shift_intervals), 2) if shift_intervals else 0,
                'median_minutes': round(np.median(shift_intervals), 2) if shift_intervals else 0,
                'max_minutes': round(max(shift_intervals), 2) if shift_intervals else 0
            },
            'segment_characteristics': {
                'avg_duration_minutes': round(np.mean(segment_durations), 2),
                'avg_messages_per_segment': round(np.mean(segment_message_counts), 2),
                'longest_segment_minutes': round(max(segment_durations), 2),
                'shortest_segment_minutes': round(min(segment_durations), 2)
            },
            'participant_dynamics': shift_participants[:10]  # Top 10 for brevity
        }
    
    def export_segments(self, segments: List[Dict[str, Any]]) -> pd.DataFrame:
        """Export segments to DataFrame"""
        
        segment_records = []
        for segment in segments:
            segment_records.append({
                'segment_id': segment['segment_id'],
                'start_time': segment['start_time'],
                'end_time': segment['end_time'],
                'duration_minutes': segment['duration_minutes'],
                'message_count': segment['message_count'],
                'participant_count': len(segment['participants']),
                'participants': ', '.join(segment['participants']),
                'top_keywords': ', '.join(segment['keywords'][:5]),
                'summary': segment['summary'],
                'interaction_density': segment['characteristics']['interaction_density'],
                'dominant_hour': segment['characteristics']['dominant_hour']
            })
        
        return pd.DataFrame(segment_records)
    
    def get_topic_timeline_data(self, segments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Get data for topic timeline visualization"""
        
        timeline_data = []
        for segment in segments:
            timeline_data.append({
                'segment_id': segment['segment_id'],
                'start': segment['start_time'].timestamp(),
                'end': segment['end_time'].timestamp(),
                'label': f"주제 {segment['segment_id']+1}",
                'keywords': ', '.join(segment['keywords'][:3]),
                'participants': len(segment['participants']),
                'messages': segment['message_count'],
                'summary': segment['summary'][:50] + '...' if len(segment['summary']) > 50 else segment['summary']
            })
        
        return timeline_data