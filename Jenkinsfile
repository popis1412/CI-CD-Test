pipeline {
    agent any

    parameters {
        string(name: 'WORKSPACE_PATH', defaultValue: 'C:\\QA\\CI-CD-Test', description: 'Workspace Path')
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
                        error "CSV 없음"
                    }

                    def content = readFile(TEST_FILE_PATH)
                    def lines = content.split("\\r?\\n")

                    // ======================
                    // CSV SAFE PARSER
                    // ======================
                    def parseCsvLine = { line ->
                        def result = []
                        def sb = new StringBuilder()
                        boolean inQuotes = false

                        for (int i = 0; i < line.length(); i++) {
                            char c = line.charAt(i)

                            if (c == '"') inQuotes = !inQuotes
                            else if (c == ',' && !inQuotes) {
                                result << sb.toString().trim()
                                sb.setLength(0)
                            }
                            else sb.append(c)
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
                            action: cols[3],
                            result: cols[6]
                        ]
                    }

                    // ======================
                    // NORMALIZE
                    // ======================
                    def normalize = { r ->
                        if (!r) return "NOT TEST"
                        switch(r.trim().toUpperCase()) {
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
                    // STATS
                    // ======================
                    def stats = [
                        Total: 0,
                        PASS: 0,
                        FAIL: 0,
                        BLOCKED: 0,
                        "NOT TEST": 0,
                        "N/A": 0
                    ]

                    testResults.each {
                        stats.Total++
                        stats[it.result] = (stats[it.result] ?: 0) + 1
                    }

                    // ======================
                    // ① 대/중분류 통계
                    // ======================
                    def groupMap = [:]

                    testResults.each { t ->
                        def key = "${t.major}|${t.minor}"

                        if (!groupMap[key]) {
                            groupMap[key] = [
                                major: t.major,
                                minor: t.minor,
                                total: 0,
                                pass: 0,
                                fail: 0
                            ]
                        }

                        def g = groupMap[key]
                        g.total++
                        if (t.result == "PASS") g.pass++
                        if (t.result == "FAIL") g.fail++
                    }

                    // ======================
                    // ② FAIL 시나리오별 비율
                    // ======================
                    def failByScenario = [:]

                    testResults.each {
                        if (it.result == "FAIL") {
                            failByScenario[it.scenario] = (failByScenario[it.scenario] ?: 0) + 1
                        }
                    }

                    // 전체 대비 비율
                    def failScenarioTable = failByScenario.collect { k, v ->
                        [
                            scenario: k,
                            rate: stats.FAIL > 0 ? (v * 100.0 / stats.FAIL) : 0
                        ]
                    }

                    // ======================
                    // ③ 결함 상세 (원본 유지)
                    // ======================
                    def defects = testResults.findAll { it.result == "FAIL" }

                    // ======================
                    // HTML REPORT
                    // ======================
                    def html = """
                    <html>
                    <head>
                        <meta charset="UTF-8">
                        <style>
                            body { font-family: Arial; padding:20px; }
                            table { border-collapse: collapse; width:100%; margin-bottom:30px; }
                            th, td { border:1px solid #ddd; padding:8px; text-align:center; }
                            th { background:#333; color:white; }
                            .fail { background:#ffdddd; }
                        </style>
                    </head>
                    <body>

                    <h2>${PROJECT_NAME} QA REPORT</h2>

                    <h3>📊 대/중분류 테스트 현황</h3>
                    <table>
                        <tr>
                            <th>Major</th>
                            <th>Minor</th>
                            <th>Total</th>
                            <th>Pass</th>
                            <th>Fail</th>
                            <th>Fail %</th>
                        </tr>
                    """

                    groupMap.values().each {
                        def failRate = it.total > 0 ? (it.fail * 100.0 / it.total) : 0

                        html += """
                        <tr>
                            <td>${it.major}</td>
                            <td>${it.minor}</td>
                            <td>${it.total}</td>
                            <td>${it.pass}</td>
                            <td>${it.fail}</td>
                            <td>${String.format('%.1f', failRate)}%</td>
                        </tr>
                        """
                    }

                    html += """
                    </table>

                    <h3>📉 분류별 실패 시나리오 비율</h3>
                    <table>
                        <tr>
                            <th>TC 이름</th>
                            <th>Fail 비율</th>
                        </tr>
                    """

                    failScenarioTable.each {
                        html += """
                        <tr>
                            <td>${it.scenario}</td>
                            <td>${String.format('%.1f', it.rate)}%</td>
                        </tr>
                        """
                    }

                    html += """
                    </table>

                    <h3>❌ 분류별 발견된 결함</h3>
                    <table>
                        <tr>
                            <th>No</th>
                            <th>대분류</th>
                            <th>중분류</th>
                            <th>테스트 액션</th>
                        </tr>
                    """

                    int idx = 1
                    defects.each {
                        html += """
                        <tr class="fail">
                            <td>${idx++}</td>
                            <td>${it.major}</td>
                            <td>${it.minor}</td>
                            <td>${it.action}</td>
                        </tr>
                        """
                    }

                    html += """
                    </table>

                    </body>
                    </html>
                    """

                    writeFile file: "${RESULT_DIR}\\qa_report.html", text: html

                    // ======================
                    // Slack 메시지
                    // ======================
                    def slackMessage = ""

                    if (defects.size() > 0) {
                        slackMessage = """❌ QA 완료 (FAIL ${defects.size()}건)

"""
                        failScenarioTable.each {
                            slackMessage += "• ${it.scenario} (${String.format('%.1f', it.rate)}%)\n"
                        }
                    } else {
                        slackMessage = "✅ QA 완료 - ALL PASS"
                    }

                    currentBuild.result = 'SUCCESS'
                    currentBuild.description = "TOTAL=${stats.Total}, FAIL=${stats.FAIL}"
                    env.SLACK_MSG = slackMessage

                    echo "[INFO] TOTAL: ${stats.Total}"
                    echo "[INFO] FAIL: ${stats.FAIL}"
                }
            }
        }
    }

    post {
        success {
            slackSend channel: '#새-채널',
                color: 'good',
                message: env.SLACK_MSG
        }

        failure {
            slackSend channel: '#새-채널',
                color: 'danger',
                message: env.SLACK_MSG
        }

        always {
            archiveArtifacts artifacts: 'Test Results/**'
        }
    }
}