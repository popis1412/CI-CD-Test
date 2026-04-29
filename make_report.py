import openpyxl
import os
import sys

# =========================
# 사용자 설정
# =========================
header_row = 9  # 헤더(컬럼명) 행 번호

# =========================
# 문자열 정규화
# =========================
def normalize(text):
    return str(text).replace(" ", "").strip() if text else ""

# 실행 인자
if len(sys.argv) < 2:
    print("사용법: python make_report.py [BASE_PATH_경로]")
    sys.exit(1)

base_path = sys.argv[1]
excel_path = os.path.join(base_path, 'Tests', 'QA_Test.xlsx')
output_dir = os.path.join(base_path, 'Test Results')
output_html = os.path.join(output_dir, 'qa_report.html')

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# 엑셀 로드
wb = openpyxl.load_workbook(excel_path, data_only=True)

# TC_ 시트 자동 탐색
target_sheets = [s for s in wb.sheetnames if s.startswith('TC_')]
if not target_sheets:
    print("[오류] TC_ 시트 없음")
    sys.exit(1)

# 통계 구조
status_keys = ["Pass", "Fail", "Not Test", "Blocked"]
overall_stats = {k: 0 for k in status_keys}
overall_stats["Total"] = 0

sheet_stats = {}
category_stats = {}
defect_list = []

# =========================
# 시트 처리
# =========================
for sheet_name in target_sheets:
    ws = wb[sheet_name]

    sheet_stats[sheet_name] = {k: 0 for k in status_keys}
    sheet_stats[sheet_name]["Total"] = 0

    # 헤더 탐색
    header_map = {}
    for col in range(1, ws.max_column + 1):
        val = ws.cell(row=header_row, column=col).value
        if val:
            header_map[normalize(val)] = col

    result_col = header_map.get("수행결과")
    cat1_col = header_map.get("대분류")
    cat2_col = header_map.get("중분류")
    action_col = header_map.get("테스트액션")

    if not result_col:
        print(f"[경고] {sheet_name}: 수행결과 컬럼 없음")
        continue

    # 데이터 처리
    for row in range(header_row + 1, ws.max_row + 1):
        status = normalize(ws.cell(row=row, column=result_col).value)

        if status in status_keys:
            cat1 = normalize(ws.cell(row=row, column=cat1_col).value) if cat1_col else "미분류"
            cat2 = normalize(ws.cell(row=row, column=cat2_col).value) if cat2_col else "미분류"
            action = normalize(ws.cell(row=row, column=action_col).value) if action_col else "액션 없음"

            overall_stats["Total"] += 1
            overall_stats[status] += 1

            sheet_stats[sheet_name]["Total"] += 1
            sheet_stats[sheet_name][status] += 1

            key = (cat1, cat2, status)
            category_stats[key] = category_stats.get(key, 0) + 1

            if status == "Fail":
                defect_list.append({
                    "Sheet": sheet_name,
                    "Cat1": cat1,
                    "Cat2": cat2,
                    "Row": row,
                    "Action": action
                })

def get_pct(c, t):
    return f"{(c/t*100):.1f}%" if t else "0.0%"

# =========================
# HTML 리포트 (원래 섹션 유지)
# =========================
html_content = '''<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<title>QA 정량 분석 리포트</title>
<style>
body { font-family: sans-serif; margin: 40px; }
table { border-collapse: collapse; width: 100%; }
th, td { border: 1px solid #ccc; padding: 10px; text-align: center; }
.pass { color: green; }
.fail { color: red; }
.not-test { color: orange; }
.blocked { color: purple; }
</style>
</head>
<body>
<h1>QA 테스트 결과 리포트</h1>
'''

# 섹션 0
html_content += f'''
<h2>0. 전체 요약</h2>
<table>
<tr><th>항목</th><th>수치</th><th>비율</th></tr>
<tr><td>Total</td><td>{overall_stats['Total']}</td><td>100%</td></tr>
<tr><td class="pass">Pass</td><td>{overall_stats['Pass']}</td><td>{get_pct(overall_stats['Pass'], overall_stats['Total'])}</td></tr>
<tr><td class="fail">Fail</td><td>{overall_stats['Fail']}</td><td>{get_pct(overall_stats['Fail'], overall_stats['Total'])}</td></tr>
<tr><td class="not-test">Not Test</td><td>{overall_stats['Not Test']}</td><td>{get_pct(overall_stats['Not Test'], overall_stats['Total'])}</td></tr>
<tr><td class="blocked">Blocked</td><td>{overall_stats['Blocked']}</td><td>{get_pct(overall_stats['Blocked'], overall_stats['Total'])}</td></tr>
</table>
'''

# 섹션 1
html_content += '''
<h2>1. 분류별 현황</h2>
<table>
<tr><th>대분류</th><th>중분류</th><th>상태</th><th>개수</th></tr>
'''
for (c1, c2, st), cnt in category_stats.items():
    html_content += f"<tr><td>{c1}</td><td>{c2}</td><td>{st}</td><td>{cnt}</td></tr>"
html_content += "</table>"

# 섹션 2
html_content += '<h2>2. 시트별 실패율</h2>'
for s in target_sheets:
    total = sheet_stats[s]["Total"]
    fail = sheet_stats[s]["Fail"]
    html_content += f"<p>{s}: {get_pct(fail, total)}</p>"

# 섹션 3
html_content += '<h2>3. 결함 리스트</h2>'
if not defect_list:
    html_content += "<p>결함 없음</p>"
else:
    html_content += "<table><tr><th>No</th><th>Sheet</th><th>행</th><th>내용</th></tr>"
    for i, d in enumerate(defect_list, 1):
        html_content += f"<tr><td>{i}</td><td>{d['Sheet']}</td><td>{d['Row']}</td><td>{d['Action']}</td></tr>"
    html_content += "</table>"

html_content += "</body></html>"

# 저장
with open(output_html, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"리포트 생성 완료: {output_html}")
print(f"[FAIL_COUNT] {overall_stats['Fail']}")