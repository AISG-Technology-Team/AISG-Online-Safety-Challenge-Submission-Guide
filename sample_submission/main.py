# Standard Python Library
import sys
import logging
import random

# Import opencv
import cv2

# Import pytesseract
import pytesseract
from pytesseract import Output

# Import numpy
import numpy as np


def get_meme_text(image):
    config = "-l eng+chi_sim+chi_tra+tam+msa --psm 4 --oem 1"

    text = pytesseract.image_to_string(image, config=config)
    d = pytesseract.image_to_data(image, output_type=Output.DICT, config=config)
    n_boxes = len(d["level"])
    coordinates = []

    for i in range(n_boxes):
        (x, y, w, h) = (d["left"][i], d["top"][i], d["width"][i], d["height"][i])
        coordinates.append((x, y, w, h))
    return text, coordinates


def get_image_mask(image, coordinates_to_mask):
    # Create a mask image with image_size
    image_mask = np.zeros_like(image[:, :, 0])

    for coordinates in coordinates_to_mask:
        # unpack the coordinates
        x, y, w, h = coordinates

        # set mask to 255 for coordinates
        image_mask[y : y + h, x : x + w] = 255

    return image_mask


def get_image_inpainted(image, image_mask):
    # Perform image inpainting to remove text from the original image
    image_inpainted = cv2.inpaint(
        image, image_mask, inpaintRadius=3, flags=cv2.INPAINT_TELEA
    )

    return image_inpainted


def classifier(image, text):
    # Random number generator to simulate a proba output
    # float values ranging from 0-1
    proba = random.random()

    # Using proba and some pre-fixed threshold to simulate a label output
    # label values of int : Harmful = 1, Benign = 0
    threshold = 0.5
    label = int(proba >= threshold)

    return proba, label


def process_line_by_line(*, filepath):
    # 1. Open image filepath ========================================= #
    im = cv2.imread(filepath)

    # 2. Get meme text =============================================== #
    text, coordinates = get_meme_text(image=im)

    # 3. Get inpainting ============================================== #
    # Get image mask for image inpainting
    im_mask = get_image_mask(image=im, coordinates_to_mask=coordinates)

    # (OPTIONAL) If necessary to read/write to /tmp file system for reading later
    # Write to /tmp folder
    cv2.imwrite("/tmp/temp_image_mask.png", im_mask)

    # (OPTIONAL) Read from /tmp folder
    im_mask = cv2.imread("/tmp/temp_image_mask.png", cv2.IMREAD_GRAYSCALE)

    # Perform image inpainting
    im_inpainted = get_image_inpainted(image=im, image_mask=im_mask)

    # 4. Get classification =========================================== #
    # Process text and image for harmful/benign
    proba, label = classifier(image=im_inpainted, text=text)

    return proba, label


if __name__ == "__main__":
    # Iteration loop to get new image filepath from sys.stdin:
    for line in sys.stdin:
        # IMPORTANT: Please ensure any trailing whitespace (eg: \n) is removed. This may impact some modules to open the filepath
        image_path = line.rstrip()

        try:
            # Process the image
            proba, label = process_line_by_line(filepath=image_path)

            # Ensure each result for each image_path is a new line
            sys.stdout.write(f"{proba:.4f}\t{label}\n")

        except Exception as e:
            # Output to any raised/caught error/exceptions to stderr
            sys.stderr.write(str(e))
