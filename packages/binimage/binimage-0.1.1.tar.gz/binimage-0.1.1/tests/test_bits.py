from binimage.decoder import bits_to_bytes, bytes_to_text

def test_bits_to_bytes_basic():
    # "Hi" -> 0x48 0x69 -> 01001000 01101001
    bits = "0100100001101001"
    data = bits_to_bytes(bits)
    assert data == b"Hi"
    text, enc = bytes_to_text(data)
    assert text == "Hi"
