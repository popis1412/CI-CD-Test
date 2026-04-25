pipeline {
    agent any

    parameters {
        string(name: 'BASE_PATH', defaultValue: '', description: '기본 경로')
    }

    environment {
        RESULT_DIR = "${params.BASE_PATH}\\Test Results"
        SLACK_CHANNEL = "#새-채널"
        SLACK_LINK = "https://test-npo3457.slack.com/app_redirect?channel=새-채널"
    }

    stages {

        stage('Prepare') {
            steps {
                script {
                    try {
                        bat """
                        if not exist "${RESULT_DIR}" (
                            mkdir "${RESULT_DIR}"
                        )
                        """

                        bat "del /q \"${RESULT_DIR}\\*\""

                    } catch (Exception e) {
                        error "[ERR-PATH-001] 경로를 찾을 수 없습니다: ${RESULT_DIR}"
                    }
                }
            }
        }

        stage('QA Analysis') {
            steps {
                script {

                    def startTime = System.currentTimeMillis()
                    def failItems = []

                    // 테스트 시뮬레이션
                    for (int i=1; i<=100; i++) {
                        if (i == 15) failItems << "[ERR-TAG-102] 캐릭터 교체 오류 (15행)"
                        if (i == 42) failItems << "[ERR-SKL-205] 스킬 버프 소실 (42행)"
                        if (i == 77) failItems << "[ERR-SYS-501] 입력 무시 (77행)"
                        if (i == 82) failItems << "[ERR-MEM-909] 리소스 오류 (82행)"
                    }

                    def htmlPath = "${RESULT_DIR}\\7DS_QA_Report.html"

                    writeFile file: htmlPath, text: """
                    <html>
                    <body>
                        <h1>QA REPORT</h1>
                        <p>경로: ${RESULT_DIR}</p>
                        <p>시간: ${new Date()}</p>
                    </body>
                    </html>
                    """

                    if (failItems.size() > 0) {

                        def msg = """
❌ [ERR-QA-002] QA 테스트 실패

📂 결과 경로:
${RESULT_DIR}

🔗 Slack 채널 바로가기:
${SLACK_LINK}

🎯 실패 상세:
${failItems.collect { "- ${it}\n  ▶ 액션: 해당 로직 및 상태 전이 확인 필요" }.join("\n\n")}

⚠️ 조치 필요: 수정 후 재빌드
"""

                        env.SLACK_FAIL_MSG = msg
                        error "[ERR-QA-002] QA 테스트 실패 발생"

                    } else {

                        env.SLACK_SUCCESS_MSG = """
✅ QA 테스트 통과

📂 결과 경로:
${RESULT_DIR}

🔗 채널 이동:
${SLACK_LINK}
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
                        bat "git add \"${RESULT_DIR}\\7DS_QA_Report.html\""
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
                reportDir: "${RESULT_DIR}",
                reportFiles: '7DS_QA_Report.html',
                reportName: 'QA Report',
                keepAll: true,
                alwaysLinkToLastBuild: true
            ])
        }

        success {
            slackSend (
                channel: "${SLACK_CHANNEL}",
                color: '#00FF00',
                message: "✅ 빌드 성공\n${env.SLACK_SUCCESS_MSG}"
            )
        }

        failure {
            slackSend (
                channel: "${SLACK_CHANNEL}",
                color: '#FF0000',
                message: "@here ${env.SLACK_FAIL_MSG ?: "❌ [ERR-UNKNOWN-999] 알 수 없는 오류 발생"}"
            )
        }
    }
}