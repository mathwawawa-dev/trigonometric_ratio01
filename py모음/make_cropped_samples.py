# -*- coding: utf-8 -*-
"""
make_cropped_samples.py — sample001/ 폴더에 여백 제거(Auto-crop) 처리된 샘플 이미지 4개 생성
"""
import os, math, importlib.util
import numpy as np
from PIL import Image

PY_DIR   = os.path.dirname(os.path.abspath(__file__))
ROOT     = os.path.dirname(PY_DIR)
SAMPLE_DIR = os.path.join(ROOT, 'sample001')
os.makedirs(SAMPLE_DIR, exist_ok=True)

# v1.0.5_260809_0010_dash_trim3.py 로드
_base_script = os.path.join(PY_DIR, 'v1.0.5_260809_0010_dash_trim3.py')
spec = importlib.util.spec_from_file_location('tri_draw', _base_script)
mod  = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
mod.OUTPUT_DIR = SAMPLE_DIR

def crop_transparent_padding(filepath, margin=12):
    """PNG 이미지의 투명 여백을 자동으로 잘라내고 지정한 margin(px)만 남김"""
    with Image.open(filepath) as img:
        img = img.convert("RGBA")
        bbox = img.getbbox()
        if bbox:
            # margin 반영
            left   = max(0, bbox[0] - margin)
            upper  = max(0, bbox[1] - margin)
            right  = min(img.width, bbox[2] + margin)
            lower  = min(img.height, bbox[3] + margin)
            cropped = img.crop((left, upper, right, lower))
            cropped.save(filepath, "PNG")

def custom_draw(vertices_dict, right_v, side_labels, filename,
                vertex_label_rotations=None, gap_factor=1.15, highlight_angle=None, **kwargs):
    
    pts = {k: np.array(v, dtype=float) for k, v in vertices_dict.items()}
    centroid = (pts['A'] + pts['B'] + pts['C']) / 3.0

    labeled_lens = [
        np.linalg.norm(pts[v1] - pts[v2])
        for v1, v2 in [('A','B'), ('B','C'), ('C','A')]
        if side_labels.get(v1+v2) or side_labels.get(v2+v1)
    ]
    L_min = min(labeled_lens) if labeled_lens else 1.0

    def custom_sfrac(L):
        if abs(L - L_min) < 1e-5:
            return 0.33
        return float(np.clip(0.28 * (L_min / L) ** 0.3, 0.12, 0.28))

    old_bracket_arc = mod.bracket_arc

    arcs = []
    all_arc_pts = []
    for v1, v2 in [('A','B'), ('B','C'), ('C','A')]:
        lbl = side_labels.get(v1+v2) or side_labels.get(v2+v1)
        if not lbl: continue
        L   = np.linalg.norm(pts[v1] - pts[v2])
        ap, peak = old_bracket_arc(pts[v1], pts[v2], centroid, custom_sfrac(L))
        arcs.append((v1, v2, lbl, ap, peak))
        all_arc_pts.extend(ap.tolist())

    extra = dict(kwargs)
    slo = extra.get('side_label_offsets', {}).copy()
    if 'BC' in side_labels:
        slo['BC'] = (0.0, -0.05 * L_min)
    extra['side_label_offsets'] = slo

    filepath = os.path.join(SAMPLE_DIR, filename)

    mod.draw(
        vertices_dict,
        right_v=right_v,
        side_labels=side_labels,
        filename=filename,
        vertex_label_rotations=vertex_label_rotations,
        gap_factor=gap_factor,
        highlight_angle=highlight_angle,
        **extra
    )

    # 렌더링 직후 투명 여백 수치 정밀 컷팅 (Auto-crop)
    crop_transparent_padding(filepath, margin=12)

# 샘플 세트
samples = [
    # (id, tmpl, p, q, p_lbl, q_lbl, h_lbl, target_a, filename)
    ('T001', 1, 1, 2, '$1$', '$2$', '$\\sqrt{3}$', 'A', 'tri_T001_1a_A_cropped.png'),
    ('T012', 1, 7, 24, '$7$', '$24$', '$25$', 'A', 'tri_T012_1a_A_cropped.png'),
    ('T024', 1, 1, 4, '$1$', '$4$', '$\\sqrt{17}$', 'A', 'tri_T024_1a_A_cropped.png'),
    ('T024', 2, 1, 4, '$1$', '$4$', '$\\sqrt{17}$', 'B', 'tri_T024_2a_B_cropped.png'),
]

for tid, tmpl, p, q, p_lbl, q_lbl, h_lbl, target_a, fname in samples:
    if tmpl == 1:
        verts = {'A': (0, q), 'B': (0, 0), 'C': (p, 0)}
        rv = 'B'
        rot = {'A': -10}
        slabels = {'AB': q_lbl, 'BC': p_lbl, 'CA': h_lbl}
        extra_opts = {'side_gap_factors': {'CA': 1.6}}
    else:
        verts = {'A': (p, q), 'B': (0, 0), 'C': (p, 0)}
        rv = 'C'
        rot = {'A': 10}
        slabels = {'AB': h_lbl, 'BC': p_lbl, 'CA': q_lbl}
        extra_opts = {'side_gap_factors': {'AB': 1.6}}

    custom_draw(
        verts,
        right_v=rv,
        side_labels=slabels,
        filename=fname,
        vertex_label_rotations=rot,
        gap_factor=1.15,
        highlight_angle=target_a,
        **extra_opts
    )

print("Generated 4 auto-cropped sample images in sample001/")
