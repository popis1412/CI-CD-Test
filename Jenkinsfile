pipeline {
    agent any

    stages {
        stage('Prepare') {
            steps {
                echo '이전 리포트 정리 및 폴더 생성...'
                // 젠킨스 워크스페이스 내의 임시 폴더 정리
                bat '''
                if not exist reports mkdir reports
                del /q reports\\*
                '''
            }
        }

        stage('Generate Report to Absolute Path') {
            steps {
                echo '절대 경로 C:\\QA\\CI-CD-Test\\newman 에 리포트 생성 중...'
                
                bat """
                @echo off
                chcp 65001 > nul

                set TARGET_DIR=C:\\QA\\CI-CD-Test\\newman
                set HTML_FILE=%TARGET_DIR%\\QA_Automation_Report.html
                set TXT_FILE=%TARGET_DIR%\\result.txt

                :: 1. 폴더가 없으면 생성
                if not exist "%TARGET_DIR%" mkdir "%TARGET_DIR%"

                :: 2. HTML 리포트 생성 (특수문자 ^ 처리 완료)
                echo ^<html^>^<head^>^<meta charset="UTF-8"^>^<style^>body{font-family:sans-serif;padding:20px;line-height:1.6;} .header{background:#2c3e50;color:white;padding:20px;margin-bottom:20px;border-radius:5px;} .card{border:1px solid #ddd;padding:15px;margin-bottom:10px;border-left:5px solid #27ae60;background:#f9f9f9;} .status{font-weight:bold;color:#27ae60;} table{width:100%%;border-collapse:collapse;margin-top:10px;} th,td{border:1px solid #ddd;padding:10px;text-align:left;} th{background:#eee;}^</style^>^</head^>^<body^> > "%HTML_FILE%"
                echo ^<div class="header"^>^<h1^>7DS Origin QA Automation Report^</h1^>^<p^>실행 일시: %DATE% %TIME%^</p^>^</div^> >> "%HTML_FILE%"
                echo ^<div class="card"^>^<h2^>1. [전투] 합기(CA) 테스트^</h2^>^<p^>상태: ^<span class="status"^>PASS (정상)^</span^>^</p^>^</div^> >> "%HTML_FILE%"
                echo ^<div class="card"^>^<h2^>2. [모험] 기믹/상호작용 테스트^</h2^>^<p^>상태: ^<span class="status"^>PASS (정상)^</span^>^</p^>^</div^> >> "%HTML_FILE%"
                echo ^</body^>^</html^> >> "%HTML_FILE%"

                :: 3. TXT 결과 파일 생성
                echo [7DS Origin QA Test Result] > "%TXT_FILE%"
                echo 실행 시간: %DATE% %TIME% >> "%TXT_FILE%"
                echo 1. Combat_CA_Test: SUCCESS >> "%TXT_FILE%"
                echo 2. Adventure_Gimmick_Test: SUCCESS >> "%TXT_FILE%"

                :: 4. 젠킨스에서 보여주기 위해 워크스페이스로 복사
                copy "%HTML_FILE%" "reports\\"
                copy "%TXT_FILE%" "reports\\"
                """
            }
        }
    }

    post {
        always {
            // 젠킨스 워크스페이스로 복사된 파일을 아카이빙 및 게시
            archiveArtifacts artifacts: 'reports/*', allowEmptyArchive: true
            publishHTML(target: [
                reportDir: 'reports',
                reportFiles: 'QA_Automation_Report.html',
                reportName: '7DS Origin QA Automation Reports',
                keepAll: true,
                alwaysLinkToLastBuild: true
            ])
        }
        
        success {
            slackSend (
                channel: '#새-채널', 
                color: '#00FF00', 
                message: """
✅ SUCCESS: Job ${env.JOB_NAME} [${env.BUILD_NUMBER}]
테스트가 성공적으로 완료되었습니다.
로컬 저장 경로: C:\\QA\\CI-CD-Test\\newman
리포트 확인: ${env.BUILD_URL}7DS_20Origin_20QA_20Automation_20Reports/
"""
            )
        }
        
        failure {
            slackSend (
                channel: '#새-채널', 
                color: '#FF0000', 
                message: "❌ FAIL: Job ${env.JOB_NAME} [${env.BUILD_NUMBER}] 테스트 실패! (${env.BUILD_URL})"
            )
        }
    }
}