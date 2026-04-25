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

        stage('QA Analysis (Multi CSV)') {
            steps {
                script {

                    def files = findFiles(glob: "${TEST_DIR}\\*.csv")

                    if (files.length == 0) {
                        error "CSV 없음"
                    }

                    def allData = []

                    // =========================
                    // CSV SAFE PARSER
                    // =========================
                    def parseCsvLine = { line ->
                        def result = []
                        def sb = new StringBuilder()
                        boolean inQuotes = false

                        for (int i = 0; i < line.length(); i++) {
                            char c = line.charAt(i)

                            if (c == '"') inQuotes = !inQuotes
                            else if (c == ',' && !inQuotes) {
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
                    // LOAD ALL CSV FILES
                    // =========================
                    files.each { f ->

                        def content = readFile(f.path)
                        def lines = content.split("\\r?\\n")

                        for (int i = 1; i < lines.size(); i++) {

                            def line = lines[i].trim()
                            if (!line) continue

                            def cols = parseCsvLine(line)
                            if (cols.size() <= 6) continue

                            allData << [
                                file: f.name,              // "시트 이름"
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
                    // TOTAL STATS
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
                    // FILE (SHEET) BASED TABLE
                    // =========================
                    def sheetMap = [:]

                    allData.each { t ->
                        def key = t.file

                        if (!sheetMap[key]) {
                            sheetMap[key] = [
                                file: key,
                                rows: [:]
                            ]
                        }

                        def groupKey = "${t.major}|${t.minor}"

                        if (!sheetMap[key].rows[groupKey]) {
                            sheetMap[key].rows[groupKey] = [
                                major: t.major,
                                minor: t.minor,
                                PASS: 0,
                                FAIL: 0,
                                BLOCKED: 0,
                                "NOT TEST": 0,
                                "N/A": 0
                            ]
                        }

                        sheetMap[key].rows[groupKey][t.result]++
                    }

                    // =========================
                    // FAIL BY TC (PER FILE)
                    // =========================
                    def failByTC = [:]

                    allData.each {
                        if (it.result == "FAIL") {
                            def key = "${it.file}|${it.scenario}"
                            failByTC[key] = (failByTC[key] ?: 0) + 1
                        }
                    }

                    // =========================
                    // DEFECT LIST
                    // =========================
                    def defects = allData.findAll { it.result == "FAIL" }

                    // =========================
                    // HTML
                    // =========================
                    def html = """
                    <html>
                    <head>
                        <meta charset="UTF-8">
                        <style>
                            body { font-family: Arial; padding:20px; }
                            table { border-collapse: collapse; width:100%; margin-bottom:30px; }
                            th, td { border:1px solid #ddd; padding:6px; text-align:center; }
                            th { background:#333; color:white; }
                        </style>
                    </head>
                    <body>

                    <h2>QA SUMMARY</h2>

                    <p><b>테스트 파일</b>: ${files.collect { it.name }.join(', ')}</p>
                    <p><b>빌드 날짜</b>: ${new Date().format("yyyy-MM-dd HH:mm")}</p>

                    <h3>전체 테스트 결과</h3>
                    <table>
                        <tr>
                            <th>Type</th><th>Count</th><th>Progress</th>
                        </tr>
                    """

                    stats.each { k, v ->
                        def pct = stats.Total > 0 ? (v * 100.0 / stats.Total) : 0
                        html += "<tr><td>${k}</td><td>${v}</td><td>${String.format('%.2f', pct)}%</td></tr>"
                    }

                    html += "</table>"

                    // =========================
                    // FILE BASED TABLE (REQUESTED FORMAT)
                    // =========================
                    sheetMap.each { fileName, data ->

                        html += "<h3>📄 ${fileName}</h3>"
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

                        data.rows.each { k, v ->
                            html += """
                            <tr>
                                <td>${v.major}</td>
                                <td>${v.minor}</td>
                                <td>${v.PASS}</td>
                                <td>${v.FAIL}</td>
                                <td>${v.BLOCKED}</td>
                                <td>${v['NOT TEST']}</td>
                                <td>${v['N/A']}</td>
                            </tr>
                            """
                        }

                        html += "</table>"
                    }

                    // =========================
                    // FAIL TC TABLE
                    // =========================
                    html += "<h3>TC Fail Ratio</h3><table><tr><th>Sheet</th><th>TC</th><th>Fail Count</th></tr>"

                    failByTC.each { k, v ->
                        def parts = k.split("\\|")
                        html += "<tr><td>${parts[0]}</td><td>${parts[1]}</td><td>${v}</td></tr>"
                    }

                    html += "</table>"

                    // =========================
                    // DEFECT LIST
                    // =========================
                    html += "<h3>Defects</h3>"
                    html += "<table><tr><th>Sheet</th><th>대분류</th><th>중분류</th><th>Action</th></tr>"

                    defects.each {
                        html += "<tr><td>${it.file}</td><td>${it.major}</td><td>${it.minor}</td><td>${it.action}</td></tr>"
                    }

                    html += "</table></body></html>"

                    writeFile file: "${RESULT_DIR}\\qa_report.html", text: html

                    echo "[INFO] TOTAL=${stats.Total}"
                    echo "[INFO] FAIL=${stats.FAIL}"
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