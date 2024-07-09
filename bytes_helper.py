import math

def to_bin_str(value, fill_count):
    return bin(value)[2:].zfill(fill_count)

def to_bin_str_all(values_list, fill_count):
    return [to_bin_str(values, fill_count) for values in values_list]


def pack_bits_into_bytes(bits):
    data = bytearray()
    while len(bits) > 0:
        byte = bits[:8]
        accumulator = 0

        # Go over all current bits and add them to the beginning of the accumulator
        for i in range(len(byte)):
            accumulator = accumulator | (byte[i] << (8 - i - 1))

        data.append(accumulator)

        # Remove first 8 bits from list
        bits = bits[8:]

    return data

def pack_values_into_bytearray(values, exponent):
    data = bytearray()

    # All values and its parts are aligned to a full byte
    for value in values:
        # If the value is a list, pack recursively
        if type(value) == list:
            data.extend(pack_values_into_bytearray(value, exponent))
            continue

        bits = []

        # Go over relevant bits of the value
        for i in range(exponent):
            bit = (value >> (exponent - i - 1)) & 1
            bits.append(bit)

        # Fill remaining bits with 0
        bytes_count = math.floor((exponent - 1) / 8)
        next_exponent_multiple_of_8 = (bytes_count + 1) * 8

        remaining_bits_for_byte_align = next_exponent_multiple_of_8 - exponent
        for i in range(remaining_bits_for_byte_align):
            bits.append(0)

        # Pack bits into full bytes and add to list
        data.extend(pack_bits_into_bytes(bits))

    return data


def unpack_values_from_bytearray(values, exponent, tight=False):
    bytes_per_entry = math.ceil(exponent / 8)

    data = [0] * int(len(values) / bytes_per_entry)
    data_idx = 0

    # ex. exponent = 12
    # The data layout is as follows:
    # [ a b c d e f g h ] [ i j k l 0 0 0 0 ] [ a b c d e f g h ] [ i j k l 0 0 0 0 ]
    # ^                   ^                   ^                   ^
    # Value 1, byte 1     Value 1, byte 2     Value 2, byte 1     Value 2, byte 2
    for i in range(len(data)):
        aligned_to_entire_bytes = (exponent % 8 == 0)
        for j in range(bytes_per_entry):
            byte_idx = i * bytes_per_entry + j
            current_byte = values[byte_idx]

            # Append bits with byte alignment
            back_idx = bytes_per_entry - j - 1
            data[i] |= current_byte << (back_idx * 8)

            # If this is the last entry, shift the entire value right by `8 - remainder` (if necessary)
            if j == bytes_per_entry - 1 and not(aligned_to_entire_bytes):
                remainder = exponent % 8
                data[i] >>= 8 - remainder

    return data

# Data helper test function
def data_helper_test_byte_aligned_1():
    import random

    TEST_ITERATIONS = 100

    VALUES_COUNT = 300
    EXPONENT = 64

    # Do test iterations
    match_counts = 0
    for i in range(TEST_ITERATIONS):
        exponent = random.randint(1, EXPONENT)

        max_value = 2 ** exponent - 1
        values = [random.randint(0, max_value) for _ in range(VALUES_COUNT)]

        packed_values = pack_values_into_bytearray(values, exponent)
        unpacked_values = unpack_values_from_bytearray(packed_values, exponent)

        arrays_match = values == unpacked_values
        if arrays_match:
            match_counts += 1

        match_status = "✅" if arrays_match else "❌"
        print(f"Iteration {i}: {match_status}")
        assert arrays_match

    print(f"Matches: {match_counts} / {TEST_ITERATIONS}")



def test_runner(functions):
    for function in functions:
        print(f"====== Test {function.__name__} ======")
        function()
        print()

if __name__ == "__main__":
    test_runner([
        data_helper_test_byte_aligned_1
    ])

