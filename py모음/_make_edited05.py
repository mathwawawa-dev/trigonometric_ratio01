import os

with open('step1_2_edited04.py', encoding='utf-8') as f:
    src = f.read()

# 폴더명 변경
dst = src.replace("'type1_edited04'", "'type1_edited05'")
dst = dst.replace("type1_edited04/", "type1_edited05/")

with open('step1_2_edited05.py', 'w', encoding='utf-8') as f:
    f.write(dst)
print("Done creating step1_2_edited05.py")
