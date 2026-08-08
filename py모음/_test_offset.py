import json, math, os, sys, importlib.util

PY_DIR   = os.path.dirname(os.path.abspath(__file__))
ROOT     = os.path.dirname(PY_DIR)
OUT_DIR  = os.path.join(ROOT, 'triangles4', 'offset_test')
os.makedirs(OUT_DIR, exist_ok=True)

# draw 함수 로드
_base_script = os.path.join(PY_DIR, 'v1.0.2_260808_1536_triangles4변경.py')
spec = importlib.util.spec_from_file_location('tri_draw', _base_script)
mod  = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
mod.OUTPUT_DIR = OUT_DIR
draw = mod.draw

with open(os.path.join(ROOT, 'data', 'triangle_data.json'), encoding='utf-8') as f:
    triangles = json.load(f)

# 테스트할 대표 삼각형들
# T001 (단순 정수), T006 (sqrt 포함), T024 (긴 변)
test_ids = ['T001', 'T006', 'T024']
test_tris = [t for t in triangles if t['id'] in test_ids]

def make_orient_test(tmpl, p, q, p_lbl, q_lbl, h_lbl, offset_mult):
    if tmpl == 3:
        _off3 = offset_mult * min(p, q) ** 0.3 * p ** 0.7
        return (
            {'A': (0, 0), 'B': (p, q), 'C': (0, q)}, 'C',
            {'AB': h_lbl, 'BC': p_lbl, 'CA': q_lbl},
            {'A': 12},
            {'side_label_offsets': {'BC': (0, _off3)}, 'side_gap_factors': {'AB': 1.6}}
        )
    elif tmpl == 4:
        _off4 = offset_mult * min(p, q) ** 0.3 * p ** 0.7
        return (
            {'A': (p, 0), 'B': (p, q), 'C': (0, q)}, 'B',
            {'AB': q_lbl, 'BC': p_lbl, 'CA': h_lbl},
            {'A': -12},
            {'side_label_offsets': {'BC': (0, _off4)}, 'side_gap_factors': {'CA': 1.6}}
        )

# offset_mult: -0.042 (기존), -0.021 (절반), 0.0 (없음)
for t in test_tris:
    l1v = t['leg1_val']
    l2v = t['leg2_val']
    hlb = t['hyp_label']
    # variant 'b' (l2v가 p) 사용 (T006_3b와 동일한 조건)
    p, q = l2v, l1v
    p_lbl, q_lbl = t['leg2_label'], t['leg1_label']
    
    for mult, name in [(-0.042, 'origin'), (-0.021, 'half'), (0.0, 'none')]:
        # tmpl 3
        verts, rv, slabels, rot, extra = make_orient_test(3, p, q, p_lbl, q_lbl, hlb, mult)
        fname = f"tri_{t['id']}_3b_{name}.png"
        draw(verts, right_v=rv, side_labels=slabels, filename=fname, vertex_label_rotations=rot, gap_factor=1.15, **extra)

print('Done')
