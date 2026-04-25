pipeline {
    agent any

    parameters {
        string(name: 'WORKSPACE_PATH', defaultValue: '', description: 'C:파일경로')
    }

    environment {
        PROJECT_NAME = "7DS Origin QA"
        WORKSPACE_PATH = "${params.WORKSPACE_PATH}"
        RESULT_DIR = "${params.WORKSPACE_PATH}\\Test Results"
        TEST_FILE_PATH = "${params.WORKSPACE_PATH}\\Tests\\QA_Test.csv"
    }

    stages {

        stage('Prepare') {
            steps {
                bat """
                if exist "${RESULT_DIR}" rmdir /s /q "${RESULT_DIR}"
                mkdir "${RESULT_DIR}"
                """
            }
        }

        stage('QA Analysis') {
            steps {
                script {

                    if (!fileExists(TEST_FILE_PATH)) {
                        error "CSV 파일 없음"
                    }

                    def content = readFile(TEST_FILE_PATH)
                    def lines = content.split("\\r?\\n")

                    // ======================
                    // CSV SAFE PARSER (Excel 대응)
                    // ======================
                    def parseCsvLine = { line ->
                        def result = []
                        def sb = new StringBuilder()
                        boolean inQuotes = false

                        for (int i = 0; i < line.length(); i++) {
                            char c = line.charAt(i)

                            if (c == '"') {
                                inQuotes = !inQuotes
                            }
                            else if (c == ',' && !inQuotes) {
                                result << sb.toString().trim()
                                sb.setLength(0)
                            }
                            else {
                                sb.append(c)
                            }
                        }

                        result << sb.toString().trim()
                        return result
                    }

                    def testResults = []

                    // ======================
                    // G열 기준 파싱
                    // ======================
                    for (int i = 1; i < lines.size(); i++) {

                        def line = lines[i].trim()
                        if (!line) continue

                        def cols = parseCsvLine(line)

                        if (cols.size() <= 6) continue

                        testResults << [
                            major: cols[0],
                            minor: cols[1],
                            scenario: cols[2],
                            result: cols[6]
                        ]
                    }

                    // ======================
                    // NORMALIZE
                    // ======================
                    def normalize = { r ->
                        if (!r) return "NOT TEST"

                        def v = r.trim().toUpperCase()

                        switch(v) {
                            case "PASS": return "PASS"
                            case "FAIL": return "FAIL"
                            case "BLOCKED": return "BLOCKED"
                            case "N/A":
                            case "NA": return "N/A"
                            default: return "NOT TEST"
                        }
                    }

                    testResults.each {
                        it.result = normalize(it.result)
                    }

                    // ======================
                    // FAIL LIST
                    // ======================
                    def fails = testResults.findAll { it.result == "FAIL" }

                    // ======================
                    // HTML (FAIL 전용 테이블)
                    // ======================
                    def html = """
                    <html>
                    <head>
                        <meta charset="UTF-8">
                        <style>
                            body { font-family: Arial; padding:20px; }
                            table { border-collapse: collapse; width:100%; }
                            th, td { border:1px solid #ddd; padding:8px; text-align:center; }
                            th { background:#333; color:white; }
                            .fail { background:#ffdddd; }
                        </style>
                    </head>
                    <body>

                    <h2>${PROJECT_NAME} - FAIL REPORT</h2>

                    <h3>FAIL 목록 (${fails.size()}건)</h3>

                    <table>
                        <tr>
                            <th>Major</th>
                            <th>Minor</th>
                            <th>Scenario</th>
                        </tr>
                    """

                    if (fails.size() == 0) {
                        html += """
                        <tr>
                            <td colspan="3">All Passed 🎉</td>
                        </tr>
                        """
                    } else {

                        fails.each { f ->
                            html += """
                            <tr class="fail">
                                <td>${f.major}</td>
                                <td>${f.minor}</td>
                                <td>${f.scenario}</td>
                            </tr>
                            """
                        }
                    }

                    html += """
                    </table>

                    </body>
                    </html>
                    """

                    writeFile file: "${RESULT_DIR}\\fail_report.html", text: html

                    // ======================
                    // Slack 메시지 생성
                    // ======================
                    def slackMessage = ""

                    if (fails.size() > 0) {

                        slackMessage = """❌ QA 완료 (FAIL 발생)
FAIL COUNT: ${fails.size()}

--- FAIL LIST ---
"""

                        fails.each { f ->
                            slackMessage += """
• Major: ${f.major}
• Minor: ${f.minor}
• Scenario: ${f.scenario}
-------------------
"""
                        }

                    } else {
                        slackMessage = "✅ QA 완료 - ALL PASS (${testResults.size()} cases)"
                    }

                    // ======================
                    // SUCCESS 고정 (빌드 실패 없음)
                    // ======================
                    currentBuild.result = 'SUCCESS'

                    echo "[INFO] FAIL: ${fails.size()}"
                    echo "[INFO] TOTAL: ${testResults.size()}"

                    // Slack용 저장
                    currentBuild.description = "FAIL=${fails.size()}, TOTAL=${testResults.size()}"

                    // Slack message export
                    env.SLACK_MSG = slackMessage
                }
            }
        }
    }

    post {

        success {
            slackSend channel: '#새-채널',
                color: (env.SLACK_MSG.contains("FAIL") ? 'danger' : 'good'),
                message: env.SLACK_MSG
        }

        always {
            archiveArtifacts artifacts: 'Test Results/**'
        }
    }
}