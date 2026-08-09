import os, sys, json, importlib.util, numpy as np

PY_DIR  = os.path.dirname(os.path.abspath(__file__))
ROOT    = os.path.dirname(PY_DIR)
OUT_DIR = os.path.join(ROOT, 'triangles4', 'dash_test4')
os.makedirs(OUT_DIR, exist_ok=True)

with open(os.path.join(PY_DIR, 'v1.0.2_260808_1536_triangles4변경.py'), 'r', encoding='utf-8') as f:
    code = f.read()

OLD = (
    "        for seg, is_post_gap in segments:\n"
    "            pts_draw = seg[::-1] if is_post_gap else seg   # 갭 뒤는 역방향\n"
    "            ax.plot(pts_draw[:, 0], pts_draw[:, 1], **dash_kw)"
)

# ── 핵심 수정: trailing + leading stub 둘 다 처리 ─────────────────────────
NEW = (
    "        # ── dash stub trim (threshold=0.36) ─────────────────────────────\n"
    "        # trailing stub: 세그먼트 끝(갭 경계)의 짧은 잔여 dash\n"
    "        # leading  stub: 세그먼트 자체가 매우 짧아 첫 dash도 완성 못하는 경우\n"
    "        _dash_on_du  = 4.5 * (span / (FIG_S * 72.0))\n"
    "        _dash_per_du = 7.5 * (span / (FIG_S * 72.0))\n"
    "        _thresh      = _dash_on_du * 0.36\n"
    "\n"
    "        for seg, is_post_gap in segments:\n"
    "            pts_draw = seg[::-1] if is_post_gap else seg\n"
    "            _diffs   = np.diff(pts_draw, axis=0)\n"
    "            _dist_du = np.concatenate(([0.0], np.cumsum(np.linalg.norm(_diffs, axis=1))))\n"
    "            _total   = float(_dist_du[-1])\n"
    "            if _total <= _thresh:\n"
    "                # leading stub: 세그먼트 전체가 기준 이하 → 통째로 제거\n"
    "                continue\n"
    "            _R = _total % _dash_per_du\n"
    "            if 0.0 < _R <= _thresh:\n"
    "                # trailing stub: 끝부분만 잘라냄\n"
    "                pts_draw = pts_draw[_dist_du <= (_total - _R)]\n"
    "            if len(pts_draw) > 1:\n"
    "                ax.plot(pts_draw[:, 0], pts_draw[:, 1], **dash_kw)"
)

if OLD not in code:
    print("ERROR: 교체 대상 코드를 찾지 못했습니다."); sys.exit(1)

patched_code = code.replace(OLD, NEW)

trim_module_path = os.path.join(PY_DIR, '_dash_trim_module4.py')
with open(trim_module_path, 'w', encoding='utf-8') as f:
    f.write(patched_code)

spec = importlib.util.spec_from_file_location('tri_dash_trim4', trim_module_path)
mod  = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
mod.OUTPUT_DIR = OUT_DIR
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

samples = [('T007', 1, 'b'), ('T007', 3, 'b'), ('T006', 3, 'b'), ('T001', 1, 'b'), ('T024', 1, 'b')]

for tid, tmpl, var in samples:
    t = tri_map[tid]
    l1v, l2v = t['leg1_val'], t['leg2_val']
    hlb = t['hyp_label']
    p, q, p_lbl, q_lbl = (l2v, l1v, t['leg2_label'], t['leg1_label']) if var == 'b' else (l1v, l2v, t['leg1_label'], t['leg2_label'])
    verts, rv, slabels, rot, extra = make_orient(tmpl, p, q, p_lbl, q_lbl, hlb)
    fname = f"tri_{tid}_{tmpl}{var}_trim4.png"
    draw(verts, right_v=rv, side_labels=slabels, filename=fname,
         vertex_label_rotations=rot, gap_factor=1.15, **extra)
    print(f"Saved: {fname}")

print("\nDone")
