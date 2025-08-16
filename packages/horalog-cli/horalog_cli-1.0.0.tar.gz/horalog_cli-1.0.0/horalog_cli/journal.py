"""
Journal mode functionality for HoraLog_CLI
"""

import sys
from .utils import load_entries, save_entry, format_timestamp, get_today_filename


def display_previous_entries(entries):
    """Display previous entries for today."""
    if entries:
        print("\nPrevious entries for today:")
        for entry in entries:
            print(f"[{entry['time']}] {entry['text']}")
        print()


def journal_mode():
    """Main journal mode function."""
    today_file = get_today_filename()
    date_str = today_file.replace('.yaml', '')
    
    print(f"HoraLog_CLI - Journal Mode")
    print(f"Today: {date_str}")
    
    # Load and display previous entries
    entries = load_entries(date_str)
    display_previous_entries(entries)
    
    print("Type your journal entries (Ctrl+C to exit):")
    
    try:
        while True:
            # Get current timestamp
            timestamp = format_timestamp()
            
            # Get user input
            try:
                text = input(f"[{timestamp}] > ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nExiting journal mode...")
                break
            
            # Skip empty entries
            if not text:
                continue
            
            # Create entry
            entry = {
                'time': timestamp,
                'text': text
            }
            
            # Save entry immediately
            if save_entry(entry, date_str):
                # Display the entry that was just saved
                print(f"[{timestamp}] {text}")
            else:
                print("Error saving entry!")
    
    except KeyboardInterrupt:
        print("\nExiting journal mode...")
    
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)
