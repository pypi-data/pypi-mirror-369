"""Topic-level sentiment and context analysis"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
import logging
import re
from collections import Counter, defaultdict


class TopicSentimentAnalyzer:
    """Analyze sentiment and context for entire topic segments"""
    
    def __init__(self, logger: logging.Logger = None):
        self.logger = logger or logging.getLogger(__name__)
        
        # Korean sentiment keywords
        self.positive_keywords = {
            '좋', '최고', '대박', '완전', '진짜', '짱', '멋져', '예쁘', '이쁘', '사랑',
            '행복', '기쁘', '즐거', '웃', 'ㅋㅋ', 'ㅎㅎ', '감사', '고마', '축하',
            '성공', '잘했', '훌륭', '완벽', '만족', '재밌', '신나', '좋아'
        }
        
        self.negative_keywords = {
            '싫', '짜증', '화나', '슬프', '우울', '힘들', '어려', '안돼', '못해', '실패',
            '걱정', '불안', '스트레스', '피곤', '지쳐', '답답', '귀찮', '빡쳐', 
            '미안', '죄송', '에러', '오류', '문제', 'ㅠㅠ', 'ㅜㅜ', '헐', '망했'
        }
        
        self.neutral_keywords = {
            '그냥', '보통', '괜찮', '음', '아', '네', '예', '알겠', '이해', '생각',
            '계획', '예정', '일단', '먼저', '다음', '나중', '지금', '오늘', '내일'
        }
        
        # Conversation context patterns
        self.context_patterns = {
            'discussion': ['의견', '생각', '어떻게', '토론', '논의', '말해', '설명'],
            'planning': ['계획', '예정', '준비', '미리', '일정', '스케줄', '언제'],
            'problem_solving': ['문제', '해결', '방법', '어떻게', '도움', '도와', '조언'],
            'casual_chat': ['그냥', '별로', '뭐해', '어디', '누구', '언제', '왜'],
            'emotional_support': ['힘들', '괜찮', '걱정', '위로', '응원', '화이팅', '이해'],
            'information_sharing': ['알려', '정보', '소식', '뉴스', '들었', '봤어', '보니']
        }
    
    def analyze_topic_segments_sentiment(self, topic_segments: List[Dict], 
                                       df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze sentiment for each topic segment"""
        
        self.logger.info("Analyzing topic-level sentiment...")
        
        if not topic_segments:
            return {
                'total_segments': 0,
                'sentiment_distribution': {},
                'segment_analysis': [],
                'overall_mood': 'neutral'
            }
        
        segment_analyses = []
        sentiment_counts = {'positive': 0, 'negative': 0, 'neutral': 0}
        
        for i, segment in enumerate(topic_segments):
            # Get messages for this segment
            start_time = pd.to_datetime(segment['start_time'])
            end_time = pd.to_datetime(segment['end_time'])
            
            segment_messages = df[
                (df['datetime'] >= start_time) & 
                (df['datetime'] <= end_time)
            ].copy()
            
            if segment_messages.empty:
                continue
            
            # Analyze this segment
            segment_analysis = self._analyze_single_segment(segment, segment_messages)
            segment_analysis['segment_id'] = i
            segment_analyses.append(segment_analysis)
            
            # Count overall sentiment
            sentiment_counts[segment_analysis['overall_sentiment']] += 1
        
        # Calculate overall statistics
        total_segments = len(segment_analyses)
        
        if total_segments > 0:
            sentiment_distribution = {
                sentiment: count / total_segments * 100 
                for sentiment, count in sentiment_counts.items()
            }
            
            # Determine overall mood
            max_sentiment = max(sentiment_counts.items(), key=lambda x: x[1])
            overall_mood = max_sentiment[0]
        else:
            sentiment_distribution = {'positive': 0, 'negative': 0, 'neutral': 0}
            overall_mood = 'neutral'
        
        return {
            'total_segments': total_segments,
            'sentiment_distribution': sentiment_distribution,
            'segment_analysis': segment_analyses,
            'overall_mood': overall_mood,
            'mood_transitions': self._analyze_mood_transitions(segment_analyses),
            'context_patterns': self._analyze_context_patterns(segment_analyses)
        }
    
    def _analyze_single_segment(self, segment: Dict, messages: pd.DataFrame) -> Dict[str, Any]:
        """Analyze sentiment and context for a single topic segment"""
        
        # Combine all messages in segment
        all_text = ' '.join(messages['message'].astype(str))
        
        # Basic sentiment analysis
        sentiment_scores = self._calculate_sentiment_scores(all_text)
        overall_sentiment = max(sentiment_scores.items(), key=lambda x: x[1])[0]
        
        # Context analysis
        context_type = self._determine_context_type(all_text)
        
        # Participation analysis
        user_participation = messages['user'].value_counts().to_dict()
        dominant_users = list(user_participation.keys())[:3]
        
        # Message pattern analysis
        message_patterns = self._analyze_message_patterns(messages)
        
        # Emotional intensity
        emotional_intensity = self._calculate_emotional_intensity(all_text)
        
        # Key phrases for this segment
        key_phrases = self._extract_key_phrases(all_text)
        
        return {
            'start_time': segment['start_time'],
            'end_time': segment['end_time'],
            'duration_minutes': segment.get('duration_minutes', 0),
            'message_count': len(messages),
            'participant_count': messages['user'].nunique(),
            'dominant_users': dominant_users,
            'overall_sentiment': overall_sentiment,
            'sentiment_scores': sentiment_scores,
            'context_type': context_type,
            'emotional_intensity': emotional_intensity,
            'message_patterns': message_patterns,
            'key_phrases': key_phrases,
            'summary': segment.get('summary', 'No summary available')
        }
    
    def _calculate_sentiment_scores(self, text: str) -> Dict[str, float]:
        """Calculate sentiment scores for text"""
        
        text_lower = text.lower()
        
        # Count sentiment keywords
        positive_count = sum(1 for word in self.positive_keywords if word in text_lower)
        negative_count = sum(1 for word in self.negative_keywords if word in text_lower)
        neutral_count = sum(1 for word in self.neutral_keywords if word in text_lower)
        
        total_count = positive_count + negative_count + neutral_count
        
        if total_count == 0:
            return {'positive': 0.33, 'negative': 0.33, 'neutral': 0.34}
        
        return {
            'positive': positive_count / total_count,
            'negative': negative_count / total_count,
            'neutral': neutral_count / total_count
        }
    
    def _determine_context_type(self, text: str) -> str:
        """Determine the main context type of the conversation"""
        
        text_lower = text.lower()
        context_scores = {}
        
        for context, keywords in self.context_patterns.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            context_scores[context] = score
        
        if not context_scores or max(context_scores.values()) == 0:
            return 'casual_chat'
        
        return max(context_scores.items(), key=lambda x: x[1])[0]
    
    def _calculate_emotional_intensity(self, text: str) -> float:
        """Calculate emotional intensity of the conversation"""
        
        # Count emotional indicators
        intensity_indicators = [
            r'!+',  # Multiple exclamation marks
            r'\?+',  # Multiple question marks
            r'ㅋ{3,}',  # Extended laughter
            r'ㅠ{3,}',  # Extended crying
            r'완전', '진짜', '대박', '헐', '와',  # Intensity words
            r'[😀-🙏]{2,}'  # Multiple emojis
        ]
        
        intensity_count = 0
        for pattern in intensity_indicators:
            if isinstance(pattern, str) and not pattern.startswith(r'['):
                intensity_count += text.lower().count(pattern)
            else:
                intensity_count += len(re.findall(pattern, text))
        
        # Normalize by text length
        text_length = len(text.split())
        if text_length == 0:
            return 0.0
        
        return min(intensity_count / text_length * 10, 1.0)  # Scale to 0-1
    
    def _analyze_message_patterns(self, messages: pd.DataFrame) -> Dict[str, Any]:
        """Analyze message patterns within the segment"""
        
        if messages.empty:
            return {}
        
        # Message length patterns
        msg_lengths = messages['message_length']
        
        # Response patterns
        response_times = []
        for i in range(1, len(messages)):
            time_diff = (messages.iloc[i]['datetime'] - messages.iloc[i-1]['datetime']).total_seconds() / 60
            response_times.append(time_diff)
        
        # User switching patterns
        user_switches = 0
        if len(messages) > 1:
            for i in range(1, len(messages)):
                if messages.iloc[i]['user'] != messages.iloc[i-1]['user']:
                    user_switches += 1
        
        return {
            'avg_message_length': float(msg_lengths.mean()) if not msg_lengths.empty else 0,
            'message_length_std': float(msg_lengths.std()) if not msg_lengths.empty else 0,
            'avg_response_time_minutes': np.mean(response_times) if response_times else 0,
            'user_switches': user_switches,
            'engagement_level': user_switches / max(len(messages) - 1, 1) if len(messages) > 1 else 0
        }
    
    def _extract_key_phrases(self, text: str) -> List[str]:
        """Extract key phrases that characterize the topic"""
        
        # Simple keyword extraction for Korean
        korean_words = re.findall(r'[가-힣]{2,}', text)
        
        # Filter out common words
        common_words = {
            '그냥', '그런데', '근데', '그래서', '그리고', '하지만', '그런', '이런', 
            '저런', '아니', '진짜', '정말', '완전', '너무', '되게', '엄청', '좀', '좀'
        }
        
        filtered_words = [word for word in korean_words 
                         if word not in common_words and len(word) >= 2]
        
        # Get most common words
        word_counts = Counter(filtered_words)
        key_phrases = [word for word, count in word_counts.most_common(5) if count >= 2]
        
        return key_phrases
    
    def _analyze_mood_transitions(self, segment_analyses: List[Dict]) -> Dict[str, Any]:
        """Analyze how mood transitions between segments"""
        
        if len(segment_analyses) < 2:
            return {'transitions': [], 'stability': 1.0}
        
        transitions = []
        mood_changes = 0
        
        for i in range(1, len(segment_analyses)):
            prev_mood = segment_analyses[i-1]['overall_sentiment']
            curr_mood = segment_analyses[i]['overall_sentiment']
            
            transition = {
                'from_segment': i-1,
                'to_segment': i,
                'from_mood': prev_mood,
                'to_mood': curr_mood,
                'is_change': prev_mood != curr_mood
            }
            transitions.append(transition)
            
            if prev_mood != curr_mood:
                mood_changes += 1
        
        stability = 1.0 - (mood_changes / len(transitions)) if transitions else 1.0
        
        return {
            'transitions': transitions,
            'total_changes': mood_changes,
            'stability': stability,
            'most_common_transition': self._find_most_common_transition(transitions)
        }
    
    def _find_most_common_transition(self, transitions: List[Dict]) -> Optional[str]:
        """Find the most common type of mood transition"""
        
        if not transitions:
            return None
        
        transition_types = []
        for trans in transitions:
            if trans['is_change']:
                transition_types.append(f"{trans['from_mood']} → {trans['to_mood']}")
        
        if not transition_types:
            return "stable mood"
        
        transition_counts = Counter(transition_types)
        return transition_counts.most_common(1)[0][0]
    
    def _analyze_context_patterns(self, segment_analyses: List[Dict]) -> Dict[str, Any]:
        """Analyze patterns in conversation contexts"""
        
        if not segment_analyses:
            return {}
        
        context_counts = Counter(seg['context_type'] for seg in segment_analyses)
        
        # Context transitions
        context_transitions = []
        if len(segment_analyses) > 1:
            for i in range(1, len(segment_analyses)):
                prev_context = segment_analyses[i-1]['context_type']
                curr_context = segment_analyses[i]['context_type']
                if prev_context != curr_context:
                    context_transitions.append(f"{prev_context} → {curr_context}")
        
        context_transition_counts = Counter(context_transitions)
        
        # Average emotional intensity by context
        context_intensities = defaultdict(list)
        for seg in segment_analyses:
            context_intensities[seg['context_type']].append(seg['emotional_intensity'])
        
        avg_intensities = {
            context: np.mean(intensities) 
            for context, intensities in context_intensities.items()
        }
        
        return {
            'context_distribution': dict(context_counts),
            'most_common_context': context_counts.most_common(1)[0][0] if context_counts else None,
            'context_transitions': dict(context_transition_counts),
            'avg_intensity_by_context': avg_intensities
        }
    
    def generate_topic_sentiment_insights(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate human-readable insights from topic sentiment analysis"""
        
        insights = []
        
        total_segments = analysis.get('total_segments', 0)
        if total_segments == 0:
            insights.append("분석할 수 있는 토픽 세그먼트가 없습니다")
            return insights
        
        # Overall mood
        overall_mood = analysis.get('overall_mood', 'neutral')
        sentiment_dist = analysis.get('sentiment_distribution', {})
        
        mood_names = {
            'positive': '긍정적',
            'negative': '부정적', 
            'neutral': '중립적'
        }
        
        insights.append(f"전체 {total_segments}개 토픽 중 {mood_names.get(overall_mood, overall_mood)} 분위기가 주를 이룸")
        
        if sentiment_dist:
            pos_pct = sentiment_dist.get('positive', 0)
            neg_pct = sentiment_dist.get('negative', 0)
            
            if pos_pct > 60:
                insights.append(f"대화의 {pos_pct:.1f}%가 긍정적 분위기로 매우 밝은 대화")
            elif neg_pct > 40:
                insights.append(f"대화의 {neg_pct:.1f}%가 부정적 분위기로 다소 무거운 주제들")
        
        # Mood transitions
        mood_transitions = analysis.get('mood_transitions', {})
        stability = mood_transitions.get('stability', 1.0)
        
        if stability > 0.8:
            insights.append("토픽별 감정 변화가 적어 안정적인 대화 흐름")
        elif stability < 0.5:
            insights.append("토픽별 감정 변화가 잦아 역동적인 대화 흐름")
        
        # Context patterns
        context_patterns = analysis.get('context_patterns', {})
        most_common_context = context_patterns.get('most_common_context')
        
        context_names = {
            'discussion': '토론/논의',
            'planning': '계획 수립',
            'problem_solving': '문제 해결',
            'casual_chat': '일상 대화',
            'emotional_support': '감정적 지지',
            'information_sharing': '정보 공유'
        }
        
        if most_common_context:
            korean_context = context_names.get(most_common_context, most_common_context)
            insights.append(f"주된 대화 맥락: {korean_context}")
        
        return insights