import os

with open('step1_2_edited03.py', encoding='utf-8') as f:
    src = f.read()

# 폴더명 변경
dst = src.replace("'type1_edited03'", "'type1_edited04'")
dst = dst.replace("type1_edited03/", "type1_edited04/")

with open('step1_2_edited04.py', 'w', encoding='utf-8') as f:
    f.write(dst)
print("Done creating step1_2_edited04.py")
