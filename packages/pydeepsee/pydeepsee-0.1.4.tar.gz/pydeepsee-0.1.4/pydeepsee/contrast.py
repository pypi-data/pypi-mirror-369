import cv2
import numpy as np

def contrast_stretch(image, equalize_bands=""):
    b, g, r = cv2.split(image)

    if "R" in equalize_bands.upper():
        r = cv2.equalizeHist(r)
    if "G" in equalize_bands.upper():
        g = cv2.equalizeHist(g)
    if "B" in equalize_bands.upper():
        b = cv2.equalizeHist(b)

    def stretch_channel(channel):
        min_intensity, max_intensity = np.min(channel), np.max(channel)
        return np.uint8((channel - min_intensity) / (max_intensity - min_intensity) * 255)

    b, g, r = stretch_channel(b), stretch_channel(g), stretch_channel(r)
    return cv2.merge((b, g, r))
