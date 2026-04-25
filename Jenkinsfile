pipeline {
    agent any

    parameters {
        string(name: 'BASE_PATH', defaultValue: 'C:\\QA\\CI-CD-Test', description: '기본 경로 입력')
    }

    environment {
        RESULT_DIR = "${params.BASE_PATH}\\Test Results"
    }

    stages {

        stage('Prepare') {
            steps {
                script {
                    try {
                        // 경로 체크 및 생성
                        bat """
                        if not exist "${RESULT_DIR}" (
                            mkdir "${RESULT_DIR}"
                        )
                        """

                        // 기존 파일 삭제
                        bat "del /q \"${RESULT_DIR}\\*\""

                    } catch (Exception e) {
                        error "[ERR-PATH-001] 지정된 경로를 찾을 수 없습니다: ${RESULT_DIR}"
                    }
                }
            }
        }

        stage('QA Analysis') {
            steps {
                script {
                    def startTime = System.currentTimeMillis()
                    def startDateTime = new Date().format('yyyy-MM-dd HH:mm:ss')

                    def testResults = []

                    for(int i=1; i<=100; i++) {
                        def category = ""
                        if(i <= 30) category = "기능: 캐릭터 교체 시스템"
                        else if(i <= 60) category = "전투: 태그 스킬 및 연계"
                        else if(i <= 85) category = "시스템: 예외 상황 처리"
                        else category = "UX: 카메라 및 UI 피드백"

                        def result = "Pass"
                        def errorCode = ""

                        if(i == 15) { result = "Fail"; errorCode = "[ERR-TAG-102] 캐릭터 교체 시 무적 프레임 미적용" }
                        if(i == 42) { result = "Fail"; errorCode = "[ERR-SKL-205] 태그 스킬 발동 시 버프 소실" }
                        if(i == 77) { result = "Fail"; errorCode = "[ERR-SYS-501] 에어본 상태 입력 무시" }
                        if(i == 82) { result = "Fail"; errorCode = "[ERR-MEM-909] 리소스 참조 오류" }

                        if(i > 95) result = "Not Test"

                        testResults << [row: i + 1, col: "H", category: category, result: result, error: errorCode]
                    }

                    def failItems = testResults.findAll { it.result == "Fail" }

                    def htmlFilePath = "${RESULT_DIR}\\7DS_QA_Report.html"

                    writeFile file: htmlFilePath, text: "<html><body>Report Generated</body></html>"

                    if (failItems.size() > 0) {
                        def slackMsg = "❌ QA 실패 발생\n📂 경로: ${RESULT_DIR}\n"

                        failItems.each { f ->
                            slackMsg += "▶ 위치: ${f.row}행/${f.col}열\n"
                            slackMsg += "▶ 에러: ${f.error}\n"
                            slackMsg += "▶ 액션: 해당 기능 로직 및 상태 전이 확인 필요\n\n"
                        }

                        env.SLACK_FAIL_MSG = slackMsg
                        error "[ERR-QA-002] QA 테스트 실패 발생"
                    } else {
                        env.SLACK_SUCCESS_MSG = "✅ QA 통과\n📂 결과 경로: ${RESULT_DIR}"
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
                channel: '#qa-alert',
                color: '#00FF00',
                message: env.SLACK_SUCCESS_MSG ?: "✅ 빌드 성공"
            )
        }

        failure {
    script {
        def msg = env.SLACK_FAIL_MSG ?: "❌ [ERR-UNKNOWN-999] 오류 발생"

        slackSend (
            webhookUrl: 'https://hooks.slack.com/services/XXXXX/XXXXX/XXXXX',
            message: msg
        )
    }
}