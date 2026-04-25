pipeline {
    agent any

    parameters {
        string(name: 'WORKSPACE_PATH', defaultValue: '', description: 'C:\\파일경로')
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
                        error "CSV 없음"
                    }

                    def content = readFile(TEST_FILE_PATH)
                    def lines = content.split("\\r?\\n")

                    def testResults = []

                    // ======================
                    // CSV PARSE (G열 = index 6)
                    // ======================
                    for (int i = 1; i < lines.size(); i++) {

                        def line = lines[i].trim()
                        if (!line) continue

                        def cols = line.split(",")

                        if (cols.size() <= 6) continue

                        testResults << [
                            major: cols[0]?.trim(),
                            minor: cols[1]?.trim(),
                            scenario: cols[2]?.trim(),
                            result: cols[6]?.trim()   // ⭐ G열
                        ]
                    }

                    // ======================
                    // NORMALIZE
                    // ======================
                    def normalize = { r ->
                        if (!r) return "NOT TEST"
                        def v = r.trim().toUpperCase()

                        if (v == "PASS") return "PASS"
                        if (v == "FAIL") return "FAIL"
                        if (v == "BLOCKED") return "BLOCKED"
                        if (v == "N/A") return "N/A"
                        return "NOT TEST"
                    }

                    testResults.each {
                        it.result = normalize(it.result)
                    }

                    // ======================
                    // STATS
                    // ======================
                    def stats = [
                        Total: testResults.size(),
                        PASS: 0,
                        FAIL: 0,
                        BLOCKED: 0,
                        "NOT TEST": 0,
                        "N/A": 0
                    ]

                    testResults.each {
                        stats[it.result] = (stats[it.result] ?: 0) + 1
                    }

                    def failRate = stats.Total > 0 ?
                        (stats.FAIL * 100.0 / stats.Total) : 0

                    // ======================
                    // GROUPING (요구사항 핵심)
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
                    // HTML
                    // ======================
                    def html = """
                    <html>
                    <head>
                        <style>
                            table { border-collapse: collapse; width:100%; }
                            th, td { border:1px solid #ddd; padding:8px; }
                            th { background:#333; color:white; }
                        </style>
                    </head>
                    <body>

                    <h2>${PROJECT_NAME}</h2>

                    <h3>Summary</h3>
                    <p>Total: ${stats.Total}</p>
                    <p>Fail: ${stats.FAIL}</p>
                    <p>Fail Rate: ${String.format('%.2f', failRate)}%</p>

                    <h3>Detailed Table</h3>

                    <table>
                        <tr>
                            <th>Major</th>
                            <th>Minor</th>
                            <th>Status</th>
                            <th>Count</th>
                        </tr>
                    """

                    rows.each {
                        html += """
                        <tr>
                            <td>${it.major}</td>
                            <td>${it.minor}</td>
                            <td>${it.status}</td>
                            <td>${it.count}</td>
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
                    // FIX: stats를 post에서 쓰기 위해 저장
                    // ======================
                    writeFile file: "${RESULT_DIR}\\stats.txt", text: """
TOTAL=${stats.Total}
FAIL=${stats.FAIL}
"""

                    // store for post
                    currentBuild.description = "TOTAL=${stats.Total}, FAIL=${stats.FAIL}"

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