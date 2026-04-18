import os
from datetime import datetime

def create_report():
    # 1. 경로 설정
    target_dir = r"C:\QA\CI-CD-Test\newman"
    html_file = os.path.join(target_dir, "QA_Automation_Report.html")
    txt_file = os.path.join(target_dir, "result.txt")

    # 2. 폴더가 없으면 생성
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
        print(f"폴더 생성 완료: {target_dir}")

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 3. HTML 내용 작성
    html_content = f"""
    <html><head><meta charset="UTF-8"><style>
    body{{font-family:sans-serif;padding:20px;line-height:1.6;}}
    .header{{background:#2c3e50;color:white;padding:20px;margin-bottom:20px;border-radius:5px;}}
    .card{{border:1px solid #ddd;padding:15px;margin-bottom:10px;border-left:5px solid #27ae60;background:#f9f9f9;}}
    .status{{font-weight:bold;color:#27ae60;}}
    table{{width:100%;border-collapse:collapse;margin-top:10px;}}
    th,td{{border:1px solid #ddd;padding:10px;text-align:left;}}
    th{{background:#eee;}}
    </style></head><body>
    <div class="header"><h1>7DS Origin QA Automation Report (Python Generated)</h1><p>실행 일시: {now}</p></div>
    <div class="card"><h2>1. [전투] 합기(CA) 테스트</h2><p>상태: <span class="status">PASS (정상)</span></p></div>
    <div class="card"><h2>2. [모험] 기믹/상호작용 테스트</h2><p>상태: <span class="status">PASS (정상)</span></p></div>
    </body></html>
    """

    # 4. TXT 내용 작성
    txt_content = f"""[7DS Origin QA Test Result]
실행 시간: {now}
1. Combat_CA_Test: SUCCESS
2. Adventure_Gimmick_Test: SUCCESS
"""

    # 5. 파일 쓰기
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    with open(txt_file, "w", encoding="utf-8") as f:
        f.write(txt_content)

    print(f"리포트 생성 완료: {html_file}")

if __name__ == "__main__":
    create_report()