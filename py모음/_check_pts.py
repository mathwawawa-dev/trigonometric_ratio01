import os, sys, json, importlib.util, numpy as np

PY_DIR  = os.path.dirname(os.path.abspath(__file__))
ROOT    = os.path.dirname(PY_DIR)

with open(os.path.join(PY_DIR, 'v1.0.2_260808_1536_triangles4변경.py'), 'r', encoding='utf-8') as f:
    code = f.read()

OLD = (
    "        for seg, is_post_gap in segments:\n"
    "            pts_draw = seg[::-1] if is_post_gap else seg   # 갭 뒤는 역방향\n"
    "            ax.plot(pts_draw[:, 0], pts_draw[:, 1], **dash_kw)"
)

NEW = (
    "        _dash_on_du  = 4.5 * (span / (FIG_S * 72.0))\n"
    "        _dash_per_du = 7.5 * (span / (FIG_S * 72.0))\n"
    "        _thresh      = _dash_on_du * 0.36\n"
    "        for seg, is_post_gap in segments:\n"
    "            pts_draw = seg[::-1] if is_post_gap else seg\n"
    "            _diffs   = np.diff(pts_draw, axis=0)\n"
    "            _dist_du = np.concatenate(([0.0], np.cumsum(np.linalg.norm(_diffs, axis=1))))\n"
    "            _total   = float(_dist_du[-1])\n"
    "            print(f'Segment total={_total:.5f}, pts={len(pts_draw)}, is_post_gap={is_post_gap}')\n"
    "            \n"
    "            if _total <= _thresh:\n"
    "                continue\n"
    "            _R = _total % _dash_per_du\n"
    "            if 0.0 < _R <= _thresh:\n"
    "                pts_draw = pts_draw[_dist_du <= (_total - _R)]\n"
    "            if len(pts_draw) > 1:\n"
    "                ax.plot(pts_draw[:, 0], pts_draw[:, 1], **dash_kw)"
)

patched_code = code.replace(OLD, NEW)
with open(os.path.join(PY_DIR, '_dash_trim_module6.py'), 'w', encoding='utf-8') as f:
    f.write(patched_code)

sys.path.insert(0, PY_DIR)
with open(os.path.join(ROOT, 'data', 'triangle_data.json'), encoding='utf-8') as f:
    triangles = json.load(f)
tri_map = {t['id']: t for t in triangles}

spec = importlib.util.spec_from_file_location('trim6', os.path.join(PY_DIR, '_dash_trim_module6.py'))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
mod.OUTPUT_DIR = os.path.join(PY_DIR, 'tmp')
os.makedirs(mod.OUTPUT_DIR, exist_ok=True)

def make_orient(tmpl, p, q, p_lbl, q_lbl, h_lbl):
    if tmpl == 3:
        _off = -0.021 * min(p, q)**0.3 * p**0.7
        return ({'A': (0, 0), 'B': (p, q), 'C': (0, q)}, 'C',
                {'AB': h_lbl, 'BC': p_lbl, 'CA': q_lbl}, {'A': 12},
                {'side_label_offsets': {'BC': (0, _off)}, 'side_gap_factors': {'AB': 1.6}})

t = tri_map['T006']
# For 3b, let's assume leg2 and leg1 order based on previous script:
verts, rv, slabels, rot, extra = make_orient(3, t['leg2_val'], t['leg1_val'], t['leg2_label'], t['leg1_label'], t['hyp_label'])
mod.draw(verts, right_v=rv, side_labels=slabels, filename='tmp_t006_3b.png', gap_factor=1.15, **extra)
