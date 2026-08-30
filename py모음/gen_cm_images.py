# -*- coding: utf-8 -*-
"""
gen_cm_images.py
================
v1.0.5 기반 draw()에서 mathtext.fontset을 stix -> cm 으로 바꿔
Tri_img_01_cm, Tri_img_02_cm, Tri_img_03_cm 폴더에 이미지 생성 후
각각 _crop 버전(margin=12px) 도 생성.
"""
import json, math, os, glob, time, importlib.util
from concurrent.futures import ProcessPoolExecutor
from PIL import Image

PY_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT   = os.path.dirname(PY_DIR)

# ── CM 폰트 패치된 draw 모듈 로드 ─────────────────────────────────────────
_base_script = os.path.join(PY_DIR, 'v1.0.5_260809_0010_dash_trim3.py')
spec = importlib.util.spec_from_file_location('tri_draw_cm', _base_script)
mod  = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

# stix -> cm 패치
import matplotlib
matplotlib.rcParams.update({'mathtext.fontset': 'cm', 'mathtext.default': 'rm'})

draw = mod.draw

# ── 삼각형 데이터 ─────────────────────────────────────────────────────────
with open(os.path.join(ROOT, 'data', 'triangle_data.json'), encoding='utf-8') as f:
    triangles = json.load(f)

# ── 템플릿 팩토리 (type1/type2 공용) ─────────────────────────────────────
def make_orient_type1(tmpl, p, q, p_lbl, q_lbl, h_lbl):
    if tmpl == 1:
        return ({'A':(0,q),'B':(0,0),'C':(p,0)}, 'B',
                {'AB':q_lbl,'BC':p_lbl,'CA':h_lbl}, {'A':-10},
                {'side_gap_factors':{'CA':1.6}})
    elif tmpl == 2:
        return ({'A':(p,q),'B':(0,0),'C':(p,0)}, 'C',
                {'AB':h_lbl,'BC':p_lbl,'CA':q_lbl}, {'A':10},
                {'side_gap_factors':{'AB':1.6}})
    elif tmpl == 3:
        _off = -0.021*min(p,q)**0.3*p**0.7
        return ({'A':(0,0),'B':(p,q),'C':(0,q)}, 'C',
                {'AB':h_lbl,'BC':p_lbl,'CA':q_lbl}, {'A':12},
                {'side_label_offsets':{'BC':(0,_off)},'side_gap_factors':{'AB':1.6}})
    elif tmpl == 4:
        _off = -0.021*min(p,q)**0.3*p**0.7
        return ({'A':(p,0),'B':(p,q),'C':(0,q)}, 'B',
                {'AB':q_lbl,'BC':p_lbl,'CA':h_lbl}, {'A':-12},
                {'side_label_offsets':{'BC':(0,_off)},'side_gap_factors':{'CA':1.6}})
    elif tmpl == 5:
        c = math.hypot(p,q)
        return ({'B':(0,0),'C':(c,0),'A':(p**2/c,p*q/c)}, 'A',
                {'AB':p_lbl,'AC':q_lbl}, {'A':0},
                {'side_gap_factors':{'BC':1.6},'vertex_label_vectors':{'A':(0,1)}})
    elif tmpl == 6:
        c = math.hypot(p,q)
        return ({'B':(0,0),'C':(c,0),'A':(q**2/c,p*q/c)}, 'A',
                {'AB':q_lbl,'AC':p_lbl}, {'A':0},
                {'side_gap_factors':{'BC':1.6},'vertex_label_vectors':{'A':(0,1)}})

def make_orient_type2(tmpl, p, q, p_lbl, q_lbl):
    c = math.hypot(p,q)
    if tmpl == 1:
        return ({'A':(0,q),'B':(0,0),'C':(p,0)}, 'B',
                {'AB':q_lbl,'BC':p_lbl}, {'A':-10}, {})
    elif tmpl == 2:
        return ({'A':(p,q),'B':(0,0),'C':(p,0)}, 'C',
                {'BC':p_lbl,'CA':q_lbl}, {'A':10}, {})
    elif tmpl == 3:
        _off = -0.021*min(p,q)**0.3*p**0.7
        return ({'A':(0,0),'B':(p,q),'C':(0,q)}, 'C',
                {'BC':p_lbl,'CA':q_lbl}, {'A':12},
                {'side_label_offsets':{'BC':(0,_off)}})
    elif tmpl == 4:
        _off = -0.021*min(p,q)**0.3*p**0.7
        return ({'A':(p,0),'B':(p,q),'C':(0,q)}, 'B',
                {'AB':q_lbl,'BC':p_lbl}, {'A':-12},
                {'side_label_offsets':{'BC':(0,_off)}})
    elif tmpl == 5:
        return ({'B':(0,0),'C':(c,0),'A':(p**2/c,p*q/c)}, 'A',
                {'AB':p_lbl,'AC':q_lbl}, {'A':0},
                {'vertex_label_vectors':{'A':(0,1)}})
    elif tmpl == 6:
        return ({'B':(0,0),'C':(c,0),'A':(q**2/c,p*q/c)}, 'A',
                {'AB':q_lbl,'AC':p_lbl}, {'A':0},
                {'vertex_label_vectors':{'A':(0,1)}})

def generate_type(img_type, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    mod.OUTPUT_DIR = out_dir
    count = 0
    t0 = time.time()
    for t in triangles:
        tid = t['id']
        l1v,l2v = t['leg1_val'],t['leg2_val']
        l1lb,l2lb,hlb = t['leg1_label'],t['leg2_label'],t['hyp_label']
        is_iso = math.isclose(l1v,l2v,rel_tol=1e-9)
        variants = [('a',l1v,l2v,l1lb,l2lb)]
        if not is_iso:
            variants.append(('b',l2v,l1v,l2lb,l1lb))
        for var,p,q,p_lbl,q_lbl in variants:
            for tmpl in [1,2,3,4,5,6]:
                if img_type == 1:
                    verts,rv,slabels,rot,extra = make_orient_type1(tmpl,p,q,p_lbl,q_lbl,hlb)
                    target_angles = [k for k in verts if k!=rv]
                    for ta in target_angles:
                        fname = f"tri_{tid}_{tmpl}{var}_{ta}.png"
                        draw(verts,right_v=rv,side_labels=slabels,filename=fname,
                             vertex_label_rotations=rot,gap_factor=1.15,highlight_angle=ta,**extra)
                        count += 1
                elif img_type == 2:
                    verts,rv,slabels,rot,extra = make_orient_type2(tmpl,p,q,p_lbl,q_lbl)
                    target_angles = [k for k in verts if k!=rv]
                    for ta in target_angles:
                        fname = f"tri2_{tid}_{tmpl}{var}_{ta}.png"
                        draw(verts,right_v=rv,side_labels=slabels,filename=fname,
                             vertex_label_rotations=rot,gap_factor=1.15,highlight_angle=ta,**extra)
                        count += 1
    print(f"  type{img_type}: {count}개 생성 ({time.time()-t0:.1f}s)")
    return count

def crop_folder(src_dir, dst_dir, margin=12):
    os.makedirs(dst_dir, exist_ok=True)
    files = glob.glob(os.path.join(src_dir,'*.png'))
    def _crop(args):
        sp,dp,m = args
        try:
            with Image.open(sp) as img:
                img = img.convert('RGBA')
                bb = img.getbbox()
                if bb:
                    c = img.crop((max(0,bb[0]-m),max(0,bb[1]-m),
                                  min(img.width,bb[2]+m),min(img.height,bb[3]+m)))
                    c.save(dp,'PNG')
                else:
                    img.save(dp,'PNG')
        except Exception as e:
            print(f"Error {sp}: {e}")
    tasks = [(f, os.path.join(dst_dir, os.path.basename(f)), margin) for f in files]
    with ProcessPoolExecutor() as ex:
        list(ex.map(_crop, tasks))
    print(f"  crop: {len(files)}개 → {dst_dir}")

if __name__ == '__main__':
    print("=== CM 폰트 이미지 생성 시작 ===")
    t_total = time.time()

    # TYPE 1
    print("[1] Tri_img_01_cm 생성 중...")
    generate_type(1, os.path.join(ROOT, 'Tri_img_01_cm'))
    print("[1-crop] Tri_img_01_cm_crop 크롭 중...")
    crop_folder(os.path.join(ROOT,'Tri_img_01_cm'), os.path.join(ROOT,'Tri_img_01_cm_crop'))

    # TYPE 2
    print("[2] Tri_img_02_cm 생성 중...")
    generate_type(2, os.path.join(ROOT, 'Tri_img_02_cm'))
    print("[2-crop] Tri_img_02_cm_crop 크롭 중...")
    crop_folder(os.path.join(ROOT,'Tri_img_02_cm'), os.path.join(ROOT,'Tri_img_02_cm_crop'))

    print(f"\n✅ 전체 완료: {time.time()-t_total:.1f}초")
