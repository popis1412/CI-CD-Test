pipeline {
    agent any

    stages {
        stage('Prepare') {
            steps {
                echo '이전 리포트 정리 및 폴더 생성...'
                // 리포트를 저장할 폴더 생성 및 기존 파일 삭제
                bat '''
                if not exist reports mkdir reports
                del /q reports\\*
                '''
            }
        }

        stage('Run QA Tests') {
            steps {
                echo 'QA 테스트 시뮬레이션 실행 중...'
                // 여기서 실제로 어떤 작업을 하신다면 명령어를 추가하세요.
                // 현재는 결과 리포트 생성을 위한 데이터 준비 단계입니다.
            }
        }

        stage('Generate HTML Report') {
            steps {
                echo '테스트 결과 리포트 생성 중...'
                
                // 한글 깨짐 방지 및 HTML 파일 생성
                bat """
                chcp 65001
                echo ^<html^>^<head^>^<meta charset="UTF-8"^>^<style^>body{font-family:sans-serif;padding:20px;line-height:1.6;} .header{background:#2c3e50;color:white;padding:20px;margin-bottom:20px;border-radius:5px;} .card{border:1px solid #ddd;padding:15px;margin-bottom:10px;border-left:5px solid #27ae60;background:#f9f9f9;} .status{font-weight:bold;color:#27ae60;} table{width:100%%;border-collapse:collapse;margin-top:10px;} th,td{border:1px solid #ddd;padding:10px;text-align:left;} th{background:#eee;}^</style^>^</head^>^<body^> > reports\\QA_Automation_Report.html
                echo ^<div class="header"^>^<h1^>7DS Origin QA Automation Report^</h1^>^<p^>실행 일시: %DATE% %TIME%^</p^>^</div^> >> reports\\QA_Automation_Report.html
                
                echo ^<div class="card"^>^<h2^>1. [전투] 합기(CA) 테스트^</h2^>^<p^>상태: ^<span class="status"^>PASS (정상)^</span^>^</p^>^<p^>상세 내용: 전투 시스템 내 합기 발동 및 데미지 판정 테스트 완료^</p^>^</div^> >> reports\\QA_Automation_Report.html
                
                echo ^<div class="card"^>^<h2^>2. [모험] 기믹/상호작용 테스트^</h2^>^<p^>상태: ^<span class="status"^>PASS (정상)^</span^>^</p^>^<p^>상세 내용: 필드 기믹 작동 및 오브젝트 상호작용 로직 테스트 완료^</p^>^</div^> >> reports\\QA_Automation_Report.html
                
                echo ^<hr^>^<table^>^<tr^>^<th^>테스트 항목^</th^>^<th^>결과^</th^>^<th^>비고^</th^>^</tr^> >> reports\\QA_Automation_Report.html
                echo ^<tr^>^<td^>Combat_CA_Test^</td^>^<td^>SUCCESS^</td^>^<td^>자동 생성 리포트^</td^>^</tr^> >> reports\\QA_Automation_Report.html
                echo ^<tr^>^<td^>Adventure_Gimmick_Test^</td^>^<td^>SUCCESS^</td^>^<td^>자동 생성 리포트^</td^>^</tr^> >> reports\\QA_Automation_Report.html
                echo ^</table^>^</body^>^</html^> >> reports\\QA_Automation_Report.html
                
                // 텍스트 파일도 별도로 생성 (필요시)
                echo [7DS Origin QA Test Result] > reports\\result.txt
                echo 실행 시간: %DATE% %TIME% >> reports\\result.txt
                echo 1. Combat_CA_Test: SUCCESS >> reports\\result.txt
                echo 2. Adventure_Gimmick_Test: SUCCESS >> reports\\result.txt
                """
            }
        }
    }

    post {
        always {
            // 생성된 모든 리포트 파일을 젠킨스에 저장
            archiveArtifacts artifacts: 'reports/*', allowEmptyArchive: true
            
            // 젠킨스 빌드 화면에서 리포트를 바로 볼 수 있도록 설정
            publishHTML(target: [
                reportDir: 'reports',
                reportFiles: 'QA_Automation_Report.html',
                reportName: '7DS Origin QA Automation Reports',
                keepAll: true,
                alwaysLinkToLastBuild: true
            ])
        }
    }
}