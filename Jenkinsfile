pipeline {
    agent any

    parameters {
        string(name: 'BASE_PATH', defaultValue: '', description: '기본 경로')
    }

    environment {
        PROJECT_NAME = "7DS Origin QA"
    }

    stages {

        stage('Prepare') {
            steps {
                script {

                    bat """
                    if exist "Test Results" (
                        rmdir /s /q "Test Results"
                    )
                    mkdir "Test Results"
                    """
                }
            }
        }

        stage('QA Analysis') {
            steps {
                script {

                    def RESULT_DIR = "Test Results"
                    def TEST_FILE = "${params.BASE_PATH}\\Tests\\QA_Test.csv"

                    // ===============================
                    // SAFE RATE
                    // ===============================
                    def rate = { num, total ->
                        if (total == 0) return 0
                        return Math.round((num * 100.0 / total) * 100) / 100
                    }

                    def safe = { v -> (v ?: "").trim() }

                    if (!fileExists(TEST_FILE)) {
                        error "[ERR-FILE-001] 테스트 파일 없음"
                    }

                    def content = readFile(TEST_FILE)
                    def lines = content.split("\\r?\\n")

                    def testResults = []

                    // ===============================
                    // CSV PARSE (문자열 그대로 사용)
                    // ===============================
                    for (int i = 1; i < lines.size(); i++) {

                        def cols = lines[i].split(",")

                        if (cols.size() >= 4) {

                            testResults << [
                                row: i + 1,
                                col: "D",
                                major: safe(cols[0]),
                                minor: safe(cols[1]),
                                scenario: safe(cols[2]),
                                result: safe(cols[3])   // ❗ 변경: toUpperCase 제거
                            ]
                        }
                    }

                    // ===============================
                    // 정렬 우선순위 (요구 문자열 기준)
                    // ===============================
                    def order = [
                        "Fail": 0,
                        "Pass": 1,
                        "Blocked": 2,
                        "Not Test": 3,
                        "N/A": 4
                    ]

                    testResults = testResults.sort { a, b ->
                        a.major <=> b.major ?:
                        a.minor <=> b.minor ?:
                        a.scenario <=> b.scenario ?:
                        order[a.result] <=> order[b.result]
                    }

                    // ===============================
                    // 전체 상태 통계
                    // ===============================
                    def statusStats = [
                        TOTAL:0, Pass:0, Fail:0, Blocked:0, "Not Test":0, "N/A":0
                    ]

                    testResults.each { t ->
                        statusStats.TOTAL++

                        switch(t.result) {
                            case "Pass": statusStats.Pass++; break
                            case "Fail": statusStats.Fail++; break
                            case "Blocked": statusStats.Blocked++; break
                            case "Not Test": statusStats["Not Test"]++; break
                            case "N/A": statusStats["N/A"]++; break
                        }
                    }

                    def failRate = rate(statusStats.Fail, statusStats.TOTAL)

                    // ===============================
                    // MATRIX
                    // ===============================
                    def matrix = [:]

                    testResults.each { t ->

                        if (!matrix[t.major]) matrix[t.major] = [:]

                        if (!matrix[t.major][t.minor]) {
                            matrix[t.major][t.minor] = [
                                total:0, Pass:0, Fail:0, Blocked:0, "Not Test":0, "N/A":0
                            ]
                        }

                        def m = matrix[t.major][t.minor]
                        m.total++

                        if (m.containsKey(t.result)) {
                            m[t.result]++
                        }
                    }

                    matrix = matrix.sort { it.key }

                    // ===============================
                    // SCENARIO
                    // ===============================
                    def scenarioMap = [:]

                    testResults.each { t ->

                        if (!scenarioMap[t.scenario]) {
                            scenarioMap[t.scenario] = [total:0, fail:0]
                        }

                        def s = scenarioMap[t.scenario]

                        s.total++
                        if (t.result == "Fail") s.fail++
                    }

                    scenarioMap = scenarioMap.sort { it.key }

                    // ===============================
                    // FAIL LIST
                    // ===============================
                    def fails = testResults.findAll { it.result == "Fail" }

                    fails = fails.sort { a, b ->
                        a.major <=> b.major ?:
                        a.minor <=> b.minor ?:
                        a.scenario <=> b.scenario
                    }

                    // ===============================
                    // HTML
                    // ===============================
                    def html = """
                    <html>
                    <head>
                    <meta charset="UTF-8">
                    <style>
                        body { font-family: 'Malgun Gothic'; background:#f4f6f8; padding:30px; }
                        .card { background:white; padding:30px; border-radius:10px; }
                        h1 { border-bottom:3px solid #333; }
                        h2 { margin-top:30px; border-left:5px solid #333; padding-left:10px; }
                        h3 { margin-top:20px; }
                        table { width:100%; border-collapse: collapse; margin-top:10px; }
                        th, td { border:1px solid #ddd; padding:8px; text-align:center; }
                        th { background:#eee; }
                        .fail { color:red; font-weight:bold; }
                        .box { background:#fff3cd; padding:12px; margin-top:10px; }
                    </style>
                    </head>
                    <body>
                    <div class="card">

                    <h1>${env.PROJECT_NAME} QA Report</h1>

                    <h2>📌 1. 전체 테스트 현황</h2>
                    <table>
                        <tr><th>Status</th><th>Count</th><th>Progress</th></tr>
                        <tr><td>Total</td><td>${statusStats.TOTAL}</td><td>100%</td></tr>
                        <tr><td>Pass</td><td>${statusStats.Pass}</td><td>${rate(statusStats.Pass, statusStats.TOTAL)}%</td></tr>
                        <tr><td>Fail</td><td>${statusStats.Fail}</td><td>${rate(statusStats.Fail, statusStats.TOTAL)}%</td></tr>
                        <tr><td>Blocked</td><td>${statusStats.Blocked}</td><td>${rate(statusStats.Blocked, statusStats.TOTAL)}%</td></tr>
                        <tr><td>Not Test</td><td>${statusStats["Not Test"]}</td><td>${rate(statusStats["Not Test"], statusStats.TOTAL)}%</td></tr>
                        <tr><td>N/A</td><td>${statusStats["N/A"]}</td><td>${rate(statusStats["N/A"], statusStats.TOTAL)}%</td></tr>
                    </table>

                    <h2>📊 2. 전체 실패율</h2>
                    <div class="box">
                        Fail Rate: ${failRate}%
                    </div>

                    <h2>📌 3. 대/중분류 테스트 현황</h2>
                    """

                    // ===============================
                    // MATRIX 출력
                    // ===============================
                    matrix.each { major, minors ->

                        html += "<h3>📍 ${major}</h3>"
                        html += """
                        <table>
                        <tr>
                            <th>대분류</th>
                            <th>중분류</th>
                            <th>Pass%</th>
                            <th>Fail%</th>
                            <th>Blocked%</th>
                            <th>Not Test%</th>
                            <th>N/A%</th>
                        </tr>
                        """

                        minors.each { minor, v ->

                            def total = v.total ?: 1

                            html += """
                            <tr>
                                <td>${major}</td>
                                <td>${minor}</td>
                                <td>${rate(v.Pass, total)}%</td>
                                <td class="fail">${rate(v.Fail, total)}%</td>
                                <td>${rate(v.Blocked, total)}%</td>
                                <td>${rate(v["Not Test"], total)}%</td>
                                <td>${rate(v["N/A"], total)}%</td>
                            </tr>
                            """
                        }

                        html += "</table>"
                    }

                    // ===============================
                    // SCENARIO
                    // ===============================
                    html += "<h2>📌 4. 시나리오 실패 비율</h2>"

                    scenarioMap.each { s, v ->

                        html += """
                        <div class="box">
                            <b>${s}</b><br>
                            Fail Rate: ${rate(v.fail, v.total)}%
                        </div>
                        """
                    }

                    // ===============================
                    // FAIL LIST
                    // ===============================
                    html += "<h2>📌 5. 결함 상세</h2>"
                    html += "<table><tr><th>대분류</th><th>중분류</th><th>시나리오</th><th>결과</th></tr>"

                    fails.each {
                        html += """
                        <tr>
                            <td>${it.major}</td>
                            <td>${it.minor}</td>
                            <td>${it.scenario}</td>
                            <td class="fail">Fail</td>
                        </tr>
                        """
                    }

                    html += "</table></div></body></html>"

                    writeFile file: "${RESULT_DIR}\\QA_Report.html", text: html

                    if (fails.size() > 0) {
                        error "[ERR-QA-002] QA 실패 ${fails.size()}건"
                    }
                }
            }
        }
    }

    post {
        always {
            script {
                publishHTML(target: [
                    reportDir: "Test Results",
                    reportFiles: 'QA_Report.html',
                    reportName: 'QA Report'
                ])
            }
        }

        success {
            slackSend(channel: "#새-채널", message: "✅ QA 성공")
        }

        failure {
            slackSend(channel: "#새-채널", message: "❌ QA 실패 발생")
        }
    }
}