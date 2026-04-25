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

                    for (int i = 1; i < lines.size(); i++) {

                        def cols = lines[i].split(",")

                        if (cols.size() >= 4) {
                            testResults << [
                                row: i + 1,
                                col: "D",
                                major: cols[0],
                                minor: cols[1],
                                scenario: cols[2],
                                result: cols[3]
                            ]
                        }
                    }

                    // 🔥 통계
                    def stats = [:]
                    def total = 0
                    def totalFail = 0

                    testResults.each { t ->
                        if(!stats[t.major]) stats[t.major] = [total:0, pass:0, fail:0]

                        stats[t.major].total++
                        total++

                        if(t.result == "PASS") stats[t.major].pass++
                        else if(t.result == "FAIL") {
                            stats[t.major].fail++
                            totalFail++
                        }
                    }

                    def failRate = total > 0 ? (totalFail * 100 / total).toInteger() : 0

                    // 🔥 실패 목록
                    def fails = testResults.findAll { it.result == "FAIL" }

                    // 🔥 HTML (기획서 스타일)
                    def html = """
                    <html>
                    <head>
                    <meta charset="UTF-8">
                    <style>
                        body { font-family: 'Malgun Gothic'; background:#f4f6f8; padding:40px; }
                        .card { background:white; padding:40px; border-radius:10px; }
                        h1 { border-bottom:3px solid #333; }
                        h2 { border-left:5px solid #333; padding-left:10px; margin-top:30px; }
                        table { width:100%; border-collapse: collapse; margin-top:15px; }
                        th, td { border:1px solid #ddd; padding:10px; text-align:center; }
                        th { background:#eee; }
                        .fail { color:red; font-weight:bold; }
                        .pass { color:green; }
                        .box { background:#fff3cd; padding:15px; margin-top:10px; }
                    </style>
                    </head>
                    <body>
                    <div class="card">

                    <h1>${env.PROJECT_NAME} 분석 리포트</h1>

                    <h2>📌 1. 개요</h2>
                    <p>경로: ${RESULT_DIR}</p>
                    <p>실행 시간: ${new Date()}</p>

                    <h2>📊 2. 전체 품질 지표</h2>
                    <div class="box">
                        총 테스트: ${total}건<br>
                        실패 건수: ${totalFail}건<br>
                        전체 실패율: ${failRate}%
                    </div>

                    <h2>📊 3. 분류별 품질 분석</h2>
                    <table>
                    <tr><th>대분류</th><th>Total</th><th>Pass</th><th>Fail</th><th>실패율</th></tr>
                    """

                    stats.each { k, v ->
                        def r = (v.fail * 100 / v.total).toInteger()
                        html += """
                        <tr>
                            <td>${k}</td>
                            <td>${v.total}</td>
                            <td class='pass'>${v.pass}</td>
                            <td class='fail'>${v.fail}</td>
                            <td>${r}%</td>
                        </tr>
                        """
                    }

                    html += "</table>"

                    // 🔥 결함 분석 (포트폴리오 스타일)
                    html += "<h2>🧠 4. 결함 분석</h2><ul>"

                    fails.each {
                        html += """
                        <li>
                        <b>${it.major} > ${it.minor}</b><br>
                        - 시나리오: ${it.scenario}<br>
                        - 문제: 해당 기능 수행 시 정상 흐름이 유지되지 않음<br>
                        - 영향: 사용자 경험 저하 및 게임 진행 불안정<br>
                        - 조치 필요: 로직 검증 및 상태 전이 조건 점검 필요
                        </li><br>
                        """
                    }

                    html += "</ul>"

                    // 🔥 실패 위치 표
                    html += """
                    <h2>⚠️ 5. 실패 위치 상세</h2>
                    <table>
                    <tr><th>위치</th><th>경로</th></tr>
                    """

                    fails.each {
                        html += """
                        <tr>
                            <td>${it.row}행 / ${it.col}열</td>
                            <td>${it.major} > ${it.minor} > ${it.scenario}</td>
                        </tr>
                        """
                    }

                    html += "</table></div></body></html>"

                    writeFile file: "${RESULT_DIR}\\QA_Report.html", text: html

                    if (fails.size() > 0) {
                        error "[ERR-QA-002] QA 실패 (${fails.size()}건)"
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
            slackSend(
                channel: "#새-채널",
                message: "@here ✅ QA 성공"
            )
        }

        failure {
            slackSend(
                channel: "#새-채널",
                message: "@here ❌ QA 실패 발생"
            )
        }
    }
}