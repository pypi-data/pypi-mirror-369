def nikon_checksum(buf):
    """
    Get Nikon checksum for buf. Second complement of the sum of ascii codes.
    Returns the last two characters as a string (uppercase).
    """
    total = 0
    for c in buf:
        total += ord(c)
    s = total & 0xFF  # lower one byte
    checksum = (s % 0x40) + 0x20
    return chr(checksum)


buf = "\x43\x54\x02\x24\x44\x4E\x58\x03"
print(f"Checksum for '{buf}': {nikon_checksum(buf)}")

checksum = nikon_checksum(buf)
print(f"Hex value of checksum: {hex(ord(checksum))}")
