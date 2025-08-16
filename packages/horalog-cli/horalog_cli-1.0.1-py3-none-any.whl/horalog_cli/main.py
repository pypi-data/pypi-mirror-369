"""
Main CLI entry point for HoraLog_CLI
"""

import argparse
import sys
from .journal import journal_mode
from .review import review_mode, review_specific_date


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="HoraLog_CLI - Terminal-based journal with timestamp logging",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  horalog-cli              # Start journal mode (default)
  horalog-cli --review     # Start review mode
  horalog-cli -r           # Start review mode (short)
  horalog-cli --date 2025-01-15  # View specific date
        """
    )
    
    parser.add_argument(
        '--review', '-r',
        action='store_true',
        help='Launch review mode to view past entries'
    )
    
    parser.add_argument(
        '--date',
        metavar='YYYY-MM-DD',
        help='Directly view logs for a specific date'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='HoraLog_CLI 1.0.0'
    )
    
    args = parser.parse_args()
    
    try:
        if args.date:
            # Review specific date
            review_specific_date(args.date)
        elif args.review:
            # Review mode
            review_mode()
        else:
            # Journal mode (default)
            journal_mode()
    
    except KeyboardInterrupt:
        print("\nExiting HoraLog_CLI...")
        sys.exit(0)
    
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
