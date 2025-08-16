"""
Utility functions for HoraLog_CLI
"""

import os
import yaml
from datetime import datetime
from pathlib import Path


def get_journal_dir():
    """Get the journal directory path, create if it doesn't exist."""
    journal_dir = Path("journal")
    journal_dir.mkdir(exist_ok=True)
    return journal_dir


def get_today_filename():
    """Get today's YAML filename in YYYY-MM-DD.yaml format."""
    return datetime.now().strftime("%Y-%m-%d.yaml")


def get_journal_file_path(date_str=None):
    """Get the full path to a journal file for a given date."""
    if date_str is None:
        date_str = get_today_filename()
    elif not date_str.endswith('.yaml'):
        date_str = f"{date_str}.yaml"
    
    return get_journal_dir() / date_str


def load_entries(date_str=None):
    """Load entries from a journal file."""
    file_path = get_journal_file_path(date_str)
    
    if not file_path.exists():
        return []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            return data.get('entries', []) if data else []
    except (yaml.YAMLError, IOError) as e:
        print(f"Error loading journal file: {e}")
        return []


def save_entry(entry, date_str=None):
    """Save a single entry to the journal file."""
    file_path = get_journal_file_path(date_str)
    entries = load_entries(date_str)
    
    entries.append(entry)
    
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump({'entries': entries}, f, default_flow_style=False, allow_unicode=True)
        return True
    except IOError as e:
        print(f"Error saving entry: {e}")
        return False


def get_available_dates():
    """Get list of available journal dates."""
    journal_dir = get_journal_dir()
    dates = []
    
    for file_path in journal_dir.glob("*.yaml"):
        try:
            date_str = file_path.stem  # Remove .yaml extension
            entries = load_entries(date_str)
            if entries:
                dates.append((date_str, len(entries)))
        except Exception:
            continue
    
    return sorted(dates, reverse=True)  # Most recent first


def validate_date_format(date_str):
    """Validate if a date string is in YYYY-MM-DD format."""
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def format_timestamp():
    """Get current timestamp in HH:MM:SS format."""
    return datetime.now().strftime("%H:%M:%S")
