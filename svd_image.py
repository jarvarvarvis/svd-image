import sys

import numpy as np
from scipy import linalg
import cv2

from matplotlib import pyplot as plt

import image_format
import cmdline

# Print options
np.set_printoptions(precision=2)
np.set_printoptions(threshold=np.inf)
np.set_printoptions(linewidth=np.inf)

# Get command line arguments
command_line_args = cmdline.get_command_line_args()

# Get the image as RGB or grayscale, depending on color mode
print("Using color mode", command_line_args["color_mode"], "to read image")

if command_line_args["color_mode"] == "grayscale":
    img = cv2.imread(command_line_args["path"], 0)
else:
    img = cv2.imread(command_line_args["path"])
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

# Pack pixel colors per row into one row of the matrix in color mode
original_shape = img.shape
if command_line_args["color_mode"] == "color":
    img = img.reshape(*img.shape[:-2], -1)

print("Final image dimension:", np.shape(img))

# Normalize image values
vmin_A = 0
vmax_A = 1
A = img / 255.0

# Compress using SVD
is_percentage_mode = command_line_args["sv_mode"] == "sv_percentage"

precision = command_line_args["precision"]

print("Percentage mode?", is_percentage_mode)
print("Precision:", precision)

(compressed_us, compressed_vs, compressed_s) = image_format.compress(
    A,
    use_count=not(is_percentage_mode), used_singular_values=int(command_line_args["sv_value"]),
    use_percentage=is_percentage_mode, used_singular_values_percentage=float(command_line_args["sv_value"])
)

print()
image_format.save_compressed_image(command_line_args["out_path"], compressed_us, compressed_vs, compressed_s, precision=precision)
print()
(us, vs, s) = image_format.read_compressed_image(command_line_args["out_path"])
print()

# Reconstruct the matrix and then the image
R_A = image_format.reconstruct_matrix(us, vs, s)
r_img = R_A.reshape(original_shape)

# Configure plots
fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(15, 7))
fig.tight_layout()

# Show original and reconstructed image
if command_line_args["color_mode"] == "grayscale":
    gray_cmap = plt.colormaps["gray"]
    ax[0].imshow(img, interpolation="nearest", cmap=gray_cmap)
    ax[0].set_title("Original image")

    ax[1].imshow(r_img, interpolation="nearest", cmap=gray_cmap)
    ax[1].set_title("Reconstructed image")

else:
    ax[0].imshow(img, interpolation="nearest")
    ax[0].set_title("Original image")

    ax[1].imshow(r_img, interpolation="nearest")
    ax[1].set_title("Reconstructed image")

# Calculate error
E = abs(R_A - A)

# Packed matrix has 3x more data per row in color mode -> set aspect ratio to 3
aspect = 3.0 if command_line_args["color_mode"] == "color" else 1.0

img_cmap = plt.colormaps["gray"]
ax[2].imshow(E, interpolation="nearest", vmin=vmin_A, vmax=vmax_A, cmap=img_cmap, aspect=aspect)
ax[2].set_title(f"Absolute error per matrix entry")

# Output mean and median error
print(f"Mean error   = {np.mean(E)}")
print(f"Median error = {np.median(E)}")

# Finally, display
plt.show()
