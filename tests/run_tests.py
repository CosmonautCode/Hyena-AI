#!/usr/bin/env python3
"""
Test Runner for Hyena-AI
=======================

This script runs all unit, integration, and E2E tests for the Hyena-AI project,
captures detailed output, and saves results to a JSON file for logging and tracking.

Features:
- Runs all tests with pytest
- Captures detailed output with traceback information
- Saves results to JSON for analysis and tracking
- Provides summary statistics
- Generates timestamp-based log files
"""

import subprocess
import json
import sys
from datetime import datetime
from pathlib import Path


def run_tests():
    """Run all tests using pytest and capture output."""
    
    # Define output directories
    project_root = Path(__file__).parent
    logs_dir = project_root / "test_logs"
    logs_dir.mkdir(exist_ok=True)
    
    # Create timestamp for this run
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Output file paths
    json_output = logs_dir / f"test_results_{timestamp}.json"
    text_output = logs_dir / f"test_results_{timestamp}.txt"
    
    print("=" * 70)
    print("HYENA-AI TEST RUNNER")
    print("=" * 70)
    print(f"\nStarting test run at: {datetime.now().isoformat()}")
    print(f"\nTest logs directory: {logs_dir}")
    print(f"JSON output: {json_output}")
    print(f"Text output: {text_output}\n")
    
    # Run pytest with JSON report
    pytest_cmd = [
        sys.executable,
        "-m",
        "pytest",
        "tests/",
        "-v",
        "--tb=short",
        f"--json-report",
        f"--json-report-file={json_output}",
    ]
    
    print(f"Running command: {' '.join(pytest_cmd)}\n")
    
    try:
        # Run tests and capture output
        result = subprocess.run(
            pytest_cmd,
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=300
        )
        
        # Save text output
        with open(text_output, "w") as f:
            f.write("=" * 70 + "\n")
            f.write("HYENA-AI TEST RESULTS\n")
            f.write("=" * 70 + "\n")
            f.write(f"\nTest Run Timestamp: {datetime.now().isoformat()}\n")
            f.write(f"Working Directory: {project_root}\n")
            f.write("\n" + "=" * 70 + "\n")
            f.write("PYTEST OUTPUT\n")
            f.write("=" * 70 + "\n\n")
            f.write(result.stdout)
            f.write("\n\n")
            if result.stderr:
                f.write("=" * 70 + "\n")
                f.write("STDERR\n")
                f.write("=" * 70 + "\n\n")
                f.write(result.stderr)
        
        # Parse the results using a simpler approach if json-report fails
        if not json_output.exists():
            # Run pytest again with simpler approach to generate JSON
            pytest_cmd_simple = [
                sys.executable,
                "-m",
                "pytest",
                "tests/",
                "-v",
                "--tb=short",
                "--quiet",
            ]
            
            result = subprocess.run(
                pytest_cmd_simple,
                cwd=project_root,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            # Parse output manually
            output_lines = result.stdout.split("\n")
            summary_line = [l for l in output_lines if "passed" in l or "failed" in l]
            
            # Extract summary
            summary_dict = extract_test_summary(result.stdout, result.returncode)
            
            with open(json_output, "w") as f:
                json.dump({
                    "timestamp": datetime.now().isoformat(),
                    "project": "Hyena-AI",
                    "summary": summary_dict,
                    "output": result.stdout,
                    "returncode": result.returncode,
                    "success": result.returncode == 0
                }, f, indent=2)
        
        # Display summary
        print("\n" + "=" * 70)
        print("TEST RESULTS SUMMARY")
        print("=" * 70)
        
        with open(json_output, "r") as f:
            results = json.load(f)
            summary = results.get("summary", {})
            
            print(f"\nTotal Tests: {summary.get('total', 'N/A')}")
            print(f"Passed: {summary.get('passed', 'N/A')}")
            print(f"Failed: {summary.get('failed', 'N/A')}")
            print(f"Errors: {summary.get('errors', 'N/A')}")
            print(f"Warnings: {summary.get('warnings', 'N/A')}")
            print(f"Success: {results.get('success', False)}")
        
        print("\n" + "=" * 70)
        print(f"Test run completed at: {datetime.now().isoformat()}")
        print(f"Results saved to: {json_output}")
        print(f"Log file saved to: {text_output}")
        print("=" * 70 + "\n")
        
        return result.returncode
        
    except subprocess.TimeoutExpired:
        print("ERROR: Test run timed out after 300 seconds")
        return 1
    except Exception as e:
        print(f"ERROR: {e}")
        return 1


def extract_test_summary(output, returncode):
    """Extract test summary from pytest output."""
    summary = {
        "total": 0,
        "passed": 0,
        "failed": 0,
        "errors": 0,
        "warnings": 0
    }
    
    # Look for the summary line at the end of output
    lines = output.split("\n")
    for line in reversed(lines):
        if "passed" in line or "failed" in line:
            # Parse the summary line
            parts = line.split()
            for i, part in enumerate(parts):
                if "passed" in part and i > 0:
                    try:
                        summary["passed"] = int(parts[i-1])
                    except:
                        pass
                if "failed" in part and i > 0:
                    try:
                        summary["failed"] = int(parts[i-1])
                    except:
                        pass
                if "error" in part and i > 0:
                    try:
                        summary["errors"] = int(parts[i-1])
                    except:
                        pass
                if "warning" in part and i > 0:
                    try:
                        summary["warnings"] = int(parts[i-1])
                    except:
                        pass
            
            summary["total"] = (
                summary["passed"] + 
                summary["failed"] + 
                summary["errors"]
            )
            break
    
    return summary


def list_recent_results(limit=5):
    """List recent test results."""
    project_root = Path(__file__).parent
    logs_dir = project_root / "test_logs"
    
    if not logs_dir.exists():
        print("No test logs found.")
        return
    
    json_files = sorted(logs_dir.glob("test_results_*.json"), reverse=True)[:limit]
    
    if not json_files:
        print("No test results found.")
        return
    
    print("\n" + "=" * 70)
    print("RECENT TEST RESULTS")
    print("=" * 70 + "\n")
    
    for json_file in json_files:
        try:
            with open(json_file, "r") as f:
                results = json.load(f)
                summary = results.get("summary", {})
                timestamp = results.get("timestamp", "Unknown")
                success = results.get("success", False)
                
                status = "✓ PASSED" if success else "✗ FAILED"
                print(f"{status} | {timestamp}")
                print(f"  Passed: {summary.get('passed', 0):3d} | "
                      f"Failed: {summary.get('failed', 0):3d} | "
                      f"Errors: {summary.get('errors', 0):3d}")
                print()
        except Exception as e:
            print(f"Error reading {json_file}: {e}\n")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Run Hyena-AI tests and log results"
    )
    parser.add_argument(
        "--history",
        action="store_true",
        help="Show recent test results history"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=5,
        help="Limit number of recent results to show (default: 5)"
    )
    
    args = parser.parse_args()
    
    if args.history:
        list_recent_results(args.limit)
        sys.exit(0)
    
    exit_code = run_tests()
    sys.exit(exit_code)
