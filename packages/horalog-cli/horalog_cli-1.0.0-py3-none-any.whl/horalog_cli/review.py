"""
Review mode functionality for HoraLog_CLI
"""

import sys
from .utils import load_entries, get_available_dates, validate_date_format


def display_entries_for_date(date_str):
    """Display all entries for a specific date."""
    entries = load_entries(date_str)
    
    if not entries:
        print(f"No entries found for {date_str}")
        return
    
    print(f"\nEntries for {date_str}:")
    for entry in entries:
        print(f"[{entry['time']}] {entry['text']}")
    print()


def review_mode():
    """Main review mode function."""
    print("HoraLog_CLI - Review Mode\n")
    
    while True:
        # Get available dates
        available_dates = get_available_dates()
        
        if not available_dates:
            print("No journal entries found.")
            print("Start journaling with: horalog-cli")
            break
        
        # Display available dates
        print("Available journal files:")
        for i, (date_str, entry_count) in enumerate(available_dates, 1):
            print(f"{i}. {date_str} ({entry_count} entries)")
        
        print()
        
        try:
            choice = input("Enter number (1-{}) or date (YYYY-MM-DD): ".format(len(available_dates))).strip()
            
            if not choice:
                continue
            
            # Check if it's a number
            try:
                index = int(choice) - 1
                if 0 <= index < len(available_dates):
                    selected_date = available_dates[index][0]
                    display_entries_for_date(selected_date)
                else:
                    print("Invalid number. Please try again.")
                    continue
            except ValueError:
                # Check if it's a date
                if validate_date_format(choice):
                    display_entries_for_date(choice)
                else:
                    print("Invalid format. Please enter a number or date (YYYY-MM-DD).")
                    continue
            
            # Ask if user wants to continue
            print("Press Enter to return to menu or Ctrl+C to exit")
            input()
            
        except (EOFError, KeyboardInterrupt):
            print("\nExiting review mode...")
            break
        
        except Exception as e:
            print(f"Unexpected error: {e}")
            sys.exit(1)


def review_specific_date(date_str):
    """Review entries for a specific date."""
    if not validate_date_format(date_str):
        print(f"Invalid date format: {date_str}")
        print("Please use YYYY-MM-DD format.")
        sys.exit(1)
    
    display_entries_for_date(date_str)
