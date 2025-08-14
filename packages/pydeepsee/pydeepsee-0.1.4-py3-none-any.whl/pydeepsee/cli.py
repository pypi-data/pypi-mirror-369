import argparse
import cv2
from . import enhance_image

def main():
    parser = argparse.ArgumentParser(description="Enhance underwater images")
    parser.add_argument("image_path", help="Path to input image")
    parser.add_argument("--grid", type=int, default=8)
    parser.add_argument("--limit", type=int, default=2)
    parser.add_argument("--sat", action="store_true", help="Enhance saturation")
    parser.add_argument("--equalize", type=str, default="", help="Bands to equalize, e.g., RGB or G")
    parser.add_argument("--output", type=str, default="enhanced.jpg", help="Output file name")
    
    args = parser.parse_args()

    result = enhance_image(args.image_path, args.grid, args.limit, args.sat, args.equalize)
    cv2.imwrite(args.output, result)
    print(f"Enhanced image saved to {args.output}")
