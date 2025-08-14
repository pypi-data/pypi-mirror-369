"""Advanced topic clustering and intelligent search capabilities"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
import logging
from collections import defaultdict, Counter
import re
from datetime import datetime, timedelta
from sklearn.cluster import KMeans, DBSCAN
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import json


class ConversationTopicAnalyzer:
    """Advanced topic analysis and intelligent search"""
    
    def __init__(self, config, logger: Optional[logging.Logger] = None):
        self.config = config
        self.logger = logger or logging.getLogger(__name__)
        
        # Korean stop words
        self.korean_stopwords = {
            '이', '그', '저', '것', '들', '수', '있', '없', '하', '되', '이다', 
            '하다', '되다', '아니다', '네', '응', '음', '아', '어', '으', '는', 
            '은', '을', '를', '이', '가', '에', '서', '로', '으로', '와', '과',
            '의', '도', '만', '까지', '부터', '께', '께서', '한테', '에게',
            '그냥', '좀', '잠깐', '진짜', '정말', '완전', '너무', '엄청'
        }
        
    def analyze_conversation_topics(self, df: pd.DataFrame, embeddings_data: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive topic analysis using multiple methods"""
        
        self.logger.info("Analyzing conversation topics and themes...")
        
        # TF-IDF based topic discovery
        tfidf_topics = self._discover_tfidf_topics(df)
        
        # Embedding-based topic clustering
        embedding_topics = self._cluster_embedding_topics(df, embeddings_data)
        
        # Time-based topic evolution
        topic_evolution = self._analyze_topic_evolution(df, tfidf_topics)
        
        # User topic preferences
        user_topic_preferences = self._analyze_user_topic_preferences(df, tfidf_topics)
        
        # Topic coherence and quality metrics
        topic_metrics = self._calculate_topic_metrics(tfidf_topics, embedding_topics)
        
        # Smart search index creation
        search_index = self._create_smart_search_index(df, tfidf_topics, embeddings_data)
        
        return {
            'tfidf_topics': tfidf_topics,
            'embedding_topics': embedding_topics,
            'topic_evolution': topic_evolution,
            'user_topic_preferences': user_topic_preferences,
            'topic_metrics': topic_metrics,
            'search_index': search_index,
            'topic_insights': self._generate_topic_insights(tfidf_topics, user_topic_preferences)
        }
    
    def _discover_tfidf_topics(self, df: pd.DataFrame, n_topics: int = 10) -> Dict[str, Any]:
        """Discover topics using TF-IDF and clustering"""
        
        # Preprocess messages
        messages = df['message'].fillna('').astype(str)
        processed_messages = []
        
        for message in messages:
            # Basic Korean text processing
            processed = self._preprocess_korean_text(message)
            if len(processed) > 2:  # Filter very short messages
                processed_messages.append(processed)
        
        if len(processed_messages) < 5:
            return {'topics': [], 'message_assignments': [], 'vocabulary': []}
        
        # Create TF-IDF vectors
        try:
            vectorizer = TfidfVectorizer(
                max_features=1000,
                stop_words=list(self.korean_stopwords),
                ngram_range=(1, 2),
                min_df=2,
                max_df=0.8
            )
            
            tfidf_matrix = vectorizer.fit_transform(processed_messages)
            feature_names = vectorizer.get_feature_names_out()
            
            # Adjust number of topics based on data size
            n_topics = min(n_topics, max(2, len(processed_messages) // 20))
            
            # K-means clustering
            kmeans = KMeans(n_clusters=n_topics, random_state=42, n_init=10)
            topic_assignments = kmeans.fit_predict(tfidf_matrix)
            
            # Extract top terms for each topic
            topics = []
            centers = kmeans.cluster_centers_
            
            for i, center in enumerate(centers):
                # Get top terms for this topic
                top_indices = center.argsort()[-10:][::-1]
                top_terms = [feature_names[idx] for idx in top_indices]
                top_scores = [center[idx] for idx in top_indices]
                
                # Find representative messages
                topic_messages = df.iloc[[idx for idx, assignment in enumerate(topic_assignments) if assignment == i]]
                representative_messages = topic_messages.head(3)['message'].tolist()
                
                # Generate topic label
                topic_label = self._generate_topic_label(top_terms[:3])
                
                topics.append({
                    'topic_id': i,
                    'label': topic_label,
                    'top_terms': list(zip(top_terms, top_scores)),
                    'message_count': sum(1 for x in topic_assignments if x == i),
                    'representative_messages': representative_messages,
                    'coherence_score': self._calculate_topic_coherence(top_terms, tfidf_matrix, vectorizer)
                })
            
            return {
                'topics': topics,
                'message_assignments': topic_assignments.tolist(),
                'vocabulary': feature_names.tolist(),
                'vectorizer_params': {
                    'max_features': 1000,
                    'ngram_range': (1, 2)
                }
            }
            
        except Exception as e:
            self.logger.warning(f"TF-IDF topic discovery failed: {e}")
            return {'topics': [], 'message_assignments': [], 'vocabulary': []}
    
    def _cluster_embedding_topics(self, df: pd.DataFrame, embeddings_data: Dict[str, Any]) -> Dict[str, Any]:
        """Cluster topics using embeddings"""
        
        if 'window_embeddings' not in embeddings_data or len(embeddings_data['window_embeddings']) == 0:
            return {'clusters': [], 'cluster_assignments': []}
        
        try:
            embeddings = embeddings_data['window_embeddings']
            window_info = embeddings_data.get('window_info', [])
            
            # Use DBSCAN for automatic cluster detection
            clustering = DBSCAN(eps=0.3, min_samples=2, metric='cosine')
            cluster_assignments = clustering.fit_predict(embeddings)
            
            # Analyze clusters
            clusters = []
            unique_clusters = set(cluster_assignments)
            
            for cluster_id in unique_clusters:
                if cluster_id == -1:  # Noise cluster
                    continue
                
                # Get messages in this cluster
                cluster_windows = [
                    window_info[i] for i, assignment in enumerate(cluster_assignments) 
                    if assignment == cluster_id
                ]
                
                if not cluster_windows:
                    continue
                
                # Extract representative messages
                cluster_messages = []
                for window in cluster_windows:
                    start_idx = window['start_idx']
                    end_idx = window['end_idx']
                    messages = df.iloc[start_idx:end_idx+1]['message'].tolist()
                    cluster_messages.extend(messages)
                
                # Generate cluster summary
                cluster_label = self._generate_embedding_cluster_label(cluster_messages)
                
                clusters.append({
                    'cluster_id': cluster_id,
                    'label': cluster_label,
                    'window_count': len(cluster_windows),
                    'message_count': len(cluster_messages),
                    'representative_messages': cluster_messages[:5],
                    'time_span': {
                        'start': min(w['start_time'] for w in cluster_windows),
                        'end': max(w['end_time'] for w in cluster_windows)
                    }
                })
            
            return {
                'clusters': clusters,
                'cluster_assignments': cluster_assignments.tolist(),
                'clustering_params': {'eps': 0.3, 'min_samples': 2}
            }
            
        except Exception as e:
            self.logger.warning(f"Embedding-based clustering failed: {e}")
            return {'clusters': [], 'cluster_assignments': []}
    
    def _analyze_topic_evolution(self, df: pd.DataFrame, tfidf_topics: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze how topics evolve over time"""
        
        if not tfidf_topics['topics']:
            return {}
        
        # Create time windows
        df_sorted = df.sort_values('datetime')
        time_span = (df_sorted['datetime'].max() - df_sorted['datetime'].min()).days
        
        if time_span < 1:
            return {}
        
        # Divide into time periods
        n_periods = min(10, max(3, time_span))
        period_length = timedelta(days=time_span / n_periods)
        
        topic_evolution = defaultdict(list)
        message_assignments = tfidf_topics.get('message_assignments', [])
        
        start_time = df_sorted['datetime'].min()
        
        for period in range(n_periods):
            period_start = start_time + period * period_length
            period_end = start_time + (period + 1) * period_length
            
            # Get messages in this period
            period_mask = (df_sorted['datetime'] >= period_start) & (df_sorted['datetime'] < period_end)
            period_indices = df_sorted[period_mask].index
            
            # Count topic occurrences in this period
            period_topics = Counter()
            for idx in period_indices:
                if idx < len(message_assignments):
                    topic_id = message_assignments[idx]
                    period_topics[topic_id] += 1
            
            # Store evolution data
            for topic_id, count in period_topics.items():
                topic_evolution[topic_id].append({
                    'period': period,
                    'start_time': period_start,
                    'end_time': period_end,
                    'message_count': count,
                    'relative_frequency': count / max(1, len(period_indices))
                })
        
        # Calculate trend metrics
        topic_trends = {}
        for topic_id, evolution in topic_evolution.items():
            frequencies = [p['relative_frequency'] for p in evolution]
            if len(frequencies) > 2:
                # Simple linear trend
                x = range(len(frequencies))
                trend_slope = np.polyfit(x, frequencies, 1)[0]
                topic_trends[topic_id] = {
                    'trend_slope': trend_slope,
                    'trend_direction': 'increasing' if trend_slope > 0.01 else 'decreasing' if trend_slope < -0.01 else 'stable',
                    'peak_period': max(evolution, key=lambda x: x['relative_frequency'])['period'],
                    'evolution_data': evolution
                }
        
        return {
            'topic_trends': topic_trends,
            'time_periods': n_periods,
            'period_length_days': time_span / n_periods
        }
    
    def _analyze_user_topic_preferences(self, df: pd.DataFrame, tfidf_topics: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze which users prefer which topics"""
        
        if not tfidf_topics['topics']:
            return {}
        
        message_assignments = tfidf_topics.get('message_assignments', [])
        user_topic_counts = defaultdict(lambda: defaultdict(int))
        
        # Count topic mentions per user
        for idx, row in df.iterrows():
            if idx < len(message_assignments):
                user = row['user']
                topic_id = message_assignments[idx]
                user_topic_counts[user][topic_id] += 1
        
        # Calculate user topic preferences
        user_preferences = {}
        
        for user, topic_counts in user_topic_counts.items():
            total_messages = sum(topic_counts.values())
            
            # Calculate topic distribution for this user
            topic_distribution = {
                topic_id: count / total_messages 
                for topic_id, count in topic_counts.items()
            }
            
            # Find dominant topics
            sorted_topics = sorted(
                topic_distribution.items(), 
                key=lambda x: x[1], 
                reverse=True
            )
            
            # Get topic labels
            topic_labels = {t['topic_id']: t['label'] for t in tfidf_topics['topics']}
            
            user_preferences[user] = {
                'total_messages': total_messages,
                'topic_distribution': topic_distribution,
                'dominant_topics': [
                    {
                        'topic_id': topic_id,
                        'label': topic_labels.get(topic_id, f'Topic {topic_id}'),
                        'frequency': freq
                    }
                    for topic_id, freq in sorted_topics[:3]
                ],
                'topic_diversity': len([f for f in topic_distribution.values() if f > 0.1])
            }
        
        # Find topic specialists and generalists
        specialists = {}
        generalists = {}
        
        for user, prefs in user_preferences.items():
            max_topic_freq = max(prefs['topic_distribution'].values()) if prefs['topic_distribution'] else 0
            diversity = prefs['topic_diversity']
            
            if max_topic_freq > 0.4:  # More than 40% in one topic
                specialists[user] = prefs['dominant_topics'][0] if prefs['dominant_topics'] else None
            
            if diversity >= 3:  # Active in 3+ topics
                generalists[user] = diversity
        
        return {
            'user_preferences': user_preferences,
            'topic_specialists': specialists,
            'topic_generalists': generalists,
            'cross_topic_interactions': self._analyze_cross_topic_interactions(df, message_assignments, user_topic_counts)
        }
    
    def _create_smart_search_index(self, df: pd.DataFrame, tfidf_topics: Dict[str, Any], embeddings_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create an intelligent search index"""
        
        search_index = {
            'messages': [],
            'topics': tfidf_topics.get('topics', []),
            'embeddings_available': len(embeddings_data.get('message_embeddings', [])) > 0
        }
        
        # Index each message with metadata
        message_assignments = tfidf_topics.get('message_assignments', [])
        
        for idx, row in df.iterrows():
            message_data = {
                'message_id': idx,
                'user': row['user'],
                'message': row['message'],
                'timestamp': row['datetime'].isoformat(),
                'topic_id': message_assignments[idx] if idx < len(message_assignments) else None,
                'message_length': len(str(row['message'])),
                'has_question': '?' in str(row['message']),
                'has_emotion': any(char in str(row['message']) for char in ['ㅋ', 'ㅎ', '!', 'ㅠ', 'ㅜ']),
                'keywords': self._extract_message_keywords(str(row['message']))
            }
            
            search_index['messages'].append(message_data)
        
        # Create lookup indexes
        search_index['user_index'] = self._create_user_index(search_index['messages'])
        search_index['keyword_index'] = self._create_keyword_index(search_index['messages'])
        search_index['topic_index'] = self._create_topic_index(search_index['messages'])
        
        return search_index
    
    def smart_search(self, search_index: Dict[str, Any], query: str, embeddings_data: Optional[Dict] = None, top_k: int = 10) -> List[Dict[str, Any]]:
        """Perform intelligent search with multiple strategies"""
        
        results = []
        query_lower = query.lower()
        
        # 1. Keyword-based search
        keyword_results = self._search_by_keywords(search_index, query_lower)
        
        # 2. User-based search
        user_results = self._search_by_user(search_index, query_lower)
        
        # 3. Topic-based search
        topic_results = self._search_by_topic(search_index, query_lower)
        
        # 4. Semantic search (if embeddings available)
        semantic_results = []
        if embeddings_data and search_index['embeddings_available']:
            semantic_results = self._search_by_semantics(search_index, embeddings_data, query, top_k)
        
        # Combine and rank results
        all_results = {}
        
        # Add keyword results
        for result in keyword_results[:top_k]:
            msg_id = result['message_id']
            if msg_id not in all_results:
                all_results[msg_id] = result
                all_results[msg_id]['search_scores'] = {'keyword': result['score']}
            else:
                all_results[msg_id]['search_scores']['keyword'] = result['score']
        
        # Add semantic results
        for result in semantic_results:
            msg_id = result['message_id']
            if msg_id not in all_results:
                all_results[msg_id] = result
                all_results[msg_id]['search_scores'] = {'semantic': result['score']}
            else:
                all_results[msg_id]['search_scores']['semantic'] = result['score']
        
        # Calculate combined scores
        for result in all_results.values():
            scores = result['search_scores']
            # Weighted combination
            combined_score = (
                scores.get('keyword', 0) * 0.4 + 
                scores.get('semantic', 0) * 0.6
            )
            result['combined_score'] = combined_score
        
        # Sort by combined score
        final_results = sorted(
            all_results.values(),
            key=lambda x: x['combined_score'],
            reverse=True
        )
        
        return final_results[:top_k]
    
    def _preprocess_korean_text(self, text: str) -> str:
        """Basic Korean text preprocessing"""
        # Remove special characters but keep Korean
        text = re.sub(r'[^\w\s가-힣ㄱ-ㅎㅏ-ㅣ]', ' ', text)
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def _generate_topic_label(self, top_terms: List[str]) -> str:
        """Generate a readable label for a topic"""
        if not top_terms:
            return "일반 대화"
        
        # Simple heuristics for Korean topic labeling
        terms_str = ' '.join(top_terms[:3])
        
        if any(word in terms_str for word in ['먹', '음식', '식사', '메뉴']):
            return "음식 이야기"
        elif any(word in terms_str for word in ['일', '회사', '업무']):
            return "업무 관련"
        elif any(word in terms_str for word in ['게임', '놀이', '재미']):
            return "게임/오락"
        elif any(word in terms_str for word in ['여행', '가다', '보다']):
            return "여행/외출"
        elif any(word in terms_str for word in ['날씨', '비', '덥', '춥']):
            return "날씨 이야기"
        elif any(word in terms_str for word in ['ㅋㅋ', 'ㅎㅎ', '웃', '재미']):
            return "유머/농담"
        else:
            return f"{top_terms[0]} 관련"
    
    def _generate_embedding_cluster_label(self, messages: List[str]) -> str:
        """Generate label for embedding-based cluster"""
        # Extract common patterns from messages
        all_text = ' '.join(messages).lower()
        
        # Simple keyword-based labeling
        if '먹' in all_text or '음식' in all_text:
            return "음식 관련 대화"
        elif '일' in all_text or '업무' in all_text:
            return "업무 관련 대화"
        elif '게임' in all_text:
            return "게임 관련 대화"
        elif 'ㅋㅋ' in all_text or 'ㅎㅎ' in all_text:
            return "유머/재미있는 대화"
        else:
            return "일반 대화"
    
    def _calculate_topic_coherence(self, terms: List[str], tfidf_matrix, vectorizer) -> float:
        """Calculate topic coherence score"""
        if len(terms) < 2:
            return 0.0
        
        try:
            # Get TF-IDF vectors for terms
            feature_names = vectorizer.get_feature_names_out()
            term_indices = [
                list(feature_names).index(term) 
                for term in terms if term in feature_names
            ]
            
            if len(term_indices) < 2:
                return 0.0
            
            # Calculate average cosine similarity between term vectors
            similarities = []
            for i, idx1 in enumerate(term_indices):
                for idx2 in term_indices[i+1:]:
                    col1 = tfidf_matrix[:, idx1].toarray().flatten()
                    col2 = tfidf_matrix[:, idx2].toarray().flatten()
                    sim = cosine_similarity([col1], [col2])[0][0]
                    similarities.append(sim)
            
            return np.mean(similarities) if similarities else 0.0
            
        except Exception:
            return 0.0
    
    def _calculate_topic_metrics(self, tfidf_topics: Dict, embedding_topics: Dict) -> Dict[str, Any]:
        """Calculate quality metrics for discovered topics"""
        
        metrics = {
            'tfidf_metrics': {},
            'embedding_metrics': {},
            'overall_quality': 0.0
        }
        
        # TF-IDF topic metrics
        if tfidf_topics.get('topics'):
            coherence_scores = [t.get('coherence_score', 0) for t in tfidf_topics['topics']]
            message_counts = [t['message_count'] for t in tfidf_topics['topics']]
            
            metrics['tfidf_metrics'] = {
                'num_topics': len(tfidf_topics['topics']),
                'avg_coherence': np.mean(coherence_scores),
                'avg_messages_per_topic': np.mean(message_counts),
                'topic_balance': np.std(message_counts) / max(1, np.mean(message_counts))  # Lower is better
            }
        
        # Embedding topic metrics
        if embedding_topics.get('clusters'):
            cluster_sizes = [c['message_count'] for c in embedding_topics['clusters']]
            
            metrics['embedding_metrics'] = {
                'num_clusters': len(embedding_topics['clusters']),
                'avg_cluster_size': np.mean(cluster_sizes),
                'cluster_balance': np.std(cluster_sizes) / max(1, np.mean(cluster_sizes))
            }
        
        # Overall quality score
        tfidf_quality = metrics['tfidf_metrics'].get('avg_coherence', 0) * 0.7
        balance_penalty = metrics['tfidf_metrics'].get('topic_balance', 1) * 0.3
        metrics['overall_quality'] = max(0, tfidf_quality - balance_penalty)
        
        return metrics
    
    def _analyze_cross_topic_interactions(self, df: pd.DataFrame, message_assignments: List[int], user_topic_counts: Dict) -> Dict[str, Any]:
        """Analyze how topics interact with each other"""
        
        if not message_assignments:
            return {}
        
        # Topic transitions
        transitions = defaultdict(lambda: defaultdict(int))
        
        for i in range(1, len(message_assignments)):
            prev_topic = message_assignments[i-1]
            curr_topic = message_assignments[i]
            
            if prev_topic != curr_topic:
                transitions[prev_topic][curr_topic] += 1
        
        # Most common transitions
        common_transitions = []
        for from_topic, to_topics in transitions.items():
            for to_topic, count in to_topics.items():
                common_transitions.append({
                    'from_topic': from_topic,
                    'to_topic': to_topic,
                    'transition_count': count
                })
        
        common_transitions.sort(key=lambda x: x['transition_count'], reverse=True)
        
        return {
            'topic_transitions': dict(transitions),
            'most_common_transitions': common_transitions[:10],
            'transition_diversity': len(common_transitions)
        }
    
    def _extract_message_keywords(self, message: str) -> List[str]:
        """Extract keywords from a message"""
        # Simple keyword extraction for Korean
        processed = self._preprocess_korean_text(message)
        words = processed.split()
        
        # Filter out stop words and short words
        keywords = [
            word for word in words 
            if len(word) > 1 and word not in self.korean_stopwords
        ]
        
        return keywords[:5]  # Return top 5 keywords
    
    def _create_user_index(self, messages: List[Dict]) -> Dict[str, List[int]]:
        """Create user-based message index"""
        user_index = defaultdict(list)
        for msg in messages:
            user_index[msg['user']].append(msg['message_id'])
        return dict(user_index)
    
    def _create_keyword_index(self, messages: List[Dict]) -> Dict[str, List[int]]:
        """Create keyword-based message index"""
        keyword_index = defaultdict(list)
        for msg in messages:
            for keyword in msg['keywords']:
                keyword_index[keyword.lower()].append(msg['message_id'])
        return dict(keyword_index)
    
    def _create_topic_index(self, messages: List[Dict]) -> Dict[int, List[int]]:
        """Create topic-based message index"""
        topic_index = defaultdict(list)
        for msg in messages:
            if msg['topic_id'] is not None:
                topic_index[msg['topic_id']].append(msg['message_id'])
        return dict(topic_index)
    
    def _search_by_keywords(self, search_index: Dict, query: str) -> List[Dict[str, Any]]:
        """Search by keyword matching"""
        results = []
        query_words = query.split()
        
        for message in search_index['messages']:
            score = 0
            message_text = message['message'].lower()
            
            # Exact phrase match
            if query in message_text:
                score += 2.0
            
            # Individual word matches
            for word in query_words:
                if word in message_text:
                    score += 1.0
                if word in message['keywords']:
                    score += 0.5
            
            if score > 0:
                results.append({
                    'message_id': message['message_id'],
                    'user': message['user'],
                    'message': message['message'],
                    'timestamp': message['timestamp'],
                    'score': score,
                    'match_type': 'keyword'
                })
        
        return sorted(results, key=lambda x: x['score'], reverse=True)
    
    def _search_by_user(self, search_index: Dict, query: str) -> List[Dict[str, Any]]:
        """Search by user name"""
        results = []
        
        # Check if query matches any user name
        for user, message_ids in search_index['user_index'].items():
            if query in user.lower():
                for msg_id in message_ids:
                    message = search_index['messages'][msg_id]
                    results.append({
                        'message_id': message['message_id'],
                        'user': message['user'],
                        'message': message['message'],
                        'timestamp': message['timestamp'],
                        'score': 1.0,
                        'match_type': 'user'
                    })
        
        return results
    
    def _search_by_topic(self, search_index: Dict, query: str) -> List[Dict[str, Any]]:
        """Search by topic labels"""
        results = []
        
        # Check if query matches any topic label
        for topic in search_index['topics']:
            if query in topic['label'].lower():
                topic_id = topic['topic_id']
                if topic_id in search_index['topic_index']:
                    for msg_id in search_index['topic_index'][topic_id]:
                        message = search_index['messages'][msg_id]
                        results.append({
                            'message_id': message['message_id'],
                            'user': message['user'],
                            'message': message['message'],
                            'timestamp': message['timestamp'],
                            'score': 1.5,
                            'match_type': 'topic'
                        })
        
        return results
    
    def _search_by_semantics(self, search_index: Dict, embeddings_data: Dict, query: str, top_k: int) -> List[Dict[str, Any]]:
        """Search by semantic similarity using embeddings"""
        # This would require encoding the query and computing similarities
        # For now, return empty list since it requires the embedding backend
        return []
    
    def _generate_topic_insights(self, tfidf_topics: Dict, user_preferences: Dict) -> List[str]:
        """Generate interesting insights about topics"""
        
        insights = []
        
        if not tfidf_topics.get('topics'):
            return insights
        
        # Most popular topic
        topics_by_size = sorted(
            tfidf_topics['topics'], 
            key=lambda x: x['message_count'], 
            reverse=True
        )
        
        if topics_by_size:
            most_popular = topics_by_size[0]
            insights.append(f"가장 인기 있는 대화 주제는 '{most_popular['label']}'입니다 ({most_popular['message_count']}개 메시지)")
        
        # Topic diversity
        if len(topics_by_size) >= 3:
            top3_ratio = sum(t['message_count'] for t in topics_by_size[:3]) / sum(t['message_count'] for t in topics_by_size)
            if top3_ratio > 0.8:
                insights.append("소수의 주제에 집중된 대화 패턴을 보입니다")
            else:
                insights.append("다양한 주제로 균형잡힌 대화를 나눕니다")
        
        # User specialization
        if user_preferences:
            specialists = sum(
                1 for prefs in user_preferences.values() 
                if prefs.get('topic_distribution') and max(prefs['topic_distribution'].values()) > 0.4
            )
            total_users = len(user_preferences)
            
            if specialists > total_users * 0.5:
                insights.append("각자 선호하는 특정 주제가 있는 편입니다")
            else:
                insights.append("모든 구성원이 다양한 주제에 참여합니다")
        
        return insights