"""Fun metrics and engagement analysis"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Tuple
from collections import Counter, defaultdict
from datetime import datetime, timedelta
import re
import logging

from .utils import calculate_gini_coefficient, format_duration


class FunMetricsCalculator:
    """Calculate fun and engagement metrics"""
    
    def __init__(self, config, logger: logging.Logger = None):
        self.config = config
        self.logger = logger or logging.getLogger(__name__)
        self.night_hours = config.night_hours
        self.streak_min_length = config.streak_min_length
        self.reply_timeout_minutes = config.reply_timeout_minutes
    
    def calculate_all_metrics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate all fun metrics"""
        
        self.logger.info("Calculating fun metrics...")
        
        metrics = {
            'participation_inequality': self.calculate_participation_inequality(df),
            'reply_latency': self.calculate_reply_latency_stats(df),
            'activity_streaks': self.calculate_activity_streaks(df),
            'night_chat_analysis': self.calculate_night_chat_metrics(df),
            'conversation_patterns': self.calculate_conversation_patterns(df),
            'engagement_metrics': self.calculate_engagement_metrics(df)
        }
        
        self.logger.info("Fun metrics calculation completed")
        return metrics
    
    def calculate_participation_inequality(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate participation inequality using Gini coefficient"""
        
        user_counts = df['user'].value_counts()
        message_counts = user_counts.values.tolist()
        
        # Calculate Gini coefficient
        gini_coefficient = calculate_gini_coefficient(message_counts)
        
        # Calculate concentration ratios
        total_messages = sum(message_counts)
        sorted_counts = sorted(message_counts, reverse=True)
        
        # Top 20% users' share
        top_20_percent_count = max(1, len(sorted_counts) // 5)
        top_20_percent_messages = sum(sorted_counts[:top_20_percent_count])
        top_20_percent_share = (top_20_percent_messages / total_messages) * 100
        
        # Top user dominance
        top_user_share = (sorted_counts[0] / total_messages) * 100
        
        # User participation levels
        participation_levels = []
        for user, count in user_counts.items():
            share = (count / total_messages) * 100
            
            if share >= 30:
                level = "매우 활발"
            elif share >= 15:
                level = "활발"
            elif share >= 5:
                level = "보통"
            else:
                level = "소극적"
            
            participation_levels.append({
                'user': user,
                'message_count': count,
                'share_percent': round(share, 2),
                'participation_level': level
            })
        
        return {
            'gini_coefficient': round(gini_coefficient, 3),
            'interpretation': self._interpret_gini(gini_coefficient),
            'top_20_percent_share': round(top_20_percent_share, 1),
            'top_user_share': round(top_user_share, 1),
            'most_active_user': user_counts.index[0],
            'participation_levels': participation_levels
        }
    
    def _interpret_gini(self, gini: float) -> str:
        """Interpret Gini coefficient"""
        if gini < 0.3:
            return "균등한 참여"
        elif gini < 0.5:
            return "약간 불균등"
        elif gini < 0.7:
            return "불균등한 참여"
        else:
            return "매우 불균등한 참여"
    
    def calculate_reply_latency_stats(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate reply latency statistics"""
        
        df_sorted = df.sort_values('datetime').reset_index(drop=True)
        reply_times = []
        user_reply_times = defaultdict(list)
        conversation_pairs = defaultdict(list)
        
        for i in range(1, len(df_sorted)):
            prev_msg = df_sorted.iloc[i-1]
            curr_msg = df_sorted.iloc[i]
            
            # Only consider as reply if different users
            if prev_msg['user'] != curr_msg['user']:
                time_diff = (curr_msg['datetime'] - prev_msg['datetime']).total_seconds() / 60
                
                # Only consider reasonable reply times (within timeout)
                if time_diff <= self.reply_timeout_minutes:
                    reply_times.append(time_diff)
                    user_reply_times[curr_msg['user']].append(time_diff)
                    conversation_pairs[f"{prev_msg['user']} -> {curr_msg['user']}"].append(time_diff)
        
        # Overall statistics
        if reply_times:
            overall_stats = {
                'mean_minutes': round(np.mean(reply_times), 2),
                'median_minutes': round(np.median(reply_times), 2),
                'std_minutes': round(np.std(reply_times), 2),
                'min_minutes': round(min(reply_times), 2),
                'max_minutes': round(max(reply_times), 2),
                'total_replies': len(reply_times)
            }
            
            # Percentiles
            percentiles = [25, 50, 75, 90, 95]
            for p in percentiles:
                overall_stats[f'p{p}_minutes'] = round(np.percentile(reply_times, p), 2)
        else:
            overall_stats = {'error': 'No reply data found'}
        
        # Per-user statistics
        user_stats = []
        for user, times in user_reply_times.items():
            if len(times) >= 3:  # Minimum for meaningful stats
                user_stats.append({
                    'user': user,
                    'reply_count': len(times),
                    'avg_reply_minutes': round(np.mean(times), 2),
                    'median_reply_minutes': round(np.median(times), 2),
                    'fastest_reply_minutes': round(min(times), 2),
                    'slowest_reply_minutes': round(max(times), 2)
                })
        
        user_stats.sort(key=lambda x: x['avg_reply_minutes'])
        
        # Conversation pair analysis
        pair_stats = []
        for pair, times in conversation_pairs.items():
            if len(times) >= 5:  # Minimum for meaningful pair stats
                pair_stats.append({
                    'conversation_pair': pair,
                    'interaction_count': len(times),
                    'avg_reply_minutes': round(np.mean(times), 2),
                    'median_reply_minutes': round(np.median(times), 2)
                })
        
        pair_stats.sort(key=lambda x: x['avg_reply_minutes'])
        
        return {
            'overall_stats': overall_stats,
            'user_stats': user_stats[:10],  # Top 10 users
            'conversation_pairs': pair_stats[:10],  # Top 10 pairs
            'reply_speed_categories': self._categorize_reply_speeds(reply_times)
        }
    
    def _categorize_reply_speeds(self, reply_times: List[float]) -> Dict[str, Any]:
        """Categorize reply speeds"""
        
        if not reply_times:
            return {}
        
        instant = sum(1 for t in reply_times if t <= 1)  # Within 1 minute
        quick = sum(1 for t in reply_times if 1 < t <= 5)  # 1-5 minutes
        normal = sum(1 for t in reply_times if 5 < t <= 30)  # 5-30 minutes
        slow = sum(1 for t in reply_times if t > 30)  # Over 30 minutes
        
        total = len(reply_times)
        
        return {
            'instant_replies': {'count': instant, 'percent': round(instant/total*100, 1)},
            'quick_replies': {'count': quick, 'percent': round(quick/total*100, 1)},
            'normal_replies': {'count': normal, 'percent': round(normal/total*100, 1)},
            'slow_replies': {'count': slow, 'percent': round(slow/total*100, 1)}
        }
    
    def calculate_activity_streaks(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate activity streaks and patterns"""
        
        # User activity streaks (consecutive messages)
        user_streaks = {}
        current_streaks = {}
        
        df_sorted = df.sort_values('datetime').reset_index(drop=True)
        
        for _, row in df_sorted.iterrows():
            user = row['user']
            
            if user not in user_streaks:
                user_streaks[user] = []
                current_streaks[user] = {'count': 1, 'start_time': row['datetime'], 'messages': [row['message']]}
            else:
                # Check if this continues the current streak
                prev_user = df_sorted[df_sorted.index < row.name].iloc[-1]['user'] if row.name > 0 else None
                
                if prev_user == user:
                    current_streaks[user]['count'] += 1
                    current_streaks[user]['messages'].append(row['message'])
                else:
                    # End current streak if it's significant
                    if current_streaks[user]['count'] >= self.streak_min_length:
                        user_streaks[user].append({
                            'length': current_streaks[user]['count'],
                            'start_time': current_streaks[user]['start_time'],
                            'end_time': row['datetime'],
                            'sample_messages': current_streaks[user]['messages'][:3]
                        })
                    
                    # Start new streak
                    current_streaks[user] = {'count': 1, 'start_time': row['datetime'], 'messages': [row['message']]}
        
        # Finalize remaining streaks
        for user, streak_data in current_streaks.items():
            if streak_data['count'] >= self.streak_min_length:
                user_streaks[user].append({
                    'length': streak_data['count'],
                    'start_time': streak_data['start_time'],
                    'end_time': df_sorted.iloc[-1]['datetime'],
                    'sample_messages': streak_data['messages'][:3]
                })
        
        # Streak statistics
        streak_stats = []
        for user, streaks in user_streaks.items():
            if streaks:
                streak_lengths = [s['length'] for s in streaks]
                streak_stats.append({
                    'user': user,
                    'streak_count': len(streaks),
                    'longest_streak': max(streak_lengths),
                    'avg_streak_length': round(np.mean(streak_lengths), 2),
                    'total_streak_messages': sum(streak_lengths)
                })
        
        streak_stats.sort(key=lambda x: x['longest_streak'], reverse=True)
        
        # Daily activity streaks (consecutive active days)
        daily_activity = df.groupby(df['datetime'].dt.date).size()
        active_days = daily_activity.index.tolist()
        
        consecutive_days = []
        current_streak_start = active_days[0] if active_days else None
        current_streak_length = 1
        
        for i in range(1, len(active_days)):
            if (active_days[i] - active_days[i-1]).days == 1:
                current_streak_length += 1
            else:
                if current_streak_length >= 3:  # Minimum 3 days for a streak
                    consecutive_days.append({
                        'start_date': current_streak_start,
                        'length_days': current_streak_length,
                        'total_messages': daily_activity[current_streak_start:active_days[i-1]].sum()
                    })
                current_streak_start = active_days[i]
                current_streak_length = 1
        
        # Add final streak
        if current_streak_length >= 3:
            consecutive_days.append({
                'start_date': current_streak_start,
                'length_days': current_streak_length,
                'total_messages': daily_activity[current_streak_start:].sum()
            })
        
        return {
            'user_message_streaks': streak_stats[:10],
            'consecutive_active_days': consecutive_days,
            'longest_message_streak': max([s['longest_streak'] for s in streak_stats]) if streak_stats else 0,
            'longest_daily_streak': max([s['length_days'] for s in consecutive_days]) if consecutive_days else 0
        }
    
    def calculate_night_chat_metrics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate night chatting metrics"""
        
        night_messages = df[df['hour'].isin(self.night_hours)]
        total_messages = len(df)
        
        if total_messages == 0:
            return {'error': 'No messages found'}
        
        night_ratio = len(night_messages) / total_messages
        
        # Per-user night activity
        user_night_stats = []
        for user in df['user'].unique():
            user_total = len(df[df['user'] == user])
            user_night = len(night_messages[night_messages['user'] == user])
            
            user_night_stats.append({
                'user': user,
                'night_messages': user_night,
                'total_messages': user_total,
                'night_ratio': round(user_night / user_total, 3) if user_total > 0 else 0,
                'night_percentage': round(user_night / user_total * 100, 1) if user_total > 0 else 0
            })
        
        user_night_stats.sort(key=lambda x: x['night_ratio'], reverse=True)
        
        # Night activity patterns
        night_hourly = night_messages['hour'].value_counts().sort_index()
        peak_night_hour = night_hourly.idxmax() if not night_hourly.empty else None
        
        # Late night sessions (continuous night activity)
        night_sessions = []
        if not night_messages.empty:
            night_sorted = night_messages.sort_values('datetime')
            session_start = night_sorted.iloc[0]['datetime']
            session_messages = [night_sorted.iloc[0]]
            
            for i in range(1, len(night_sorted)):
                curr_msg = night_sorted.iloc[i]
                time_gap = (curr_msg['datetime'] - session_messages[-1]['datetime']).total_seconds() / 60
                
                if time_gap <= 60:  # Within 1 hour
                    session_messages.append(curr_msg)
                else:
                    # End current session
                    if len(session_messages) >= 10:  # Minimum 10 messages for a session
                        night_sessions.append({
                            'start_time': session_start,
                            'end_time': session_messages[-1]['datetime'],
                            'duration_minutes': (session_messages[-1]['datetime'] - session_start).total_seconds() / 60,
                            'message_count': len(session_messages),
                            'participants': list(set([msg['user'] for msg in session_messages]))
                        })
                    
                    # Start new session
                    session_start = curr_msg['datetime']
                    session_messages = [curr_msg]
            
            # Add final session
            if len(session_messages) >= 10:
                night_sessions.append({
                    'start_time': session_start,
                    'end_time': session_messages[-1]['datetime'],
                    'duration_minutes': (session_messages[-1]['datetime'] - session_start).total_seconds() / 60,
                    'message_count': len(session_messages),
                    'participants': list(set([msg['user'] for _, msg in pd.DataFrame(session_messages).iterrows()]))
                })
        
        # Sort sessions by duration
        night_sessions.sort(key=lambda x: x['duration_minutes'], reverse=True)
        
        return {
            'night_chat_ratio': round(night_ratio, 3),
            'night_chat_percentage': round(night_ratio * 100, 1),
            'total_night_messages': len(night_messages),
            'peak_night_hour': f"{peak_night_hour:02d}:00" if peak_night_hour is not None else None,
            'user_night_activity': user_night_stats[:10],
            'night_sessions': night_sessions[:5],  # Top 5 longest sessions
            'night_hourly_distribution': {f"{h:02d}": night_hourly.get(h, 0) for h in self.night_hours}
        }
    
    def calculate_conversation_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze conversation patterns and behaviors"""
        
        # Question patterns
        questions = df[df['message'].str.contains(r'\?', na=False)]
        exclamations = df[df['message'].str.contains(r'!', na=False)]
        
        # Emoji/emoticon usage
        emoji_pattern = r'[😀-🙏🌀-🗿💀-💯🚀-🛿]|ㅋ+|ㅎ+|ㅠ+|ㅜ+'
        emoji_messages = df[df['message'].str.contains(emoji_pattern, na=False, regex=True)]
        
        # Short vs long messages
        short_messages = df[df['message_length'] <= 10]
        long_messages = df[df['message_length'] >= 100]
        
        # Repetitive expressions
        all_text = ' '.join(df['message'].astype(str))
        
        # Common Korean expressions/reactions
        reactions = {
            'ㅋㅋ': len(re.findall(r'ㅋ{2,}', all_text)),
            'ㅎㅎ': len(re.findall(r'ㅎ{2,}', all_text)),
            'ㅠㅠ': len(re.findall(r'ㅠ{2,}', all_text)),
            'ㄱㄱ': all_text.count('ㄱㄱ'),
            'ㅇㅋ': all_text.count('ㅇㅋ'),
            'ㄴㄴ': all_text.count('ㄴㄴ'),
            '아니': all_text.count('아니'),
            '진짜': all_text.count('진짜'),
            '완전': all_text.count('완전')
        }
        
        # Most common n-grams (simple approach)
        words = all_text.split()
        bigrams = []
        trigrams = []
        
        for i in range(len(words) - 1):
            bigrams.append(f"{words[i]} {words[i+1]}")
        
        for i in range(len(words) - 2):
            trigrams.append(f"{words[i]} {words[i+1]} {words[i+2]}")
        
        common_bigrams = Counter(bigrams).most_common(10)
        common_trigrams = Counter(trigrams).most_common(10)
        
        total_messages = len(df)
        
        return {
            'message_types': {
                'questions': {'count': len(questions), 'percentage': round(len(questions)/total_messages*100, 1)},
                'exclamations': {'count': len(exclamations), 'percentage': round(len(exclamations)/total_messages*100, 1)},
                'with_emoji': {'count': len(emoji_messages), 'percentage': round(len(emoji_messages)/total_messages*100, 1)},
                'short_messages': {'count': len(short_messages), 'percentage': round(len(short_messages)/total_messages*100, 1)},
                'long_messages': {'count': len(long_messages), 'percentage': round(len(long_messages)/total_messages*100, 1)}
            },
            'common_reactions': reactions,
            'popular_phrases': {
                'bigrams': [{'phrase': phrase, 'count': count} for phrase, count in common_bigrams],
                'trigrams': [{'phrase': phrase, 'count': count} for phrase, count in common_trigrams]
            }
        }
    
    def calculate_engagement_metrics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate overall engagement metrics"""
        
        if df.empty:
            return {'error': 'No data available'}
        
        # Time span
        time_span = df['datetime'].max() - df['datetime'].min()
        total_days = time_span.days + 1
        
        # Unique active days
        active_days = df['datetime'].dt.date.nunique()
        activity_consistency = active_days / total_days
        
        # Peak engagement periods
        hourly_activity = df['hour'].value_counts()
        daily_activity = df.groupby(df['datetime'].dt.date).size()
        
        peak_hour = hourly_activity.idxmax()
        peak_day = daily_activity.idxmax()
        
        # User interaction diversity
        user_interactions = {}
        users = df['user'].unique()
        
        for i, user1 in enumerate(users):
            user_interactions[user1] = set()
            user1_times = df[df['user'] == user1]['datetime'].values
            
            for user2 in users:
                if user1 != user2:
                    user2_times = df[df['user'] == user2]['datetime'].values
                    
                    # Check if they had messages close in time (within 10 minutes)
                    for t1 in user1_times:
                        for t2 in user2_times:
                            if abs(pd.Timestamp(t1) - pd.Timestamp(t2)).total_seconds() <= 600:
                                user_interactions[user1].add(user2)
                                break
        
        # Convert sets to counts
        interaction_counts = {user: len(interacted_with) for user, interacted_with in user_interactions.items()}
        
        return {
            'overall_engagement': {
                'total_days': total_days,
                'active_days': active_days,
                'activity_consistency': round(activity_consistency, 3),
                'messages_per_active_day': round(len(df) / active_days, 2),
                'peak_activity_hour': f"{peak_hour:02d}:00",
                'peak_activity_day': str(peak_day)
            },
            'user_interaction_diversity': [
                {'user': user, 'interacted_with_count': count}
                for user, count in sorted(interaction_counts.items(), key=lambda x: x[1], reverse=True)
            ],
            'engagement_distribution': {
                'high_activity_users': len([u for u in users if df[df['user'] == u].shape[0] > len(df) * 0.2]),
                'moderate_activity_users': len([u for u in users if len(df) * 0.05 < df[df['user'] == u].shape[0] <= len(df) * 0.2]),
                'low_activity_users': len([u for u in users if df[df['user'] == u].shape[0] <= len(df) * 0.05])
            }
        }