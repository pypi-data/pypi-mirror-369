import cv2
import numpy as np

def gamma_trans(img, gamma=1.2):
    gamma_table = np.round(np.array([((x / 255.0) ** gamma) * 255.0 for x in range(256)])).astype(np.uint8)
    return cv2.LUT(img, gamma_table)

def dehazing(image, grid=8, limit=2, enhance_saturation=False):
    # Convert to HSV
    image_hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    v_channel = image_hsv[:, :, 2]
    s_channel = image_hsv[:, :, 1]

    if enhance_saturation:
        s_channel = cv2.addWeighted(s_channel, 1.5, np.zeros_like(s_channel), 0, 0)

    clahe = cv2.createCLAHE(clipLimit=limit, tileGridSize=(grid, grid))
    v_channel_eq = clahe.apply(v_channel)

    image_hsv[:, :, 2] = v_channel_eq
    if enhance_saturation:
        image_hsv[:, :, 1] = s_channel

    image_dehazed = cv2.cvtColor(image_hsv, cv2.COLOR_HSV2BGR)
    image_dehazed = gamma_trans(image_dehazed, 1.2)
    return image_dehazed
