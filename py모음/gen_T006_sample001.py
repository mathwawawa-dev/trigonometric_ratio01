# -*- coding: utf-8 -*-
"""
T006 계열 이미지 수정 샘플 생성
수정: case3 CLR_TABLE L/R 여백 축소 → A 꼭짓점 쪽 점선 일부 살아남도록
출력: sample001/ 폴더에 tri2_T006_*_*.png 48개 생성
"""

import json, math, os, sys, importlib.util, time

PY_DIR   = os.path.dirname(os.path.abspath(__file__))
ROOT     = os.path.dirname(PY_DIR)
SAMPLE_DIR = os.path.join(PY_DIR, 'sample001')
os.makedirs(SAMPLE_DIR, exist_ok=True)

_base_script = os.path.join(PY_DIR, 'v1.0.5_260809_0010_dash_trim3.py')
spec = importlib.util.spec_from_file_location('tri_draw', _base_script)
mod  = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
mod.OUTPUT_DIR = SAMPLE_DIR
draw = mod.draw

# CLR_TABLE case3 여백 축소: L=16.5->8, R=20.5->10, T=19.5->14, B=12->8
mod._CLR_TABLE[3] = dict(L=8, R=10, T=14, B=8)

with open(os.path.join(ROOT, 'data', 'triangle_data.json'), encoding='utf-8') as f:
    triangles = json.load(f)
tri_map = {t['id']: t for t in triangles}

t006 = tri_map['T006']
l1v, l2v = t006['leg1_val'], t006['leg2_val']
l1lb, l2lb = t006['leg1_label'], t006['leg2_label']

def make_orient_type2(tmpl, p, q, p_lbl, q_lbl):
    c = math.hypot(p, q)
    if tmpl == 1:
        return ({'A': (0, q), 'B': (0, 0), 'C': (p, 0)}, 'B', {'AB': q_lbl, 'BC': p_lbl}, {'A': -10}, {})
    elif tmpl == 2:
        return ({'A': (p, q), 'B': (0, 0), 'C': (p, 0)}, 'C', {'BC': p_lbl, 'CA': q_lbl}, {'A': 10}, {})
    elif tmpl == 3:
        _off3 = -0.021 * min(p, q) ** 0.3 * p ** 0.7
        return ({'A': (0, 0), 'B': (p, q), 'C': (0, q)}, 'C', {'BC': p_lbl, 'CA': q_lbl}, {'A': 12}, {'side_label_offsets': {'BC': (0, _off3)}})
    elif tmpl == 4:
        _off4 = -0.021 * min(p, q) ** 0.3 * p ** 0.7
        return ({'A': (p, 0), 'B': (p, q), 'C': (0, q)}, 'B', {'AB': q_lbl, 'BC': p_lbl}, {'A': -12}, {'side_label_offsets': {'BC': (0, _off4)}})
    elif tmpl == 5:
        return ({'B': (0.0, 0.0), 'C': (c, 0.0), 'A': (p**2 / c, p * q / c)}, 'A', {'AB': p_lbl, 'AC': q_lbl}, {'A': 0}, {'vertex_label_vectors': {'A': (0, 1)}})
    elif tmpl == 6:
        return ({'B': (0.0, 0.0), 'C': (c, 0.0), 'A': (q**2 / c, p * q / c)}, 'A', {'AB': q_lbl, 'AC': p_lbl}, {'A': 0}, {'vertex_label_vectors': {'A': (0, 1)}})

count = 0
t_start = time.time()
variants = [('a', l1v, l2v, l1lb, l2lb), ('b', l2v, l1v, l2lb, l1lb)]

for var, p, q, p_lbl, q_lbl in variants:
    for tmpl in [1, 2, 3, 4, 5, 6]:
        verts, rv, slabels, rot, extra = make_orient_type2(tmpl, p, q, p_lbl, q_lbl)
        target_angles = [k for k in verts.keys() if k != rv]
        for target_a in target_angles:
            fname = f"tri2_T006_{tmpl}{var}_{target_a}.png"
            draw(verts, right_v=rv, side_labels=slabels, filename=fname,
                 vertex_label_rotations=rot, gap_factor=1.15, highlight_angle=target_a, **extra)
            count += 1
            print(f"  [{count:3d}] {fname}  ({time.time()-t_start:.1f}s)")

print(f"\n✅ {count}개 → sample001/")
