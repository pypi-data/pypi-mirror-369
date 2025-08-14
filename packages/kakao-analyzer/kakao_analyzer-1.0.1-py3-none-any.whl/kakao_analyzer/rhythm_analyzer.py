"""Advanced conversation rhythm and timing pattern analysis"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
import logging
from collections import defaultdict, Counter
from datetime import datetime, timedelta
import re


class ConversationRhythmAnalyzer:
    """Analyze conversation rhythm, timing patterns and communication dynamics"""
    
    def __init__(self, config, logger: Optional[logging.Logger] = None):
        self.config = config
        self.logger = logger or logging.getLogger(__name__)
        
    def analyze_conversation_rhythm(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Comprehensive rhythm and timing analysis"""
        
        self.logger.info("Analyzing conversation rhythm and timing patterns...")
        
        # Message timing patterns
        timing_patterns = self._analyze_timing_patterns(df)
        
        # Response speed analysis
        response_analysis = self._analyze_response_patterns(df)
        
        # Conversation intensity bursts
        intensity_analysis = self._analyze_conversation_intensity(df)
        
        # User communication rhythms
        user_rhythms = self._analyze_user_rhythms(df)
        
        # Conversation flow patterns
        flow_patterns = self._analyze_conversation_flow(df)
        
        # Peak activity detection
        peak_activity = self._detect_peak_activity_periods(df)
        
        # Communication synchronicity
        synchronicity = self._analyze_communication_synchronicity(df)
        
        return {
            'timing_patterns': timing_patterns,
            'response_analysis': response_analysis,
            'intensity_analysis': intensity_analysis,
            'user_rhythms': user_rhythms,
            'flow_patterns': flow_patterns,
            'peak_activity': peak_activity,
            'synchronicity': synchronicity,
            'rhythm_insights': self._generate_rhythm_insights(timing_patterns, user_rhythms, intensity_analysis)
        }
    
    def _analyze_timing_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze message timing patterns"""
        
        df_sorted = df.sort_values('datetime')
        
        # Calculate inter-message intervals
        intervals = []
        for i in range(1, len(df_sorted)):
            interval = (df_sorted.iloc[i]['datetime'] - df_sorted.iloc[i-1]['datetime']).total_seconds()
            intervals.append(interval)
        
        intervals = np.array(intervals)
        
        # Hourly distribution
        hourly_counts = df['datetime'].dt.hour.value_counts().sort_index()
        
        # Daily distribution
        daily_counts = df['datetime'].dt.day_of_week.value_counts().sort_index()
        weekday_names = ['월', '화', '수', '목', '금', '토', '일']
        daily_distribution = {weekday_names[i]: daily_counts.get(i, 0) for i in range(7)}
        
        # Message length patterns by time
        df['hour'] = df['datetime'].dt.hour
        df['message_length'] = df['message'].str.len()
        
        hourly_length_stats = df.groupby('hour')['message_length'].agg(['mean', 'std', 'count']).to_dict('index')
        
        return {
            'interval_statistics': {
                'mean_seconds': float(np.mean(intervals)) if len(intervals) > 0 else 0,
                'median_seconds': float(np.median(intervals)) if len(intervals) > 0 else 0,
                'std_seconds': float(np.std(intervals)) if len(intervals) > 0 else 0,
                'min_seconds': float(np.min(intervals)) if len(intervals) > 0 else 0,
                'max_seconds': float(np.max(intervals)) if len(intervals) > 0 else 0
            },
            'hourly_distribution': hourly_counts.to_dict(),
            'daily_distribution': daily_distribution,
            'hourly_message_lengths': hourly_length_stats,
            'most_active_hour': int(hourly_counts.idxmax()) if not hourly_counts.empty else None,
            'most_active_day': max(daily_distribution.items(), key=lambda x: x[1])[0],
            'conversation_span_days': (df['datetime'].max() - df['datetime'].min()).days
        }
    
    def _analyze_response_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze response speed and patterns"""
        
        df_sorted = df.sort_values('datetime')
        responses = []
        
        # Find responses (different user following another user)
        for i in range(1, len(df_sorted)):
            prev_msg = df_sorted.iloc[i-1]
            curr_msg = df_sorted.iloc[i]
            
            if prev_msg['user'] != curr_msg['user']:
                response_time = (curr_msg['datetime'] - prev_msg['datetime']).total_seconds()
                
                # Only consider responses within reasonable time (< 1 hour)
                if response_time <= 3600:
                    responses.append({
                        'responder': curr_msg['user'],
                        'original_sender': prev_msg['user'],
                        'response_time_seconds': response_time,
                        'response_time_minutes': response_time / 60,
                        'original_message': prev_msg['message'],
                        'response_message': curr_msg['message'],
                        'timestamp': curr_msg['datetime']
                    })
        
        if not responses:
            return {}
        
        # Response speed categories
        response_times = [r['response_time_seconds'] for r in responses]
        
        instant_responses = sum(1 for rt in response_times if rt <= 30)  # ≤ 30 seconds
        quick_responses = sum(1 for rt in response_times if 30 < rt <= 300)  # 30s - 5min
        normal_responses = sum(1 for rt in response_times if 300 < rt <= 1800)  # 5min - 30min
        slow_responses = sum(1 for rt in response_times if rt > 1800)  # > 30min
        
        # User response patterns
        user_response_stats = defaultdict(list)
        for response in responses:
            user_response_stats[response['responder']].append(response['response_time_seconds'])
        
        user_avg_response_times = {
            user: {
                'avg_response_time_seconds': np.mean(times),
                'median_response_time_seconds': np.median(times),
                'response_count': len(times),
                'fastest_response': min(times),
                'slowest_response': max(times)
            }
            for user, times in user_response_stats.items()
        }
        
        return {
            'total_responses': len(responses),
            'response_speed_distribution': {
                'instant_responses': instant_responses,
                'quick_responses': quick_responses,
                'normal_responses': normal_responses,
                'slow_responses': slow_responses
            },
            'response_speed_percentages': {
                'instant_percent': (instant_responses / len(responses)) * 100,
                'quick_percent': (quick_responses / len(responses)) * 100,
                'normal_percent': (normal_responses / len(responses)) * 100,
                'slow_percent': (slow_responses / len(responses)) * 100
            },
            'overall_response_stats': {
                'avg_response_time_seconds': np.mean(response_times),
                'median_response_time_seconds': np.median(response_times),
                'std_response_time_seconds': np.std(response_times)
            },
            'user_response_patterns': user_avg_response_times,
            'fastest_responder': min(user_avg_response_times.items(), key=lambda x: x[1]['avg_response_time_seconds'])[0] if user_avg_response_times else None,
            'slowest_responder': max(user_avg_response_times.items(), key=lambda x: x[1]['avg_response_time_seconds'])[0] if user_avg_response_times else None
        }
    
    def _analyze_conversation_intensity(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze conversation intensity and burst patterns"""
        
        df_sorted = df.sort_values('datetime')
        
        # Define time windows for intensity calculation
        window_minutes = 10
        intensity_data = []
        
        # Calculate rolling intensity
        start_time = df_sorted['datetime'].min()
        end_time = df_sorted['datetime'].max()
        current_time = start_time
        
        while current_time < end_time:
            window_end = current_time + timedelta(minutes=window_minutes)
            
            # Count messages in this window
            window_messages = df_sorted[
                (df_sorted['datetime'] >= current_time) & 
                (df_sorted['datetime'] < window_end)
            ]
            
            if not window_messages.empty:
                intensity_data.append({
                    'window_start': current_time,
                    'window_end': window_end,
                    'message_count': len(window_messages),
                    'unique_users': window_messages['user'].nunique(),
                    'avg_message_length': window_messages['message'].str.len().mean(),
                    'intensity_score': len(window_messages) * window_messages['user'].nunique()  # Messages * user diversity
                })
            
            current_time = window_end
        
        if not intensity_data:
            return {}
        
        # Find intensity bursts
        intensity_scores = [d['intensity_score'] for d in intensity_data]
        mean_intensity = np.mean(intensity_scores)
        std_intensity = np.std(intensity_scores)
        
        # Bursts are windows with intensity > mean + 2*std
        burst_threshold = mean_intensity + 2 * std_intensity
        
        bursts = [
            d for d in intensity_data 
            if d['intensity_score'] > burst_threshold
        ]
        
        # Longest conversation sessions (consecutive high-activity windows)
        sessions = []
        current_session = []
        
        for window in intensity_data:
            if window['message_count'] >= 3:  # Active window
                current_session.append(window)
            else:
                if len(current_session) >= 2:  # End of session
                    session_start = current_session[0]['window_start']
                    session_end = current_session[-1]['window_end']
                    total_messages = sum(w['message_count'] for w in current_session)
                    
                    sessions.append({
                        'start_time': session_start,
                        'end_time': session_end,
                        'duration_minutes': (session_end - session_start).total_seconds() / 60,
                        'total_messages': total_messages,
                        'avg_intensity': np.mean([w['intensity_score'] for w in current_session]),
                        'windows': current_session
                    })
                current_session = []
        
        # Handle final session
        if len(current_session) >= 2:
            session_start = current_session[0]['window_start']
            session_end = current_session[-1]['window_end']
            total_messages = sum(w['message_count'] for w in current_session)
            
            sessions.append({
                'start_time': session_start,
                'end_time': session_end,
                'duration_minutes': (session_end - session_start).total_seconds() / 60,
                'total_messages': total_messages,
                'avg_intensity': np.mean([w['intensity_score'] for w in current_session]),
                'windows': current_session
            })
        
        return {
            'intensity_windows': intensity_data,
            'intensity_statistics': {
                'mean_intensity': mean_intensity,
                'max_intensity': max(intensity_scores),
                'min_intensity': min(intensity_scores),
                'intensity_variation': std_intensity / mean_intensity if mean_intensity > 0 else 0
            },
            'conversation_bursts': bursts,
            'peak_intensity_period': max(intensity_data, key=lambda x: x['intensity_score']) if intensity_data else None,
            'conversation_sessions': sorted(sessions, key=lambda x: x['avg_intensity'], reverse=True),
            'longest_session': max(sessions, key=lambda x: x['duration_minutes']) if sessions else None,
            'most_intense_session': max(sessions, key=lambda x: x['avg_intensity']) if sessions else None
        }
    
    def _analyze_user_rhythms(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze individual user communication rhythms"""
        
        user_rhythms = {}
        
        for user in df['user'].unique():
            user_messages = df[df['user'] == user].sort_values('datetime')
            
            if len(user_messages) < 2:
                continue
            
            # Calculate user's inter-message intervals
            intervals = []
            for i in range(1, len(user_messages)):
                interval = (user_messages.iloc[i]['datetime'] - user_messages.iloc[i-1]['datetime']).total_seconds()
                intervals.append(interval)
            
            intervals = np.array(intervals)
            
            # User's active hours
            hourly_activity = user_messages['datetime'].dt.hour.value_counts().sort_index()
            
            # Message patterns
            message_lengths = user_messages['message'].str.len()
            
            # Consistency metrics
            hourly_std = hourly_activity.std()
            hourly_mean = hourly_activity.mean()
            consistency_score = 1 / (1 + hourly_std / max(1, hourly_mean))  # Higher is more consistent
            
            # User's peak activity times
            peak_hours = hourly_activity.nlargest(3).index.tolist()
            
            user_rhythms[user] = {
                'message_count': len(user_messages),
                'avg_interval_seconds': float(np.mean(intervals)) if len(intervals) > 0 else 0,
                'median_interval_seconds': float(np.median(intervals)) if len(intervals) > 0 else 0,
                'interval_consistency': 1 / (1 + np.std(intervals) / max(1, np.mean(intervals))) if len(intervals) > 0 else 0,
                'hourly_activity': hourly_activity.to_dict(),
                'peak_activity_hours': peak_hours,
                'activity_consistency_score': consistency_score,
                'avg_message_length': float(message_lengths.mean()),
                'message_length_std': float(message_lengths.std()),
                'most_active_hour': int(hourly_activity.idxmax()) if not hourly_activity.empty else None,
                'activity_span_hours': len([h for h, count in hourly_activity.items() if count > 0]),
                'burst_tendency': len([i for i in intervals if i < 60]) / max(1, len(intervals)) if len(intervals) > 0 else 0  # % of messages sent within 1 minute
            }
        
        # Identify rhythm types
        rhythm_types = self._classify_user_rhythms(user_rhythms)
        
        # Find users with valid metrics
        valid_users = {k: v for k, v in user_rhythms.items() if 'activity_consistency_score' in v and 'burst_tendency' in v}
        
        return {
            'user_rhythms': user_rhythms,
            'rhythm_classifications': rhythm_types,
            'most_consistent_user': max(valid_users.items(), key=lambda x: x[1]['activity_consistency_score'])[0] if valid_users else None,
            'most_bursty_user': max(valid_users.items(), key=lambda x: x[1]['burst_tendency'])[0] if valid_users else None
        }
    
    def _analyze_conversation_flow(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze conversation flow patterns"""
        
        df_sorted = df.sort_values('datetime')
        
        # User transition patterns
        transitions = []
        for i in range(1, len(df_sorted)):
            prev_user = df_sorted.iloc[i-1]['user']
            curr_user = df_sorted.iloc[i]['user']
            
            transitions.append({
                'from_user': prev_user,
                'to_user': curr_user,
                'is_switch': prev_user != curr_user,
                'timestamp': df_sorted.iloc[i]['datetime']
            })
        
        # Calculate flow metrics
        total_transitions = len(transitions)
        user_switches = sum(1 for t in transitions if t['is_switch'])
        
        # User dominance patterns (consecutive messages)
        consecutive_patterns = defaultdict(list)
        current_streak = 1
        current_user = df_sorted.iloc[0]['user'] if not df_sorted.empty else None
        
        for i in range(1, len(df_sorted)):
            if df_sorted.iloc[i]['user'] == current_user:
                current_streak += 1
            else:
                consecutive_patterns[current_user].append(current_streak)
                current_user = df_sorted.iloc[i]['user']
                current_streak = 1
        
        if current_user:
            consecutive_patterns[current_user].append(current_streak)
        
        # Flow smoothness (how often users switch vs. dominate)
        switch_rate = user_switches / max(1, total_transitions)
        
        # Conversation turn-taking patterns
        user_turn_stats = {}
        for user, streaks in consecutive_patterns.items():
            user_turn_stats[user] = {
                'avg_consecutive_messages': np.mean(streaks),
                'max_consecutive_messages': max(streaks) if streaks else 0,
                'total_turns': len(streaks),
                'turn_length_std': np.std(streaks)
            }
        
        return {
            'total_transitions': total_transitions,
            'user_switches': user_switches,
            'switch_rate': switch_rate,
            'flow_smoothness': 'smooth' if 0.3 < switch_rate < 0.7 else 'choppy' if switch_rate > 0.7 else 'dominated',
            'consecutive_message_patterns': dict(consecutive_patterns),
            'user_turn_statistics': user_turn_stats,
            'most_dominant_user': max(user_turn_stats.items(), key=lambda x: x[1]['avg_consecutive_messages'])[0] if user_turn_stats else None,
            'best_turn_taker': min(user_turn_stats.items(), key=lambda x: x[1]['avg_consecutive_messages'])[0] if user_turn_stats else None
        }
    
    def _detect_peak_activity_periods(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Detect periods of peak conversation activity"""
        
        # Group by hour and date
        df['date'] = df['datetime'].dt.date
        df['hour'] = df['datetime'].dt.hour
        
        # Daily activity patterns
        daily_activity = df.groupby('date').size()
        
        # Hourly activity patterns
        hourly_activity = df.groupby(['date', 'hour']).size().reset_index(name='message_count')
        
        # Find peak days
        top_days = daily_activity.nlargest(3)
        
        # Find peak hours across all days
        peak_hourly = df.groupby('hour').size().nlargest(3)
        
        # Find specific peak periods (day + hour combinations)
        peak_periods = hourly_activity.nlargest(5, 'message_count')
        
        return {
            'peak_days': [
                {
                    'date': str(date),
                    'message_count': int(count),
                    'weekday': date.strftime('%A')
                }
                for date, count in top_days.items()
            ],
            'peak_hours': [
                {
                    'hour': int(hour),
                    'message_count': int(count),
                    'time_period': self._get_time_period_name(hour)
                }
                for hour, count in peak_hourly.items()
            ],
            'peak_periods': [
                {
                    'date': str(row['date']),
                    'hour': int(row['hour']),
                    'message_count': int(row['message_count']),
                    'period_name': f"{row['date']} {row['hour']:02d}:00"
                }
                for _, row in peak_periods.iterrows()
            ]
        }
    
    def _analyze_communication_synchronicity(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze how synchronized user communications are"""
        
        # Group messages by time windows to detect simultaneous activity
        window_minutes = 5
        df_sorted = df.sort_values('datetime')
        
        # Create time windows
        start_time = df_sorted['datetime'].min()
        end_time = df_sorted['datetime'].max()
        
        sync_windows = []
        current_time = start_time
        
        while current_time < end_time:
            window_end = current_time + timedelta(minutes=window_minutes)
            
            window_messages = df_sorted[
                (df_sorted['datetime'] >= current_time) & 
                (df_sorted['datetime'] < window_end)
            ]
            
            if len(window_messages) > 1:  # Multiple messages in window
                unique_users = window_messages['user'].nunique()
                if unique_users > 1:  # Multiple users active
                    sync_windows.append({
                        'start_time': current_time,
                        'end_time': window_end,
                        'message_count': len(window_messages),
                        'active_users': unique_users,
                        'users': window_messages['user'].unique().tolist(),
                        'synchronicity_score': unique_users * len(window_messages)
                    })
            
            current_time = window_end
        
        # User co-activity analysis
        user_pairs = {}
        users = df['user'].unique()
        
        for i, user1 in enumerate(users):
            for user2 in users[i+1:]:
                # Find overlapping activity periods
                user1_messages = df[df['user'] == user1]['datetime']
                user2_messages = df[df['user'] == user2]['datetime']
                
                # Count simultaneous activity (within 5 minutes)
                simultaneous_count = 0
                for msg1_time in user1_messages:
                    nearby_msgs = user2_messages[
                        (user2_messages >= msg1_time - timedelta(minutes=5)) &
                        (user2_messages <= msg1_time + timedelta(minutes=5))
                    ]
                    if len(nearby_msgs) > 0:
                        simultaneous_count += 1
                
                user_pairs[f"{user1}_{user2}"] = {
                    'simultaneous_periods': simultaneous_count,
                    'synchronicity_ratio': simultaneous_count / max(1, len(user1_messages))
                }
        
        return {
            'synchronous_periods': sync_windows,
            'total_sync_periods': len(sync_windows),
            'user_pair_synchronicity': user_pairs,
            'overall_synchronicity_score': np.mean([w['synchronicity_score'] for w in sync_windows]) if sync_windows else 0,
            'most_synchronized_period': max(sync_windows, key=lambda x: x['synchronicity_score']) if sync_windows else None,
            'most_synchronized_users': max(user_pairs.items(), key=lambda x: x[1]['synchronicity_ratio'])[0] if user_pairs else None
        }
    
    def _classify_user_rhythms(self, user_rhythms: Dict[str, Any]) -> Dict[str, str]:
        """Classify users based on their communication rhythms"""
        
        classifications = {}
        
        for user, rhythm_data in user_rhythms.items():
            consistency = rhythm_data['activity_consistency_score']
            burst_tendency = rhythm_data['burst_tendency']
            span_hours = rhythm_data['activity_span_hours']
            
            if consistency > 0.7:
                if span_hours > 12:
                    classifications[user] = "규칙적_활발형"  # Regular & Active
                else:
                    classifications[user] = "규칙적_집중형"  # Regular & Focused
            elif burst_tendency > 0.3:
                classifications[user] = "폭발적_소통형"  # Bursty communicator
            elif span_hours > 15:
                classifications[user] = "야행성_소통형"  # Night owl
            else:
                classifications[user] = "일반적_소통형"  # Normal communicator
        
        return classifications
    
    def _get_time_period_name(self, hour: int) -> str:
        """Get descriptive name for time period"""
        if 6 <= hour < 12:
            return "오전"
        elif 12 <= hour < 18:
            return "오후"
        elif 18 <= hour < 22:
            return "저녁"
        else:
            return "밤"
    
    def _generate_rhythm_insights(self, timing_patterns: Dict, user_rhythms: Dict, intensity_analysis: Dict) -> List[str]:
        """Generate insights about conversation rhythm"""
        
        insights = []
        
        # Peak activity insights
        if timing_patterns.get('most_active_hour'):
            hour = timing_patterns['most_active_hour']
            period_name = self._get_time_period_name(hour)
            insights.append(f"가장 활발한 대화 시간은 {hour}시({period_name})입니다")
        
        # Response speed insights
        if user_rhythms:
            valid_users = {k: v for k, v in user_rhythms.items() if 'burst_tendency' in v and 'activity_consistency_score' in v}
            
            if valid_users:
                fastest_user = max(valid_users.items(), key=lambda x: x[1]['burst_tendency'])[0]
                most_consistent = max(valid_users.items(), key=lambda x: x[1]['activity_consistency_score'])[0]
                
                insights.append(f"{fastest_user}님이 가장 빠른 응답 속도를 보입니다")
                insights.append(f"{most_consistent}님이 가장 규칙적인 소통 패턴을 가집니다")
        
        # Intensity insights
        if intensity_analysis.get('conversation_sessions'):
            session_count = len(intensity_analysis['conversation_sessions'])
            if session_count > 5:
                insights.append("활발한 대화 세션이 자주 발생합니다")
            
            longest_session = intensity_analysis.get('longest_session')
            if longest_session and longest_session['duration_minutes'] > 60:
                insights.append(f"가장 긴 대화 세션은 {longest_session['duration_minutes']:.0f}분 지속되었습니다")
        
        # Weekend vs weekday patterns
        if timing_patterns.get('daily_distribution'):
            weekday_total = sum(timing_patterns['daily_distribution'][day] for day in ['월', '화', '수', '목', '금'])
            weekend_total = sum(timing_patterns['daily_distribution'][day] for day in ['토', '일'])
            
            if weekend_total > weekday_total:
                insights.append("주말에 더 활발한 대화를 나눕니다")
            else:
                insights.append("평일에 더 많은 대화를 나눕니다")
        
        return insights