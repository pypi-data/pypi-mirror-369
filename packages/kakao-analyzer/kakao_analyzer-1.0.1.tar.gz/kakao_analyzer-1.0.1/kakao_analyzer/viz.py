"""Visualization utilities for Kakao analysis"""

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import seaborn as sns
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
import logging
from pathlib import Path
from collections import Counter
import warnings
warnings.filterwarnings('ignore')

# Set up Korean font
plt.rcParams['font.family'] = ['Arial Unicode MS', 'AppleGothic', 'Malgun Gothic', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class KakaoVisualizer:
    """Create visualizations for Kakao analysis results"""
    
    def __init__(self, config, logger: logging.Logger = None):
        self.config = config
        self.logger = logger or logging.getLogger(__name__)
        self.figure_dpi = config.figure_dpi
        self.figure_format = config.figure_format
        self._setup_style()
    
    def _setup_style(self):
        """Setup visualization style"""
        plt.style.use('default')
        sns.set_palette("husl")
        
        # Try to set Korean font
        try:
            font_path = self._find_korean_font()
            if font_path:
                plt.rcParams['font.family'] = [font_path]
                self.logger.info(f"Using Korean font: {font_path}")
        except Exception as e:
            self.logger.warning(f"Could not set Korean font: {e}")
    
    def _find_korean_font(self) -> Optional[str]:
        """Find available Korean font"""
        korean_fonts = [
            'Apple SD Gothic Neo',
            'AppleGothic', 
            'Malgun Gothic',
            'Noto Sans CJK KR',
            'NanumGothic'
        ]
        
        available_fonts = [f.name for f in fm.fontManager.ttflist]
        
        for font in korean_fonts:
            if font in available_fonts:
                return font
        
        return None
    
    def create_all_visualizations(self, analysis_results: Dict[str, Any], 
                                output_dir: Path) -> Dict[str, str]:
        """Create all visualizations and save to output directory"""
        
        self.logger.info("Creating visualizations...")
        
        viz_files = {}
        
        try:
            # 1. Hour x Weekday Heatmap
            if 'temporal' in analysis_results.get('basic_stats', {}):
                viz_files['heatmap'] = self.create_heatmap(
                    analysis_results, output_dir / 'heatmap_hour_weekday.png'
                )
            
            # 2. Daily Timeline
            if 'temporal' in analysis_results.get('basic_stats', {}):
                viz_files['timeline'] = self.create_daily_timeline(
                    analysis_results, output_dir / 'timeseries_daily.png'
                )
            
            # 3. Topic Timeline
            if 'topic_segments' in analysis_results:
                viz_files['topic_timeline'] = self.create_topic_timeline(
                    analysis_results, output_dir / 'topic_timeline.png'
                )
            
            # 4. Word Cloud
            if 'global_words' in analysis_results.get('basic_stats', {}):
                viz_files['wordcloud'] = self.create_wordcloud(
                    analysis_results, output_dir / 'wordcloud_global.png'
                )
            
            # 5. User Activity Distribution
            if 'per_user' in analysis_results.get('basic_stats', {}):
                viz_files['user_activity'] = self.create_user_activity_chart(
                    analysis_results, output_dir / 'user_activity_distribution.png'
                )
            
            # 6. Reply Latency Distribution
            if 'fun_metrics' in analysis_results and 'reply_latency' in analysis_results['fun_metrics']:
                viz_files['reply_latency'] = self.create_reply_latency_chart(
                    analysis_results, output_dir / 'reply_latency_distribution.png'
                )
            
            # 7. Network Graph (User Interaction)
            if 'basic_stats' in analysis_results and 'per_user' in analysis_results['basic_stats']:
                viz_files['network_graph'] = self.create_network_graph(
                    analysis_results, output_dir / 'user_interaction_network.png'
                )
            
            # 8. Mention Network (if available)
            if 'mention_analysis' in analysis_results and analysis_results['mention_analysis'].get('mention_statistics', {}).get('total_mentions', 0) > 0:
                viz_files['mention_network'] = self.create_mention_network_graph(
                    analysis_results, output_dir / 'mention_network.png'
                )
            
        except Exception as e:
            self.logger.error(f"Error creating visualizations: {e}")
        
        self.logger.info(f"Created {len(viz_files)} visualizations")
        return viz_files
    
    def create_heatmap(self, analysis_results: Dict[str, Any], 
                      output_path: Path) -> str:
        """Create hour x weekday activity heatmap"""
        
        temporal_data = analysis_results['basic_stats']['temporal']
        
        # Create hour x weekday matrix
        weekdays = ['월요일', '화요일', '수요일', '목요일', '금요일', '토요일', '일요일']
        hours = range(24)
        
        # Initialize matrix
        activity_matrix = np.zeros((len(weekdays), len(hours)))
        
        # This would need actual hour x weekday cross-tabulation
        # For now, create a sample based on available data
        hourly_dist = temporal_data.get('hourly_distribution', {})
        weekday_dist = temporal_data.get('weekday_distribution', {})
        
        # Create synthetic heatmap data (in real implementation, use cross-tab)
        for i, weekday in enumerate(weekdays):
            weekday_factor = weekday_dist.get(weekday, 0) / max(weekday_dist.values()) if weekday_dist else 0.5
            for j, hour in enumerate(hours):
                hour_factor = hourly_dist.get(f"{hour:02d}", 0) / max(hourly_dist.values()) if hourly_dist else 0.5
                activity_matrix[i, j] = weekday_factor * hour_factor * 100
        
        # Create heatmap
        plt.figure(figsize=(15, 8))
        
        sns.heatmap(
            activity_matrix,
            xticklabels=[f"{h:02d}" for h in hours],
            yticklabels=weekdays,
            annot=False,
            fmt='.0f',
            cmap='YlOrRd',
            cbar_kws={'label': '활동도'}
        )
        
        plt.title('시간대별 × 요일별 활동 히트맵', fontsize=16, pad=20)
        plt.xlabel('시간', fontsize=12)
        plt.ylabel('요일', fontsize=12)
        plt.tight_layout()
        
        plt.savefig(output_path, dpi=self.figure_dpi, bbox_inches='tight')
        plt.close()
        
        return str(output_path)
    
    def create_daily_timeline(self, analysis_results: Dict[str, Any], 
                            output_path: Path) -> str:
        """Create daily message count timeline"""
        
        temporal_data = analysis_results['basic_stats']['temporal']
        daily_data = temporal_data.get('daily_timeseries', [])
        
        if not daily_data:
            # Create empty plot
            plt.figure(figsize=(12, 6))
            plt.text(0.5, 0.5, '일별 데이터가 없습니다', 
                    ha='center', va='center', transform=plt.gca().transAxes,
                    fontsize=14)
            plt.title('일별 메시지 수 추이')
            plt.savefig(output_path, dpi=self.figure_dpi, bbox_inches='tight')
            plt.close()
            return str(output_path)
        
        # Convert to DataFrame
        df = pd.DataFrame(daily_data)
        df['date_only'] = pd.to_datetime(df['date_only'])
        df = df.sort_values('date_only')
        
        # Create timeline plot
        plt.figure(figsize=(15, 8))
        
        plt.plot(df['date_only'], df['count'], 
                linewidth=2, marker='o', markersize=4,
                color='#2E86AB', alpha=0.8)
        
        # Add trend line
        z = np.polyfit(range(len(df)), df['count'], 1)
        p = np.poly1d(z)
        plt.plot(df['date_only'], p(range(len(df))), 
                linestyle='--', color='red', alpha=0.7,
                label='추세선')
        
        plt.title('일별 메시지 수 추이', fontsize=16, pad=20)
        plt.xlabel('날짜', fontsize=12)
        plt.ylabel('메시지 수', fontsize=12)
        plt.grid(True, alpha=0.3)
        plt.legend()
        
        # Format x-axis dates
        plt.xticks(rotation=45)
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=self.figure_dpi, bbox_inches='tight')
        plt.close()
        
        return str(output_path)
    
    def create_topic_timeline(self, analysis_results: Dict[str, Any], 
                            output_path: Path) -> str:
        """Create topic segment timeline"""
        
        segments = analysis_results.get('topic_segments', [])
        
        if not segments:
            plt.figure(figsize=(12, 6))
            plt.text(0.5, 0.5, '주제 세그먼트 데이터가 없습니다', 
                    ha='center', va='center', transform=plt.gca().transAxes,
                    fontsize=14)
            plt.title('주제 세그먼트 타임라인')
            plt.savefig(output_path, dpi=self.figure_dpi, bbox_inches='tight')
            plt.close()
            return str(output_path)
        
        # Determine figure size based on number of segments
        num_segments = len(segments)
        if num_segments > 10:
            # Show only top 10 most important segments
            segments = sorted(segments, key=lambda x: x.get('message_count', 0), reverse=True)[:10]
            num_segments = 10
            self.logger.info(f"Showing top 10 segments out of {len(analysis_results.get('topic_segments', []))}")
        
        fig_height = max(6, num_segments * 0.8)  # Dynamic height
        plt.figure(figsize=(15, fig_height))
        
        # Create timeline bars
        colors = plt.cm.Set3(np.linspace(0, 1, num_segments))
        
        for i, segment in enumerate(segments):
            start_time = pd.to_datetime(segment['start_time'])
            end_time = pd.to_datetime(segment['end_time'])
            
            plt.barh(i, (end_time - start_time).total_seconds() / 3600,  # Convert to hours
                    left=start_time, height=0.6,  # Reduced height to prevent overlap
                    color=colors[i], alpha=0.7,
                    label=f"주제 {i+1}")
            
            # Add segment info with adaptive font size
            mid_time = start_time + (end_time - start_time) / 2
            keywords = ', '.join(segment.get('keywords', [])[:2])  # Limit to 2 keywords
            if len(keywords) > 20:  # Truncate long keywords
                keywords = keywords[:20] + '...'
            
            font_size = max(6, 10 - num_segments * 0.2)  # Adaptive font size
            plt.text(mid_time, i, f"{keywords}\n({segment['message_count']}개)", 
                    ha='center', va='center', fontsize=font_size,
                    bbox=dict(boxstyle="round,pad=0.2", facecolor='white', alpha=0.8))
        
        plt.title('주제 세그먼트 타임라인', fontsize=16, pad=20)
        plt.xlabel('시간', fontsize=12)
        plt.ylabel('주제 세그먼트', fontsize=12)
        plt.grid(True, axis='x', alpha=0.3)
        
        # Format y-axis with better spacing
        y_positions = range(num_segments)
        y_labels = [f"주제 {i+1}" for i in range(num_segments)]
        plt.yticks(y_positions, y_labels)
        plt.ylim(-0.5, num_segments - 0.5)  # Add margins
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=self.figure_dpi, bbox_inches='tight')
        plt.close()
        
        return str(output_path)
    
    def create_wordcloud(self, analysis_results: Dict[str, Any], 
                        output_path: Path) -> str:
        """Create word cloud from global word frequency"""
        
        try:
            from wordcloud import WordCloud
        except ImportError:
            self.logger.warning("wordcloud library not available, creating bar chart instead")
            return self._create_word_frequency_chart(analysis_results, output_path)
        
        word_data = analysis_results['basic_stats']['global_words']
        word_freq = word_data.get('korean_word_frequency', [])
        
        if not word_freq:
            # Fallback to regular words
            word_freq = word_data.get('word_frequency', [])
        
        if not word_freq:
            plt.figure(figsize=(10, 6))
            plt.text(0.5, 0.5, '단어 빈도 데이터가 없습니다', 
                    ha='center', va='center', transform=plt.gca().transAxes,
                    fontsize=14)
            plt.title('전역 워드클라우드')
            plt.savefig(output_path, dpi=self.figure_dpi, bbox_inches='tight')
            plt.close()
            return str(output_path)
        
        # Convert to dictionary
        word_dict = {item['word']: item['count'] for item in word_freq[:50]}
        
        # Create word cloud with proper error handling
        font_path = self._find_korean_font_path()
        wordcloud_kwargs = {
            'width': 800, 
            'height': 600,
            'background_color': 'white',
            'max_words': 50,
            'colormap': 'viridis',
            'relative_scaling': 0.5,
            'min_font_size': 10
        }
        
        if font_path:
            wordcloud_kwargs['font_path'] = font_path
        
        try:
            wordcloud = WordCloud(**wordcloud_kwargs).generate_from_frequencies(word_dict)
        except Exception as e:
            self.logger.warning(f"WordCloud generation failed: {e}, falling back to bar chart")
            return self._create_word_frequency_chart(analysis_results, output_path)
        
        plt.figure(figsize=(12, 8))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.title('전역 워드클라우드', fontsize=16, pad=20)
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=self.figure_dpi, bbox_inches='tight')
        plt.close()
        
        return str(output_path)
    
    def _find_korean_font_path(self) -> Optional[str]:
        """Find path to Korean font file"""
        # Extended list of Korean fonts
        korean_fonts = [
            # macOS fonts
            '/System/Library/Fonts/AppleSDGothicNeo.ttc',
            '/System/Library/Fonts/AppleGothic.ttf',
            '/Library/Fonts/AppleGothic.ttf',
            '/System/Library/Fonts/PingFang.ttc',  # Supports some Korean
            
            # Windows fonts
            'C:/Windows/Fonts/malgun.ttf',
            'C:/Windows/Fonts/malgunbd.ttf',
            'C:/Windows/Fonts/gulim.ttc',
            'C:/Windows/Fonts/batang.ttc',
            
            # Linux fonts
            '/usr/share/fonts/truetype/nanum/NanumGothic.ttf',
            '/usr/share/fonts/truetype/nanum/NanumBarunGothic.ttf',
            '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
        ]
        
        # First try the specified paths
        for font_path in korean_fonts:
            if Path(font_path).exists():
                self.logger.info(f"Found Korean font: {font_path}")
                return font_path
        
        # Try using matplotlib font manager
        try:
            import matplotlib.font_manager as fm
            korean_font_families = ['AppleGothic', 'Apple SD Gothic Neo', 'Malgun Gothic', 'NanumGothic', 'Noto Sans CJK KR']
            
            for family in korean_font_families:
                try:
                    font_prop = fm.FontProperties(family=family)
                    font_path = fm.findfont(font_prop)
                    if font_path and Path(font_path).exists():
                        self.logger.info(f"Found Korean font via matplotlib: {font_path}")
                        return font_path
                except:
                    continue
        except ImportError:
            pass
        
        self.logger.warning("No Korean font found, using default font")
        return None
    
    def _create_word_frequency_chart(self, analysis_results: Dict[str, Any], 
                                   output_path: Path) -> str:
        """Create word frequency bar chart as fallback"""
        
        word_data = analysis_results['basic_stats']['global_words']
        word_freq = word_data.get('korean_word_frequency', [])[:20]
        
        if not word_freq:
            word_freq = word_data.get('word_frequency', [])[:20]
        
        if not word_freq:
            plt.figure(figsize=(10, 6))
            plt.text(0.5, 0.5, '단어 빈도 데이터가 없습니다', 
                    ha='center', va='center', transform=plt.gca().transAxes)
            plt.title('단어 빈도 차트')
            plt.savefig(output_path, dpi=self.figure_dpi, bbox_inches='tight')
            plt.close()
            return str(output_path)
        
        # Create bar chart
        words = [item['word'] for item in word_freq]
        counts = [item['count'] for item in word_freq]
        
        plt.figure(figsize=(12, 8))
        bars = plt.barh(range(len(words)), counts, color='skyblue', alpha=0.8)
        
        plt.yticks(range(len(words)), words)
        plt.xlabel('빈도', fontsize=12)
        plt.title('상위 단어 빈도', fontsize=16, pad=20)
        plt.grid(axis='x', alpha=0.3)
        
        # Add value labels
        for i, (bar, count) in enumerate(zip(bars, counts)):
            plt.text(bar.get_width() + max(counts) * 0.01, bar.get_y() + bar.get_height()/2, 
                    str(count), ha='left', va='center')
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=self.figure_dpi, bbox_inches='tight')
        plt.close()
        
        return str(output_path)
    
    def create_user_activity_chart(self, analysis_results: Dict[str, Any], 
                                 output_path: Path) -> str:
        """Create user activity distribution chart"""
        
        user_stats = analysis_results['basic_stats']['per_user']
        
        if not user_stats:
            plt.figure(figsize=(10, 6))
            plt.text(0.5, 0.5, '사용자 통계 데이터가 없습니다', 
                    ha='center', va='center', transform=plt.gca().transAxes)
            plt.title('사용자 활동 분포')
            plt.savefig(output_path, dpi=self.figure_dpi, bbox_inches='tight')
            plt.close()
            return str(output_path)
        
        users = [stat['user'] for stat in user_stats]
        message_counts = [stat['total_messages'] for stat in user_stats]
        participation_ratios = [stat['participation_ratio'] for stat in user_stats]
        
        # Limit to top users if too many
        max_users = 15
        if len(users) > max_users:
            # Sort by message count and take top users
            sorted_stats = sorted(user_stats, key=lambda x: x['total_messages'], reverse=True)
            users = [stat['user'] for stat in sorted_stats[:max_users]]
            message_counts = [stat['total_messages'] for stat in sorted_stats[:max_users]]
            participation_ratios = [stat['participation_ratio'] for stat in sorted_stats[:max_users]]
            self.logger.info(f"Showing top {max_users} users out of {len(user_stats)}")
        
        # Truncate long usernames
        display_users = []
        for user in users:
            if len(user) > 10:
                display_users.append(user[:8] + '..')
            else:
                display_users.append(user)
        
        # Dynamic figure size based on number of users
        width = max(12, len(users) * 0.5)
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(width, 8))
        
        # Message count bar chart
        bars1 = ax1.bar(range(len(display_users)), message_counts, color='lightblue', alpha=0.8)
        ax1.set_title('사용자별 메시지 수', fontsize=14)
        ax1.set_ylabel('메시지 수')
        ax1.set_xticks(range(len(display_users)))
        ax1.set_xticklabels(display_users, rotation=45, ha='right')
        
        # Add value labels with better positioning
        for i, (bar, count) in enumerate(zip(bars1, message_counts)):
            ax1.text(i, count + max(message_counts) * 0.01,
                    str(count), ha='center', va='bottom', fontsize=9)
        
        # Participation ratio pie chart - only show top contributors for clarity
        top_n = min(8, len(users))  # Limit pie chart to 8 slices
        if len(users) > top_n:
            top_ratios = participation_ratios[:top_n]
            top_users = display_users[:top_n]
            other_ratio = sum(participation_ratios[top_n:])
            top_ratios.append(other_ratio)
            top_users.append(f'기타 ({len(users) - top_n}명)')
        else:
            top_ratios = participation_ratios
            top_users = display_users
        
        wedges, texts, autotexts = ax2.pie(top_ratios, labels=top_users, autopct='%1.1f%%', 
               startangle=90, colors=plt.cm.Pastel1(range(len(top_ratios))))
        
        # Improve text readability
        for autotext in autotexts:
            autotext.set_fontsize(8)
            autotext.set_fontweight('bold')
        
        ax2.set_title('참여 비율', fontsize=14)
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=self.figure_dpi, bbox_inches='tight')
        plt.close()
        
        return str(output_path)
    
    def create_reply_latency_chart(self, analysis_results: Dict[str, Any], 
                                 output_path: Path) -> str:
        """Create reply latency distribution chart"""
        
        reply_data = analysis_results['fun_metrics']['reply_latency']
        overall_stats = reply_data.get('overall_stats', {})
        
        if 'error' in overall_stats:
            plt.figure(figsize=(10, 6))
            plt.text(0.5, 0.5, '답장 지연 데이터가 없습니다', 
                    ha='center', va='center', transform=plt.gca().transAxes)
            plt.title('답장 지연 시간 분포')
            plt.savefig(output_path, dpi=self.figure_dpi, bbox_inches='tight')
            plt.close()
            return str(output_path)
        
        # Extract percentile data
        percentiles = ['p25_minutes', 'p50_minutes', 'p75_minutes', 'p90_minutes', 'p95_minutes']
        percentile_values = [overall_stats.get(p, 0) for p in percentiles]
        percentile_labels = ['25%', '50%', '75%', '90%', '95%']
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Percentile bar chart
        bars = ax1.bar(percentile_labels, percentile_values, color='lightcoral', alpha=0.8)
        ax1.set_title('답장 지연 시간 분위수')
        ax1.set_ylabel('시간 (분)')
        ax1.set_xlabel('분위수')
        
        for bar, value in zip(bars, percentile_values):
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(percentile_values) * 0.01,
                    f'{value:.1f}분', ha='center', va='bottom')
        
        # Category distribution
        categories = reply_data.get('reply_speed_categories', {})
        if categories:
            cat_names = ['즉석 답장\n(1분 이내)', '빠른 답장\n(1-5분)', '보통 답장\n(5-30분)', '느린 답장\n(30분 이상)']
            cat_counts = [
                categories.get('instant_replies', {}).get('count', 0),
                categories.get('quick_replies', {}).get('count', 0),
                categories.get('normal_replies', {}).get('count', 0),
                categories.get('slow_replies', {}).get('count', 0)
            ]
            
            ax2.pie(cat_counts, labels=cat_names, autopct='%1.1f%%', 
                   startangle=90, colors=['lightgreen', 'yellow', 'orange', 'lightcoral'])
            ax2.set_title('답장 속도 분포')
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=self.figure_dpi, bbox_inches='tight')
        plt.close()
        
        return str(output_path)
    
    def create_network_graph(self, analysis_results: Dict[str, Any], 
                           output_path: Path) -> str:
        """Create user interaction network graph"""
        
        try:
            import networkx as nx
        except ImportError:
            self.logger.warning("NetworkX not available, skipping network graph")
            # Create a simple placeholder image
            plt.figure(figsize=(10, 8))
            plt.text(0.5, 0.5, 'NetworkX가 설치되지 않아\n네트워크 그래프를 생성할 수 없습니다', 
                    ha='center', va='center', fontsize=14, transform=plt.gca().transAxes)
            plt.axis('off')
            plt.savefig(output_path, dpi=self.figure_dpi, bbox_inches='tight')
            plt.close()
            return str(output_path)
        
        # Extract user interaction data from turn analysis
        turn_analysis = analysis_results.get('turn_analysis', [])
        user_stats = analysis_results['basic_stats']['per_user']
        
        # Create graph
        G = nx.Graph()
        
        # Add nodes (users) with sizes based on message count
        user_message_counts = {user['user']: user['total_messages'] for user in user_stats}
        max_messages = max(user_message_counts.values()) if user_message_counts else 1
        
        for user, count in user_message_counts.items():
            # Node size proportional to message count
            node_size = (count / max_messages) * 1500 + 300
            G.add_node(user, size=node_size, messages=count)
        
        # Add edges based on conversation interactions
        user_interactions = {}
        
        if isinstance(turn_analysis, list):
            for turn in turn_analysis:
                messages = turn.get('messages', [])
                if len(messages) >= 2:
                    users_in_turn = [msg.get('user') for msg in messages if msg.get('user')]
                    # Create edges between users who participated in same turn
                    for i, user1 in enumerate(users_in_turn):
                        for user2 in users_in_turn[i+1:]:
                            if user1 != user2:
                                edge_key = tuple(sorted([user1, user2]))
                                user_interactions[edge_key] = user_interactions.get(edge_key, 0) + 1
        
        # Add edges to graph
        max_interactions = max(user_interactions.values()) if user_interactions else 1
        for (user1, user2), count in user_interactions.items():
            if count >= 2:  # Only show significant interactions
                weight = (count / max_interactions) * 6 + 1
                G.add_edge(user1, user2, weight=weight, interactions=count)
        
        # Create visualization
        plt.figure(figsize=(16, 12))
        
        # Use better layout with more spacing
        try:
            pos = nx.spring_layout(G, k=3.5, iterations=100, seed=42)
        except:
            pos = nx.random_layout(G, seed=42)
        
        # Adjust positions to prevent overlap
        if len(pos) > 1:
            # Scale positions to create more space
            pos_array = np.array(list(pos.values()))
            center = pos_array.mean(axis=0)
            for node in pos:
                pos[node] = center + (pos[node] - center) * 1.8
        
        # Draw nodes
        node_sizes = [G.nodes[node]['size'] for node in G.nodes()]
        node_colors = plt.cm.Set3(np.linspace(0, 1, len(G.nodes())))
        
        nx.draw_networkx_nodes(G, pos, node_size=node_sizes, node_color=node_colors, 
                               alpha=0.9, edgecolors='black', linewidths=2)
        
        # Draw edges
        if G.edges():
            edge_weights = [G.edges[edge]['weight'] for edge in G.edges()]
            nx.draw_networkx_edges(G, pos, width=edge_weights, alpha=0.6, edge_color='gray')
        
        # Draw labels with better positioning to avoid overlap
        label_pos = {}
        for node, (x, y) in pos.items():
            # Offset labels slightly to avoid overlap with nodes
            label_pos[node] = (x, y + 0.1)
        
        # Draw labels with background
        for node, (x, y) in label_pos.items():
            plt.text(x, y, node, fontsize=10, fontweight='bold', 
                    ha='center', va='center',
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8, edgecolor='gray'))
        
        # Add legend with message counts (positioned outside the plot)
        legend_text = []
        sorted_users = sorted(user_message_counts.items(), key=lambda x: x[1], reverse=True)
        for user, count in sorted_users[:8]:  # Top 8 users
            legend_text.append(f'{user}: {count}개')
        
        plt.text(1.15, 0.98, '메시지 수 상위 사용자', transform=plt.gca().transAxes, 
                fontsize=11, fontweight='bold', verticalalignment='top')
        plt.text(1.15, 0.92, '\n'.join(legend_text), transform=plt.gca().transAxes, 
                fontsize=9, verticalalignment='top',
                bbox=dict(boxstyle='round,pad=0.5', facecolor='lightyellow', alpha=0.8))
        
        plt.title('사용자 상호작용 네트워크\n(노드 크기: 메시지 수, 연결선 굵기: 상호작용 빈도)', 
                 fontsize=16, fontweight='bold', pad=30)
        
        plt.axis('off')
        plt.subplots_adjust(right=0.85)  # Make room for legend
        plt.savefig(output_path, dpi=self.figure_dpi, bbox_inches='tight')
        plt.close()
        
        return str(output_path)
    
    def create_mention_network_graph(self, analysis_results: Dict[str, Any], 
                                   output_path: Path) -> str:
        """Create mention network graph showing who mentions whom"""
        
        try:
            import networkx as nx
        except ImportError:
            self.logger.warning("NetworkX not available, skipping mention network graph")
            return None
        
        mention_analysis = analysis_results.get('mention_analysis', {})
        mention_stats = mention_analysis.get('mention_statistics', {})
        
        # Create directed graph for mentions
        G = nx.DiGraph()
        
        # Add nodes and edges from mention data
        most_active_pairs = mention_stats.get('most_active_pairs', [])
        top_mentioners = mention_stats.get('top_mentioners', [])
        top_mentioned = mention_stats.get('top_mentioned', [])
        
        # Get all users involved in mentions
        all_users = set()
        for mentioner in top_mentioners:
            all_users.add(mentioner['user'])
        for mentioned in top_mentioned:
            all_users.add(mentioned['user'])
        
        # Add nodes
        mentioner_counts = {user['user']: user['count'] for user in top_mentioners}
        mentioned_counts = {user['user']: user['count'] for user in top_mentioned}
        
        for user in all_users:
            out_degree = mentioner_counts.get(user, 0)
            in_degree = mentioned_counts.get(user, 0)
            total_mentions = out_degree + in_degree
            node_size = total_mentions * 100 + 300
            G.add_node(user, size=node_size, out_mentions=out_degree, in_mentions=in_degree)
        
        # Add edges
        for pair in most_active_pairs:
            mentioner = pair['mentioner']
            mentioned = pair['mentioned']
            count = pair['count']
            edge_width = count * 3 + 1
            G.add_edge(mentioner, mentioned, weight=edge_width, mentions=count)
        
        if len(G.nodes()) == 0:
            # No mention data available
            plt.figure(figsize=(12, 8))
            plt.text(0.5, 0.5, '멘션 데이터가 없습니다\n(@ 기능이 사용되지 않았습니다)', 
                    ha='center', va='center', fontsize=16, transform=plt.gca().transAxes,
                    bbox=dict(boxstyle='round,pad=1', facecolor='lightgray', alpha=0.7))
            plt.axis('off')
            plt.savefig(output_path, dpi=self.figure_dpi, bbox_inches='tight')
            plt.close()
            return str(output_path)
        
        # Create visualization
        plt.figure(figsize=(16, 12))
        
        # Layout with more spacing
        try:
            pos = nx.spring_layout(G, k=4, iterations=100, seed=42)
        except:
            pos = nx.circular_layout(G)
        
        # Scale positions for better spacing
        if len(pos) > 1:
            pos_array = np.array(list(pos.values()))
            center = pos_array.mean(axis=0)
            for node in pos:
                pos[node] = center + (pos[node] - center) * 2
        
        # Draw nodes with different colors for different roles
        node_sizes = [G.nodes[node]['size'] for node in G.nodes()]
        
        # Color nodes based on mention behavior
        node_colors = []
        for node in G.nodes():
            out_mentions = G.nodes[node]['out_mentions']
            in_mentions = G.nodes[node]['in_mentions']
            
            if out_mentions > in_mentions:
                node_colors.append('lightcoral')  # More outgoing mentions
            elif in_mentions > out_mentions:
                node_colors.append('lightblue')   # More incoming mentions
            else:
                node_colors.append('lightgreen')  # Balanced
        
        nx.draw_networkx_nodes(G, pos, node_size=node_sizes, node_color=node_colors, 
                               alpha=0.9, edgecolors='black', linewidths=2)
        
        # Draw edges with arrows
        if G.edges():
            edge_weights = [G.edges[edge]['weight'] for edge in G.edges()]
            nx.draw_networkx_edges(G, pos, width=edge_weights, alpha=0.7, edge_color='darkgray',
                                  arrows=True, arrowsize=25, arrowstyle='->')
        
        # Draw labels with background to prevent overlap
        for node, (x, y) in pos.items():
            plt.text(x, y + 0.15, node, fontsize=11, fontweight='bold', 
                    ha='center', va='center',
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.9, edgecolor='black'))
        
        # Legend
        legend_elements = [
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='lightcoral', 
                      markersize=12, label='멘션을 많이 하는 사용자'),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='lightblue', 
                      markersize=12, label='멘션을 많이 받는 사용자'),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='lightgreen', 
                      markersize=12, label='균형잡힌 사용자')
        ]
        plt.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(1.25, 1),
                  fontsize=10, frameon=True, fancybox=True, shadow=True)
        
        plt.title('멘션 네트워크\n(화살표: 멘션 방향, 노드 크기: 총 멘션 수)', 
                 fontsize=16, fontweight='bold', pad=30)
        
        plt.axis('off')
        plt.subplots_adjust(right=0.8)  # Make room for legend
        plt.savefig(output_path, dpi=self.figure_dpi, bbox_inches='tight')
        plt.close()
        
        return str(output_path)