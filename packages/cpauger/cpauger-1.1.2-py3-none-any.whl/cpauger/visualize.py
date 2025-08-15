import cv2
import json
import os
from glob import glob
from PIL import Image, ImageDraw, ImageFont
import random
from pycocotools.coco import COCO
from typing import Tuple, Union

def visualize_bboxes(annotation_file: str, image_dir: str, output_dir: str)->None:
    """Visualize bbox(es) of objects in image(s) when given coco annotation file

    Args:
        annotation_file (str, Path): Coco annotation file path
        image_dir (str): Directory where images to visualize are located
        output_dir (str): Directory to store the output of visualization
    Returns: None
    """
    with open(annotation_file, 'r') as f:
        coco_data = json.load(f)
    category_map = {category['id']: category['name'] for category in coco_data['categories']}

    for image_info in coco_data['images']:
        image_id = image_info['id']
        image_path = os.path.join(image_dir, image_info['file_name'])
        image = cv2.imread(image_path)
        annotations = [ann for ann in coco_data['annotations'] if ann['image_id'] == image_id]
        for ann in annotations:
            bbox = ann['bbox']
            category_id = ann['category_id']
            category_name = category_map[category_id]
            x, y, w, h = map(int, bbox)
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(image, category_name, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        output_path = os.path.join(output_dir, f"bbox_{image_info['file_name']}")
        cv2.imwrite(output_path, image)
        print(f"Bounding boxes visualized for {image_info['file_name']} and saved as {output_path}")

def random_color() -> Tuple[int, int, int]:
    """ Generate random RGB color values"""
    return tuple(random.randint(0, 255) for _ in range(3))

def draw_bbox_and_polygons(annotation_path: str, img_dir: Union[str, None]=None, 
                           visualize_dir: str="visualize_bbox_and_polygons",
                           imgpaths_list: Union[str, None]=None
                           ) -> None:
    """Visualize the bbox(es) and segmentation mask(s) of objects in image(s)

    Args:
        annotation_path (str): Coco annotation path for image(s).
        img_dir (str, optional): Directory of images. This is required when imgpaths_list 
                                is not provided in which case all images in img_dir 
                                will be visualize.
        visualize_dir (str, optional): Directory to store output of visualization. 
                                        Defaults to "visualize_bbox_and_polygons".
        imgpaths_list (str, optional): List of images to visualize. Required when img_dir 
                                        is not povided. Use when only a subset of images 
                                        are to visualize rather than all images in the img_dir.
                                        Defaults to None.

    Returns: None
    """
    if not img_dir and not imgpaths_list:
        raise ValueError("Either img_dir or imgpaths_list should be provided")
    os.makedirs(visualize_dir, exist_ok=True)
    coco = COCO(annotation_path)
    for id, imginfo in coco.imgs.items():
        file_name = imginfo["file_name"]
        imgid = imginfo["id"]
        ann_ids = coco.getAnnIds(imgIds=imgid)
        anns = coco.loadAnns(ids=ann_ids)
        bboxes = [ann["bbox"] for ann in anns]

        polygons = [ann["segmentation"][0] for ann in anns]
        category_ids = [ann["category_id"] for ann in anns]
        category_names = [coco.cats[cat_id]["name"] for cat_id in category_ids]
        ann_ids = [ann["id"] for ann in anns]
        if img_dir:
            image_path = os.path.join(img_dir, file_name)
        elif imgpaths_list:
            image_path = [imgpath for imgpath in imgpaths_list if os.path.basename(imgpath) == file_name][0]
        
        img = Image.open(image_path).convert("RGBA")
        mask_img = Image.new("RGBA", img.size)
        draw = ImageDraw.Draw(mask_img)
        font = ImageFont.load_default()
        # Draw bounding boxes
        for bbox, polygon, category_name, ann_id in zip(bboxes, polygons, category_names, ann_ids):
            color = random_color()
            bbox = [bbox[0], bbox[1], bbox[0]+bbox[2], bbox[1]+bbox[3]]
            draw.rectangle(bbox, outline=color, width=2)
            draw.polygon(polygon, outline=color, fill=color + (100,))
            text_position = (bbox[0], bbox[1] - 10)
            draw.text(text_position, category_name, fill=color, font=font)
        blended_img = Image.alpha_composite(img, mask_img)
        final_img = blended_img.convert("RGB")
        # Save the output image
        output_path = os.path.join(visualize_dir, file_name) 
        final_img.save(output_path, format='PNG') 
