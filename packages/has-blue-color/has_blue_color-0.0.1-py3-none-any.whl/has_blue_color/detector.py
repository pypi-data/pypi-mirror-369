import cv2
import numpy as np
from pathlib import Path

def has_blue_color(image_rel_path: str) -> bool:
    """
    Detects if an image contains the color blue.

    :param image_rel_path: Relative path to the .png image (e.g., "output/image.png").
    :param threshold: Minimum fraction of blue pixels required to confirm presence.
    :return: True if the image has blue color, otherwise False.
    """

    output_folder = Path("output")

    image_path = output_folder / image_rel_path  # Moves up one level and appends image path

    if not image_path.is_file():
        raise FileNotFoundError(f"Image not found: {image_path}")


    image = cv2.imread(str(image_path))
    
    # Convert image to HSV
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Define blue color range
    lower_blue = np.array([100, 150, 50])
    upper_blue = np.array([140, 255, 255])

    # Create mask
    mask = cv2.inRange(hsv, lower_blue, upper_blue)

    # Efficiently count nonzero pixels
    return np.count_nonzero(mask) > 0

