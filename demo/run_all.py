#!/usr/bin/env python3
"""
Run all predefined LLT demos and save outputs.
Usage: python demo/run_all.py
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import demo cases
from demo.cases import piecewise_linear, simple_wave, nonstationary


def main():
    """Run all demos sequentially."""
    print(f"\n{'#'*60}")
    print(f"# LLT Demo Suite")
    print(f"# Running all demos")
    print(f"# Output directory: output/")
    print(f"# Generating 5 plots per demo:")
    print(f"#   - Error analysis plot")
    print(f"#   - Slope comparison plot")
    print(f"#   - Full decomposition plot")
    print(f"#   - Iteration grid plot")
    print(f"#   - Model statistics plot")
    print(f"{'#'*60}")
    
    demos = [
        ("Piecewise Linear", piecewise_linear),
        ("Simple Wave", simple_wave),
        ("Nonstationary Wave", nonstationary)
    ]
    
    for demo_name, demo_module in demos:
        try:
            print(f"\n>>> Running {demo_name} Demos...")
            demo_module.main()
        except Exception as e:
            print(f"\n❌ Error in {demo_name} demos: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n{'#'*60}")
    print(f"# All demos completed!")
    print(f"# Check 'output/' for results")
    print(f"# Each demo generated 5 visualization plots + 1 log file")
    print(f"{'#'*60}\n")


if __name__ == "__main__":
    main()