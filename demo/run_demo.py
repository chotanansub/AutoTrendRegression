#!/usr/bin/env python3
"""
Main demo runner for autotrend package.
Runs all demos and exports logs + figures.

Usage:
    python demos/run_demo.py
"""
import os
import sys
import logging
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from demo_simple_wave import run_simple_wave_demo
from demo_behavioral import run_behavioral_demo


def setup_logging():
    """Setup logging configuration"""
    # Create output directories
    log_dir = Path('outputs/logs')
    fig_dir = Path('outputs/figures')
    log_dir.mkdir(parents=True, exist_ok=True)
    fig_dir.mkdir(parents=True, exist_ok=True)
    
    # Create timestamped log file
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = log_dir / f'demo_run_{timestamp}.log'
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return log_file, timestamp


def main():
    """Run all demos"""
    log_file, timestamp = setup_logging()
    
    logging.info("="*80)
    logging.info("AUTOTREND DEMO RUNNER")
    logging.info("="*80)
    logging.info(f"Timestamp: {timestamp}")
    logging.info(f"Log file: {log_file}")
    logging.info(f"Figures will be saved to: outputs/figures/")
    logging.info("")
    
    demos = [
        ("Simple Wave Demo", run_simple_wave_demo),
        ("Behavioral Sequence Demo", run_behavioral_demo),
    ]
    
    for demo_name, demo_func in demos:
        logging.info("="*80)
        logging.info(f"Running: {demo_name}")
        logging.info("="*80)
        
        try:
            demo_func(timestamp)
            logging.info(f"✓ {demo_name} completed successfully")
        except Exception as e:
            logging.error(f"✗ {demo_name} failed: {str(e)}")
            import traceback
            logging.error(traceback.format_exc())
        
        logging.info("")
    
    logging.info("="*80)
    logging.info("ALL DEMOS COMPLETED")
    logging.info("="*80)
    logging.info(f"Check outputs/logs/{log_file.name} for full log")
    logging.info(f"Check outputs/figures/ for generated plots")


if __name__ == "__main__":
    main()