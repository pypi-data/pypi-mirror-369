"""Advanced mood and emotion analysis for conversations"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
import logging
from collections import Counter, defaultdict
import re
from datetime import datetime, timedelta


class ConversationMoodAnalyzer:
    """Analyze conversation mood, emotional patterns and social dynamics"""
    
    def __init__(self, config, logger: Optional[logging.Logger] = None):
        self.config = config
        self.logger = logger or logging.getLogger(__name__)
        
        # Korean emotion patterns
        self.emotion_patterns = {
            'joy': {
                'patterns': [r'ㅋㅋ+', r'ㅎㅎ+', r'하하+', r'좋[다네요]', r'기쁘', r'행복', r'즐거', r'신나', r'최고', r'대박', r'완전'],
                'weight': 1.0
            },
            'sadness': {
                'patterns': [r'ㅠㅠ+', r'ㅜㅜ+', r'슬프', r'우울', r'힘들', r'아쉽', r'실망', r'후회', r'눈물'],
                'weight': -1.0
            },
            'anger': {
                'patterns': [r'짜증', r'화나', r'열받', r'미쳐', r'아니', r'진짜\s*[짜증화]', r'개[짜증빡]', r'어이없'],
                'weight': -1.5
            },
            'surprise': {
                'patterns': [r'헉', r'어\?+', r'와+', r'진짜\?+', r'정말\?+', r'어머', r'깜짝', r'놀랐'],
                'weight': 0.5
            },
            'fear': {
                'patterns': [r'무서', r'두려', r'걱정', r'불안', r'떨려'],
                'weight': -0.8
            },
            'love': {
                'patterns': [r'사랑', r'♥+', r'❤+', r'좋아', r'최고', r'완전\s*좋', r'너무\s*좋'],
                'weight': 1.2
            }
        }
        
        # Energy level indicators
        self.energy_patterns = {
            'high': [r'!{2,}', r'[ㅋㅎ]{3,}', r'완전', r'진짜', r'대박', r'엄청', r'너무'],
            'low': [r'\.{2,}', r'그냥', r'뭔가', r'약간', r'좀'],
        }
        
        # Social cues
        self.social_patterns = {
            'supportive': [r'화이팅', r'괜찮', r'잘\s*될', r'힘내', r'응원', r'수고'],
            'questioning': [r'\?+', r'왜', r'뭐', r'어떻', r'언제', r'어디', r'누구'],
            'agreeing': [r'^네+$', r'^응+$', r'^맞', r'그래', r'인정', r'동감'],
            'disagreeing': [r'아니', r'근데', r'하지만', r'그런데']
        }
    
    def analyze_conversation_mood(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze overall conversation mood patterns"""
        
        self.logger.info("Analyzing conversation mood patterns...")
        
        # Message-level emotion analysis
        message_emotions = self._analyze_message_emotions(df)
        
        # Temporal mood analysis
        temporal_moods = self._analyze_temporal_moods(df, message_emotions)
        
        # User mood profiles
        user_mood_profiles = self._analyze_user_mood_profiles(df, message_emotions)
        
        # Mood contagion analysis
        mood_contagion = self._analyze_mood_contagion(df, message_emotions)
        
        # Energy level analysis
        energy_analysis = self._analyze_energy_levels(df)
        
        # Social dynamics
        social_dynamics = self._analyze_social_dynamics(df)
        
        return {
            'message_emotions': message_emotions,
            'temporal_moods': temporal_moods,
            'user_mood_profiles': user_mood_profiles,
            'mood_contagion': mood_contagion,
            'energy_analysis': energy_analysis,
            'social_dynamics': social_dynamics,
            'overall_sentiment': self._calculate_overall_sentiment(message_emotions),
            'mood_summary': self._generate_mood_summary(temporal_moods, user_mood_profiles)
        }
    
    def _analyze_message_emotions(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Analyze emotions in each message"""
        
        emotions_list = []
        
        for idx, row in df.iterrows():
            message = str(row['message']).lower()
            user = row['user']
            timestamp = row['datetime']
            
            emotion_scores = {}
            detected_patterns = []
            
            # Check each emotion pattern
            for emotion, config in self.emotion_patterns.items():
                score = 0
                matches = []
                
                for pattern in config['patterns']:
                    pattern_matches = re.findall(pattern, message)
                    if pattern_matches:
                        score += len(pattern_matches) * config['weight']
                        matches.extend(pattern_matches)
                
                if score != 0:
                    emotion_scores[emotion] = score
                    detected_patterns.extend(matches)
            
            # Determine dominant emotion
            dominant_emotion = None
            max_score = 0
            if emotion_scores:
                dominant_emotion = max(emotion_scores.items(), key=lambda x: abs(x[1]))[0]
                max_score = emotion_scores[dominant_emotion]
            
            emotions_list.append({
                'message_idx': idx,
                'user': user,
                'timestamp': timestamp,
                'message': row['message'],
                'emotion_scores': emotion_scores,
                'dominant_emotion': dominant_emotion,
                'emotion_intensity': abs(max_score) if max_score else 0,
                'sentiment_polarity': max_score if max_score else 0,
                'detected_patterns': detected_patterns
            })
        
        return emotions_list
    
    def _analyze_temporal_moods(self, df: pd.DataFrame, message_emotions: List[Dict]) -> Dict[str, Any]:
        """Analyze how mood changes over time"""
        
        if not message_emotions:
            return {}
        
        # Hourly mood patterns
        hourly_moods = defaultdict(list)
        daily_moods = defaultdict(list)
        
        for emotion_data in message_emotions:
            hour = emotion_data['timestamp'].hour
            date = emotion_data['timestamp'].date()
            sentiment = emotion_data['sentiment_polarity']
            
            hourly_moods[hour].append(sentiment)
            daily_moods[date].append(sentiment)
        
        # Calculate averages
        hourly_sentiment = {
            hour: np.mean(sentiments) if sentiments else 0 
            for hour, sentiments in hourly_moods.items()
        }
        
        daily_sentiment = {
            str(date): np.mean(sentiments) if sentiments else 0
            for date, sentiments in daily_moods.items()
        }
        
        # Find mood peaks
        peak_positive_hour = max(hourly_sentiment.items(), key=lambda x: x[1])[0]
        peak_negative_hour = min(hourly_sentiment.items(), key=lambda x: x[1])[0]
        
        return {
            'hourly_sentiment': hourly_sentiment,
            'daily_sentiment': daily_sentiment,
            'peak_positive_hour': peak_positive_hour,
            'peak_negative_hour': peak_negative_hour,
            'mood_volatility': np.std(list(hourly_sentiment.values())),
            'happiest_day': max(daily_sentiment.items(), key=lambda x: x[1])[0] if daily_sentiment else None,
            'saddest_day': min(daily_sentiment.items(), key=lambda x: x[1])[0] if daily_sentiment else None
        }
    
    def _analyze_user_mood_profiles(self, df: pd.DataFrame, message_emotions: List[Dict]) -> Dict[str, Any]:
        """Create mood profiles for each user"""
        
        user_emotions = defaultdict(list)
        
        for emotion_data in message_emotions:
            user = emotion_data['user']
            user_emotions[user].append(emotion_data)
        
        user_profiles = {}
        
        for user, emotions in user_emotions.items():
            sentiments = [e['sentiment_polarity'] for e in emotions]
            dominant_emotions = [e['dominant_emotion'] for e in emotions if e['dominant_emotion']]
            
            emotion_counts = Counter(dominant_emotions)
            avg_sentiment = np.mean(sentiments) if sentiments else 0
            sentiment_std = np.std(sentiments) if sentiments else 0
            
            # Personality insights
            personality_traits = []
            if avg_sentiment > 0.5:
                personality_traits.append("긍정적")
            elif avg_sentiment < -0.5:
                personality_traits.append("부정적")
            else:
                personality_traits.append("중성적")
            
            if sentiment_std > 1.0:
                personality_traits.append("감정기복이 있는")
            else:
                personality_traits.append("안정적인")
            
            if 'joy' in emotion_counts and emotion_counts['joy'] > len(emotions) * 0.3:
                personality_traits.append("유머러스한")
            
            user_profiles[user] = {
                'message_count': len(emotions),
                'avg_sentiment': avg_sentiment,
                'sentiment_volatility': sentiment_std,
                'dominant_emotions': dict(emotion_counts.most_common(3)),
                'personality_traits': personality_traits,
                'most_positive_message': max(emotions, key=lambda x: x['sentiment_polarity']) if emotions else None,
                'most_negative_message': min(emotions, key=lambda x: x['sentiment_polarity']) if emotions else None
            }
        
        return user_profiles
    
    def _analyze_mood_contagion(self, df: pd.DataFrame, message_emotions: List[Dict]) -> Dict[str, Any]:
        """Analyze how moods spread between users"""
        
        if len(message_emotions) < 2:
            return {}
        
        contagion_events = []
        
        for i in range(1, len(message_emotions)):
            current = message_emotions[i]
            previous = message_emotions[i-1]
            
            # Check if different users
            if current['user'] != previous['user']:
                # Check if sentiment changed in same direction
                curr_sentiment = current['sentiment_polarity']
                prev_sentiment = previous['sentiment_polarity']
                
                if abs(curr_sentiment) > 0 and abs(prev_sentiment) > 0:
                    if (curr_sentiment > 0) == (prev_sentiment > 0):
                        # Same polarity - potential contagion
                        time_diff = (current['timestamp'] - previous['timestamp']).total_seconds() / 60
                        
                        if time_diff < 5:  # Within 5 minutes
                            contagion_events.append({
                                'source_user': previous['user'],
                                'target_user': current['user'],
                                'emotion_type': 'positive' if curr_sentiment > 0 else 'negative',
                                'strength': min(abs(curr_sentiment), abs(prev_sentiment)),
                                'time_lag_minutes': time_diff
                            })
        
        # Analyze contagion patterns
        contagion_network = defaultdict(lambda: defaultdict(int))
        for event in contagion_events:
            contagion_network[event['source_user']][event['target_user']] += 1
        
        return {
            'contagion_events': contagion_events,
            'contagion_network': dict(contagion_network),
            'most_influential_user': max(contagion_network.items(), key=lambda x: sum(x[1].values()))[0] if contagion_network else None,
            'contagion_rate': len(contagion_events) / max(1, len(message_emotions) - 1)
        }
    
    def _analyze_energy_levels(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze energy levels in conversations"""
        
        high_energy_count = 0
        low_energy_count = 0
        user_energy = defaultdict(list)
        
        for _, row in df.iterrows():
            message = str(row['message'])
            user = row['user']
            
            energy_score = 0
            
            # Check high energy patterns
            for pattern in self.energy_patterns['high']:
                matches = len(re.findall(pattern, message))
                energy_score += matches * 0.5
            
            # Check low energy patterns  
            for pattern in self.energy_patterns['low']:
                matches = len(re.findall(pattern, message))
                energy_score -= matches * 0.3
            
            if energy_score > 0.5:
                high_energy_count += 1
            elif energy_score < -0.5:
                low_energy_count += 1
            
            user_energy[user].append(energy_score)
        
        # Calculate user average energies
        user_avg_energy = {
            user: np.mean(scores) for user, scores in user_energy.items()
        }
        
        return {
            'high_energy_messages': high_energy_count,
            'low_energy_messages': low_energy_count,
            'energy_ratio': high_energy_count / max(1, low_energy_count),
            'user_energy_levels': user_avg_energy,
            'most_energetic_user': max(user_avg_energy.items(), key=lambda x: x[1])[0] if user_avg_energy else None,
            'least_energetic_user': min(user_avg_energy.items(), key=lambda x: x[1])[0] if user_avg_energy else None
        }
    
    def _analyze_social_dynamics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze social interaction patterns"""
        
        user_interactions = defaultdict(lambda: defaultdict(int))
        social_behaviors = defaultdict(lambda: defaultdict(int))
        
        for _, row in df.iterrows():
            message = str(row['message']).lower()
            user = row['user']
            
            # Check social patterns
            for behavior, patterns in self.social_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, message):
                        social_behaviors[user][behavior] += 1
        
        # Calculate social roles
        user_roles = {}
        for user, behaviors in social_behaviors.items():
            total_messages = df[df['user'] == user].shape[0]
            
            roles = []
            if behaviors['supportive'] / total_messages > 0.1:
                roles.append("지지하는")
            if behaviors['questioning'] / total_messages > 0.2:
                roles.append("궁금한")  
            if behaviors['agreeing'] / total_messages > 0.15:
                roles.append("동조하는")
            if behaviors['disagreeing'] / total_messages > 0.1:
                roles.append("비판적인")
            
            user_roles[user] = roles if roles else ["중립적인"]
        
        return {
            'social_behaviors': dict(social_behaviors),
            'user_social_roles': user_roles,
            'most_supportive_user': self._find_most_supportive_user(social_behaviors),
            'most_inquisitive_user': self._find_most_inquisitive_user(social_behaviors)
        }
    
    def _find_most_supportive_user(self, social_behaviors: Dict) -> Optional[str]:
        max_support = 0
        most_supportive = None
        
        for user, behaviors in social_behaviors.items():
            support_count = behaviors.get('supportive', 0)
            if support_count > max_support:
                max_support = support_count
                most_supportive = user
        
        return most_supportive
    
    def _find_most_inquisitive_user(self, social_behaviors: Dict) -> Optional[str]:
        max_questions = 0
        most_inquisitive = None
        
        for user, behaviors in social_behaviors.items():
            question_count = behaviors.get('questioning', 0)
            if question_count > max_questions:
                max_questions = question_count
                most_inquisitive = user
        
        return most_inquisitive
    
    def _calculate_overall_sentiment(self, message_emotions: List[Dict]) -> Dict[str, Any]:
        """Calculate overall conversation sentiment"""
        
        if not message_emotions:
            return {}
        
        sentiments = [e['sentiment_polarity'] for e in message_emotions]
        positive_count = sum(1 for s in sentiments if s > 0)
        negative_count = sum(1 for s in sentiments if s < 0)
        neutral_count = len(sentiments) - positive_count - negative_count
        
        return {
            'average_sentiment': np.mean(sentiments),
            'sentiment_std': np.std(sentiments),
            'positive_ratio': positive_count / len(sentiments),
            'negative_ratio': negative_count / len(sentiments),
            'neutral_ratio': neutral_count / len(sentiments),
            'sentiment_trend': 'positive' if np.mean(sentiments) > 0.1 else 'negative' if np.mean(sentiments) < -0.1 else 'neutral'
        }
    
    def _generate_mood_summary(self, temporal_moods: Dict, user_mood_profiles: Dict) -> Dict[str, Any]:
        """Generate a summary of conversation mood insights"""
        
        insights = []
        
        # Temporal insights
        if temporal_moods:
            peak_hour = temporal_moods.get('peak_positive_hour')
            if peak_hour is not None:
                insights.append(f"대화가 가장 긍정적인 시간대는 {peak_hour}시입니다")
            
            if temporal_moods.get('mood_volatility', 0) > 1.0:
                insights.append("대화 중 감정 변화가 활발합니다")
        
        # User insights
        if user_mood_profiles:
            most_positive_user = max(
                user_mood_profiles.items(),
                key=lambda x: x[1]['avg_sentiment']
            )[0]
            insights.append(f"{most_positive_user}님이 가장 긍정적인 에너지를 보입니다")
            
            funny_users = [
                user for user, profile in user_mood_profiles.items()
                if 'joy' in profile['dominant_emotions']
            ]
            if funny_users:
                insights.append(f"{', '.join(funny_users[:2])}님이 대화에 유머를 더합니다")
        
        return {
            'key_insights': insights,
            'mood_keywords': self._extract_mood_keywords(user_mood_profiles),
            'conversation_atmosphere': self._assess_atmosphere(temporal_moods, user_mood_profiles)
        }
    
    def _extract_mood_keywords(self, user_mood_profiles: Dict) -> List[str]:
        """Extract key mood-related keywords"""
        
        all_emotions = []
        for profile in user_mood_profiles.values():
            all_emotions.extend(profile['dominant_emotions'].keys())
        
        emotion_counter = Counter(all_emotions)
        return [emotion for emotion, count in emotion_counter.most_common(3)]
    
    def _assess_atmosphere(self, temporal_moods: Dict, user_mood_profiles: Dict) -> str:
        """Assess overall conversation atmosphere"""
        
        if not temporal_moods or not user_mood_profiles:
            return "중성적"
        
        avg_sentiments = [
            profile['avg_sentiment'] 
            for profile in user_mood_profiles.values()
        ]
        
        overall_sentiment = np.mean(avg_sentiments)
        
        if overall_sentiment > 0.5:
            return "활기찬"
        elif overall_sentiment > 0:
            return "긍정적"
        elif overall_sentiment > -0.5:
            return "중성적"
        else:
            return "우울한"