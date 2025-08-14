"""KakaoTalk mention (@) analysis functionality"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Tuple
import logging
import re
from collections import defaultdict, Counter


class KakaoTalkMentionAnalyzer:
    """Analyze KakaoTalk mention patterns using @ symbol"""
    
    def __init__(self, logger: logging.Logger = None):
        self.logger = logger or logging.getLogger(__name__)
        
        # Mention patterns for KakaoTalk
        self.mention_patterns = [
            r'@([가-힣a-zA-Z0-9_]+)',  # @username (Korean + English + numbers)
            r'@\s*([가-힣a-zA-Z0-9_\s]+?)(?:\s|$|[^\w가-힣])',  # @username with spaces
        ]
    
    def analyze_mentions(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze mention patterns in conversation"""
        
        self.logger.info("Analyzing mention patterns...")
        
        # Extract all mentions with context
        mentions_data = self._extract_mentions_with_context(df)
        
        # Analyze mention statistics
        mention_stats = self._calculate_mention_statistics(mentions_data, df)
        
        # Analyze mention networks
        mention_networks = self._analyze_mention_networks(mentions_data)
        
        # Analyze mention patterns by time/user
        mention_patterns = self._analyze_mention_patterns(mentions_data, df)
        
        # Analyze mention context and conversation flow
        context_analysis = self._analyze_mention_context_flow(mentions_data, df)
        
        return {
            'mention_statistics': mention_stats,
            'mention_networks': mention_networks,
            'mention_patterns': mention_patterns,
            'context_analysis': context_analysis,
            'raw_mentions': mentions_data[:50],  # Sample of raw mentions for debugging
            'analysis_summary': {
                'total_mentions': len(mentions_data),
                'unique_mentioners': len(set(m['mentioner'] for m in mentions_data)),
                'unique_mentioned': len(set(m['mentioned'] for m in mentions_data)),
                'mention_rate': len(mentions_data) / len(df) * 100 if len(df) > 0 else 0
            }
        }
    
    def _extract_mentions_with_context(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Extract mention data from messages with conversation context"""
        
        mentions = []
        df_sorted = df.sort_values('datetime').reset_index(drop=True)
        
        for idx, row in df_sorted.iterrows():
            message = str(row['message'])
            user = row['user']
            timestamp = row['datetime']
            
            # Try different mention patterns
            for pattern in self.mention_patterns:
                matches = re.findall(pattern, message, re.IGNORECASE)
                
                for mentioned_user in matches:
                    # Clean up the mentioned username
                    mentioned_user = mentioned_user.strip()
                    
                    # Skip if empty or too short
                    if len(mentioned_user) < 2:
                        continue
                    
                    # Skip self-mentions
                    if mentioned_user.lower() == user.lower():
                        continue
                    
                    # Get conversation context (3 messages before and after)
                    context_window = 3
                    context_before = []
                    context_after = []
                    
                    # Messages before
                    for i in range(max(0, idx - context_window), idx):
                        context_before.append({
                            'user': df_sorted.iloc[i]['user'],
                            'message': df_sorted.iloc[i]['message'],
                            'timestamp': df_sorted.iloc[i]['datetime']
                        })
                    
                    # Messages after
                    for i in range(idx + 1, min(len(df_sorted), idx + context_window + 1)):
                        context_after.append({
                            'user': df_sorted.iloc[i]['user'],
                            'message': df_sorted.iloc[i]['message'], 
                            'timestamp': df_sorted.iloc[i]['datetime']
                        })
                    
                    # Analyze if mentioned user responded
                    responded = any(msg['user'] == mentioned_user for msg in context_after)
                    response_time_minutes = None
                    
                    if responded:
                        for msg in context_after:
                            if msg['user'] == mentioned_user:
                                response_time_minutes = (msg['timestamp'] - timestamp).total_seconds() / 60
                                break
                    
                    mentions.append({
                        'mentioner': user,
                        'mentioned': mentioned_user,
                        'message': message,
                        'timestamp': timestamp,
                        'message_id': idx,
                        'context_before': context_before,
                        'context_after': context_after,
                        'mentioned_user_responded': responded,
                        'response_time_minutes': response_time_minutes,
                        'conversation_topic': self._extract_conversation_topic(context_before + [{'user': user, 'message': message, 'timestamp': timestamp}] + context_after)
                    })
        
        return mentions
    
    def _extract_conversation_topic(self, context_messages: List[Dict]) -> str:
        """Extract main topic/keywords from conversation context"""
        
        all_text = ' '.join([msg['message'] for msg in context_messages])
        
        # Extract key Korean words (2+ characters)
        korean_words = re.findall(r'[가-힣]{2,}', all_text)
        
        # Filter out common words
        stop_words = {'것', '수', '있', '없', '하', '되', '이다', '하다', '되다', '아니다', '그런데', '그리고', '하지만', '그래서'}
        filtered_words = [w for w in korean_words if w not in stop_words and len(w) >= 2]
        
        # Get most common words
        from collections import Counter
        common_words = Counter(filtered_words).most_common(3)
        
        return ', '.join([word for word, _ in common_words]) if common_words else '일반 대화'
    
    def _analyze_mention_context_flow(self, mentions_data: List[Dict], df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze conversation flow around mentions"""
        
        if not mentions_data:
            return {'context_patterns': {}, 'response_analysis': {}, 'topic_distribution': {}}
        
        # Response rate analysis
        responded_mentions = [m for m in mentions_data if m['mentioned_user_responded']]
        response_rate = len(responded_mentions) / len(mentions_data) * 100
        
        # Response time analysis
        response_times = [m['response_time_minutes'] for m in responded_mentions if m['response_time_minutes'] is not None]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        # Topic distribution
        topics = [m['conversation_topic'] for m in mentions_data if m['conversation_topic']]
        topic_counts = Counter(topics)
        
        # Mention effectiveness (mentions that got responses)
        effectiveness_by_user = {}
        for mention in mentions_data:
            mentioner = mention['mentioner']
            if mentioner not in effectiveness_by_user:
                effectiveness_by_user[mentioner] = {'total': 0, 'responded': 0}
            effectiveness_by_user[mentioner]['total'] += 1
            if mention['mentioned_user_responded']:
                effectiveness_by_user[mentioner]['responded'] += 1
        
        # Calculate effectiveness rates
        user_effectiveness = []
        for user, stats in effectiveness_by_user.items():
            if stats['total'] >= 3:  # Minimum 3 mentions for meaningful stats
                effectiveness_rate = stats['responded'] / stats['total'] * 100
                user_effectiveness.append({
                    'user': user,
                    'total_mentions': stats['total'],
                    'successful_mentions': stats['responded'],
                    'effectiveness_rate': round(effectiveness_rate, 1)
                })
        
        user_effectiveness.sort(key=lambda x: x['effectiveness_rate'], reverse=True)
        
        # Context pattern analysis
        context_patterns = self._analyze_context_patterns(mentions_data)
        
        return {
            'response_analysis': {
                'overall_response_rate': round(response_rate, 1),
                'average_response_time_minutes': round(avg_response_time, 1),
                'total_mentions': len(mentions_data),
                'mentions_with_response': len(responded_mentions),
                'user_effectiveness': user_effectiveness[:10]
            },
            'topic_distribution': {
                'top_topics': [{'topic': topic, 'count': count} for topic, count in topic_counts.most_common(10)],
                'unique_topics': len(topic_counts)
            },
            'context_patterns': context_patterns
        }
    
    def _analyze_context_patterns(self, mentions_data: List[Dict]) -> Dict[str, Any]:
        """Analyze patterns in conversation context around mentions"""
        
        patterns = {
            'mention_in_question': 0,
            'mention_in_request': 0, 
            'mention_in_greeting': 0,
            'mention_in_discussion': 0,
            'mention_after_silence': 0,  # Mention after long gap in conversation
            'mention_in_group_chat': 0   # Mention when multiple people active
        }
        
        for mention in mentions_data:
            message = mention['message'].lower()
            context_before = mention['context_before']
            context_after = mention['context_after']
            
            # Pattern detection
            if any(char in message for char in ['?', '뭐', '어떻게', '언제', '어디', '왜']):
                patterns['mention_in_question'] += 1
            
            if any(word in message for word in ['해줘', '부탁', '도와', '해달라', '좀']):
                patterns['mention_in_request'] += 1
                
            if any(word in message for word in ['안녕', 'hi', 'hello', 'ㅎㅇ']):
                patterns['mention_in_greeting'] += 1
                
            if any(word in message for word in ['생각', '의견', '어떻게 생각', '말해']):
                patterns['mention_in_discussion'] += 1
            
            # Check if mention comes after conversation silence
            if context_before:
                time_since_last = (mention['timestamp'] - context_before[-1]['timestamp']).total_seconds() / 60
                if time_since_last > 60:  # More than 1 hour gap
                    patterns['mention_after_silence'] += 1
            
            # Check if multiple people were active recently
            if context_before:
                recent_users = set(msg['user'] for msg in context_before[-3:])  # Last 3 messages
                if len(recent_users) >= 2:
                    patterns['mention_in_group_chat'] += 1
        
        total_mentions = len(mentions_data)
        pattern_percentages = {
            pattern: round(count / total_mentions * 100, 1) if total_mentions > 0 else 0
            for pattern, count in patterns.items()
        }
        
        return {
            'pattern_counts': patterns,
            'pattern_percentages': pattern_percentages,
            'most_common_pattern': max(patterns.items(), key=lambda x: x[1])[0] if patterns else None
        }
    
    def _extract_mentions(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Extract mention data from messages"""
        
        mentions = []
        
        for idx, row in df.iterrows():
            message = str(row['message'])
            user = row['user']
            timestamp = row['datetime']
            
            # Try different mention patterns
            for pattern in self.mention_patterns:
                matches = re.findall(pattern, message, re.IGNORECASE)
                
                for mentioned_user in matches:
                    # Clean up the mentioned username
                    mentioned_user = mentioned_user.strip()
                    
                    # Skip if empty or too short
                    if len(mentioned_user) < 2:
                        continue
                    
                    # Skip self-mentions
                    if mentioned_user.lower() == user.lower():
                        continue
                    
                    mentions.append({
                        'mentioner': user,
                        'mentioned': mentioned_user,
                        'message': message,
                        'timestamp': timestamp,
                        'message_id': idx
                    })
        
        return mentions
    
    def _calculate_mention_statistics(self, mentions_data: List[Dict], df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate basic mention statistics"""
        
        if not mentions_data:
            return {
                'total_mentions': 0,
                'mention_rate': 0.0,
                'top_mentioners': [],
                'top_mentioned': [],
                'most_active_pairs': []
            }
        
        # Count mentions by user
        mentioner_counts = Counter(m['mentioner'] for m in mentions_data)
        mentioned_counts = Counter(m['mentioned'] for m in mentions_data)
        
        # Count mention pairs
        pair_counts = Counter((m['mentioner'], m['mentioned']) for m in mentions_data)
        
        return {
            'total_mentions': len(mentions_data),
            'mention_rate': len(mentions_data) / len(df) * 100,
            'top_mentioners': [
                {'user': user, 'count': count, 'percentage': count/len(mentions_data)*100}
                for user, count in mentioner_counts.most_common(10)
            ],
            'top_mentioned': [
                {'user': user, 'count': count, 'percentage': count/len(mentions_data)*100}
                for user, count in mentioned_counts.most_common(10)
            ],
            'most_active_pairs': [
                {
                    'mentioner': pair[0], 
                    'mentioned': pair[1], 
                    'count': count,
                    'percentage': count/len(mentions_data)*100
                }
                for pair, count in pair_counts.most_common(10)
            ]
        }
    
    def _analyze_mention_networks(self, mentions_data: List[Dict]) -> Dict[str, Any]:
        """Analyze mention network patterns"""
        
        if not mentions_data:
            return {'network_density': 0, 'reciprocal_mentions': [], 'mention_clusters': []}
        
        # Build mention graph
        mention_graph = defaultdict(set)
        for mention in mentions_data:
            mention_graph[mention['mentioner']].add(mention['mentioned'])
        
        # Find reciprocal mentions (mutual mentions)
        reciprocal_pairs = []
        processed_pairs = set()
        
        for mentioner, mentioned_users in mention_graph.items():
            for mentioned in mentioned_users:
                pair = tuple(sorted([mentioner, mentioned]))
                if pair in processed_pairs:
                    continue
                processed_pairs.add(pair)
                
                # Check if it's reciprocal
                if mentioned in mention_graph and mentioner in mention_graph[mentioned]:
                    reciprocal_pairs.append({
                        'user1': pair[0],
                        'user2': pair[1],
                        'mentions_1_to_2': sum(1 for m in mentions_data 
                                             if m['mentioner'] == pair[0] and m['mentioned'] == pair[1]),
                        'mentions_2_to_1': sum(1 for m in mentions_data 
                                             if m['mentioner'] == pair[1] and m['mentioned'] == pair[0])
                    })
        
        # Calculate network density
        all_users = set()
        for mention in mentions_data:
            all_users.add(mention['mentioner'])
            all_users.add(mention['mentioned'])
        
        total_possible_connections = len(all_users) * (len(all_users) - 1)
        actual_connections = len(set((m['mentioner'], m['mentioned']) for m in mentions_data))
        network_density = actual_connections / total_possible_connections if total_possible_connections > 0 else 0
        
        return {
            'network_density': network_density,
            'reciprocal_mentions': reciprocal_pairs,
            'total_unique_pairs': actual_connections,
            'total_possible_pairs': total_possible_connections,
            'mention_clusters': self._find_mention_clusters(mention_graph)
        }
    
    def _find_mention_clusters(self, mention_graph: Dict) -> List[Dict[str, Any]]:
        """Find clusters of users who frequently mention each other"""
        
        # Simple clustering based on mutual mentions
        clusters = []
        processed_users = set()
        
        for user, mentioned_users in mention_graph.items():
            if user in processed_users:
                continue
            
            # Find users who mention each other
            cluster_members = {user}
            for mentioned in mentioned_users:
                if mentioned in mention_graph and user in mention_graph[mentioned]:
                    cluster_members.add(mentioned)
            
            if len(cluster_members) >= 2:
                clusters.append({
                    'members': list(cluster_members),
                    'size': len(cluster_members),
                    'internal_mentions': sum(
                        1 for mentioner in cluster_members 
                        for mentioned in mention_graph.get(mentioner, set())
                        if mentioned in cluster_members
                    )
                })
                processed_users.update(cluster_members)
        
        return sorted(clusters, key=lambda x: x['size'], reverse=True)
    
    def _analyze_mention_patterns(self, mentions_data: List[Dict], df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze mention patterns by time and context"""
        
        if not mentions_data:
            return {
                'hourly_distribution': {},
                'daily_distribution': {},
                'mention_context_analysis': {}
            }
        
        # Convert timestamps to pandas datetime
        mention_df = pd.DataFrame(mentions_data)
        mention_df['timestamp'] = pd.to_datetime(mention_df['timestamp'])
        mention_df['hour'] = mention_df['timestamp'].dt.hour
        mention_df['day_of_week'] = mention_df['timestamp'].dt.day_name()
        
        # Hourly distribution
        hourly_dist = mention_df['hour'].value_counts().sort_index().to_dict()
        
        # Daily distribution
        daily_dist = mention_df['day_of_week'].value_counts().to_dict()
        
        # Context analysis (what triggers mentions)
        mention_contexts = self._analyze_mention_contexts(mentions_data)
        
        return {
            'hourly_distribution': hourly_dist,
            'daily_distribution': daily_dist,
            'mention_context_analysis': mention_contexts,
            'peak_mention_hour': max(hourly_dist.items(), key=lambda x: x[1])[0] if hourly_dist else None,
            'peak_mention_day': max(daily_dist.items(), key=lambda x: x[1])[0] if daily_dist else None
        }
    
    def _analyze_mention_contexts(self, mentions_data: List[Dict]) -> Dict[str, Any]:
        """Analyze the context around mentions"""
        
        context_patterns = {
            'questions': [r'\?', r'뭐', r'어떻게', r'언제', r'어디', r'왜'],
            'requests': [r'해줘', r'부탁', r'도와', r'해달라', r'좀'],
            'greetings': [r'안녕', r'hi', r'hello', r'ㅎㅇ'],
            'urgent': [r'급해', r'빨리', r'긴급', r'urgent', r'!!!'],
            'discussions': [r'생각', r'의견', r'어떻게 생각', r'말해'],
        }
        
        context_counts = {context: 0 for context in context_patterns.keys()}
        
        for mention in mentions_data:
            message = mention['message'].lower()
            
            for context, patterns in context_patterns.items():
                if any(re.search(pattern, message) for pattern in patterns):
                    context_counts[context] += 1
                    break  # Count each mention only once
        
        total_contexts = sum(context_counts.values())
        
        return {
            'context_counts': context_counts,
            'context_percentages': {
                context: count/len(mentions_data)*100 
                for context, count in context_counts.items()
            } if mentions_data else {},
            'categorized_mentions': total_contexts,
            'uncategorized_mentions': len(mentions_data) - total_contexts
        }
    
    def generate_mention_insights(self, mention_analysis: Dict[str, Any]) -> List[str]:
        """Generate human-readable insights from mention analysis"""
        
        insights = []
        stats = mention_analysis['mention_statistics']
        networks = mention_analysis['mention_networks']
        patterns = mention_analysis['mention_patterns']
        summary = mention_analysis['analysis_summary']
        
        # Basic mention statistics
        if summary['total_mentions'] > 0:
            insights.append(f"전체 {summary['total_mentions']}개의 멘션이 발견됨 (메시지 대비 {summary['mention_rate']:.1f}%)")
            
            if stats['top_mentioners']:
                top_mentioner = stats['top_mentioners'][0]
                insights.append(f"가장 많이 멘션을 사용하는 사용자: {top_mentioner['user']} ({top_mentioner['count']}회)")
            
            if stats['top_mentioned']:
                top_mentioned = stats['top_mentioned'][0]
                insights.append(f"가장 많이 멘션받는 사용자: {top_mentioned['user']} ({top_mentioned['count']}회)")
            
            # Reciprocal mentions
            if networks['reciprocal_mentions']:
                insights.append(f"상호 멘션하는 관계: {len(networks['reciprocal_mentions'])}쌍")
            
            # Time patterns
            if patterns.get('peak_mention_hour') is not None:
                insights.append(f"멘션이 가장 활발한 시간: {patterns['peak_mention_hour']}시")
            
            if patterns.get('peak_mention_day'):
                insights.append(f"멘션이 가장 활발한 요일: {patterns['peak_mention_day']}")
            
            # Context analysis
            context_analysis = patterns['mention_context_analysis']
            if context_analysis['context_counts']:
                top_context = max(context_analysis['context_counts'].items(), key=lambda x: x[1])
                if top_context[1] > 0:
                    insights.append(f"멘션의 주요 목적: {top_context[0]} ({top_context[1]}회)")
        else:
            insights.append("이 대화에서는 @ 멘션이 사용되지 않았습니다")
        
        return insights