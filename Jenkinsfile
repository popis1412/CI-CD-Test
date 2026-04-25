pipeline {
    agent any

    parameters {
        string(name: 'WORKSPACE_PATH', defaultValue: '', description: 'Workspace Path')
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
                script {
                    bat """
                    if exist "${RESULT_DIR}" rmdir /s /q "${RESULT_DIR}"
                    mkdir "${RESULT_DIR}"
                    """
                }
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

                    // 빈 줄 제거
                    def lines = content.split(/\r?\n/).findAll { it.trim() }

                    def testResults = []

                    // ======================
                    // CSV PARSE (G열 기준)
                    // ======================
                    for (int i = 1; i < lines.size(); i++) {

                        def cols = lines[i].split(",", -1)

                        if (cols.size() < 7) continue

                        testResults << [
                            major: cols[0]?.trim(),
                            minor: cols[1]?.trim(),
                            scenario: cols[2]?.trim(),
                            result: cols[6]?.trim()   // ⭐ G열
                        ]
                    }

                    // ======================
                    // 정규화
                    // ======================
                    def normalize = { r ->
                        if (!r) return "Not Test"
                        def v = r.toLowerCase()

                        if (v == "pass") return "Pass"
                        if (v == "fail") return "Fail"
                        if (v == "blocked") return "Blocked"
                        if (v == "n/a" || v == "na") return "N/A"

                        return "Not Test"
                    }

                    testResults.each { it.result = normalize(it.result) }

                    // ======================
                    // 전체 통계
                    // ======================
                    def stats = [
                        Total: testResults.size(),
                        Pass: 0,
                        Fail: 0,
                        Blocked: 0,
                        "Not Test": 0,
                        "N/A": 0
                    ]

                    testResults.each { t ->
                        stats[t.result] = (stats[t.result] ?: 0) + 1
                    }

                    def failRate = stats.Total > 0 ? stats.Fail * 100.0 / stats.Total : 0

                    // ======================
                    // ★ 핵심: 집계 테이블
                    // ======================
                    def summaryMap = [:]

                    testResults.each { t ->
                        def key = "${t.major}|${t.minor}|${t.result}"
                        summaryMap[key] = (summaryMap[key] ?: 0) + 1
                    }

                    // ======================
                    // Fail 목록
                    // ======================
                    def fails = testResults.findAll { it.result == "Fail" }

                    // ======================
                    // HTML
                    // ======================
                    def html = """
                    <html>
                    <head>
                        <meta charset="UTF-8">
                        <style>
                            table { border-collapse: collapse; width:100%; }
                            th, td { border:1px solid #ddd; padding:8px; }
                            th { background:#f2f2f2; }
                        </style>
                    </head>
                    <body>

                    <h2>${PROJECT_NAME}</h2>

                    <h3>전체 통계</h3>
                    <p>Total: ${stats.Total} | Pass: ${stats.Pass} | Fail: ${stats.Fail}</p>

                    <h3>대분류 | 중분류 | 상태 | 개수</h3>
                    <table>
                        <tr>
                            <th>대분류</th>
                            <th>중분류</th>
                            <th>상태</th>
                            <th>개수</th>
                        </tr>
                    """

                    summaryMap.each { k, v ->
                        def p = k.split("\\|")

                        html += """
                        <tr>
                            <td>${p[0]}</td>
                            <td>${p[1]}</td>
                            <td>${p[2]}</td>
                            <td>${v}</td>
                        </tr>
                        """
                    }

                    html += """
                    </table>

                    <h3>Fail 리스트</h3>
                    """

                    if (fails.size() == 0) {
                        html += "<p>Fail 없음</p>"
                    } else {
                        html += "<ul>"
                        fails.each {
                            html += "<li>${it.major} / ${it.minor} / ${it.scenario}</li>"
                        }
                        html += "</ul>"
                    }

                    html += """
                    </body>
                    </html>
                    """

                    writeFile file: "${RESULT_DIR}\\QA_Report.html", text: html

                    println "[INFO] FAIL: ${fails.size()}"
                    println "[INFO] TOTAL: ${stats.Total}"

                    if (fails.size() > 0) {
                        currentBuild.result = "FAILURE"
                    }
                }
            }
        }
    }

post {

    always {
        archiveArtifacts artifacts: 'Test Results/**'
    }

    success {
        script {
            echo "✅ QA 성공"

            slackSend(
                color: "good",
                message: """
✅ QA SUCCESS
Project: ${env.PROJECT_NAME}
Total: ${env.TOTAL}
Pass: ${env.PASS}
Fail: ${env.FAIL}
Fail Rate: ${env.FAILRATE}
Report: ${env.BUILD_URL}artifact/Test Results/QA_Report.html
"""
            )
        }
    }

    failure {
        script {
            echo "❌ QA 실패"

            slackSend(
                color: "danger",
                message: """
❌ QA FAILURE
Project: ${env.PROJECT_NAME}
Total: ${env.TOTAL}
Pass: ${env.PASS}
Fail: ${env.FAIL}
Fail Rate: ${env.FAILRATE}
Report: ${env.BUILD_URL}artifact/Test Results/QA_Report.html
"""
            )
        }
    }
}
}