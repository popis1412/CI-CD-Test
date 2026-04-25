pipeline {
    agent any

    environment {
        PROJECT_NAME = "7DS Origin QA"
    }

    stages {

        stage('Prepare') {
            steps {
                script {
                    def RESULT_DIR = "${env.WORKSPACE}\\Test Results"

                    bat """
                    if exist "${RESULT_DIR}" (
                        rmdir /s /q "${RESULT_DIR}"
                    )
                    mkdir "${RESULT_DIR}"
                    """
                }
            }
        }

        stage('QA Analysis') {
            steps {
                script {

                    def WORK_DIR = env.WORKSPACE
                    def RESULT_DIR = "${WORK_DIR}\\Test Results"
                    def TEST_FILE = "${WORK_DIR}\\Tests\\QA_Test.csv"

                    if (!fileExists(TEST_FILE)) {
                        error "[ERR-FILE-001] 테스트 파일 없음: ${TEST_FILE}"
                    }

                    def content = readFile(TEST_FILE)
                    def lines = content.split("\\r?\\n")

                    def testResults = []

                    // ======================
                    // CSV PARSE
                    // ======================
                    for (int i = 1; i < lines.size(); i++) {

                        def cols = lines[i].split(",")

                        if (cols.length >= 4) {
                            testResults << [
                                major: cols[0]?.trim(),
                                minor: cols[1]?.trim(),
                                scenario: cols[2]?.trim(),
                                result: cols[3]?.trim()
                            ]
                        }
                    }

                    // ======================
                    // 상태 정규화 함수
                    // ======================
                    def normalize = { r ->
                        if (r == null) return "Not Test"
                        def v = r.trim().toLowerCase()

                        if (v == "pass") return "Pass"
                        if (v == "fail") return "Fail"
                        if (v == "blocked") return "Blocked"
                        if (v == "n/a" || v == "na") return "N/A"
                        return "Not Test"
                    }

                    // ======================
                    // 전체 통계
                    // ======================
                    def stats = [
                        "Total": 0,
                        "Pass": 0,
                        "Fail": 0,
                        "Blocked": 0,
                        "Not Test": 0,
                        "N/A": 0
                    ]

                    testResults.each { t ->
                        def r = normalize(t.result)
                        t.result = r
                        stats["Total"]++

                        stats[r] = (stats[r] ?: 0) + 1
                    }

                    def failRate = stats["Total"] > 0 ?
                            (stats["Fail"] * 100.0 / stats["Total"]).toString().substring(0,5) : "0"

                    // ======================
                    // 대/중분류 Matrix
                    // ======================
                    def matrix = [:]

                    testResults.each { t ->

                        if (!matrix[t.major]) matrix[t.major] = [:]
                        if (!matrix[t.major][t.minor]) {
                            matrix[t.major][t.minor] = [
                                Total:0, Pass:0, Fail:0, Blocked:0, "Not Test":0, "N/A":0
                            ]
                        }

                        def m = matrix[t.major][t.minor]
                        m.Total++
                        m[t.result] = (m[t.result] ?: 0) + 1
                    }

                    // ======================
                    // Fail 리스트
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
                        body { font-family: Malgun Gothic; background:#f4f6f8; padding:30px; }
                        .card { background:white; padding:30px; border-radius:10px; }
                        h1 { border-bottom:3px solid #333; }
                        h2 { margin-top:30px; border-left:5px solid #333; padding-left:10px; }
                        h3 { margin-top:20px; }
                        table { width:100%; border-collapse: collapse; margin-top:10px; }
                        th, td { border:1px solid #ddd; padding:8px; text-align:center; }
                        th { background:#eee; }
                        .fail { color:red; font-weight:bold; }
                        .pass { color:green; }
                        .box { background:#fff3cd; padding:12px; margin-top:10px; }
                    </style>
                    </head>
                    <body>
                    <div class="card">

                    <h1>${env.PROJECT_NAME} QA REPORT</h1>

                    <h2>📌 1. 전체 테스트 현황</h2>

                    <table>
                        <tr><th>Status</th><th>Count</th><th>Progress</th></tr>
                        <tr><td>Total</td><td>${stats["Total"]}</td><td>100%</td></tr>
                        <tr><td>Pass</td><td>${stats["Pass"]}</td><td>${stats["Pass"] * 100 / stats["Total"]}%</td></tr>
                        <tr><td>Fail</td><td>${stats["Fail"]}</td><td>${stats["Fail"] * 100 / stats["Total"]}%</td></tr>
                        <tr><td>Blocked</td><td>${stats["Blocked"]}</td><td>${stats["Blocked"] * 100 / stats["Total"]}%</td></tr>
                        <tr><td>Not Test</td><td>${stats["Not Test"]}</td><td>${stats["Not Test"] * 100 / stats["Total"]}%</td></tr>
                        <tr><td>N/A</td><td>${stats["N/A"]}</td><td>${stats["N/A"] * 100 / stats["Total"]}%</td></tr>
                    </table>

                    <h2>📌 2. Fail Rate</h2>
                    <div class="box">
                        ${failRate}%
                    </div>

                    <h2>📌 3. 대/중분류 테스트 현황</h2>
                    """

                    // ======================
                    // 정렬된 출력
                    // ======================
                    matrix.keySet().sort().each { major ->

                        html += "<h3>${major}</h3>"
                        html += """
                        <table>
                        <tr>
                            <th>대분류</th>
                            <th>중분류</th>
                            <th>Total</th>
                            <th>Pass%</th>
                            <th>Fail%</th>
                            <th>Blocked%</th>
                            <th>Not Test%</th>
                            <th>N/A%</th>
                        </tr>
                        """

                        matrix[major].keySet().sort().each { minor ->

                            def v = matrix[major][minor]
                            def total = v.Total ?: 1

                            html += """
                            <tr>
                                <td>${major}</td>
                                <td>${minor}</td>
                                <td>${v.Total}</td>
                                <td>${(v.Pass * 100 / total)}</td>
                                <td class="fail">${(v.Fail * 100 / total)}</td>
                                <td>${(v.Blocked * 100 / total)}</td>
                                <td>${(v["Not Test"] * 100 / total)}</td>
                                <td>${(v["N/A"] * 100 / total)}</td>
                            </tr>
                            """
                        }

                        html += "</table>"
                    }

                    // ======================
                    // Fail 상세
                    // ======================
                    html += "<h2>📌 4. 결함 상세</h2>"
                    html += "<table><tr><th>대분류</th><th>중분류</th><th>시나리오</th><th>결과</th></tr>"

                    fails.each { f ->
                        html += """
                        <tr>
                            <td>${f.major}</td>
                            <td>${f.minor}</td>
                            <td>${f.scenario}</td>
                            <td class="fail">FAIL</td>
                        </tr>
                        """
                    }

                    html += "</table></div></body></html>"

                    writeFile file: "${RESULT_DIR}\\QA_Report.html", text: html

                    if (fails.size() > 0) {
                        error "[ERR-QA-002] FAIL ${fails.size()}건"
                    }
                }
            }
        }
    }

    post {
        always {
            script {
                def RESULT_DIR = "${env.WORKSPACE}\\Test Results"

                publishHTML(target: [
                    reportDir: RESULT_DIR,
                    reportFiles: 'QA_Report.html',
                    reportName: 'QA Report'
                ])
            }
        }

        success {
            slackSend(channel: "#새-채널", message: "✅ QA 성공")
        }

        failure {
            slackSend(channel: "#새-채널", message: "❌ QA 실패")
        }
    }
}