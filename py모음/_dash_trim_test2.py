"""
_dash_trim_test2.py
- dashes=(4.5, 3.0) 임을 반영한 올바른 stub 제거 로직
- data unit 기준으로 dash 주기를 계산하여 threshold를 적용
- dash_test2 폴더에 샘플 생성
"""

import os, sys, json, importlib.util, numpy as np

PY_DIR  = os.path.dirname(os.path.abspath(__file__))
ROOT    = os.path.dirname(PY_DIR)
OUT_DIR = os.path.join(ROOT, 'triangles4', 'dash_test2')
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

# ── 새 블록 ──────────────────────────────────────────────────────────────────
# dash 주기를 data unit으로 역산:
#   _px2du = span / (FIG_S * 100.0)  ← 100 DPI 기준 (코드 기존 공식)
#   dashes=(4.5, 3.0) → 단위: pt
#   pt → data unit: 1pt = 1/72 inch, 1 inch = FIG_S/span data_unit
#   dash_on_du = 4.5/72 * (span/FIG_S)
# 그런데 실제로는 matplotlib이 path length를 display point로 계산하므로
# du → pt 변환: pt = du * 72 * (FIG_S / span)
# 단, 그림에서 축이 전체 figure를 다 채우지 않을 수 있으므로
# 실제 scale은 axes 크기에 따라 다름.
# → 가장 안전한 방법: 같은 _px2du 공식으로 pt ↔ du 변환
#   1px @100DPI = 1/100 inch = 72/100 pt = 0.72 pt
#   dash_on_pt = 4.5 pt = 4.5/0.72 px @100DPI = 6.25 px
#   dash_on_du = 6.25 * _px2du = 6.25 * span/(FIG_S*100)
# threshold (1/3) = dash_on_du / 3

NEW = (
    "        # ── dash trim: 갭 경계의 잔여 stub이 1/3 이하면 제거 ──────────\n"
    "        _dash_on_pt  = 4.5   # dashes=(4.5, 3.0)의 on 길이 (pt)\n"
    "        _dash_off_pt = 3.0\n"
    "        _dash_per_pt = _dash_on_pt + _dash_off_pt  # 7.5 pt\n"
    "        # pt → data unit:  1pt = (span / (FIG_S * 72)) du\n"
    "        _pt2du       = span / (FIG_S * 72.0)\n"
    "        _dash_on_du  = _dash_on_pt  * _pt2du\n"
    "        _dash_per_du = _dash_per_pt * _pt2du\n"
    "        _trim_thresh = _dash_on_du / 3.0   # 1/3 미만 stub 제거\n"
    "\n"
    "        for seg, is_post_gap in segments:\n"
    "            pts_draw = seg[::-1] if is_post_gap else seg   # 갭 뒤는 역방향\n"
    "            # 누적 arc 길이 (data unit)\n"
    "            _diffs      = np.diff(pts_draw, axis=0)\n"
    "            _step_du    = np.linalg.norm(_diffs, axis=1)\n"
    "            _dist_du    = np.concatenate(([0.0], np.cumsum(_step_du)))\n"
    "            _total_du   = float(_dist_du[-1])\n"
    "            _R_du       = _total_du % _dash_per_du  # 마지막 잔여 길이\n"
    "            if 0.0 < _R_du <= _trim_thresh:\n"
    "                # 잔여 stub 제거: 해당 길이만큼 끝을 잘라냄\n"
    "                _keep = _dist_du <= (_total_du - _R_du)\n"
    "                pts_draw = pts_draw[_keep]\n"
    "            if len(pts_draw) > 1:\n"
    "                ax.plot(pts_draw[:, 0], pts_draw[:, 1], **dash_kw)"
)

if OLD not in code:
    print("ERROR: 교체 대상 코드를 찾지 못했습니다.")
    sys.exit(1)

patched_code = code.replace(OLD, NEW)

# ── 패치 모듈 파일 저장 ─────────────────────────────────────────────────────
trim_module_path = os.path.join(PY_DIR, '_dash_trim_module2.py')
with open(trim_module_path, 'w', encoding='utf-8') as f:
    f.write(patched_code)

# ── 모듈 동적 로드 ──────────────────────────────────────────────────────────
spec = importlib.util.spec_from_file_location('tri_dash_trim2', trim_module_path)
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

# ── 샘플 생성 ────────────────────────────────────────────────────────────────
samples = [
    ('T007', 1, 'b'),  # 원래 문제 이미지
    ('T007', 3, 'b'),
    ('T006', 3, 'b'),  # √3 포함
    ('T001', 1, 'b'),  # 단순 정수
    ('T024', 1, 'b'),  # 큰 삼각형
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
    fname = f"tri_{tid}_{tmpl}{var}_trim2.png"
    draw(verts, right_v=rv, side_labels=slabels, filename=fname,
         vertex_label_rotations=rot, gap_factor=1.15, **extra)
    print(f"Saved: {fname}")

print("\nDone")
