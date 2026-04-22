#!/usr/bin/env python3
"""
Test runner for all database tests
Run individual tests or all tests at once
"""
import sys
import os
import subprocess

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_test(test_file):
    """Run a single test file"""
    print(f"\n{'='*50}")
    print(f"🧪 RUNNING: {test_file}")
    print(f"{'='*50}")
    
    try:
        result = subprocess.run([sys.executable, test_file], 
                              cwd=os.path.dirname(__file__),
                              capture_output=True, text=True)
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
            
        if result.returncode == 0:
            print(f"PASS: {test_file} PASSED")
            return True
        else:
            print(f"FAIL: {test_file} FAILED (exit code: {result.returncode})")
            return False
            
    except Exception as e:
        print(f"FAIL: Error running {test_file}: {e}")
        return False

def run_all_tests():
    """Run all test files"""
    test_files = [
        "test_connection.py",
        "test_insert.py", 
        "test_retrieve.py",
        "test_update.py",
        "test_search.py",
        "test_delete.py"
    ]
    
    print(" Starting Database Test Suite")
    print(f" Test directory: {os.path.dirname(__file__)}")
    
    results = {}
    passed = 0
    failed = 0
    
    for test_file in test_files:
        test_path = os.path.join(os.path.dirname(__file__), test_file)
        if os.path.exists(test_path):
            success = run_test(test_path)
            results[test_file] = success
            if success:
                passed += 1
            else:
                failed += 1
        else:
            print(f"⚠️  Test file not found: {test_file}")
    
    # Summary
    print(f"\n{'='*50}")
    print("INFO: TEST SUMMARY")
    print(f"{'='*50}")
    print(f"PASS: PASSED: {passed}")
    print(f"FAIL: FAILED: {failed}")
    print(f" SUCCESS RATE: {(passed/(passed+failed)*100):.1f}%" if (passed+failed) > 0 else "N/A")
    
    print(f"\nINFO: DETAILED RESULTS:")
    for test_file, success in results.items():
        status = "PASS: PASS" if success else "FAIL: FAIL"
        print(f"  {status} {test_file}")
    
    return failed == 0

def main():
    """Main function with command line argument handling"""
    if len(sys.argv) > 1:
        # Run specific test
        test_name = sys.argv[1]
        if not test_name.endswith('.py'):
            test_name += '.py'
        
        test_path = os.path.join(os.path.dirname(__file__), test_name)
        if os.path.exists(test_path):
            success = run_test(test_path)
            sys.exit(0 if success else 1)
        else:
            print(f"FAIL: Test file not found: {test_name}")
            print("Available tests:")
            for f in os.listdir(os.path.dirname(__file__)):
                if f.startswith('test_') and f.endswith('.py'):
                    print(f"  - {f}")
            sys.exit(1)
    else:
        # Run all tests
        success = run_all_tests()
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()