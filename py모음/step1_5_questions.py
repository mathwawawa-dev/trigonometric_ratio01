# -*- coding: utf-8 -*-
"""
STEP 1-5: questions.json 자동 생성
====================================
type1~3_angle_metadata.json + triangle_data.json 을 연동하여
각 이미지별 sin/cos/tan 3문항, 선지 4개(정답1 + 오답3)를 자동 생성합니다.

산출물: data/questions.json
총 문항 수: 이미지 수 × 3 (sin/cos/tan) × 3 유형 = 약 5,508문항
"""

import json, math, random, os

# ── 경로 ────────────────────────────────────────────────────────────────────
ROOT     = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, 'data')

# ── 데이터 로드 ──────────────────────────────────────────────────────────────
with open(os.path.join(DATA_DIR, 'triangle_data.json'), encoding='utf-8') as f:
    tri_list = json.load(f)
tri_map = {t['id']: t for t in tri_list}  # id → triangle dict

metas = []
for type_num in [1, 2, 3]:
    fname = f'type{type_num}_angle_metadata.json'
    with open(os.path.join(DATA_DIR, fname), encoding='utf-8') as f:
        metas += json.load(f)

print(f"총 메타데이터 항목: {len(metas)}")

# ── 헬퍼 함수 ────────────────────────────────────────────────────────────────

def get_edge_length(side_lengths, v1, v2):
    """두 꼭짓점 이름으로 변 길이 조회 (AB/BA 모두 처리)"""
    return side_lengths.get(v1 + v2) or side_lengths.get(v2 + v1)


def get_edge_label(length, tri):
    """변 길이로 triangle_data에서 라벨 문자열 조회"""
    if math.isclose(length, tri['hyp_val'], rel_tol=1e-5):
        return tri['hyp_label']
    if math.isclose(length, tri['leg1_val'], rel_tol=1e-5):
        return tri['leg1_label']
    if math.isclose(length, tri['leg2_val'], rel_tol=1e-5):
        return tri['leg2_label']
    return f"${length:.4g}$"


def inner(lbl):
    """'$\\sqrt{3}$' → '\\sqrt{3}' ($ 제거)"""
    return lbl.strip().strip('$').strip()


def frac_label(num_lbl, den_lbl):
    """분수 LaTeX 문자열 생성: 약분 포함"""
    import re
    def parse(l):
        l = l.strip().strip('$').strip()
        m = re.match(r'^(\d*)\\sqrt\{(\d+)\}$', l)
        if m: return (int(m.group(1)) if m.group(1) else 1, int(m.group(2)))
        m = re.match(r'^(\d+)$', l)
        if m: return (int(m.group(1)), 1)
        return None

    pn = parse(num_lbl)
    pd = parse(den_lbl)
    
    if not pn or not pd:
        n = num_lbl.strip().strip('$').strip()
        d = den_lbl.strip().strip('$').strip()
        if n == d: return "$1$"
        if d == '1': return f"${n}$"
        return f"$\\frac{{{n}}}{{{d}}}$"
    
    c, r = pn
    C, R = pd
    
    g = math.gcd(c, C)
    c //= g
    C //= g
    
    if r == R:
        r = 1
        R = 1
        
    g_root = math.gcd(r, R)
    r //= g_root
    R //= g_root
    
    def fmt(c, r):
        if r == 1: return str(c)
        if c == 1: return f"\\sqrt{{{r}}}"
        return f"{c}\\sqrt{{{r}}}"
        
    num_str = fmt(c, r)
    den_str = fmt(C, R)
    
    if den_str == '1':
        return f"${num_str}$"
    return f"$\\frac{{{num_str}}}{{{den_str}}}$"


def make_choices(correct_lbl, distractor_lbls):
    """정답 + 오답 3개 → 셔플된 4개 선지, 정답 인덱스 반환"""
    choices = [correct_lbl] + distractor_lbls[:3]
    random.shuffle(choices)
    answer_idx = choices.index(correct_lbl)
    return choices, answer_idx


# ── 문항 생성 ────────────────────────────────────────────────────────────────
random.seed(42)  # 재현 가능한 셔플

questions = []
q_id = 1

for entry in metas:
    tid   = entry['triangle_id']
    tri   = tri_map[tid]
    H     = entry['highlight_angle']   # 타겟 예각
    R     = entry['right_vertex']      # 직각 꼭짓점
    T     = ({'A', 'B', 'C'} - {H, R}).pop()  # 나머지 꼭짓점
    sl    = entry['side_lengths']
    itype = entry['image_type']
    fname = entry['filename']

    # 변 길이
    hyp_len = get_edge_length(sl, H, T)   # 빗변 (직각 꼭짓점 반대편)
    opp_len = get_edge_length(sl, R, T)   # H의 대변
    adj_len = get_edge_length(sl, H, R)   # H의 인접변(직각변)

    if not (hyp_len and opp_len and adj_len):
        continue  # 비정상 데이터 skip

    # 변 라벨
    hyp_lbl = get_edge_label(hyp_len, tri)
    opp_lbl = get_edge_label(opp_len, tri)
    adj_lbl = get_edge_label(adj_len, tri)

    # 삼각비 값
    sin_val = opp_len / hyp_len
    cos_val = adj_len / hyp_len
    tan_val = opp_len / adj_len

    # 분수 라벨 (약분 자동 적용)
    sin_correct = frac_label(opp_lbl, hyp_lbl)
    cos_correct = frac_label(adj_lbl, hyp_lbl)
    tan_correct = frac_label(opp_lbl, adj_lbl)
    
    # 그 외 나올 수 있는 모든 삼각비 값들 (오답 풀)
    pool = [
        cos_correct,
        tan_correct,
        frac_label(hyp_lbl, opp_lbl), # csc
        frac_label(adj_lbl, opp_lbl), # cot
        frac_label(hyp_lbl, adj_lbl), # sec
        frac_label(adj_lbl, hyp_lbl)  # cos (for fallback)
    ]

    def get_unique_distractors(correct_ans):
        unique_pool = []
        for p in pool:
            if p != correct_ans and p not in unique_pool:
                unique_pool.append(p)
        
        # 만약 길이가 3개가 안 된다면 임의의 더미 오답 추가 (거의 발생 안 함)
        dummy_val = 2
        while len(unique_pool) < 3:
            dummy_ans = f"${dummy_val}$"
            if dummy_ans != correct_ans and dummy_ans not in unique_pool:
                unique_pool.append(dummy_ans)
            dummy_val += 1
            
        return unique_pool[:3]

    # 오답 선지 고유하게 3개 추출
    sin_distractors = get_unique_distractors(sin_correct)
    cos_distractors = get_unique_distractors(cos_correct)
    tan_distractors = get_unique_distractors(tan_correct)

    base = {
        'filename':      fname,
        'image_type':    itype,
        'triangle_id':   tid,
        'category':      entry['category'],
        'template':      entry['template'],
        'variant':       entry['variant'],
        'highlight_angle': H,
        'right_vertex':  R,
    }

    for qtype, correct, distractors, val in [
        ('sin', sin_correct, sin_distractors, sin_val),
        ('cos', cos_correct, cos_distractors, cos_val),
        ('tan', tan_correct, tan_distractors, tan_val),
    ]:
        choices, ans_idx = make_choices(correct, distractors)
        questions.append({
            'id':            f"Q{q_id:05d}",
            'question_type': qtype,
            'question':      f"다음 삼각형에서 $\\{qtype} {H}$의 값은?",
            'choices':       choices,
            'answer_index':  ans_idx,
            'answer_value':  round(val, 10),
            **base,
        })
        q_id += 1

# ── 저장 ─────────────────────────────────────────────────────────────────────
out_path = os.path.join(DATA_DIR, 'questions.json')
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(questions, f, ensure_ascii=False, indent=2)

print(f"\n=======================================================")
print(f"✅ 완료: {len(questions)}개 문항 → data/questions.json")
print(f"   이미지 유형별 분포:")
for t in [1, 2, 3]:
    cnt = sum(1 for q in questions if q['image_type'] == t)
    print(f"     유형 {t}: {cnt}개")
print(f"   삼각비 유형별 분포:")
for qt in ['sin', 'cos', 'tan']:
    cnt = sum(1 for q in questions if q['question_type'] == qt)
    print(f"     {qt}: {cnt}개")
