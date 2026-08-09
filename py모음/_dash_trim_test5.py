import os, sys, json, importlib.util, numpy as np
import matplotlib.pyplot as plt

PY_DIR  = os.path.dirname(os.path.abspath(__file__))
ROOT    = os.path.dirname(PY_DIR)
OUT_DIR = os.path.join(ROOT, 'triangles4', 'dash_test5')
os.makedirs(OUT_DIR, exist_ok=True)

with open(os.path.join(PY_DIR, 'v1.0.2_260808_1536_triangles4변경.py'), 'r', encoding='utf-8') as f:
    code = f.read()

OLD = (
    "        for seg, is_post_gap in segments:\n"
    "            pts_draw = seg[::-1] if is_post_gap else seg   # 갭 뒤는 역방향\n"
    "            ax.plot(pts_draw[:, 0], pts_draw[:, 1], **dash_kw)"
)

NEW = (
    "        # 정확한 Data 단위당 Point 계산\n"
    "        p0 = ax.transData.transform((0, 0))\n"
    "        p1 = ax.transData.transform((1, 0))\n"
    "        pts_per_du = np.linalg.norm(p1 - p0)\n"
    "        _dash_on_du  = 4.5 / pts_per_du\n"
    "        _dash_per_du = 7.5 / pts_per_du\n"
    "        _thresh      = _dash_on_du * 0.36\n"
    "\n"
    "        for seg, is_post_gap in segments:\n"
    "            pts_draw = seg[::-1] if is_post_gap else seg\n"
    "            _diffs   = np.diff(pts_draw, axis=0)\n"
    "            _dist_du = np.concatenate(([0.0], np.cumsum(np.linalg.norm(_diffs, axis=1))))\n"
    "            _total   = float(_dist_du[-1])\n"
    "            \n"
    "            if _total <= _thresh:\n"
    "                continue\n"
    "            \n"
    "            _R = _total % _dash_per_du\n"
    "            if 0.0 < _R <= _thresh:\n"
    "                pts_draw = pts_draw[_dist_du <= (_total - _R)]\n"
    "            elif _thresh < _R < _dash_on_du:\n"
    "                pass\n"
    "            \n"
    "            print(f'is_post_gap={is_post_gap}, _total={_total:.5f}, _R={_R:.5f}, dash_on={_dash_on_du:.5f}, R/dash_on={_R/_dash_on_du:.2f}')\n"
    "            \n"
    "            if len(pts_draw) > 1:\n"
    "                ax.plot(pts_draw[:, 0], pts_draw[:, 1], **dash_kw)"
)

patched_code = code.replace(OLD, NEW)

trim_module_path = os.path.join(PY_DIR, '_dash_trim_module5.py')
with open(trim_module_path, 'w', encoding='utf-8') as f:
    f.write(patched_code)

spec = importlib.util.spec_from_file_location('tri_dash_trim5', trim_module_path)
mod  = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
mod.OUTPUT_DIR = OUT_DIR
draw = mod.draw

def make_orient(tmpl, p, q, p_lbl, q_lbl, h_lbl):
    _off3 = -0.021 * min(p, q) ** 0.3 * p ** 0.7
    return (
        {'A': (0, 0), 'B': (p, q), 'C': (0, q)},
        'C',
        {'AB': h_lbl, 'BC': p_lbl, 'CA': q_lbl},
        {'A': 12},
        {'side_label_offsets': {'BC': (0, _off3)}, 'side_gap_factors': {'AB': 1.6}}
    )

with open(os.path.join(ROOT, 'data', 'triangle_data.json'), encoding='utf-8') as f:
    triangles = json.load(f)
tri_map = {t['id']: t for t in triangles}

t = tri_map['T006']
l1v, l2v = t['leg1_val'], t['leg2_val']
# 'b' variant: p=l2v, q=l1v
p, q = l2v, l1v
p_lbl, q_lbl = t['leg2_label'], t['leg1_label']
hlb = t['hyp_label']

verts, rv, slabels, rot, extra = make_orient(3, p, q, p_lbl, q_lbl, hlb)
fname = f"tri_T006_3b_trim5.png"
print(f"--- Generating {fname} ---")
draw(verts, right_v=rv, side_labels=slabels, filename=fname, vertex_label_rotations=rot, gap_factor=1.15, **extra)
print(f"Saved: {fname}")

print("\nDone")
