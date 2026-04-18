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

        stage('Generate HTML Report (Python)') {
            steps {
                echo 'Python을 사용하여 C:\\QA\\CI-CD-Test\\newman 경로에 리포트 생성 중...'
                
                // 1. 파이썬 스크립트 실행 (절대 경로에 파일 생성)
                bat 'python generate_report.py'
                
                // 2. 생성된 파일을 젠킨스에서 보여주기 위해 워크스페이스(reports)로 복사
                bat 'copy "C:\\QA\\CI-CD-Test\\newman\\QA_Automation_Report.html" "reports\\"'
                bat 'copy "C:\\QA\\CI-CD-Test\\newman\\result.txt" "reports\\"'
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
테스트가 성공적으로 완료되었습니다. (Python 리포트 생성 완료)
로컬 경로: C:\\QA\\CI-CD-Test\\newman
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