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

                    echo "[INFO] FILE: ${TEST_FILE_PATH}"

                    if (!fileExists(TEST_FILE_PATH)) {
                        error "CSV 파일 없음: ${TEST_FILE_PATH}"
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
                    // PARSE (G열 = index 6)
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
                    // STATS (정확한 방식)
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

                    def failRate = stats.Total > 0 ?
                        (stats.FAIL * 100.0 / stats.Total) : 0

                    // ======================
                    // 핵심: 대분류 | 중분류 | 상태 | 개수
                    // ======================
                    def tableMap = [:]

                    testResults.each { t ->
                        def key = "${t.major}|${t.minor}|${t.result}"

                        if (!tableMap[key]) {
                            tableMap[key] = [
                                major: t.major,
                                minor: t.minor,
                                status: t.result,
                                count: 0
                            ]
                        }

                        tableMap[key].count++
                    }

                    def rows = tableMap.values().toList()

                    // ======================
                    // FAIL 리스트 (정확)
                    // ======================
                    def fails = testResults.findAll { it.result == "FAIL" }

                    // ======================
                    // HTML REPORT
                    // ======================
                    def html = """
                    <html>
                    <head>
                        <meta charset="UTF-8">
                        <style>
                            body { font-family: Arial; padding:20px; }
                            table { border-collapse: collapse; width:100%; margin-bottom:20px; }
                            th, td { border:1px solid #ddd; padding:8px; text-align:center; }
                            th { background:#333; color:white; }
                            .fail { background:#ffdddd; }
                        </style>
                    </head>
                    <body>

                    <h2>${PROJECT_NAME}</h2>

                    <h3>Summary</h3>
                    <p>Total: ${stats.Total}</p>
                    <p>PASS: ${stats.PASS}</p>
                    <p>FAIL: ${stats.FAIL}</p>
                    <p>Fail Rate: ${String.format('%.2f', failRate)}%</p>

                    <h3>대분류 | 중분류 | 상태 | 개수</h3>

                    <table>
                        <tr>
                            <th>Major</th>
                            <th>Minor</th>
                            <th>Status</th>
                            <th>Count</th>
                        </tr>
                    """

                    rows.each {
                        def cls = (it.status == "FAIL") ? "fail" : ""
                        html += """
                        <tr class="${cls}">
                            <td>${it.major}</td>
                            <td>${it.minor}</td>
                            <td>${it.status}</td>
                            <td>${it.count}</td>
                        </tr>
                        """
                    }

                    html += """
                    </table>

                    <h3>FAIL 상세</h3>
                    <table>
                        <tr>
                            <th>Major</th>
                            <th>Minor</th>
                            <th>Scenario</th>
                        </tr>
                    """

                    fails.each {
                        html += """
                        <tr class="fail">
                            <td>${it.major}</td>
                            <td>${it.minor}</td>
                            <td>${it.scenario}</td>
                        </tr>
                        """
                    }

                    html += """
                    </table>

                    </body>
                    </html>
                    """

                    writeFile file: "${RESULT_DIR}\\report.html", text: html

                    // ======================
                    // stats scope 해결 (post용)
                    // ======================
                    currentBuild.description = "TOTAL=${stats.Total}, FAIL=${stats.FAIL}"

                    writeFile file: "${RESULT_DIR}\\stats.txt", text: """
TOTAL=${stats.Total}
FAIL=${stats.FAIL}
FAIL_RATE=${String.format('%.2f', failRate)}
"""

                    echo "[INFO] TOTAL: ${stats.Total}"
                    echo "[INFO] FAIL: ${stats.FAIL}"

                    if (stats.FAIL > 0) {
                        currentBuild.result = 'FAILURE'
                    } else {
                        currentBuild.result = 'SUCCESS'
                    }
                }
            }
        }
    }

    post {

        success {
            slackSend channel: '#새-채널',
                color: 'good',
                message: "✅ QA 성공: ${currentBuild.description}"
        }

        failure {
            slackSend channel: '#새-채널',
                color: 'danger',
                message: "❌ QA 실패: ${currentBuild.description}"
        }

        always {
            archiveArtifacts artifacts: 'Test Results/**'
        }
    }
}