from src.sboxes import AES_SBOX, PRESENT_SBOX, aes_sbox, present_sbox
from src.utils import bits_to_int_lsb, int_to_bits_lsb


def test_bit_round_trip():
    for width in (3, 4, 8):
        for value in range(1 << width):
            assert bits_to_int_lsb(int_to_bits_lsb(value, width)) == value


def test_present_table_known_entries():
    assert PRESENT_SBOX[0x0] == 0xC
    assert PRESENT_SBOX[0xF] == 0x2
    assert bits_to_int_lsb(present_sbox(int_to_bits_lsb(0x0, 4))) == 0xC


def test_aes_table_known_entries():
    assert AES_SBOX[0x00] == 0x63
    assert AES_SBOX[0x53] == 0xED
    assert bits_to_int_lsb(aes_sbox(int_to_bits_lsb(0x53, 8))) == 0xED


def test_sboxes_are_permutations():
    assert len(set(PRESENT_SBOX)) == 16
    assert len(set(AES_SBOX)) == 256
