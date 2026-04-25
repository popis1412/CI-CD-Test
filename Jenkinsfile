pipeline {
    agent any

    parameters {
        string(name: 'WORKSPACE_PATH', defaultValue: '', description: 'C:\\파일경로')
    }

    environment {
        WORKSPACE_PATH = "${params.WORKSPACE_PATH}"
        RESULT_DIR = "${WORKSPACE_PATH}\\Test Results"
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

                    if (!fileExists(TEST_FILE_PATH)) {
                        error "CSV 없음"
                    }

                    def lines = readFile(TEST_FILE_PATH).split("\\r?\\n")

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
                    // DATA LOAD
                    // =========================
                    def all = []

                    for (int i = 1; i < lines.size(); i++) {
                        def line = lines[i].trim()
                        if (!line) continue

                        def cols = parseCsv(line)
                        if (cols.size() < 7) continue

                        def scenario = cols[3]

                        // TC 기준 분리 (핵심)
                        def sheet =
                                scenario?.toLowerCase()?.contains("battle") ? "TC_Battle" :
                                scenario?.toLowerCase()?.contains("test") ? "TC_Test" :
                                "UNKNOWN"

                        all << [
                            sheet: sheet,
                            major: cols[1],
                            minor: cols[2],
                            scenario: cols[3],
                            action: cols[4],
                            result: cols[6]
                        ]
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

                    all.each { it.result = norm(it.result) }

                    // =========================
                    // TOTAL STATS
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
                        if (!sheetMap[it.sheet]) sheetMap[it.sheet] = []
                        sheetMap[it.sheet] << it
                    }

                    // =========================
                    // HTML
                    // =========================
                    def html = """
<html>
<head>
<style>
body { font-family: Arial; padding:20px; background:#f5f5f5; }
h1 { color:#222; }

table {
    border-collapse: collapse;
    width:100%;
    margin-bottom:30px;
    background:white;
    box-shadow:0 2px 5px rgba(0,0,0,0.1);
}

th {
    background:#2c3e50;
    color:white;
    padding:10px;
}

td {
    border:1px solid #ddd;
    padding:8px;
    text-align:center;
}

tr:nth-child(even) {
    background:#f9f9f9;
}

.fail {
    background:#ffdddd !important;
}

.pass {
    background:#ddffdd;
}
</style>
</head>
<body>

<h1>QA REPORT</h1>

<h3>📌 Summary</h3>
<p>Test File: QA_Test.csv</p>
<p>Build Date: ${new Date().format("yyyy-MM-dd HH:mm:ss")}</p>

<table>
<tr><th>Type</th><th>Count</th><th>Progress</th></tr>
"""

                    stats.each { k,v ->
                        def rate = stats.Total > 0 ? (v*100.0/stats.Total) : 0
                        html += "<tr><td>${k}</td><td>${v}</td><td>${String.format('%.2f',rate)}%</td></tr>"
                    }

                    html += "</table>"

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

                            group[key][it.result] = (group[key][it.result] ?: 0) + 1
                        }

                        html += "<h2>${sheet} (${list.size()}개)</h2>"
                        html += """
<table>
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

                        html += "</table>"
                    }

                    html += "</body></html>"

                    writeFile file: REPORT_FILE, text: html

                    echo "[DONE] TOTAL=${stats.Total}"
                }
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: '**/Test Results/**'
        }
    }
}