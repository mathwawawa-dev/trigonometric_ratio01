"""
dash_trim_test.py
- v1.0.2_260808_1536_triangles4변경.py 를 읽어서
  segment 렌더링 부분에 "짧은 잔여 대시 제거" 패치를 삽입한 모듈을 생성하고,
  T007 / T006 / T001 의 샘플 이미지를 dash_test 폴더에 생성합니다.
"""

import os, sys, json, importlib.util, numpy as np

PY_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT   = os.path.dirname(PY_DIR)
OUT_DIR = os.path.join(ROOT, 'triangles4', 'dash_test')
os.makedirs(OUT_DIR, exist_ok=True)

# ── 원본 코드 읽기 ──────────────────────────────────────────────────────────
with open(os.path.join(PY_DIR, 'v1.0.2_260808_1536_triangles4변경.py'),
          'r', encoding='utf-8') as f:
    code = f.read()

# ── 교체할 원본 블록 ──────────────────────────────────────────────────────
OLD = (
    "        for seg, is_post_gap in segments:\n"
    "            pts_draw = seg[::-1] if is_post_gap else seg   # 갭 뒤는 역방향\n"
    "            ax.plot(pts_draw[:, 0], pts_draw[:, 1], **dash_kw)"
)

# ── 새 블록 (import numpy 없이 이미 임포트된 np 사용) ─────────────────────
NEW = (
    "        # ── dash trim: 잔여 stub < 1/3 dash_on 이면 제거 ──────────────\n"
    "        _dash_on_pt  = 6.0          # points\n"
    "        _dash_period = 6.0 + 4.0   # on + off  (dash_kw의 dashes와 동일)\n"
    "        _trim_thresh = _dash_on_pt / 3.0   # 2.0 pt 이하면 제거\n"
    "        _du2pt       = 72.0 * (FIG_S / span)  # data unit → pt\n"
    "\n"
    "        for seg, is_post_gap in segments:\n"
    "            pts_draw = seg[::-1] if is_post_gap else seg   # 갭 뒤는 역방향\n"
    "            _diffs      = np.diff(pts_draw, axis=0)\n"
    "            _step_dists = np.linalg.norm(_diffs, axis=1)\n"
    "            _dist_pt    = np.concatenate(([0.0], np.cumsum(_step_dists))) * _du2pt\n"
    "            _total_pt   = _dist_pt[-1]\n"
    "            _R          = _total_pt % _dash_period\n"
    "            if 0.0 < _R <= _trim_thresh:\n"
    "                _target = _total_pt - _R\n"
    "                pts_draw = pts_draw[_dist_pt <= _target]\n"
    "            if len(pts_draw) > 1:\n"
    "                ax.plot(pts_draw[:, 0], pts_draw[:, 1], **dash_kw)"
)

if OLD not in code:
    print("ERROR: 교체 대상 코드를 찾지 못했습니다.")
    sys.exit(1)

patched_code = code.replace(OLD, NEW)

# ── 패치 모듈 파일 저장 ─────────────────────────────────────────────────────
trim_module_path = os.path.join(PY_DIR, '_dash_trim_module.py')
with open(trim_module_path, 'w', encoding='utf-8') as f:
    f.write(patched_code)

# ── 모듈 동적 로드 ──────────────────────────────────────────────────────────
spec = importlib.util.spec_from_file_location('tri_dash_trim', trim_module_path)
mod  = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
mod.OUTPUT_DIR = OUT_DIR
draw = mod.draw

# ── 삼각형 데이터 로드 ──────────────────────────────────────────────────────
with open(os.path.join(ROOT, 'data', 'triangle_data.json'), encoding='utf-8') as f:
    triangles = json.load(f)

tri_map = {t['id']: t for t in triangles}

def make_orient(tmpl, p, q, p_lbl, q_lbl, h_lbl):
    import math
    if tmpl == 1:
        return (
            {'A': (0, q), 'B': (0, 0), 'C': (p, 0)}, 'B',
            {'AB': q_lbl, 'BC': p_lbl, 'CA': h_lbl},
            {'A': -10}, {'side_gap_factors': {'CA': 1.6}}
        )
    elif tmpl == 2:
        return (
            {'A': (p, q), 'B': (0, 0), 'C': (p, 0)}, 'C',
            {'AB': h_lbl, 'BC': p_lbl, 'CA': q_lbl},
            {'A': 10}, {'side_gap_factors': {'AB': 1.6}}
        )
    elif tmpl == 3:
        _off3 = -0.021 * min(p, q) ** 0.3 * p ** 0.7
        return (
            {'A': (0, 0), 'B': (p, q), 'C': (0, q)}, 'C',
            {'AB': h_lbl, 'BC': p_lbl, 'CA': q_lbl},
            {'A': 12},
            {'side_label_offsets': {'BC': (0, _off3)}, 'side_gap_factors': {'AB': 1.6}}
        )
    elif tmpl == 4:
        _off4 = -0.021 * min(p, q) ** 0.3 * p ** 0.7
        return (
            {'A': (p, 0), 'B': (p, q), 'C': (0, q)}, 'B',
            {'AB': q_lbl, 'BC': p_lbl, 'CA': h_lbl},
            {'A': -12},
            {'side_label_offsets': {'BC': (0, _off4)}, 'side_gap_factors': {'CA': 1.6}}
        )

# ── 샘플 생성 (T007_1b, T007_3b, T006_3b, T001_1b) ─────────────────────────
samples = [
    ('T007', 1, 'b'),
    ('T007', 3, 'b'),
    ('T006', 3, 'b'),
    ('T001', 1, 'b'),
]

for tid, tmpl, var in samples:
    t = tri_map[tid]
    l1v, l2v = t['leg1_val'], t['leg2_val']
    hlb = t['hyp_label']
    if var == 'b':
        p, q, p_lbl, q_lbl = l2v, l1v, t['leg2_label'], t['leg1_label']
    else:
        p, q, p_lbl, q_lbl = l1v, l2v, t['leg1_label'], t['leg2_label']
    
    verts, rv, slabels, rot, extra = make_orient(tmpl, p, q, p_lbl, q_lbl, hlb)
    fname = f"tri_{tid}_{tmpl}{var}_trimmed.png"
    draw(verts, right_v=rv, side_labels=slabels, filename=fname,
         vertex_label_rotations=rot, gap_factor=1.15, **extra)
    print(f"Saved: {fname}")

print("\nDone")
