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

                    def RESULT_DIR = "${params.BASE_PATH}\\Test Results"

                    bat """
                    if not exist "${RESULT_DIR}" (
                        mkdir "${RESULT_DIR}"
                    )
                    """
                }
            }
        }

        stage('QA Analysis') {
            steps {
                script {

                    def RESULT_DIR = "${params.BASE_PATH}\\Test Results"
                    def TEST_FILE = "${params.BASE_PATH}\\Tests\\QA_Test.csv"

                    if (!fileExists(TEST_FILE)) {
                        error "[ERR-FILE-001] 테스트 파일 없음"
                    }

                    def content = readFile(TEST_FILE)
                    def lines = content.split("\\r?\\n")

                    def testResults = []

                    // ===============================
                    // CSV PARSE
                    // ===============================
                    for (int i = 1; i < lines.size(); i++) {

                        def cols = lines[i].split(",")

                        if (cols.size() >= 4) {

                            testResults << [
                                row: i + 1,
                                col: "D",
                                major: cols[0]?.trim(),
                                minor: cols[1]?.trim(),
                                scenario: cols[2]?.trim(),
                                result: cols[3]?.trim()?.toUpperCase()
                            ]
                        }
                    }

                    // ===============================
                    // 전체 상태 통계
                    // ===============================
                    def statusStats = [
                        TOTAL:0, PASS:0, FAIL:0, BLOCKED:0, NOTTEST:0, NA:0
                    ]

                    testResults.each { t ->
                        statusStats.TOTAL++

                        switch(t.result) {
                            case "PASS": statusStats.PASS++; break
                            case "FAIL": statusStats.FAIL++; break
                            case "BLOCKED": statusStats.BLOCKED++; break
                            case "NOTTEST": statusStats.NOTTEST++; break
                            case "N/A": statusStats.NA++; break
                        }
                    }

                    def failRate = statusStats.TOTAL > 0 ?
                            (statusStats.FAIL * 100 / statusStats.TOTAL).toDouble().round(2) : 0

                    // ===============================
                    // 대/중분류 매트릭스
                    // ===============================
                    def matrix = [:]

                    testResults.each { t ->

                        if(!matrix[t.major]) matrix[t.major] = [:]

                        if(!matrix[t.major][t.minor]) {
                            matrix[t.major][t.minor] = [
                                total:0, PASS:0, FAIL:0, BLOCKED:0, NOTTEST:0, NA:0
                            ]
                        }

                        def m = matrix[t.major][t.minor]
                        m.total++

                        if(m.containsKey(t.result)) {
                            m[t.result]++
                        }
                    }

                    // ===============================
                    // 시나리오 분석
                    // ===============================
                    def scenarioMap = [:]

                    testResults.each { t ->

                        if(!scenarioMap[t.scenario]) {
                            scenarioMap[t.scenario] = [total:0, fail:0, list:[]]
                        }

                        def s = scenarioMap[t.scenario]

                        s.total++

                        if(t.result == "FAIL") {
                            s.fail++
                            s.list << t
                        }
                    }

                    def fails = testResults.findAll { it.result == "FAIL" }

                    // ===============================
                    // HTML 시작
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
                        .pass { color:green; }
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
                        <tr><td>Pass</td><td>${statusStats.PASS}</td><td>${(statusStats.PASS*100/statusStats.TOTAL).round(2)}%</td></tr>
                        <tr><td>Fail</td><td>${statusStats.FAIL}</td><td>${(statusStats.FAIL*100/statusStats.TOTAL).round(2)}%</td></tr>
                        <tr><td>Blocked</td><td>${statusStats.BLOCKED}</td><td>${(statusStats.BLOCKED*100/statusStats.TOTAL).round(2)}%</td></tr>
                        <tr><td>NotTest</td><td>${statusStats.NOTTEST}</td><td>${(statusStats.NOTTEST*100/statusStats.TOTAL).round(2)}%</td></tr>
                        <tr><td>N/A</td><td>${statusStats.NA}</td><td>${(statusStats.NA*100/statusStats.TOTAL).round(2)}%</td></tr>
                    </table>

                    <h2>📊 2. 전체 실패율</h2>
                    <div class="box">
                        Fail Rate: ${failRate}%
                    </div>

                    <h2>📌 3. 대/중분류 테스트 현황</h2>
                    """

                    // ===============================
                    // 대분류별 출력
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
                            <th>NotTest%</th>
                            <th>N/A%</th>
                        </tr>
                        """

                        minors.each { minor, v ->

                            def total = v.total ?: 1

                            def passP = (v.PASS * 100 / total).round(2)
                            def failP = (v.FAIL * 100 / total).round(2)
                            def blockP = (v.BLOCKED * 100 / total).round(2)
                            def notP = (v.NOTTEST * 100 / total).round(2)
                            def naP = (v.NA * 100 / total).round(2)

                            html += """
                            <tr>
                                <td>${major}</td>
                                <td>${minor}</td>
                                <td>${passP}%</td>
                                <td class="fail">${failP}%</td>
                                <td>${blockP}%</td>
                                <td>${notP}%</td>
                                <td>${naP}%</td>
                            </tr>
                            """
                        }

                        html += "</table>"
                    }

                    // ===============================
                    // 시나리오 분석
                    // ===============================
                    html += "<h2>📌 4. 시나리오 실패 비율</h2>"

                    scenarioMap.each { s, v ->

                        def failRateS = (v.fail * 100 / v.total).round(2)

                        html += """
                        <div class="box">
                            <b>${s}</b><br>
                            Fail Rate: ${failRateS}%
                        </div>
                        """
                    }

                    // ===============================
                    // Fail 상세
                    // ===============================
                    html += "<h2>📌 5. 결함 상세</h2>"
                    html += "<table><tr><th>대분류</th><th>중분류</th><th>시나리오</th><th>결과</th></tr>"

                    fails.each {
                        html += """
                        <tr>
                            <td>${it.major}</td>
                            <td>${it.minor}</td>
                            <td>${it.scenario}</td>
                            <td class="fail">FAIL</td>
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
                def RESULT_DIR = "${params.BASE_PATH}\\Test Results"

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
            slackSend(channel: "#새-채널", message: "❌ QA 실패 발생")
        }
    }
}