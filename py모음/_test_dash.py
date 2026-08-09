import os, json, importlib.util

PY_DIR   = os.path.dirname(os.path.abspath(__file__))
ROOT     = os.path.dirname(PY_DIR)
OUT_DIR  = os.path.join(ROOT, 'triangles4', 'dash_test')
os.makedirs(OUT_DIR, exist_ok=True)

# 원본 코드 읽기
with open(os.path.join(PY_DIR, 'v1.0.2_260808_1536_triangles4변경.py'), 'r', encoding='utf-8') as f:
    code = f.read()

# patch 삽입
patch = """
        import numpy as np
        
        # dash length 1/3 trim logic
        dash_on = 6.0
        dash_off = 4.0
        dash_period = dash_on + dash_off
        threshold = dash_on / 3.0  # 2.0 pt 이하이면 삭제
        
        du2pt = 72.0 * (FIG_S / span)
        
        for seg, is_post_gap in segments:
            pts_draw = seg[::-1] if is_post_gap else seg
            
            diffs = np.diff(pts_draw, axis=0)
            step_dists = np.linalg.norm(diffs, axis=1)
            dist_du = np.concatenate(([0.0], np.cumsum(step_dists)))
            dist_pt = dist_du * du2pt
            
            total_pt = dist_pt[-1]
            R = total_pt % dash_period
            
            if 0 < R <= threshold:
                target_pt = total_pt - R
                keep_idx = dist_pt <= target_pt
                pts_draw = pts_draw[keep_idx]
            
            if len(pts_draw) > 1:
                ax.plot(pts_draw[:, 0], pts_draw[:, 1], **dash_kw)
"""

target_str = """        for seg, is_post_gap in segments:
            pts_draw = seg[::-1] if is_post_gap else seg   # 갭 뒤는 역방향
            ax.plot(pts_draw[:, 0], pts_draw[:, 1], **dash_kw)"""

code = code.replace(target_str, patch)

test_script_path = os.path.join(PY_DIR, '_test_dash_trim_module.py')
with open(test_script_path, 'w', encoding='utf-8') as f:
    f.write(code)

# 생성 스크립트 작성 (T007_3b만 생성)
gen_script = """import os, json, importlib.util
from step1_2_edited05 import make_orient

PY_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(PY_DIR)
OUT_DIR = os.path.join(ROOT, 'triangles4', 'dash_test')

spec = importlib.util.spec_from_file_location('tri_draw', os.path.join(PY_DIR, '_test_dash_trim_module.py'))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
mod.OUTPUT_DIR = OUT_DIR
draw = mod.draw

with open(os.path.join(ROOT, 'data', 'triangle_data.json'), encoding='utf-8') as f:
    triangles = json.load(f)

for t in triangles:
    if t['id'] == 'T007':
        p, q = t['leg2_val'], t['leg1_val']
        p_lbl, q_lbl = t['leg2_label'], t['leg1_label']
        hlb = t['hyp_label']
        verts, rv, slabels, rot, extra = make_orient(3, p, q, p_lbl, q_lbl, hlb)
        draw(verts, right_v=rv, side_labels=slabels, filename='tri_T007_3b_trimmed.png', vertex_label_rotations=rot, gap_factor=1.15, **extra)
        print('Saved: tri_T007_3b_trimmed.png')
        break
"""
with open(os.path.join(PY_DIR, '_test_dash_gen.py'), 'w', encoding='utf-8') as f:
    f.write(gen_script)
