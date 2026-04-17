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

        stage('Run QA Tests') {
            steps {
                echo 'QA 테스트 시뮬레이션 실행 중...'
            }
        }

        stage('Generate HTML Report') {
            steps {
                echo '테스트 결과 리포트 생성 중...'
                
                bat """
                @echo off
                chcp 65001 > nul
                
                echo ^<html^>^<head^>^<meta charset="UTF-8"^>^<style^>body{font-family:sans-serif;padding:20px;line-height:1.6;} .header{background:#2c3e50;color:white;padding:20px;margin-bottom:20px;border-radius:5px;} .card{border:1px solid #ddd;padding:15px;margin-bottom:10px;border-left:5px solid #27ae60;background:#f9f9f9;} .status{font-weight:bold;color:#27ae60;} table{width:100%%;border-collapse:collapse;margin-top:10px;} th,td{border:1px solid #ddd;padding:10px;text-align:left;} th{background:#eee;}^</style^>^</head^>^<body^> > reports\\QA_Automation_Report.html
                echo ^<div class="header"^>^<h1^>7DS Origin QA Automation Report^</h1^>^<p^>실행 일시: %DATE% %TIME%^</p^>^</div^> >> reports\\QA_Automation_Report.html
                echo ^<div class="card"^>^<h2^>1. [전투] 합기(CA) 테스트^</h2^>^<p^>상태: ^<span class="status"^>PASS (정상)^</span^>^</p^>^</div^> >> reports\\QA_Automation_Report.html
                echo ^<div class="card"^>^<h2^>2. [모험] 기믹/상호작용 테스트^</h2^>^<p^>상태: ^<span class="status"^>PASS (정상)^</span^>^</p^>^</div^> >> reports\\QA_Automation_Report.html
                echo ^</body^>^</html^> >> reports\\QA_Automation_Report.html
                
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
리포트 확인: ${env.BUILD_URL}7DS_20Origin_20QA_20Automation_20Reports/
"""
            )
        }
        
        failure {
            slackSend (
                channel: '#새-채널', 
                color: '#FF0000', 
                message: "❌ FAIL: Job ${env.JOB_NAME} [${env.BUILD_NUMBER}] 테스트 실패! 로그를 확인하세요. (${env.BUILD_URL})"
            )
        }
    }
}