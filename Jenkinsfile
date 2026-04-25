pipeline {
    agent any

    parameters {
        string(name: 'BASE_PATH', defaultValue: 'C:\\QA\\CI-CD-Test', description: '기본 경로')
    }

    environment {
        RESULT_DIR = "${params.BASE_PATH}\\Test Results"
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
                        error "[ERR-PATH-001] 경로 생성 실패: ${RESULT_DIR}"
                    }
                }
            }
        }

        stage('QA Analysis') {
            steps {
                script {
                    def failItems = []

                    for (int i=1; i<=100; i++) {
                        if (i == 15 || i == 42 || i == 77 || i == 82) {
                            failItems << "TC-${i}"
                        }
                    }

                    writeFile file: "${RESULT_DIR}\\report.html", text: "QA REPORT"

                    if (failItems.size() > 0) {
                        def msg = "❌ QA 실패\n경로: ${RESULT_DIR}\n"
                        failItems.each {
                            msg += "- 실패: ${it}\n"
                        }

                        env.SLACK_FAIL_MSG = msg
                        error "[ERR-QA-002] QA 실패"
                    } else {
                        env.SLACK_SUCCESS_MSG = "✅ QA 성공\n경로: ${RESULT_DIR}"
                    }
                }
            }
        }

        stage('GitHub Update') {
            steps {
                script {
                    bat 'git config user.email "jenkins@example.com"'
                    bat 'git config user.name "Jenkins CI"'
                    bat "git add \"${RESULT_DIR}\\report.html\""
                    bat 'git commit -m "QA report"'
                    bat 'git push origin HEAD'
                }
            }
        }
    }

    post {

        always {
            echo "항상 실행"
        }

        success {
            slackSend (
                channel: '#qa-alert',
                color: '#00FF00',
                message: env.SLACK_SUCCESS_MSG ?: "성공"
            )
        }

        failure {
            slackSend (
                channel: '#qa-alert',
                color: '#FF0000',
                message: env.SLACK_FAIL_MSG ?: "실패"
            )
        }
    }
}