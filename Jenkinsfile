pipeline {
    agent any

    parameters {
        string(name: 'WORKSPACE_PATH', defaultValue: '', description: 'C:\\파일경로')
    }

    environment {
        WORKSPACE_PATH = "${params.WORKSPACE_PATH}"
        RESULT_DIR = "${WORKSPACE_PATH}\\Test Results"
        TEST_DIR = "${WORKSPACE_PATH}\\Tests"
        REPORT_FILE = "${RESULT_DIR}\\qa_report.html"
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

        stage('QA Analysis (Sheet Based Multi CSV)') {
            steps {
                script {

                    // =========================
                    // CSV 목록 (PowerShell)
                    // =========================
                    def csvListRaw = bat(
                        script: """
                        powershell -Command "Get-ChildItem '${TEST_DIR}' -Filter '*.csv' | Select-Object -Expand FullName"
                        """,
                        returnStdout: true
                    ).trim()

                    def csvFiles = csvListRaw.split("\\r?\\n")

                    if (csvFiles.length == 0 || csvFiles[0] == "") {
                        error "CSV 없음"
                    }

                    // =========================
                    // 전체 데이터
                    // =========================
                    def all = []

                    def parseCsv = { line ->
                        def res = []
                        def sb = new StringBuilder()
                        boolean inQ = false

                        for (int i = 0; i < line.length(); i++) {
                            char c = line.charAt(i)

                            if (c == '"') inQ = !inQ
                            else if (c == ',' && !inQ) {
                                res << sb.toString().trim()
                                sb.setLength(0)
                            } else {
                                sb.append(c)
                            }
                        }
                        res << sb.toString().trim()
                        return res
                    }

                    // =========================
                    // CSV 로딩
                    // =========================
                    csvFiles.each { filePath ->

                        def content = readFile(filePath)
                        def lines = content.split("\\r?\\n")

                        for (int i = 1; i < lines.size(); i++) {

                            def line = lines[i].trim()
                            if (!line) continue

                            def cols = parseCsv(line)
                            if (cols.size() <= 6) continue

                            all << [
                                file: filePath.tokenize("\\").last(),
                                sheet: cols[0],
                                major: cols[1],
                                minor: cols[2],
                                scenario: cols[3],
                                action: cols[4],
                                result: cols[6]
                            ]
                        }
                    }

                    // =========================
                    // normalize
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

                    all.each {
                        it.result = norm(it.result)
                    }

                    // =========================
                    // 전체 통계
                    // =========================
                    def stats = [Total:0, PASS:0, FAIL:0, BLOCKED:0, "NOT TEST":0, "N/A":0]

                    all.each {
                        stats.Total++
                        stats[it.result] = (stats[it.result] ?: 0) + 1
                    }

                    // =========================
                    // SHEET GROUP
                    // =========================
                    def sheetMap = [:]

                    all.each {
                        def key = it.sheet

                        if (!sheetMap[key]) sheetMap[key] = []
                        sheetMap[key] << it
                    }

                    // =========================
                    // TC FAIL 비율
                    // =========================
                    def tcFail = [:]

                    all.each {
                        def key = it.sheet + "|" + it.scenario

                        if (!tcFail[key]) {
                            tcFail[key] = [
                                sheet: it.sheet,
                                scenario: it.scenario,
                                total:0,
                                fail:0
                            ]
                        }

                        def g = tcFail[key]
                        g.total++
                        if (it.result == "FAIL") g.fail++
                    }

                    // =========================
                    // FAIL 상세
                    // =========================
                    def defects = all.findAll { it.result == "FAIL" }

                    // =========================
                    // HTML START
                    // =========================
                    def html = """
                    <html>
                    <body>
                    <h1>QA REPORT</h1>

                    <h3>📌 Summary</h3>
                    <p>Test Files: ${csvFiles.length}</p>

                    <table border="1">
                    <tr><th>Type</th><th>Count</th><th>Progress</th></tr>
                    """

                    stats.each { k,v ->
                        def rate = stats.Total > 0 ? (v*100.0/stats.Total) : 0
                        html += "<tr><td>${k}</td><td>${v}</td><td>${String.format('%.2f',rate)}%</td></tr>"
                    }

                    html += "</table><br/>"

                    // =========================
                    // SHEET TABLES
                    // =========================
                    sheetMap.each { sheet, list ->

                        def group = [:]

                        list.each {
                            def key = it.major + "|" + it.minor

                            if (!group[key]) {
                                group[key] = [
                                    major: it.major,
                                    minor: it.minor,
                                    PASS:0,
                                    FAIL:0,
                                    BLOCKED:0,
                                    "NOT TEST":0,
                                    "N/A":0
                                ]
                            }

                            def g = group[key]
                            g[it.result] = (g[it.result] ?: 0) + 1
                        }

                        html += """
                        <h2>📄 Sheet: ${sheet}</h2>

                        <table border="1">
                        <tr>
                            <th>Major</th>
                            <th>Minor</th>
                            <th>PASS</th>
                            <th>FAIL</th>
                            <th>BLOCKED</th>
                            <th>NOT TEST</th>
                            <th>N/A</th>
                        </tr>
                        """

                        group.values().each {
                            html += """
                            <tr>
                                <td>${it.major}</td>
                                <td>${it.minor}</td>
                                <td>${it.PASS}</td>
                                <td>${it.FAIL}</td>
                                <td>${it.BLOCKED}</td>
                                <td>${it["NOT TEST"]}</td>
                                <td>${it["N/A"]}</td>
                            </tr>
                            """
                        }

                        html += "</table><br/>"
                    }

                    // =========================
                    // TC FAIL TABLE
                    // =========================
                    html += """
                    <h2>📉 TC FAIL Ratio</h2>
                    <table border="1">
                    <tr><th>Sheet</th><th>Scenario</th><th>Fail %</th></tr>
                    """

                    tcFail.values().each {
                        def rate = it.total > 0 ? (it.fail*100.0/it.total) : 0
                        html += "<tr><td>${it.sheet}</td><td>${it.scenario}</td><td>${String.format('%.1f',rate)}%</td></tr>"
                    }

                    html += "</table>"

                    // =========================
                    // DEFECT TABLE
                    // =========================
                    html += """
                    <h2>❌ Defects</h2>
                    <table border="1">
                    <tr><th>Sheet</th><th>Major</th><th>Minor</th><th>Action</th></tr>
                    """

                    defects.each {
                        html += """
                        <tr>
                            <td>${it.sheet}</td>
                            <td>${it.major}</td>
                            <td>${it.minor}</td>
                            <td>${it.action}</td>
                        </tr>
                        """
                    }

                    html += "</table></body></html>"

                    writeFile file: REPORT_FILE, text: html

                    echo "[DONE] TOTAL=${stats.Total}, FAIL=${stats.FAIL}"
                }
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'Test Results/**'
        }
    }
}