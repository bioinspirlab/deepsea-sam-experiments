#!/usr/bin/env python3
"""
Convert OBSEA annotations to COCO format and integrate SAM predictions.

This script processes ground truth bounding box annotations and SAM model
outputs into standardized COCO JSON format for evaluation.
"""

import argparse
import json
import os
from pathlib import Path
from typing import Dict, List, Tuple, Any

import cv2
import numpy as np
import pandas as pd
from pycocotools.coco import COCO


def retrieve_parallel(coords: np.ndarray) -> Tuple[int, int, int, int]:
    """
    Convert arbitrary quadrilateral coordinates to axis-aligned rectangle.
    
    Args:
        coords: 4x2 array of corner points
        
    Returns:
        Tuple of (x, y, width, height) for axis-aligned bounding box
    """
    xs = coords[:, 0]
    ys = coords[:, 1]
    
    x_min = max(0, int(np.min(xs)))
    y_min = max(0, int(np.min(ys)))
    x_max = int(np.max(xs))
    y_max = int(np.max(ys))
    
    width = x_max - x_min
    height = y_max - y_min
    
    return x_min, y_min, width, height


def load_ground_truth(annotation_file: Path) -> pd.DataFrame:
    """Load ground truth annotations from tab-separated file."""
    df = pd.read_csv(annotation_file, sep='\t')
    return df


def build_coco_gt(
    df: pd.DataFrame,
    image_dir: Path,
    output_file: Path
) -> None:
    """
    Build COCO format ground truth annotations.
    
    Args:
        df: DataFrame with ground truth annotations
        image_dir: Directory containing images
        output_file: Path to output COCO JSON file
    """
    coco_data = {
        "info": {
            "description": "OBSEA Deep-Sea Fish Dataset",
            "version": "1.0",
            "year": 2024
        },
        "licenses": [],
        "images": [],
        "annotations": [],
        "categories": [{"id": 1, "name": "fish", "supercategory": "animal"}]
    }
    
    image_id = 1
    annotation_id = 1
    image_map = {}
    
    for img_file in sorted(image_dir.glob("*.jpg")):
        image_map[os.path.basename(str(img_file))] = image_id
        img = cv2.imread(str(img_file))
        height, width = img.shape[:2]
        
        coco_data["images"].append({
            "id": image_id,
            "file_name": os.path.basename(str(img_file)),
            "width": width,
            "height": height
        })
        image_id += 1
        
    print(image_map.keys())
    for _, row in df.iterrows():
        image_name = row['IMAGE']
        if image_name not in image_map.keys():
            continue
        
        print(image_name)
        img_id = image_map[image_name]
        coords = np.array([
            [row['bboxx1 [pixel]'], row['bboxy1 [pixel]']],
            [row['bboxx2 [pixel]'], row['bboxy2 [pixel]']],
            [row['bboxx3 [pixel]'], row['bboxy3 [pixel]']],
            [row['bboxx4 [pixel]'], row['bboxy4 [pixel]']]
        ])
        
        print(coords)
        x, y, w, h = retrieve_parallel(coords)
        
        coco_data["annotations"].append({
            "id": annotation_id,
            "image_id": img_id,
            "category_id": 1,
            "bbox": [x, y, w, h],
            "area": w * h,
            "iscrowd": 0
        })
        annotation_id += 1
    
    with open(output_file, 'w') as f:
        json.dump(coco_data, f, indent=2)
    
    print(f"Saved ground truth COCO annotations to {output_file}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Convert OBSEA annotations to COCO format"
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path("obsea"),
        help="Root data directory (default: obsea)"
    )
    parser.add_argument(
        "--annotation-file",
        type=Path,
        default=None,
        help="Ground truth annotation file (default: {data-dir}/PANGAEA.946149.csv)"
    )
    parser.add_argument(
        "--image-dir",
        type=Path,
        default=None,
        help="Image directory (default: {data-dir}/image_data)"
    )
    parser.add_argument(
        "--output-gt",
        type=Path,
        default=None,
        help="Output ground truth file (default: {data-dir}/gt-rectified-coco.json)"
    )
    
    args = parser.parse_args()
    
    # Set defaults based on data-dir
    data_dir = args.data_dir
    annotation_file = args.annotation_file or data_dir / "PANGAEA.946149.csv"
    image_dir = args.image_dir or data_dir / "image_data"
    output_gt = args.output_gt or data_dir / "gt-rectified-coco.json"
   
    
    # Validate inputs
    if not annotation_file.exists():
        raise FileNotFoundError(f"Annotation file not found: {annotation_file}")
    if not image_dir.exists():
        raise FileNotFoundError(f"Image directory not found: {image_dir}")
    
    # Process
    print("Loading ground truth annotations...")
    df = load_ground_truth(annotation_file)
    
    print("Building COCO ground truth format...")
    build_coco_gt(df, image_dir, output_gt)
    
    print("Done!")


if __name__ == "__main__":
    main()