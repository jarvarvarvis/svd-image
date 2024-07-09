import math
import struct

import numpy as np
from scipy import linalg

import bz2

from compression import *
from bytes_helper import *

def compress(A, use_count=True, used_singular_values=0, use_percentage=False, used_singular_values_percentage=0):
    # Compute the SVD of the matrix
    U, S, Vh = linalg.svd(A)
    Uh = np.transpose(U)

    # How many singular values are used for reconstruction
    if (use_count and use_percentage) or (not(use_count) and not(use_percentage)):
        raise ValueError("Exactly one of arguments `use_count` and `use_percentage` needs to be set to True")

    if use_percentage:
        used_singular_values = max(round(len(S) * used_singular_values_percentage), 1)
        print(f"Using {used_singular_values}/{len(S)} ({used_singular_values_percentage * 100}%) of singular values for compression")

    if used_singular_values <= 0:
        raise ValueError("Given arguments caused the number of singular values to be <= 0")

    if used_singular_values > len(S):
        raise ValueError("Given arguments caused the number of singular values to be greater than the number of available values")

    # Output info
    print_compress_status(A, S, used_singular_values)

    # Return singular vectors and values stored for reconstruction
    us = Uh[:used_singular_values]
    vs = Vh[:used_singular_values]
    s  = S[:used_singular_values]

    return (us, vs, s)

def print_compress_status(A, S, used_singular_values):
    # Print some info about how much storage is saved
    raw_image_num_count     = A.shape[0] * A.shape[1]

    # We need to store the n left and n right singular vectors for each singular value (n in total),
    # as well as the singular values themselves
    reduced_image_num_count = used_singular_values * (A.shape[0] + A.shape[1]) + used_singular_values

    storage_reduction_percentage = 1.0 - reduced_image_num_count / raw_image_num_count
    print(f"Values needed to store image: {raw_image_num_count} -> {reduced_image_num_count} ({storage_reduction_percentage * 100}% reduction)")



def reconstruct_matrix(us, vs, s):
    matrix_shape = (len(us[0]), len(vs[0]))
    R_A = np.zeros(matrix_shape)

    # Reconstruct A from given matrices U, S and Vh
    for i in range(len(s)):
        R_A = R_A + s[i] * np.outer(us[i], vs[i])

    return R_A


def save_compressed_image(path, us, vs, s, precision):
    height   = us.shape[1]
    width    = vs.shape[1]
    sv_count = s.shape[0]

    data = bytearray()

    # Write precision (8 bit), maximum singular value (32-bit float), singular value count an dimensions (16 bit for the last two)
    data.extend(struct.pack("<B", precision))

    max_singular_value = max(s)
    data.extend(struct.pack("<f", max_singular_value))
    data.extend(struct.pack("<H", sv_count))

    data.extend(struct.pack("<H", height))
    data.extend(struct.pack("<H", width))

    print(f"Left vectors length: {np.prod(us.shape)}")
    print(f"Right vectors length: {np.prod(vs.shape)}")
    print(f"Singular values length: {np.prod(s.shape)}")

    # Compress data
    compressed_us = compress_normalized_numpy_array(us, precision)
    compressed_vs = compress_normalized_numpy_array(vs, precision)
    compressed_s  = compress_numpy_array_rounded(s, precision)

    # Generate data
    byte_us = pack_values_into_bytearray(compressed_us, precision)
    print(f"Compressed left vectors bytes: {len(byte_us)}")
    byte_vs = pack_values_into_bytearray(compressed_vs, precision)
    print(f"Compressed right vectors bytes: {len(byte_vs)}")
    byte_s  = pack_values_into_bytearray(compressed_s, precision)
    print(f"Compressed singular values bytes: {len(byte_s)}")

    data.extend(byte_us)
    data.extend(byte_vs)
    data.extend(byte_s)

    print(f"Total image size (bytes): {len(data)}")

    # Write data to the file
    with bz2.open(path, "wb") as binary_file:
        binary_file.write(data)

    print(f"Saved image {path}")

def read_compressed_image(path):
    with bz2.open(path, "rb") as binary_file:
        precision           = struct.unpack("<B", binary_file.read(1))[0]
        max_singular_value = struct.unpack("<f", binary_file.read(4))[0]
        sv_count           = struct.unpack("<H", binary_file.read(2))[0]
        height             = struct.unpack("<H", binary_file.read(2))[0]
        width              = struct.unpack("<H", binary_file.read(2))[0]

        print("Read float compression precision:", precision)
        print("Read maximum singular value:", max_singular_value)
        print("Read singular value count:", sv_count)
        print("Read image dimension:", (height, width))

        # Calculate size based on mode
        packed_bytes = math.ceil(precision / 8)
        us_byte_count = sv_count * height * packed_bytes
        vs_byte_count = sv_count * width  * packed_bytes
        s_byte_count  = sv_count * packed_bytes

        print(f"Compressed left vectors bytes: {us_byte_count}")
        print(f"Compressed right vectors bytes: {vs_byte_count}")
        print(f"Compressed singular values bytes: {s_byte_count}")

        byte_us = bytearray(binary_file.read(us_byte_count))
        byte_vs = bytearray(binary_file.read(vs_byte_count))
        byte_s  = bytearray(binary_file.read(s_byte_count))

        # Unpack values
        unpacked_us = unpack_values_from_bytearray(byte_us, precision)
        unpacked_vs = unpack_values_from_bytearray(byte_vs, precision)
        unpacked_s  = unpack_values_from_bytearray(byte_s,  precision)[:sv_count]

        print(f"Unpacked left vectors length: {len(unpacked_us)}")
        print(f"Unpacked right vectors length: {len(unpacked_vs)}")
        print(f"Unpacked singular values length: {len(unpacked_s)}")

        # Convert back to numpy arrays
        us_flat = np.array(decompress_normalized_list(unpacked_us, precision))
        vs_flat = np.array(decompress_normalized_list(unpacked_vs, precision))
        s       = np.array(decompress_list_rounded_with_rescale(unpacked_s, precision, max_singular_value))

        us = us_flat.reshape((sv_count, height))
        vs = vs_flat.reshape((sv_count, width))

        return (us, vs, s)
