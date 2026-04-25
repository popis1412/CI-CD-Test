pipeline {
    agent any

    parameters {
        string(name: 'WORKSPACE_PATH', defaultValue: '', description: 'C:\\파일경로')
    }

    environment {
        WORKSPACE_PATH = "${params.WORKSPACE_PATH}"
        RESULT_DIR = "${env.WORKSPACE}\\Test Results"
        TEST_FILE_PATH = "${WORKSPACE_PATH}\\Tests\\QA_Test.csv"
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

        stage('QA Analysis') {
            steps {
                script {

                    // =========================
                    // CSV 체크
                    // =========================
                    if (!fileExists(TEST_FILE_PATH)) {
                        error "QA_Test.csv 없음"
                    }

                    def content = readFile(TEST_FILE_PATH)
                    def lines = content.split("\\r?\\n")

                    // =========================
                    // CSV PARSER (Excel 대응)
                    // =========================
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
                    // 데이터 로딩
                    // =========================
                    def all = []

                    for (int i = 1; i < lines.size(); i++) {
                        def line = lines[i].trim()
                        if (!line) continue

                        def cols = parseCsv(line)
                        if (cols.size() <= 6) continue

                        all << [
                            sheet: cols[0],
                            major: cols[1],
                            minor: cols[2],
                            scenario: cols[3],
                            action: cols[4],
                            result: cols[6]
                        ]
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

                    all.each { it.result = norm(it.result) }

                    // =========================
                    // 전체 통계 (정확)
                    // =========================
                    def stats = [
                        Total: 0,
                        PASS: 0,
                        FAIL: 0,
                        BLOCKED: 0,
                        "NOT TEST": 0,
                        "N/A": 0
                    ]

                    all.each {
                        stats.Total++
                        stats[it.result] = (stats[it.result] ?: 0) + 1
                    }

                    // =========================
                    // 시트별 그룹 (엑셀 Sheet 기준)
                    // =========================
                    def sheetMap = [:]

                    all.each {
                        if (!sheetMap[it.sheet]) sheetMap[it.sheet] = []
                        sheetMap[it.sheet] << it
                    }

                    // =========================
                    // TC Fail 비율 (시트 기준)
                    // =========================
                    def tcFail = [:]

                    all.each {
                        def key = it.sheet + "|" + it.scenario

                        if (!tcFail[key]) {
                            tcFail[key] = [
                                sheet: it.sheet,
                                scenario: it.scenario,
                                total: 0,
                                fail: 0
                            ]
                        }

                        def g = tcFail[key]
                        g.total++
                        if (it.result == "FAIL") g.fail++
                    }

                    // =========================
                    // Defect (FAIL만)
                    // =========================
                    def defects = all.findAll { it.result == "FAIL" }

                    // =========================
                    // HTML START
                    // =========================
                    def html = """
                    <html>
                    <head>
                        <meta charset="UTF-8">
                        <style>
                            body { font-family: Arial; padding:20px; }

                            table {
                                border-collapse: collapse;
                                width: 100%;
                                margin-bottom: 30px;
                            }

                            th {
                                background: #222;
                                color: white;
                                padding: 8px;
                            }

                            td {
                                border: 1px solid #ddd;
                                padding: 6px;
                                text-align: center;
                            }

                            tr:nth-child(even) { background: #f5f5f5; }

                            .fail { background: #ffd6d6; }
                        </style>
                    </head>
                    <body>

                    <h1>QA REPORT</h1>

                    <h3>📌 기본 정보</h3>
                    <p>테스트 파일 : QA_Test.csv</p>
                    <p>빌드 날짜 : ${new Date().format("yyyy-MM-dd HH:mm:ss")}</p>

                    <h3>📊 전체 테스트 결과</h3>

                    <table>
                        <tr>
                            <th>Type</th>
                            <th>Count</th>
                            <th>Progress</th>
                        </tr>
                    """

                    stats.each { k, v ->
                        def rate = stats.Total > 0 ? (v * 100.0 / stats.Total) : 0
                        html += """
                        <tr>
                            <td>${k}</td>
                            <td>${v}</td>
                            <td>${String.format('%.2f', rate)}%</td>
                        </tr>
                        """
                    }

                    html += "</table>"

                    // =========================
                    // 시트별 결과
                    // =========================
                    sheetMap.each { sheet, list ->

                        def group = [:]

                        list.each {
                            def key = it.major + "|" + it.minor

                            if (!group[key]) {
                                group[key] = [
                                    major: it.major,
                                    minor: it.minor,
                                    PASS: 0,
                                    FAIL: 0,
                                    BLOCKED: 0,
                                    "NOT TEST": 0,
                                    "N/A": 0,
                                    total: 0
                                ]
                            }

                            def g = group[key]
                            g.total++
                            g[it.result] = (g[it.result] ?: 0) + 1
                        }

                        html += """
                        <h2>📄 시트: ${sheet}</h2>

                        <table>
                        <tr>
                            <th>대분류</th>
                            <th>중분류</th>
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

                        html += "</table>"
                    }

                    // =========================
                    // TC FAIL 비율
                    // =========================
                    html += """
                    <h2>📉 TC 실패 비율</h2>

                    <table>
                    <tr>
                        <th>시트</th>
                        <th>TC</th>
                        <th>Fail %</th>
                    </tr>
                    """

                    tcFail.values().each {
                        def rate = it.total > 0 ? (it.fail * 100.0 / it.total) : 0

                        html += """
                        <tr>
                            <td>${it.sheet}</td>
                            <td>${it.scenario}</td>
                            <td>${String.format('%.1f', rate)}%</td>
                        </tr>
                        """
                    }

                    html += "</table>"

                    // =========================
                    // Defect
                    // =========================
                    html += """
                    <h2>❌ 결함 목록</h2>

                    <table>
                    <tr>
                        <th>시트</th>
                        <th>대분류</th>
                        <th>중분류</th>
                        <th>액션</th>
                    </tr>
                    """

                    defects.each {
                        html += """
                        <tr class="fail">
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