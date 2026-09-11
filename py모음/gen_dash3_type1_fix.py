import json, math, os, glob, time, importlib.util
from PIL import Image

PY_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT   = os.path.dirname(PY_DIR)

_base_path = os.path.join(PY_DIR, 'v1.0.5_260809_0010_dash_trim3.py')
with open(_base_path, 'r', encoding='utf-8') as f:
    _src = f.read()

_src = _src.replace('_DASH_ON_DU  = 4.5 / _pt_per_du',  '_DASH_ON_DU  = 2.25 / _pt_per_du')
_src = _src.replace('_DASH_CYC_DU = 7.5 / _pt_per_du',  '_DASH_CYC_DU = 5.25 / _pt_per_du')
_src = _src.replace('dashes=(4.5, 3.0),',                'dashes=(2.25, 3.0),')
_src = _src.replace('dash_cycle_data = ((4.5 + 3.0) / 72.0) * span / FIG_S',
                    'dash_cycle_data = ((2.25 + 3.0) / 72.0) * span / FIG_S')

_tmp = os.path.join(PY_DIR, '_tri_draw_dash3_tmp.py')
with open(_tmp, 'w', encoding='utf-8') as f:
    f.write(_src)

spec = importlib.util.spec_from_file_location('tri_draw_dash3', _tmp)
mod  = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
draw = mod.draw

with open(os.path.join(ROOT, 'data', 'triangle_data.json'), encoding='utf-8') as f:
    triangles = json.load(f)

# ── TYPE1 only (원본 make_orient 로직 완전 일치) ──────────────
def make1(tmpl, p, q, pl, ql, hl):
    c = math.hypot(p, q)
    if tmpl == 1:
        return ({'A':(0,q),'B':(0,0),'C':(p,0)}, 'B',
                {'AB':ql,'BC':pl,'CA':hl}, {'A':-10},
                {'side_gap_factors':{'CA':1.6}})
    elif tmpl == 2:
        return ({'A':(p,q),'B':(0,0),'C':(p,0)}, 'C',
                {'AB':hl,'BC':pl,'CA':ql}, {'A':10},
                {'side_gap_factors':{'AB':1.6}})
    elif tmpl == 3:
        o = -0.021*min(p,q)**0.3*p**0.7
        return ({'A':(0,0),'B':(p,q),'C':(0,q)}, 'C',
                {'AB':hl,'BC':pl,'CA':ql}, {'A':12},
                {'side_label_offsets':{'BC':(0,o)},'side_gap_factors':{'AB':1.6}})
    elif tmpl == 4:
        o = -0.021*min(p,q)**0.3*p**0.7
        return ({'A':(p,0),'B':(p,q),'C':(0,q)}, 'B',
                {'AB':ql,'BC':pl,'CA':hl}, {'A':-12},
                {'side_label_offsets':{'BC':(0,o)},'side_gap_factors':{'CA':1.6}})
    elif tmpl == 5:
        # 원본과 동일: BC=h_lbl 포함
        return ({'B':(0,0),'C':(c,0),'A':(p**2/c,p*q/c)}, 'A',
                {'AB':pl,'AC':ql,'BC':hl}, {'A':0},
                {'side_gap_factors':{'BC':1.6},'vertex_label_vectors':{'A':(0,1)}})
    elif tmpl == 6:
        # 원본과 동일: BC=h_lbl 포함
        return ({'B':(0,0),'C':(c,0),'A':(q**2/c,p*q/c)}, 'A',
                {'AB':ql,'AC':pl,'BC':hl}, {'A':0},
                {'side_gap_factors':{'BC':1.6},'vertex_label_vectors':{'A':(0,1)}})

def generate_type1(out):
    os.makedirs(out, exist_ok=True); mod.OUTPUT_DIR = out
    n = 0; t0 = time.time()
    for t in triangles:
        tid = t['id']
        l1v,l2v = t['leg1_val'],t['leg2_val']
        l1lb,l2lb,hlb = t['leg1_label'],t['leg2_label'],t['hyp_label']
        iso = math.isclose(l1v,l2v,rel_tol=1e-9)
        variants = [('a',l1v,l2v,l1lb,l2lb)]
        if not iso: variants.append(('b',l2v,l1v,l2lb,l1lb))
        for var,p,q,pl,ql in variants:
            for tmpl in [1,2,3,4,5,6]:
                verts,rv,sl,rot,ex = make1(tmpl,p,q,pl,ql,hlb)
                for ta in [k for k in verts if k != rv]:
                    draw(verts,right_v=rv,side_labels=sl,
                         filename=f'tri_{tid}_{tmpl}{var}_{ta}.png',
                         vertex_label_rotations=rot,gap_factor=1.15,
                         highlight_angle=ta,**ex)
                    n += 1
    print(f'  type1: {n}개 ({time.time()-t0:.1f}s)')

def crop_dir(src, dst, m=12):
    os.makedirs(dst, exist_ok=True)
    files = glob.glob(os.path.join(src,'*.png')); t0 = time.time()
    for f in files:
        with Image.open(f) as img:
            img = img.convert('RGBA'); bb = img.getbbox()
            if bb:
                c = img.crop((max(0,bb[0]-m),max(0,bb[1]-m),
                              min(img.width,bb[2]+m),min(img.height,bb[3]+m)))
                c.save(os.path.join(dst,os.path.basename(f)),'PNG')
            else:
                img.save(os.path.join(dst,os.path.basename(f)),'PNG')
    print(f'  crop: {len(files)}개 ({time.time()-t0:.1f}s)')

T = time.time()
raw  = os.path.join(ROOT, 'Tri_img_01_dash3')
crp  = os.path.join(ROOT, 'Tri_img_01_crop_dash3')
print(f'[1] 생성 → {raw}')
generate_type1(raw)
print(f'[1-crop] 크롭 → {crp}')
crop_dir(raw, crp)
try: os.remove(_tmp)
except: pass
print(f'완료: {time.time()-T:.1f}s')
