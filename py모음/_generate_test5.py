import json, math, os, sys, importlib.util, time

PY_DIR   = os.path.dirname(os.path.abspath(__file__))
ROOT     = os.path.dirname(PY_DIR)
TYPE1_DIR = os.path.join(ROOT, 'triangles4', 'dash_test5')
os.makedirs(TYPE1_DIR, exist_ok=True)

_base_script = os.path.join(PY_DIR, '_dash_trim_module5.py')
spec = importlib.util.spec_from_file_location('tri_draw', _base_script)
mod  = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
mod.OUTPUT_DIR = TYPE1_DIR
draw = mod.draw

with open(os.path.join(ROOT, 'data', 'triangle_data.json'), encoding='utf-8') as f:
    triangles = json.load(f)
tri_map = {t['id']: t for t in triangles}

def make_orient(tmpl, p, q, p_lbl, q_lbl, h_lbl):
    if tmpl == 1:
        return ({'A': (0, q), 'B': (0, 0), 'C': (p, 0)}, 'B',
                {'AB': q_lbl, 'BC': p_lbl, 'CA': h_lbl}, {'A': -10},
                {'side_gap_factors': {'CA': 1.6}})
    elif tmpl == 2:
        return ({'A': (p, q), 'B': (0, 0), 'C': (p, 0)}, 'C',
                {'AB': h_lbl, 'BC': p_lbl, 'CA': q_lbl}, {'A': 10},
                {'side_gap_factors': {'AB': 1.6}})
    elif tmpl == 3:
        _off = -0.021 * min(p, q)**0.3 * p**0.7
        return ({'A': (0, 0), 'B': (p, q), 'C': (0, q)}, 'C',
                {'AB': h_lbl, 'BC': p_lbl, 'CA': q_lbl}, {'A': 12},
                {'side_label_offsets': {'BC': (0, _off)}, 'side_gap_factors': {'AB': 1.6}})
    elif tmpl == 4:
        _off = -0.021 * min(p, q)**0.3 * p**0.7
        return ({'A': (p, 0), 'B': (p, q), 'C': (0, q)}, 'B',
                {'AB': q_lbl, 'BC': p_lbl, 'CA': h_lbl}, {'A': -12},
                {'side_label_offsets': {'BC': (0, _off)}, 'side_gap_factors': {'CA': 1.6}})

samples = [
    ('T006', 3, 'b'),
    ('T007', 1, 'b'),
    ('T004', 3, 'a'),
    ('T005', 1, 'a'),
]

for tid, tmpl, var in samples:
    t = tri_map[tid]
    l1v, l2v = t['leg1_val'], t['leg2_val']
    hlb = t['hyp_label']
    p, q, p_lbl, q_lbl = (l2v, l1v, t['leg2_label'], t['leg1_label']) if var == 'b' else (l1v, l2v, t['leg1_label'], t['leg2_label'])
    verts, rv, slabels, rot, extra = make_orient(tmpl, p, q, p_lbl, q_lbl, hlb)
    fname = f"tri_{tid}_{tmpl}{var}_trim5.png"
    print(f"--- Generating {fname} ---")
    draw(verts, right_v=rv, side_labels=slabels, filename=fname, vertex_label_rotations=rot, gap_factor=1.15, **extra)
    print(f"Saved: {fname}")

print("완료")
