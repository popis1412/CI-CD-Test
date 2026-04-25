pipeline {
    agent any

    parameters {
        string(name: 'BASE_PATH', defaultValue: '', description: '기본 경로')
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

                    // 🔥 Sandbox 안전 loop
                    for (int i = 1; i < lines.size(); i++) {

                        def cols = lines[i].split(",")

                        if (cols.size() >= 4) {
                            testResults << [
                                major: cols[0],
                                minor: cols[1],
                                scenario: cols[2],
                                result: cols[3]
                            ]
                        }
                    }

                    // 🔥 통계
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
                    def html = "<html><body>"
                    html += "<h1>QA 정량 분석 리포트</h1>"
                    html += "<p>경로: ${RESULT_DIR}</p>"
                    html += "<p>시간: ${new Date()}</p>"

                    html += "<table border='1'><tr><th>대분류</th><th>중분류</th><th>Total</th><th>Pass</th><th>Fail</th></tr>"

                    stats.each { major, minors ->
                        minors.each { minor, s ->
                            html += "<tr><td>${major}</td><td>${minor}</td><td>${s.total}</td><td>${s.pass}</td><td>${s.fail}</td></tr>"
                        }
                    }

                    html += "</table>"

                    // 🔥 실패 상세
                    def fails = testResults.findAll { it.result == "FAIL" }

                    html += "<h2>실패 상세</h2><ul>"

                    fails.each {
                        def path = "${it.major} > ${it.minor} > ${it.scenario}"
                        html += "<li>${path}</li>"
                    }

                    html += "</ul></body></html>"

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
                message: "✅ QA 성공"
            )
        }

        failure {
            slackSend(
                channel: "#새-채널",
                message: "❌ QA 실패"
            )
        }
    }
}