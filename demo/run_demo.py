"""
Main demo runner for Local Linear Trend (LLT) examples.

This script runs all available demos in sequence.
"""

import sys
import os

# Add parent directory to path to import autotrend
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def main():
    print("\n" + "=" * 80)
    print(" " * 20 + "LOCAL LINEAR TREND (LLT) DEMOS")
    print("=" * 80)
    print("\nThis will run all available demos in sequence.")
    print("Close each plot window to proceed to the next demo.")
    print("\n" + "=" * 80 + "\n")
    
    input("Press Enter to start...")
    
    # ============================================================
    # Demo 1: Simple Wave
    # ============================================================
    try:
        print("\n" + "=" * 80)
        print("DEMO 1: Simple Wave with Noise")
        print("=" * 80)
        
        from demo_simple_wave import main as run_simple_wave
        run_simple_wave()
        
        print("\n✅ Demo 1 Complete!\n")
        input("Press Enter to continue to Demo 2...")
        
    except Exception as e:
        print(f"\n❌ Error in Demo 1: {e}")
        import traceback
        traceback.print_exc()
    
    # ============================================================
    # Demo 2: Behavioral Sequence
    # ============================================================
    try:
        print("\n" + "=" * 80)
        print("DEMO 2: Behavioral Sequence")
        print("=" * 80)
        
        from demo_behavioral import main as run_behavioral
        run_behavioral()
        
        print("\n✅ Demo 2 Complete!\n")
        
    except Exception as e:
        print(f"\n❌ Error in Demo 2: {e}")
        import traceback
        traceback.print_exc()
    
    # ============================================================
    # Completion
    # ============================================================
    print("\n" + "=" * 80)
    print(" " * 25 + "ALL DEMOS COMPLETE! ✨")
    print("=" * 80)
    print("\nThank you for trying the Local Linear Trend (LLT) method!")
    print("\nFor more information, check out:")
    print("  - README.md")
    print("  - Google Colab: https://colab.research.google.com/drive/1jifMsj8nI_ZV-FL3ZScFP4wJJLQp97jH")
    print("\n" + "=" * 80 + "\n")


if __name__ == "__main__":
    main()