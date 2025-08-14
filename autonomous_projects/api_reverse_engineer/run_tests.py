"""
Test runner for the API reverse engineering tool.

This script runs all tests including unit tests, integration tests, and examples.
"""

import sys
import unittest
import subprocess
from pathlib import Path


def run_unit_tests():
    """Run all unit tests."""
    print("Running unit tests...")
    print("=" * 50)
    
    # Discover and run unit tests
    loader = unittest.TestLoader()
    start_dir = Path(__file__).parent / "tests"
    suite = loader.discover(str(start_dir), pattern="test_*.py")
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


def run_integration_test():
    """Run the integration test."""
    print("\nRunning integration test...")
    print("=" * 50)
    
    try:
        # Run the integration test
        integration_script = Path(__file__).parent / "examples" / "integration_test.py"
        result = subprocess.run([
            sys.executable, str(integration_script)
        ], capture_output=True, text=True, timeout=300)  # 5 minute timeout
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
            
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("✗ Integration test timed out")
        return False
    except Exception as e:
        print(f"✗ Error running integration test: {e}")
        return False


def run_example_scripts():
    """Run example scripts to ensure they work."""
    print("\nRunning example scripts...")
    print("=" * 50)
    
    examples_dir = Path(__file__).parent / "examples"
    example_scripts = [
        "basic_usage.py"
    ]
    
    success = True
    
    for script in example_scripts:
        script_path = examples_dir / script
        if not script_path.exists():
            print(f"⚠ Example script not found: {script}")
            continue
            
        try:
            print(f"Running {script}...")
            result = subprocess.run([
                sys.executable, str(script_path)
            ], capture_output=True, text=True, timeout=120, cwd=examples_dir.parent)
            
            if result.returncode == 0:
                print(f"✓ {script} completed successfully")
            else:
                print(f"✗ {script} failed with return code {result.returncode}")
                if result.stdout:
                    print("STDOUT:", result.stdout[-500:])  # Last 500 chars
                if result.stderr:
                    print("STDERR:", result.stderr[-500:])  # Last 500 chars
                success = False
                
        except subprocess.TimeoutExpired:
            print(f"✗ {script} timed out")
            success = False
        except Exception as e:
            print(f"✗ Error running {script}: {e}")
            success = False
            
    return success


def check_dependencies():
    """Check that all required dependencies are installed."""
    print("Checking dependencies...")
    print("=" * 50)
    
    required_packages = [
        "mitmproxy",
        "requests", 
        "jinja2",
        "flask"  # For integration tests
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✓ {package}")
        except ImportError:
            print(f"✗ {package} (missing)")
            missing_packages.append(package)
            
    if missing_packages:
        print(f"\nMissing packages: {', '.join(missing_packages)}")
        print("Install them with: pip install " + " ".join(missing_packages))
        return False
        
    return True


def run_code_quality_checks():
    """Run basic code quality checks."""
    print("\nRunning code quality checks...")
    print("=" * 50)
    
    src_dir = Path(__file__).parent / "src"
    
    # Check for syntax errors
    python_files = list(src_dir.rglob("*.py"))
    
    syntax_errors = 0
    for file_path in python_files:
        try:
            with open(file_path, 'r') as f:
                compile(f.read(), str(file_path), 'exec')
            print(f"✓ {file_path.relative_to(src_dir)}")
        except SyntaxError as e:
            print(f"✗ {file_path.relative_to(src_dir)}: {e}")
            syntax_errors += 1
        except Exception as e:
            print(f"⚠ {file_path.relative_to(src_dir)}: {e}")
            
    if syntax_errors > 0:
        print(f"\nFound {syntax_errors} syntax errors")
        return False
        
    return True


def main():
    """Run all tests and checks."""
    print("API Reverse Engineering Tool - Test Suite")
    print("=" * 60)
    
    all_passed = True
    
    # Check dependencies first
    if not check_dependencies():
        print("\n✗ Dependency check failed")
        return False
        
    # Run code quality checks
    if not run_code_quality_checks():
        print("\n✗ Code quality checks failed")
        all_passed = False
        
    # Run unit tests
    if not run_unit_tests():
        print("\n✗ Unit tests failed")
        all_passed = False
        
    # Run example scripts
    if not run_example_scripts():
        print("\n✗ Example scripts failed")
        all_passed = False
        
    # Run integration test (skip if previous tests failed)
    if all_passed:
        if not run_integration_test():
            print("\n✗ Integration test failed")
            all_passed = False
    else:
        print("\nSkipping integration test due to previous failures")
        
    # Final summary
    print("\n" + "=" * 60)
    if all_passed:
        print("✓ All tests passed successfully!")
        print("\nThe API reverse engineering tool is ready to use.")
        print("Try running:")
        print("  python -m src.cli --help")
        print("  python examples/basic_usage.py")
    else:
        print("✗ Some tests failed")
        print("\nPlease fix the issues before using the tool.")
        
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)