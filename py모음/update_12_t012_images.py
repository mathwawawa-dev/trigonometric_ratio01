# -*- coding: utf-8 -*-
"""
update_12_t012_images.py — Tri_img_01, Tri_img_02, Tri_img_03 내 T012 1a/2a 12개 이미지 0.05 거리 추가 로직 적용 재생성
"""
import os, math, importlib.util
import numpy as np

PY_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT   = os.path.dirname(PY_DIR)

_base_script = os.path.join(PY_DIR, 'v1.0.5_260809_0010_dash_trim3.py')
spec = importlib.util.spec_from_file_location('tri_draw', _base_script)
mod  = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

def custom_draw(out_dir, vertices_dict, right_v, side_labels, filename,
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
        slo['BC'] = (0.0, -0.35)   # -0.05 * 7
    extra['side_label_offsets'] = slo

    mod.OUTPUT_DIR = out_dir
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

items = [
    (1, 'A', '1a_A.png'),
    (1, 'C', '1a_C.png'),
    (2, 'A', '2a_A.png'),
    (2, 'B', '2a_B.png'),
]

p_lbl, q_lbl, h_lbl = '$7$', '$24$', '$25$'
p, q = 7, 24

types_info = [
    ('Tri_img_01', 'tri_', {
        1: ({'AB': q_lbl, 'BC': p_lbl, 'CA': h_lbl}, {'side_gap_factors': {'CA': 1.6}}),
        2: ({'AB': h_lbl, 'BC': p_lbl, 'CA': q_lbl}, {'side_gap_factors': {'AB': 1.6}}),
    }),
    ('Tri_img_02', 'tri2_', {
        1: ({'AB': q_lbl, 'BC': p_lbl}, {}),
        2: ({'BC': p_lbl, 'CA': q_lbl}, {}),
    }),
    ('Tri_img_03', 'tri3_', {
        1: ({'BC': p_lbl, 'CA': h_lbl}, {'side_gap_factors': {'CA': 1.6}}),
        2: ({'AB': h_lbl, 'BC': p_lbl}, {'side_gap_factors': {'AB': 1.6}}),
    }),
]

total_count = 0
for folder_name, prefix, tmpl_map in types_info:
    out_dir = os.path.join(ROOT, folder_name)
    os.makedirs(out_dir, exist_ok=True)
    
    for tmpl, target_a, suffix in items:
        slabels, extra_opts = tmpl_map[tmpl]
        if tmpl == 1:
            verts = {'A': (0, q), 'B': (0, 0), 'C': (p, 0)}
            rv = 'B'
            rot = {'A': -10}
        else:
            verts = {'A': (p, q), 'B': (0, 0), 'C': (p, 0)}
            rv = 'C'
            rot = {'A': 10}
        
        fname = f"{prefix}T012_{suffix}"
        custom_draw(
            out_dir=out_dir,
            vertices_dict=verts,
            right_v=rv,
            side_labels=slabels,
            filename=fname,
            vertex_label_rotations=rot,
            gap_factor=1.15,
            highlight_angle=target_a,
            **extra_opts
        )
        total_count += 1
        print(f"[{total_count}/12] Created {folder_name}/{fname}")

print("All 12 T012 images updated successfully!")
