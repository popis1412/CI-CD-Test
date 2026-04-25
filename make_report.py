import openpyxl
import os
import sys

# 1. 실행 인자(Argument)로 BASE_PATH 전달받기
if len(sys.argv) < 2:
    print("사용법: python make_report.py [BASE_PATH_경로]")
    sys.exit(1)

base_path = sys.argv[1]
excel_path = os.path.join(base_path, 'Tests', 'QA_Test.xlsx')
output_dir = os.path.join(base_path, 'Test Results')
output_html = os.path.join(output_dir, 'qa_report.html')

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# 2. 엑셀 파일 로드
try:
    wb = openpyxl.load_workbook(excel_path, data_only=True)
except Exception as e:
    print(f"엑셀 파일 읽기 오류: {e}")
    sys.exit(1)

# [수정 포인트] 시트 이름을 직접 쓰지 않고, "TC_"로 시작하는 시트만 자동으로 추출
target_sheets = [sheet for sheet in wb.sheetnames if sheet.startswith('TC_')]

if not target_sheets:
    print("[오류] 'TC_'로 시작하는 테스트 케이스 시트를 찾을 수 없습니다.")
    sys.exit(1)

# --- 통계 저장을 위한 데이터 구조 ---
status_keys = ["Pass", "Fail", "Not Test", "Blocked"]
overall_stats = {k: 0 for k in status_keys}
overall_stats["Total"] = 0

sheet_stats = {}
category_stats = {} # {(대분류, 중분류, 현황): 개수}
defect_list = []    # Fail 결함 리스트

# 3. 발견된 대상 시트 순회 및 데이터 분석
for sheet_name in target_sheets:
    ws = wb[sheet_name]
    sheet_stats[sheet_name] = {k: 0 for k in status_keys}
    sheet_stats[sheet_name]["Total"] = 0
    
    # 행 단위 순회 (C=대분류[2], D=중분류[3], F=테스트액션[5], H=수행결과[7])
    for r_idx, row in enumerate(ws.iter_rows(min_col=1, max_col=8, values_only=True), start=1):
        status = str(row[7]).strip() if row[7] is not None else ""
        
        if status in status_keys:
            cat1 = str(row[2]).strip() if row[2] else "미분류"
            cat2 = str(row[3]).strip() if row[3] else "미분류"
            action = str(row[5]).strip() if row[5] else "액션 없음"
            
            # 전체 및 시트별 집계
            overall_stats["Total"] += 1
            overall_stats[status] += 1
            sheet_stats[sheet_name]["Total"] += 1
            sheet_stats[sheet_name][status] += 1
            
            # 대분류/중분류별 현황 누적
            cat_key = (cat1, cat2, status)
            category_stats[cat_key] = category_stats.get(cat_key, 0) + 1
            
            # 결함(Fail) 상세 정보 수집
            if status == "Fail":
                defect_list.append({
                    "Sheet": sheet_name,
                    "Cat1": cat1,
                    "Cat2": cat2,
                    "Row": r_idx,
                    "Action": action
                })

def get_pct(count, total):
    return f"{(count / total * 100):.1f}%" if total > 0 else "0.0%"

# 4. HTML 리포트 생성 (디자인 강화)
html_content = '''<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>QA 정량 분석 리포트</title>
    <style>
        body { font-family: 'Segoe UI', 'Malgun Gothic', sans-serif; margin: 40px; color: #333; background-color: #f9f9f9; }
        .container { background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 0 20px rgba(0,0,0,0.05); }
        h1 { color: #1a2a6c; border-bottom: 4px solid #1a2a6c; padding-bottom: 15px; text-align: center; }
        h2 { color: #2c3e50; margin-top: 50px; border-left: 5px solid #1a2a6c; padding-left: 15px; }
        h3 { color: #555; margin-top: 30px; }
        table { border-collapse: collapse; width: 100%; margin-bottom: 30px; border-radius: 8px; overflow: hidden; }
        th, td { border: 1px solid #eee; padding: 14px; text-align: center; }
        th { background-color: #f1f3f5; font-weight: 700; color: #444; }
        tr:hover { background-color: #f8f9fa; }
        .pass { color: #2ecc71; font-weight: bold; }
        .fail { color: #e74c3c; font-weight: bold; }
        .not-test { color: #f39c12; font-weight: bold; }
        .blocked { color: #9b59b6; font-weight: bold; }
        .total-row { background-color: #f1f5f8; font-weight: bold; }
        .defect-table { text-align: left; }
        .center { text-align: center; }
    </style>
</head>
<body>
<div class="container">
    <h1>📋 QA 테스트 결과 정량 분석 보고서</h1>
'''

# 섹션 0: 요약
html_content += f'''
    <h2>0. 테스트 요약 (Overall)</h2>
    <table>
        <tr><th>항목</th><th>카운트</th><th>비율</th></tr>
        <tr class="total-row"><td>Total Test Cases</td><td>{overall_stats['Total']}</td><td>100.0%</td></tr>
        <tr><td><span class="pass">Pass</span></td><td>{overall_stats['Pass']}</td><td>{get_pct(overall_stats['Pass'], overall_stats['Total'])}</td></tr>
        <tr><td><span class="fail">Fail</span></td><td>{overall_stats['Fail']}</td><td>{get_pct(overall_stats['Fail'], overall_stats['Total'])}</td></tr>
        <tr><td><span class="not-test">Not Test</span></td><td>{overall_stats['Not Test']}</td><td>{get_pct(overall_stats['Not Test'], overall_stats['Total'])}</td></tr>
        <tr><td><span class="blocked">Blocked</span></td><td>{overall_stats['Blocked']}</td><td>{get_pct(overall_stats['Blocked'], overall_stats['Total'])}</td></tr>
    </table>
'''

# 섹션 1: 분류별 현황
html_content += '''
    <h2>1. 대분류 / 중분류 별 테스트 현황</h2>
    <table>
        <tr><th>대분류</th><th>중분류</th><th>현황</th><th>개수</th></tr>
'''
for (cat1, cat2, status), count in sorted(category_stats.items()):
    status_class = status.lower().replace(" ", "-")
    html_content += f'<tr><td>{cat1}</td><td>{cat2}</td><td><span class="{status_class}">{status}</span></td><td>{count}</td></tr>'
html_content += '</table>'

# 섹션 2: 실패 비율
html_content += '<h2>2. 시나리오별 실패 비율</h2>'
for sheet in target_sheets:
    total = sheet_stats[sheet]['Total']
    fails = sheet_stats[sheet]['Fail']
    html_content += f'''
    <h3>📁 {sheet}</h3>
    <table>
        <tr><th>시나리오</th><th>실패 비율</th></tr>
        <tr><td>{sheet}</td><td class="fail">{get_pct(fails, total)}</td></tr>
    </table>'''

# 섹션 3: 결함 리스트
html_content += '<h2>3. 발견된 결함 상세 (Defect List)</h2>'
if not defect_list:
    html_content += '<p class="pass center">발견된 결함이 없습니다.</p>'
else:
    html_content += '''
    <table class="defect-table">
        <tr><th>No</th><th>시나리오</th><th>대분류</th><th>중분류</th><th>행</th><th>테스트 액션</th></tr>'''
    for i, defect in enumerate(defect_list, 1):
        html_content += f'''
        <tr>
            <td class="center">{i}</td>
            <td class="center">{defect['Sheet']}</td>
            <td class="center">{defect['Cat1']}</td>
            <td class="center">{defect['Cat2']}</td>
            <td class="center">{defect['Row']}</td>
            <td>{defect['Action']}</td>
        </tr>'''
    html_content += '</table>'

html_content += '</div></body></html>'

with open(output_html, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"자동 시트 탐색 리포트 생성 완료: {output_html}")

with open(output_html, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"자동 시트 탐색 리포트 생성 완료: {output_html}")

# [추가] 젠킨스에서 인식하기 쉽게 결함 개수를 표준 출력으로 내보냅니다.
print(f"[FAIL_COUNT] {overall_stats['Fail']}")