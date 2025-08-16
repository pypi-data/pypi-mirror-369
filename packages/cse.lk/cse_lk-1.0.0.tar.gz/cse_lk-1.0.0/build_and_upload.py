#!/usr/bin/env python3
"""
Build and upload script for the CSE.LK package.

This script helps build the package and upload it to PyPI.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def run_command(command: str, check: bool = True) -> subprocess.CompletedProcess:
    """Run a shell command and return the result."""
    print(f"🔧 Running: {command}")
    result = subprocess.run(
        command, 
        shell=True, 
        capture_output=True, 
        text=True,
        check=check
    )
    
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    
    return result


def clean_build_artifacts():
    """Clean up build artifacts."""
    print("🧹 Cleaning build artifacts...")
    
    artifacts = ["build", "dist", "*.egg-info"]
    for artifact in artifacts:
        for path in Path(".").glob(artifact):
            if path.is_dir():
                shutil.rmtree(path)
                print(f"  Removed directory: {path}")
            else:
                path.unlink()
                print(f"  Removed file: {path}")


def run_tests():
    """Run the test suite."""
    print("🧪 Running tests...")
    try:
        run_command("python -m pytest tests/ -v --tb=short")
        print("✅ All tests passed!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Tests failed!")
        return False


def run_linting():
    """Run code linting checks."""
    print("🔍 Running linting checks...")
    
    try:
        # Check if black is available
        run_command("python -m black --version", check=False)
        run_command("python -m black --check cse_lk/ tests/ examples/")
        print("✅ Code formatting is correct!")
    except subprocess.CalledProcessError:
        print("⚠️  Code formatting issues found. Run 'python -m black cse_lk/ tests/ examples/' to fix.")
        return False
    
    try:
        # Check if flake8 is available
        run_command("python -m flake8 --version", check=False)
        run_command("python -m flake8 cse_lk/ tests/ examples/ --max-line-length=88 --extend-ignore=E203,W503")
        print("✅ Linting checks passed!")
    except subprocess.CalledProcessError:
        print("❌ Linting issues found!")
        return False
    
    return True


def build_package():
    """Build the package."""
    print("📦 Building package...")
    
    try:
        # Build source distribution and wheel
        run_command("python -m build")
        print("✅ Package built successfully!")
        
        # List built files
        dist_files = list(Path("dist").glob("*"))
        print("📄 Built files:")
        for file in dist_files:
            print(f"  {file}")
        
        return True
    except subprocess.CalledProcessError:
        print("❌ Package build failed!")
        return False


def check_package():
    """Check the built package."""
    print("🔍 Checking package...")
    
    try:
        run_command("python -m twine check dist/*")
        print("✅ Package check passed!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Package check failed!")
        return False


def upload_to_test_pypi():
    """Upload to Test PyPI."""
    print("🚀 Uploading to Test PyPI...")
    
    try:
        run_command("python -m twine upload --repository testpypi dist/*")
        print("✅ Package uploaded to Test PyPI!")
        print("🔗 Test your package: pip install --index-url https://test.pypi.org/simple/ cse.lk")
        return True
    except subprocess.CalledProcessError:
        print("❌ Upload to Test PyPI failed!")
        return False


def upload_to_pypi():
    """Upload to PyPI."""
    print("🚀 Uploading to PyPI...")
    
    response = input("⚠️  Are you sure you want to upload to PyPI? (y/N): ")
    if response.lower() != 'y':
        print("❌ Upload cancelled.")
        return False
    
    try:
        run_command("python -m twine upload dist/*")
        print("✅ Package uploaded to PyPI!")
        print("🔗 Install your package: pip install cse.lk")
        return True
    except subprocess.CalledProcessError:
        print("❌ Upload to PyPI failed!")
        return False


def main():
    """Main build and upload workflow."""
    print("🏗️  CSE.LK Package Build and Upload Script")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("setup.py").exists():
        print("❌ setup.py not found! Run this script from the package root directory.")
        sys.exit(1)
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
    else:
        command = None
    
    # Show help
    if command in ["-h", "--help", "help"]:
        print("Usage: python build_and_upload.py [command]")
        print("\nCommands:")
        print("  clean     - Clean build artifacts")
        print("  test      - Run tests only")
        print("  lint      - Run linting checks only")
        print("  build     - Build package only")
        print("  check     - Check built package only")
        print("  test-pypi - Upload to Test PyPI")
        print("  pypi      - Upload to PyPI")
        print("  full      - Full workflow (default)")
        return
    
    # Execute specific command
    if command == "clean":
        clean_build_artifacts()
        return
    elif command == "test":
        success = run_tests()
        sys.exit(0 if success else 1)
    elif command == "lint":
        success = run_linting()
        sys.exit(0 if success else 1)
    elif command == "build":
        clean_build_artifacts()
        success = build_package()
        sys.exit(0 if success else 1)
    elif command == "check":
        success = check_package()
        sys.exit(0 if success else 1)
    elif command == "test-pypi":
        if not Path("dist").exists() or not list(Path("dist").glob("*")):
            print("❌ No built package found. Run 'python build_and_upload.py build' first.")
            sys.exit(1)
        success = upload_to_test_pypi()
        sys.exit(0 if success else 1)
    elif command == "pypi":
        if not Path("dist").exists() or not list(Path("dist").glob("*")):
            print("❌ No built package found. Run 'python build_and_upload.py build' first.")
            sys.exit(1)
        success = upload_to_pypi()
        sys.exit(0 if success else 1)
    
    # Full workflow (default)
    print("🚀 Starting full build and upload workflow...")
    
    # Step 1: Clean
    clean_build_artifacts()
    
    # Step 2: Run tests
    if not run_tests():
        print("❌ Stopping due to test failures.")
        sys.exit(1)
    
    # Step 3: Run linting
    if not run_linting():
        print("❌ Stopping due to linting issues.")
        sys.exit(1)
    
    # Step 4: Build package
    if not build_package():
        print("❌ Stopping due to build failure.")
        sys.exit(1)
    
    # Step 5: Check package
    if not check_package():
        print("❌ Stopping due to package check failure.")
        sys.exit(1)
    
    # Step 6: Ask what to do next
    print("\n🎉 Package is ready for upload!")
    print("What would you like to do?")
    print("1. Upload to Test PyPI")
    print("2. Upload to PyPI")
    print("3. Exit")
    
    choice = input("Enter your choice (1-3): ").strip()
    
    if choice == "1":
        upload_to_test_pypi()
    elif choice == "2":
        upload_to_pypi()
    else:
        print("👋 Exiting. You can manually upload later using:")
        print("  Test PyPI: python -m twine upload --repository testpypi dist/*")
        print("  PyPI: python -m twine upload dist/*")


if __name__ == "__main__":
    main() 