def sokkia_checksum(buf):
    """
    Get Sokkia checksum for buf. Second complement of the sum of ascii codes.
    Returns the last two hex digits as a string (uppercase).
    """
    total = 0
    for c in buf:
        total += ord(c)
    total = -total
    hex_str = f"{total:X}"
    # Return the last two characters (pad with zeros if needed)
    return hex_str[-2:].upper().zfill(2)

# Should be 88
buf = "0002624 0941455 0244103 "
print(f"Checksum for '{buf}': {sokkia_checksum(buf)}")

# Shoul be 85
buf = "0002624 0941506 0244102 "
print(f"Checksum for '{buf}': {sokkia_checksum(buf)}")

# Should be A4
buf = "123456712345671234567A4"
print(f"Checksum for '{buf}': {sokkia_checksum(buf)}")

buf = "A SETXXX, 123456, 4100, 2506,"
print(f"Checksum for '{buf}': {sokkia_checksum(buf)}")

# Should be 97
buf = "0006662 0804806 0394324 "
print(f"Checksum for '{buf}': {sokkia_checksum(buf)}")
