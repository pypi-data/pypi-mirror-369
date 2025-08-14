import cv2
from .dehaze import dehazing
from .contrast import contrast_stretch
from .filters import bilateral_filter, sharpen

def enhance_image(image_path, grid=8, limit=2, enhance_saturation=False, equalize=""):
    image = cv2.imread(image_path)
    dehazed = dehazing(image, grid, limit, enhance_saturation)
    contrasted = contrast_stretch(dehazed, equalize)
    smoothed = bilateral_filter(contrasted)
    final = sharpen(smoothed)
    return final
