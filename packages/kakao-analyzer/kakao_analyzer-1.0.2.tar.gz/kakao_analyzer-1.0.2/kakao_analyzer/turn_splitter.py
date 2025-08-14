"""Turn and thread splitting logic"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Tuple
from datetime import datetime, timedelta
import logging
import re

from .utils import format_duration


class TurnSplitter:
    """Split conversations into turns and threads based on time gaps and patterns"""
    
    def __init__(self, config, logger: logging.Logger = None):
        self.config = config
        self.logger = logger or logging.getLogger(__name__)
        self.window_minutes = config.window_minutes
    
    def split_turns(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Split conversation into turns based on time gaps and speaker changes"""
        self.logger.info(f"Splitting conversation into turns (window: {self.window_minutes} minutes)")
        
        if df.empty:
            return []
        
        df_sorted = df.sort_values('datetime').reset_index(drop=True)
        turns = []
        current_turn = {
            'turn_id': 0,
            'start_time': df_sorted.iloc[0]['datetime'],
            'end_time': df_sorted.iloc[0]['datetime'],
            'messages': [],
            'participants': set(),
            'message_count': 0,
            'duration_minutes': 0
        }
        
        turn_id = 0
        
        for idx, row in df_sorted.iterrows():
            time_diff = (row['datetime'] - current_turn['end_time']).total_seconds() / 60
            
            # Start new turn if time gap exceeds threshold
            if time_diff > self.window_minutes and current_turn['messages']:
                # Finalize current turn
                current_turn['participants'] = list(current_turn['participants'])
                current_turn['duration_minutes'] = (current_turn['end_time'] - current_turn['start_time']).total_seconds() / 60
                turns.append(current_turn)
                
                # Start new turn
                turn_id += 1
                current_turn = {
                    'turn_id': turn_id,
                    'start_time': row['datetime'],
                    'end_time': row['datetime'],
                    'messages': [],
                    'participants': set(),
                    'message_count': 0,
                    'duration_minutes': 0
                }
            
            # Add message to current turn
            current_turn['messages'].append({
                'datetime': row['datetime'],
                'user': row['user'],
                'message': row['message'],
                'message_length': row['message_length'],
                'word_count': row['word_count']
            })
            current_turn['participants'].add(row['user'])
            current_turn['message_count'] += 1
            current_turn['end_time'] = row['datetime']
        
        # Add the last turn
        if current_turn['messages']:
            current_turn['participants'] = list(current_turn['participants'])
            current_turn['duration_minutes'] = (current_turn['end_time'] - current_turn['start_time']).total_seconds() / 60
            turns.append(current_turn)
        
        self.logger.info(f"Split into {len(turns)} conversation turns")
        return turns
    
    def analyze_turn_patterns(self, turns: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze patterns in conversation turns"""
        if not turns:
            return {}
        
        # Basic turn statistics
        turn_durations = [turn['duration_minutes'] for turn in turns]
        turn_message_counts = [turn['message_count'] for turn in turns]
        turn_participant_counts = [len(turn['participants']) for turn in turns]
        
        # Time distribution of turns
        turn_starts = [turn['start_time'] for turn in turns]
        turn_hours = [t.hour for t in turn_starts]
        turn_weekdays = [t.weekday() for t in turn_starts]
        
        # Participant patterns
        all_participants = set()
        for turn in turns:
            all_participants.update(turn['participants'])
        
        # Turn transitions (who initiates conversations)
        initiators = [turn['messages'][0]['user'] if turn['messages'] else None for turn in turns]
        initiator_counts = {}
        for initiator in initiators:
            if initiator:
                initiator_counts[initiator] = initiator_counts.get(initiator, 0) + 1
        
        # Response patterns
        response_patterns = self._analyze_response_patterns(turns)
        
        weekday_names = ['월요일', '화요일', '수요일', '목요일', '금요일', '토요일', '일요일']
        
        return {
            'total_turns': len(turns),
            'duration_stats': {
                'avg_duration_minutes': round(np.mean(turn_durations), 2),
                'median_duration_minutes': round(np.median(turn_durations), 2),
                'max_duration_minutes': round(max(turn_durations), 2),
                'min_duration_minutes': round(min(turn_durations), 2)
            },
            'message_stats': {
                'avg_messages_per_turn': round(np.mean(turn_message_counts), 2),
                'median_messages_per_turn': int(np.median(turn_message_counts)),
                'max_messages_per_turn': max(turn_message_counts),
                'min_messages_per_turn': min(turn_message_counts)
            },
            'participant_stats': {
                'avg_participants_per_turn': round(np.mean(turn_participant_counts), 2),
                'total_unique_participants': len(all_participants),
                'participant_list': list(all_participants)
            },
            'temporal_distribution': {
                'by_hour': {f"{h:02d}": turn_hours.count(h) for h in range(24)},
                'by_weekday': {weekday_names[i]: turn_weekdays.count(i) for i in range(7)}
            },
            'conversation_initiators': initiator_counts,
            'response_patterns': response_patterns
        }
    
    def _analyze_response_patterns(self, turns: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze response patterns within turns"""
        
        quick_responses = []  # Responses within 1 minute
        delayed_responses = []  # Responses after 10 minutes
        speaker_changes = 0
        monologues = 0  # Turns with only one speaker
        
        for turn in turns:
            if len(turn['messages']) < 2:
                continue
            
            if len(turn['participants']) == 1:
                monologues += 1
                continue
            
            # Analyze response times within turn
            messages = turn['messages']
            for i in range(1, len(messages)):
                prev_msg = messages[i-1]
                curr_msg = messages[i]
                
                # Count speaker changes
                if prev_msg['user'] != curr_msg['user']:
                    speaker_changes += 1
                    
                    # Calculate response time
                    response_time = (curr_msg['datetime'] - prev_msg['datetime']).total_seconds() / 60
                    
                    if response_time <= 1:
                        quick_responses.append(response_time)
                    elif response_time >= 10:
                        delayed_responses.append(response_time)
        
        return {
            'total_speaker_changes': speaker_changes,
            'monologue_turns': monologues,
            'quick_responses': {
                'count': len(quick_responses),
                'avg_seconds': round(np.mean(quick_responses) * 60, 1) if quick_responses else 0
            },
            'delayed_responses': {
                'count': len(delayed_responses),
                'avg_minutes': round(np.mean(delayed_responses), 1) if delayed_responses else 0
            },
            'interaction_rate': round(speaker_changes / len(turns), 2) if turns else 0
        }
    
    def export_turns(self, turns: List[Dict[str, Any]]) -> pd.DataFrame:
        """Export turns data to DataFrame"""
        
        turn_records = []
        for turn in turns:
            turn_records.append({
                'turn_id': turn['turn_id'],
                'start_time': turn['start_time'],
                'end_time': turn['end_time'],
                'duration_minutes': round(turn['duration_minutes'], 2),
                'message_count': turn['message_count'],
                'participant_count': len(turn['participants']),
                'participants': ', '.join(sorted(turn['participants'])),
                'first_message': turn['messages'][0]['message'][:100] + '...' if turn['messages'] and len(turn['messages'][0]['message']) > 100 else turn['messages'][0]['message'] if turn['messages'] else '',
                'initiator': turn['messages'][0]['user'] if turn['messages'] else None
            })
        
        return pd.DataFrame(turn_records)
    
    def get_conversation_threads(self, turns: List[Dict[str, Any]], min_messages: int = 5) -> List[Dict[str, Any]]:
        """Identify longer conversation threads from turns"""
        
        threads = []
        current_thread = None
        thread_id = 0
        
        for turn in turns:
            # Start new thread if this is a significant turn
            if turn['message_count'] >= min_messages or turn['duration_minutes'] >= 30:
                if current_thread:
                    threads.append(current_thread)
                
                current_thread = {
                    'thread_id': thread_id,
                    'start_time': turn['start_time'],
                    'end_time': turn['end_time'],
                    'turns': [turn],
                    'total_messages': turn['message_count'],
                    'all_participants': set(turn['participants']),
                    'duration_minutes': turn['duration_minutes']
                }
                thread_id += 1
            
            # Extend current thread if within reasonable time gap
            elif current_thread:
                time_gap = (turn['start_time'] - current_thread['end_time']).total_seconds() / 60
                
                if time_gap <= self.window_minutes * 2:  # Allow longer gaps for threads
                    current_thread['turns'].append(turn)
                    current_thread['end_time'] = turn['end_time']
                    current_thread['total_messages'] += turn['message_count']
                    current_thread['all_participants'].update(turn['participants'])
                    current_thread['duration_minutes'] = (current_thread['end_time'] - current_thread['start_time']).total_seconds() / 60
                else:
                    # Gap too large, finalize current thread and start new one
                    threads.append(current_thread)
                    current_thread = None
        
        # Add last thread
        if current_thread:
            threads.append(current_thread)
        
        # Convert participants set to list
        for thread in threads:
            thread['all_participants'] = list(thread['all_participants'])
        
        self.logger.info(f"Identified {len(threads)} conversation threads")
        return threads