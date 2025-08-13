import pytest
import zlib
from pypatchergba.patcher import apply_ips, apply_ups, apply_bps, apply_patch, read_vli
import io

# --- VLI Tests ---

def test_read_vli_simple():
    # 0 is encoded as 0x80
    stream = io.BytesIO(b"\x80")
    assert read_vli(stream) == 0

def test_read_vli_multibyte():
    # 300 is encoded as 0x2C 0x81
    stream = io.BytesIO(b"\x2C\x81")
    assert read_vli(stream) == 300

def test_read_vli_eof():
    # Truncated VLI
    stream = io.BytesIO(b"\x2C")
    with pytest.raises(EOFError):
        read_vli(stream)

# --- IPS Tests ---

def test_ips_simple_patch():
    source = b"HELLO WORLD"
    target = b"HELLO THERE"
    # Patch record: offset 6 (00 00 06), size 5 (00 05), payload "THERE"
    patch_data = b"PATCH" + b"\x00\x00\x06\x00\x05" + b"THERE" + b"EOF"
    assert apply_ips(source, patch_data) == target

def test_ips_rle_patch():
    source = b"AAAAAAAAAA" # 10 A"s
    target = b"ZZZZZAAAAA" # 5 Z"s, 5 A"s
    # RLE record: offset 0 (00 00 00), size 0 (00 00), RLE size 5 (00 05), byte "Z"
    patch_data = b"PATCH" + b"\x00\x00\x00\x00\x00" + b"\x00\x05Z" + b"EOF"
    assert apply_ips(source, patch_data) == target

def test_ips_invalid_header():
    with pytest.raises(ValueError, match="Invalid IPS patch header"):
        apply_ips(b"", b"INVALID")

def test_ips_truncated():
    patch_data = b"PATCH" + b"\x00\x00\x06\x00\x05" + b"THER" # Missing "E" and EOF
    with pytest.raises(ValueError):
        apply_ips(b"HELLO WORLD", patch_data)

# --- UPS Tests ---

def test_ups_simple_patch_success():
    source = b"SOURCE FILE DATA"
    target = b"SOURCE FILE DAtA" # "t" -> "t" ^ 0x02 = "r", "A" -> "A" ^ 0x20 = "a"
    
    # Hand-craft a valid UPS patch
    # 1. Header
    patch = b"UPS1"
    # 2. Source/Target size VLIs (len=16 -> 0x90)
    patch += b"\x90\x90"
    # 3. Patch body: skip 14, XOR 0x20, skip 0, XOR 0x02, end chunk
    # skip 14 -> vli(14) = 0x8E
    # skip 0 -> vli(0) = 0x80
    patch_body = b"\x8E\x20\x80\x02\x00"
    patch += patch_body
    # 4. Footer CRCs
    patch += zlib.crc32(source).to_bytes(4, "little")
    patch += zlib.crc32(target).to_bytes(4, "little")
    patch += zlib.crc32(patch_body).to_bytes(4, "little")

    assert apply_ups(source, patch) == target

def test_ups_source_size_mismatch():
    source = b"WRONG SIZE"
    patch = b"UPS1" + b"\x90\x90" + b"\x00" + (b"\x00" * 12) # Patch expects size 16
    with pytest.raises(ValueError):
        apply_ups(source, patch)

def test_ups_source_crc_mismatch():
    source = b"CORRUPT SOURCE!!" # Correct length (16) but wrong data
    target = b"SOURCE FILE DAtA"
    patch_body = b"\x8E\x20\x80\x02\x00"
    patch = b"UPS1" + b"\x90\x90" + patch_body
    # Use CRC of the *correct* source to build the patch
    patch += zlib.crc32(b"SOURCE FILE DATA").to_bytes(4, "little")
    patch += zlib.crc32(target).to_bytes(4, "little")
    patch += zlib.crc32(patch_body).to_bytes(4, "little")
    
    with pytest.raises(ValueError, match="Source file is invalid"):
        apply_ups(source, patch)

# --- BPS Tests ---
def test_bps_simple_patch_success():
    source = b"ABCDEFGHIJKLMNOP"
    target = b"ABCDEFGHIJKLxxxx"
    
    # Hand-craft a valid BPS patch
    patch = b"BPS1"
    # Source/Target size VLIs (len=16 -> 0x90)
    patch += b"\x90\x90"
    # Metadata size (0 -> 0x80)
    patch += b"\x80"
    
    # Patch Body
    # Action 0 (SourceRead), len 12 -> command VLI (12-1)<<2|0 = 44 = 0x2C
    # Action 1 (TargetRead), len 4 -> command VLI (4-1)<<2|1 = 13 = 0x0D
    patch_body = b"\x2C" + b"\x0D" + b"xxxx"
    patch += patch_body
    
    # Footer CRCs
    patch += zlib.crc32(source).to_bytes(4, "little")
    patch += zlib.crc32(target).to_bytes(4, "little")
    patch += zlib.crc32(patch_body).to_bytes(4, "little")

    assert apply_bps(source, patch) == target

def test_bps_crc_mismatch():
    source = b"WRONG DATA"
    target = b"ABCDEFGHIJKLxxxx"
    patch_body = b"\x2C\x0D" + b"xxxx"
    patch = b"BPS1" + b"\x90\x90\x80" + patch_body
    # Use CRC of correct source
    patch += zlib.crc32(b"ABCDEFGHIJKLMNOP").to_bytes(4, "little")
    patch += zlib.crc32(target).to_bytes(4, "little")
    patch += zlib.crc32(patch_body).to_bytes(4, "little")
    
    with pytest.raises(ValueError, match="Source file is invalid"):
        apply_bps(source, patch)

# --- Dispatcher Tests ---
def test_apply_patch_dispatcher():
    # A minimal valid IPS patch
    ips_patch = b"PATCH" + b"EOF"
    assert apply_patch(b"", ips_patch) == b""
    
    # A minimal (but invalid due to CRC) UPS patch to test routing
    ups_patch = b"UPS1" + b"\x80\x80" + (b"\x00" * 12)
    with pytest.raises(ValueError):
        apply_patch(b"", ups_patch)
        
    # A minimal (but invalid due to CRC) BPS patch to test routing
    bps_patch = b"BPS1" + b"\x80\x80\x80" + (b"\x00" * 12)
    with pytest.raises(ValueError):
        apply_patch(b"", bps_patch)
        
    # Unknown format
    with pytest.raises(ValueError):
        apply_patch(b"", b"UNKNOWN")