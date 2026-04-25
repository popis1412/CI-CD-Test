pipeline {
    agent any

    parameters {
        string(name: 'BASE_PATH', defaultValue: '', description: '기본 경로 (비워두면 기본 경로 사용)')
    }

    environment {
        DEFAULT_PATH = "C:\\QA\\CI-CD-Test"
    }

    stages {

        stage('Prepare') {
            steps {
                script {
                    try {
                        // 경로 결정 (빈 값이면 기본 경로 사용)
                        def basePath = params.BASE_PATH?.trim() ? params.BASE_PATH : env.DEFAULT_PATH
                        env.RESULT_DIR = "${basePath}\\Test Results"

                        bat """
                        if not exist "${env.RESULT_DIR}" (
                            mkdir "${env.RESULT_DIR}"
                        )
                        """

                        bat "del /q \"${env.RESULT_DIR}\\*\""

                    } catch (Exception e) {
                        error "[ERR-PATH-001] 경로를 찾을 수 없습니다: ${env.RESULT_DIR}"
                    }
                }
            }
        }

        stage('QA Analysis') {
            steps {
                script {

                    def failItems = []

                    for (int i=1; i<=100; i++) {
                        if (i == 15) failItems << "[ERR-TAG-102] 캐릭터 교체 오류 (15행)"
                        if (i == 42) failItems << "[ERR-SKL-205] 스킬 버프 소실 (42행)"
                        if (i == 77) failItems << "[ERR-SYS-501] 입력 무시 (77행)"
                        if (i == 82) failItems << "[ERR-MEM-909] 리소스 오류 (82행)"
                    }

                    def htmlPath = "${env.RESULT_DIR}\\7DS_QA_Report.html"

                    writeFile file: htmlPath, text: """
                    <html>
                    <body>
                        <h1>QA REPORT</h1>
                        <p>경로: ${env.RESULT_DIR}</p>
                        <p>시간: ${new Date()}</p>
                    </body>
                    </html>
                    """

                    if (failItems.size() > 0) {

                        def msg = """
❌ [ERR-QA-002] QA 테스트 실패

📂 결과 경로:
${env.RESULT_DIR}

🎯 실패 상세:
${failItems.collect { "- ${it}\n  ▶ 액션: 로직 확인 필요" }.join("\n\n")}
"""

                        env.SLACK_FAIL_MSG = msg
                        error "[ERR-QA-002] QA 테스트 실패 발생"

                    } else {

                        env.SLACK_SUCCESS_MSG = """
✅ QA 테스트 통과

📂 결과 경로:
${env.RESULT_DIR}
"""
                    }
                }
            }
        }

        stage('GitHub Update') {
            steps {
                script {
                    try {
                        bat 'git config user.email "jenkins@example.com"'
                        bat 'git config user.name "Jenkins CI"'
                        bat "git add \"${env.RESULT_DIR}\\7DS_QA_Report.html\""
                        bat 'git commit -m "QA_Report_Auto_Update"'
                        bat 'git push origin HEAD'
                    } catch (Exception e) {
                        error "[ERR-GIT-003] Git 업로드 실패"
                    }
                }
            }
        }
    }

    post {

        always {
            publishHTML(target: [
                reportDir: "${env.RESULT_DIR}",
                reportFiles: '7DS_QA_Report.html',
                reportName: 'QA Report',
                keepAll: true,
                alwaysLinkToLastBuild: true
            ])
        }

        success {
            slackSend (
                channel: "#새-채널",
                color: '#00FF00',
                message: env.SLACK_SUCCESS_MSG ?: "빌드 성공"
            )
        }

        failure {
            slackSend (
                channel: "#새-채널",
                color: '#FF0000',
                message: env.SLACK_FAIL_MSG ?: "빌드 실패"
            )
        }
    }
}