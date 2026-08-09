import os, json, importlib.util
from step1_2_edited05 import make_orient

PY_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(PY_DIR)
OUT_DIR = os.path.join(ROOT, 'triangles4', 'dash_test')

spec = importlib.util.spec_from_file_location('tri_draw', os.path.join(PY_DIR, '_test_dash_trim_module.py'))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
mod.OUTPUT_DIR = OUT_DIR
draw = mod.draw

with open(os.path.join(ROOT, 'data', 'triangle_data.json'), encoding='utf-8') as f:
    triangles = json.load(f)

for t in triangles:
    if t['id'] == 'T007':
        p, q = t['leg2_val'], t['leg1_val']
        p_lbl, q_lbl = t['leg2_label'], t['leg1_label']
        hlb = t['hyp_label']
        verts, rv, slabels, rot, extra = make_orient(3, p, q, p_lbl, q_lbl, hlb)
        draw(verts, right_v=rv, side_labels=slabels, filename='tri_T007_3b_trimmed.png', vertex_label_rotations=rot, gap_factor=1.15, **extra)
        print('Saved: tri_T007_3b_trimmed.png')
        break
