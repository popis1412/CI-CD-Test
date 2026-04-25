pipeline {
    agent any

    parameters {
        string(name: 'WORKSPACE_PATH', defaultValue: '', description: 'C:\\QA_PATH')
    }

    environment {
        WORKSPACE_PATH = "${params.WORKSPACE_PATH}"
        RESULT_DIR = "${params.WORKSPACE_PATH}\\Test Results"
        TEST_DIR = "${params.WORKSPACE_PATH}\\Tests"
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

        stage('QA Analysis (Multi CSV Safe)') {
            steps {
                script {

                    // =========================
                    // CSV FILE LIST (NO PLUGIN)
                    // =========================
                    def files = []

                    def result = bat(
                        script: "dir /b \"${TEST_DIR}\\\\*.csv\"",
                        returnStdout: true
                    ).trim()

                    if (!result) {
                        error "CSV 파일 없음"
                    }

                    result.split("\\r?\\n").each {
                        if (it?.trim()) files << it.trim()
                    }

                    def allData = []

                    // =========================
                    // SAFE CSV PARSER
                    // =========================
                    def parseCsvLine = { line ->
                        def result = []
                        def sb = new StringBuilder()
                        boolean inQuotes = false

                        for (int i = 0; i < line.length(); i++) {
                            char c = line.charAt(i)

                            if (c == '"') {
                                inQuotes = !inQuotes
                            } else if (c == ',' && !inQuotes) {
                                result << sb.toString().trim()
                                sb.setLength(0)
                            } else {
                                sb.append(c)
                            }
                        }

                        result << sb.toString().trim()
                        return result
                    }

                    // =========================
                    // LOAD MULTI CSV
                    // =========================
                    files.each { fileName ->

                        def path = "${TEST_DIR}\\${fileName}"
                        def content = readFile(path)
                        def lines = content.split("\\r?\\n")

                        for (int i = 1; i < lines.size(); i++) {

                            def line = lines[i].trim()
                            if (!line) continue

                            def cols = parseCsvLine(line)
                            if (cols.size() <= 6) continue

                            allData << [
                                file: fileName,
                                major: cols[0],
                                minor: cols[1],
                                scenario: cols[2],
                                action: cols[3],
                                result: cols[6]
                            ]
                        }
                    }

                    // =========================
                    // NORMALIZE RESULT
                    // =========================
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

                    allData.each {
                        it.result = normalize(it.result)
                    }

                    // =========================
                    // TOTAL STATS (%)
                    // =========================
                    def stats = [
                        Total: 0,
                        PASS: 0,
                        FAIL: 0,
                        BLOCKED: 0,
                        "NOT TEST": 0,
                        "N/A": 0
                    ]

                    allData.each {
                        stats.Total++
                        stats[it.result] = (stats[it.result] ?: 0) + 1
                    }

                    // =========================
                    // GROUP BY MAJOR / MINOR
                    // =========================
                    def groupMap = [:]

                    allData.each { t ->
                        def key = "${t.major}|${t.minor}"

                        if (!groupMap[key]) {
                            groupMap[key] = [
                                major: t.major,
                                minor: t.minor,
                                PASS: 0,
                                FAIL: 0,
                                BLOCKED: 0,
                                "NOT TEST": 0,
                                "N/A": 0
                            ]
                        }

                        groupMap[key][t.result]++
                    }

                    // =========================
                    // FAIL SCENARIO RATIO
                    // =========================
                    def failByScenario = [:]

                    allData.findAll { it.result == "FAIL" }.each {
                        failByScenario[it.scenario] = (failByScenario[it.scenario] ?: 0) + 1
                    }

                    def failScenarioTable = failByScenario.collect { k, v ->
                        [
                            scenario: k,
                            rate: stats.FAIL > 0 ? (v * 100.0 / stats.FAIL) : 0
                        ]
                    }

                    // =========================
                    // DEFECT LIST
                    // =========================
                    def defects = allData.findAll { it.result == "FAIL" }

                    def buildDate = new Date().format("yyyy-MM-dd HH:mm")

                    // =========================
                    // HTML REPORT
                    // =========================
                    def html = """
                    <html>
                    <head>
                        <meta charset="UTF-8">
                        <style>
                            body { font-family: Arial; padding:20px; }
                            table { border-collapse: collapse; width:100%; margin-bottom:30px; }
                            th, td { border:1px solid #ddd; padding:6px; text-align:center; }
                            th { background:#222; color:white; }
                        </style>
                    </head>
                    <body>

                    <h2>QA REPORT</h2>

                    <p><b>테스트 파일</b>: ${files.join(', ')}</p>
                    <p><b>빌드 날짜</b>: ${buildDate}</p>

                    <h3>전체 테스트 결과</h3>
                    <table>
                        <tr><th>Type</th><th>Count</th><th>Rate</th></tr>
                    """

                    stats.each { k, v ->
                        def rate = stats.Total > 0 ? (v * 100.0 / stats.Total) : 0
                        html += "<tr><td>${k}</td><td>${v}</td><td>${String.format('%.2f', rate)}%</td></tr>"
                    }

                    html += "</table>"

                    // =========================
                    // GROUP TABLE (REQUEST FORMAT)
                    // =========================
                    html += "<h3>대/중분류 테스트 현황</h3>"
                    html += """
                    <table>
                        <tr>
                            <th>대분류</th>
                            <th>중분류</th>
                            <th>Pass</th>
                            <th>Fail</th>
                            <th>Blocked</th>
                            <th>Not Test</th>
                            <th>N/A</th>
                        </tr>
                    """

                    groupMap.values().each { g ->
                        html += """
                        <tr>
                            <td>${g.major}</td>
                            <td>${g.minor}</td>
                            <td>${g.PASS}</td>
                            <td>${g.FAIL}</td>
                            <td>${g.BLOCKED}</td>
                            <td>${g['NOT TEST']}</td>
                            <td>${g['N/A']}</td>
                        </tr>
                        """
                    }

                    html += "</table>"

                    // =========================
                    // FAIL SCENARIO TABLE
                    // =========================
                    html += "<h3>TC Fail 비율</h3>"
                    html += "<table><tr><th>TC</th><th>Fail Rate</th></tr>"

                    failScenarioTable.each {
                        html += "<tr><td>${it.scenario}</td><td>${String.format('%.1f', it.rate)}%</td></tr>"
                    }

                    html += "</table>"

                    // =========================
                    // DEFECT TABLE
                    // =========================
                    html += "<h3>Defects</h3>"
                    html += "<table><tr><th>시트</th><th>대분류</th><th>중분류</th><th>Action</th></tr>"

                    defects.each {
                        html += "<tr><td>${it.file}</td><td>${it.major}</td><td>${it.minor}</td><td>${it.action}</td></tr>"
                    }

                    html += "</table></body></html>"

                    writeFile file: "${RESULT_DIR}\\qa_report.html", text: html

                    // =========================
                    // SLACK MESSAGE (SUCCESS ONLY)
                    // =========================
                    def slackMsg = """
QA 완료

Total: ${stats.Total}
Fail: ${stats.FAIL}

Report 생성 완료
"""

                    env.SLACK_MSG = slackMsg

                    echo "[INFO] TOTAL=${stats.Total}"
                    echo "[INFO] FAIL=${stats.FAIL}"
                }
            }
        }
    }

    post {
        always {
            slackSend channel: '#새-채널',
                color: (env.SLACK_MSG?.contains("Fail: 0") ? "good" : "danger"),
                message: env.SLACK_MSG

            archiveArtifacts artifacts: 'Test Results/**'
        }
    }
}