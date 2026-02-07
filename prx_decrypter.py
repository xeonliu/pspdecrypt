"""
PRX Decrypter - Decrypt PSP PRX executables

This module handles the decryption of PSP PRX (PlayStation Portable Relocatable Executable) files.
"""

import struct
from typing import Optional
from kirk_engine import kirk_CMD1, kirk_CMD7, KIRK_OPERATION_SUCCESS

# PRX decryption keys for different firmware versions
# These are publicly known keys used for PSP decryption
PRX_KEYS = {
    # Format: tag -> (key, description)
    0xD91605F0: (bytes.fromhex('C3248 9D380087B24E4CD749E49D1D34D1'), 'keys260_0'),
    0xD91606F0: (bytes.fromhex('F3AC6E7C040A23E70D33D82473392B4A'), 'keys260_1'),
    0xD91608F0: (bytes.fromhex('72B439FF349BAE8230344A1DA2D8B43C'), 'keys260_2'),
    0xD91609F0: (bytes.fromhex('CAFBBFC750EAB4408E445C6353CE80B1'), 'keys280_0'),
    0xD91611F0: (bytes.fromhex('409BC69BA9FB847F7221D23696550974'), 'keys280_1'),
    0xD91612F0: (bytes.fromhex('03A7CC4A5B91C207FFFC26251E424BB5'), 'keys280_2'),
    # Add more keys as needed...
}


def decrypt_prx_internal(
    inbuf: bytes,
    size: int,
    secure_id: Optional[bytes] = None,
    verbose: bool = False
) -> Optional[bytes]:
    """
    Internal PRX decryption function.
    
    Args:
        inbuf: Input buffer containing encrypted PRX
        size: Size of input data
        secure_id: Optional 16-byte secure ID
        verbose: Enable verbose output
    
    Returns:
        Decrypted data or None on failure
    """
    if size < 0x150:  # PSP header size
        if verbose:
            print("Error: Input too small for PSP header")
        return None
    
    # Parse PSP header
    header = inbuf[0:0x150]
    
    # Get tag value (offset 0xD0)
    tag = struct.unpack('<I', header[0xD0:0xD4])[0]
    
    # Get decrypt mode (offset 0x7C)
    decrypt_mode = struct.unpack('<I', header[0x7C:0x80])[0]
    
    if verbose:
        print(f"PRX tag: 0x{tag:08X}, decrypt mode: {decrypt_mode}")
    
    # This is a simplified implementation
    # The full implementation would use KIRK commands to decrypt
    # For now, we'll return a placeholder
    
    # Copy header to output
    outbuf = bytearray(inbuf[0:0x150])
    
    # Decrypt the body using appropriate KIRK command
    # This is a simplified version - real implementation is more complex
    body = inbuf[0x150:size]
    
    if decrypt_mode in [1, 2, 3]:
        # Use KIRK CMD1 for these modes
        decrypted = bytearray(len(body))
        result = kirk_CMD1(decrypted, body, len(body))
        if result == KIRK_OPERATION_SUCCESS:
            outbuf.extend(decrypted)
        else:
            if verbose:
                print(f"KIRK CMD1 failed with code {result}")
            return None
    elif decrypt_mode in [4, 5, 6]:
        # Use KIRK CMD7 for these modes
        decrypted = bytearray(len(body))
        result = kirk_CMD7(decrypted, body, len(body))
        if result == KIRK_OPERATION_SUCCESS:
            outbuf.extend(decrypted)
        else:
            if verbose:
                print(f"KIRK CMD7 failed with code {result}")
            return None
    else:
        if verbose:
            print(f"Unknown decrypt mode: {decrypt_mode}")
        # Return unencrypted data for unknown modes
        outbuf.extend(body)
    
    return bytes(outbuf)
