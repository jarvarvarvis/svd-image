import math

def compress_fraction_with_power_of_2(value, exponent):
    # Value is in the range [-1, 1], convert that to [0,1]
    value = max(min(value, 1.0), -1.0)
    value = (value + 1) / 2.0
    # Convert value to a multiple of (2 ** exponent - 1)
    value = value * (2 ** exponent - 1)
    return int(value)

def compress_normalized_list_recursively(values, exponent):
    compressed = []
    for value in values:
        if type(value) == list:
            compressed.append(compress_normalized_list_recursively(value, exponent))
        else:
            compressed.append(compress_fraction_with_power_of_2(value, exponent))

    return compressed

def compress_normalized_numpy_array(array, exponent):
    return compress_normalized_list_recursively(array.tolist(), exponent)



def compress_list_rounded_recursively(values, exponent):
    max_value = max(values)
    compressed = []
    for value in values:
        if type(value) == list:
            compressed.append(compress_list_rounded_recursively(value, exponent))
        else:
            # Remap the value to the range [0, 2 ** exponent - 1]
            value = int((value / max_value) * (2 ** exponent - 1))
            compressed.append(value)

    return compressed

def compress_numpy_array_rounded(array, exponent):
    return compress_list_rounded_recursively(array.tolist(), exponent)



def decompress_fraction_with_power_of_2(value, exponent):
    # Get value in range [0, 2 ** e - 1]
    value = max(min(float(value), 2 ** exponent - 1), 0)
    # Normalize, range is now [0, 1]
    value = value / (2 ** exponent - 1)
    # Rescale to interval [-1, 1]
    value = value * 2 - 1
    return value

def decompress_normalized_list(values, exponent):
    return [decompress_fraction_with_power_of_2(value, exponent) for value in values]

def decompress_list_rounded_with_rescale(values, exponent, rescale):
    return [
        # Normalize the value to the range [0, 2 ** exponent - 1] and
        # then rescale with the given value
        rescale * (value / (2 ** exponent - 1)) for value in values
    ]
