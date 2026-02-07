"""
LibLZR - 2RLZ Decompression

This module handles 2RLZ decompression used in PSP files.
Based on libLZR by BenHur - http://www.psp-programming.com/benhur
"""

from typing import Optional


def lzr_fill_buffer(test_mask: int, mask: int, buffer: int, inbuf: memoryview, pos: int) -> tuple:
    """Fill up buffer and shift mask if necessary."""
    if test_mask <= 0x00FFFFFF:
        buffer = (buffer << 8) + inbuf[pos]
        pos += 1
        mask = test_mask << 8
    return (mask, buffer, pos)


def lzr_next_bit(buf_ptr_val: int, number: Optional[int], test_mask: int, mask: int, 
                  buffer: int, inbuf: memoryview, pos: int) -> tuple:
    """
    Extract and return next bit of information from input stream.
    
    Returns: (bit, new_buf_ptr_val, new_number, new_test_mask, new_mask, new_buffer, new_pos)
    """
    mask, buffer, pos = lzr_fill_buffer(test_mask, mask, buffer, inbuf, pos)
    value = (mask >> 8) * buf_ptr_val
    
    if test_mask != mask:
        test_mask = value
    
    buf_ptr_val -= buf_ptr_val >> 3
    
    if number is not None:
        number <<= 1
    
    if buffer < value:
        mask = value
        buf_ptr_val += 31
        if number is not None:
            number += 1
        return (1, buf_ptr_val, number, test_mask, mask, buffer, pos)
    else:
        buffer -= value
        mask -= value
        return (0, buf_ptr_val, number, test_mask, mask, buffer, pos)


def lzr_get_number(n_bits: int, buf_ptr: list, inc: int, mask: int, buffer: int, 
                    inbuf: memoryview, pos: int) -> tuple:
    """
    Extract and return a number (consisting of n_bits bits) from input stream.
    
    Returns: (number, flag, new_mask, new_buffer, new_pos, new_buf_ptr)
    """
    number = 1
    
    if n_bits >= 3:
        bit, buf_ptr[3*inc], number, mask, mask, buffer, pos = lzr_next_bit(
            buf_ptr[3*inc], number, mask, mask, buffer, inbuf, pos
        )
        
        if n_bits >= 4:
            bit, buf_ptr[3*inc], number, mask, mask, buffer, pos = lzr_next_bit(
                buf_ptr[3*inc], number, mask, mask, buffer, inbuf, pos
            )
            
            if n_bits >= 5:
                mask, buffer, pos = lzr_fill_buffer(mask, mask, buffer, inbuf, pos)
                for _ in range(n_bits - 4):
                    number <<= 1
                    mask >>= 1
                    if buffer < mask:
                        number += 1
                    else:
                        buffer -= mask
    
    flag, buf_ptr[0], number, mask, mask, buffer, pos = lzr_next_bit(
        buf_ptr[0], number, mask, mask, buffer, inbuf, pos
    )
    
    if n_bits >= 1:
        bit, buf_ptr[inc], number, mask, mask, buffer, pos = lzr_next_bit(
            buf_ptr[inc], number, mask, mask, buffer, inbuf, pos
        )
        
        if n_bits >= 2:
            bit, buf_ptr[2*inc], number, mask, mask, buffer, pos = lzr_next_bit(
                buf_ptr[2*inc], number, mask, mask, buffer, inbuf, pos
            )
    
    return (number, flag, mask, buffer, pos, buf_ptr)


def decompress_2rlz(
    inbuf: bytes,
    outcapacity: int,
    verbose: bool = False
) -> Optional[bytes]:
    """
    Decompress 2RLZ compressed data.
    
    Args:
        inbuf: Input buffer with 2RLZ data
        outcapacity: Maximum output size
        verbose: Enable verbose output
    
    Returns:
        Decompressed data or None on error
    """
    if len(inbuf) < 8:
        return None
    
    # Check magic
    if inbuf[0:4] != b'2RLZ':
        if verbose:
            print("Invalid 2RLZ magic")
        return None
    
    try:
        stream_type = inbuf[4] if inbuf[4] < 128 else inbuf[4] - 256  # Convert to signed
        buffer = (inbuf[5] << 24) | (inbuf[6] << 16) | (inbuf[7] << 8) | inbuf[8]
        
        inbuf_view = memoryview(inbuf)
        pos = 9
        outbuf = bytearray(outcapacity)
        out_pos = 0
        
        # Handle uncompressed data
        if stream_type < 0:
            data_size = buffer
            if data_size > outcapacity:
                if verbose:
                    print("Output buffer too small")
                return None
            outbuf[0:data_size] = inbuf[pos:pos+data_size]
            if verbose:
                print(f"2RLZ uncompressed copy: {data_size} bytes")
            return bytes(outbuf[:data_size])
        
        # Initialize probability buffer
        buf = [0x80] * 2800
        mask = 0xFFFFFFFF
        last_char = 0
        buf_off = 0
        
        # Main decompression loop
        while out_pos < outcapacity:
            buf_ptr1_idx = buf_off + 2488
            
            bit, buf[buf_ptr1_idx], _, mask, mask, buffer, pos = lzr_next_bit(
                buf[buf_ptr1_idx], None, mask, mask, buffer, inbuf_view, pos
            )
            
            if not bit:
                # Single new char
                if buf_off > 0:
                    buf_off -= 1
                
                if out_pos >= outcapacity:
                    if verbose:
                        print("Output buffer overflow")
                    return None
                
                # Read byte using probabilities
                buf_ptr1_base = (((((out_pos & 0x07) << 8) + last_char) >> stream_type) & 0x07) * 0xFF
                j = 1
                while j <= 0xFF:
                    bit, buf[buf_ptr1_base + j], j, mask, mask, buffer, pos = lzr_next_bit(
                        buf[buf_ptr1_base + j], j, mask, mask, buffer, inbuf_view, pos
                    )
                
                outbuf[out_pos] = j & 0xFF
                out_pos += 1
                last_char = j & 0xFF
            else:
                # Sequence of chars that exists in output stream
                test_mask = mask
                n_bits = -1
                flag = 1
                
                # Find number of bits of sequence length
                while flag != 0 and n_bits < 6:
                    buf_ptr1_idx += 8
                    flag, buf[buf_ptr1_idx], _, test_mask, mask, buffer, pos = lzr_next_bit(
                        buf[buf_ptr1_idx], None, test_mask, mask, buffer, inbuf_view, pos
                    )
                    n_bits += flag
                
                # Find sequence length
                buf_ptr2_idx = n_bits + 2033
                j_limit = 64
                
                if flag != 0 or n_bits >= 0:
                    buf_ptr1_base = (n_bits << 5) + (((out_pos << n_bits) & 0x03) << 3) + buf_off + 2552
                    buf_ptr = [buf[buf_ptr1_base + i*8] for i in range(4)]
                    seq_len, flag, mask, buffer, pos, buf_ptr = lzr_get_number(
                        n_bits, buf_ptr, 8, mask, buffer, inbuf_view, pos
                    )
                    # Update buf
                    for i in range(4):
                        buf[buf_ptr1_base + i*8] = buf_ptr[i]
                    
                    if seq_len == 0xFF:
                        # End of data stream
                        if verbose:
                            print(f"2RLZ decompressed: {out_pos} bytes")
                        return bytes(outbuf[:out_pos])
                    
                    if flag != 0 or n_bits > 0:
                        buf_ptr2_idx += 56
                        j_limit = 352
                else:
                    seq_len = 1
                
                # Find number of bits of sequence offset
                i = 1
                while True:
                    n_bits = (i << 4) - j_limit
                    bit, buf[buf_ptr2_idx + (i << 3)], i, mask, mask, buffer, pos = lzr_next_bit(
                        buf[buf_ptr2_idx + (i << 3)], i, mask, mask, buffer, inbuf_view, pos
                    )
                    flag = bit
                    if n_bits >= 0:
                        break
                
                # Find sequence offset
                if flag or n_bits > 0:
                    if not flag:
                        n_bits -= 8
                    buf_ptr = [buf[n_bits + 2344 + i] for i in range(4)]
                    seq_off, flag, mask, buffer, pos, buf_ptr = lzr_get_number(
                        n_bits // 8, buf_ptr, 1, mask, buffer, inbuf_view, pos
                    )
                    # Update buf
                    for i in range(4):
                        buf[n_bits + 2344 + i] = buf_ptr[i]
                else:
                    seq_off = 1
                
                # Copy sequence
                if out_pos < seq_off:
                    if verbose:
                        print(f"Invalid sequence offset: {seq_off} at position {out_pos}")
                    return None
                
                if out_pos + seq_len + 1 > outcapacity:
                    if verbose:
                        print("Output buffer overflow during sequence copy")
                    return None
                
                # Copy bytes
                for i in range(seq_len + 1):
                    outbuf[out_pos + i] = outbuf[out_pos - seq_off + i]
                
                out_pos += seq_len + 1
                buf_off = ((out_pos + 1) & 0x01) + 0x06
                last_char = outbuf[out_pos - 1]
        
        if verbose:
            print(f"2RLZ decompressed: {out_pos} bytes")
        return bytes(outbuf[:out_pos])
        
    except Exception as e:
        if verbose:
            print(f"2RLZ decompression exception: {e}")
            import traceback
            traceback.print_exc()
        return None
