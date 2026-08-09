import json, math

with open('data/questions.json', encoding='utf-8') as f:
    qs = json.load(f)

# T001 sinA (30° → sin=0.5)
samples = [q for q in qs if q['triangle_id']=='T001' and q['highlight_angle']=='A' and q['question_type']=='sin' and q['image_type']==1]
print('== T001, highlight A, sin, type1 ==')
for s in samples[:2]:
    print('  파일:', s['filename'])
    print('  질문:', s['question'])
    print('  선지:', s['choices'])
    correct = s['choices'][s['answer_index']]
    print('  정답:', correct)
    print('  정답값:', round(s['answer_value'],6), '(기대: 0.5)')
    print()

# T026 sinA (1,2,sqrt5 / arctan(0.5))
samples2 = [q for q in qs if q['triangle_id']=='T026' and q['image_type']==1 and q['question_type']=='tan']
print('== T026, tan, type1 샘플 2개 ==')
for s in samples2[:2]:
    print('  파일:', s['filename'])
    print('  질문:', s['question'])
    print('  선지:', s['choices'])
    print('  정답:', s['choices'][s['answer_index']])
    print()
