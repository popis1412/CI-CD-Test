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
                    bat '''
                    if exist "Test Results" (
                        rmdir /s /q "Test Results"
                    )
                    mkdir "Test Results"
                    '''
                }
            }
        }

        stage('QA Analysis') {
            steps {
                script {

                    def WORK_DIR = "Test Results"
                    def TEST_FILE = "${params.BASE_PATH}\\Tests\\QA_Test.csv"

                    // =========================
                    // SAFE UTIL
                    // =========================
                    def safe = { v ->
                        if (v == null) return ""
                        return v.toString().trim()
                    }

                    // Jenkins-safe percentage (Math 제거)
                    def rate = { num, total ->
                        if (total == null || total == 0) return 0
                        return ((num * 10000) / total).intValue() / 100.0
                    }

                    if (!fileExists(TEST_FILE)) {
                        error "[ERR] QA CSV 파일 없음: ${TEST_FILE}"
                    }

                    def lines = readFile(TEST_FILE).split("\\r?\\n")
                    def testResults = []

                    // =========================
                    // CSV PARSE
                    // =========================
                    for (int i = 1; i < lines.size(); i++) {

                        def cols = lines[i].split(",")

                        if (cols.length >= 4) {
                            testResults.add([
                                row: i + 1,
                                major: safe(cols[0]),
                                minor: safe(cols[1]),
                                scenario: safe(cols[2]),
                                result: safe(cols[3])
                            ])
                        }
                    }

                    // =========================
                    // RESULT ORDER
                    // =========================
                    def order = [
                        "Fail": 0,
                        "Pass": 1,
                        "Blocked": 2,
                        "Not Test": 3,
                        "N/A": 4
                    ]

                    // =========================
                    // SAFE SORT (CPS 회피)
                    // =========================
                    def sorted = new ArrayList(testResults)

                    sorted.sort(new Comparator() {
                        int compare(a, b) {

                            def aM = a.major
                            def bM = b.major

                            def aN = a.minor
                            def bN = b.minor

                            def aS = a.scenario
                            def bS = b.scenario

                            def aR = order[a.result] ?: 99
                            def bR = order[b.result] ?: 99

                            if (aM != bM) return aM <=> bM
                            if (aN != bN) return aN <=> bN
                            if (aS != bS) return aS <=> bS
                            return aR <=> bR
                        }
                    })

                    testResults = sorted

                    // =========================
                    // STATUS COUNT
                    // =========================
                    def status = [
                        Total:0,
                        Pass:0,
                        Fail:0,
                        Blocked:0,
                        "Not Test":0,
                        "N/A":0
                    ]

                    testResults.each { t ->
                        status.Total++

                        switch(t.result) {
                            case "Pass": status.Pass++; break
                            case "Fail": status.Fail++; break
                            case "Blocked": status.Blocked++; break
                            case "Not Test": status["Not Test"]++; break
                            case "N/A": status["N/A"]++; break
                        }
                    }

                    def failRate = rate(status.Fail, status.Total)

                    def fails = testResults.findAll { it.result == "Fail" }

                    // =========================
                    // HTML
                    // =========================
                    def html = """
                    <html>
                    <head>
                        <meta charset="UTF-8">
                        <style>
                            body { font-family: Malgun Gothic; padding:30px; background:#f4f6f8; }
                            .card { background:white; padding:30px; border-radius:10px; }
                            table { width:100%; border-collapse:collapse; margin-top:10px; }
                            th, td { border:1px solid #ddd; padding:8px; text-align:center; }
                            th { background:#eee; }
                            .fail { color:red; font-weight:bold; }
                            .box { background:#fff3cd; padding:10px; margin-top:10px; }
                        </style>
                    </head>
                    <body>
                    <div class="card">

                    <h1>${env.PROJECT_NAME}</h1>

                    <h2>1. 전체 현황</h2>
                    <table>
                        <tr><th>Status</th><th>Count</th><th>Rate</th></tr>
                        <tr><td>Total</td><td>${status.Total}</td><td>100%</td></tr>
                        <tr><td>Pass</td><td>${status.Pass}</td><td>${rate(status.Pass,status.Total)}%</td></tr>
                        <tr><td>Fail</td><td>${status.Fail}</td><td>${failRate}%</td></tr>
                        <tr><td>Blocked</td><td>${status.Blocked}</td><td>${rate(status.Blocked,status.Total)}%</td></tr>
                        <tr><td>Not Test</td><td>${status["Not Test"]}</td><td>${rate(status["Not Test"],status.Total)}%</td></tr>
                        <tr><td>N/A</td><td>${status["N/A"]}</td><td>${rate(status["N/A"],status.Total)}%</td></tr>
                    </table>

                    <h2>2. Fail 목록</h2>
                    <table>
                        <tr><th>Major</th><th>Minor</th><th>Scenario</th><th>Result</th></tr>
                    """

                    fails.each { f ->
                        html += """
                        <tr>
                            <td>${f.major}</td>
                            <td>${f.minor}</td>
                            <td>${f.scenario}</td>
                            <td class="fail">Fail</td>
                        </tr>
                        """
                    }

                    html += """
                    </table>
                    </div>
                    </body>
                    </html>
                    """

                    writeFile file: "${WORK_DIR}\\QA_Report.html", text: html

                    if (fails.size() > 0) {
                        error "[QA FAILED] ${fails.size()} issues"
                    }
                }
            }
        }
    }

    post {
        always {
            publishHTML(target: [
                reportDir: "Test Results",
                reportFiles: "QA_Report.html",
                reportName: "QA Report"
            ])
        }

        success {
            slackSend(channel: "#새-채널", message: "✅ QA 성공")
        }

        failure {
            slackSend(channel: "#새-채널", message: "❌ QA 실패")
        }
    }
}