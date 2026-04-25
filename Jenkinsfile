pipeline {
    agent any

    parameters {
        string(name: 'BASE_PATH', defaultValue: 'C:\\QA\\CI-CD-Test', description: '결과 저장 경로')
    }

    environment {
        RESULT_DIR = "${params.BASE_PATH}\\Test Results"
        TEST_FILE = "${params.BASE_PATH}\\Tests\\QA_Test.csv"
    }

    stages {

        stage('Prepare') {
            steps {
                script {
                    try {
                        bat """
                        if not exist "${env.RESULT_DIR}" (
                            mkdir "${env.RESULT_DIR}"
                        )
                        """
                    } catch (Exception e) {
                        error "[ERR-PATH-001] 경로 생성 실패: ${env.RESULT_DIR}"
                    }
                }
            }
        }

        stage('QA Analysis') {
            steps {
                script {

                    if (!fileExists(env.TEST_FILE)) {
                        error "[ERR-FILE-001] 테스트 파일 없음: ${env.TEST_FILE}"
                    }

                    def lines = readFile(env.TEST_FILE).split("\\r?\\n")

                    def testResults = []

                    // CSV 구조: 대분류,중분류,시나리오,결과
                    lines.drop(1).each { line ->
                        def cols = line.split(",")

                        if (cols.size() >= 4) {
                            testResults << [
                                major: cols[0],
                                minor: cols[1],
                                scenario: cols[2],
                                result: cols[3]
                            ]
                        }
                    }

                    // 🔥 통계 집계
                    def stats = [:]

                    testResults.each { t ->
                        if(!stats[t.major]) stats[t.major] = [:]
                        if(!stats[t.major][t.minor]) {
                            stats[t.major][t.minor] = [total:0, pass:0, fail:0]
                        }

                        def s = stats[t.major][t.minor]
                        s.total++

                        if(t.result == "PASS") s.pass++
                        else if(t.result == "FAIL") s.fail++
                    }

                    // 🔥 HTML 생성
                    def html = """
                    <html>
                    <head>
                    <meta charset="UTF-8">
                    <style>
                        body { font-family: Arial; padding:20px; }
                        table { border-collapse: collapse; width:100%; }
                        th, td { border:1px solid #ccc; padding:10px; text-align:center; }
                        th { background:#eee; }
                        .fail { color:red; }
                        .pass { color:green; }
                    </style>
                    </head>
                    <body>

                    <h1>QA 정량 분석 리포트</h1>
                    <p>경로: ${env.RESULT_DIR}</p>
                    <p>파일: ${env.TEST_FILE}</p>
                    <p>시간: ${new Date()}</p>

                    <h2>📊 분류별 테스트 결과</h2>
                    <table>
                        <tr>
                            <th>대분류</th>
                            <th>중분류</th>
                            <th>총 TC</th>
                            <th>PASS</th>
                            <th>FAIL</th>
                            <th>실패율</th>
                        </tr>
                    """

                    stats.each { major, minors ->
                        minors.each { minor, s ->
                            def failRate = s.total > 0 ? (s.fail * 100 / s.total).toInteger() : 0

                            html += """
                            <tr>
                                <td>${major}</td>
                                <td>${minor}</td>
                                <td>${s.total}</td>
                                <td class='pass'>${s.pass}</td>
                                <td class='fail'>${s.fail}</td>
                                <td>${failRate}%</td>
                            </tr>
                            """
                        }
                    }

                    html += "</table>"

                    // 🔥 실패 상세 (경로 포함)
                    def fails = testResults.findAll { it.result == "FAIL" }

                    html += """
                    <h2>⚠️ 실패 상세</h2>
                    <ul>
                    """

                    def slackMsg = "❌ QA 실패 (${fails.size()}건)\n\n"

                    fails.each {
                        def path = "${it.major} > ${it.minor} > ${it.scenario}"
                        html += "<li>${path} → 실패</li>"
                        slackMsg += "- ${path}\n"
                    }

                    html += "</ul></body></html>"

                    writeFile file: "${env.RESULT_DIR}\\QA_Report.html", text: html, encoding: 'UTF-8'

                    if(fails.size() > 0) {
                        env.SLACK_MSG = slackMsg
                        error "[ERR-QA-002] QA 실패 (${fails.size()}건)"
                    } else {
                        env.SLACK_MSG = "✅ QA 성공\n결과 경로: ${env.RESULT_DIR}"
                    }
                }
            }
        }
    }

    post {
        always {
            publishHTML(target: [
                reportDir: "${env.RESULT_DIR}",
                reportFiles: 'QA_Report.html',
                reportName: 'QA Report'
            ])
        }

        success {
            slackSend(
                channel: "#새-채널",
                color: '#00FF00',
                message: env.SLACK_MSG
            )
        }

        failure {
            slackSend(
                channel: "#새-채널",
                color: '#FF0000',
                message: env.SLACK_MSG
            )
        }
    }
}