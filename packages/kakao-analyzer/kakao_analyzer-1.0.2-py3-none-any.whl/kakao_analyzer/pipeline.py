"""Main analysis pipeline orchestrator"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
from pathlib import Path
import logging
import json
from datetime import datetime
import traceback

from .config import Config
from .io_loader import KakaoDataLoader
from .stats_basic import BasicStatsCalculator
from .turn_splitter import TurnSplitter
from .embeddings import EmbeddingManager
from .context_topics import TopicAnalyzer
from .fun_metrics import FunMetricsCalculator
from .splade import HybridRetriever
from .viz import KakaoVisualizer
from .report import ReportGenerator
from .mood_analyzer import ConversationMoodAnalyzer
from .smart_search import ConversationTopicAnalyzer
from .rhythm_analyzer import ConversationRhythmAnalyzer
from .dataset_optimizer import DatasetOptimizer
from .chat_preprocessor import KakaoTalkPreprocessor
from .mention_analyzer import KakaoTalkMentionAnalyzer
from .topic_sentiment_analyzer import TopicSentimentAnalyzer
from .utils import setup_logger, create_output_directories


class KakaoAnalysisPipeline:
    """Main pipeline orchestrator for Kakao analysis"""
    
    def __init__(self, config: Config, logger: logging.Logger = None):
        self.config = config
        self.logger = logger or setup_logger("pipeline")
        
        # Initialize components
        self.data_loader = KakaoDataLoader(self.logger)
        self.stats_calculator = BasicStatsCalculator(self.logger)
        self.turn_splitter = TurnSplitter(config, self.logger)
        self.embedding_manager = EmbeddingManager(config, self.logger)
        self.topic_analyzer = TopicAnalyzer(config, self.logger)
        self.fun_metrics = FunMetricsCalculator(config, self.logger)
        
        # Pass device info to HybridRetriever
        device_info = getattr(self.embedding_manager, 'device_info', {'device': 'cpu'})
        self.hybrid_retriever = HybridRetriever(config, self.logger, device_info)
        self.visualizer = KakaoVisualizer(config, self.logger)
        self.report_generator = ReportGenerator(config, self.logger)
        
        # Advanced analyzers
        self.mood_analyzer = ConversationMoodAnalyzer(config, self.logger)
        self.topic_analyzer_advanced = ConversationTopicAnalyzer(config, self.logger)
        self.rhythm_analyzer = ConversationRhythmAnalyzer(config, self.logger)
        self.dataset_optimizer = DatasetOptimizer(config, self.logger)
        self.chat_preprocessor = KakaoTalkPreprocessor(self.logger)
        self.mention_analyzer = KakaoTalkMentionAnalyzer(self.logger)
        self.topic_sentiment_analyzer = TopicSentimentAnalyzer(self.logger)
    
    def run_full_analysis(self, input_csv: Path, output_dir: Path) -> Dict[str, Any]:
        """Run complete analysis pipeline"""
        
        self.logger.info(f"Starting full analysis pipeline for {input_csv}")
        start_time = datetime.now()
        
        try:
            # Create output directory structure
            output_paths = create_output_directories(output_dir)
            
            # 1. Load and validate data
            self.logger.info("Step 1: Loading and validating data...")
            df, data_info, validation_results = self.data_loader.load_and_validate(input_csv)
            
            if not validation_results['is_valid']:
                raise ValueError(f"Data validation failed: {validation_results['errors']}")
            
            # 1.3. KakaoTalk-specific preprocessing (message grouping)
            self.logger.info("Step 1.3: Applying KakaoTalk-specific preprocessing...")
            df_processed, chat_metadata = self.chat_preprocessor.preprocess_for_analysis(
                df, group_messages=self.config.enable_message_grouping
            )
            self.logger.info(f"Message grouping: {chat_metadata['original_message_count']} → {chat_metadata['processed_message_count']} "
                           f"({chat_metadata['reduction_ratio']:.1f}% reduction)")
            
            # Use processed dataframe for analysis
            df = df_processed
            
            # 1.5. Dataset optimization analysis
            self.logger.info("Step 1.5: Analyzing dataset size and optimizing processing...")
            dataset_analysis = self.dataset_optimizer.analyze_dataset_size(df)
            self.logger.info(f"Dataset category: {dataset_analysis['dataset_category']} ({dataset_analysis['total_messages']} messages)")
            
            # Apply optimizations if needed
            optimized_config = self.dataset_optimizer.optimize_processing_config(df, {
                'batch_size': self.config.batch_size,
                'topic_window_size': self.config.topic_window_size,
                'max_workers': self.config.max_workers
            })
            
            # Update config with optimizations
            if optimized_config.get('memory_efficient_mode'):
                self.logger.info("🔧 Enabling memory-efficient processing mode")
            if optimized_config.get('embedding_batch_size') != self.config.batch_size:
                self.logger.info(f"🔧 Optimized batch size: {optimized_config['embedding_batch_size']}")
            
            # Memory usage estimation
            memory_estimate = self.dataset_optimizer.estimate_memory_usage(df, True, self.config.use_splade)
            self.logger.info(f"💾 Estimated memory usage: {memory_estimate['total_estimated_mb']:.1f} MB")
            
            # 2. Basic statistics
            self.logger.info("Step 2: Calculating basic statistics...")
            basic_stats = self.stats_calculator.calculate_all_stats(df)
            
            # 3. Turn analysis
            self.logger.info("Step 3: Analyzing conversation turns...")
            turn_analysis = self.turn_splitter.split_turns(df)
            
            # 4. Embeddings and topic analysis (with optimization)
            self.logger.info("Step 4: Generating embeddings and analyzing topics...")
            # Use optimized batch size
            original_batch_size = self.config.batch_size
            if 'embedding_batch_size' in optimized_config:
                self.config.batch_size = optimized_config['embedding_batch_size']
            
            embeddings_data = self.embedding_manager.create_embeddings(df)
            
            # Restore original batch size
            self.config.batch_size = original_batch_size
            topic_segments = self.topic_analyzer.detect_topic_segments(df, embeddings_data)
            topic_analysis = self.topic_analyzer.analyze_topic_shifts(topic_segments, df)
            
            # 5. Fun metrics
            self.logger.info("Step 5: Calculating fun metrics...")
            fun_metrics = self.fun_metrics.calculate_all_metrics(df)
            
            # 6. Advanced mood analysis
            self.logger.info("Step 6: Analyzing conversation mood and emotions...")
            mood_analysis = self.mood_analyzer.analyze_conversation_mood(df)
            
            # 7. Advanced topic analysis
            self.logger.info("Step 7: Advanced topic clustering and search index...")
            advanced_topics = self.topic_analyzer_advanced.analyze_conversation_topics(df, embeddings_data)
            
            # 8. Conversation rhythm analysis
            self.logger.info("Step 8: Analyzing conversation rhythm and timing...")
            rhythm_analysis = self.rhythm_analyzer.analyze_conversation_rhythm(df)
            
            # 8.5. Mention analysis (KakaoTalk @ feature)
            self.logger.info("Step 8.5: Analyzing mention patterns (@username)...")
            mention_analysis = self.mention_analyzer.analyze_mentions(df)
            
            # 8.7. Topic-level sentiment analysis
            self.logger.info("Step 8.7: Analyzing topic-level sentiment and context...")
            topic_sentiment = self.topic_sentiment_analyzer.analyze_topic_segments_sentiment(topic_segments, df)
            
            # 9. Hybrid retrieval (if enabled)
            sparse_index = None
            if self.config.use_splade:
                self.logger.info("Step 9: Creating sparse index...")
                sparse_index = self.hybrid_retriever.create_sparse_index(df)
                self.hybrid_retriever.save_sparse_index(sparse_index, output_paths['context'])
            
            # 10. Compile results
            analysis_results = {
                'version': '1.2.0',  # Updated version for KakaoTalk features
                'analysis_timestamp': datetime.now().isoformat(),
                'data_info': data_info,
                'data_validation': validation_results,
                'chat_preprocessing': chat_metadata,  # New: KakaoTalk preprocessing info
                'basic_stats': basic_stats,
                'turn_analysis': turn_analysis,
                'embeddings_info': {
                    'model_info': embeddings_data.get('model_info', {}),
                    'window_size': self.config.topic_window_size,
                    'total_windows': len(embeddings_data.get('window_embeddings', []))
                },
                'topic_segments': topic_segments,
                'topic_analysis': topic_analysis,
                'fun_metrics': fun_metrics,
                'sparse_index_info': sparse_index.get('statistics', {}) if sparse_index else None,
                # New advanced features
                'mood_analysis': mood_analysis,
                'advanced_topics': advanced_topics,
                'rhythm_analysis': rhythm_analysis,
                'mention_analysis': mention_analysis,
                'topic_sentiment': topic_sentiment
            }
            
            # 11. Save structured data
            self.logger.info("Step 11: Saving structured analysis data...")
            self._save_structured_data(analysis_results, output_paths, df, topic_segments)
            
            # 12. Generate visualizations
            self.logger.info("Step 12: Creating visualizations...")
            viz_files = self.visualizer.create_all_visualizations(analysis_results, output_paths['figures'])
            
            # 13. Generate reports
            self.logger.info("Step 13: Generating reports...")
            report_path = self.report_generator.generate_analysis_report(
                analysis_results, 
                output_paths['reports'] / 'analysis_report.md',
                viz_files
            )
            
            # 14. Save pipeline metadata
            pipeline_duration = (datetime.now() - start_time).total_seconds()
            pipeline_metadata = {
                'input_file': str(input_csv),
                'output_directory': str(output_dir),
                'start_time': start_time.isoformat(),
                'end_time': datetime.now().isoformat(),
                'duration_seconds': pipeline_duration,
                'config': self.config.__dict__,
                'data_summary': {
                    'total_messages': len(df),
                    'unique_users': df['user'].nunique(),
                    'date_range': {
                        'start': df['datetime'].min().isoformat(),
                        'end': df['datetime'].max().isoformat()
                    }
                },
                'output_files': {
                    'report': report_path,
                    'visualizations': viz_files,
                    'structured_data': {
                        'basic_stats': str(output_paths['basics'] / 'basic_statistics.json'),
                        'topic_segments': str(output_paths['context'] / 'topic_segments.json'),
                        'fun_metrics': str(output_paths['fun'] / 'fun_metrics.json')
                    }
                }
            }
            
            with open(output_paths['logs'] / 'pipeline_metadata.json', 'w', encoding='utf-8') as f:
                json.dump(pipeline_metadata, f, ensure_ascii=False, indent=2, default=str)
            
            self.logger.info(f"Pipeline completed successfully in {pipeline_duration:.1f}s")
            self.logger.info(f"Report saved to: {report_path}")
            
            return {
                'success': True,
                'analysis_results': analysis_results,
                'output_paths': output_paths,
                'report_path': report_path,
                'duration_seconds': pipeline_duration
            }
            
        except Exception as e:
            error_msg = f"Pipeline failed: {str(e)}"
            self.logger.error(error_msg)
            self.logger.error(traceback.format_exc())
            
            return {
                'success': False,
                'error': error_msg,
                'traceback': traceback.format_exc()
            }
    
    def _save_structured_data(self, analysis_results: Dict[str, Any], 
                            output_paths: Dict[str, Path], 
                            df: pd.DataFrame, 
                            topic_segments: list) -> None:
        """Save structured analysis data to files"""
        
        # Save basic statistics
        if 'basic_stats' in analysis_results:
            with open(output_paths['basics'] / 'basic_statistics.json', 'w', encoding='utf-8') as f:
                json.dump(analysis_results['basic_stats'], f, ensure_ascii=False, indent=2, default=str)
        
        # Save topic analysis
        if topic_segments:
            with open(output_paths['context'] / 'topic_segments.json', 'w', encoding='utf-8') as f:
                json.dump(topic_segments, f, ensure_ascii=False, indent=2, default=str)
            
            # Export topic segments as CSV
            topic_df = self.topic_analyzer.export_segments(topic_segments)
            topic_df.to_csv(output_paths['context'] / 'topic_segments.csv', index=False, encoding='utf-8')
        
        # Save fun metrics
        if 'fun_metrics' in analysis_results:
            with open(output_paths['fun'] / 'fun_metrics.json', 'w', encoding='utf-8') as f:
                json.dump(analysis_results['fun_metrics'], f, ensure_ascii=False, indent=2, default=str)
        
        # Save advanced analysis results
        if 'mood_analysis' in analysis_results:
            with open(output_paths['context'] / 'mood_analysis.json', 'w', encoding='utf-8') as f:
                json.dump(analysis_results['mood_analysis'], f, ensure_ascii=False, indent=2, default=str)
        
        if 'advanced_topics' in analysis_results:
            with open(output_paths['context'] / 'advanced_topics.json', 'w', encoding='utf-8') as f:
                json.dump(analysis_results['advanced_topics'], f, ensure_ascii=False, indent=2, default=str)
        
        if 'rhythm_analysis' in analysis_results:
            with open(output_paths['context'] / 'rhythm_analysis.json', 'w', encoding='utf-8') as f:
                json.dump(analysis_results['rhythm_analysis'], f, ensure_ascii=False, indent=2, default=str)
        
        if 'mention_analysis' in analysis_results:
            with open(output_paths['context'] / 'mention_analysis.json', 'w', encoding='utf-8') as f:
                json.dump(analysis_results['mention_analysis'], f, ensure_ascii=False, indent=2, default=str)
        
        if 'topic_sentiment' in analysis_results:
            with open(output_paths['context'] / 'topic_sentiment.json', 'w', encoding='utf-8') as f:
                json.dump(analysis_results['topic_sentiment'], f, ensure_ascii=False, indent=2, default=str)
        
        # Save processed dataset with additional columns
        enriched_df = df.copy()
        if topic_segments:
            # Add topic segment IDs to messages
            segment_map = {}
            for segment in topic_segments:
                start_time = segment['start_time']
                end_time = segment['end_time']
                mask = (enriched_df['datetime'] >= start_time) & (enriched_df['datetime'] <= end_time)
                enriched_df.loc[mask, 'topic_segment_id'] = segment['segment_id']
        
        enriched_df.to_csv(output_paths['summary'] / 'processed_messages.csv', index=False, encoding='utf-8')
        
        # Save summary statistics
        summary_stats = {
            'total_messages': len(df),
            'unique_users': df['user'].nunique(),
            'date_range': {
                'start': df['datetime'].min().isoformat(),
                'end': df['datetime'].max().isoformat(),
                'total_days': (df['datetime'].max() - df['datetime'].min()).days + 1
            },
            'activity_summary': {
                'messages_per_day': len(df) / max(1, (df['datetime'].max() - df['datetime'].min()).days + 1),
                'most_active_user': df['user'].value_counts().index[0],
                'most_active_user_count': df['user'].value_counts().iloc[0],
                'most_active_user_percent': (df['user'].value_counts().iloc[0] / len(df)) * 100
            },
            'topic_summary': {
                'total_segments': len(topic_segments),
                'avg_segment_duration': np.mean([s['duration_minutes'] for s in topic_segments]) if topic_segments else 0,
                'avg_messages_per_segment': np.mean([s['message_count'] for s in topic_segments]) if topic_segments else 0
            }
        }
        
        with open(output_paths['summary'] / 'analysis_summary.json', 'w', encoding='utf-8') as f:
            json.dump(summary_stats, f, ensure_ascii=False, indent=2, default=str)
    
    def test_pipeline_components(self, test_df: pd.DataFrame) -> Dict[str, Any]:
        """Test individual pipeline components"""
        
        test_results = {
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'passed': [],
            'failed': [],
            'success_rate': 0.0
        }
        
        # Test data loader
        try:
            data_info, validation = self.data_loader.get_data_info(test_df), self.data_loader.validate_dataframe(test_df)
            test_results['passed'].append({'name': 'data_loader', 'description': 'Data loading and validation'})
            test_results['passed_tests'] += 1
        except Exception as e:
            test_results['failed'].append({'name': 'data_loader', 'error': str(e)})
            test_results['failed_tests'] += 1
        test_results['total_tests'] += 1
        
        # Test basic stats
        try:
            basic_stats = self.stats_calculator.calculate_all_stats(test_df)
            test_results['passed'].append({'name': 'basic_stats', 'description': 'Basic statistics calculation'})
            test_results['passed_tests'] += 1
        except Exception as e:
            test_results['failed'].append({'name': 'basic_stats', 'error': str(e)})
            test_results['failed_tests'] += 1
        test_results['total_tests'] += 1
        
        # Test turn splitter
        try:
            turn_analysis = self.turn_splitter.split_turns(test_df)
            test_results['passed'].append({'name': 'turn_splitter', 'description': 'Conversation turn analysis'})
            test_results['passed_tests'] += 1
        except Exception as e:
            test_results['failed'].append({'name': 'turn_splitter', 'error': str(e)})
            test_results['failed_tests'] += 1
        test_results['total_tests'] += 1
        
        # Test embeddings
        try:
            embeddings_data = self.embedding_manager.create_embeddings(test_df)
            test_results['passed'].append({'name': 'embeddings', 'description': 'Embedding generation'})
            test_results['passed_tests'] += 1
        except Exception as e:
            test_results['failed'].append({'name': 'embeddings', 'error': str(e)})
            test_results['failed_tests'] += 1
        test_results['total_tests'] += 1
        
        # Test topic analysis
        try:
            embeddings_data = self.embedding_manager.create_embeddings(test_df)
            topic_segments = self.topic_analyzer.detect_topic_segments(test_df, embeddings_data)
            test_results['passed'].append({'name': 'topic_analysis', 'description': 'Topic segmentation'})
            test_results['passed_tests'] += 1
        except Exception as e:
            test_results['failed'].append({'name': 'topic_analysis', 'error': str(e)})
            test_results['failed_tests'] += 1
        test_results['total_tests'] += 1
        
        # Test fun metrics
        try:
            fun_metrics = self.fun_metrics.calculate_all_metrics(test_df)
            test_results['passed'].append({'name': 'fun_metrics', 'description': 'Fun metrics calculation'})
            test_results['passed_tests'] += 1
        except Exception as e:
            test_results['failed'].append({'name': 'fun_metrics', 'error': str(e)})
            test_results['failed_tests'] += 1
        test_results['total_tests'] += 1
        
        test_results['success_rate'] = (test_results['passed_tests'] / test_results['total_tests']) * 100
        
        return test_results