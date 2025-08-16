#!/usr/bin/env python3
"""
Build script for HoraLog_CLI PyPI distribution
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

def clean_build():
    """Clean previous build artifacts."""
    print("Cleaning previous build artifacts...")
    dirs_to_clean = ['build', 'dist', '*.egg-info']
    
    for pattern in dirs_to_clean:
        for path in Path('.').glob(pattern):
            if path.is_dir():
                shutil.rmtree(path)
                print(f"Removed {path}")
            elif path.is_file():
                path.unlink()
                print(f"Removed {path}")

def build_distribution():
    """Build the distribution packages."""
    print("Building distribution packages...")
    
    try:
        # Build source distribution and wheel
        subprocess.run([sys.executable, 'setup.py', 'sdist', 'bdist_wheel'], check=True)
        print("✓ Distribution packages built successfully")
    except subprocess.CalledProcessError as e:
        print(f"✗ Error building distribution: {e}")
        return False
    
    return True

def check_distribution():
    """Check the built distribution."""
    print("Checking distribution...")
    
    try:
        # Check the wheel
        subprocess.run([sys.executable, '-m', 'twine', 'check', 'dist/*'], check=True)
        print("✓ Distribution check passed")
    except subprocess.CalledProcessError as e:
        print(f"✗ Distribution check failed: {e}")
        return False
    
    return True

def list_distribution_files():
    """List the files that will be included in the distribution."""
    print("\nDistribution files:")
    dist_dir = Path('dist')
    if dist_dir.exists():
        for file_path in dist_dir.iterdir():
            print(f"  {file_path.name}")

def main():
    """Main build process."""
    print("HoraLog_CLI - PyPI Build Script")
    print("=" * 40)
    
    # Clean previous builds
    clean_build()
    
    # Build distribution
    if not build_distribution():
        print("Build failed!")
        sys.exit(1)
    
    # Check distribution
    if not check_distribution():
        print("Distribution check failed!")
        sys.exit(1)
    
    # List files
    list_distribution_files()
    
    print("\n✓ Build completed successfully!")
    print("\nNext steps:")
    print("1. Test the distribution: pip install dist/*.whl")
    print("2. Upload to PyPI: python scripts/upload.py")
    print("3. Upload to TestPyPI: python scripts/upload.py --test")

if __name__ == "__main__":
    main()
