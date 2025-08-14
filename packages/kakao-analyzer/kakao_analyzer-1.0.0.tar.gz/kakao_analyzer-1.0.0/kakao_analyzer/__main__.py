"""Main CLI entry point for Kakao Analyzer"""

import argparse
import sys
from pathlib import Path
import logging
from datetime import datetime
import traceback

from .config import Config
from .utils import setup_logger, create_output_structure
from .pipeline import KakaoAnalysisPipeline


def create_parser() -> argparse.ArgumentParser:
    """Create command line argument parser"""
    parser = argparse.ArgumentParser(
        description="Kakao Talk CSV Analyzer - 카카오톡 대화 분석기",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  kakao-analyzer --input test.csv
  kakao-analyzer --input test.csv --use-ollama --model-name oss:20b
  kakao-analyzer --input test.csv --use-splade --embed-model bge-m3
        """
    )
    
    # Required arguments
    parser.add_argument(
        '--input', 
        required=True,
        help='Path to input CSV file'
    )
    
    # Optional arguments
    parser.add_argument(
        '--outdir',
        help='Output directory (default: <input_filename>_analysis/)'
    )
    
    parser.add_argument(
        '--language', 
        default='ko',
        choices=['ko', 'en'],
        help='Analysis language (default: ko)'
    )
    
    # Model settings
    parser.add_argument(
        '--use-ollama',
        action='store_true',
        help='Use local Ollama for text generation'
    )
    
    parser.add_argument(
        '--model-name',
        default='oss:20b',
        help='Ollama model name (default: oss:20b)'
    )
    
    parser.add_argument(
        '--embed-model',
        default='bge-m3',
        help='Embedding model name (default: bge-m3)'
    )
    
    parser.add_argument(
        '--use-splade',
        action='store_true',
        help='Use SPLADE for sparse retrieval'
    )
    
    # Analysis parameters
    parser.add_argument(
        '--window-minutes',
        type=int,
        default=30,
        help='Time window for conversation turns (default: 30)'
    )
    
    parser.add_argument(
        '--topic-window',
        type=int,
        default=15,
        help='Message window for topic analysis (default: 15)'
    )
    
    parser.add_argument(
        '--topic-window-size',
        type=int,
        default=15,
        help='Message window size for topic analysis (alias for --topic-window)'
    )
    
    parser.add_argument(
        '--similarity-threshold',
        type=float,
        default=0.3,
        help='Similarity threshold for topic segmentation (default: 0.3)'
    )
    
    parser.add_argument(
        '--figure-dpi',
        type=int,
        default=300,
        help='DPI for generated figures (default: 300)'
    )
    
    # Processing settings
    parser.add_argument(
        '--batch-size',
        type=int,
        default=32,
        help='Batch size for embeddings (default: 32)'
    )
    
    parser.add_argument(
        '--max-workers',
        type=int,
        default=4,
        help='Maximum worker threads (default: 4)'
    )
    
    # Output settings
    parser.add_argument(
        '--log-level',
        default='INFO',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        help='Logging level (default: INFO)'
    )
    
    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Suppress console output'
    )
    
    parser.add_argument(
        '--skip-viz',
        action='store_true',
        help='Skip visualization generation'
    )
    
    parser.add_argument(
        '--subset-size',
        type=int,
        help='Create intelligent subset of specified size for large datasets'
    )
    
    parser.add_argument(
        '--subset-strategy',
        default='balanced',
        choices=['balanced', 'temporal', 'diverse', 'random'],
        help='Strategy for creating dataset subset (default: balanced)'
    )
    
    # KakaoTalk-specific options
    parser.add_argument(
        '--disable-message-grouping',
        action='store_true',
        help='Disable automatic grouping of consecutive messages (카톡 특성 고려 안함)'
    )
    
    parser.add_argument(
        '--group-window-seconds',
        type=int,
        default=60,
        help='Time window for grouping consecutive messages in seconds (default: 60)'
    )
    
    return parser


def main():
    """Main entry point"""
    parser = create_parser()
    args = parser.parse_args()
    
    # Validate input file
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}")
        sys.exit(1)
    
    # Determine output directory
    if args.outdir:
        output_dir = Path(args.outdir)
    else:
        output_dir = input_path.parent / f"{input_path.stem}_analysis"
    
    # Create output structure
    output_dirs = create_output_structure(output_dir)
    
    # Setup logging
    log_file = output_dirs['logs'] / 'run.log'
    logger = setup_logger(str(log_file), args.log_level)
    
    if args.quiet:
        # Suppress console logging
        logger.handlers = [h for h in logger.handlers if not isinstance(h, logging.StreamHandler)]
    
    # Create configuration
    config = Config.from_args(args)
    config.output_dir = str(output_dir)
    
    logger.info("="*60)
    logger.info("Kakao Talk CSV Analyzer Starting")
    logger.info("="*60)
    logger.info(f"Input file: {input_path}")
    logger.info(f"Output directory: {output_dir}")
    logger.info(f"Configuration: {config}")
    
    try:
        # Run analysis pipeline
        pipeline = KakaoAnalysisPipeline(config, logger)
        results = pipeline.run_full_analysis(Path(input_path), output_dir)
        
        logger.info("="*60)
        logger.info("Analysis completed successfully!")
        logger.info("="*60)
        
        # Print key insights to console
        if not args.quiet and results.get('insights'):
            print("\n🎯 주요 인사이트:")
            for insight in results['insights'][:3]:
                print(f"  • {insight}")
        
        print(f"\n📁 결과 저장 위치: {output_dir}")
        print(f"📊 분석 리포트: {output_dirs['reports'] / 'analysis_report.md'}")
        
        return 0
        
    except KeyboardInterrupt:
        logger.error("Analysis interrupted by user")
        return 130
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        logger.error(traceback.format_exc())
        return 1


if __name__ == '__main__':
    sys.exit(main())