# ================================
# UTF-8 출력 설정
# ================================
import sys
try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

# ================================
# 표준 라이브러리만 사용
# ================================
from http.server import HTTPServer, BaseHTTPRequestHandler
import os
import csv
import subprocess
from urllib.parse import urlparse

# ================================
# ✔ 설정 영역 (직접 수정)
# ================================

# // 예시: 엑셀에서 열 수 있는 CSV 파일 경로
FILE_PATH = r"C:\QA\CI-CD-Test\Test Results\result.csv"

# // 예시: 확인할 PID 직접 입력
pid = 132

# ================================
# 폴더 자동 생성
# ================================
os.makedirs(os.path.dirname(FILE_PATH), exist_ok=True)


# ================================
# PID 실행 확인 // 나중에 자동으로 PID를 가져오는 것으로 고칠 예정
# ================================
def check_pid_running(pid):
    try:
        result = subprocess.run(
            ["tasklist", "/FI", f"PID eq {pid}"],
            capture_output=True,
            text=True
        )

        return str(pid) in result.stdout
    except Exception as e:
        print(f"PID 확인 오류: {e}")
        return False


# ================================
# PASS 기록 (엑셀에서 바로 열림)
# ================================
def write_result():
    with open(FILE_PATH, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["PASS"])


# ================================
# HTML UI
# ================================
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Mock Steam Purchase</title>
</head>
<body style="background-color:#1b2838; color:white; font-family:sans-serif;">
    <h2>가짜 Steam 결제 페이지</h2>

    <div style="border:1px solid #555; padding:20px; width:300px;">
        <p>상품: SSR 무기 선택 패키지</p>
        <p>가격: ₩1,200</p>

        <form method="POST" action="/purchase">
            <button type="submit" style="padding:10px; background-color:green; color:white;">
                구매
            </button>
        </form>
    </div>
</body>
</html>
"""


# ================================
# 웹 서버 핸들러
# ================================
class MyHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(HTML_PAGE.encode("utf-8"))

    def do_POST(self):
        if self.path == "/purchase":

            if check_pid_running(pid):
                print("실행 중입니다", flush=True)
            else:
                print("실행 중이 아닙니다", flush=True)

            write_result()

            response = """
            <html>
            <head><meta charset="UTF-8"></head>
            <body>
                <h3 style="color:green;">결제 성공 (Mock) - PASS 기록 완료</h3>
            </body>
            </html>
            """

            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(response.encode("utf-8"))


# ================================
# 서버 실행
# ================================
if __name__ == "__main__":
    server = HTTPServer(("127.0.0.1", 5000), MyHandler)

    print("서버 실행 중: http://127.0.0.1:5000", flush=True)

    server.serve_forever()