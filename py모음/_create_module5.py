import os, sys, json, importlib.util, numpy as np
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties

PY_DIR  = os.path.dirname(os.path.abspath(__file__))
ROOT    = os.path.dirname(PY_DIR)

with open(os.path.join(PY_DIR, 'v1.0.2_260808_1536_triangles4변경.py'), 'r', encoding='utf-8') as f:
    code = f.read()

OLD = (
    "        for seg, is_post_gap in segments:\n"
    "            pts_draw = seg[::-1] if is_post_gap else seg   # 갭 뒤는 역방향\n"
    "            ax.plot(pts_draw[:, 0], pts_draw[:, 1], **dash_kw)"
)

NEW = (
    "        # 정확한 Data 단위당 Point 계산\n"
    "        p0 = ax.transData.transform((0, 0))\n"
    "        p1 = ax.transData.transform((1, 0))\n"
    "        pts_per_du = np.linalg.norm(p1 - p0)\n"
    "        if pts_per_du > 0:\n"
    "            _dash_on_du  = 4.5 / pts_per_du\n"
    "            _dash_per_du = 7.5 / pts_per_du\n"
    "        else:\n"
    "            _dash_on_du  = 0.05\n"
    "            _dash_per_du = 0.08\n"
    "\n"
    "        for seg, is_post_gap in segments:\n"
    "            pts_draw = seg[::-1] if is_post_gap else seg\n"
    "            _diffs   = np.diff(pts_draw, axis=0)\n"
    "            _dist_du = np.concatenate(([0.0], np.cumsum(np.linalg.norm(_diffs, axis=1))))\n"
    "            _total   = float(_dist_du[-1])\n"
    "            \n"
    "            # 세그먼트 전체가 온전한 대시 1개 길이보다 짧으면 아예 그리지 않음\n"
    "            if _total < _dash_on_du:\n"
    "                continue\n"
    "            \n"
    "            # 마지막 대시가 잘려서 짧아지는 경우(Trailing stub) 제거\n"
    "            # _R은 마지막 주기의 남은 길이\n"
    "            _R = _total % _dash_per_du\n"
    "            # _R이 _dash_on_du보다 작다는 것은, 마지막 대시가 도중에 끊겼음을 의미함.\n"
    "            # 이를 제거하면 항상 온전한 길이의 대시로 끝남.\n"
    "            if _R < _dash_on_du:\n"
    "                pts_draw = pts_draw[_dist_du <= (_total - _R)]\n"
    "            \n"
    "            if len(pts_draw) > 1:\n"
    "                ax.plot(pts_draw[:, 0], pts_draw[:, 1], **dash_kw)"
)

patched_code = code.replace(OLD, NEW)

trim_module_path = os.path.join(PY_DIR, '_dash_trim_module5.py')
with open(trim_module_path, 'w', encoding='utf-8') as f:
    f.write(patched_code)
