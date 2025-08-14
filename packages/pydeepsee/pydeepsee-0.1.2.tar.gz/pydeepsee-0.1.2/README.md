# Underwater Dehazer

**Underwater Dehazer** is a Python library for enhancing underwater images using a combination of:
- **CLAHE** (Contrast Limited Adaptive Histogram Equalization)  
- **Saturation Enhancement**  
- **Contrast Stretching**  
- **Bilateral Filtering**  
- **Sharpening**  

It works for underwater, hazy, or low-contrast images to bring out details and improve visibility.

---

## Installation

```bash
pip install pydeepsee==0.1.2
```

---

## Useage

```bash
from pydeepsee import enchance_image
import cv2

result = enhance_image(
    "underwater.jpg",
    grid=8,               # CLAHE grid size
    limit=2,              # CLAHE clip limit
    enhance_saturation=True,  # Boost colors
    equalize="RGB"        # Equalize specific color channels
)

cv2.imwrite("enhanced.jpg", result)

```