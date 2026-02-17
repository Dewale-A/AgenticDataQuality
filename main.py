#!/usr/bin/env python3
"""
Agentic Data Quality Assessment Tool

A multi-agent AI system for automated data quality profiling, validation,
and assessment with special focus on Critical Data Elements (CDEs).

Usage:
    python main.py                              # Interactive mode
    python main.py --data sample_data/customers.csv
    python main.py --data data.csv --cde cde_config.json
    python main.py --list                       # List sample files
"""
import argparse
import os
import sys
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.crew import DataQualityCrew
from src.config.settings import OUTPUT_DIR


def list_sample_files():
    """List available sample data files."""
    sample_dir = os.path.join(os.path.dirname(__file__), "sample_data")
    print("\n📁 Available Sample Files:")
    print("-" * 40)
    
    for f in os.listdir(sample_dir):
        filepath = os.path.join(sample_dir, f)
        size = os.path.getsize(filepath)
        print(f"  • {f} ({size:,} bytes)")
    
    print("\nUsage: python main.py --data sample_data/<filename>")
    print()


def run_assessment(data_file: str, cde_config: str = "", polish: bool = False) -> str:
    """Run the data quality assessment.
    
    Args:
        data_file: Path to the data file
        cde_config: Path to CDE configuration (optional)
        polish: Whether to include Senior Editor for executive polish
        
    Returns:
        Path to the generated report
    """
    # Validate inputs
    if not os.path.exists(data_file):
        raise FileNotFoundError(f"Data file not found: {data_file}")
    
    if cde_config and not os.path.exists(cde_config):
        raise FileNotFoundError(f"CDE config not found: {cde_config}")
    
    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    print("\n" + "=" * 60)
    print("🔍 AGENTIC DATA QUALITY ASSESSMENT")
    print("=" * 60)
    print(f"📄 Data File: {data_file}")
    if cde_config:
        print(f"📋 CDE Config: {cde_config}")
    if polish:
        print(f"✨ Executive Polish: ENABLED (Senior Editor will review)")
    print(f"🕐 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60 + "\n")
    
    # Create and run crew
    crew = DataQualityCrew(data_file, cde_config, polish=polish)
    result = crew.run()
    
    # Generate report filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    data_name = os.path.splitext(os.path.basename(data_file))[0]
    report_path = os.path.join(OUTPUT_DIR, f"dq_assessment_{data_name}_{timestamp}.md")
    
    # Save report
    with open(report_path, 'w') as f:
        f.write(str(result))
    
    print("\n" + "=" * 60)
    print("✅ ASSESSMENT COMPLETE")
    print("=" * 60)
    print(f"📊 Report saved to: {report_path}")
    print("=" * 60 + "\n")
    
    return report_path


def interactive_mode():
    """Run in interactive mode."""
    print("\n" + "=" * 60)
    print("🔍 AGENTIC DATA QUALITY ASSESSMENT TOOL")
    print("=" * 60)
    print("\nThis tool uses AI agents to assess data quality with")
    print("special focus on Critical Data Elements (CDEs).")
    print()
    
    # List sample files
    sample_dir = os.path.join(os.path.dirname(__file__), "sample_data")
    print("📁 Sample files available:")
    for f in os.listdir(sample_dir):
        print(f"   • sample_data/{f}")
    print()
    
    # Get data file
    data_file = input("Enter data file path (or press Enter for sample): ").strip()
    if not data_file:
        data_file = os.path.join(sample_dir, "customers.csv")
        print(f"Using sample: {data_file}")
    
    # Get CDE config
    cde_config = input("Enter CDE config path (or press Enter to skip): ").strip()
    if not cde_config:
        default_cde = os.path.join(sample_dir, "cde_config.json")
        if os.path.exists(default_cde):
            use_default = input(f"Use default CDE config? (Y/n): ").strip().lower()
            if use_default != 'n':
                cde_config = default_cde
                print(f"Using CDE config: {cde_config}")
    
    # Ask about executive polish
    polish_input = input("Enable executive polish (Senior Editor review)? (y/N): ").strip().lower()
    polish = polish_input == 'y'
    if polish:
        print("✨ Executive polish enabled - report will be reviewed by Senior Editor")
    
    # Run assessment
    try:
        report_path = run_assessment(data_file, cde_config, polish=polish)
        print(f"\n📖 To view report: cat {report_path}")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Agentic Data Quality Assessment Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                                    # Interactive mode
  python main.py --data sample_data/customers.csv  # Assess sample data
  python main.py --data data.csv --cde cde.json    # With CDE config
  python main.py --data data.csv --polish          # With executive polish
  python main.py --data data.csv -c cde.json -p    # Full assessment with polish
  python main.py --list                            # List sample files
        """
    )
    
    parser.add_argument(
        "--data", "-d",
        help="Path to data file (CSV or JSON)"
    )
    parser.add_argument(
        "--cde", "-c",
        help="Path to CDE configuration file (JSON)"
    )
    parser.add_argument(
        "--polish", "-p",
        action="store_true",
        help="Enable executive polish (Senior Editor reviews report)"
    )
    parser.add_argument(
        "--list", "-l",
        action="store_true",
        help="List available sample files"
    )
    
    args = parser.parse_args()
    
    if args.list:
        list_sample_files()
        return
    
    if args.data:
        # Direct mode with arguments
        try:
            run_assessment(args.data, args.cde or "", polish=args.polish)
        except Exception as e:
            print(f"\n❌ Error: {e}")
            sys.exit(1)
    else:
        # Interactive mode
        interactive_mode()


if __name__ == "__main__":
    main()
