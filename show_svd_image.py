import sys

import numpy as np
from scipy import linalg
import cv2

from matplotlib import pyplot as plt

import image_format

if len(sys.argv) == 1:
    print(f"Expected arguments: {sys.argv[0]} PATH [color/grayscale]")
    sys.exit(-1)

(us, vs, s) = image_format.read_compressed_image(sys.argv[1])
height   = us.shape[1]
width    = vs.shape[1]
sv_count = s.shape[0]

# Grayscale?
grayscale = False
if len(sys.argv) > 2:
    if sys.argv[2] != "color" and sys.argv[2] != "grayscale":
        print(f"Unexpected value `{sys.argv[2]}` for color_mode, needs to be one of: color, grayscale")
        sys.exit(-1)

    grayscale = (sys.argv[2] == "grayscale")

# Reconstruct the matrix and then the image
img = image_format.reconstruct_matrix(us, vs, s)

if not(grayscale):
    rgb_shape = (height, int(width / 3), 3)
    img = img.reshape(rgb_shape)

print(f"Matrix shape: {img.shape}")

# Configure plots
fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(10, 8))
fig.tight_layout()

if grayscale:
    img_cmap = plt.colormaps["gray"]
    ax.imshow(img, interpolation="nearest", vmin=0, vmax=1, cmap=img_cmap)
else:
    ax.imshow(img, interpolation="nearest")

# Finally, display
plt.show()
