# -*- coding: utf-8 -*-
"""
STEP 1-4-2: 유형 ③ 각 하이라이트(부채꼴) 이미지 생성 (중간 길이 변 라벨 숨김 / 두 변만 표기, 템플릿 6종)
=============================================================================================
triangle_data.json (25가지 삼각형 조합) ×
6가지 방향 템플릿 × 최대 2가지 변형(등변 제외) × 2개 예각 (직각 제외)
= 총 540개 PNG → Tri_img_03/

동시에 data/type3_angle_metadata.json 생성 (questions.json 생성에 사용)

[6가지 방향 템플릿]
  tmpl 1: A 상좌 / B 하좌(직각) / C 하우
  tmpl 2: A 상우 / B 하좌       / C 하우(직각)
  tmpl 3: A 하좌 / B 상우       / C 상좌(직각)
  tmpl 4: A 하우 / B 상우(직각) / C 상좌
  tmpl 5: B-C 수평 바닥 (빗변) / A 상단(직각) (AB=p, AC=q)
  tmpl 6: B-C 수평 바닥 (빗변) / A 상단(직각) (AB=q, AC=p)
"""

import json, math, os, sys, importlib.util, time

# ── 경로 설정 ─────────────────────────────────────────────────────────────────
PY_DIR   = os.path.dirname(os.path.abspath(__file__))          # py모음/
ROOT     = os.path.dirname(PY_DIR)                              # 삼각비 게임1/
TYPE3_DIR = os.path.join(ROOT, 'Tri_img_03')
os.makedirs(TYPE3_DIR, exist_ok=True)

# ── draw() 함수 import (v1.0.5_260809_0010_dash_trim3.py 재사용) ───────────────
_base_script = os.path.join(PY_DIR, 'v1.0.5_260809_0010_dash_trim3.py')
spec = importlib.util.spec_from_file_location('tri_draw', _base_script)
mod  = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
mod.OUTPUT_DIR = TYPE3_DIR
draw = mod.draw

# ── 삼각형 데이터 로드 ────────────────────────────────────────────────────────
with open(os.path.join(ROOT, 'data', 'triangle_data.json'), encoding='utf-8') as f:
    triangles = json.load(f)

# ── 방향 템플릿 팩토리 (유형 ③: 중간 길이 변 라벨 제외 6종) ─────────────────────
def make_orient_type3(tmpl, p, q, p_lbl, q_lbl, h_lbl):
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
            {'A': (0, q), 'B': (0, 0), 'C': (p, 0)},
            'B',
            full_labels,
            {'A': -10},
            {'side_gap_factors': {'CA': 1.6}} if 'CA' in full_labels else {}
        )
    elif tmpl == 2:
        return (
            {'A': (p, q), 'B': (0, 0), 'C': (p, 0)},
            'C',
            full_labels,
            {'A': 10},
            {'side_gap_factors': {'AB': 1.6}} if 'AB' in full_labels else {}
        )
    elif tmpl == 3:
        _off3 = -0.021 * min(p, q) ** 0.3 * p ** 0.7
        extra = {'side_gap_factors': {'AB': 1.6}} if 'AB' in full_labels else {}
        if 'BC' in full_labels:
            extra['side_label_offsets'] = {'BC': (0, _off3)}
        return (
            {'A': (0, 0), 'B': (p, q), 'C': (0, q)},
            'C',
            full_labels,
            {'A': 12},
            extra
        )
    elif tmpl == 4:
        _off4 = -0.021 * min(p, q) ** 0.3 * p ** 0.7
        extra = {'side_gap_factors': {'CA': 1.6}} if 'CA' in full_labels else {}
        if 'BC' in full_labels:
            extra['side_label_offsets'] = {'BC': (0, _off4)}
        return (
            {'A': (p, 0), 'B': (p, q), 'C': (0, q)},
            'B',
            full_labels,
            {'A': -12},
            extra
        )
    elif tmpl == 5:
        extra = {'side_gap_factors': {'BC': 1.6}} if 'BC' in full_labels else {}
        return (
            {'B': (0.0, 0.0), 'C': (c, 0.0), 'A': (p**2 / c, p * q / c)},
            'A',
            full_labels,
            {'A': 0},
            extra
        )
    elif tmpl == 6:
        extra = {'side_gap_factors': {'BC': 1.6}} if 'BC' in full_labels else {}
        return (
            {'B': (0.0, 0.0), 'C': (c, 0.0), 'A': (q**2 / c, p * q / c)},
            'A',
            full_labels,
            {'A': 0},
            extra
        )

# ── 이미지 생성 루프 ──────────────────────────────────────────────────────────
metadata = []
count    = 0
t_start  = time.time()

for t in triangles:
    tid   = t['id']
    l1v   = t['leg1_val']
    l2v   = t['leg2_val']
    hv    = t['hyp_val']
    l1lb  = t['leg1_label']
    l2lb  = t['leg2_label']
    hlb   = t['hyp_label']
    cat   = t['category']
    is_iso = math.isclose(l1v, l2v, rel_tol=1e-9)

    variants = [('a', l1v, l2v, l1lb, l2lb)]
    if not is_iso:
        variants.append(('b', l2v, l1v, l2lb, l1lb))

    for var, p, q, p_lbl, q_lbl in variants:
        for tmpl in [1, 2, 3, 4, 5, 6]:
            verts, rv, slabels, rot, extra = make_orient_type3(tmpl, p, q, p_lbl, q_lbl, hlb)
            target_angles = [k for k in verts.keys() if k != rv]
            
            for target_a in target_angles:
                fname = f"tri3_{tid}_{tmpl}{var}_{target_a}.png"
                
                draw(
                    verts,
                    right_v=rv,
                    side_labels=slabels,
                    filename=fname,
                    vertex_label_rotations=rot,
                    gap_factor=1.15,
                    highlight_angle=target_a,
                    **extra
                )
                
                count += 1
                
                if tmpl in [1, 4]:
                    side_len = {'AB': q, 'BC': p, 'CA': hv}
                elif tmpl in [2, 3]:
                    side_len = {'AB': hv, 'BC': p, 'CA': q}
                elif tmpl == 5:
                    side_len = {'AB': p, 'AC': q, 'BC': hv}
                elif tmpl == 6:
                    side_len = {'AB': q, 'AC': p, 'BC': hv}

                metadata.append({
                    'filename':        fname,
                    'triangle_id':     tid,
                    'category':        cat,
                    'template':        tmpl,
                    'variant':         var,
                    'right_vertex':    rv,
                    'highlight_angle': target_a,
                    'image_type':      3,
                    'side_lengths':    side_len,
                    'side_labels':     slabels,
                })

                elapsed = time.time() - t_start
                print(f"  [{count:3d}] {fname}  ({elapsed:.1f}s)")

# ── 메타데이터 저장 ────────────────────────────────────────────────────────────
meta_path = os.path.join(ROOT, 'data', 'type3_angle_metadata.json')
with open(meta_path, 'w', encoding='utf-8') as f:
    json.dump(metadata, f, ensure_ascii=False, indent=2)

print("\n=======================================================")
print(f"✅ 완료: {count}개 유형 ③ 이미지 → Tri_img_03/")
print(f"   메타데이터  → data/type3_angle_metadata.json")
print(f"   총 소요시간 : {time.time() - t_start:.1f}초")
