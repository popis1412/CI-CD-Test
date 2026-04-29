import openpyxl
import os
import sys

# =========================
# 사용자 설정
# =========================
header_row = 9  # 헤더(컬럼명)가 있는 행 번호

# =========================
# 문자열 정규화 함수
# =========================
def normalize(text):
    return str(text).replace(" ", "").strip() if text else ""

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

# TC_ 시트 자동 탐색
target_sheets = [sheet for sheet in wb.sheetnames if sheet.startswith('TC_')]

if not target_sheets:
    print("[오류] 'TC_'로 시작하는 테스트 케이스 시트를 찾을 수 없습니다.")
    sys.exit(1)

# --- 통계 구조 ---
status_keys = ["Pass", "Fail", "Not Test", "Blocked"]
overall_stats = {k: 0 for k in status_keys}
overall_stats["Total"] = 0

sheet_stats = {}
category_stats = {}
defect_list = []

# =========================
# 시트 순회
# =========================
for sheet_name in target_sheets:
    ws = wb[sheet_name]

    sheet_stats[sheet_name] = {k: 0 for k in status_keys}
    sheet_stats[sheet_name]["Total"] = 0

    # -------------------------
    # 1. 헤더 기반 컬럼 찾기 (정규화 적용)
    # -------------------------
    header_map = {}

    for col in range(1, ws.max_column + 1):
        value = ws.cell(row=header_row, column=col).value
        if value:
            key = normalize(value)
            header_map[key] = col

    # 필수 컬럼 확인
    result_col = header_map.get("수행결과")
    if result_col is None:
        print(f"[경고] {sheet_name} 시트에서 '수행 결과' 컬럼을 찾을 수 없습니다.")
        continue

    # 선택 컬럼 (없어도 동작)
    cat1_col = header_map.get("대분류")
    cat2_col = header_map.get("중분류")
    action_col = header_map.get("테스트액션")

    # -------------------------
    # 2. 데이터 행 순회
    # -------------------------
    for row in range(header_row + 1, ws.max_row + 1):
        status = ws.cell(row=row, column=result_col).value
        status = normalize(status)

        if status in status_keys:
            cat1 = normalize(ws.cell(row=row, column=cat1_col).value) if cat1_col else "미분류"
            cat2 = normalize(ws.cell(row=row, column=cat2_col).value) if cat2_col else "미분류"
            action = normalize(ws.cell(row=row, column=action_col).value) if action_col else "액션 없음"

            # 전체 통계
            overall_stats["Total"] += 1
            overall_stats[status] += 1

            # 시트별 통계
            sheet_stats[sheet_name]["Total"] += 1
            sheet_stats[sheet_name][status] += 1

            # 카테고리 통계
            cat_key = (cat1, cat2, status)
            category_stats[cat_key] = category_stats.get(cat_key, 0) + 1

            # 결함 리스트
            if status == "Fail":
                defect_list.append({
                    "Sheet": sheet_name,
                    "Cat1": cat1,
                    "Cat2": cat2,
                    "Row": row,
                    "Action": action
                })

def get_pct(count, total):
    return f"{(count / total * 100):.1f}%" if total > 0 else "0.0%"

# =========================
# HTML 리포트 생성
# =========================
html_content = '''<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<title>QA 리포트</title>
</head>
<body>
<h1>QA 테스트 결과 요약</h1>
'''

html_content += f"""
<p>Total: {overall_stats['Total']}</p>
<p>Pass: {overall_stats['Pass']}</p>
<p>Fail: {overall_stats['Fail']}</p>
<p>Not Test: {overall_stats['Not Test']}</p>
<p>Blocked: {overall_stats['Blocked']}</p>
"""

html_content += "</body></html>"

with open(output_html, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"리포트 생성 완료: {output_html}")

# Jenkins용 출력
print(f"[FAIL_COUNT] {overall_stats['Fail']}")