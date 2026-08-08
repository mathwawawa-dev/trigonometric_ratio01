src = open('step1_2_edited01.py', encoding='utf-8').read()
dst = src.replace("'type1_edited01'", "'type1_edited02'").replace('type1_edited01/', 'type1_edited02/')
open('step1_2_edited02.py', 'w', encoding='utf-8').write(dst)
print('Done')
