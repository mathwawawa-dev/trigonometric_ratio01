# -*- coding: utf-8 -*-
"""
batch_crop_all_folders.py — Tri_img_01, Tri_img_02, Tri_img_03 전체 1,836개 이미지 투명 여백 크롭 
결과를 각각 Tri_img_01_crop, Tri_img_02_crop, Tri_img_03_crop 폴더에 저장
"""
import os, glob, time
from concurrent.futures import ProcessPoolExecutor
from PIL import Image

PY_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT   = os.path.dirname(PY_DIR)

TARGET_FOLDERS = [
    ('Tri_img_01', 'Tri_img_01_crop'),
    ('Tri_img_02', 'Tri_img_02_crop'),
    ('Tri_img_03', 'Tri_img_03_crop'),
]

def crop_single_image(args):
    src_path, dst_path, margin = args
    try:
        with Image.open(src_path) as img:
            img = img.convert("RGBA")
            bbox = img.getbbox()
            if bbox:
                left   = max(0, bbox[0] - margin)
                upper  = max(0, bbox[1] - margin)
                right  = min(img.width, bbox[2] + margin)
                lower  = min(img.height, bbox[3] + margin)
                cropped = img.crop((left, upper, right, lower))
                cropped.save(dst_path, "PNG")
            else:
                img.save(dst_path, "PNG")
        return True
    except Exception as e:
        print(f"Error processing {src_path}: {e}")
        return False

def main():
    t_start = time.time()
    margin = 12   # 라벨/각 기호 훼손 차단용 12px 안전 여백
    
    tasks = []
    total_files = 0

    for src_dir_name, dst_dir_name in TARGET_FOLDERS:
        src_dir = os.path.join(ROOT, src_dir_name)
        dst_dir = os.path.join(ROOT, dst_dir_name)
        os.makedirs(dst_dir, exist_ok=True)
        
        files = glob.glob(os.path.join(src_dir, '*.png'))
        total_files += len(files)
        
        for src_path in files:
            fname = os.path.basename(src_path)
            dst_path = os.path.join(dst_dir, fname)
            tasks.append((src_path, dst_path, margin))

    print(f"총 {total_files}개 이미지 투명 여백 크롭 작업 시작 (안전 여백: {margin}px)...")

    # 병렬 처리로 초고속 처리
    success_count = 0
    with ProcessPoolExecutor() as executor:
        results = executor.map(crop_single_image, tasks)
        for r in results:
            if r: success_count += 1

    t_elapsed = time.time() - t_start
    print(f"DONE: Total {success_count}/{total_files} images cropped in {t_elapsed:.2f} seconds.")

if __name__ == '__main__':
    main()
