pipeline {
    agent any

    parameters {
        string(name: 'WORKSPACE_PATH', defaultValue: '', description: 'C:\\QA 경로')
    }

    environment {
        PROJECT_NAME = "QA REPORT"
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

        stage('QA Analysis (Multi CSV)') {
            steps {
                script {

                    def files = findFiles(glob: "${TEST_DIR}/*.csv")
                    if (files.length == 0) {
                        error "CSV 없음"
                    }

                    def allResults = []

                    // =========================
                    // CSV SAFE PARSER
                    // =========================
                    def parseCsv = { line ->
                        def out = []
                        def sb = new StringBuilder()
                        boolean q = false

                        for (int i = 0; i < line.length(); i++) {
                            def c = line.charAt(i)

                            if (c == '"') q = !q
                            else if (c == ',' && !q) {
                                out << sb.toString().trim()
                                sb.setLength(0)
                            } else {
                                sb.append(c)
                            }
                        }
                        out << sb.toString().trim()
                        return out
                    }

                    // =========================
                    // CSV LOAD
                    // =========================
                    files.each { f ->
                        def content = readFile("${TEST_DIR}/${f.name}")
                        def lines = content.split("\\r?\\n")

                        for (int i = 1; i < lines.size(); i++) {
                            def line = lines[i].trim()
                            if (!line) continue

                            def cols = parseCsv(line)
                            if (cols.size() <= 6) continue

                            allResults << [
                                sheet: f.name.replace(".csv",""),
                                major: cols[0],
                                minor: cols[1],
                                scenario: cols[2],
                                action: cols[3],
                                result: cols[6]
                            ]
                        }
                    }

                    // =========================
                    // NORMALIZE
                    // =========================
                    def norm = { r ->
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

                    allResults.each {
                        it.result = norm(it.result)
                    }

                    // =========================
                    // TOTAL STATS
                    // =========================
                    def stats = [
                        Total: allResults.size(),
                        PASS: 0,
                        FAIL: 0,
                        BLOCKED: 0,
                        "NOT TEST": 0,
                        "N/A": 0
                    ]

                    allResults.each {
                        stats[it.result] = (stats[it.result] ?: 0) + 1
                    }

                    // =========================
                    // ① 대/중분류
                    // =========================
                    def group = [:]

                    allResults.each {
                        def key = "${it.sheet}|${it.major}|${it.minor}"

                        if (!group[key]) {
                            group[key] = [
                                sheet: it.sheet,
                                major: it.major,
                                minor: it.minor,
                                pass: 0,
                                fail: 0,
                                blocked: 0,
                                nottest: 0,
                                na: 0,
                                total: 0
                            ]
                        }

                        def g = group[key]
                        g.total++

                        switch(it.result) {
                            case "PASS": g.pass++; break
                            case "FAIL": g.fail++; break
                            case "BLOCKED": g.blocked++; break
                            case "NOT TEST": g.nottest++; break
                            case "N/A": g.na++; break
                        }
                    }

                    // =========================
                    // ② TC FAIL 비율
                    // =========================
                    def tcMap = [:]

                    allResults.each {
                        def key = it.sheet + "|" + it.scenario

                        if (!tcMap[key]) {
                            tcMap[key] = [sheet: it.sheet, scenario: it.scenario, total: 0, fail: 0]
                        }

                        tcMap[key].total++
                        if (it.result == "FAIL") tcMap[key].fail++
                    }

                    def tcTable = tcMap.values().collect {
                        [
                            sheet: it.sheet,
                            scenario: it.scenario,
                            rate: it.total > 0 ? (it.fail * 100.0 / it.total) : 0
                        ]
                    }

                    // =========================
                    // ③ DEFECTS
                    // =========================
                    def defects = allResults.findAll { it.result == "FAIL" }

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
                        th, td { border:1px solid #ddd; padding:8px; text-align:center; }
                        th { background:#222; color:white; }
                        .fail { background:#ffe5e5; }
                    </style>
                    </head>
                    <body>

                    <h2>${PROJECT_NAME}</h2>

                    <h3>테스트 파일</h3>
                    <p>${files.collect { it.name }.join(", ")}</p>

                    <h3>전체 결과</h3>
                    <table>
                        <tr><th>Type</th><th>Count</th><th>Progress</th></tr>
                    """

                    def total = stats.Total

                    stats.each { k,v ->
                        if (k == "Total") return
                        def rate = total > 0 ? (v * 100.0 / total) : 0
                        html += "<tr><td>${k}</td><td>${v}</td><td>${String.format('%.2f', rate)}%</td></tr>"
                    }

                    html += """
                    </table>

                    <h3>대/중분류 테스트 현황</h3>
                    <table>
                        <tr>
                            <th>Sheet</th>
                            <th>대분류</th>
                            <th>중분류</th>
                            <th>Pass</th>
                            <th>Fail</th>
                            <th>Blocked</th>
                            <th>Not Test</th>
                            <th>N/A</th>
                        </tr>
                    """

                    group.values().each {
                        html += """
                        <tr>
                            <td>${it.sheet}</td>
                            <td>${it.major}</td>
                            <td>${it.minor}</td>
                            <td>${it.pass}</td>
                            <td>${it.fail}</td>
                            <td>${it.blocked}</td>
                            <td>${it.nottest}</td>
                            <td>${it.na}</td>
                        </tr>
                        """
                    }

                    html += """
                    </table>

                    <h3>TC 실패 비율</h3>
                    <table>
                        <tr><th>Sheet</th><th>TC</th><th>Fail %</th></tr>
                    """

                    tcTable.each {
                        html += "<tr><td>${it.sheet}</td><td>${it.scenario}</td><td>${String.format('%.1f', it.rate)}%</td></tr>"
                    }

                    html += """
                    </table>

                    <h3>결함 목록</h3>
                    <table>
                        <tr><th>No</th><th>Sheet</th><th>대분류</th><th>중분류</th><th>Action</th></tr>
                    """

                    int idx = 1
                    defects.each {
                        html += """
                        <tr class="fail">
                            <td>${idx++}</td>
                            <td>${it.sheet}</td>
                            <td>${it.major}</td>
                            <td>${it.minor}</td>
                            <td>${it.action}</td>
                        </tr>
                        """
                    }

                    html += "</table></body></html>"

                    writeFile file: "${RESULT_DIR}\\qa_report.html", text: html

                    currentBuild.result = "SUCCESS"

                    echo "TOTAL=${stats.Total}"
                    echo "FAIL=${stats.FAIL}"
                }
            }
        }
    }

    post {
        success {
            slackSend channel: '#새-채널',
                color: 'good',
                message: "✅ QA 완료"
        }

        failure {
            slackSend channel: '#새-채널',
                color: 'danger',
                message: "❌ QA 실패"
        }

        always {
            archiveArtifacts artifacts: 'Test Results/**'
        }
    }
}