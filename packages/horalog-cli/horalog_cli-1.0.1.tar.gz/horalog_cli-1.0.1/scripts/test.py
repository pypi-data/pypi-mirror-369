#!/usr/bin/env python3
"""
Test script for HoraLog_CLI
"""

import os
import sys
from pathlib import Path

# Add the parent directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from horalog_cli.utils import get_journal_dir, load_entries, save_entry, format_timestamp
from horalog_cli.journal import journal_mode
from horalog_cli.review import review_mode, review_specific_date


def test_basic_functionality():
    """Test basic functionality of the journal system."""
    print("Testing HoraLog_CLI basic functionality...")
    
    # Test journal directory creation
    journal_dir = get_journal_dir()
    print(f"✓ Journal directory: {journal_dir}")
    
    # Test timestamp formatting
    timestamp = format_timestamp()
    print(f"✓ Current timestamp: {timestamp}")
    
    # Test entry saving and loading
    test_entry = {
        'time': '12:00:00',
        'text': 'Test entry for functionality testing'
    }
    
    if save_entry(test_entry, '2025-01-20'):
        print("✓ Entry saved successfully")
        
        entries = load_entries('2025-01-20')
        if entries and entries[-1]['text'] == test_entry['text']:
            print("✓ Entry loaded successfully")
        else:
            print("✗ Entry loading failed")
    else:
        print("✗ Entry saving failed")
    
    print("\nAll basic tests completed!")


def test_review_functionality():
    """Test review functionality."""
    print("\nTesting review functionality...")
    
    # Test specific date review
    print("Testing specific date review:")
    review_specific_date('2025-01-15')
    
    print("\nReview functionality test completed!")


def main():
    """Main test function."""
    print("HoraLog_CLI - Test Suite")
    print("=" * 30)
    
    test_basic_functionality()
    test_review_functionality()
    
    print("\n✅ All tests completed!")


if __name__ == "__main__":
    main()
