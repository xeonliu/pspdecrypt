#!/usr/bin/env python3
"""
Example usage of pspdecrypt Python bindings
Demonstrates how to use the library for decrypting PSP files
"""

import pspdecrypt
import sys
import os


def example_decrypt_prx_from_file():
    """Example: Decrypt a PRX file from disk"""
    print("=== Example: Decrypt PRX from file ===")
    
    if len(sys.argv) < 2:
        print("Usage: python examples.py <prx_file>")
        print("No input file provided, skipping file example")
        return
    
    input_file = sys.argv[1]
    if not os.path.exists(input_file):
        print(f"File not found: {input_file}")
        return
    
    try:
        # Decrypt the PRX file
        decrypted_data = pspdecrypt.decrypt_prx_file(input_file, verbose=True)
        
        # Save the decrypted data
        output_file = input_file + ".dec"
        with open(output_file, 'wb') as f:
            f.write(decrypted_data)
        
        print(f"Decrypted {len(decrypted_data)} bytes to {output_file}")
    except Exception as e:
        print(f"Error: {e}")


def example_decrypt_prx_from_bytes():
    """Example: Decrypt a PRX from bytes (useful for in-memory processing)"""
    print("\n=== Example: Decrypt PRX from bytes ===")
    
    if len(sys.argv) < 2:
        print("No input file provided, skipping bytes example")
        return
    
    input_file = sys.argv[1]
    if not os.path.exists(input_file):
        return
    
    try:
        # Read file into memory
        with open(input_file, 'rb') as f:
            file_data = f.read()
        
        print(f"Read {len(file_data)} bytes from {input_file}")
        
        # Decrypt from bytes
        decrypted_data = pspdecrypt.decrypt_prx(file_data, verbose=True)
        
        print(f"Decrypted to {len(decrypted_data)} bytes")
    except Exception as e:
        print(f"Error: {e}")


def example_get_prx_info():
    """Example: Get information about a PRX file"""
    print("\n=== Example: Get PRX information ===")
    
    if len(sys.argv) < 2:
        print("No input file provided, skipping info example")
        return
    
    input_file = sys.argv[1]
    if not os.path.exists(input_file):
        return
    
    try:
        # Read file into memory
        with open(input_file, 'rb') as f:
            file_data = f.read()
        
        # Get PRX info
        info = pspdecrypt.get_prx_info(file_data)
        
        print(f"Tag:           0x{info['tag']:08X}")
        print(f"ELF Size:      {info['elf_size']} bytes")
        print(f"PSP Size:      {info['psp_size']} bytes")
        print(f"Comp Size:     {info['comp_size']} bytes")
        print(f"Is Compressed: {info['is_compressed']}")
    except Exception as e:
        print(f"Error: {e}")


def example_decrypt_with_secure_id():
    """Example: Decrypt a PRX with a secure ID (for type 3/5/7/10 PRX)"""
    print("\n=== Example: Decrypt PRX with secure ID ===")
    print("This example shows how to use a secure ID for certain PRX types")
    
    # Example secure ID (16 bytes, typically specific to a PSP console)
    # This is just a placeholder - real secure IDs are device-specific
    secure_id = b'\x00' * 16
    
    print(f"Secure ID: {secure_id.hex()}")
    print("In practice, you would:")
    print("1. Read your input file")
    print("2. Convert your hex secure ID string to bytes")
    print("3. Call: decrypted = pspdecrypt.decrypt_prx(data, secure_id=secure_id)")


def example_ipl_decryption():
    """Example: Decrypt IPL stages"""
    print("\n=== Example: IPL Decryption ===")
    print("IPL (Initial Program Loader) decryption is a multi-stage process:")
    print("1. Stage 1: decrypt_ipl1() - Decrypts the first stage")
    print("2. Stage 2: linearize_ipl2() - Linearizes the decrypted data")
    print("3. Stage 3: decrypt_ipl3() - Decrypts the final payload (for FW 1.00-2.50)")
    print("\nExample code:")
    print("""
    # Stage 1
    with open('ipl.bin', 'rb') as f:
        ipl_data = f.read()
    
    stage1_data = pspdecrypt.decrypt_ipl1(ipl_data, verbose=True)
    
    # Stage 2
    stage2_data, start_addr = pspdecrypt.linearize_ipl2(stage1_data)
    print(f"Linearized at address: 0x{start_addr:08X}")
    
    # Stage 3 (for older firmware)
    stage3_data = pspdecrypt.decrypt_ipl3(stage2_data)
    """)


def example_decompression():
    """Example: Decompress data"""
    print("\n=== Example: Data Decompression ===")
    print("The library supports GZIP, KL4E, KL3E, and 2RLZ compression formats")
    print("Example code:")
    print("""
    # Decompress data (automatically detects format)
    compressed_data = b'...'  # Your compressed data
    decompressed = pspdecrypt.decompress(compressed_data, verbose=True)
    
    # You can also specify max output size
    decompressed = pspdecrypt.decompress(compressed_data, max_size=1024*1024)
    """)


def main():
    print("PSP Decrypt Python Bindings - Examples")
    print("=" * 50)
    print(f"Library version: {pspdecrypt.__version__}")
    print()
    
    # Run all examples
    example_decrypt_prx_from_file()
    example_decrypt_prx_from_bytes()
    example_get_prx_info()
    example_decrypt_with_secure_id()
    example_ipl_decryption()
    example_decompression()
    
    print("\n" + "=" * 50)
    print("Examples completed!")


if __name__ == '__main__':
    main()
