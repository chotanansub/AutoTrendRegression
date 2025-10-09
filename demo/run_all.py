#!/usr/bin/env python3
"""
Run all predefined LLT demos and save outputs.
Usage: python demo/run_all.py
"""
from demo_utils import get_demo_configs, run_single_demo


def main():
    """Run all demos sequentially."""
    configs = get_demo_configs()
    
    print(f"\n{'#'*60}")
    print(f"# LLT Demo Suite")
    print(f"# Running {len(configs)} demos")
    print(f"# Output directory: output/")
    print(f"{'#'*60}")
    
    for key, config in configs.items():
        try:
            run_single_demo(config, verbose=False)
        except Exception as e:
            print(f"\n❌ Error in '{config.name}': {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n{'#'*60}")
    print(f"# All demos completed!")
    print(f"# Check 'output/' for results")
    print(f"{'#'*60}\n")


if __name__ == "__main__":
    main()