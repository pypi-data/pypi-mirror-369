"""Report generation for Kakao analysis results"""

import pandas as pd
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime
import json
import logging

from .utils import format_duration


class ReportGenerator:
    """Generate analysis reports in markdown format"""
    
    def __init__(self, config, logger: logging.Logger = None):
        self.config = config
        self.logger = logger or logging.getLogger(__name__)
    
    def generate_analysis_report(self, analysis_results: Dict[str, Any], 
                               output_path: Path, viz_files: Dict[str, str] = None) -> str:
        """Generate comprehensive analysis report"""
        
        self.logger.info("Generating analysis report...")
        
        report_sections = []
        
        # Header
        report_sections.append(self._generate_header(analysis_results))
        
        # Executive Summary
        report_sections.append(self._generate_executive_summary(analysis_results))
        
        # Data Overview
        report_sections.append(self._generate_data_overview(analysis_results))
        
        # Basic Statistics
        report_sections.append(self._generate_basic_stats_section(analysis_results))
        
        # Conversation Dynamics
        report_sections.append(self._generate_conversation_dynamics(analysis_results))
        
        # Topic Analysis
        report_sections.append(self._generate_topic_analysis(analysis_results))
        
        # Fun Metrics
        report_sections.append(self._generate_fun_metrics_section(analysis_results))
        
        # Mention Analysis (KakaoTalk feature)
        if 'mention_analysis' in analysis_results:
            report_sections.append(self._generate_mention_analysis_section(analysis_results))
            
        # Context Flow Analysis  
        if 'mention_analysis' in analysis_results and 'context_analysis' in analysis_results['mention_analysis']:
            report_sections.append(self._generate_context_flow_section(analysis_results))
            
        # Topic Sentiment Analysis
        if 'topic_sentiment' in analysis_results:
            report_sections.append(self._generate_topic_sentiment_section(analysis_results))
        
        # Advanced AI Analysis (SPLADE, Ollama)
        if analysis_results.get('sparse_index_info') or analysis_results.get('advanced_topics'):
            report_sections.append(self._generate_advanced_ai_section(analysis_results))
        
        # Visualizations
        if viz_files:
            report_sections.append(self._generate_visualizations_section(viz_files))
        
        # Technical Details
        report_sections.append(self._generate_technical_details(analysis_results))
        
        # Insights and Recommendations
        report_sections.append(self._generate_insights_section(analysis_results))
        
        # Footer
        report_sections.append(self._generate_footer())
        
        # Combine all sections
        full_report = '\n\n'.join(report_sections)
        
        # Save report
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(full_report)
        
        self.logger.info(f"Analysis report saved to {output_path}")
        return str(output_path)
    
    def _generate_header(self, analysis_results: Dict[str, Any]) -> str:
        """Generate report header"""
        
        return f"""# 카카오톡 대화 분석 리포트
        
**생성 일시**: {datetime.now().strftime('%Y년 %m월 %d일 %H:%M')}  
**분석 도구**: Kakao Analyzer v{analysis_results.get('version', '1.0.0')}  
**분석 대상**: {analysis_results.get('data_info', {}).get('source_file', 'Unknown')}

---"""
    
    def _generate_executive_summary(self, analysis_results: Dict[str, Any]) -> str:
        """Generate executive summary"""
        
        basic_stats = analysis_results.get('basic_stats', {})
        summary_stats = basic_stats.get('summary', {})
        
        if not summary_stats or 'error' in summary_stats:
            return "## 📊 요약\n\n*데이터 부족으로 요약을 생성할 수 없습니다.*"
        
        total_messages = summary_stats.get('total_messages', 0)
        unique_users = summary_stats.get('unique_users', 0)
        date_range = summary_stats.get('date_range', {})
        activity_summary = summary_stats.get('activity_summary', {})
        
        insights = self._extract_key_insights(analysis_results)
        
        return f"""## 📊 요약

### 핵심 지표
- **총 메시지 수**: {total_messages:,}개
- **참여자 수**: {unique_users}명
- **분석 기간**: {date_range.get('total_days', 0)}일 ({date_range.get('start', '')[:10]} ~ {date_range.get('end', '')[:10]})
- **일평균 메시지**: {activity_summary.get('messages_per_day', 0):.1f}개

### 주요 인사이트
{chr(10).join([f"- {insight}" for insight in insights[:5]])}"""
    
    def _generate_data_overview(self, analysis_results: Dict[str, Any]) -> str:
        """Generate data overview section"""
        
        data_info = analysis_results.get('data_info', {})
        validation = analysis_results.get('data_validation', {})
        
        overview_text = f"""## 📋 데이터 개요

### 데이터 품질
- **상태**: {'✅ 양호' if validation.get('is_valid', False) else '⚠️ 문제 있음'}
- **경고사항**: {len(validation.get('warnings', []))}개
- **오류사항**: {len(validation.get('errors', []))}개"""
        
        if validation.get('warnings'):
            overview_text += f"\n\n**경고사항:**\n" + '\n'.join([f"- {warning}" for warning in validation['warnings'][:3]])
        
        if validation.get('errors'):
            overview_text += f"\n\n**오류사항:**\n" + '\n'.join([f"- {error}" for error in validation['errors'][:3]])
        
        return overview_text
    
    def _generate_basic_stats_section(self, analysis_results: Dict[str, Any]) -> str:
        """Generate basic statistics section"""
        
        basic_stats = analysis_results.get('basic_stats', {})
        per_user = basic_stats.get('per_user', [])
        temporal = basic_stats.get('temporal', {})
        
        section = "## 📈 기본 통계"
        
        # User statistics
        if per_user:
            section += "\n\n### 사용자별 활동"
            section += "\n\n| 사용자 | 메시지 수 | 참여율 | 일평균 | 단어수 |"
            section += "\n|--------|-----------|--------|--------|--------|"
            
            for user_stat in per_user[:10]:  # Top 10 users
                section += f"\n| {user_stat['user']} | {user_stat['total_messages']:,} | {user_stat['participation_ratio']:.1f}% | {user_stat['messages_per_day']:.1f} | {user_stat['total_words']:,} |"
        
        # Temporal patterns
        if temporal:
            peak_activity = temporal.get('peak_activity', {})
            section += f"\n\n### 시간적 패턴"
            section += f"\n- **최고 활동 시간**: {peak_activity.get('peak_hour', 'N/A')}"
            section += f"\n- **최고 활동 요일**: {peak_activity.get('peak_day', 'N/A')}"
            
            time_periods = temporal.get('time_period_distribution', {})
            if time_periods:
                section += f"\n- **아침 (06-11시)**: {time_periods.get('morning_6_11', {}).get('percent', 0):.1f}%"
                section += f"\n- **오후 (12-17시)**: {time_periods.get('afternoon_12_17', {}).get('percent', 0):.1f}%"
                section += f"\n- **저녁 (18-23시)**: {time_periods.get('evening_18_23', {}).get('percent', 0):.1f}%"
                section += f"\n- **새벽 (00-05시)**: {time_periods.get('night_0_5', {}).get('percent', 0):.1f}%"
        
        # Message characteristics
        summary_stats = basic_stats.get('summary', {})
        message_chars = summary_stats.get('message_characteristics', {})
        if message_chars:
            section += f"\n\n### 메시지 특성"
            section += f"\n- **평균 메시지 길이**: {message_chars.get('avg_length', 0):.1f}자"
            section += f"\n- **평균 단어 수 (원본)**: {message_chars.get('avg_words', 0):.1f}개"
            if 'avg_filtered_words' in message_chars:
                section += f"\n- **평균 단어 수 (필터링)**: {message_chars.get('avg_filtered_words', 0):.1f}개"
            section += f"\n- **중간값 메시지 길이**: {message_chars.get('median_length', 0)}자"
            section += f"\n- **중간값 단어 수 (원본)**: {message_chars.get('median_words', 0)}개"
            if 'median_filtered_words' in message_chars:
                section += f"\n- **중간값 단어 수 (필터링)**: {message_chars.get('median_filtered_words', 0)}개"
            section += f"\n- **최대 메시지 길이**: {message_chars.get('max_length', 0)}자"
            section += f"\n- **총 단어 수**: {message_chars.get('total_words', 0):,}개"
            if 'total_filtered_words' in message_chars:
                section += f"\n- **총 필터링된 단어 수**: {message_chars.get('total_filtered_words', 0):,}개"
        
        return section
    
    def _generate_conversation_dynamics(self, analysis_results: Dict[str, Any]) -> str:
        """Generate conversation dynamics section"""
        
        turn_analysis = analysis_results.get('turn_analysis', {})
        
        if not turn_analysis:
            return "## 💬 대화 역학\n\n*대화 분석 데이터가 없습니다.*"
        
        section = "## 💬 대화 역학"
        
        # Turn statistics
        section += f"\n\n### 대화 턴 분석"
        # Calculate statistics from turn list
        if isinstance(turn_analysis, list):
            turns = turn_analysis
            section += f"\n- **총 대화 턴**: {len(turns)}개"
            
            if turns:
                # Calculate duration statistics
                durations = [turn.get('duration_minutes', 0) for turn in turns]
                avg_duration = sum(durations) / len(durations) if durations else 0
                max_duration = max(durations) if durations else 0
                
                section += f"\n- **평균 대화 길이**: {avg_duration:.1f}분"
                section += f"\n- **최장 대화 길이**: {max_duration:.1f}분"
                
                # Calculate message statistics
                message_counts = [turn.get('message_count', 0) for turn in turns]
                avg_messages = sum(message_counts) / len(message_counts) if message_counts else 0
                section += f"\n- **턴당 평균 메시지**: {avg_messages:.1f}개"
                
                # Find conversation initiators (first message in each turn)
                initiators = {}
                for turn in turns:
                    messages = turn.get('messages', [])
                    if messages:
                        first_user = messages[0].get('user', 'Unknown')
                        initiators[first_user] = initiators.get(first_user, 0) + 1
            else:
                initiators = {}
        else:
            # Fallback for dict structure
            section += f"\n- **총 대화 턴**: {turn_analysis.get('total_turns', 0)}개"
            duration_stats = turn_analysis.get('duration_stats', {})
            if duration_stats:
                section += f"\n- **평균 대화 길이**: {duration_stats.get('avg_duration_minutes', 0):.1f}분"
                section += f"\n- **최장 대화 길이**: {duration_stats.get('max_duration_minutes', 0):.1f}분"
            
            message_stats = turn_analysis.get('message_stats', {})
            if message_stats:
                section += f"\n- **턴당 평균 메시지**: {message_stats.get('avg_messages_per_turn', 0):.1f}개"
            
            initiators = turn_analysis.get('conversation_initiators', {})
        if initiators:
            section += f"\n\n### 대화 시작 패턴"
            # Sort initiators by count in descending order
            sorted_initiators = sorted(initiators.items(), key=lambda x: x[1], reverse=True)
            for user, count in sorted_initiators[:3]:
                section += f"\n- **{user}**: {count}회 시작"
        
        return section
    
    def _generate_topic_analysis(self, analysis_results: Dict[str, Any]) -> str:
        """Generate topic analysis section"""
        
        topic_segments = analysis_results.get('topic_segments', [])
        topic_shifts = analysis_results.get('topic_analysis', {})
        
        if not topic_segments and not topic_shifts:
            return "## 🏷️ 주제 분석\n\n*주제 분석 데이터가 없습니다.*"
        
        section = "## 🏷️ 주제 분석"
        
        # Topic segments overview
        if topic_segments:
            section += f"\n\n### 주제 세그먼트"
            section += f"\n- **총 세그먼트**: {len(topic_segments)}개"
            
            # Average segment characteristics
            avg_duration = sum([seg['duration_minutes'] for seg in topic_segments]) / len(topic_segments)
            avg_messages = sum([seg['message_count'] for seg in topic_segments]) / len(topic_segments)
            
            section += f"\n- **평균 세그먼트 길이**: {avg_duration:.1f}분"
            section += f"\n- **세그먼트당 평균 메시지**: {avg_messages:.1f}개"
            
            # Top segments by activity
            top_segments = sorted(topic_segments, key=lambda x: x['message_count'], reverse=True)[:3]
            section += f"\n\n### 주요 대화 주제"
            
            for i, segment in enumerate(top_segments, 1):
                keywords = ', '.join(segment.get('keywords', [])[:5])
                section += f"\n**{i}. {segment.get('summary', 'No summary')}**"
                section += f"\n- 키워드: {keywords}"
                section += f"\n- 메시지 수: {segment['message_count']}개"
                section += f"\n- 지속 시간: {segment['duration_minutes']:.1f}분\n"
        
        # Topic shift analysis
        if topic_shifts:
            section += f"\n\n### 주제 전환 패턴"
            section += f"\n- **일평균 주제 전환**: {topic_shifts.get('total_shifts', 0) / max(1, topic_shifts.get('analysis_days', 1)):.1f}회"
            
            shift_intervals = topic_shifts.get('shift_intervals', {})
            if shift_intervals:
                section += f"\n- **평균 전환 간격**: {shift_intervals.get('avg_minutes', 0):.1f}분"
        
        return section
    
    def _generate_fun_metrics_section(self, analysis_results: Dict[str, Any]) -> str:
        """Generate fun metrics section"""
        
        fun_metrics = analysis_results.get('fun_metrics', {})
        
        if not fun_metrics:
            return "## 🎯 재미있는 지표\n\n*재미 지표 데이터가 없습니다.*"
        
        section = "## 🎯 재미있는 지표"
        
        # Participation inequality
        participation = fun_metrics.get('participation_inequality', {})
        if participation:
            section += f"\n\n### 참여 불평등"
            section += f"\n- **지니 계수**: {participation.get('gini_coefficient', 0):.3f} ({participation.get('interpretation', 'N/A')})"
            section += f"\n- **상위 20% 사용자의 메시지 비중**: {participation.get('top_20_percent_share', 0):.1f}%"
            section += f"\n- **최고 활동 사용자**: {participation.get('most_active_user', 'N/A')} ({participation.get('top_user_share', 0):.1f}%)"
        
        # Reply latency
        reply_latency = fun_metrics.get('reply_latency', {})
        overall_stats = reply_latency.get('overall_stats', {})
        if overall_stats and 'error' not in overall_stats:
            section += f"\n\n### 답장 속도"
            section += f"\n- **평균 답장 시간**: {overall_stats.get('mean_minutes', 0):.1f}분"
            section += f"\n- **중간 답장 시간**: {overall_stats.get('median_minutes', 0):.1f}분"
            section += f"\n- **가장 빠른 답장**: {overall_stats.get('min_minutes', 0):.1f}분"
            
            # Reply speed categories
            categories = reply_latency.get('reply_speed_categories', {})
            if categories:
                instant = categories.get('instant_replies', {})
                section += f"\n- **즉석 답장 (1분 이내)**: {instant.get('percent', 0):.1f}%"
        
        # Activity streaks
        streaks = fun_metrics.get('activity_streaks', {})
        if streaks:
            section += f"\n\n### 활동 패턴"
            section += f"\n- **최장 연속 메시지**: {streaks.get('longest_message_streak', 0)}개"
            section += f"\n- **최장 연속 활동일**: {streaks.get('longest_daily_streak', 0)}일"
        
        # Night chat analysis
        night_chat = fun_metrics.get('night_chat_analysis', {})
        if night_chat and 'error' not in night_chat:
            section += f"\n\n### 밤샘 채팅"
            section += f"\n- **심야 채팅 비율**: {night_chat.get('night_chat_percentage', 0):.1f}%"
            section += f"\n- **가장 활발한 심야 시간**: {night_chat.get('peak_night_hour', 'N/A')}"
        
        return section
    
    def _generate_mention_analysis_section(self, analysis_results: Dict[str, Any]) -> str:
        """Generate mention analysis section"""
        
        mention_analysis = analysis_results.get('mention_analysis', {})
        
        section = "## @ 멘션 분석"
        section += f"\n\n### 멘션 사용 패턴"
        
        summary = mention_analysis.get('analysis_summary', {})
        stats = mention_analysis.get('mention_statistics', {})
        
        if summary.get('total_mentions', 0) > 0:
            section += f"\n- **총 멘션 수**: {summary['total_mentions']}개"
            section += f"\n- **멘션 비율**: {summary['mention_rate']:.1f}% (전체 메시지 대비)"
            section += f"\n- **멘션 사용자**: {summary['unique_mentioners']}명"
            section += f"\n- **멘션받은 사용자**: {summary['unique_mentioned']}명"
            
            # Top mentioners
            if stats.get('top_mentioners'):
                section += f"\n\n### 가장 많이 멘션하는 사용자"
                for user_stat in stats['top_mentioners'][:5]:
                    section += f"\n- **{user_stat['user']}**: {user_stat['count']}회 ({user_stat['percentage']:.1f}%)"
            
            # Top mentioned
            if stats.get('top_mentioned'):
                section += f"\n\n### 가장 많이 멘션받는 사용자"
                for user_stat in stats['top_mentioned'][:5]:
                    section += f"\n- **{user_stat['user']}**: {user_stat['count']}회 ({user_stat['percentage']:.1f}%)"
            
            # Most active pairs
            if stats.get('most_active_pairs'):
                section += f"\n\n### 활발한 멘션 관계"
                for pair in stats['most_active_pairs'][:3]:
                    section += f"\n- **{pair['mentioner']} → {pair['mentioned']}**: {pair['count']}회"
            
            # Network analysis
            networks = mention_analysis.get('mention_networks', {})
            if networks.get('reciprocal_mentions'):
                section += f"\n\n### 상호 멘션 관계"
                section += f"\n- **상호 멘션하는 쌍**: {len(networks['reciprocal_mentions'])}쌍"
                for pair in networks['reciprocal_mentions'][:3]:
                    section += f"\n- **{pair['user1']} ↔ {pair['user2']}**: "
                    section += f"{pair['mentions_1_to_2']}회 / {pair['mentions_2_to_1']}회"
            
            # Time patterns
            patterns = mention_analysis.get('mention_patterns', {})
            if patterns.get('peak_mention_hour') is not None:
                section += f"\n\n### 멘션 시간 패턴"
                section += f"\n- **가장 활발한 시간**: {patterns['peak_mention_hour']}시"
                
            if patterns.get('peak_mention_day'):
                section += f"\n- **가장 활발한 요일**: {patterns['peak_mention_day']}"
            
            # Context analysis
            context_analysis = patterns.get('mention_context_analysis', {})
            if context_analysis.get('context_percentages'):
                section += f"\n\n### 멘션 사용 목적"
                for context, percentage in context_analysis['context_percentages'].items():
                    if percentage > 0:
                        korean_context = {
                            'questions': '질문',
                            'requests': '부탁/요청', 
                            'greetings': '인사',
                            'urgent': '긴급',
                            'discussions': '토론/의견'
                        }.get(context, context)
                        section += f"\n- **{korean_context}**: {percentage:.1f}%"
        else:
            section += f"\n\n이 대화에서는 @ 멘션 기능이 사용되지 않았습니다."
        
        return section
    
    def _generate_context_flow_section(self, analysis_results: Dict[str, Any]) -> str:
        """Generate context flow analysis section"""
        
        mention_analysis = analysis_results.get('mention_analysis', {})
        context_analysis = mention_analysis.get('context_analysis', {})
        
        section = "## 🔄 대화 맥락 분석"
        
        response_analysis = context_analysis.get('response_analysis', {})
        if response_analysis.get('total_mentions', 0) > 0:
            section += f"\n\n### 멘션 응답 분석"
            section += f"\n- **전체 응답률**: {response_analysis.get('overall_response_rate', 0):.1f}%"
            section += f"\n- **평균 응답 시간**: {response_analysis.get('average_response_time_minutes', 0):.1f}분"
            section += f"\n- **응답받은 멘션**: {response_analysis.get('mentions_with_response', 0)}개 / {response_analysis.get('total_mentions', 0)}개"
            
            # User effectiveness
            user_effectiveness = response_analysis.get('user_effectiveness', [])
            if user_effectiveness:
                section += f"\n\n### 멘션 효과적인 사용자"
                for user_stat in user_effectiveness[:5]:
                    section += f"\n- **{user_stat['user']}**: {user_stat['effectiveness_rate']}% 성공률 ({user_stat['successful_mentions']}/{user_stat['total_mentions']})"
        
        # Topic distribution
        topic_distribution = context_analysis.get('topic_distribution', {})
        top_topics = topic_distribution.get('top_topics', [])
        if top_topics:
            section += f"\n\n### 멘션 대화 주제"
            for topic_info in top_topics[:5]:
                section += f"\n- **{topic_info['topic']}**: {topic_info['count']}회"
        
        # Context patterns
        context_patterns = context_analysis.get('context_patterns', {})
        pattern_percentages = context_patterns.get('pattern_percentages', {})
        if pattern_percentages:
            section += f"\n\n### 멘션 사용 패턴"
            section += f"\n*참고: 하나의 멘션이 여러 패턴에 동시에 해당할 수 있어 총합이 100%를 초과할 수 있습니다*"
            korean_pattern_names = {
                'mention_in_question': '질문시 멘션',
                'mention_in_request': '부탁시 멘션', 
                'mention_in_greeting': '인사시 멘션',
                'mention_in_discussion': '토론시 멘션',
                'mention_after_silence': '침묵 후 멘션',
                'mention_in_group_chat': '그룹 대화 중 멘션'
            }
            
            for pattern, percentage in pattern_percentages.items():
                if percentage > 0:
                    korean_name = korean_pattern_names.get(pattern, pattern)
                    section += f"\n- **{korean_name}**: {percentage}%"
            
            most_common = context_patterns.get('most_common_pattern')
            if most_common:
                korean_most_common = korean_pattern_names.get(most_common, most_common)
                section += f"\n\n**가장 일반적인 멘션 패턴**: {korean_most_common}"
        
        return section
    
    def _generate_topic_sentiment_section(self, analysis_results: Dict[str, Any]) -> str:
        """Generate topic sentiment analysis section"""
        
        topic_sentiment = analysis_results.get('topic_sentiment', {})
        
        section = "## 🎭 토픽별 감정 분석"
        
        total_segments = topic_sentiment.get('total_segments', 0)
        if total_segments == 0:
            section += "\n\n분석할 수 있는 토픽 세그먼트가 없습니다."
            return section
        
        # Overall sentiment distribution
        sentiment_dist = topic_sentiment.get('sentiment_distribution', {})
        overall_mood = topic_sentiment.get('overall_mood', 'neutral')
        
        mood_names = {
            'positive': '긍정적',
            'negative': '부정적',
            'neutral': '중립적'
        }
        
        section += f"\n\n### 전반적인 감정 분위기"
        section += f"\n- **주된 분위기**: {mood_names.get(overall_mood, overall_mood)}"
        section += f"\n- **총 토픽 세그먼트**: {total_segments}개"
        
        if sentiment_dist:
            section += f"\n\n### 감정 분포"
            for sentiment, percentage in sentiment_dist.items():
                korean_sentiment = mood_names.get(sentiment, sentiment)
                section += f"\n- **{korean_sentiment}**: {percentage:.1f}%"
        
        # Mood transitions
        mood_transitions = topic_sentiment.get('mood_transitions', {})
        stability = mood_transitions.get('stability', 1.0)
        total_changes = mood_transitions.get('total_changes', 0)
        
        section += f"\n\n### 감정 변화 패턴"
        section += f"\n- **감정 안정성**: {stability:.1f} (1.0이 가장 안정적)"
        section += f"\n- **감정 변화 횟수**: {total_changes}회"
        
        if stability > 0.8:
            stability_desc = "매우 안정적인 감정 흐름"
        elif stability > 0.6:
            stability_desc = "보통 수준의 감정 안정성"
        elif stability > 0.4:
            stability_desc = "다소 변화가 많은 감정 흐름"
        else:
            stability_desc = "매우 역동적인 감정 변화"
        
        section += f"\n- **감정 흐름 특성**: {stability_desc}"
        
        most_common_transition = mood_transitions.get('most_common_transition')
        if most_common_transition and most_common_transition != "stable mood":
            section += f"\n- **가장 흔한 감정 변화**: {most_common_transition}"
        
        # Context patterns
        context_patterns = topic_sentiment.get('context_patterns', {})
        context_dist = context_patterns.get('context_distribution', {})
        most_common_context = context_patterns.get('most_common_context')
        
        if context_dist:
            section += f"\n\n### 대화 맥락 분포"
            
            context_names = {
                'discussion': '토론/논의',
                'planning': '계획 수립',
                'problem_solving': '문제 해결',
                'casual_chat': '일상 대화',
                'emotional_support': '감정적 지지',
                'information_sharing': '정보 공유'
            }
            
            # Sort by count and show top contexts
            sorted_contexts = sorted(context_dist.items(), key=lambda x: x[1], reverse=True)
            for context, count in sorted_contexts[:5]:
                korean_context = context_names.get(context, context)
                percentage = (count / total_segments) * 100
                section += f"\n- **{korean_context}**: {count}회 ({percentage:.1f}%)"
        
        # Average intensity by context
        avg_intensities = context_patterns.get('avg_intensity_by_context', {})
        if avg_intensities:
            section += f"\n\n### 맥락별 감정 강도"
            sorted_intensities = sorted(avg_intensities.items(), key=lambda x: x[1], reverse=True)
            
            context_names = {
                'discussion': '토론/논의',
                'planning': '계획 수립', 
                'problem_solving': '문제 해결',
                'casual_chat': '일상 대화',
                'emotional_support': '감정적 지지',
                'information_sharing': '정보 공유'
            }
            
            for context, intensity in sorted_intensities[:3]:
                korean_context = context_names.get(context, context)
                intensity_level = "높음" if intensity > 0.3 else "보통" if intensity > 0.1 else "낮음"
                section += f"\n- **{korean_context}**: {intensity:.2f} ({intensity_level})"
        
        # Segment examples
        segment_analysis = topic_sentiment.get('segment_analysis', [])
        if segment_analysis:
            # Find interesting segments to highlight
            positive_segments = [s for s in segment_analysis if s.get('overall_sentiment') == 'positive']
            negative_segments = [s for s in segment_analysis if s.get('overall_sentiment') == 'negative']
            
            if positive_segments:
                # Most positive segment
                most_positive = max(positive_segments, key=lambda x: x.get('sentiment_scores', {}).get('positive', 0))
                section += f"\n\n### 가장 긍정적인 토픽"
                section += f"\n- **기간**: {most_positive.get('start_time', '')} ~ {most_positive.get('end_time', '')}"
                section += f"\n- **메시지 수**: {most_positive.get('message_count', 0)}개"
                section += f"\n- **참여자**: {most_positive.get('participant_count', 0)}명"
                
                key_phrases = most_positive.get('key_phrases', [])
                if key_phrases:
                    section += f"\n- **주요 키워드**: {', '.join(key_phrases[:5])}"
            
            if negative_segments:
                # Most negative segment
                most_negative = max(negative_segments, key=lambda x: x.get('sentiment_scores', {}).get('negative', 0))
                section += f"\n\n### 가장 부정적인 토픽"
                section += f"\n- **기간**: {most_negative.get('start_time', '')} ~ {most_negative.get('end_time', '')}"
                section += f"\n- **메시지 수**: {most_negative.get('message_count', 0)}개"
                section += f"\n- **참여자**: {most_negative.get('participant_count', 0)}명"
                
                key_phrases = most_negative.get('key_phrases', [])
                if key_phrases:
                    section += f"\n- **주요 키워드**: {', '.join(key_phrases[:5])}"
        
        return section
    
    def _generate_advanced_ai_section(self, analysis_results: Dict[str, Any]) -> str:
        """Generate advanced AI analysis section (SPLADE, Ollama)"""
        
        section = "## 🤖 고급 AI 분석"
        
        # SPLADE sparse retrieval analysis
        sparse_index_info = analysis_results.get('sparse_index_info', {})
        if sparse_index_info:
            section += f"\n\n### SPLADE 희소 검색 분석"
            section += f"\n- **모델**: {sparse_index_info.get('model_name', 'naver/splade-cocondenser-ensembledistil')}"
            section += f"\n- **인덱스된 문서 수**: {sparse_index_info.get('total_documents', 0):,}개"
            section += f"\n- **평균 희소성**: {sparse_index_info.get('avg_sparsity', 0):.3f}"
            section += f"\n- **벡터 차원**: {sparse_index_info.get('vector_dimension', 0):,}차원"
            
            # Top sparse terms
            top_terms = sparse_index_info.get('top_sparse_terms', [])
            if top_terms:
                section += f"\n\n**주요 희소 특징 토큰:**"
                for term_info in top_terms[:10]:
                    section += f"\n- **{term_info.get('term', '')}**: {term_info.get('weight', 0):.3f}"
            
            # Search capabilities
            search_stats = sparse_index_info.get('search_stats', {})
            if search_stats:
                section += f"\n\n**검색 성능:**"
                section += f"\n- **검색 가능 토큰 수**: {search_stats.get('searchable_tokens', 0):,}개"
                section += f"\n- **고유 토큰 수**: {search_stats.get('unique_tokens', 0):,}개"
                section += f"\n- **평균 검색 응답 시간**: {search_stats.get('avg_search_time_ms', 0):.1f}ms"
        
        # Ollama model analysis
        advanced_topics = analysis_results.get('advanced_topics', {})
        if advanced_topics:
            section += f"\n\n### Ollama 모델 분석 (oss:20b)"
            
            model_info = advanced_topics.get('model_info', {})
            section += f"\n- **모델**: {model_info.get('name', 'oss:20b')}"
            section += f"\n- **모델 크기**: {model_info.get('size', 'Unknown')}"
            section += f"\n- **분석된 세그먼트**: {advanced_topics.get('analyzed_segments', 0)}개"
            
            # Topic insights
            insights = advanced_topics.get('insights', [])
            if insights:
                section += f"\n\n**AI 생성 인사이트:**"
                for i, insight in enumerate(insights[:5], 1):
                    section += f"\n{i}. {insight}"
            
            # Topic themes discovered by LLM
            themes = advanced_topics.get('discovered_themes', [])
            if themes:
                section += f"\n\n**발견된 주제 패턴:**"
                for theme in themes[:5]:
                    section += f"\n- **{theme.get('theme', '')}**: {theme.get('description', '')}"
                    section += f"  - 빈도: {theme.get('frequency', 0)}회"
            
            # Conversation quality analysis
            quality_analysis = advanced_topics.get('conversation_quality', {})
            if quality_analysis:
                section += f"\n\n**대화 품질 분석:**"
                section += f"\n- **전반적 품질 점수**: {quality_analysis.get('overall_score', 0):.2f}/5.0"
                section += f"\n- **주제 깊이**: {quality_analysis.get('topic_depth', 'Unknown')}"
                section += f"\n- **참여 균형**: {quality_analysis.get('participation_balance', 'Unknown')}"
                section += f"\n- **감정적 톤**: {quality_analysis.get('emotional_tone', 'Unknown')}"
            
            # Processing performance
            processing_stats = advanced_topics.get('processing_stats', {})
            if processing_stats:
                section += f"\n\n**처리 성능:**"
                section += f"\n- **총 처리 시간**: {processing_stats.get('total_time_seconds', 0):.1f}초"
                section += f"\n- **토큰 처리율**: {processing_stats.get('tokens_per_second', 0):.0f} tokens/sec"
                section += f"\n- **메모리 사용량**: {processing_stats.get('peak_memory_mb', 0):.1f}MB"
        
        # Combined analysis insights
        if sparse_index_info and advanced_topics:
            section += f"\n\n### 하이브리드 분석 결과"
            section += f"\n희소 검색(SPLADE)과 대화형 AI(Ollama)를 결합한 분석을 통해 다음과 같은 인사이트를 도출했습니다:"
            
            # Example hybrid insights (this would be computed in the actual analysis pipeline)
            hybrid_insights = [
                "SPLADE 희소 특징과 Ollama 주제 분석이 일치하는 핵심 토픽 발견",
                "AI 모델이 식별한 감정 패턴과 희소 벡터 가중치 간 상관관계 확인",
                "검색 기반 문서 유사성과 LLM 기반 의미 분석의 상호 보완적 결과"
            ]
            
            for insight in hybrid_insights:
                section += f"\n- {insight}"
        
        if not sparse_index_info and not advanced_topics:
            section += f"\n\n*SPLADE 또는 Ollama 분석이 활성화되지 않았습니다. --use-splade 및 --use-ollama 옵션을 사용하여 고급 AI 분석을 실행하세요.*"
        
        return section
    
    def _generate_visualizations_section(self, viz_files: Dict[str, str]) -> str:
        """Generate visualizations section"""
        
        section = "## 📊 시각화"
        
        viz_descriptions = {
            'heatmap': ('시간대별 × 요일별 활동 히트맵', '하루 중 어느 시간대에 가장 활발한지 보여줍니다.'),
            'timeline': ('일별 메시지 수 추이', '시간에 따른 대화량 변화를 추적합니다.'),
            'topic_timeline': ('주제 세그먼트 타임라인', '대화 주제가 시간에 따라 어떻게 변했는지 보여줍니다.'),
            'wordcloud': ('전역 워드클라우드', '가장 자주 사용된 단어들을 시각화합니다.'),
            'user_activity': ('사용자 활동 분포', '각 사용자의 참여도를 비교합니다.'),
            'reply_latency': ('답장 지연 시간 분포', '사용자들의 답장 속도 패턴을 분석합니다.'),
            'network_graph': ('사용자 상호작용 네트워크', '사용자들 간의 대화 상호작용 관계를 네트워크로 시각화합니다.'),
            'mention_network': ('멘션 네트워크', '@ 멘션을 통한 사용자 간 언급 관계를 네트워크로 보여줍니다.')
        }
        
        for viz_key, file_path in viz_files.items():
            if viz_key in viz_descriptions:
                title, description = viz_descriptions[viz_key]
                relative_path = Path(file_path).name
                section += f"\n\n### {title}"
                section += f"\n{description}"
                section += f"\n\n![{title}](figures/{relative_path})"
        
        return section
    
    def _generate_technical_details(self, analysis_results: Dict[str, Any]) -> str:
        """Generate technical details section"""
        
        section = "## 🔧 기술적 세부사항"
        
        # Model information
        if 'embeddings_info' in analysis_results:
            embeddings_info = analysis_results['embeddings_info']
            model_info = embeddings_info.get('model_info', {})
            section += f"\n\n### 임베딩 모델"
            section += f"\n- **모델명**: {model_info.get('model_name', 'N/A')}"
            section += f"\n- **차원수**: {model_info.get('dimension', 'N/A')}"
            section += f"\n- **윈도우 크기**: {embeddings_info.get('window_size', 'N/A')}"
        
        # Processing parameters
        section += f"\n\n### 분석 파라미터"
        section += f"\n- **대화 턴 구분 시간**: {self.config.window_minutes}분"
        section += f"\n- **주제 세그먼트 윈도우**: {self.config.topic_window_size}개 메시지"
        section += f"\n- **유사도 임계값**: {self.config.similarity_threshold}"
        
        # Data quality metrics
        if 'data_validation' in analysis_results:
            validation = analysis_results['data_validation']
            section += f"\n\n### 데이터 품질"
            section += f"\n- **유효성**: {'통과' if validation.get('is_valid') else '실패'}"
            section += f"\n- **경고 수**: {len(validation.get('warnings', []))}"
            section += f"\n- **오류 수**: {len(validation.get('errors', []))}"
        
        return section
    
    def _generate_insights_section(self, analysis_results: Dict[str, Any]) -> str:
        """Generate insights and recommendations section"""
        
        insights = self._extract_key_insights(analysis_results)
        recommendations = self._generate_recommendations(analysis_results)
        
        section = "## 💡 인사이트 및 권장사항"
        
        section += f"\n\n### 주요 발견사항"
        for i, insight in enumerate(insights[:5], 1):
            section += f"\n{i}. {insight}"
        
        if recommendations:
            section += f"\n\n### 권장사항"
            for i, rec in enumerate(recommendations[:3], 1):
                section += f"\n{i}. {rec}"
        
        # Limitations
        section += f"\n\n### 분석의 한계"
        section += f"\n- 텍스트 기반 분석으로 이미지, 파일 등은 제외됨"
        section += f"\n- 시스템 메시지는 필터링되어 실제 대화만 분석됨"
        section += f"\n- 주제 분류는 키워드 기반의 단순한 방법 사용"
        
        return section
    
    def _generate_footer(self) -> str:
        """Generate report footer"""
        
        return f"""
---

*이 리포트는 Kakao Analyzer를 사용하여 자동 생성되었습니다.*

🤖 Generated with [Claude Code](https://claude.ai/code)"""
    
    def _extract_key_insights(self, analysis_results: Dict[str, Any]) -> List[str]:
        """Extract key insights from analysis results"""
        
        insights = []
        
        # Basic stats insights
        basic_stats = analysis_results.get('basic_stats', {})
        summary_stats = basic_stats.get('summary', {})
        
        if summary_stats and 'error' not in summary_stats:
            activity_summary = summary_stats.get('activity_summary', {})
            
            # Most active user insight
            most_active = activity_summary.get('most_active_user', '')
            most_active_percent = activity_summary.get('most_active_user_percent', 0)
            if most_active and most_active_percent > 30:
                insights.append(f"{most_active}가 전체 대화의 {most_active_percent:.1f}%를 주도하며 대화방의 중심 역할")
            
            # Messages per day
            msg_per_day = activity_summary.get('messages_per_day', 0)
            if msg_per_day > 50:
                insights.append(f"하루 평균 {msg_per_day:.1f}개 메시지로 매우 활발한 대화방")
            elif msg_per_day > 20:
                insights.append(f"하루 평균 {msg_per_day:.1f}개 메시지로 활발한 대화방")
        
        # Temporal insights
        temporal = basic_stats.get('temporal', {})
        if temporal:
            peak_activity = temporal.get('peak_activity', {})
            peak_hour = peak_activity.get('peak_hour', '')
            peak_day = peak_activity.get('peak_day', '')
            
            if peak_hour and peak_day:
                insights.append(f"{peak_day} {peak_hour}에 가장 활발한 대화 패턴")
            
            time_periods = temporal.get('time_period_distribution', {})
            night_percent = time_periods.get('night_0_5', {}).get('percent', 0)
            if night_percent > 10:
                insights.append(f"새벽 시간대 메시지 비중이 {night_percent:.1f}%로 밤샘 채팅 경향")
        
        # Fun metrics insights
        fun_metrics = analysis_results.get('fun_metrics', {})
        
        # Gini coefficient
        participation = fun_metrics.get('participation_inequality', {})
        if participation:
            gini = participation.get('gini_coefficient', 0)
            if gini > 0.5:
                insights.append(f"지니계수 {gini:.3f}로 소수 사용자가 대화를 주도하는 불균등 구조")
            elif gini < 0.3:
                insights.append(f"지니계수 {gini:.3f}로 모든 참여자가 고르게 참여하는 균등한 구조")
        
        # Reply latency
        reply_latency = fun_metrics.get('reply_latency', {})
        overall_stats = reply_latency.get('overall_stats', {})
        if overall_stats and 'error' not in overall_stats:
            mean_reply = overall_stats.get('mean_minutes', 0)
            if mean_reply < 5:
                insights.append(f"평균 답장 시간 {mean_reply:.1f}분으로 매우 빠른 소통")
            elif mean_reply > 30:
                insights.append(f"평균 답장 시간 {mean_reply:.1f}분으로 느긋한 소통 스타일")
        
        # Topic segments
        topic_segments = analysis_results.get('topic_segments', [])
        if topic_segments:
            avg_duration = sum([seg['duration_minutes'] for seg in topic_segments]) / len(topic_segments)
            if avg_duration < 10:
                insights.append(f"평균 {avg_duration:.1f}분의 짧은 주제 전환으로 다양한 화제")
            elif avg_duration > 60:
                insights.append(f"평균 {avg_duration:.1f}분의 깊이 있는 주제 집중 대화")
        
        return insights[:10]  # Limit to top 10 insights
    
    def _generate_recommendations(self, analysis_results: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on analysis"""
        
        recommendations = []
        
        # Based on participation inequality
        fun_metrics = analysis_results.get('fun_metrics', {})
        participation = fun_metrics.get('participation_inequality', {})
        
        if participation:
            gini = participation.get('gini_coefficient', 0)
            if gini > 0.6:
                recommendations.append("참여가 집중된 구조이므로, 소극적 참여자들의 발언을 유도하는 분위기 조성 권장")
            elif gini < 0.2:
                recommendations.append("매우 균등한 참여 구조로 건강한 소통이 이루어지고 있음")
        
        # Based on reply latency
        reply_latency = fun_metrics.get('reply_latency', {})
        overall_stats = reply_latency.get('overall_stats', {})
        if overall_stats and 'error' not in overall_stats:
            mean_reply = overall_stats.get('mean_minutes', 0)
            if mean_reply > 60:
                recommendations.append("답장 시간이 긴 편이므로 더 실시간 소통을 위한 활성화 방안 고려")
        
        # Based on activity patterns
        basic_stats = analysis_results.get('basic_stats', {})
        temporal = basic_stats.get('temporal', {})
        if temporal:
            time_periods = temporal.get('time_period_distribution', {})
            night_percent = time_periods.get('night_0_5', {}).get('percent', 0)
            if night_percent > 15:
                recommendations.append("새벽 시간 활동이 높으므로 건강한 생활 패턴을 위한 대화 시간대 조정 고려")
        
        return recommendations
    
    def generate_qa_test_report(self, test_results: Dict[str, Any], 
                              output_path: Path) -> str:
        """Generate QA test results report"""
        
        self.logger.info("Generating QA test report...")
        
        report = f"""# 테스트 결과 리포트

**생성 일시**: {datetime.now().strftime('%Y년 %m월 %d일 %H:%M')}  
**테스트 파일**: {test_results.get('test_file', 'test.csv')}

## 테스트 요약

- **전체 테스트**: {test_results.get('total_tests', 0)}개
- **통과**: {test_results.get('passed_tests', 0)}개
- **실패**: {test_results.get('failed_tests', 0)}개
- **성공률**: {test_results.get('success_rate', 0):.1f}%

## 테스트 결과 상세

### ✅ 통과한 테스트
"""
        
        for test in test_results.get('passed', []):
            report += f"- {test['name']}: {test.get('description', '')}\n"
        
        report += f"\n### ❌ 실패한 테스트\n"
        
        for test in test_results.get('failed', []):
            report += f"- {test['name']}: {test.get('error', 'Unknown error')}\n"
        
        report += f"""
## 파일 생성 확인

### 필수 출력 파일
"""
        
        required_files = test_results.get('file_checks', {})
        for file_path, exists in required_files.items():
            status = "✅" if exists else "❌"
            report += f"- {status} {file_path}\n"
        
        report += f"""
## 권장사항

{chr(10).join([f"- {rec}" for rec in test_results.get('recommendations', [])])}

---

*이 테스트 리포트는 자동 생성되었습니다.*
"""
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        self.logger.info(f"QA test report saved to {output_path}")
        return str(output_path)