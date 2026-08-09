#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
data/questions.json → js/questionsData.js 변환
: window.QUESTIONS_DATA 전역 변수로 내장
"""
import json, os

SRC = r'C:\Users\user\Documents\삼각비 게임1\data\questions.json'
DST = r'C:\Users\user\Documents\삼각비 게임1\js\questionsData.js'

with open(SRC, 'r', encoding='utf-8') as f:
    data = json.load(f)

header = (
    "/**\n"
    " * questionsData.js — questions.json 내장 데이터\n"
    " * 이 파일은 build_questions_data.py 로 자동 생성됩니다.\n"
    f" * 문항 수: {len(data):,}개\n"
    " * 목적: file:// 프로토콜에서도 fetch 없이 동작하도록 데이터 내장\n"
    " */\n"
    "window.QUESTIONS_DATA = "
)

minified = json.dumps(data, ensure_ascii=False, separators=(',', ':'))

with open(DST, 'w', encoding='utf-8') as f:
    f.write(header + minified + ';\n')

out_size = os.path.getsize(DST)
print(f"생성 완료: {DST}")
print(f"문항 수: {len(data):,}개")
print(f"파일 크기: {out_size:,} bytes ({out_size/1024:.0f} KB)")
