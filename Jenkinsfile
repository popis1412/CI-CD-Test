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

                    def safe = { v -> v?.toString()?.trim() ?: "" }

                    def rate = { num, total ->
                        if (!total || total == 0) return 0
                        return Math.round((num * 100.0 / total) * 100) / 100
                    }

                    if (!fileExists(TEST_FILE)) {
                        error "[ERR-FILE-001] 테스트 파일 없음"
                    }

                    def lines = readFile(TEST_FILE).split("\\r?\\n")
                    def testResults = []

                    // =========================
                    // CSV PARSE (SAFE)
                    // =========================
                    for (int i = 1; i < lines.size(); i++) {

                        def cols = lines[i].split(",")

                        if (cols.size() >= 4) {

                            testResults << [
                                row: i + 1,
                                major: safe(cols[0]),
                                minor: safe(cols[1]),
                                scenario: safe(cols[2]),
                                result: safe(cols[3])
                            ]
                        }
                    }

                    // =========================
                    // SAFE SORT (CPS SAFE)
                    // =========================
                    def order = [
                        "Fail": 0,
                        "Pass": 1,
                        "Blocked": 2,
                        "Not Test": 3,
                        "N/A": 4
                    ]

                    def sorted = []
                    sorted.addAll(testResults)

                    sorted.sort { a, b ->

                        def aMajor = a?.major ?: ""
                        def bMajor = b?.major ?: ""

                        def aMinor = a?.minor ?: ""
                        def bMinor = b?.minor ?: ""

                        def aSc = a?.scenario ?: ""
                        def bSc = b?.scenario ?: ""

                        def aR = order[a?.result] ?: 99
                        def bR = order[b?.result] ?: 99

                        return aMajor <=> bMajor ?:
                               aMinor <=> bMinor ?:
                               aSc <=> bSc ?:
                               aR <=> bR
                    }

                    testResults = sorted

                    // =========================
                    // STATUS
                    // =========================
                    def status = [
                        TOTAL:0, Pass:0, Fail:0, Blocked:0, "Not Test":0, "N/A":0
                    ]

                    testResults.each { t ->
                        def r = t?.result

                        status.TOTAL++

                        if (r == "Pass") status.Pass++
                        else if (r == "Fail") status.Fail++
                        else if (r == "Blocked") status.Blocked++
                        else if (r == "Not Test") status["Not Test"]++
                        else if (r == "N/A") status["N/A"]++
                    }

                    def fails = testResults.findAll { it?.result == "Fail" }

                    // =========================
                    // HTML
                    // =========================
                    def html = """
                    <html>
                    <head>
                    <meta charset="UTF-8">
                    <style>
                        body { font-family: 'Malgun Gothic'; padding:30px; background:#f4f6f8; }
                        .card { background:white; padding:30px; border-radius:10px; }
                        table { width:100%; border-collapse:collapse; margin-top:10px; }
                        th, td { border:1px solid #ddd; padding:8px; text-align:center; }
                        th { background:#eee; }
                        .fail { color:red; font-weight:bold; }
                    </style>
                    </head>
                    <body>
                    <div class="card">

                    <h1>${env.PROJECT_NAME}</h1>

                    <h2>전체 현황</h2>
                    <table>
                        <tr><th>Status</th><th>Count</th><th>Rate</th></tr>
                        <tr><td>Total</td><td>${status.TOTAL}</td><td>100%</td></tr>
                        <tr><td>Pass</td><td>${status.Pass}</td><td>${rate(status.Pass,status.TOTAL)}%</td></tr>
                        <tr><td>Fail</td><td>${status.Fail}</td><td>${rate(status.Fail,status.TOTAL)}%</td></tr>
                        <tr><td>Blocked</td><td>${status.Blocked}</td><td>${rate(status.Blocked,status.TOTAL)}%</td></tr>
                        <tr><td>Not Test</td><td>${status["Not Test"]}</td><td>${rate(status["Not Test"],status.TOTAL)}%</td></tr>
                        <tr><td>N/A</td><td>${status["N/A"]}</td><td>${rate(status["N/A"],status.TOTAL)}%</td></tr>
                    </table>

                    <h2>FAIL LIST</h2>
                    <table>
                        <tr><th>Major</th><th>Minor</th><th>Scenario</th><th>Result</th></tr>
                    """

                    fails.each {
                        html += """
                        <tr>
                            <td>${it?.major}</td>
                            <td>${it?.minor}</td>
                            <td>${it?.scenario}</td>
                            <td class="fail">Fail</td>
                        </tr>
                        """
                    }

                    html += "</table></div></body></html>"

                    writeFile file: "${RESULT_DIR}\\QA_Report.html", text: html

                    if (fails.size() > 0) {
                        error "[QA FAIL] ${fails.size()} issues found"
                    }
                }
            }
        }
    }

    post {
        always {
            publishHTML(target: [
                reportDir: "Test Results",
                reportFiles: 'QA_Report.html',
                reportName: 'QA Report'
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