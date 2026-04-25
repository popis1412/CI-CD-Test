pipeline {
    agent any

    stages {
        stage('Prepare') {
            steps {
                echo '이전 리포트 정리 및 폴더 생성...'
                bat '''
                if not exist reports mkdir reports
                del /q reports\\*
                '''
            }
        }

        stage('Generate Tag Battle QA Report') {
            steps {
                echo '태그 전투 시스템 QA 리포트 생성 중...'
                
                bat """
                @echo off
                chcp 65001 > nul

                set TARGET_DIR=C:\\QA\\CI-CD-Test\\newman
                set HTML_FILE=%TARGET_DIR%\\Tag_Battle_QA_Report.html

                :: [데이터 설정] 각 분류별 정량적 지표 (이 수치들을 자동화 결과에 따라 변경하게 됨)
                :: 1. 기능 테스트 (총 5개 항목)
                set /a f_total=5, f_pass=4, f_fail=1, f_defect=1
                :: 2. 전투 연계 (총 3개 항목)
                set /a c_total=3, c_pass=3, c_fail=0, f_defect2=0
                :: 3. 예외 상황 (총 3개 항목)
                set /a e_total=3, e_pass=2, e_fail=1, f_defect3=2
                :: 4. UX/피드백 (총 3개 항목)
                set /a u_total=3, u_pass=3, u_fail=0, f_defect4=0

                :: 폴더 생성
                if not exist "%TARGET_DIR%" mkdir "%TARGET_DIR%"

                :: HTML 헤더 및 스타일 작성
                echo ^<html^>^<head^>^<meta charset="UTF-8"^> > "%HTML_FILE%"
                echo ^<style^> >> "%HTML_FILE%"
                echo body{font-family:'Malgun Gothic',sans-serif;padding:20px;line-height:1.6;background:#f4f7f6;} >> "%HTML_FILE%"
                echo .header{background:#2c3e50;color:white;padding:20px;margin-bottom:20px;border-radius:5px;text-align:center;} >> "%HTML_FILE%"
                echo .summary-table{width:100%%;border-collapse:collapse;margin-bottom:30px;background:white;box-shadow:0 2px 5px rgba(0,0,0,0.1);} >> "%HTML_FILE%"
                echo .summary-table th, .summary-table td{border:1px solid #ddd;padding:12px;text-align:center;} >> "%HTML_FILE%"
                echo .summary-table th{background:#ecf0f1;font-weight:bold;} >> "%HTML_FILE%"
                echo .status-pass{color:#27ae60;font-weight:bold;} >> "%HTML_FILE%"
                echo .status-fail{color:#e74c3c;font-weight:bold;} >> "%HTML_FILE%"
                echo .card{background:white;border-radius:5px;padding:15px;margin-bottom:15px;border-left:5px solid #3498db;box-shadow:0 1px 3px rgba(0,0,0,0.1);} >> "%HTML_FILE%"
                echo .priority-critical{background:#ffeded;color:#c0392b;padding:2px 6px;border-radius:3px;font-size:0.8em;font-weight:bold;} >> "%HTML_FILE%"
                echo ^</style^>^</head^>^<body^> >> "%HTML_FILE%"

                :: 리포트 제목
                echo ^<div class="header"^>^<h1^>태그 전투 시스템 QA 분석 리포트^</h1^>^<p^>테스트 차수: 정기 배포 전 수시 점검 ^| 실행: %DATE% %TIME%^</p^>^</div^> >> "%HTML_FILE%"

                :: [정량적 지표 섹션]
                echo ^<h2^>1. 테스트 결과 요약 (정량 지표)^</h2^> >> "%HTML_FILE%"
                echo ^<table class="summary-table"^> >> "%HTML_FILE%"
                echo ^<tr^>^<th^>대분류^</th^>^<th^>시나리오 수^</th^>^<th^>성공^</th^>^<th^>실패^</th^>^<th^>실패율(%%)^</th^>^<th^>발견 결함^</th^^></tr^> >> "%HTML_FILE%"
                
                :: 각 행 계산 및 작성 (실패율 예시 계산: 실패*100/전체)
                echo ^<tr^>^<td^>1. 기능 테스트^</td^>^<td^>%f_total%^</td^>^<td^>%f_pass%^</td^>^<td class="status-fail"^>%f_fail%^</td^>^<td^>20%%^</td^>^<td^>%f_defect%^</td^^></tr^> >> "%HTML_FILE%"
                echo ^<tr^>^<td^>2. 전투 연계 테스트^</td^>^<td^>%c_total%^</td^>^<td^>%c_pass%^</td^>^<td^>%c_fail%^</td^>^<td^>0%%^</td^>^<td^>%f_defect2%^</td^^></tr^> >> "%HTML_FILE%"
                echo ^<tr^>^<td^>3. 예외 상황 테스트^</td^>^<td^>%e_total%^</td^>^<td^>%e_pass%^</td^>^<td class="status-fail"^>%e_fail%^</td^>^<td^>33%%^</td^>^<td^>%f_defect3%^</td^^></tr^> >> "%HTML_FILE%"
                echo ^<tr^>^<td^>4. UX / 피드백 테스트^</td^>^<td^>%u_total%^</td^>^<td^>%u_pass%^</td^>^<td^>%u_fail%^</td^>^<td^>0%%^</td^>^<td^>%f_defect4%^</td^^></tr^> >> "%HTML_FILE%"
                echo ^</table^> >> "%HTML_FILE%"

                :: [세부 실패 시나리오 분석]
                echo ^<h2^>2. 상세 실패 시나리오 및 결함^</h2^> >> "%HTML_FILE%"
                
                echo ^<div class="card"^>^<span class="priority-critical"^>1순위 (Critical)^</span^> >> "%HTML_FILE%"
                echo ^<h3^>[기능] 캐릭터 상태(넉백, 피격 등)에 따른 교체 가능 여부 확인^</h3^> >> "%HTML_FILE%"
                echo ^<p^>결과: ^<span class="status-fail"^>FAILED^</span^> (이유: 피격 애니메이션 중 교체 입력 무시 현상 발생)^</p^> >> "%HTML_FILE%"
                echo ^<p^>관련 결함: [BUG-1021] 피격 상태 프레임 태그 인터럽트 불가^</p^>^</div^> >> "%HTML_FILE%"

                echo ^<div class="card"^>^<h3^>[예외] 스킬 사용 중 교체 시 충돌 여부^</h3^> >> "%HTML_FILE%"
                echo ^<p^>결과: ^<span class="status-fail"^>FAILED^</span^> (이유: 특정 광역기 사용 중 교체 시 캐릭터 증발)^</p^> >> "%HTML_FILE%"
                echo ^<p^>관련 결함: [BUG-1025] 스킬 리소스 해제 전 캐릭터 스왑 시 널 참조 에러^</p^>^</div^> >> "%HTML_FILE%"

                echo ^<h2^>3. 테스트 환경^</h2^> >> "%HTML_FILE%"
                echo ^<ul^>^<li^>AOS: 갤럭시 S20^</li^>^<li^>iOS: iPhone 12 Pro^</li^>^<li^>PC: i5 / 16GB^</li^^></ul^> >> "%HTML_FILE%"

                echo ^</body^>^</html^> >> "%HTML_FILE%"

                :: 젠킨스 워크스페이스로 복사
                copy "%HTML_FILE%" "reports\\"
                """
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'reports/*', allowEmptyArchive: true
            publishHTML(target: [
                reportDir: 'reports',
                reportFiles: 'Tag_Battle_QA_Report.html',
                reportName: 'Tag Battle QA Analysis Report',
                keepAll: true,
                alwaysLinkToLastBuild: true
            ])
        }
        
        success {
            slackSend (
                channel: '#qa-alert', 
                color: '#00FF00', 
                message: """
✅ 태그 전투 시스템 테스트 완료
- 전체 시나리오 중 성공률: 85%
- 미결함 버그: 3건 (Critical 1건 포함)
리포트 확인: ${env.BUILD_URL}Tag_20Battle_20QA_20Analysis_20Report/
"""
            )
        }
        
        failure {
            slackSend (
                channel: '#qa-alert', 
                color: '#FF0000', 
                message: "❌ 태그 전투 시스템 테스트 실패! 빌드 상태를 확인하세요. (${env.BUILD_URL})"
            )
        }
    }
}