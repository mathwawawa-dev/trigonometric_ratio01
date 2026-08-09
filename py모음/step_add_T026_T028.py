# -*- coding: utf-8 -*-
"""
STEP ADD: T026/T027/T028 증분 이미지 생성 (세 유형 × 세 폴더)
================================================================
triangle_data.json 의 T026, T027, T028 만 처리하여 기존 이미지에 추가합니다.
각 메타데이터 JSON 에도 append 합니다.

T026: 1, 2, sqrt(5)       - 정수 일반형
T027: 4, 8, 4*sqrt(5)     - 정수 일반형
T028: sqrt(3), sqrt(6), 3 - 무리수 변 포함
"""

import json, math, os, sys, importlib.util, time

# ── 경로 설정 ─────────────────────────────────────────────────────────────────
PY_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT   = os.path.dirname(PY_DIR)

DIR1 = os.path.join(ROOT, 'Tri_img_01')
DIR2 = os.path.join(ROOT, 'Tri_img_02')
DIR3 = os.path.join(ROOT, 'Tri_img_03')
for d in [DIR1, DIR2, DIR3]:
    os.makedirs(d, exist_ok=True)

# ── draw() 모듈 로드 ──────────────────────────────────────────────────────────
_base_script = os.path.join(PY_DIR, 'v1.0.5_260809_0010_dash_trim3.py')
spec = importlib.util.spec_from_file_location('tri_draw', _base_script)
mod  = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
draw = mod.draw

# ── 삼각형 데이터 로드 및 필터 ────────────────────────────────────────────────
with open(os.path.join(ROOT, 'data', 'triangle_data.json'), encoding='utf-8') as f:
    all_triangles = json.load(f)

NEW_IDS = {'T026', 'T027', 'T028'}
triangles = [t for t in all_triangles if t['id'] in NEW_IDS]
print(f"대상 삼각형: {[t['id'] for t in triangles]}")

# ── 템플릿 팩토리 ─────────────────────────────────────────────────────────────

def make_orient_type1(tmpl, p, q, p_lbl, q_lbl, h_lbl):
    """유형 ①: 세 변 모두 표기"""
    c = math.hypot(p, q)
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
    elif tmpl == 5:
        return (
            {'B': (0.0, 0.0), 'C': (c, 0.0), 'A': (p**2 / c, p * q / c)}, 'A',
            {'AB': p_lbl, 'AC': q_lbl, 'BC': h_lbl},
            {'A': 0},
            {'side_gap_factors': {'BC': 1.6}, 'vertex_label_vectors': {'A': (0, 1)}}
        )
    elif tmpl == 6:
        return (
            {'B': (0.0, 0.0), 'C': (c, 0.0), 'A': (q**2 / c, p * q / c)}, 'A',
            {'AB': q_lbl, 'AC': p_lbl, 'BC': h_lbl},
            {'A': 0},
            {'side_gap_factors': {'BC': 1.6}, 'vertex_label_vectors': {'A': (0, 1)}}
        )


def make_orient_type2(tmpl, p, q, p_lbl, q_lbl):
    """유형 ②: 빗변 라벨 숨김"""
    c = math.hypot(p, q)
    if tmpl == 1:
        return (
            {'A': (0, q), 'B': (0, 0), 'C': (p, 0)}, 'B',
            {'AB': q_lbl, 'BC': p_lbl},
            {'A': -10}, {}
        )
    elif tmpl == 2:
        return (
            {'A': (p, q), 'B': (0, 0), 'C': (p, 0)}, 'C',
            {'BC': p_lbl, 'CA': q_lbl},
            {'A': 10}, {}
        )
    elif tmpl == 3:
        _off3 = -0.021 * min(p, q) ** 0.3 * p ** 0.7
        return (
            {'A': (0, 0), 'B': (p, q), 'C': (0, q)}, 'C',
            {'BC': p_lbl, 'CA': q_lbl},
            {'A': 12}, {'side_label_offsets': {'BC': (0, _off3)}}
        )
    elif tmpl == 4:
        _off4 = -0.021 * min(p, q) ** 0.3 * p ** 0.7
        return (
            {'A': (p, 0), 'B': (p, q), 'C': (0, q)}, 'B',
            {'AB': q_lbl, 'BC': p_lbl},
            {'A': -12}, {'side_label_offsets': {'BC': (0, _off4)}}
        )
    elif tmpl == 5:
        return (
            {'B': (0.0, 0.0), 'C': (c, 0.0), 'A': (p**2 / c, p * q / c)}, 'A',
            {'AB': p_lbl, 'AC': q_lbl},
            {'A': 0}, {'vertex_label_vectors': {'A': (0, 1)}}
        )
    elif tmpl == 6:
        return (
            {'B': (0.0, 0.0), 'C': (c, 0.0), 'A': (q**2 / c, p * q / c)}, 'A',
            {'AB': q_lbl, 'AC': p_lbl},
            {'A': 0}, {'vertex_label_vectors': {'A': (0, 1)}}
        )


def make_orient_type3(tmpl, p, q, p_lbl, q_lbl, h_lbl):
    """유형 ③: 중간 길이 변 라벨 숨김"""
    c = math.hypot(p, q)
    if tmpl in [1, 4]:
        lens = [('AB', q, q_lbl), ('BC', p, p_lbl), ('CA', c, h_lbl)]
    elif tmpl in [2, 3]:
        lens = [('AB', c, h_lbl), ('BC', p, p_lbl), ('CA', q, q_lbl)]
    elif tmpl == 5:
        lens = [('AB', p, p_lbl), ('AC', q, q_lbl), ('BC', c, h_lbl)]
    elif tmpl == 6:
        lens = [('AB', q, q_lbl), ('AC', p, p_lbl), ('BC', c, h_lbl)]
    lens_sorted = sorted(lens, key=lambda x: x[1])
    mid_side_key = lens_sorted[1][0]
    full_labels = {k: lbl for k, val, lbl in lens}
    full_labels.pop(mid_side_key, None)

    if tmpl == 1:
        return (
            {'A': (0, q), 'B': (0, 0), 'C': (p, 0)}, 'B', full_labels,
            {'A': -10}, {'side_gap_factors': {'CA': 1.6}} if 'CA' in full_labels else {}
        )
    elif tmpl == 2:
        return (
            {'A': (p, q), 'B': (0, 0), 'C': (p, 0)}, 'C', full_labels,
            {'A': 10}, {'side_gap_factors': {'AB': 1.6}} if 'AB' in full_labels else {}
        )
    elif tmpl == 3:
        _off3 = -0.021 * min(p, q) ** 0.3 * p ** 0.7
        extra = {'side_gap_factors': {'AB': 1.6}} if 'AB' in full_labels else {}
        if 'BC' in full_labels:
            extra['side_label_offsets'] = {'BC': (0, _off3)}
        return ({'A': (0, 0), 'B': (p, q), 'C': (0, q)}, 'C', full_labels, {'A': 12}, extra)
    elif tmpl == 4:
        _off4 = -0.021 * min(p, q) ** 0.3 * p ** 0.7
        extra = {'side_gap_factors': {'CA': 1.6}} if 'CA' in full_labels else {}
        if 'BC' in full_labels:
            extra['side_label_offsets'] = {'BC': (0, _off4)}
        return ({'A': (p, 0), 'B': (p, q), 'C': (0, q)}, 'B', full_labels, {'A': -12}, extra)
    elif tmpl == 5:
        extra = {'side_gap_factors': {'BC': 1.6}} if 'BC' in full_labels else {}
        extra['vertex_label_vectors'] = {'A': (0, 1)}
        return (
            {'B': (0.0, 0.0), 'C': (c, 0.0), 'A': (p**2 / c, p * q / c)}, 'A',
            full_labels, {'A': 0}, extra
        )
    elif tmpl == 6:
        extra = {'side_gap_factors': {'BC': 1.6}} if 'BC' in full_labels else {}
        extra['vertex_label_vectors'] = {'A': (0, 1)}
        return (
            {'B': (0.0, 0.0), 'C': (c, 0.0), 'A': (q**2 / c, p * q / c)}, 'A',
            full_labels, {'A': 0}, extra
        )


# ── 기존 메타데이터 로드 함수 ─────────────────────────────────────────────────
def load_meta(path):
    if os.path.exists(path):
        with open(path, encoding='utf-8') as f:
            return json.load(f)
    return []

meta1_path = os.path.join(ROOT, 'data', 'type1_angle_metadata.json')
meta2_path = os.path.join(ROOT, 'data', 'type2_angle_metadata.json')
meta3_path = os.path.join(ROOT, 'data', 'type3_angle_metadata.json')

meta1 = load_meta(meta1_path)
meta2 = load_meta(meta2_path)
meta3 = load_meta(meta3_path)

# ── 이미지 생성 루프 ──────────────────────────────────────────────────────────
count = 0
t_start = time.time()

for t in triangles:
    tid  = t['id']
    l1v  = t['leg1_val']
    l2v  = t['leg2_val']
    hv   = t['hyp_val']
    l1lb = t['leg1_label']
    l2lb = t['leg2_label']
    hlb  = t['hyp_label']
    cat  = t['category']
    is_iso = math.isclose(l1v, l2v, rel_tol=1e-9)

    variants = [('a', l1v, l2v, l1lb, l2lb)]
    if not is_iso:
        variants.append(('b', l2v, l1v, l2lb, l1lb))

    for var, p, q, p_lbl, q_lbl in variants:
        for tmpl in [1, 2, 3, 4, 5, 6]:

            # 유형①②③ 팩토리 호출
            r1 = make_orient_type1(tmpl, p, q, p_lbl, q_lbl, hlb)
            r2 = make_orient_type2(tmpl, p, q, p_lbl, q_lbl)
            r3 = make_orient_type3(tmpl, p, q, p_lbl, q_lbl, hlb)

            verts1, rv1, sl1, rot1, ex1 = r1
            verts2, rv2, sl2, rot2, ex2 = r2
            verts3, rv3, sl3, rot3, ex3 = r3

            target_angles = [k for k in verts1.keys() if k != rv1]

            for target_a in target_angles:
                # ─ 유형 ① ─
                fname1 = f"tri_{tid}_{tmpl}{var}_{target_a}.png"
                mod.OUTPUT_DIR = DIR1
                draw(verts1, right_v=rv1, side_labels=sl1, filename=fname1,
                     vertex_label_rotations=rot1, gap_factor=1.15,
                     highlight_angle=target_a, **ex1)

                # ─ 유형 ② ─
                fname2 = f"tri2_{tid}_{tmpl}{var}_{target_a}.png"
                mod.OUTPUT_DIR = DIR2
                draw(verts2, right_v=rv2, side_labels=sl2, filename=fname2,
                     vertex_label_rotations=rot2, gap_factor=1.15,
                     highlight_angle=target_a, **ex2)

                # ─ 유형 ③ ─
                fname3 = f"tri3_{tid}_{tmpl}{var}_{target_a}.png"
                mod.OUTPUT_DIR = DIR3
                draw(verts3, right_v=rv3, side_labels=sl3, filename=fname3,
                     vertex_label_rotations=rot3, gap_factor=1.15,
                     highlight_angle=target_a, **ex3)

                count += 1
                elapsed = time.time() - t_start
                print(f"  [{count:3d}] {tid}_{tmpl}{var}_{target_a}  ({elapsed:.1f}s)")

                # 메타데이터 공통 계산
                if tmpl in [1, 4]:
                    sl_len1 = {'AB': q, 'BC': p, 'CA': hv}
                elif tmpl in [2, 3]:
                    sl_len1 = {'AB': hv, 'BC': p, 'CA': q}
                elif tmpl == 5:
                    sl_len1 = {'AB': p, 'AC': q, 'BC': hv}
                elif tmpl == 6:
                    sl_len1 = {'AB': q, 'AC': p, 'BC': hv}

                base_meta = {
                    'triangle_id':     tid,
                    'category':        cat,
                    'template':        tmpl,
                    'variant':         var,
                    'right_vertex':    rv1,
                    'highlight_angle': target_a,
                    'side_lengths':    sl_len1,
                }
                meta1.append({'filename': fname1, 'image_type': 1, 'side_labels': sl1, **base_meta})
                meta2.append({'filename': fname2, 'image_type': 2, 'side_labels': sl2, **base_meta})
                meta3.append({'filename': fname3, 'image_type': 3, 'side_labels': sl3, **base_meta})

# ── 메타데이터 저장 ────────────────────────────────────────────────────────────
with open(meta1_path, 'w', encoding='utf-8') as f:
    json.dump(meta1, f, ensure_ascii=False, indent=2)
with open(meta2_path, 'w', encoding='utf-8') as f:
    json.dump(meta2, f, ensure_ascii=False, indent=2)
with open(meta3_path, 'w', encoding='utf-8') as f:
    json.dump(meta3, f, ensure_ascii=False, indent=2)

elapsed_total = time.time() - t_start
print(f"\n=======================================================")
print(f"✅ 완료: {count}개 이미지 (T026~T028, 3유형 × 3폴더 동시 생성)")
print(f"   Tri_img_01/ (유형①) + Tri_img_02/ (유형②) + Tri_img_03/ (유형③)")
print(f"   메타데이터 append → data/type1~3_angle_metadata.json")
print(f"   총 소요시간 : {elapsed_total:.1f}초")
