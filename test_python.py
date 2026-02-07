#!/usr/bin/env python3
"""
Simple test script for pspdecrypt Python bindings
"""

import sys
import os

# Add the build directory to the path
build_dir = 'build/lib.linux-x86_64-cpython-312'
if os.path.exists(build_dir):
    sys.path.insert(0, build_dir)

try:
    import pspdecrypt
    print("✓ Module import successful")
    print(f"  Version: {pspdecrypt.__version__}")
except ImportError as e:
    print(f"✗ Failed to import module: {e}")
    sys.exit(1)

# Test 1: Module has expected functions
print("\nTest 1: Check available functions")
expected_functions = [
    'decrypt_prx',
    'decrypt_prx_file',
    'get_prx_info',
    'decrypt_ipl1',
    'linearize_ipl2',
    'decrypt_ipl3',
    'decompress',
]

for func_name in expected_functions:
    if hasattr(pspdecrypt, func_name):
        print(f"  ✓ {func_name} found")
    else:
        print(f"  ✗ {func_name} NOT found")

# Test 2: Test error handling
print("\nTest 2: Test error handling")
try:
    # Try to decrypt invalid data (too small)
    pspdecrypt.decrypt_prx(b"too small")
    print("  ✗ Should have raised an exception for small data")
except RuntimeError as e:
    print(f"  ✓ Correctly raised RuntimeError: {e}")

# Test 3: Test get_prx_info with minimal valid header
print("\nTest 3: Test get_prx_info with minimal data")
try:
    # Create a minimal "fake" PRX header (0x150 bytes)
    fake_prx = b'\x00' * 0x150
    info = pspdecrypt.get_prx_info(fake_prx)
    print(f"  ✓ get_prx_info returned: {info}")
except Exception as e:
    print(f"  ✗ get_prx_info failed: {e}")

print("\n" + "=" * 50)
print("Basic tests completed!")
print("\nTo test with real PSP files, run:")
print("  python3 examples.py <path_to_prx_file>")
