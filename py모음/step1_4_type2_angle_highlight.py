# -*- coding: utf-8 -*-
"""
STEP 1-4: 유형 ② 각 하이라이트(부채꼴) 이미지 생성 (두 변만 표기 / 빗변 라벨 및 점선 호 숨김)
=========================================================
triangle_data.json (25가지 삼각형 조합) ×
4가지 방향 템플릿 × 최대 2가지 변형(등변 제외) × 2개 예각 (직각 제외)
= 총 360개 PNG → Tri_img_02/

동시에 data/type2_angle_metadata.json 생성 (questions.json 생성에 사용)

[유형 ② 특성]
- 빗변 라벨 숨김 (두 직각변만 표기)
- 빗변 점선 호 미표기
- 직각 기호 + 꼭짓점 A/B/C 표기
- 예각 1개에 반투명 Red 부채꼴 (각 표시 로직01: 기본 7%, 30° 미만 예각 13%) 하이라이트
"""

import json, math, os, sys, importlib.util, time

# ── 경로 설정 ─────────────────────────────────────────────────────────────────
PY_DIR   = os.path.dirname(os.path.abspath(__file__))          # py모음/
ROOT     = os.path.dirname(PY_DIR)                              # 삼각비 게임1/
TYPE2_DIR = os.path.join(ROOT, 'Tri_img_02')
os.makedirs(TYPE2_DIR, exist_ok=True)

# ── draw() 함수 import (v1.0.5_260809_0010_dash_trim3.py 재사용) ───────────────
_base_script = os.path.join(PY_DIR, 'v1.0.5_260809_0010_dash_trim3.py')
spec = importlib.util.spec_from_file_location('tri_draw', _base_script)
mod  = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
mod.OUTPUT_DIR = TYPE2_DIR     # 출력 폴더를 Tri_img_02 로 override
draw = mod.draw

# ── 삼각형 데이터 로드 ────────────────────────────────────────────────────────
with open(os.path.join(ROOT, 'data', 'triangle_data.json'), encoding='utf-8') as f:
    triangles = json.load(f)

# ── 방향 템플릿 팩토리 (유형 ②: 빗변 라벨 제외) ──────────────────────────────────
def make_orient_type2(tmpl, p, q, p_lbl, q_lbl):
    """
    유형 ②용 orientation 팩토리.
    빗변(h_lbl)을 side_labels에서 제거하여 빗변 라벨과 빗변 점선 호를 생성하지 않음.
    """
    if tmpl == 1:
        # AB=q(수직leg), BC=p(수평leg), CA=hyp (빗변 제외)
        return (
            {'A': (0, q), 'B': (0, 0), 'C': (p, 0)},
            'B',
            {'AB': q_lbl, 'BC': p_lbl},
            {'A': -10},
            {}
        )
    elif tmpl == 2:
        # AB=hyp (빗변 제외), BC=p(수평leg), CA=q(수직leg)
        return (
            {'A': (p, q), 'B': (0, 0), 'C': (p, 0)},
            'C',
            {'BC': p_lbl, 'CA': q_lbl},
            {'A': 10},
            {}
        )
    elif tmpl == 3:
        # AB=hyp (빗변 제외), BC=p(수평leg,상단), CA=q(수직leg)
        _off3 = -0.021 * min(p, q) ** 0.3 * p ** 0.7
        return (
            {'A': (0, 0), 'B': (p, q), 'C': (0, q)},
            'C',
            {'BC': p_lbl, 'CA': q_lbl},
            {'A': 12},
            {'side_label_offsets': {'BC': (0, _off3)}}
        )
    elif tmpl == 4:
        # AB=q(수직leg), BC=p(수평leg,상단), CA=hyp (빗변 제외)
        _off4 = -0.021 * min(p, q) ** 0.3 * p ** 0.7
        return (
            {'A': (p, 0), 'B': (p, q), 'C': (0, q)},
            'B',
            {'AB': q_lbl, 'BC': p_lbl},
            {'A': -12},
            {'side_label_offsets': {'BC': (0, _off4)}}
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
        for tmpl in [1, 2, 3, 4]:
            verts, rv, slabels, rot, extra = make_orient_type2(tmpl, p, q, p_lbl, q_lbl)
            target_angles = [k for k in verts.keys() if k != rv]
            
            for target_a in target_angles:
                fname = f"tri2_{tid}_{tmpl}{var}_{target_a}.png"
                
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
                else:
                    side_len = {'AB': hv, 'BC': p, 'CA': q}

                metadata.append({
                    'filename':        fname,
                    'triangle_id':     tid,
                    'category':        cat,
                    'template':        tmpl,
                    'variant':         var,
                    'right_vertex':    rv,
                    'highlight_angle': target_a,
                    'image_type':      2,
                    'side_lengths':    side_len,
                    'side_labels':     slabels,
                })

                elapsed = time.time() - t_start
                print(f"  [{count:3d}] {fname}  ({elapsed:.1f}s)")

# ── 메타데이터 저장 ────────────────────────────────────────────────────────────
meta_path = os.path.join(ROOT, 'data', 'type2_angle_metadata.json')
with open(meta_path, 'w', encoding='utf-8') as f:
    json.dump(metadata, f, ensure_ascii=False, indent=2)

print("\n=======================================================")
print(f"✅ 완료: {count}개 유형 ② 이미지 → Tri_img_02/")
print(f"   메타데이터  → data/type2_angle_metadata.json")
print(f"   총 소요시간 : {time.time() - t_start:.1f}초")
