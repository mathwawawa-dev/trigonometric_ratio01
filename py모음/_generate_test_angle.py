import os
import sys

PY_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(PY_DIR)
TEST_DIR = os.path.join(ROOT, 'triangles4', 'dash_test_angle')
os.makedirs(TEST_DIR, exist_ok=True)

from _test_angle_module import draw, OUTPUT_DIR

# 몽키패치 출력 경로
import _test_angle_module
_test_angle_module.OUTPUT_DIR = TEST_DIR

# 테스트 샘플 12개 설정
samples = [
    # 3:4:5 직각삼각형 계열
    ({"A": (0,0), "B": (4,3), "C": (0,3)}, "C", {"A-B": "5", "B-C": "4", "C-A": "3"}, "tri_T006_3b.png", "A"),
    
    # 5:12:13 계열 (크기가 큰 직각삼각형, 각도가 아주 뾰족함)
    ({"B": (0,0), "C": (5,0), "A": (0,12)}, "B", {"B-C": "5", "C-A": "13", "A-B": "12"}, "tri_T019_1a.png", "C"),
    ({"B": (0,0), "C": (5,0), "A": (0,12)}, "B", {"B-C": "5", "C-A": "13", "A-B": "12"}, "tri_T019_1a_A.png", "A"),

    # 1:2:루트3 계열 (크기가 작음)
    ({"B": (0,0), "C": (1,0), "A": (0,1.732)}, "B", {"B-C": "1", "C-A": "2", "A-B": r"\sqrt{3}"}, "tri_T017_1a.png", "C"),
    ({"B": (0,0), "C": (1,0), "A": (0,1.732)}, "B", {"B-C": "1", "C-A": "2", "A-B": r"\sqrt{3}"}, "tri_T017_1a_A.png", "A"),

    # 이등변 직각삼각형 1:1:루트2 계열
    ({"C": (0,0), "B": (1,0), "A": (1,1)}, "B", {"C-B": "1", "B-A": "1", "A-C": r"\sqrt{2}"}, "tri_T015_2a.png", "C"),
    ({"C": (0,0), "B": (1,0), "A": (1,1)}, "B", {"C-B": "1", "B-A": "1", "A-C": r"\sqrt{2}"}, "tri_T015_2a_A.png", "A"),

    # 둔각에 가까운 모양 (예각이 아주 작은 경우)
    ({"C": (0,0), "A": (-5,-3), "B": (0,-3)}, "B", {"C-A": r"\sqrt{34}", "A-B": "5", "B-C": "3"}, "tri_T024_4a.png", "A"),
    ({"C": (0,0), "B": (5,-3), "A": (0,-3)}, "A", {"C-B": r"\sqrt{34}", "B-A": "5", "A-C": "3"}, "tri_T025_3b.png", "B"),

    # 임의의 비율 추가
    ({"B": (0,0), "C": (6,0), "A": (0,2)}, "B", {"B-C": "6", "C-A": r"2\sqrt{10}", "A-B": "2"}, "tri_T007_1a.png", "C"),
    ({"B": (0,0), "C": (3,0), "A": (3,4)}, "C", {"B-C": "3", "C-A": "4", "A-B": "5"}, "tri_T022_1b.png", "A"),
]

for verts, rv, labels, fname, hl in samples:
    draw(verts, rv, labels, fname, highlight_angle=hl)

print("Done generating 12 samples in dash_test_angle/")
