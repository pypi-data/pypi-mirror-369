#!/usr/bin/env python3
"""
Professional PyPI Upload Script for HoraLog_CLI
Securely handles API keys and provides complete upload workflow.
"""

import os
import sys
import getpass
import subprocess
import tempfile
import argparse
from pathlib import Path
import shutil


def get_pypi_credentials():
    """Securely get PyPI credentials from user."""
    print("PyPI Upload Configuration")
    print("=" * 40)
    
    # Get username
    username = input("PyPI Username: ").strip()
    if not username:
        print("❌ Username is required")
        return None, None
    
    # Get password/API key securely
    password = getpass.getpass("PyPI Password/API Key: ")
    if not password:
        print("❌ Password/API Key is required")
        return None, None
    
    return username, password


def create_pypirc_file(username, password, test_pypi=False):
    """Create .pypirc file with credentials."""
    pypirc_content = f"""[distutils]
index-servers =
    {'testpypi' if test_pypi else 'pypi'}

[{'testpypi' if test_pypi else 'pypi'}]
repository = {'https://test.pypi.org/legacy/' if test_pypi else 'https://upload.pypi.org/legacy/'}
username = {username}
password = {password}
"""
    
    # Create .pypirc in user's home directory
    home_dir = Path.home()
    pypirc_path = home_dir / ".pypirc"
    
    try:
        with open(pypirc_path, 'w') as f:
            f.write(pypirc_content)
        
        # Set restrictive permissions (Unix-like systems)
        if os.name != 'nt':  # Not Windows
            os.chmod(pypirc_path, 0o600)
        
        print(f"✓ Created .pypirc file at {pypirc_path}")
        return pypirc_path
    except Exception as e:
        print(f"❌ Error creating .pypirc file: {e}")
        return None


def clean_pypirc_file():
    """Remove .pypirc file after upload."""
    home_dir = Path.home()
    pypirc_path = home_dir / ".pypirc"
    
    if pypirc_path.exists():
        try:
            pypirc_path.unlink()
            print("✓ Removed .pypirc file")
        except Exception as e:
            print(f"⚠️  Warning: Could not remove .pypirc file: {e}")


def check_prerequisites():
    """Check if all required tools are installed."""
    print("Checking prerequisites...")
    
    # Try to import the tools directly
    try:
        import twine
        print(f"✓ twine")
    except ImportError:
        print("❌ twine not found")
        return False
    
    try:
        import wheel
        print(f"✓ wheel")
    except ImportError:
        print("❌ wheel not found")
        return False
    
    try:
        import setuptools
        print(f"✓ setuptools")
    except ImportError:
        print("❌ setuptools not found")
        return False
    
    return True


def build_distribution():
    """Build the distribution packages."""
    print("\nBuilding distribution packages...")
    
    try:
        # Clean previous builds
        for pattern in ['build', 'dist', '*.egg-info']:
            for path in Path('.').glob(pattern):
                if path.is_dir():
                    shutil.rmtree(path)
                elif path.is_file():
                    path.unlink()
        
        # Build packages
        subprocess.run([sys.executable, 'setup.py', 'sdist', 'bdist_wheel'], 
                      check=True, capture_output=True, text=True)
        
        # Check if files were created
        dist_dir = Path('dist')
        if not dist_dir.exists() or not list(dist_dir.glob('*')):
            print("❌ No distribution files created")
            return False
        
        print("✓ Distribution packages built successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        return False


def validate_distribution():
    """Validate the built distribution."""
    print("Validating distribution...")
    
    try:
        subprocess.run([sys.executable, '-m', 'twine', 'check', 'dist/*'], 
                      check=True, capture_output=True, text=True)
        print("✓ Distribution validation passed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Distribution validation failed: {e}")
        return False


def upload_to_pypi(test_pypi=False):
    """Upload to PyPI or TestPyPI."""
    repository = "testpypi" if test_pypi else "pypi"
    repo_name = "TestPyPI" if test_pypi else "PyPI"
    
    print(f"\nUploading to {repo_name}...")
    
    try:
        cmd = [sys.executable, '-m', 'twine', 'upload', 'dist/*']
        if test_pypi:
            cmd.extend(['--repository', 'testpypi'])
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✓ Successfully uploaded to {repo_name}")
            return True
        else:
            print(f"❌ Upload failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Upload error: {e}")
        return False


def test_installation(test_pypi=False):
    """Test installation from PyPI."""
    if test_pypi:
        print("\nTesting installation from TestPyPI...")
        cmd = [
            sys.executable, '-m', 'pip', 'install', 
            '--index-url', 'https://test.pypi.org/simple/',
            'horalog-cli'
        ]
    else:
        print("\nTesting installation from PyPI...")
        cmd = [sys.executable, '-m', 'pip', 'install', 'horalog-cli']
    
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✓ Installation test successful")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Installation test failed: {e}")
        return False


def main():
    """Main upload workflow."""
    parser = argparse.ArgumentParser(
        description="Upload HoraLog_CLI to PyPI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/upload.py --test    # Upload to TestPyPI
  python scripts/upload.py           # Upload to PyPI (production)
        """
    )
    
    parser.add_argument(
        '--test', '-t',
        action='store_true',
        help='Upload to TestPyPI instead of PyPI'
    )
    
    parser.add_argument(
        '--no-build',
        action='store_true',
        help='Skip building distribution (use existing dist/ files)'
    )
    
    parser.add_argument(
        '--no-test',
        action='store_true',
        help='Skip installation testing after upload'
    )
    
    args = parser.parse_args()
    
    print("HoraLog_CLI - Professional PyPI Upload Script")
    print("=" * 50)
    
    # Check prerequisites
    if not check_prerequisites():
        sys.exit(1)
    
    # Get credentials
    username, password = get_pypi_credentials()
    if not username or not password:
        sys.exit(1)
    
    # Determine upload target
    test_pypi = args.test
    repo_name = "TestPyPI" if test_pypi else "PyPI"
    
    if test_pypi:
        print(f"\n📦 Uploading to {repo_name}...")
    else:
        print(f"\n🚀 Uploading to {repo_name} (production)...")
        confirm = input("Are you sure you want to upload to production PyPI? (yes/no): ").strip().lower()
        if confirm != 'yes':
            print("Upload cancelled.")
            sys.exit(0)
    
    # Create .pypirc file
    pypirc_path = create_pypirc_file(username, password, test_pypi)
    if not pypirc_path:
        sys.exit(1)
    
    try:
        # Build distribution (unless skipped)
        if not args.no_build:
            if not build_distribution():
                sys.exit(1)
        else:
            print("Skipping build (using existing dist/ files)")
        
        # Validate distribution
        if not validate_distribution():
            sys.exit(1)
        
        # Upload to PyPI
        if not upload_to_pypi(test_pypi):
            sys.exit(1)
        
        # Test installation (unless skipped)
        if not args.no_test:
            if not test_installation(test_pypi):
                print("⚠️  Upload successful but installation test failed")
        
        print(f"\n🎉 Successfully uploaded to {repo_name}!")
        
        if test_pypi:
            print("\nNext steps:")
            print("1. Test the package: pip install --index-url https://test.pypi.org/simple/ horalog-cli")
            print("2. If everything works, run: python scripts/upload.py")
        else:
            print("\nPackage is now available on PyPI!")
            print("Users can install with: pip install horalog-cli")
    
    finally:
        # Clean up .pypirc file
        clean_pypirc_file()


if __name__ == "__main__":
    main()
