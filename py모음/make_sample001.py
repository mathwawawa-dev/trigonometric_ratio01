# -*- coding: utf-8 -*-
import json, math, os, sys, importlib.util
import numpy as np

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

# Custom draw wrapper that increases shortest side (BC) arc distance from side
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
        # 가장 짧은 변(L_min)인 경우 sagitta_frac를 기존 0.28에서 2단위 확대 -> 0.48~0.50으로 적용
        if abs(L - L_min) < 1e-5:
            return 0.48
        return float(np.clip(0.28 * (L_min / L) ** 0.3, 0.12, 0.28))

    # monkey patch adaptive_sfrac in mod during draw
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

    # Call original draw with side_label_offsets for BC
    extra = dict(kwargs)
    slo = extra.get('side_label_offsets', {}).copy()
    slo['BC'] = (0.0, -0.22)
    extra['side_label_offsets'] = slo

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

def make_orient(tmpl, p, q, p_lbl, q_lbl, h_lbl):
    if tmpl == 1:
        return (
            {'A': (0, q), 'B': (0, 0), 'C': (p, 0)},
            'B',
            {'AB': q_lbl, 'BC': p_lbl, 'CA': h_lbl},
            {'A': -10},
            {'side_gap_factors': {'CA': 1.6}}
        )
    elif tmpl == 2:
        return (
            {'A': (p, q), 'B': (0, 0), 'C': (p, 0)},
            'C',
            {'AB': h_lbl, 'BC': p_lbl, 'CA': q_lbl},
            {'A': 10},
            {'side_gap_factors': {'AB': 1.6}}
        )

# T024 data
p = 1
q = 4
p_lbl = '$1$'
q_lbl = '$4$'
h_lbl = '$\\sqrt{17}$'

targets = [
    (1, 'A', 'tri_T024_1a_A.png'),
    (1, 'C', 'tri_T024_1a_C.png'),
    (2, 'A', 'tri_T024_2a_A.png'),
    (2, 'B', 'tri_T024_2a_B.png'),
]

for tmpl, target_a, fname in targets:
    verts, rv, slabels, rot, extra = make_orient(tmpl, p, q, p_lbl, q_lbl, h_lbl)
    custom_draw(
        verts,
        right_v=rv,
        side_labels=slabels,
        filename=fname,
        vertex_label_rotations=rot,
        gap_factor=1.15,
        highlight_angle=target_a,
        **extra
    )

print("Generated 4 enhanced sample images in sample001/")
