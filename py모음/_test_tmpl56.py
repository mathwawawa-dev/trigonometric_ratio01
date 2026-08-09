import json, math, os, sys, importlib.util

PY_DIR   = os.path.dirname(os.path.abspath(__file__))
ROOT     = os.path.dirname(PY_DIR)
TEST_DIR = os.path.join(ROOT, 'triangles4', 'dash_test_tmpl56')
os.makedirs(TEST_DIR, exist_ok=True)

_base_script = os.path.join(PY_DIR, 'v1.0.5_260809_0010_dash_trim3.py')
spec = importlib.util.spec_from_file_location('tri_draw', _base_script)
mod  = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
mod.OUTPUT_DIR = TEST_DIR
draw = mod.draw

# tmpl 5, tmpl 6 생성 함수 테스트 (p=2, q=4, c=sqrt(20)=4.472136)
p, q = 2.0, 4.0
c = math.hypot(p, q)

# tmpl 5: B(0,0), C(c,0), A(p^2/c, p*q/c)
verts5 = {'B': (0.0, 0.0), 'C': (c, 0.0), 'A': (p**2 / c, p * q / c)}
labels5 = {'AB': '2', 'AC': '4', 'BC': r'2\sqrt{5}'}

# tmpl 6: B(0,0), C(c,0), A(q^2/c, p*q/c)
verts6 = {'B': (0.0, 0.0), 'C': (c, 0.0), 'A': (q**2 / c, p * q / c)}
labels6 = {'AB': '4', 'AC': '2', 'BC': r'2\sqrt{5}'}

draw(verts5, right_v='A', side_labels=labels5, filename='test_tmpl5_B.png', highlight_angle='B')
draw(verts5, right_v='A', side_labels=labels5, filename='test_tmpl5_C.png', highlight_angle='C')
draw(verts6, right_v='A', side_labels=labels6, filename='test_tmpl6_B.png', highlight_angle='B')
draw(verts6, right_v='A', side_labels=labels6, filename='test_tmpl6_C.png', highlight_angle='C')

print("Done test tmpl 5 & 6 in dash_test_tmpl56")
