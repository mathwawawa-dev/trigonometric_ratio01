import os

with open('step1_2_edited02.py', encoding='utf-8') as f:
    src = f.read()

# 폴더명 변경
dst = src.replace("'type1_edited02'", "'type1_edited03'")
dst = dst.replace("type1_edited02/", "type1_edited03/")

# 오프셋 절반으로 축소
dst = dst.replace("-0.042 * min", "-0.021 * min")

with open('step1_2_edited03.py', 'w', encoding='utf-8') as f:
    f.write(dst)
print("Done creating step1_2_edited03.py")
